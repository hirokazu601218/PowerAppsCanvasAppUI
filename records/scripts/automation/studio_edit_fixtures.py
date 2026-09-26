"""Seed synthetic records into the three isolated Studio tables only."""

import json
import uuid
from pathlib import Path

import commute_schema
import payrollledger_schema
import staff_schema


ROOT = Path(__file__).resolve().parents[2]


def seed(api, metas):
    parent, commute, payroll = metas
    names = ("crb3c_studiostaffbasic", "crb3c_studiocommute",
             "crb3c_studiopayrollledger")
    if tuple(m["LogicalName"] for m in metas) != names:
        raise RuntimeError("Studio table identity mismatch; no fixture writes")
    sets = [m["EntitySetName"] for m in metas]
    ids = [m["PrimaryIdAttribute"] for m in metas]
    staff_rows = json.loads((ROOT / "tests/fixtures/staff-basic-25.json").read_text())
    assert len(staff_rows) == 25
    staff_schema_rows = staff_schema.payload

    parent_keys = {str(uuid.uuid5(uuid.NAMESPACE_URL,
                   "studio-edit/staff/" + row["staffnumber"])) for row in staff_rows}
    existing_parents = {row[ids[0]] for row in
                        api(sets[0] + "?$select=" + ids[0])["value"]}
    if not existing_parents <= parent_keys:
        raise RuntimeError("Unexpected Studio parent; no fixture writes")
    for row in staff_rows:
        sid = row["staffnumber"]
        key = str(uuid.uuid5(uuid.NAMESPACE_URL, "studio-edit/staff/" + sid))
        payload = {**staff_schema_rows(row), ids[0]: key}
        if key not in existing_parents:
            api(sets[0] + "(" + key + ")", "PATCH", payload, {"If-None-Match": "*"})

    parents = api(sets[0] + "?$orderby=crb3c_staffnumber")["value"]
    if len(parents) != 25:
        raise RuntimeError("Studio parent seed count mismatch")
    # Existing fixture validators use this legacy key for parent identity.
    for item in parents:
        item["crb3c_staffbasicid"] = item[ids[0]]
    counts = [25]
    for index, module in ((1, commute_schema), (2, payrollledger_schema)):
        records = module.build_fixtures(parents, ids[0])
        module.validate_rows(records, parents)
        relation = ("crb3c_studiostaffbasic_commute" if index == 1
                    else "crb3c_studiostaffbasic_payrollledger")
        observed = api("RelationshipDefinitions(SchemaName='" + relation +
                       "')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
        if observed["ReferencedEntity"] != names[0] or observed["ReferencingEntity"] != names[index]:
            raise RuntimeError("Studio relationship identity mismatch")
        nav = observed["ReferencingEntityNavigationPropertyName"]
        fixture_keys = {str(uuid.uuid5(uuid.NAMESPACE_URL, "studio-edit/" + names[index] +
                        "/" + item["data"]["crb3c_name"])) for item in records}
        existing = {row[ids[index]] for row in
                    api(sets[index] + "?$select=" + ids[index])["value"]}
        if not existing <= fixture_keys:
            raise RuntimeError("Unexpected Studio child; no fixture writes: " + names[index])
        for item in records:
            sid = item["data"]["crb3c_staffnumber"]
            key = str(uuid.uuid5(uuid.NAMESPACE_URL, "studio-edit/" + names[index] +
                                 "/" + item["data"]["crb3c_name"]))
            data = {**item["data"], ids[index]: key,
                    nav + "@odata.bind": "/" + sets[0] +
                    "(crb3c_staffnumber='" + sid + "')"}
            if key not in existing:
                api(sets[index] + "(" + key + ")", "PATCH", data, {"If-None-Match": "*"})
        counts.append(len(records))
    for set_name, key, expected in zip(sets, ids, counts):
        count = len(api(set_name + "?$select=" + key)["value"])
        if count != expected:
            raise RuntimeError("Studio fixture count mismatch: " + set_name)
    return dict(zip(names, counts))
