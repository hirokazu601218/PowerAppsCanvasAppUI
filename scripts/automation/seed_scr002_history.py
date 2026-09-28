"""Seed only four isolated SCR-002 Studio tables with one synthetic staff history.

No original/production table is written. Existing unrelated rows cause a stop.
"""
import json
import subprocess
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from scr002_history_schema import SPEC

ROOT = Path(__file__).resolve().parents[2]
URL = "https://orge762dd9e.crm7.dynamics.com"
ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"
STAFF = "009900000011"


def main():
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", URL,
         "--query", "accessToken", "--output", "tsv"], text=True, timeout=45).strip()

    def api(path, method="GET", body=None, extra=None):
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
                   "Content-Type": "application/json", "OData-Version": "4.0",
                   "OData-MaxVersion": "4.0"}
        headers.update(extra or {})
        req = urllib.request.Request(
            URL + "/api/data/v9.2/" + path, method=method,
            data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            try:
                message = json.loads(exc.read()).get("error", {}).get("message", "Dataverse error")
            except ValueError:
                message = "Non-JSON Dataverse error"
            raise RuntimeError(f"{exc.code}: {message}") from None

    if api("WhoAmI")["OrganizationId"] != ORG:
        raise RuntimeError("Wrong organization; no writes")
    parent_meta = api("EntityDefinitions(LogicalName='crb3c_studiostaffbasic')?"
                      "$select=PrimaryIdAttribute,EntitySetName")
    parent_set = parent_meta["EntitySetName"]
    parents = api(parent_set + "?$select=" + parent_meta["PrimaryIdAttribute"] +
                  ",crb3c_staffnumber&$filter=crb3c_staffnumber%20eq%20'" + STAFF + "'")["value"]
    if len(parents) != 1:
        raise RuntimeError("Fixture parent missing or duplicated; no writes")

    targets = []
    for spec in SPEC["tables"]:
        logical = spec["studio_logical_name"]
        meta = api("EntityDefinitions(LogicalName='" + logical +
                   "')?$select=PrimaryIdAttribute,EntitySetName")
        relation = api("RelationshipDefinitions(SchemaName='crb3c_studiostaffbasic_" +
                       spec["key"] + "')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
        if relation["ReferencedEntity"] != "crb3c_studiostaffbasic" or relation["ReferencingEntity"] != logical:
            raise RuntimeError("Unexpected relationship; no writes")
        key = str(uuid.uuid5(uuid.NAMESPACE_URL, "scr002-history/" + logical + "/" + STAFF))
        rows = api(meta["EntitySetName"] + "?$select=" + meta["PrimaryIdAttribute"] + "&$top=100")["value"]
        if any(str(row[meta["PrimaryIdAttribute"]]).lower() != key for row in rows):
            raise RuntimeError("Unexpected Studio row in " + logical + "; no writes")
        targets.append((spec, meta, relation, key, bool(rows)))

    result = {"organization_verified": True, "staff": STAFF, "fixtures": []}
    for spec, meta, relation, key, exists in targets:
        payload = {"crb3c_name": "SCR002-架空試験-" + spec["key"] + "-" + STAFF,
                   meta["PrimaryIdAttribute"]: key,
                   relation["ReferencingEntityNavigationPropertyName"] + "@odata.bind":
                   "/" + parent_set + "(crb3c_staffnumber='" + STAFF + "')"}
        for column in spec["columns"]:
            name = column["logical_name"]
            if name == "crb3c_staffnumber":
                value = STAFF
            elif name == "crb3c_fullname":
                value = "試験 同姓同名"
            elif spec["key"] == "work" and name == "crb3c_notes":
                value = None  # NULLと金額0を区別する表示試験
            elif column["kind"] == "date":
                value = "2026-09-01"
            elif column["kind"] == "integer":
                value = 0 if "amount" in name or "rate" in name else 1
            elif column["kind"] == "decimal":
                value = 7.75
            else:
                value = "架空試験-" + column["display_name"]
            payload[name] = value
        if not exists:
            api(meta["EntitySetName"] + "(" + key + ")", "PATCH", payload,
                {"If-None-Match": "*"})
        elif spec["key"] == "work":
            api(meta["EntitySetName"] + "(" + key + ")", "PATCH",
                {"crb3c_notes": None}, {"If-Match": "*"})
        result["fixtures"].append({"table": spec["studio_logical_name"],
                                   "record_id": key, "existed_before": exists,
                                   "columns": len(spec["columns"])})
    out = ROOT / "artifacts/scr002-history"
    out.mkdir(parents=True, exist_ok=True)
    (out / "seed.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
