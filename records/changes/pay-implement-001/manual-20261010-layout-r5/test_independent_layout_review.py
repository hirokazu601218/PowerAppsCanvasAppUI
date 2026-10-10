"""Independent source/model checks; NOT Power Fx compilation or Player rendering."""
from collections import Counter
from pathlib import Path
import ast
import copy
import hashlib
import json
import os
import re
import unittest
import yaml

def repository_root():
    if os.environ.get('PAY_REVIEW_ROOT'):
        return Path(os.environ['PAY_REVIEW_ROOT']).resolve()
    return next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())

CANDIDATE = repository_root()
if not os.environ.get('PAY_REVIEW_BASELINE_ROOT') or not os.environ.get('PAY_REVIEW_READBACK'):
    raise SystemExit('Set PAY_REVIEW_BASELINE_ROOT to the frozen r4 checkout and PAY_REVIEW_READBACK to its captured payroll UI readback. Missing evidence must not be synthesized from the candidate.')
BASE = Path(os.environ['PAY_REVIEW_BASELINE_ROOT']).resolve()
READBACK = Path(os.environ['PAY_REVIEW_READBACK']).resolve()
OUT = Path(os.environ.get('PAY_REVIEW_OUTPUT', str(Path(__file__).resolve().parent))).resolve()
OUT.mkdir(parents=True, exist_ok=True)

def read_root(base, paste=False):
    p = base / 'src/screen-ui/v1.31' / ('payroll-root.paste.yaml' if paste else 'payroll-root.pa.yaml')
    y = yaml.safe_load(p.read_text())
    return y[0]['conscrPayrollRoot'] if paste else y['Screens']['scrPayroll']['Children'][0]['conscrPayrollRoot']

def controls(root):
    result = {'conscrPayrollRoot': root}
    def visit(node):
        for child in node.get('Children', []):
            for name, definition in child.items():
                assert name not in result, f'duplicate: {name}'
                result[name] = definition
                visit(definition)
    visit(root)
    return result

R4 = read_root(BASE)
R5 = read_root(CANDIDATE)
BEFORE = controls(R4)
AFTER = controls(R5)
DEDUCT = AFTER['conPayDeductions']
NAMES = [next(iter(c)) for c in DEDUCT['Children']]
FORMULA = DEDUCT['Properties']['Height']
PREFIX = '=If(Coalesce(varUiDeductionsOpen,true),'
assert FORMULA.startswith(PREFIX) and FORMULA.endswith(',0)')
EXPR = FORMULA[len(PREFIX):-3]

# Evaluate only the additive/multiplicative numerical formula shape under review.
# Runtime values below come from actual source properties, rather than r5 constants.
def evaluate(expr, values):
    token = re.compile(r'\b(?:Self|[A-Za-z][A-Za-z0-9]*)\.[A-Za-z][A-Za-z0-9]*\b')
    seen = set(token.findall(expr))
    assert seen <= values.keys(), seen - values.keys()
    source = token.sub(lambda m: repr(values[m.group()]), expr)
    def walk(node):
        if isinstance(node, ast.Expression): return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add): return walk(node.left) + walk(node.right)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult): return walk(node.left) * walk(node.right)
        raise AssertionError(f'Unsupported formula term: {ast.dump(node)}')
    return walk(ast.parse(source, mode='eval'))

def child_heights(deduction_width):
    result = {}
    for name in NAMES:
        formula = AFTER[name]['Properties']['Height']
        if re.fullmatch(r'=\d+', formula):
            result[name + '.Height'] = int(formula[1:])
        else:
            assert formula == '=If(Parent.Width<750,128,64)', formula
            result[name + '.Height'] = 128 if deduction_width < 750 else 64
    return result

def values_at(body_width, scrollbar=12, top=0, bottom=0, gap=8):
    deduction_width = body_width - 40 - scrollbar
    values = child_heights(deduction_width)
    values.update({'Self.PaddingTop':top, 'Self.PaddingBottom':bottom, 'Self.LayoutGap':gap})
    return values

def expected(values):
    return sum(values[n + '.Height'] for n in NAMES) + values['Self.PaddingTop'] + values['Self.PaddingBottom'] + (len(NAMES) - 1) * values['Self.LayoutGap']

def aggregate(body_width, scrollbar=12, open_state=True, **kwargs):
    return 0 if open_state is False else evaluate(EXPR, values_at(body_width, scrollbar, **kwargs))

