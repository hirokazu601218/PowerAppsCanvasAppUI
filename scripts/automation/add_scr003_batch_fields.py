"""One-time migration for batch staging columns on tables created in this task."""
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from provision_scr003_attendance import ORG, SOLUTION, URL, attr

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "config/dataverse/scr003-attendance-columns.json").read_text())
FIELDS = {"report": "active_batch_id", "detail": "batch_id"}


def main():
    token = subprocess.check_output(["az", "account", "get-access-token", "--resource", URL,
                                     "--query", "accessToken", "--output", "tsv"], text=True).strip()

    def api(path, method="GET", body=None):
        request = urllib.request.Request(URL + "/api/data/v9.2/" + path,
            method=method, data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "Content-Type": "application/json", "OData-Version": "4.0",
                     "OData-MaxVersion": "4.0", "MSCRM.SolutionUniqueName": SOLUTION})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Dataverse HTTP {exc.code}: {exc.read().decode(errors='replace')[:1000]}") from None

    assert api("WhoAmI")["OrganizationId"].lower() == ORG
    lcid = api("organizations?$select=languagecode")["value"][0]["languagecode"]
    result = []
    for entity in SPEC["entities"]:
        if entity["key"] not in FIELDS:
            continue
        logical = entity["logical_name"]
        field = next(f for f in entity["fields"] if f["key"] == FIELDS[entity["key"]])
        expected = attr(field, lcid)
        path = "EntityDefinitions(LogicalName='" + logical + "')"
        meta = api(path + "?$select=LogicalName,OwnershipType,PrimaryIdAttribute&$expand=Attributes")
        assert meta["OwnershipType"] == "UserOwned"
        actual = {a["LogicalName"]: a for a in meta["Attributes"]}
        column = expected["SchemaName"].lower()
        if column not in actual:
            api(path + "/Attributes", "POST", expected)
            print("ADDED", logical, column, flush=True)
        refreshed = api(path + "?$expand=Attributes")
        observed = next(a for a in refreshed["Attributes"] if a["LogicalName"] == column)
        assert observed["MaxLength"] == 36, (logical, column)
        result.append((logical, column))
    api("PublishXml", "POST", {"ParameterXml": "<importexportxml><entities>" +
        "".join("<entity>" + logical + "</entity>" for logical, _ in result) +
        "</entities></importexportxml>"})
    print(json.dumps({"organization_verified": True, "columns": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
