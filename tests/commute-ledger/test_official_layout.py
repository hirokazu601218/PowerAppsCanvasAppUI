"""Independent checks of the candidate; not live-browser acceptance."""
import importlib.util, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'src/commute-ledger/v1.02/build.py'
spec=importlib.util.spec_from_file_location('builder',p);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
BASE=ROOT/'other/src/staff-master/candidates/commute-html-v1.01/src/commute-ledger.html'
PDF=ROOT/'tmp/commute-review/official.pdf'
class LayoutTests(unittest.TestCase):
 def test_field_contract(self):
  self.assertCountEqual(re.findall(r'data-field="([^"]+)"',BASE.read_text()),[f['key'] for f in b.fields()])
 def test_fields_inside_page_and_nonoverlapping(self):
  fs=b.fields()
  for i,a in enumerate(fs):
   self.assertGreaterEqual(a['x'],0);self.assertGreaterEqual(a['y'],0)
   self.assertLessEqual(a['x']+a['w'],841.89);self.assertLessEqual(a['y']+a['h'],595.276)
   for c in fs[i+1:]:
    if a['page']==c['page']:
     overlap=min(a['x']+a['w'],c['x']+c['w'])>max(a['x'],c['x']) and min(a['y']+a['h'],c['y']+c['h'])>max(a['y'],c['y'])
     self.assertFalse(overlap,(a['key'],c['key']))
 @unittest.skipUnless(PDF.exists(),'download pinned PDF first')
 def test_preserves_complete_runtime_and_toolbar(self):
  old=BASE.read_text();new=b.build(BASE,PDF)
  self.assertEqual(re.findall(r'<script\b[^>]*>.*?</script>',old,re.S),re.findall(r'<script\b[^>]*>.*?</script>',new,re.S))
  self.assertEqual(old.split('<body>')[1].split('<main')[0],new.split('<body>')[1].split('<main')[0])
  self.assertEqual(new.count('class="page official-page"'),2)
  self.assertEqual(new.count('<svg class="official-form"'),2)
  self.assertNotIn('foreignObject',new)
if __name__=='__main__':unittest.main()
