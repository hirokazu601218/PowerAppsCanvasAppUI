"""Offline contracts for the generated HTML review package."""
from pathlib import Path
import importlib.util
import json
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[2]
class PayrollReviewTest(unittest.TestCase):
    def test_static_contract(self):
        result=subprocess.run(['python3','scripts/review/validate_payroll_review.py'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_generator_is_current(self):
        result=subprocess.run(['python3','scripts/review/generate_payroll_review.py','--check'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_approved_interface_and_deferred_formula(self):
        data=json.loads((ROOT/'docs/review/pay-html-001/data/model.json').read_text())
        combined=json.dumps(data,ensure_ascii=False)
        for decision in range(1,13):self.assertIn('I'+str(decision),combined)
        self.assertIn('D9',combined)
        screens={s['id']:s for s in data['screens']}
        self.assertEqual(screens['SCR-002']['tabs'],['基本情報','勤務条件','通勤','社会保険','税固定控除','給与簿'])
        self.assertEqual(screens['FUT-JLINK']['tabs'],['支給回の状況','出力','取込・照合'])
        home_to_trial=[o for o in data['operations'] if o['screen_id']=='SCR-001' and o['destination_screen_id']=='SCR-005']
        self.assertFalse(home_to_trial,'Old direct home-to-trial route must not be restored')
if __name__=='__main__':unittest.main()
