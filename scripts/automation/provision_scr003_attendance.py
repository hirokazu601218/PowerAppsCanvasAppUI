"""Provision the three SCR-003 Dataverse tables in the isolated test environment.

No rows, roles, users, or app sharing are changed. An existing target table
is a hard stop so its metadata can be compared with the approved contract.
"""
import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "config/dataverse/scr003-attendance-columns.json").read_text())
URL = "https://orge762dd9e.crm7.dynamics.com"
ORG = "9efe0732-a9b0-f111-8ade-002248f061b1"
SOLUTION = "StaffMasterAutomation"
SCHEMAS = {
    "report": "crb3c_AttendanceReport",
    "detail": "crb3c_AttendanceReportLine",
    "target_month": "crb3c_AttendanceTargetMonth",
}


def label(value, lcid):
    return {"LocalizedLabels": [{"Label": value, "LanguageCode": lcid}]}


def attr(field, lcid):
    key = field["key"]
    value = {
        "SchemaName": "crb3c_" + "".join(s.title() for s in key.split("_")),
        "DisplayName": label(field["display_name"], lcid),
        "RequiredLevel": {"Value": "ApplicationRequired" if field["required"] else "None"},
    }
    kind = field["kind"]
    if kind in ("text", "lookup_user"):
        # User references are kept as native Dataverse lookups, never strings.
        if kind == "lookup_user":
            return None
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                      "MaxLength": field["max_length"], "FormatName": {"Value": "Text"}})
    elif kind == "date_only":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
                      "Format": "DateOnly", "DateTimeBehavior": {"Value": "DateOnly"}})
    elif kind == "datetime":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
                      "Format": "DateAndTime", "DateTimeBehavior": {"Value": "UserLocal"}})
    elif kind == "integer":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
                      "MinValue": field["min"], "MaxValue": field["max"], "Format": "None"})
    elif kind == "decimal":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
                      "MinValue": field["min"], "MaxValue": field["max"],
                      "Precision": field["precision"]})
    elif kind == "boolean":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
                      "DefaultValue": False, "OptionSet": {"TrueOption": {"Value": 1, "Label": label("対象", lcid)},
                                                     "FalseOption": {"Value": 0, "Label": label("対象外", lcid)}}})
    elif kind == "choice":
        value.update({"@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
                      "OptionSet": {"IsGlobal": False, "OptionSetType": "Picklist",
                                    "Options": [{"Value": 100000000 + i, "Label": label(s, lcid)}
                                                for i, s in enumerate(field["values"])]}})
    else:
        raise ValueError(kind)
    return value


def table(entity, lcid):
    fields = [attr(f, lcid) for f in entity["fields"]]
    fields = [f for f in fields if f is not None]
    fields.append({"@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                   "SchemaName": "crb3c_Name", "DisplayName": label("レコード名", lcid),
                   "RequiredLevel": {"Value": "ApplicationRequired"}, "MaxLength": 100,
                   "IsPrimaryName": True, "FormatName": {"Value": "Text"}})
    return {"@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
            "SchemaName": SCHEMAS[entity["key"]], "DisplayName": label(entity["display_name"], lcid),
            "DisplayCollectionName": label(entity["display_name"], lcid),
            "Description": label("SCR-003勤務時間報告。検証環境。アクセス制御設定前は実データ禁止。", lcid),
            "OwnershipType": "UserOwned", "IsActivity": False, "HasActivities": False,
            "HasNotes": False, "Attributes": fields}


