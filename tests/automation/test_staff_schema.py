import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/automation'))
from staff_schema import table,payload
from staff_data_contract import validate


class StaffSchemaTests(unittest.TestCase):
    def test_fixture_has_valid_types_and_preserves_leading_zero(self):
        rows=json.loads((ROOT/'tests/fixtures/staff-basic-5.json').read_text())
        validate(rows)
        for row in rows:
            converted=payload(row)
            self.assertEqual(converted['crb3c_staffnumber'],row['staffnumber'])
            self.assertIn(converted['crb3c_taxclass'],[100000000,100000001])
        self.assertNotIn('crb3c_hiredate',payload(rows[0]))
        self.assertNotIn('crb3c_pension',payload(rows[0]))
        self.assertEqual(payload(rows[2])['crb3c_hiredate'],'2026-04-01T00:00:00Z')

    def test_metadata_preserves_approved_contract(self):
        m=table(1041)
        cols={x['SchemaName']:x for x in m['Attributes']}
        self.assertEqual(len(cols),24)
        required={k for k,v in cols.items() if v['RequiredLevel']['Value']=='ApplicationRequired'}
        self.assertEqual(required,{'crb3c_staffnumber','crb3c_taxclass'})
        self.assertTrue(cols['crb3c_staffnumber']['IsPrimaryName'])
        self.assertNotIn('crb3c_status',cols)
        self.assertNotIn('crb3c_residenttax',cols)
        self.assertEqual(cols['crb3c_hiredate']['DateTimeBehavior']['Value'],'DateOnly')
        self.assertNotIn('DefaultFormValue',cols['crb3c_pension'])


if __name__=='__main__': unittest.main()
