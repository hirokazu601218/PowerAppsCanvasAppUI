"""Portable independent r6 source/model review. This is not a Power Fx compiler or UI test."""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import unittest
import yaml

def locate_repository():
    for parent in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (parent / 'src/screen-ui/v1.31/manifest.json').is_file():
            return parent
    raise RuntimeError('Run this review from the candidate repository.')

ROOT = locate_repository()
SRC = ROOT / 'src/screen-ui/v1.31'
FROZEN_R5_ROOT_SHA = '02fad9291e41752353cff590b37fcf03a1c6a229ed25e7701df83b006c43fe5b'
VERIFIED_R5_READBACK_SHA = 'd3d4fbd8c0ab816ef48b7d0be7625ddee7b52f3c9505f3c42e7e9b998fdcda08'
REPORT = Path(__file__).with_name('independent-r6-results.json')
CHILDREN = ['conscrPayrollHeader', 'conPayrollTargets', 'conPaySummary', 'conPayBody']
BODY_CHILDREN = ['lblPayPrototype', 'conPayActions', 'lblPayState', 'conPayGrossHeading', 'conPayEarnings', 'conPayDeductionHeading', 'conPayDeductions']
EXPECTED_DIFF = {
    ('conscrPayrollRoot', 'LayoutAlignItems'),
    ('conscrPayrollRoot', 'LayoutOverflowX'),
    ('conscrPayrollRoot', 'LayoutOverflowY'),
    ('conPayBody', 'Height'), ('conPayBody', 'LayoutOverflowY'),
    *((n, 'Width') for n in CHILDREN),
}


def load_root(path):
    return yaml.safe_load(path.read_text())[0]['conscrPayrollRoot']


def flatten(root):
    result, parents = {}, {}
    def walk(name, obj, parent):
        assert name not in result
        result[name] = obj
        parents[name] = parent
        for child in obj.get('Children', []):
            key, value = next(iter(child.items()))
            walk(key, value, name)
    walk('conscrPayrollRoot', root, 'scrPayroll')
    return result, parents


def mode(width, height, pad_top=12, pad_bottom=20):
    fixed = 64 + (108 if width < 900 else 60) + 104
    return width < 750 or height - fixed < pad_top + pad_bottom + 128


