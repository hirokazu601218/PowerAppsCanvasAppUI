"""Static/local-model tests, not a substitute for Studio compilation or E2E."""
import copy
import json
import re
import sys
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/automation'))
from prepare_commute_v118 import candidate, mappings, nodes, OUT


class CommuteAppCandidateTests(unittest.TestCase):
    def setUp(self):
        self.changes = candidate()
        self.by = {(c['control'], c['property']): c['after'] for c in self.changes}
        self.fixtures = json.loads((ROOT / 'tests/fixtures/commute-6.json').read_text())

    def test_every_existing_ledger_field_has_exactly_one_mapping(self):
        source = (ROOT / 'powerapps/canvas-v3/Src/Screen1.pa.yaml').read_text()
        expected = set(re.findall(r'Field="([a-z0-9_]+)"', source))
        field_map = mappings()
        self.assertEqual(len(field_map), 69)
        self.assertEqual(len({m['field'] for m in field_map}), 69)
        self.assertEqual({m['field'] for m in field_map}, expected)
        columns = {f['logical_name'] for f in json.loads((ROOT / 'config/dataverse/commute-columns.json').read_text())['fields']}
        self.assertTrue(all(m['column'] in columns for m in field_map if m['source'] == 'commute'))

    def test_removes_all_old_commute_values_and_template_references(self):
        app = self.by['App', 'Formulas']
        for text in ['StaffCommuteHistory = Table(', 'StaffLedgerTemplate', 'TEST-TK-', 'C-3-2026', 'LedgerFrom:', 'LedgerPass:']:
            self.assertNotIn(text, app)
        screen = yaml.safe_load((ROOT / 'powerapps/canvas-v3/Src/Screen1.pa.yaml').read_text())
        controls = {n: v for n, v, _ in nodes(screen)}
        for c in self.changes:
            if c['control'] != 'App':
                controls[c['control']]['Properties'][c['property']] = c['after']
        after = json.dumps(screen, ensure_ascii=False)
        for token in ['demoCommute', 'StaffLedgerTemplate', 'c.LedgerPass', 'c.LedgerFrom', 'c.LedgerTo']:
            self.assertNotIn(token, after)
        self.assertIn("Filter('T_通勤', '職員基本'.職員番号 = StaffSelected.StaffId)", app)
        self.assertNotIn("ForAll('T_通勤'", app)

    def test_selection_uses_record_guid_and_rejects_old_staff(self):
        click = self.by['btnCertificate111', 'OnSelect']
        self.assertIn('galCommute111.Selected', click)
        self.assertIn('c.職員基本.職員番号 <> s.StaffId', click)
        self.assertIn('Set(varLedgerCommute111,c)', click)
        self.assertIn('ClearCollect(colLedgerFields111,StaffLedgerFields)', click)
        for name in ['btnLoad111', 'btnSearch111', 'btnClear111', 'galStaff111']:
            self.assertIn('Set(varLedgerCommute111,Blank())', self.by[name, 'OnSelect'])
            self.assertIn('Set(varLedgerPdf111,Blank())', self.by[name, 'OnSelect'])
        self.assertIn("Refresh('T_通勤')", self.by['btnLoad111', 'OnSelect'])

    def test_two_periods_zero_blank_future_and_same_name_expected_values(self):
        rows = {r['data']['crb3c_recognitionid']: r['data'] for r in self.fixtures}
        fm = {m['field']: m['column'] for m in mappings() if m['source'] == 'commute'}
        # Expectations are independently stated against the workbook/seed cases.
        self.assertEqual(rows['TK-910001'][fm['route_1_season_amount']], 7800)
        self.assertEqual(rows['TK-910002'][fm['route_1_season_amount']], 8400)
        self.assertEqual(rows['TK-910002'][fm['event_date_month']], '2026-10-01')
        self.assertEqual(rows['TK-910003'][fm['route_1_other_amount']], 16800)
        self.assertEqual(rows['TK-910003'][fm['route_1_other_basis']], 40)
        self.assertEqual(rows['TK-910004'][fm['monthly_amount_total']], 0)
        self.assertIsNone(rows['TK-910004'][fm['route_1_season_amount']])
        self.assertIsNone(rows['TK-910001'][fm['route_2_transport']])
        self.assertEqual(rows['TK-910006'][fm['event_date_year']], '2099-04-01')
        self.assertFalse(any(r['crb3c_staffnumber'] == '009900000012' for r in rows.values()))

    def test_candidate_fixture_preserves_other_histories(self):
        before = json.loads((ROOT / 'tests/fixtures/staff-history-synthetic.json').read_text())
        after = json.loads((OUT / 'staff-history-synthetic.json').read_text())
        self.assertEqual(set(before) - set(after), {'Commute', 'LedgerTemplate'})
        for key in after:
            self.assertEqual(after[key], before[key])
        # Re-running the proposed renderer must retain Dataverse formulas.
        namespace = {'__file__': str(ROOT / 'scripts/automation/render_staff_history.py'), '__name__': 'candidate_renderer'}
        exec(compile((OUT / 'render_staff_history.py').read_text(), 'candidate_renderer', 'exec'), namespace)
        app = self.by['App', 'Formulas']
        prefix, _ = app.split(namespace['MARKER'])
        self.assertEqual(prefix + namespace['render'](after), app)


if __name__ == '__main__':
    unittest.main()
