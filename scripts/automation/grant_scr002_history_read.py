"""Grant the existing dedicated test-reader role Read on four isolated tables only."""
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from scr002_history_schema import SPEC

ROOT = Path(__file__).resolve().parents[2]
URL = "https://orge762dd9e.crm7.dynamics.com"
ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"
USER = "powerapps-test@govaca.onmicrosoft.com"
ROLE = "StaffMaster Test Reader"


def main():
    token = subprocess.check_output(
        ["az", "account", "get-access-token", "--resource", URL,
         "--query", "accessToken", "--output", "tsv"], text=True, timeout=45).strip()

    def api(path, method="GET", body=None):
        req = urllib.request.Request(
            URL + "/api/data/v9.2/" + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "Content-Type": "application/json", "OData-Version": "4.0",
                     "OData-MaxVersion": "4.0"})
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
        raise RuntimeError("Wrong organization; no grant")
    query = urllib.parse.urlencode({"$select": "systemuserid,isdisabled",
                                    "$filter": "internalemailaddress eq '" + USER + "'"})
    users = api("systemusers?" + query)["value"]
    if len(users) != 1 or users[0]["isdisabled"]:
        raise RuntimeError("Dedicated account unavailable; no grant")
    uid = users[0]["systemuserid"]
    roles = api("systemusers(" + uid + ")/systemuserroles_association?$select=roleid,name")["value"]
    matches = [role for role in roles if role["name"] == ROLE]
    if len(matches) != 1:
        raise RuntimeError("Dedicated reader role changed; no grant")
    rid = matches[0]["roleid"]
    direct = api("roles(" + rid + ")/systemuserroles_association?$select=systemuserid")["value"]
    teams = api("roles(" + rid + ")/teamroles_association?$select=teamid")["value"]
    if len(direct) != 1 or direct[0]["systemuserid"] != uid or teams:
        raise RuntimeError("Reader role not isolated to dedicated account")

    original_write = set()
    for logical in ("crb3c_staffbasic", "crb3c_commute", "crb3c_payrollledger"):
        entity = api("EntityDefinitions(LogicalName='" + logical + "')?$select=Privileges")
        original_write.update(p["PrivilegeId"] for p in entity["Privileges"]
                              if p["PrivilegeType"] in ("Create", "Write", "Delete"))
    desired = set()
    forbidden = set()
    for spec in SPEC["tables"]:
        entity = api("EntityDefinitions(LogicalName='" + spec["studio_logical_name"] +
                     "')?$select=Privileges")
        privileges = entity["Privileges"]
        read = [p["PrivilegeId"] for p in privileges if p["PrivilegeType"] == "Read"]
        if len(read) != 1:
            raise RuntimeError("Missing unique Studio Read privilege")
        desired.add(read[0])
        forbidden.update(p["PrivilegeId"] for p in privileges
                         if p["PrivilegeType"] in ("Create", "Write", "Delete"))

    def role_privileges():
        return {p["PrivilegeId"]: p["Depth"] for p in
                api("RetrieveRolePrivilegesRole(RoleId=" + rid + ")")["RolePrivileges"]}

    def user_privileges():
        return {p["PrivilegeId"] for p in
                api("systemusers(" + uid +
                    ")/Microsoft.Dynamics.CRM.RetrieveUserPrivileges()")["RolePrivileges"]}

    before = role_privileges()
    effective = user_privileges()
    if (forbidden | original_write) & effective:
        raise RuntimeError("Test user has unexpected write privilege; no grant")
    missing = [{"PrivilegeId": pid, "Depth": "Global"} for pid in desired
               if before.get(pid) != "Global"]
    if missing:
        api("roles(" + rid + ")/Microsoft.Dynamics.CRM.AddPrivilegesRole", "POST",
            {"Privileges": missing})
    after = role_privileges()
    effective = user_privileges()
    if any(after.get(pid) != "Global" for pid in desired) or not desired <= effective:
        raise RuntimeError("Dedicated read grant not effective")
    if {p: depth for p, depth in before.items() if p not in desired} != {
            p: depth for p, depth in after.items() if p not in desired}:
        raise RuntimeError("Unrelated privilege delta")
    if (forbidden | original_write) & effective:
        raise RuntimeError("Write privilege detected after grant")
    result = {"role": ROLE, "dedicated_account_only": True,
              "studio_read_privilege_count": len(desired),
              "other_privileges_unchanged": True, "original_write": False,
              "studio_write": False}
    out = ROOT / "artifacts/scr002-history"
    out.mkdir(parents=True, exist_ok=True)
    (out / "read-access.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
