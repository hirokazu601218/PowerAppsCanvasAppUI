"""Read-only Dataverse preflight for SCR-003 attendance import metadata."""
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://orge762dd9e.crm7.dynamics.com"
ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"
ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "config/dataverse/scr003-attendance-columns.json").read_text())


def main():
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", URL,
         "--query", "accessToken", "--output", "tsv"], text=True, timeout=45).strip()
    def get(path):
        req = urllib.request.Request(
            URL + "/api/data/v9.2/" + path,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "OData-Version": "4.0", "OData-MaxVersion": "4.0"})
        with urllib.request.urlopen(req, timeout=90) as response:
            return json.load(response)
    assert get("WhoAmI")["OrganizationId"].lower() == ORG, "Wrong Dataverse organization"
    results = []
    for entity in SPEC["entities"]:
        logical = entity["logical_name"]
        path = "EntityDefinitions?$select=LogicalName,DisplayName,OwnershipType&$filter=" + urllib.parse.quote("LogicalName eq '" + logical + "'")
        found = get(path)["value"]
        results.append({"display_name": entity["display_name"], "logical_name": logical,
                        "exists": bool(found)})
        if found:
            # A pre-existing table needs a full column/relationship diff and user decision.
            raise RuntimeError("Existing SCR-003 table: " + logical + "; stop before provisioning")
    assert len(SPEC["import_contract"]["columns"]) == 20
    print(json.dumps({"organization_verified": True, "tables": results,
                      "excel_table": SPEC["import_contract"]["excel_table"],
                      "provisioning_performed": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
