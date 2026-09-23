"""Create and verify three Studio-only Dataverse tables; never write original data.

Modes: preflight (read-only), provision (create missing metadata), verify (read-only),
seed (insert synthetic records only into the isolated Studio tables),
access (give the dedicated user CRUD on those Studio tables),
audit (read-only leftover record and role check), cleanup (remove both).
Provision can be retried after checking the readback; no records or roles are
created here. Requires the existing GitHub OIDC service principal.
"""

import json
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from studio_edit_schema import TABLES, relationship_definition, table_definition


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"


def main():
    cfg = json.loads((ROOT / "config/apps/staff-master.json").read_text())
    request = json.loads((ROOT / "automation/studio-edit-run.json").read_text())
    mode = request["mode"]
    if mode not in ("preflight", "provision", "verify", "seed", "access", "audit", "cleanup") or request.get("approved") is not True:
        raise RuntimeError("Unsupported or unapproved operation")
    started = datetime.fromisoformat(request["started_at"]).timestamp()
    if time.time() - started >= 3480:
        raise RuntimeError("PAUSED_TIME_LIMIT")
    url = cfg["target"]["dataverse_url"].rstrip("/")
    if cfg["target"]["environment_id"] != "68e00049-b7e5-eda6-9888-9a3cc493c5be":
        raise RuntimeError("Wrong environment")
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", url,
         "--query", "accessToken", "--output", "tsv"], text=True, timeout=45
    ).strip()

    def api(path, method="GET", body=None, extra_headers=None):
        if time.time() - started >= 3480:
            raise RuntimeError("PAUSED_TIME_LIMIT")
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
                   "Content-Type": "application/json", "OData-Version": "4.0",
                   "OData-MaxVersion": "4.0", "MSCRM.SolutionUniqueName": cfg["solution_name"]}
        headers.update(extra_headers or {})
        req = urllib.request.Request(
            url + "/api/data/v9.2/" + path, method=method,
            data=json.dumps(body).encode() if body is not None else None, headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=180 if method != "GET" else 45) as res:
                data = res.read()
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as exc:
            try:
                message = json.loads(exc.read()).get("error", {}).get("message", "Dataverse error")
            except ValueError:
                message = "Non-JSON Dataverse error"
            raise RuntimeError(f"{exc.code}: {message}") from None

    who = api("WhoAmI")
    if who["OrganizationId"] != EXPECTED_ORG:
        raise RuntimeError("Unexpected organization")
    sol = api("solutions?$select=uniquename,ismanaged&$filter=uniquename%20eq%20'"
              + cfg["solution_name"] + "'&$expand=publisherid($select=customizationprefix)")["value"]
    if len(sol) != 1 or sol[0]["ismanaged"] or sol[0]["publisherid"]["customizationprefix"] != "crb3c":
        raise RuntimeError("Wrong solution or publisher")
    lcid = api("organizations?$select=languagecode")["value"][0]["languagecode"]
    snapshot = {}
    for original in ("crb3c_staffbasic", "crb3c_commute", "crb3c_payrollledger"):
        meta = api("EntityDefinitions(LogicalName='" + original +
                   "')?$select=EntitySetName,PrimaryIdAttribute")
        snapshot[original] = len(api(meta["EntitySetName"] + "?$select=" +
                                     meta["PrimaryIdAttribute"] + "&$top=100")["value"])

    out = ROOT / "artifacts/studio-edit"
    out.mkdir(parents=True, exist_ok=True)
    state = {"mode": mode, "checked_at": datetime.now(timezone.utc).isoformat(),
             "original_counts_before": snapshot, "studio_tables": []}
    if mode == "preflight":
        for logical, _, _, _ in TABLES:
            state["studio_tables"].append({"logical_name": logical, "exists": bool(api(
                "EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'" + logical + "'"
            )["value"])})
        state["result"] = "PREFLIGHT_PASSED"
        (out / "result.json").write_text(json.dumps(state, ensure_ascii=False, indent=2))
        print(json.dumps(state, ensure_ascii=False), flush=True)
        return

    metas = []
    for index, (logical, _, _, module) in enumerate(TABLES):
        existing = api("EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'" + logical + "'")["value"]
        if not existing:
            if mode != "provision":
                raise RuntimeError("Missing Studio table: " + logical)
            api("EntityDefinitions", "POST", table_definition(index, lcid))
            print("Created " + logical, flush=True)
        entity = "EntityDefinitions(LogicalName='" + logical + "')"
        meta = api(entity + "?$select=LogicalName,OwnershipType,PrimaryNameAttribute,PrimaryIdAttribute,EntitySetName&$expand=Attributes")
        if meta["OwnershipType"] != "UserOwned":
            raise RuntimeError("Wrong table ownership: " + logical)
        expected = table_definition(index, lcid)["Attributes"]
        actual = {a["LogicalName"]: a for a in meta["Attributes"]}
        if len(expected) != len(module.attributes(lcid)):
            raise RuntimeError("Unexpected column count")
        for column in expected:
            field = actual[column["SchemaName"].lower()]
            typ = column["@odata.type"].split(".")[-1].replace("AttributeMetadata", "")
            if field["AttributeType"] != typ or field["RequiredLevel"]["Value"] != column["RequiredLevel"]["Value"]:
                raise RuntimeError("Schema mismatch: " + field["LogicalName"])
            for prop in ("MaxLength", "MinValue", "MaxValue", "Precision", "Format"):
                if prop in column and field[prop] != column[prop]:
                    raise RuntimeError("Column mismatch: " + field["LogicalName"] + "." + prop)
        if index == 0:
            key_name = "crb3c_studio_staffnumber_key"
            keys = api(entity + "/Keys")["value"]
            if not any(k["SchemaName"] == key_name for k in keys):
                if mode != "provision":
                    raise RuntimeError("Missing Studio parent key")
                api(entity + "/Keys", "POST", {"SchemaName": key_name,
                    "KeyAttributes": ["crb3c_staffnumber"],
                    "DisplayName": module.label("Studio職員番号一意キー", lcid)})
            for _ in range(90):
                keys = api(entity + "/Keys")["value"]
                key = next(k for k in keys if k["SchemaName"] == key_name)
                if key["EntityKeyIndexStatus"] == "Active":
                    break
                if key["EntityKeyIndexStatus"] == "Failed":
                    raise RuntimeError("Studio key index failed")
                time.sleep(2)
            else:
                raise RuntimeError("Studio key is not active")
        else:
            relation = relationship_definition(index, lcid, metas[0]["PrimaryIdAttribute"])
            rel_name = relation["SchemaName"]
            found = api("RelationshipDefinitions/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata?$filter=SchemaName%20eq%20'" + rel_name + "'")["value"]
            if not found:
                if mode != "provision":
                    raise RuntimeError("Missing Studio relationship: " + rel_name)
                api("RelationshipDefinitions", "POST", relation)
            observed = api("RelationshipDefinitions(SchemaName='" + rel_name +
                           "')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
            if (observed["ReferencedEntity"] != TABLES[0][0] or
                    observed["ReferencingEntity"] != logical or
                    observed["CascadeConfiguration"]["Delete"] != "Restrict"):
                raise RuntimeError("Studio relationship mismatch")
        metas.append(meta)
        state["studio_tables"].append({"logical_name": logical,
                                      "columns": len(expected), "entity_set": meta["EntitySetName"]})

    if mode == "provision":
        names = "".join("<entity>" + logical + "</entity>" for logical, _, _, _ in TABLES)
        api("PublishXml", "POST", {"ParameterXml": "<importexportxml><entities>" +
            names + "</entities></importexportxml>"})
    if mode == "seed":
        from studio_edit_fixtures import seed
        state["fixture_counts"] = seed(api, metas)
    if mode == "access":
        from studio_edit_access import grant
        state["access"] = grant(api, cfg, metas, url)
    if mode in ("audit", "cleanup"):
        from studio_edit_cleanup import audit, cleanup
        state["cleanup"] = audit(api, cfg, metas[0])
        if mode == "cleanup":
            state["cleanup"] = cleanup(api, cfg, metas[0], state["cleanup"])
    after = {}
    for original in snapshot:
        meta = api("EntityDefinitions(LogicalName='" + original + "')?$select=EntitySetName,PrimaryIdAttribute")
        after[original] = len(api(meta["EntitySetName"] + "?$select=" +
                                  meta["PrimaryIdAttribute"] + "&$top=100")["value"])
    if after != snapshot:
        raise RuntimeError("Original counts changed during Studio setup")
    state["original_counts_after"] = after
    state["result"] = {"seed": "STUDIO_FIXTURES_VERIFIED",
                       "access": "STUDIO_ACCESS_VERIFIED",
                       "audit": "STUDIO_CLEANUP_AUDITED",
                       "cleanup": "STUDIO_CLEANUP_VERIFIED"}.get(mode, "STUDIO_SCHEMA_VERIFIED")
    (out / "result.json").write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(json.dumps(state, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