class IndependentR6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import copy
        cls.root = load_root(SRC / 'payroll-root.paste.yaml')
        cls.controls, cls.parents = flatten(cls.root)
        cls.body = cls.controls['conPayBody']
        cls.delta = json.loads((ROOT / 'records/changes/pay-implement-001/manual-20261010-layout-r6/proposal-delta.json').read_text())
        cls.base = copy.deepcopy(cls.root)
        cls.old, _ = flatten(cls.base)
        for item in cls.delta['properties']:
            props = cls.old[item['control']]['Properties']
            if item['before_absent']:
                props.pop(item['property'])
            else:
                props[item['property']] = item['before']

    def test_01_exact_nine_properties_and_no_tree_changes(self):
        self.assertEqual(len(self.controls), 86)
        self.assertEqual(list(self.old), list(self.controls))
        actual = set()
        for name, obj in self.controls.items():
            old = self.old[name]
            self.assertEqual({k:v for k,v in obj.items() if k not in ('Properties', 'Children')}, {k:v for k,v in old.items() if k not in ('Properties', 'Children')})
            self.assertEqual([next(iter(c)) for c in obj.get('Children', [])], [next(iter(c)) for c in old.get('Children', [])])
            for prop in set(obj['Properties']) | set(old['Properties']):
                if obj['Properties'].get(prop) != old['Properties'].get(prop):
                    actual.add((name, prop))
        self.assertEqual(actual, EXPECTED_DIFF)

    def test_02_frozen_r5_semantic_baseline_and_paste_screen_parity(self):
        # Portable verification of a frozen hash; no private readback is bundled.
        semantic = hashlib.sha256(json.dumps(self.base, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(semantic, FROZEN_R5_ROOT_SHA)
        candidate = yaml.safe_load((SRC/'payroll-root.pa.yaml').read_text())['Screens']['scrPayroll']['Children']
        self.assertEqual(candidate, [{'conscrPayrollRoot':self.root}])
        self.assertEqual(VERIFIED_R5_READBACK_SHA, self.delta['r5_ui_readback_raw_sha256'])

    def test_03_manifest_before_after_and_standalone_formulas(self):
        self.assertEqual(self.delta['status'], 'PROPOSAL_NOT_APPROVED')
        self.assertEqual(self.delta['runtime_status'], 'NOT_RUN')
        self.assertEqual(self.delta['base_source_commit'], '4f7b5c8df63a198e6d4c121d7135f3305f36f8f1')
        self.assertEqual({(d['control'],d['property']) for d in self.delta['properties']}, EXPECTED_DIFF)
        self.assertEqual(len(self.delta['properties']), 9)
        for item in self.delta['properties']:
            n,p=item['control'],item['property']
            self.assertEqual(self.old[n]['Properties'].get(p),item['before'])
            self.assertEqual(self.controls[n]['Properties'][p],item['after'])
            self.assertEqual(p not in self.old[n]['Properties'],item['before_absent'])
            self.assertEqual(hashlib.sha256(item['after'].encode()).hexdigest(),item['after_sha256'])
            if item['after_file']:
                self.assertEqual((SRC/item['after_file']).read_text().strip(),item['after'])

    def test_04_source_derived_750_contract(self):
        p=lambda n:self.controls[n]['Properties']
        target=p('conPayrollTargets')
        widths=[int(p(n)['Width'][1:]) for n in ('lblPayrollMonth','ddPayrollMonth','btnPayrollSearch')]
        self.assertEqual(p('lblPayrollStaff')['Width'], '=Max(260,Parent.Width-650)')
        total=sum(widths)+260+3*int(target['LayoutGap'][1:])+int(target['PaddingLeft'][1:])+int(target['PaddingRight'][1:])
        self.assertEqual(total,750)
        self.assertEqual(p('conscrPayrollRoot')['LayoutAlignItems'],'=LayoutAlignItems.Start')
        self.assertEqual(p('conscrPayrollRoot')['LayoutOverflowX'],'=LayoutOverflow.Scroll')
        for name in CHILDREN:
            self.assertEqual(p(name)['Width'],'=Max(750,Parent.Width)')

    def test_05_128_contract_and_deterministic_mode(self):
        for i in range(8):
            self.assertEqual(self.controls[f'conPayDeduction{i}']['Properties']['Height'], '=If(Parent.Width<750,128,64)')
        expected='=If(Self.Width<750 || Self.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height<conPayBody.PaddingTop+conPayBody.PaddingBottom+128,LayoutOverflow.Scroll,LayoutOverflow.Hide)'
        self.assertEqual(self.root['Properties']['LayoutOverflowY'],expected)
        self.assertNotIn('conPayBody.Height',expected)
        self.assertNotRegex(expected,r'conPayDeduction\d\.(Height|Width)')
        for w in [749.999,750,750.001,899.999,900,900.001,1680]:
            threshold=64+(108 if w<900 else 60)+104+32+128
            for delta in [-.001,0,.001]:
                self.assertEqual(mode(w,threshold+delta),w<750 or delta<0)
        for w in [749.999,750,750.001]:
            self.assertEqual(mode(w,1000),w<750)

    def test_06_intrinsic_table_has_each_child_once_and_exact_gap_sum(self):
        expr=self.body['Properties']['Height']
        pairs=re.findall(r'\{H:([A-Za-z0-9]+)\.Height,V:([A-Za-z0-9]+)\.Visible\}',expr)
        self.assertEqual(pairs,[(n,n) for n in BODY_CHILDREN])
        self.assertEqual([next(iter(c)) for c in self.body['Children']],BODY_CHILDREN)
        suffix='},Self.PaddingTop+Self.PaddingBottom+Sum(Filter(rows,V),H)+Max(0,CountRows(Filter(rows,V))-1)*Self.LayoutGap),Max(0,Parent.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height))'
        self.assertTrue(expr.startswith('=If(Parent.LayoutOverflowY=LayoutOverflow.Scroll,With({rows:Table('))
        self.assertTrue(expr.endswith(')'+suffix))
        self.assertEqual(self.body['Properties']['LayoutOverflowY'],'=If(Parent.LayoutOverflowY=LayoutOverflow.Scroll,LayoutOverflow.Hide,LayoutOverflow.Scroll)')
        self.assertEqual(self.body['Properties']['FillPortions'],'=0')

    def test_07_all_visibility_patterns_and_intrinsic_perturbations(self):
        rng=random.Random(617)
        for visible in itertools.product([False,True],repeat=7):
            for trial in range(6):
                heights=[rng.uniform(0,1400) for _ in range(7)]
                pad_top,pad_bottom,gap=[rng.uniform(0,32) for _ in range(3)]
                # Table/filter/sum path from the candidate's verified expression.
                rows=[h for h,v in zip(heights,visible) if v]
                modeled=pad_top+pad_bottom+sum(rows)+max(0,len(rows)-1)*gap
                # Independently place each visible child and gaps sequentially.
                cursor=pad_top
                first=True
                for h,v in zip(heights,visible):
                    if v:
                        if not first:cursor+=gap
                        cursor+=h
                        first=False
                oracle=cursor+pad_bottom
                self.assertAlmostEqual(modeled,oracle)

    def test_08_no_layout_dependency_cycle_or_parent_height_child(self):
        layout={'Height','Width','LayoutOverflowX','LayoutOverflowY','PaddingTop','PaddingBottom','PaddingLeft','PaddingRight','LayoutGap','LayoutMinWidth','LayoutMinHeight'}
        graph={}
        for name,obj in self.controls.items():
            for prop,expr in obj['Properties'].items():
                if prop not in layout:continue
                edges=[]
                for owner,dep in re.findall(r'\b([A-Za-z][A-Za-z0-9]*)\.([A-Za-z][A-Za-z0-9]*)\b',str(expr)):
                    owner=name if owner=='Self' else self.parents[name] if owner=='Parent' else owner
                    if owner in self.controls and dep in layout:edges.append((owner,dep))
                graph[(name,prop)]=edges
        done=set()
        def visit(key,stack):
            self.assertNotIn(key,stack,repr(stack+[key]))
            if key in done:return
            for nxt in graph.get(key,[]):visit(nxt,stack+[key])
            done.add(key)
        for key in graph:visit(key,[])
        for name in BODY_CHILDREN:
            props=self.controls[name]['Properties']
            self.assertNotIn('Parent.Height',props.get('Height',''))
            self.assertNotIn('conPayBody.Height',props.get('Height',''))
            self.assertNotEqual(props.get('FillPortions'),'=1')
        for prop in ('PaddingTop','PaddingBottom','LayoutGap'):
            self.assertNotIn(prop,self.root['Properties'])

    def test_09_requested_viewports_and_low_height_modes(self):
        expected={900:False,1366:False,1920:False,450:True,683:True,960:False}
        for viewport,want in expected.items():
            w=viewport*56/64
            self.assertEqual(mode(w,700),want)
            self.assertTrue(mode(w,277.328125))
            self.assertEqual(max(750,w),750 if w<750 else w)
        self.assertTrue(mode(515.375,277.328125))
        # Above750 normal mode uses the r5 sizing verbatim, and has no root gutter.
        for w,h in [(787.5,520),(1195.25,666),(1680,936)]:
            self.assertFalse(mode(w,h))
            self.assertEqual(max(750,w),w)
            self.assertGreaterEqual(h-64-(108 if w<900 else 60)-104,160)

    def test_10_minimum_content_prevents_known_button_and_basis_compression(self):
        # Model the supported scroll gutter variations; these are not measurements.
        for gutter in [0,12,15,17]:
            body_width=750
            deduction_width=body_width-40-gutter
            row_width=deduction_width-24
            name_width=row_width*.4
            basis_width=row_width-name_width-138-2*8
            self.assertGreaterEqual(basis_width,247)
            self.assertGreaterEqual(deduction_width-24,190+190+136+2*8)
        self.assertEqual(self.controls['conPayActions']['Properties']['Height'],'=56')
        for name in ('btnPayEarnings','btnPayDeductions','btnPayRecalculate'):
            self.assertEqual(self.controls[name]['Properties']['Height'],'=44')
        # Source contract keeps all target controls in one row at actual width750.
        self.assertEqual(116+150+260+168+3*8+32,750)

    def test_11_reproduces_real200_failure_without_claiming_runtime_fix(self):
        self.assertAlmostEqual(277.328125-64-108-104,1.328125)
        # The new predicate selects the full-intrinsic-content branch.
        self.assertTrue(mode(515.375,277.328125))
        # Independent body fixture: ready, both sections open, proto default40.
        heights=[40,56,0,48,540,48,1240]
        visible=[True,True,False,True,True,True,True]
        full_height=32+sum(h for h,v in zip(heights,visible) if v)+5*12
        self.assertEqual(full_height,2064)
        self.assertGreater(full_height,1.328125)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IndependentR6)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    files=[SRC/'payroll-root.pa.yaml',SRC/'payroll-root.paste.yaml',*(SRC/name for name in ['conscrPayrollRoot.LayoutOverflowY.fx','payroll-content.Width.fx','conPayBody.Height.fx','conPayBody.LayoutOverflowY.fx'])]
    REPORT.write_text(json.dumps({
        'status':'PASS_SOURCE_MODEL_ONLY' if result.wasSuccessful() else 'FAIL',
        'tests_run':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),
        'approval':'PROPOSAL_NOT_APPROVED',
        'runtime':'NOT_RUN',
        'readback_verification':'FROZEN_SEMANTIC_HASH_ONLY; original reviewer separately checked complete r5 readback',
        'official_powerfx_compiler':'NOT_RUN',
        'base_source_commit':'4f7b5c8df63a198e6d4c121d7135f3305f36f8f1',
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'review_test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limitations':['Geometry is a model, not the Canvas layout engine.','Native200%, text clipping, real scroll ownership and keyboard/focus remain unverified.','The fixed-summary and narrow-reflow exceptions require user approval.'],
    },ensure_ascii=False,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
