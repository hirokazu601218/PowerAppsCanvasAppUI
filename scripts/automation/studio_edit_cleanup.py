"""Verify and remove only this Work's disposable Studio row and unused role."""

import urllib.parse


ROLE_NAME = "StaffMaster Studio CRUD"
TEST_NUMBERS = ("009900009999", "009900009998")


def _query(api, path, **params):
    return api(path + "?" + urllib.parse.urlencode(params))["value"]


def audit(api, cfg, meta):
    users = _query(api, "systemusers", **{"$select": "systemuserid,isdisabled",
        "$filter": "internalemailaddress eq '" + cfg["test_user"] + "'"})
    if len(users) != 1 or users[0]["isdisabled"]:
        raise RuntimeError("Dedicated test user is not uniquely active")
    uid = users[0]["systemuserid"]
    key = meta["PrimaryIdAttribute"]
    rows = _query(api, meta["EntitySetName"], **{
        "$select": key + ",crb3c_staffnumber,_createdby_value",
        "$filter": " or ".join("crb3c_staffnumber eq '" + n + "'" for n in TEST_NUMBERS)})
    if len(rows) > 1:
        raise RuntimeError("Multiple matching test rows; refusing cleanup")
    roles = _query(api, "roles", **{"$select": "roleid,name",
        "$filter": "name eq '" + ROLE_NAME + "'"})
    role_checks = []
    for role in roles:
        rid = role["roleid"]
        people = _query(api, "roles(" + rid + ")/systemuserroles_association",
                        **{"$select": "systemuserid"})
        teams = _query(api, "roles(" + rid + ")/teamroles_association",
                       **{"$select": "teamid"})
        role_checks.append({"id": rid, "users": len(people), "teams": len(teams)})
    return {"dedicated_user_id": uid, "table_set": meta["EntitySetName"],
            "primary_id": key, "test_rows": rows,
            "test_row_created_by_dedicated_user": bool(rows) and rows[0]["_createdby_value"] == uid,
            "temporary_roles": role_checks}


def cleanup(api, cfg, meta, prior):
    uid = prior["dedicated_user_id"]
    rows = prior["test_rows"]
    if rows:
        row = rows[0]
        key = prior["primary_id"]
        entity_path = prior["table_set"] + "(" + row[key] + ")"
        caller = {"MSCRMCallerID": uid, "If-Match": "*"}
        if row["crb3c_staffnumber"] == TEST_NUMBERS[0]:
            api(entity_path, "PATCH", {"crb3c_staffnumber": TEST_NUMBERS[1]}, caller)
            changed = api(entity_path + "?$select=crb3c_staffnumber")
            if changed["crb3c_staffnumber"] != TEST_NUMBERS[1]:
                raise RuntimeError("Impersonated update was not persisted")
        api(entity_path, "DELETE", extra_headers=caller)
    roles = prior["temporary_roles"]
    if len(roles) != 1 or roles[0]["users"] or roles[0]["teams"]:
        raise RuntimeError("Temporary role is absent, ambiguous, or assigned")
    api("roles(" + roles[0]["id"] + ")", "DELETE", extra_headers={"If-Match": "*"})
    after = audit(api, cfg, meta)
    if after["test_rows"] or after["temporary_roles"]:
        raise RuntimeError("Cleanup did not remove the test row and role")
    return {"test_row_deleted": bool(rows), "dedicated_user_update_verified": bool(rows) and
            rows[0]["crb3c_staffnumber"] == TEST_NUMBERS[0],
            "dedicated_user_delete_verified": bool(rows), "unassigned_role_deleted": True,
            "test_rows_after": 0, "temporary_roles_after": 0}
