"""r6a explicit child-inheritance source/model checks; never a Canvas runtime result."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import re
import unittest
import yaml
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'src/screen-ui/v1.31'
RECORD = ROOT / 'records/changes/pay-implement-001/manual-20261010-layout-r6a'
DIRECT = ['conscrPayrollHeader', 'conPayrollTargets', 'conPaySummary', 'conPayBody']
BODY = ['lblPayPrototype', 'conPayActions', 'lblPayState', 'conPayGrossHeading', 'conPayEarnings', 'conPayDeductionHeading', 'conPayDeductions']
def index(root):
    result = {'conscrPayrollRoot': root}
    def visit(owner):
        for child in owner.get('Children', []):
            name, node = next(iter(child.items()))
            if name in result: raise ValueError('duplicate control')
            result[name] = node; visit(node)
    visit(root); return result

def semantic(root):
    return hashlib.sha256(json.dumps(root, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def layout(root_width, root_height, gutter=12):
    """Independent arithmetic model of the proposed sizing contract, not CSS."""
    targets = 108 if root_width < 900 else 60
    fixed = 64 + targets + 104
    pan = root_width < 750 or root_height-fixed < 32+128
    content_width = max(750, root_width)
    deduction_width = content_width-40-(0 if pan else gutter)
    row_width = deduction_width-24
    name_width = row_width*.4 if row_width < 750 else 260
    return {'pan': pan, 'content_width': content_width, 'fixed_height': fixed,
            'normal_body_height': max(0,root_height-fixed),
            'basis_width': row_width-name_width-138-16,
            'actions_inner_width': content_width-40-(0 if pan else gutter)-24,
            'root_viewport_width': root_width-(gutter if pan else 0)}

class LayoutR6(unittest.TestCase):
    def setUp(self):
        self.root=yaml.safe_load((SRC/'payroll-root.paste.yaml').read_text())[0]['conscrPayrollRoot']
        self.nodes=index(self.root)
        self.delta=json.loads((RECORD/'delta.json').read_text())

    def test_exact_thirteen_properties_and_no_controls_or_structure_change(self):
        self.assertEqual(len(self.delta['properties']),13)
        self.assertEqual(len(self.nodes),86)
        reverse=copy.deepcopy(self.root); before=index(reverse)
        for entry in self.delta['properties']:
            props=before[entry['control']]['Properties']; self.assertEqual(props[entry['property']],entry['after'])
            if entry['before_absent']: props.pop(entry['property'])
            else: props[entry['property']]=entry['before']
        self.assertEqual(semantic(reverse),self.delta['r5_source_root_sha256'])
        self.assertEqual(semantic(self.root),self.delta['r6_root_sha256'])

    def test_four_explicit_children_reverse_exactly_to_frozen_r6(self):
        reverse=copy.deepcopy(self.root); nodes=index(reverse)
        for name in DIRECT:
            self.assertEqual(nodes[name]["Properties"].pop("AlignInContainer"),"=AlignInContainer.SetByContainer")
        self.assertEqual(semantic(reverse),self.delta["r6_original_root_sha256"])

    def test_source_clarification_still_requires_freeze(self):
        self.assertEqual(self.delta['status'],'R6A_SOURCE_CLARIFICATION_PENDING_FREEZE')
        manifest=json.loads((SRC/'manifest.json').read_text())
        self.assertEqual(manifest['status'],'R6A_SOURCE_CLARIFICATION_PENDING_FREEZE')
        self.assertIn('R6A_PUBLIC_SOURCE_FREEZE_PENDING',manifest['proposal']['approval_status'])
        self.assertEqual(manifest['proposal']['business_formula_changes'],0)

    def test_current_r5_readback_identity_is_explicit(self):
        self.assertTrue(self.delta['r5_ui_readback_equals_source'])
        self.assertEqual(self.delta['base_source_commit'],'4f7b5c8df63a198e6d4c121d7135f3305f36f8f1')
        self.assertRegex(self.delta['r5_ui_readback_raw_sha256'],r'^[0-9a-f]{64}$')

    def test_external_frame_ratio_and_child_order_unchanged(self):
        self.assertEqual([next(iter(x)) for x in self.root['Children']],DIRECT)
        self.assertEqual({k:self.root['Properties'][k] for k in ['Width','Height','X','Y']},
                         {'Width':'=Parent.Width*UiOuterWidth','Height':'=Parent.Height*UiOuterHeight','X':'=Parent.Width*UiOuterX','Y':'=Parent.Height*UiOuterY'})
        self.assertEqual(self.root['Properties']['LayoutAlignItems'],'=LayoutAlignItems.Start')
        self.assertEqual(self.root['Properties']['LayoutOverflowX'],'=LayoutOverflow.Scroll')
        for name in DIRECT:
            self.assertEqual(self.nodes[name]['Properties']['Width'],'=Max(750,Parent.Width)')
            self.assertEqual(self.nodes[name]['Properties']['FillPortions'],'=0')
            self.assertEqual(self.nodes[name]['Properties']['AlignInContainer'],'=AlignInContainer.SetByContainer')

    def test_minimum_width_is_derived_from_target_controls(self):
        expected=116+150+260+168+3*8+16+16
        self.assertEqual(expected,750)
        self.assertEqual(self.nodes['lblPayrollMonth']['Properties']['Width'],'=116')
        self.assertEqual(self.nodes['ddPayrollMonth']['Properties']['Width'],'=150')
        self.assertEqual(self.nodes['lblPayrollStaff']['Properties']['Width'],'=Max(260,Parent.Width-650)')
        self.assertEqual(self.nodes['btnPayrollSearch']['Properties']['Width'],'=168')
        for prop,value in [('LayoutGap','=8'),('PaddingLeft','=16'),('PaddingRight','=16')]:
            self.assertEqual(self.nodes['conPayrollTargets']['Properties'][prop],value)

    def test_readable_height_constant_is_guarded_existing_row_maximum(self):
        for i in range(8):
            self.assertEqual(self.nodes[f'conPayDeduction{i}']['Properties']['Height'],'=If(Parent.Width<750,128,64)')
            self.assertEqual(self.nodes[f'lblPayDeductionName{i}']['Properties']['Width'],'=If(Parent.Width<750,Parent.Width*0.4,260)')
        self.assertEqual(self.nodes['conPayBody']['Properties']['PaddingTop'],'=12')
        self.assertEqual(self.nodes['conPayBody']['Properties']['PaddingBottom'],'=20')

    def test_mode_uses_only_stable_root_size_and_fixed_source_dimensions(self):
        fx=self.root['Properties']['LayoutOverflowY']
        self.assertEqual(fx,'=If(Self.Width<750 || Self.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height<conPayBody.PaddingTop+conPayBody.PaddingBottom+128,LayoutOverflow.Scroll,LayoutOverflow.Hide)')
        for forbidden in ['conPayBody.Height','conPayDeduction7.Height','ScrollTop','Screen.Size','var']:
            self.assertNotIn(forbidden,fx)

    def test_body_scroll_owner_and_ordinary_branch_are_explicit(self):
        body=self.nodes['conPayBody']['Properties']
        self.assertEqual(body['LayoutOverflowY'],'=If(Parent.LayoutOverflowY=LayoutOverflow.Scroll,LayoutOverflow.Hide,LayoutOverflow.Scroll)')
        self.assertTrue(body['Height'].startswith('=If(Parent.LayoutOverflowY=LayoutOverflow.Scroll,'))
        self.assertTrue(body['Height'].endswith(',Max(0,Parent.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height))'))
        self.assertNotIn('conPayBody.Height',body['Height'])

    def test_intrinsic_height_references_every_visible_immediate_child_once(self):
        body=self.nodes['conPayBody']; text=body['Properties']['Height']
        self.assertEqual([next(iter(x)) for x in body['Children']],BODY)
        self.assertEqual(re.findall(r'\{H:([A-Za-z0-9]+)\.Height,V:\1\.Visible\}',text),BODY)
        self.assertIn('Sum(Filter(rows,V),H)',text)
        self.assertIn('Max(0,CountRows(Filter(rows,V))-1)*Self.LayoutGap',text)
        self.assertIn('Self.PaddingTop+Self.PaddingBottom',text)

    def test_no_explicit_body_height_cycle_or_business_formula_edits(self):
        for name in BODY:
            props=self.nodes[name]['Properties']
            self.assertNotIn('Parent.Height',props.get('Height',''))
            self.assertNotIn('conPayBody.Height',props.get('Height',''))
        allowed={'Width','Height','LayoutAlignItems','LayoutOverflowX','LayoutOverflowY','AlignInContainer'}
        self.assertTrue(all(x['property'] in allowed for x in self.delta['properties']))
        self.assertTrue(all(x['control'] in DIRECT+['conscrPayrollRoot'] for x in self.delta['properties']))

    def test_visible_count_and_gaps_all_eight_state_combinations(self):
        for state,earnings,deductions in itertools.product([False,True],repeat=3):
            visible=[(40,True),(56,True),(40,state),(48,True),(540,earnings),(48,True),(1240,deductions)]
            selected=[h for h,v in visible if v]
            expected=32+sum(selected)+12*max(0,len(selected)-1)
            iterative=32
            for n,h in enumerate(selected): iterative+=h+(12 if n else 0)
            self.assertEqual(iterative,expected)
            self.assertGreaterEqual(expected,32+40+56+48+48+36)

    def test_width_boundary_is_deterministic_with_fractional_values(self):
        for w,want in [(749.999,True),(750,False),(750.001,False)]:
            self.assertEqual(layout(w,700)['pan'],want)

    def test_height_boundary_exactly_keeps_fixed_mode(self):
        for width,threshold in [(750,436),(899.999,436),(900,388),(1195.25,388)]:
            self.assertTrue(layout(width,threshold-.001)['pan'])
            self.assertFalse(layout(width,threshold)['pan'])
            self.assertFalse(layout(width,threshold+.001)['pan'])

    def test_normal_required_viewports_keep_fixed_layout(self):
        for width,height in [(900,600),(1366,768),(1920,1080)]:
            m=layout(width*56/64,height*26/30)
            self.assertFalse(m['pan']);self.assertGreaterEqual(m['normal_body_height'],160)
            self.assertEqual(m['content_width'],width*56/64)

    def test_real_200_observed_geometry_enters_proposed_root_pan(self):
        m=layout(515.375,277.328125)
        self.assertTrue(m['pan']);self.assertEqual(m['content_width'],750)
        self.assertAlmostEqual(m['normal_body_height'],1.328125)

    def test_declared_reflow_widths_have_explicit_modes(self):
        for width,want in [(450,True),(683,True),(960,False)]:
            self.assertEqual(layout(width*56/64,768*26/30)['pan'],want)

    def test_scrollbar_width_does_not_enter_mode_or_require_fixed_padding(self):
        for width,height in itertools.product([749,750,751,787.5,1195.25],[277.328125,388,436,700]):
            for gutter in [0,12,15,17]:
                self.assertEqual(layout(width,height,gutter)['pan'],layout(width,height,0)['pan'])
        fx=self.root['Properties']['LayoutOverflowY']
        self.assertNotIn('17',fx);self.assertNotIn('scrollbar',fx.lower())

    def test_basis_and_action_widths_are_not_squeezed_below_source_contract(self):
        for width,height,gutter in itertools.product([393.75,515.375,597.625,750,751,787.5,840,1195.25],[277.328125,665.6],[0,12,15,17]):
            m=layout(width,height,gutter)
            self.assertGreaterEqual(m['basis_width'],247.39)
            self.assertGreaterEqual(m['actions_inner_width'],190+190+136+16)

    def test_shrink_and_restore_have_zero_normal_root_scroll_range_in_model(self):
        for width,height in [(393.75,665.6),(515.375,277.328125),(1195.25,277.328125)]:
            self.assertTrue(layout(width,height)['pan'])
            restored=layout(1195.25,665.6)
            self.assertFalse(restored['pan'])
            self.assertAlmostEqual(restored['fixed_height']+restored['normal_body_height'],665.6)
            self.assertEqual(restored['content_width'],1195.25)
        # This demonstrates range zero, not that Canvas/DOM has actually clamped an old offset.

    def test_paste_screen_and_standalone_formulas_match(self):
        self.assertEqual(yaml.safe_load((SRC/'payroll-root.pa.yaml').read_text())['Screens']['scrPayroll']['Children'],[{'conscrPayrollRoot':self.root}])
        for entry in self.delta['properties']:
            if entry['after_file']:
                self.assertEqual((SRC/entry['after_file']).read_text().strip(),entry['after'])

if __name__=='__main__': unittest.main()
