"""r5 intrinsic-height and graph checks. Not a Canvas layout engine or zoom test."""
import copy,json,re,unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'src/screen-ui/v1.31'
EXPECTED_CHILDREN=['lblPaySocialHeading']+[f'conPayDeduction{i}' for i in range(5)]+['conPaySocialTotal','lblPayTaxHeading']+[f'conPayDeduction{i}' for i in range(5,8)]
OLD='=If(Coalesce(varUiDeductionsOpen,true),If(Parent.Width<750,1210,698),0)'
def find(root,name):
 for child in root.get('Children',[]):
  if name in child:return child[name]
  for value in child.values():
   result=find(value,name)
   if result is not None:return result
 return None
class LayoutR5(unittest.TestCase):
 def setUp(self):
  self.root=yaml.safe_load((SRC/'payroll-root.paste.yaml').read_text())[0]['conscrPayrollRoot'];self.box=find(self.root,'conPayDeductions');self.formula=self.box['Properties']['Height']
 def height(self,deduction_width,opened=True,gap=8,top=0,bottom=0,extra=None):
  """Evaluate the deliberately small Height formula using fixture runtime properties."""
  if not opened:return 0
  expression=self.formula.split(',true),',1)[1][:-3]
  values={'Self.PaddingTop':top,'Self.PaddingBottom':bottom,'Self.LayoutGap':gap}
  values.update({name+'.Height':(128 if deduction_width<750 else 64) if name.startswith('conPayDeduction') else 48 if name=='conPaySocialTotal' else 44 for name in EXPECTED_CHILDREN})
  values.update(extra or {})
  expression=re.sub(r'[A-Za-z][A-Za-z0-9]*\.(?:Height|PaddingTop|PaddingBottom|LayoutGap)',lambda m:str(values[m.group()]),expression)
  self.assertRegex(expression,r'^[0-9+*. ]+$');return eval(expression,{'__builtins__':{}},{})
 def test_height_is_sum_of_each_actual_child_and_ten_gaps(self):
  self.assertEqual([next(iter(c)) for c in self.box['Children']],EXPECTED_CHILDREN)
  self.assertEqual(re.findall(r'([A-Za-z0-9]+)\.Height',self.formula),EXPECTED_CHILDREN)
  self.assertIn('+10*Self.LayoutGap',self.formula);self.assertIn('Self.PaddingTop+Self.PaddingBottom',self.formula)
  for hardcoded in ['Parent.Width','1210','698','1240','728']:self.assertNotIn(hardcoded,self.formula)
 def test_observed_wide_and_narrow_intrinsic_heights(self):
  self.assertEqual(self.height(1143.25),728);self.assertEqual(self.height(735.5),1240)
 def test_reproduces_both_old_failure_modes(self):
  self.assertEqual(self.height(1143.25)-698,30)
  self.assertEqual(self.height(735.5)-698,542)
  self.assertEqual(self.height(700)-1210,30)
 def test_nested_width_threshold_boundaries(self):
  for parent_width in [749.999,750,750.001,801.999,802,802.001]:
   child_width=parent_width-40-12
   expected=1240 if child_width<750 else 728
   self.assertEqual(self.height(child_width),expected)
 def test_child_width_750_boundary(self):
  self.assertEqual(self.height(749.999),1240);self.assertEqual(self.height(750),728);self.assertEqual(self.height(750.001),728)
 def test_viewports_and_effective_double_zoom_widths(self):
  for viewport,expected in [(900,1240),(1366,728),(1920,728),(450,1240),(683,1240),(960,728)]:
   with self.subTest(viewport=viewport):self.assertEqual(self.height(viewport*56/64-40-12),expected)
 def test_scrollbar_width_is_not_baked_into_height(self):
  for scrollbar in [0,12,15,17]:
   for body_width in [740,750,780,790,800,802,820,1100]:
    width=body_width-40-scrollbar
    self.assertEqual(self.height(width),8*(128 if width<750 else 64)+44+48+44+10*8)
 def test_gap_padding_changes_do_not_reintroduce_clipping(self):
  for gap in [0,4,8,12,20]:
   for top,bottom in [(0,0),(12,20),(4,4)]:self.assertEqual(self.height(800,gap=gap,top=top,bottom=bottom),648+10*gap+top+bottom)
 def test_actual_child_height_change_flows_through(self):self.assertEqual(self.height(800,extra={'conPayDeduction7.Height':96}),760)
 def test_collapsed_remains_zero(self):self.assertEqual(self.height(700,opened=False,top=20,bottom=20),0);self.assertEqual(self.box['Properties']['Visible'],'=Coalesce(varUiDeductionsOpen,true)')
 def test_no_height_dependency_cycle(self):
  for child in self.box['Children']:
   name,obj=next(iter(child.items()));height=obj['Properties']['Height']
   self.assertNotIn('Parent.Height',height,name);self.assertNotIn('conPayDeductions.Height',height,name);self.assertNotIn('FillPortions: =1',str(obj))
 def test_r5_deduction_and_summary_structure_survive_r6_proposal(self):
  names=[next(iter(c)) for c in self.root['Children']];self.assertLess(names.index('conPaySummary'),names.index('conPayBody'))
  body=find(self.root,'conPayBody');self.assertIsNone(find(body,'conPaySummary'))
  self.assertTrue(body['Properties']['Height'].endswith(',Max(0,Parent.Height-conscrPayrollHeader.Height-conPayrollTargets.Height-conPaySummary.Height))'))
  self.assertEqual(body['Properties']['LayoutOverflowY'],'=If(Parent.LayoutOverflowY=LayoutOverflow.Scroll,LayoutOverflow.Hide,LayoutOverflow.Scroll)');self.assertNotIn('LayoutOverflowY',self.box['Properties'])
 def test_manifest_and_standalone_formula_match(self):
  m=json.loads((SRC/'manifest.json').read_text());entries=[x for x in m['changes'] if x['control']=='conPayDeductions'];self.assertEqual(len(entries),1)
  self.assertEqual(entries[0]['before'],OLD);self.assertEqual((SRC/entries[0]['after_file']).read_text().strip(),self.formula)
 def test_paste_and_screen_are_semantically_identical(self):self.assertEqual(yaml.safe_load((SRC/'payroll-root.pa.yaml').read_text())['Screens']['scrPayroll']['Children'],[{'conscrPayrollRoot':self.root}])
 def test_new_e2e_never_programmatically_scrolls_hidden_ancestors(self):
  text=(ROOT/'e2e/current-app/state-retention.test.ts').read_text();start=text.index('async function scrollPayrollBodyToEnd');end=text.index("test('UT-STATE-SEARCH-001",start)
  helper=text[start:end];self.assertIn("['auto', 'scroll'].includes",helper);self.assertIn("closest('[data-control-name]') === body",helper)
  self.assertNotIn('.scrollIntoView',text);self.assertIn('clippingViolations',helper);self.assertIn('lblPayDeductionBasis7',helper);self.assertIn('lblPayDeductionAmount7',helper)
if __name__=='__main__':unittest.main()
