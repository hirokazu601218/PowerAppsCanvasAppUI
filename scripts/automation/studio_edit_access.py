"""Add Studio-only CRUD to the already dedicated reader role, preserving its baseline."""

import urllib.parse


ROLE_NAME = "StaffMaster Test Reader"
OPERATIONS = {"Create", "Read", "Write", "Delete", "Append", "AppendTo"}
ORIGINALS = ("crb3c_staffbasic", "crb3c_commute", "crb3c_payrollledger")


def grant(api, cfg, metas, base_url):
    q = urllib.parse.urlencode({"$select": "systemuserid,isdisabled",
                               "$filter": "internalemailaddress eq '" + cfg["test_user"] + "'"})
    users = api("systemusers?" + q)["value"]
    if len(users) != 1 or users[0]["isdisabled"]:
        raise RuntimeError("Dedicated user not uniquely active")
    uid = users[0]["systemuserid"]
    roles = api("systemusers(" + uid + ")/systemuserroles_association?$select=roleid,name")["value"]
    matches = [r for r in roles if r["name"] == ROLE_NAME]
    if len(matches) != 1:
        raise RuntimeError("Dedicated reader role baseline changed")
    rid = matches[0]["roleid"]
    direct = api("roles(" + rid + ")/systemuserroles_association?$select=systemuserid")["value"]
    teams = api("roles(" + rid + ")/teamroles_association?$select=teamid")["value"]
    if len(direct) != 1 or direct[0]["systemuserid"] != uid or teams:
        raise RuntimeError("Existing reader role is no longer dedicated")

    original_privileges = set()
    for name in ORIGINALS:
        meta = api("EntityDefinitions(LogicalName='" + name + "')?$select=Privileges")
        original_privileges.update(p["PrivilegeId"] for p in meta["Privileges"]
                                   if p["PrivilegeType"] in ("Create", "Write", "Delete"))
    def user_privileges():
        return {p["PrivilegeId"] for p in api("systemusers(" + uid +
                ")/Microsoft.Dynamics.CRM.RetrieveUserPrivileges()")["RolePrivileges"]}
    if original_privileges & user_privileges():
        raise RuntimeError("Dedicated user already has original table write privileges")

    desired = {}
    for meta in metas:
        entity = api("EntityDefinitions(LogicalName='" + meta["LogicalName"] +
                     "')?$select=Privileges")
        found = {p["PrivilegeType"]: p["PrivilegeId"] for p in entity["Privileges"]
                 if p["PrivilegeType"] in OPERATIONS}
        if found.keys() != OPERATIONS:
            raise RuntimeError("Studio table privileges incomplete")
        desired.update({pid: "Global" for pid in found.values()})

    def role_privileges():
        return {p["PrivilegeId"]: p["Depth"] for p in
                api("RetrieveRolePrivilegesRole(RoleId=" + rid + ")")["RolePrivileges"]}
    before = role_privileges()
    missing = [{"PrivilegeId": pid, "Depth": "Global"} for pid in desired
               if before.get(pid) != "Global"]
    if missing:
        api("roles(" + rid + ")/Microsoft.Dynamics.CRM.AddPrivilegesRole", "POST",
            {"Privileges": missing})
    after = role_privileges()
    if any(after.get(pid) != "Global" for pid in desired):
        raise RuntimeError("Studio privileges not granted as requested")
    if {pid: depth for pid, depth in before.items() if pid not in desired} != {
            pid: depth for pid, depth in after.items() if pid not in desired}:
        raise RuntimeError("Reader role unrelated privilege delta")
    effective = user_privileges()
    if not set(desired) <= effective or original_privileges & effective:
        raise RuntimeError("Dedicated user privilege isolation failed")
    return {"role": ROLE_NAME, "studio_privilege_count": len(desired),
            "assigned_to_dedicated_user_only": True,
            "original_table_create_write_delete": False,
            "other_privileges_unchanged": True}
