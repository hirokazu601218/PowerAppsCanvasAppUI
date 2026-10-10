"""Portable fail-closed helper review. No authentication or external writes."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

sys.dont_write_bytecode = True
ROOT = next((p for p in [Path.cwd(), *Path(__file__).resolve().parents]
             if (p/'src/screen-ui/v1.31/manifest.json').is_file()), None)
if ROOT is None:
    raise RuntimeError('Run from the candidate repository.')
HERE = Path(__file__).resolve().parent
SRC = ROOT/'src/screen-ui/v1.31'
HELPER_PATH = ROOT/'scripts/implementation/apply_pay_implement_001.py'
spec = importlib.util.spec_from_file_location('reviewed_patch_helper', HELPER_PATH)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
INSERTION = '''        if entry.get('before_absent'):
            if entry['property'] in owner.get('Properties', {}):
                raise ValueError(f"Expected absent baseline property: {entry['control']}.{entry['property']}")
            continue
'''
BASE_HELPER_SHA = '852a0763ca6d38e5f4cb9842c1c1151feb416dc88e2bb61270e8c0172ca7a2f1'


class HelperReview(unittest.TestCase):
    def setUp(self):
        self.manifest=json.loads((SRC/'manifest.json').read_text())
        self.root=yaml.safe_load((SRC/'payroll-root.paste.yaml').read_text())[0]['conscrPayrollRoot']

    def baseline(self):
        payroll={'Properties':{},'Children':[{'conscrPayrollRoot':copy.deepcopy(self.root)}]}
        staff={'Properties':{},'Children':[]}
        root=helper.control(payroll,'conscrPayrollRoot')
        summary=next(x for x in root['Children'] if 'conPaySummary' in x)
        root['Children'].remove(summary)
        helper.control(root,'conPayBody')['Children'].insert(1,summary)
        screens={'scrPayroll':payroll,'scrStaffMasterSearch':staff}
        for change in self.manifest['changes']:
            if 'property' not in change:continue
            screen=screens[change['screen']]
            owner=screen if change['control']==change['screen'] else helper.control(screen,change['control'])
            if owner is None:
                owner={'Properties':{}}
                screen['Children'].append({change['control']:owner})
            props=owner['Properties']
            if change.get('before_absent'):
                props.pop(change['property'],None)
            elif change.get('mode')=='preserve_first_statement_replace_tail':
                props[change['property']]='=Set(varCommuteReportBase111,"https://example.invalid/approved-existing");'+change['before_tail']
            else:
                props[change['property']]=change['before']
        return screens

    def test_01_helper_only_adds_four_guard_lines(self):
        source=HELPER_PATH.read_text()
        self.assertEqual(source.count(INSERTION),1)
        reversed_source=source.replace(INSERTION,'',1)
        self.assertEqual(hashlib.sha256(reversed_source.encode()).hexdigest(),BASE_HELPER_SHA)

    def test_02_only_expected_two_absent_properties_declared(self):
        absent=[x for x in self.manifest['changes'] if x.get('before_absent')]
        self.assertEqual({(x['screen'],x['control'],x['property']) for x in absent},
                         {('scrPayroll','conscrPayrollRoot','LayoutOverflowX'),('scrPayroll','conscrPayrollRoot','LayoutOverflowY')})
        self.assertTrue(all(x['before_absent'] is True and x.get('before') is None for x in absent))

    def test_03_absent_guard_rejects_all_explicit_values_in_both_axes(self):
        for prop in ['LayoutOverflowX','LayoutOverflowY']:
            for value in [None,'',False,0,'=LayoutOverflow.Hide','=LayoutOverflow.Scroll']:
                with self.subTest(prop=prop,value=value):
                    before=self.baseline()
                    helper.control(before['scrPayroll'],'conscrPayrollRoot')['Properties'][prop]=value
                    original=copy.deepcopy(before)
                    with self.assertRaisesRegex(ValueError,f'Expected absent baseline property: conscrPayrollRoot.{prop}'):
                        helper.apply(before,self.manifest)
                    self.assertEqual(before,original)

    def test_04_absent_success_adds_exact_properties_and_preserves_input(self):
        before=self.baseline()
        original=copy.deepcopy(before)
        after=helper.apply(before,self.manifest)
        self.assertEqual(before,original)
        after_root=helper.control(after['scrPayroll'],'conscrPayrollRoot')
        self.assertEqual(after_root,self.root)
        self.assertNotIn('LayoutOverflowX',helper.control(before['scrPayroll'],'conscrPayrollRoot')['Properties'])
        self.assertNotIn('LayoutOverflowY',helper.control(before['scrPayroll'],'conscrPayrollRoot')['Properties'])

    def test_05_whole_root_guard_rejects_unrelated_drift(self):
        before=self.baseline()
        helper.control(before['scrPayroll'],'lblPayrollStaff')['Properties']['Text']='="unexpected"'
        original=copy.deepcopy(before)
        with self.assertRaisesRegex(ValueError,'Payroll root differs from reviewed baseline'):
            helper.apply(before,self.manifest)
        self.assertEqual(before,original)

    def test_06_existing_formula_and_duplicate_guards_remain(self):
        before=self.baseline()
        helper.control(before['scrStaffMasterSearch'],'btnSearch111')['Properties']['OnSelect']+=';Notify("unexpected")'
        with self.assertRaisesRegex(ValueError,'Baseline mismatch'):
            helper.apply(before,self.manifest)
        before=self.baseline()
        before['scrStaffMasterSearch']['Children'].append(copy.deepcopy(before['scrStaffMasterSearch']['Children'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate control name'):
            helper.apply(before,self.manifest)

    def test_07_full_ten_file_set_and_content_guards_remain(self):
        self.assertEqual(len(self.manifest['baseline']['source_files']),10)
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            directory=Path(temporary)
            manifest=copy.deepcopy(self.manifest)
            for filename in manifest['baseline']['source_files']:
                data=('App: {}' if filename=='App.pa.yaml' else '_EditorState: {}' if filename=='_EditorState.pa.yaml' else 'Screens: {}')+'\n'
                (directory/filename).write_text(data)
                manifest['baseline']['source_files'][filename]=hashlib.sha256(data.encode()).hexdigest()
            helper.load_readback(directory,manifest)
            extra=directory/'unreviewed.pa.yaml'
            extra.write_text('Screens: {}\n')
            with self.assertRaisesRegex(ValueError,'Unexpected readback source set'):
                helper.load_readback(directory,manifest)
            extra.unlink()
            app=directory/'App.pa.yaml'
            original=app.read_bytes()
            app.write_text('App: {unexpected: true}\n')
            with self.assertRaisesRegex(ValueError,'Full readback baseline mismatch: App.pa.yaml'):
                helper.load_readback(directory,manifest)
            app.write_bytes(original)
            app.unlink()
            with self.assertRaisesRegex(ValueError,'Unexpected readback source set'):
                helper.load_readback(directory,manifest)

    def test_08_existing_destination_and_after_scope_guards_remain(self):
        before=self.baseline()
        after=helper.apply(before,self.manifest)
        self.assertTrue(after['scrStaffMasterSearch']['Properties']['OnVisible'].startswith('=Set(varCommuteReportBase111,"https://example.invalid/approved-existing");'))
        helper.control(after['scrPayroll'],'lblPayrollStaff')['Properties']['Text']='="unexpected"'
        with self.assertRaisesRegex(ValueError,'Unexpected property change: lblPayrollStaff.Text'):
            helper.change_evidence(before,after,self.manifest)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HelperReview))
    (HERE/'independent-helper-results.json').write_text(json.dumps({
        'status':'PASS_LOCAL_GUARD_TESTS_ONLY' if result.wasSuccessful() else 'FAIL',
        'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'runtime':'NOT_RUN','approval':'PROPOSAL_NOT_APPROVED',
        'helper_sha256':hashlib.sha256(HELPER_PATH.read_bytes()).hexdigest(),
        'review_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    },indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
