"""Serializer rule tests, not Canvas runtime tests."""
import copy
import importlib.util
from pathlib import Path
import unittest
import yaml
R=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('reader',R/'scripts/testing/check_payroll_readback.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
class Readback(unittest.TestCase):
    def setUp(self):
        self.expected=yaml.safe_load((R/'src/screen-ui/v1.31/payroll-root.pa.yaml').read_text())
        self.actual=copy.deepcopy(self.expected)
    def root(self):return self.actual['Screens']['scrPayroll']['Children'][0]['conscrPayrollRoot']
    def test_exact_pass(self):self.assertEqual(reader.compare(self.expected,self.actual)['normalized'],[])
    def test_only_root_start_omission_pass(self):
        del self.root()['Properties']['LayoutAlignItems']
        self.assertEqual(len(reader.compare(self.expected,self.actual)['normalized']),1)
    def test_wrong_or_null_root_alignment_rejected(self):
        for value in [None,'','=LayoutAlignItems.Stretch','=LayoutAlignItems.Center']:
            with self.subTest(value=value):
                self.root()['Properties']['LayoutAlignItems']=value
                with self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
    def test_four_child_omissions_or_stretch_rejected(self):
        for index in range(4):
            for value in [None,'=AlignInContainer.Stretch','=AlignInContainer.Start']:
                self.actual=copy.deepcopy(self.expected)
                props=next(iter(self.root()['Children'][index].values()))['Properties']
                if value is None:del props['AlignInContainer']
                else:props['AlignInContainer']=value
                with self.subTest(index=index,value=value),self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
    def test_unrelated_business_formula_rejected(self):
        self.root()['Children'][0]['conscrPayrollHeader']['Children'][1]['btnscrPayrollHome']['Properties']['OnSelect']='=false'
        with self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
    def test_structure_extra_or_reorder_rejected(self):
        for mode in ['reorder','extra']:
            self.actual=copy.deepcopy(self.expected)
            if mode=='reorder':self.root()['Children'].reverse()
            else:self.root()['Properties']['Other']='=0'
            with self.subTest(mode=mode),self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
    def test_implicit_expected_child_rejected(self):
        del self.expected['Screens']['scrPayroll']['Children'][0]['conscrPayrollRoot']['Children'][0]['conscrPayrollHeader']['Properties']['AlignInContainer']
        with self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
    def test_screen_property_mismatch_rejected(self):
        self.actual['Screens']['scrPayroll']['Properties']={'OnVisible':'=false'}
        with self.assertRaises(ValueError):reader.compare(self.expected,self.actual)
if __name__=='__main__':unittest.main()
