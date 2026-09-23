"""Verify and remove only this Work's disposable Studio row and unused role."""

import urllib.parse


ROLE_NAME = "StaffMaster Studio CRUD"
LEFTOVER_NUMBER = "009900009999"
CRUD_NUMBERS = ("009900009997", "009900009996")
TEST_NUMBERS = (LEFTOVER_NUMBER, *CRUD_NUMBERS)


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
    if len(rows) > 2 or len({r["crb3c_staffnumber"] for r in rows}) != len(rows):
        raise RuntimeError("Unexpected matching test rows; refusing cleanup")
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
            "test_row_created_by_dedicated_user": any(
                r["crb3c_staffnumber"] == LEFTOVER_NUMBER and r["_createdby_value"] == uid
                for r in rows),
            "temporary_roles": role_checks}


def verify_crud(api, meta, prior):
    if any(r["crb3c_staffnumber"] in CRUD_NUMBERS for r in prior["test_rows"]):
        raise RuntimeError("Previous CRUD test row remains; refusing duplicate creation")
    uid = prior["dedicated_user_id"]
    table = prior["table_set"]
    key = prior["primary_id"]
    caller = {"MSCRMCallerID": uid}
    api(table, "POST", {"crb3c_staffnumber": CRUD_NUMBERS[0]}, caller)
    rows = _query(api, table, **{"$select": key + ",crb3c_staffnumber,_createdby_value",
        "$filter": "crb3c_staffnumber eq '" + CRUD_NUMBERS[0] + "'"})
    if len(rows) != 1 or rows[0]["_createdby_value"] != uid:
        raise RuntimeError("Dedicated user impersonated create did not persist")
    path = table + "(" + rows[0][key] + ")"
    api(path, "PATCH", {"crb3c_staffnumber": CRUD_NUMBERS[1]},
        {**caller, "If-Match": "*"})
    changed = api(path + "?$select=crb3c_staffnumber")
    if changed["crb3c_staffnumber"] != CRUD_NUMBERS[1]:
        raise RuntimeError("Dedicated user impersonated update did not persist")
    api(path, "DELETE", extra_headers={**caller, "If-Match": "*"})
    after = _query(api, table, **{"$select": key,
        "$filter": " or ".join("crb3c_staffnumber eq '" + n + "'" for n in CRUD_NUMBERS)})
    if after:
        raise RuntimeError("Dedicated user impersonated delete did not persist")
    return {"create": True, "update": True, "delete": True,
            "execution_context": "MSCRMCallerID", "temporary_records_after": 0}


def cleanup(api, cfg, meta, prior):
    roles = prior["temporary_roles"]
    if len(roles) != 1 or roles[0]["users"] or roles[0]["teams"]:
        raise RuntimeError("Temporary role is absent, ambiguous, or assigned")
    for row in prior["test_rows"]:
        path = prior["table_set"] + "(" + row[prior["primary_id"]] + ")"
        api(path, "DELETE", extra_headers={"If-Match": "*"})
    rid = roles[0]["id"]
    if _query(api, "roles(" + rid + ")/systemuserroles_association",
              **{"$select": "systemuserid"}) or _query(
                  api, "roles(" + rid + ")/teamroles_association",
                  **{"$select": "teamid"}):
        raise RuntimeError("Temporary role was assigned during cleanup")
    api("roles(" + rid + ")", "DELETE", extra_headers={"If-Match": "*"})
    after = audit(api, cfg, meta)
    if after["test_rows"] or after["temporary_roles"]:
        raise RuntimeError("Cleanup did not remove the test row and role")
    return {"test_rows_deleted": len(prior["test_rows"]), "unassigned_role_deleted": True,
            "test_rows_after": 0, "temporary_roles_after": 0}
