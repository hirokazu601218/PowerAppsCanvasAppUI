import copy
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/automation'))
from commute_schema import FIELDS, attributes, build_fixtures, relationship, validate_rows
from staff_schema import payload


class CommuteTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((ROOT / 'tests/fixtures/commute-6.json').read_text())
        ids = {r['data']['crb3c_staffnumber']: r['parent_id'] for r in self.rows}
        self.parents = [payload(p) for p in json.loads((ROOT / 'tests/fixtures/staff-basic-25.json').read_text())]
        for p in self.parents:
            p['crb3c_staffbasicid'] = ids.get(p['crb3c_staffnumber'], 'unused-zero-child-parent')

    def test_live_snapshot_fixture_matches_existing_staff_contract(self):
        validate_rows(self.rows, self.parents)
        self.assertEqual(self.rows, build_fixtures(self.parents, 'crb3c_staffbasicid'))
        counts = Counter(r['data']['crb3c_staffnumber'] for r in self.rows)
        self.assertEqual(counts['009900000003'], 2)
        self.assertEqual(len(counts), 5)
        self.assertEqual(sum(p['crb3c_staffnumber'] not in counts for p in self.parents), 20)
        self.assertEqual(counts['009900000011'], 1)
        self.assertEqual(counts['009900000012'], 0)  # Same name must not become the key.

    def test_rejects_orphan_wrong_guid_and_name(self):
        for field, value in [('crb3c_staffnumber', '009900999999'), ('crb3c_fullname', 'wrong')]:
            rows = copy.deepcopy(self.rows)
            rows[0]['data'][field] = value
            with self.assertRaises(AssertionError):
                validate_rows(rows, self.parents)
        self.rows[0]['parent_id'] = 'wrong-guid'
        with self.assertRaises(AssertionError):
            validate_rows(self.rows, self.parents)

    def test_rejects_dates_outside_employment_and_parent_amount_mismatch(self):
        for idx, field, value in [(0, 'crb3c_startdate', '2026-03-01'), (2, 'crb3c_enddate', '2026-04-01'), (3, 'crb3c_icfare', 100)]:
            rows = copy.deepcopy(self.rows)
            rows[idx]['data'][field] = value
            with self.assertRaises(AssertionError):
                validate_rows(rows, self.parents)

    def test_optional_null_zero_and_numeric_limits_are_distinct(self):
        self.assertIsNone(self.rows[0]['data']['crb3c_route2_passmonths'])
        self.assertEqual(self.rows[3]['data']['crb3c_month04'], 0)
        for field, value in [('crb3c_month04', -1), ('crb3c_sixmonthpass', 2), ('crb3c_route1_paymonth', 13)]:
            rows = copy.deepcopy(self.rows)
            rows[0]['data'][field] = value
            with self.assertRaises(AssertionError):
                validate_rows(rows, self.parents)

    def test_schema_preserves_84_optional_fields_and_non_cascading_relation(self):
        self.assertEqual(len(FIELDS), 84)
        self.assertEqual(len({f['logical_name'] for f in FIELDS}), 84)
        attrs = attributes(1041)
        self.assertTrue(all(a['RequiredLevel']['Value'] == 'None' for a in attrs[:-1]))
        self.assertEqual(len(attrs), 85)
        rel = relationship(1041, 'crb3c_staffbasicid')
        self.assertEqual(rel['ReferencedEntity'], 'crb3c_staffbasic')
        self.assertEqual(rel['ReferencingEntity'], 'crb3c_commute')
        self.assertEqual(rel['Lookup']['RequiredLevel']['Value'], 'ApplicationRequired')
        self.assertEqual(rel['CascadeConfiguration']['Delete'], 'Restrict')
        self.assertTrue(all(v == 'NoCascade' for k, v in rel['CascadeConfiguration'].items() if k != 'Delete'))


if __name__ == '__main__':
    unittest.main()
