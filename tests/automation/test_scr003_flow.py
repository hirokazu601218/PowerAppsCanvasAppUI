"""Source validation only; no claim of Power Automate execution."""
import copy, importlib.util, json, unittest
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('flowbuilder',ROOT/'scripts/automation/build_scr003_flow.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def actions(d):
    for n,a in d.items():
        yield n,a
        yield from actions(a.get('actions',{}))
        yield from actions(a.get('else',{}).get('actions',{}))

class FlowSourceTest(unittest.TestCase):
    def setUp(self):
        self.flow=mod.build();self.all=dict(actions(self.flow['actions']))
        self.schema=self.all['Check_shape']['inputs']['schema']
        self.row={'勤務月':'2026-08','所属部局名':'秘書課','所属課室名':'総務課','所属長氏名':'架空 長','勤務時間管理員氏名':'架空 員','No':1,'職員番号':'000000000001','氏名':'架空 太郎','備考':''}
        for k,v in self.schema['items']['properties'].items():
            if k not in self.row:self.row[k]=0
    def test_valid_zero_decimal_null(self):
        self.row['超過勤務時間125']=33.167
        self.row['通勤手当日数']=None
        jsonschema.validate([self.row],self.schema)
    def test_reject_invalid_range_type_month_and_identifier(self):
        for field,value in [('欠勤時間',.5),('欠勤時間',-1),('職員番号','0000000000001'),('職員番号','+00000000001'),('通勤手当日数',32),('No',0),('勤務月','2026-13'),('氏名','')]:
            with self.subTest(field=field,value=value):
                row={**self.row,field:value}
                with self.assertRaises(jsonschema.ValidationError):jsonschema.validate([row],self.schema)
    def test_no_destructive_line_deletion(self):
        # Failure can leave orphan staging rows, never delete the old active batch.
        for _,action in self.all.items():
            self.assertNotEqual(action.get('inputs',{}).get('host',{}).get('operationId'),'DeleteRecord')
    def test_single_serialization_boundary(self):
        self.assertEqual(self.flow['triggers']['manual']['runtimeConfiguration']['concurrency']['runs'],1)
        self.assertEqual(self.all['Activate_batch']['runAfter'],{'Commit_guard':['Succeeded']})
        self.assertEqual(self.all['Read_staged']['runAfter'],{'Stage_rows':['Succeeded']})
        self.assertEqual(self.all['Commit_guard']['runAfter'],{'Before_commit':['Succeeded']})
    def test_concurrency_uses_async_response(self):
        self.assertEqual(self.all['Respond']['operationOptions'],'Asynchronous')
    def test_response_even_when_cleanup_fails(self):
        self.assertIn('Failed',self.all['Respond']['runAfter']['Cleanup'])
        self.assertEqual(self.all['Failure']['runAfter'],{'Execute':['Failed','TimedOut']})
    def test_oversized_excel_not_silently_truncated(self):
        self.assertEqual(self.all['Excel_rows']['runtimeConfiguration']['paginationPolicy']['minimumItemCount'],1000)
        self.assertEqual(self.schema['maxItems'],999)
    def test_every_run_after_is_sibling(self):
        def check(group):
            for _,a in group.items():
                self.assertTrue(set(a.get('runAfter',{}))<=set(group))
                check(a.get('actions',{}));check(a.get('else',{}).get('actions',{}))
        check(self.flow['actions'])
    def test_saved_definition_matches_generator(self):
        saved=json.loads((ROOT/'powerapps/flows/scr003/definition.json').read_text())
        self.assertEqual(saved,self.flow)

if __name__=='__main__':unittest.main()
