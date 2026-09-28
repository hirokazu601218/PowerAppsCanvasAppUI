"""Exact metadata for the four SCR-002 history workbooks (no personnel records)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "config/dataverse/scr002-history-columns.json").read_text())


def label(value, lcid):
    return {"LocalizedLabels": [{"Label": value, "LanguageCode": lcid}]}


def names(spec, studio):
    return (spec["studio_logical_name"], spec["studio_schema_name"]) if studio else (
        spec["logical_name"], spec["schema_name"])


def attributes(spec, lcid):
    result = []
    for field in spec["columns"]:
        item = {
            "SchemaName": field["logical_name"],
            "DisplayName": label(field["display_name"], lcid),
            "Description": label(field["source_constraint"], lcid),
            "RequiredLevel": {"Value": "None"},
        }
        kind = field["kind"]
        if kind == "text":
            item.update({"@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                         "MaxLength": field["max_length"], "FormatName": {"Value": "Text"}})
        elif kind == "date":
            item.update({"@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
                         "Format": "DateOnly", "DateTimeBehavior": {"Value": "DateOnly"}})
        elif kind == "integer":
            item.update({"@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
                         "MinValue": field["min"], "MaxValue": field["max"], "Format": "None"})
        elif kind == "decimal":
            item.update({"@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
                         "MinValue": field["min"], "MaxValue": field["max"],
                         "Precision": field["precision"]})
        else:
            raise ValueError(kind)
        result.append(item)
    result.append({
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": "crb3c_name",
        "DisplayName": label("履歴レコード名", lcid),
        "RequiredLevel": {"Value": "ApplicationRequired"},
        "MaxLength": 100, "IsPrimaryName": True,
        "FormatName": {"Value": "Text"},
    })
    return result


def table(spec, studio, lcid):
    logical, schema = names(spec, studio)
    display = spec["display_name"] + ("_STUDIO" if studio else "")
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
        "SchemaName": schema,
        "DisplayName": label(display, lcid),
        "DisplayCollectionName": label(display, lcid),
        "Description": label("SCR-002履歴。添付の列定義に準拠。" + (
            "隔離された架空データの画面試験用。" if studio else "本番移行前は空表。"), lcid),
        "OwnershipType": "UserOwned", "IsActivity": False,
        "HasActivities": False, "HasNotes": False,
        "Attributes": attributes(spec, lcid),
    }


def relationship(spec, studio, lcid, parent_id):
    logical, _ = names(spec, studio)
    suffix = spec["key"]
    parent = "crb3c_studiostaffbasic" if studio else "crb3c_staffbasic"
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
        "SchemaName": "crb3c_" + ("studiostaffbasic_" if studio else "staffbasic_") + suffix,
        "ReferencedEntity": parent, "ReferencedAttribute": parent_id,
        "ReferencingEntity": logical,
        "ReferencingEntityNavigationPropertyName": "crb3c_StaffBasic",
        "ReferencedEntityNavigationPropertyName": "crb3c_StaffBasic_" + suffix.title() +
        ("Studio" if studio else ""),
        "AssociatedMenuConfiguration": {
            "Behavior": "UseCollectionName", "Group": "Details",
            "Label": label(spec["display_name"], lcid), "Order": 10000,
        },
        "CascadeConfiguration": {
            "Assign": "NoCascade", "Delete": "Restrict", "Merge": "NoCascade",
            "Reparent": "NoCascade", "Share": "NoCascade", "Unshare": "NoCascade",
            "RollupView": "NoCascade",
        },
        "Lookup": {
            "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
            "SchemaName": "crb3c_StaffBasicId", "DisplayName": label("職員基本", lcid),
            "Description": label("12桁職員番号で照合した親レコードの参照", lcid),
            "RequiredLevel": {"Value": "ApplicationRequired"},
        },
    }