def relationship(name, parent, child, lookup_name, display, lcid):
    return {"@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
            "SchemaName": name, "ReferencedEntity": parent,
            "ReferencedAttribute": parent + "id", "ReferencingEntity": child,
            "ReferencingEntityNavigationPropertyName": lookup_name,
            "ReferencedEntityNavigationPropertyName": name,
            "AssociatedMenuConfiguration": {"Behavior": "UseCollectionName", "Group": "Details",
                                            "Label": label(display, lcid), "Order": 10000},
            "CascadeConfiguration": {"Assign": "NoCascade", "Delete": "Restrict",
                                     "Merge": "NoCascade", "Reparent": "NoCascade",
                                     "Share": "NoCascade", "Unshare": "NoCascade",
                                     "RollupView": "NoCascade"},
            "Lookup": {"@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
                       "SchemaName": lookup_name, "DisplayName": label(display, lcid),
                       "RequiredLevel": {"Value": "ApplicationRequired" if child.endswith("reportline") else "None"}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["preflight", "provision", "verify"], required=True)
    mode = parser.parse_args().mode
    token = subprocess.check_output(["az", "account", "get-access-token", "--resource", URL,
                                     "--query", "accessToken", "--output", "tsv"],
                                    text=True, timeout=45).strip()

    def api(path, method="GET", body=None):
        request = urllib.request.Request(URL + "/api/data/v9.2/" + path,
            data=json.dumps(body).encode() if body is not None else None, method=method,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "Content-Type": "application/json", "OData-Version": "4.0",
                     "OData-MaxVersion": "4.0", "MSCRM.SolutionUniqueName": SOLUTION})
        try:
            with urllib.request.urlopen(request, timeout=150) as response:
                payload = response.read()
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Dataverse HTTP {exc.code}: {exc.read().decode(errors='replace')[:1500]}") from None

    assert api("WhoAmI")["OrganizationId"].lower() == ORG, "Wrong organization"
    solution = api("solutions?$select=uniquename,ismanaged&$filter=uniquename%20eq%20'" +
                   SOLUTION + "'&$expand=publisherid($select=customizationprefix)")["value"]
    assert len(solution) == 1 and not solution[0]["ismanaged"]
    assert solution[0]["publisherid"]["customizationprefix"] == "crb3c"
    lcid = api("organizations?$select=languagecode")["value"][0]["languagecode"]
    found = {}
    for entity in SPEC["entities"]:
        logical = entity["logical_name"]
        found[logical] = api("EntityDefinitions?$select=LogicalName&$filter=LogicalName%20eq%20'" + logical + "'")["value"]
    if mode == "preflight":
        assert not any(found.values()), "Existing target table: compare metadata and ask user before changing"
        print(json.dumps({"mode": mode, "organization_verified": True, "tables_absent": list(found)}, ensure_ascii=False))
        return
    if mode == "provision" and any(found.values()):
        raise RuntimeError("Target table exists; stop and compare metadata before changing")
    if mode == "provision":
        for entity in SPEC["entities"]:
            api("EntityDefinitions", "POST", table(entity, lcid))
            print("CREATED_TABLE", entity["logical_name"], flush=True)
        rels = [("crb3c_AttendanceReport_Lines", "crb3c_attendancereport",
                 "crb3c_attendancereportline", "crb3c_AttendanceReportId", "勤務時間報告"),
                ("crb3c_AttendanceReport_ReportedBy", "systemuser",
                 "crb3c_attendancereport", "crb3c_ReportedBy", "報告者"),
                ("crb3c_AttendanceReport_ReopenedBy", "systemuser",
                 "crb3c_attendancereport", "crb3c_ReopenedBy", "戻した給与班担当")]
        for name, parent, child, lookup, display in rels:
            rel = relationship(name, parent, child, lookup, display, lcid)
            if parent == "systemuser":
                rel["ReferencedAttribute"] = "systemuserid"
            api("RelationshipDefinitions", "POST", rel)
            print("CREATED_RELATIONSHIP", name, flush=True)
        api("PublishXml", "POST", {"ParameterXml": "<importexportxml><entities>" +
            "".join("<entity>" + e["logical_name"] + "</entity>" for e in SPEC["entities"]) +
            "</entities></importexportxml>"})
    for entity in SPEC["entities"]:
        meta = api("EntityDefinitions(LogicalName='" + entity["logical_name"] +
                   "')?$select=LogicalName,OwnershipType,PrimaryNameAttribute,PrimaryIdAttribute&$expand=Attributes")
        assert meta["OwnershipType"] == "UserOwned"
        actual = {a["LogicalName"]: a for a in meta["Attributes"]}
        for field in entity["fields"]:
            expected = attr(field, lcid)
            if expected is None:
                continue
            logical = expected["SchemaName"].lower()
            assert logical in actual, logical
            observed = actual[logical]
            for prop in ("MaxLength", "MinValue", "MaxValue", "Precision"):
                if prop in expected:
                    assert observed[prop] == expected[prop], (logical, prop)
        print("VERIFIED_TABLE", entity["logical_name"], len(entity["fields"]), flush=True)


if __name__ == "__main__":
    main()
