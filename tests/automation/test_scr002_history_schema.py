import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/automation"))
from scr002_history_schema import SPEC, attributes, relationship, table


class SchemaContract(unittest.TestCase):
    def test_all_source_columns_and_names(self):
        self.assertEqual([len(t["columns"]) for t in SPEC["tables"]], [15, 26, 9, 6])
        for spec in SPEC["tables"]:
            self.assertEqual(spec["columns"][0]["display_name"], "職員番号")
            self.assertEqual(spec["columns"][1]["display_name"], "氏名")
            for studio in (False, True):
                definition = table(spec, studio, 1041)
                self.assertEqual(len(definition["Attributes"]), len(spec["columns"]) + 1)
                self.assertEqual(len({a["SchemaName"] for a in definition["Attributes"]}),
                                 len(definition["Attributes"]))
                self.assertEqual(definition["Attributes"][0]["MaxLength"], 200)
                self.assertEqual(definition["OwnershipType"], "UserOwned")

    def test_types_and_parent_relationships(self):
        social = SPEC["tables"][1]
        attrs = {a["SchemaName"]: a for a in attributes(social, 1041)}
        self.assertEqual(attrs["crb3c_birthdate"]["DateTimeBehavior"]["Value"], "DateOnly")
        self.assertEqual(attrs["crb3c_multiemployerpensionamount"]["Precision"], 2)
        for studio, parent in ((False, "crb3c_staffbasic"),
                               (True, "crb3c_studiostaffbasic")):
            relation = relationship(social, studio, 1041, parent + "id")
            self.assertEqual(relation["ReferencedEntity"], parent)
            self.assertEqual(relation["CascadeConfiguration"]["Delete"], "Restrict")
            self.assertEqual(relation["Lookup"]["RequiredLevel"]["Value"],
                             "ApplicationRequired")


if __name__ == "__main__":
    unittest.main()