class IndependentLayoutReview(unittest.TestCase):
    def test_exact_whitelist_and_no_structure_change(self):
        self.assertEqual(set(BEFORE), set(AFTER))
        differences = []
        for name in BEFORE:
            a, b = BEFORE[name], AFTER[name]
            self.assertEqual([next(iter(x)) for x in a.get('Children', [])], [next(iter(x)) for x in b.get('Children', [])])
            self.assertEqual({k:v for k,v in a.items() if k not in ['Properties','Children']}, {k:v for k,v in b.items() if k not in ['Properties','Children']})
            ap, bp = a.get('Properties', {}), b.get('Properties', {})
            for prop in ap.keys() | bp.keys():
                if ap.get(prop) != bp.get(prop): differences.append([name,prop])
        self.assertEqual(differences, [['conPayDeductions','Height']])

    def test_frozen_readback_and_paste_equality(self):
        readback = yaml.safe_load(READBACK.read_text())
        self.assertEqual(readback['Screens']['scrPayroll']['Children'], [{'conscrPayrollRoot':R4}])
        self.assertEqual(read_root(CANDIDATE, True), R5)

    def test_every_child_once_no_circular_height_dependency(self):
        refs = re.findall(r'\b([A-Za-z][A-Za-z0-9]*)\.Height\b', EXPR)
        self.assertEqual(Counter(refs), Counter(NAMES))
        self.assertEqual(len(NAMES),11)
        self.assertNotIn('Parent.Width', EXPR)
        for name in NAMES:
            self.assertNotIn('Height', AFTER[name]['Properties']['Height'])
        self.assertEqual(DEDUCT['Properties']['FillPortions'], '=0')

    def test_requested_viewports_and_200_percent_effective_widths(self):
        for viewport in [900,1366,1920]:
            for zoom in [1,2]:
                for scrollbar in [0,12,17]:
                    body = viewport / zoom * 56 / 64
                    with self.subTest(viewport=viewport,zoom=zoom,scrollbar=scrollbar):
                        self.assertEqual(aggregate(body,scrollbar),expected(values_at(body,scrollbar)))
                        self.assertEqual(aggregate(body,scrollbar,False),0)
                        self.assertEqual(aggregate(body,scrollbar,None),aggregate(body,scrollbar,True))
        self.assertEqual([aggregate(v*.875) for v in [900,1366,1920]],[1240,728,728])
        self.assertEqual([aggregate(v/2*.875) for v in [900,1366,1920]],[1240,1240,728])

    def test_boundary_matrix_including_nested_offsets(self):
        for scrollbar in [0,12,17]:
            # body threshold750; row-height threshold750+body padding+scrollbar;
            # leaf width threshold750+body padding+scrollbar+deduction padding.
            for threshold in [750,750+40+scrollbar,750+40+scrollbar+24]:
                for epsilon in [-.001,0,.001]:
                    body = threshold + epsilon
                    with self.subTest(scrollbar=scrollbar,body=body):
                        self.assertEqual(aggregate(body,scrollbar),expected(values_at(body,scrollbar)))
            self.assertEqual(aggregate(750+40+scrollbar-.001,scrollbar),1240)
            self.assertEqual(aggregate(750+40+scrollbar,scrollbar),728)

    def test_reproduces_both_old_defects(self):
        for body, clipping in [(1195.25,30),(787.5,542),(740,30)]:
            old_height = 1210 if body < 750 else 698
            self.assertEqual(expected(values_at(body))-old_height,clipping)
            self.assertEqual(aggregate(body)-expected(values_at(body)),0)

    def test_gap_padding_and_child_height_sensitivity(self):
        for gap in [0,1,8,12]:
            for top,bottom in [(0,0),(3,7),(17,23)]:
                for width in [700,800,1200]:
                    v = values_at(width,top=top,bottom=bottom,gap=gap)
                    self.assertEqual(evaluate(EXPR,v),expected(v))
                    for name in NAMES:
                        modified = dict(v)
                        modified[name+'.Height'] += 13
                        self.assertEqual(evaluate(EXPR,modified),expected(v)+13)

    def test_fixed_summary_and_existing_body_scrolling_preserved(self):
        self.assertEqual([next(iter(c)) for c in R5['Children']], ['conscrPayrollHeader','conPayrollTargets','conPaySummary','conPayBody'])
        self.assertEqual(AFTER['conPaySummary'], BEFORE['conPaySummary'])
        self.assertEqual(AFTER['conPayBody']['Properties'], BEFORE['conPayBody']['Properties'])
        self.assertEqual(AFTER['conPayBody']['Properties']['LayoutOverflowY'],'=LayoutOverflow.Scroll')
        self.assertEqual(AFTER['conPayEarnings'], BEFORE['conPayEarnings'])
        self.assertNotIn('LayoutOverflowY', DEDUCT['Properties'])

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentLayoutReview))
    matrix=[]
    for viewport in [900,1366,1920]:
        for zoom in [1,2]:
            effective=viewport/zoom
            body=effective*.875
            actual=aggregate(body)
            old=1210 if body<750 else 698
            matrix.append({'nominal_viewport_width':viewport,'zoom_model':zoom,'effective_width':effective,'body_width':body,'deduction_width':body-52,'row_width':body-76,'model_assumption_scrollbar_px':12,'old_height':old,'new_height':actual,'old_clipped_height':actual-old,'runtime_status':'NOT_RUN'})
    summary={'kind':'independent_static_source_and_geometry_model_review','official_power_fx_compiler':False,'player_render_test':False,'tests_run':result.testsRun,'passed':result.wasSuccessful(),'formula':FORMULA,'source_sha256':hashlib.sha256((CANDIDATE/'src/screen-ui/v1.31/payroll-root.pa.yaml').read_bytes()).hexdigest(),'matrix':matrix}
    (OUT/'independent-review-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
