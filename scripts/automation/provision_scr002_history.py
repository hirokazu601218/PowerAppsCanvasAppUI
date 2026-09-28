"""Idempotent SCR-002 metadata provisioning; never create personnel rows or change roles."""
import argparse
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from scr002_history_schema import SPEC, attributes, names, relationship, table

ROOT = Path(__file__).resolve().parents[2]
URL = "https://orge762dd9e.crm7.dynamics.com"
ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"
SOLUTION = "StaffMasterAutomation"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "provision", "verify"), required=True)
    args = parser.parse_args()
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", URL,
         "--query", "accessToken", "--output", "tsv"], text=True, timeout=45).strip()

    def api(path, method="GET", body=None):
        headers = {"Authorization": "Bearer " + token, "Accept": "application/json",
                   "Content-Type": "application/json", "OData-Version": "4.0",
                   "OData-MaxVersion": "4.0", "MSCRM.SolutionUniqueName": SOLUTION}
        req = urllib.request.Request(
            URL + "/api/data/v9.2/" + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=150) as response:
                payload = response.read()
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as exc:
            try:
                message = json.loads(exc.read()).get("error", {}).get("message", "Dataverse error")
            except ValueError:
                message = "Non-JSON Dataverse error"
            raise RuntimeError(f"{exc.code}: {message}") from None

    assert api("WhoAmI")["OrganizationId"] == ORG, "Wrong organization"
    sol = api("solutions?$select=uniquename,ismanaged&$filter=uniquename%20eq%20'"
              + SOLUTION + "'&$expand=publisherid($select=customizationprefix)")["value"]
    assert len(sol) == 1 and not sol[0]["ismanaged"]
    assert sol[0]["publisherid"]["customizationprefix"] == "crb3c"
    lcid = api("organizations?$select=languagecode")["value"][0]["languagecode"]
    parents = {}
    for studio in (False, True):
        parent = "crb3c_studiostaffbasic" if studio else "crb3c_staffbasic"
        parents[studio] = api("EntityDefinitions(LogicalName='" + parent +
                              "')?$select=PrimaryIdAttribute,EntitySetName")
        assert parents[studio]["PrimaryIdAttribute"]
    result = {"mode": args.mode, "checked_at": datetime.now(timezone.utc).isoformat(),
              "tables": [], "organization_verified": True, "solution_verified": True}
    if args.mode == "preflight":
        for studio in (False, True):
            for spec in SPEC["tables"]:
                logical, _ = names(spec, studio)
                found = api("EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'"
                            + logical + "'")["value"]
                result["tables"].append({"logical_name": logical, "exists": bool(found)})
    else:
        for studio in (False, True):
            parent = "crb3c_studiostaffbasic" if studio else "crb3c_staffbasic"
            for spec in SPEC["tables"]:
                logical, _ = names(spec, studio)
                entity = "EntityDefinitions(LogicalName='" + logical + "')"
                found = api("EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'"
                            + logical + "'")["value"]
                if not found:
                    assert args.mode == "provision", "Missing table: " + logical
                    api("EntityDefinitions", "POST", table(spec, studio, lcid))
                    print("CREATED_TABLE", logical, flush=True)
                meta = api(entity + "?$select=LogicalName,OwnershipType,PrimaryNameAttribute,"
                           "PrimaryIdAttribute,EntitySetName&$expand=Attributes")
                assert meta["OwnershipType"] == "UserOwned"
                assert meta["PrimaryNameAttribute"] == "crb3c_name"
                actual = {a["LogicalName"]: a for a in meta["Attributes"]}
                for expected in attributes(spec, lcid):
                    field = actual[expected["SchemaName"].lower()]
                    kind = expected["@odata.type"].split(".")[-1].replace("AttributeMetadata", "")
                    assert field["AttributeType"] == kind, field["LogicalName"]
                    assert field["RequiredLevel"]["Value"] == expected["RequiredLevel"]["Value"]
                    for key in ("MaxLength", "MinValue", "MaxValue", "Precision", "Format"):
                        if key in expected:
                            assert field[key] == expected[key], (field["LogicalName"], key)
                    if "DateTimeBehavior" in expected:
                        assert field["DateTimeBehavior"]["Value"] == "DateOnly"
                rel = relationship(spec, studio, lcid, parents[studio]["PrimaryIdAttribute"])
                found_rel = api("RelationshipDefinitions/"
                                "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata?"
                                "$filter=SchemaName%20eq%20'" + rel["SchemaName"] + "'")["value"]
                if not found_rel:
                    assert args.mode == "provision", "Missing relationship: " + rel["SchemaName"]
                    api("RelationshipDefinitions", "POST", rel)
                    print("CREATED_RELATIONSHIP", rel["SchemaName"], flush=True)
                observed = api("RelationshipDefinitions(SchemaName='" + rel["SchemaName"] +
                               "')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
                assert observed["ReferencedEntity"] == parent
                assert observed["ReferencingEntity"] == logical
                assert observed["CascadeConfiguration"]["Delete"] == "Restrict"
                result["tables"].append({
                    "logical_name": logical, "columns_from_attachment": len(spec["columns"]),
                    "relationship": rel["SchemaName"], "entity_set": meta["EntitySetName"],
                    "verified": True,
                })
        if args.mode == "provision":
            xml = "<importexportxml><entities>" + "".join(
                "<entity>" + item["logical_name"] + "</entity>" for item in result["tables"]
            ) + "</entities></importexportxml>"
            api("PublishXml", "POST", {"ParameterXml": xml})
    output = ROOT / "artifacts/scr002-history"
    output.mkdir(parents=True, exist_ok=True)
    (output / (args.mode + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
