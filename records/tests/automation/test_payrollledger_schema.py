import copy,json,sys,unittest
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/automation'))
from payrollledger_schema import FIELDS,attributes,relationship,build_fixtures,validate_rows
from staff_schema import payload
class PayrollLedgerTests(unittest.TestCase):
    def setUp(self):
        self.parents=[payload(r) for r in json.loads((ROOT/'tests/fixtures/staff-basic-25.json').read_text())]
        for p in self.parents:p['crb3c_staffbasicid']='fixture-'+p['crb3c_staffnumber']
        self.rows=build_fixtures(self.parents,'crb3c_staffbasicid')
    def test_definition_163_types_and_parent_contract(self):
        self.assertEqual(len(FIELDS),163)
        self.assertEqual(len({f['logical_name'] for f in FIELDS}),163)
        self.assertEqual(Counter(f['kind'] for f in FIELDS),{'text':14,'integer':147,'decimal':2})
        self.assertTrue(all(a['RequiredLevel']['Value']=='None' for a in attributes(1033)[:-1]))
        r=relationship(1033,'crb3c_staffbasicid')
        self.assertEqual(r['ReferencedEntity'],'crb3c_staffbasic')
        self.assertEqual(r['ReferencingEntity'],'crb3c_payrollledger')
        self.assertEqual(r['CascadeConfiguration']['Delete'],'Restrict')
    def test_valid_records_zero_one_many_same_names_and_net_math(self):
        validate_rows(self.rows,self.parents)
        counts=Counter(r['data']['crb3c_staffnumber'] for r in self.rows)
        self.assertEqual(len(self.rows),7)
        self.assertEqual(counts['009900000003'],3)
        self.assertEqual(counts['009900000011'],1)
        self.assertEqual(counts['009900000012'],1)
        self.assertEqual(len(self.parents)-len(counts),20)
        self.assertEqual(self.rows[4]['data']['crb3c_fullname'],self.rows[5]['data']['crb3c_fullname'])
        self.assertNotEqual(self.rows[4]['parent_id'],self.rows[5]['parent_id'])
    def test_reject_orphan_wrong_parent_name_and_organization(self):
        for key,v in [('staffnumber','009900999999'),('fullname','wrong'),('organization','wrong')]:
            rows=copy.deepcopy(self.rows);rows[0]['data']['crb3c_'+key]=v
            with self.assertRaises(AssertionError):validate_rows(rows,self.parents)
        self.rows[0]['parent_id']='wrong'
        with self.assertRaises(AssertionError):validate_rows(self.rows,self.parents)
    def test_reject_pre_hire_post_retirement_and_wrong_totals(self):
        for idx,key,value in [(0,'period_start','03月01日'),(3,'period_end','04月30日'),(0,'gross',1),(0,'transfer1',1),(0,'social_total_current',1)]:
            rows=copy.deepcopy(self.rows);rows[idx]['data']['crb3c_'+key]=value
            with self.assertRaises(AssertionError):validate_rows(rows,self.parents)
    def test_signed_adjustments_hours_precision_and_optional_null(self):
        validate_rows(self.rows,self.parents)
        self.assertLess(self.rows[2]['data']['crb3c_basepay_adjustment'],0)
        self.assertIsNone(self.rows[0]['data']['crb3c_salary_table'])
        self.rows[0]['data']['crb3c_reduction_hours_current']=1.25
        validate_rows(self.rows,self.parents)
        self.rows[0]['data']['crb3c_basepay_current']=1.5
        with self.assertRaises(AssertionError):validate_rows(self.rows,self.parents)
if __name__=='__main__':unittest.main()
