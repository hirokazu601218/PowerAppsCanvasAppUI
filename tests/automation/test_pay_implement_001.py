"""Offline delta checks only; these are not Power Fx execution or Player tests."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import hashlib
import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src/screen-ui/v1.31'
_spec = importlib.util.spec_from_file_location('wave1', ROOT / 'scripts/implementation/apply_pay_implement_001.py')
wave1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wave1)

class WaveOneTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SRC / 'manifest.json').read_text())
        self.root = yaml.safe_load((SRC / 'payroll-root.paste.yaml').read_text())[0]['conscrPayrollRoot']

    def baseline(self):
        # Reconstruct only the exact properties/structure required by the patcher;
        # no tenant URLs, personal data, authentication state or packaged app fixture.
        payroll = {'Children': [{'conscrPayrollRoot': copy.deepcopy(self.root)}]}
        staff = {'Properties': {}, 'Children': []}
        root = wave1.control(payroll, 'conscrPayrollRoot')
        summary = next(x for x in root['Children'] if 'conPaySummary' in x)
        root['Children'].remove(summary)
        wave1.control(root, 'conPayBody')['Children'].insert(1, summary)
        for change in self.manifest['changes']:
            if 'property' not in change:
                continue
            if change['screen'] == 'scrPayroll':
                wave1.control(payroll, change['control'])['Properties'][change['property']] = change['before']
            elif change.get('mode') == 'preserve_first_statement_replace_tail':
                staff['Properties']['OnVisible'] = '=Set(varCommuteReportBase111,"https://example.invalid/verified-existing-report");' + change['before_tail']
            else:
                staff['Children'].append({change['control']: {'Properties': {change['property']: change['before']}}})
        return {'scrStaffMasterSearch': staff, 'scrPayroll': payroll}

    def test_staff_fetch_failure_clears_inline_without_queued_select(self):
        text = (SRC / 'scrStaffMasterSearch.OnVisible.tail.fx').read_text()
        failure = text[text.index('Clear(colStaffSource111);Clear(colResult111);'):text.rindex('If(IsBlank(varFetchError111),Select(btnLoadDetails111));')]
        self.assertNotIn('Select(', failure)
        self.assertEqual(text.count('Select(btnLoadDetails111)'), 1)
        self.assertTrue(text.rstrip().endswith('If(IsBlank(varFetchError111),Select(btnLoadDetails111));'))
        for collection in ['colCommute111', 'colWork111', 'colSocial111', 'colTax111', 'colResident111', 'colHistory111', 'colHistorySelection111', 'colPayrollSource111', 'colPayrollColumns111', 'colPayrollExceptions111']:
            self.assertIn(f'Clear({collection})', failure)
        self.assertIn('Set(varStaffSource111,Blank())', failure)
        self.assertIn('Set(varHistoryId111,Blank())', failure)
        self.assertIn('Set(varFetched111,Blank())', failure)
        self.assertIn('Set(varFetchError111,"職員データを取得できませんでした：" & FirstError.Message)', failure)

    def test_full_readback_rejects_unexpected_file_and_untouched_app_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest = copy.deepcopy(self.manifest)
            for name in manifest['baseline']['source_files']:
                data = ('App: {}' if name == 'App.pa.yaml' else '_EditorState: {}' if name == '_EditorState.pa.yaml' else 'Screens: {}') + '\n'
                (directory / name).write_text(data)
                manifest['baseline']['source_files'][name] = wave1.sha(data)
            wave1.load_readback(directory, manifest)
            extra = directory / 'unexpectedScreen.pa.yaml'
            extra.write_text('Screens: {}\n')
            with self.assertRaisesRegex(ValueError, 'Unexpected readback source set'):
                wave1.load_readback(directory, manifest)
            extra.unlink()
            (directory / 'App.pa.yaml').write_text('App: {changed: true}\n')
            with self.assertRaisesRegex(ValueError, 'Full readback baseline mismatch: App'):
                wave1.load_readback(directory, manifest)

    def test_rejects_duplicate_control_names(self):
        baseline = self.baseline()
        baseline['scrStaffMasterSearch']['Children'].append(copy.deepcopy(baseline['scrStaffMasterSearch']['Children'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate control name'):
            wave1.apply(baseline, self.manifest)

    def test_preserves_existing_report_destination(self):
        baseline = self.baseline()
        after = wave1.apply(baseline, self.manifest)
        self.assertTrue(after['scrStaffMasterSearch']['Properties']['OnVisible'].startswith(
            '=Set(varCommuteReportBase111,"https://example.invalid/verified-existing-report");'))
        self.assertEqual(baseline, self.baseline(), 'apply must not mutate source baseline')

    def test_fails_closed_on_changed_formula(self):
        baseline = self.baseline()
        wave1.control(baseline['scrStaffMasterSearch'], 'btnSearch111')['Properties']['OnSelect'] += ';Notify("unreviewed")'
        with self.assertRaisesRegex(ValueError, 'Baseline mismatch'):
            wave1.apply(baseline, self.manifest)

    def test_fails_closed_on_unrelated_payroll_change(self):
        baseline = self.baseline()
        wave1.control(baseline['scrPayroll'], 'lblPayrollStaff')['Properties']['Text'] = '="unreviewed"'
        with self.assertRaisesRegex(ValueError, 'Payroll root differs'):
            wave1.apply(baseline, self.manifest)

    def test_preserves_all_control_properties_except_manifest(self):
        baseline = self.baseline()
        after = wave1.apply(baseline, self.manifest)
        def properties(screen):
            found = {}
            def visit(root):
                for node in root.get('Children', []):
                    for name, value in node.items():
                        self.assertNotIn(name, found)
                        found[name] = value.get('Properties', {})
                        visit(value)
            visit(screen)
            return found
        for name in baseline:
            old, new = properties(baseline[name]), properties(after[name])
            self.assertEqual(set(old), set(new), 'No controls added, lost or renamed')
            approved = {(c['control'], c['property']) for c in self.manifest['changes'] if c['screen'] == name and 'property' in c}
            for control in old:
                for prop in set(old[control]) | set(new[control]):
                    if old[control].get(prop) != new[control].get(prop):
                        self.assertIn((control, prop), approved)

    def test_payroll_summary_is_fixed_sibling_not_scrolling_child(self):
        children = [next(iter(x)) for x in self.root['Children']]
        self.assertEqual(children, ['conscrPayrollHeader', 'conPayrollTargets', 'conPaySummary', 'conPayBody'])
        body = wave1.control(self.root, 'conPayBody')
        self.assertIsNone(wave1.control(body, 'conPaySummary'))
        self.assertEqual(body['Properties']['Height'], '=Max(0,Parent.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height)')
        self.assertEqual(body['Properties']['LayoutOverflowY'], '=LayoutOverflow.Scroll')
        self.assertIsNotNone(wave1.control(body, 'lblPayDeductionName7'))

    def test_all_eight_basis_labels_share_amount_validity_guard(self):
        for i in range(8):
            basis = wave1.control(self.root, f'lblPayDeductionBasis{i}')['Properties']['Text']
            self.assertEqual(basis, f'=If(UiReady,If(Month(UiMonth)=11,"登録済み0円（仮例）",Index(UiDeductionRows,{i+1}).Basis),"算定根拠　—")')
            amount = wave1.control(self.root, f'lblPayDeductionAmount{i}')['Properties']['Text']
            self.assertTrue(amount.startswith('=If(UiReady,'))

    def test_paste_and_pa_children_are_equal(self):
        pa = yaml.safe_load((SRC / 'payroll-root.pa.yaml').read_text())
        self.assertEqual(pa['Screens']['scrPayroll']['Children'], [{'conscrPayrollRoot': self.root}])

    def test_search_captures_committed_controls_before_filter(self):
        text = (SRC / 'btnSearch111.OnSelect.fx').read_text()
        self.assertTrue(text.startswith('=Set(varSearchKeyword111,Trim(txtKeyword111.Text));'))
        predicate = text[text.index('ClearCollect(colResult111,'):]
        for control in ['txtKeyword111', 'ddOrg111', 'ddStatus111']:
            self.assertNotIn(control, predicate)
        for variable in ['varSearchKeyword111', 'varSearchOrg111', 'varSearchStatus111']:
            self.assertIn(variable, predicate)

    def test_return_refetch_uses_committed_query_and_clamps_page(self):
        text = (SRC / 'scrStaffMasterSearch.OnVisible.tail.fx').read_text()
        self.assertIn("Refresh('M_職員基本_STUDIO')", text)
        self.assertIn('varSearchDepartment111=UiDepartment', text)
        self.assertIn('LookUp(colResult111,StaffId=varStaff111.StaffId)', text)
        self.assertIn('RoundUp(CountRows(colResult111)/20,0)', text)
        self.assertIn('Clear(colStaffSource111);Clear(colResult111);Set(varResultsReady111,true)', text)
        for control in ['txtKeyword111', 'ddOrg111', 'ddStatus111']:
            self.assertNotIn(control, text)

    def test_history_validates_remembered_key_in_current_category(self):
        for filename in ['btnDetailTab111.OnSelect.fx', 'btnLoadDetails111.OnSelect.fx']:
            text = (SRC / filename).read_text()
            self.assertIn('LookUp(colHistory111,Section=varStaffDetailTab111 && RecordId=rememberedId)', text)
            self.assertIn('First(Filter(colHistory111,Section=varStaffDetailTab111)).RecordId', text)
        load = (SRC / 'btnLoadDetails111.OnSelect.fx').read_text()
        self.assertTrue(load.startswith('=If(varHistoryStaff111<>StaffSelected.StaffId || IsBlank(StaffSelected.StaffId),Clear(colHistorySelection111));'))
        self.assertIn('Clear(colHistory111)', load)
        self.assertIn('Set(varFetchError111,"詳細データを取得できませんでした：" & FirstError.Message);Set(varFetched111,Blank())', load)

    def test_no_new_backend_mutation_or_business_formula(self):
        for path in SRC.glob('*.fx'):
            text = path.read_text()
            for unsafe in ['Patch(', 'SubmitForm(', 'UpdateIf(', 'Remove(', '.Run(', 'Launch(']:
                self.assertNotIn(unsafe, text)
        self.assertEqual(self.manifest['data_migrations'], [])
        self.assertFalse(self.manifest['business_rules_changed'])
        self.assertEqual(len(self.manifest['baseline']['source_files']), 10)
        self.assertEqual(self.manifest['baseline']['published_version'], '36')
        self.assertEqual(self.manifest['baseline']['published_package_sha256'], 'f3af186814e138f60fe8e2848ccecdafd7db4af6d1454a852be815ca5e33266c')

if __name__ == '__main__':
    unittest.main()
