"""Grant a single dedicated user CRUD on Studio-only Dataverse tables."""

import urllib.parse


ROLE_NAME = "StaffMaster Studio CRUD"
OPERATIONS = {"Create", "Read", "Write", "Delete", "Append", "AppendTo"}
ORIGINALS = ("crb3c_staffbasic", "crb3c_commute", "crb3c_payrollledger")


def grant(api, cfg, metas, base_url):
    q = urllib.parse.urlencode({"$select": "systemuserid,isdisabled,_businessunitid_value",
                               "$filter": "internalemailaddress eq '" + cfg["test_user"] + "'"})
    users = api("systemusers?" + q)["value"]
    if len(users) != 1 or users[0]["isdisabled"]:
        raise RuntimeError("Dedicated user not uniquely active")
    uid = users[0]["systemuserid"]
    existing_roles = api("systemusers(" + uid + ")/systemuserroles_association?$select=roleid,name")["value"]
    if sum(r["name"] == "StaffMaster Test Reader" for r in existing_roles) != 1:
        raise RuntimeError("Dedicated reader baseline changed")

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

    bu = users[0]["_businessunitid_value"]
    q = urllib.parse.urlencode({"$select": "roleid,name,_businessunitid_value",
                               "$filter": "name eq '" + ROLE_NAME + "'"})
    roles = api("roles?" + q)["value"]
    if len(roles) > 1 or (roles and roles[0]["_businessunitid_value"] != bu):
        raise RuntimeError("Studio role is ambiguous or in another business unit")
    if not roles:
        api("roles", "POST", {"businessunitid@odata.bind": "businessunits(" + bu + ")",
                             "name": ROLE_NAME})
        roles = api("roles?" + q)["value"]
    if len(roles) != 1:
        raise RuntimeError("Studio role creation was not confirmed")
    rid = roles[0]["roleid"]
    def role_privileges():
        return {p["PrivilegeId"]: p["Depth"] for p in
                api("RetrieveRolePrivilegesRole(RoleId=" + rid + ")")["RolePrivileges"]}
    before = role_privileges()
    extra_names = []
    if set(before) - set(desired):
        extra_names = []
        for pid in sorted(set(before) - set(desired)):
            found = api("privileges(" + pid + ")?$select=name")
            extra_names.append(found["name"])
    automatic = {"prvReadSdkMessageProcessingStepImage", "prvCreateSharePointData",
                 "prvReadPluginType", "prvReadSdkMessage", "prvWriteSharePointData",
                 "prvReadSharePointDocument", "prvReadSdkMessageProcessingStep",
                 "prvReadPluginAssembly", "prvReadSharePointData"}
    if set(extra_names) not in (set(), automatic):
        raise RuntimeError("Unexpected baseline role privileges: " + ",".join(extra_names))
    prior_users = api("roles(" + rid + ")/systemuserroles_association?$select=systemuserid")["value"]
    prior_teams = api("roles(" + rid + ")/teamroles_association?$select=teamid")["value"]
    if prior_teams or any(u["systemuserid"] != uid for u in prior_users):
        raise RuntimeError("Studio role is already assigned beyond the dedicated user")
    if before != desired:
        api("roles(" + rid + ")/Microsoft.Dynamics.CRM.ReplacePrivilegesRole", "POST",
            {"Privileges": [{"PrivilegeId": pid, "Depth": depth}
                            for pid, depth in desired.items()]})
    if role_privileges() != desired:
        raise RuntimeError("Studio role privileges mismatch")

    if not any(r["roleid"] == rid for r in existing_roles):
        api("systemusers(" + uid + ")/systemuserroles_association/$ref", "POST",
            {"@odata.id": base_url + "/api/data/v9.2/roles(" + rid + ")"})
    direct = api("roles(" + rid + ")/systemuserroles_association?$select=systemuserid")["value"]
    teams = api("roles(" + rid + ")/teamroles_association?$select=teamid")["value"]
    if len(direct) != 1 or direct[0]["systemuserid"] != uid or teams:
        raise RuntimeError("Studio role assignment scope mismatch")
    effective = user_privileges()
    if not set(desired) <= effective or original_privileges & effective:
        raise RuntimeError("Dedicated user privilege isolation failed")
    return {"role": ROLE_NAME, "studio_privilege_count": len(desired),
            "assigned_to_dedicated_user_only": True,
            "original_table_create_write_delete": False}
