import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "automation"))

import studio_edit_schema as studio


class StudioEditSchemaTest(unittest.TestCase):
    def test_business_columns_match_original_and_names_are_separate(self):
        for i, (logical, schema, display, module) in enumerate(studio.TABLES):
            with self.subTest(table=logical):
                copy = studio.table_definition(i, 1041)
                original = module.table(1041)
                self.assertNotEqual(copy["SchemaName"], original["SchemaName"])
                self.assertEqual(copy["SchemaName"], schema)
                self.assertEqual(copy["DisplayName"]["LocalizedLabels"][0]["Label"], display)
                self.assertEqual(copy["Attributes"], original["Attributes"])
                self.assertEqual(copy["OwnershipType"], "UserOwned")
                self.assertEqual(original, module.table(1041))

    def test_children_refer_only_to_studio_parent_and_restrict_delete(self):
        for i in (1, 2):
            with self.subTest(child=i):
                child = studio.relationship_definition(i, 1041, "crb3c_studiostaffbasicid")
                self.assertEqual(child["ReferencedEntity"], studio.TABLES[0][0])
                self.assertEqual(child["ReferencingEntity"], studio.TABLES[i][0])
                self.assertEqual(child["ReferencedAttribute"], "crb3c_studiostaffbasicid")
                self.assertEqual(child["CascadeConfiguration"]["Delete"], "Restrict")
                self.assertNotIn("crb3c_staffbasic", child["SchemaName"])


if __name__ == "__main__":
    unittest.main()
