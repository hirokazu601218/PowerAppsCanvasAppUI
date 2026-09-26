"""Prepare v1.19 property edits for official Studio compilation."""
import json,hashlib,sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.automation.bridge import read_archive
SOURCE=ROOT/'powerapps/dataverse-v1.18/staff-master.msapp'
OUT=ROOT/'src/staff-master/patches/v1.19'
def nodes(v,path=()):
 if isinstance(v,dict):
  for name,c in v.items():
   if isinstance(c,dict) and 'Properties' in c:yield name,c,path
   yield from nodes(c,path+(name,))
 elif isinstance(v,list):
  for c in v:yield from nodes(c,path)
def candidate():
 archive=read_archive(SOURCE);app=yaml.safe_load(archive['Src/App.pa.yaml']);screen=yaml.safe_load(archive['Src/Screen1.pa.yaml']);controls={n:(o,p) for n,o,p in nodes(screen)};changes=[]
 def edit(name,prop,after):
  obj,path=(app['App'],('App',)) if name=='App' else controls[name];before=obj['Properties'].get(prop)
  if before!=after:changes.append(dict(source='Src/App.pa.yaml' if name=='App' else 'Src/Screen1.pa.yaml',control=name,parent_path='/'.join(path),property=prop,operation='property_add' if before is None else 'property_update',before=before,after=after))
 s=app['App']['Properties']['Formulas'];a=s.index('StaffPayrollHistory = Table(');b=s.index('StaffResidentHistory =',a);s=s[:a]+s[b:]
 marker='// Synthetic histories: source is tests/fixtures/staff-history-synthetic.json.\n'
 payroll='''// Payroll history is filtered on its parent employee in Dataverse.
StaffPayrollHistory = SortByColumns(
    Filter('T_基準給与簿', '職員基本'.職員番号 = StaffSelected.StaffId),
    "crb3c_payment_date",SortOrder.Descending,"crb3c_sequence",SortOrder.Descending
);
'''
 s=s.replace(marker,payroll+marker);edit('App','Formulas',s)
 edit('lblMeta111','Text','="v1.19 ／ Dataverse・" & Text(StaffTestCount) & "名"')
 edit('lblTestNote111','Text','=If(StaffTestCount>100,"テスト対象の上限（100名）を超えたため一覧を表示できません。","テスト環境：職員基本・通勤・認定簿・基準給与簿はDataverseの架空データです。勤務・保険・税控除の履歴は内蔵テストデータです。")')
 edit('btnLoad111','OnSelect',controls['btnLoad111'][0]['Properties']['OnSelect'].replace("Refresh('T_通勤')","Refresh('T_通勤'); Refresh('T_基準給与簿')"))
 mapping=[('給与期間対象年','period_year','text'),('支給年月日','payment_date','text'),('俸給支給額・当給与期間分','basepay_current','amount'),('俸給支給額・返納・追給分','basepay_adjustment','amount'),('通勤手当・当給与期間分','commuting_allowance_current','amount'),('通勤手当・返納・追給分','commuting_allowance_adjustment','amount'),('在宅勤務等手当・当給与期間分','telework_allowance_current','amount'),('在宅勤務等手当・返納・追給分','telework_allowance_adjustment','amount'),('超過勤務手当等・当給与期間分','overtime_allowance_current','amount'),('超過勤務手当等・返納・追給分','overtime_allowance_adjustment','amount'),('給与支給総額','gross','amount'),('控除額計・当給与期間分','deduction_total_current','amount'),('控除額計・返納・追給分','deduction_total_adjustment','amount'),('現金支給額','net','amount'),('備考','remarks','text')]
 def val(field,kind,prefix='ThisItem'):
  ref=prefix+'.crb3c_'+field
  return ref if kind=='text' else 'If(IsBlank('+ref+'),Blank(),Text('+ref+',"#,##0"))'
 for suffix in ['Payroll','PayrollModal']:
  edit('gal'+suffix+'111','Items','=StaffPayrollHistory')
  edit('gal'+suffix+'111','ItemAccessibleLabel','=ThisItem.crb3c_staffnumber & " " & ThisItem.crb3c_payment_date')
  edit('lblSection'+suffix+'111','Text','=IfError("基準給与簿履歴'+('（主要15項目）' if suffix=='PayrollModal' else '')+'　" & Text(CountRows(StaffPayrollHistory)) & "件（Dataverse）","給与データを取得できません")')
  edit('lblEmpty'+suffix+'111','Visible','=IfError(IsEmpty(StaffPayrollHistory),false)')
  for i,(_,field,kind) in enumerate(mapping):edit('lblC'+suffix+'111'+str(i),'Text','='+val(field,kind))
 edit('lblPayrollModalTitle111','Text','="基準給与簿　" & StaffSelected.Name & "　職員番号：" & StaffSelected.StaffId')
 edit('lblPayrollCaution111','Text','="基準給与簿163項目のうち、主要15項目を表示しています。給与項目の出力は表示先頭の支給日が対象です。"')
 edit('btnPayExport111','DisplayMode','=IfError(If(IsEmpty(StaffPayrollHistory),DisplayMode.Disabled,DisplayMode.Edit),DisplayMode.Disabled)')
 rows=','.join('{Key:"'+label+'",Value:'+val(field,kind,'p')+'}' for label,field,kind in mapping)
 edit('btnPayExport111','OnSelect','=IfError(If(!IsEmpty(StaffPayrollHistory),ClearCollect(colReport111,With({p:First(StaffPayrollHistory)},Table('+rows+'))); Set(varTsv111,Concat(colReport111,Key & Char(9) & Value,Char(10))); Set(varReport111,"基準給与簿（主要15項目）"); Set(varReportPage111,1); Set(varPayroll111,false)),Notify("給与データを取得できませんでした。再読込してください。",NotificationType.Error))')
 return changes,mapping
if __name__=='__main__':
 if (OUT/'manifest.json').exists() and json.loads((OUT/'manifest.json').read_text()).get('state','').startswith('PUBLISHED'): raise SystemExit('Published readback is authoritative; do not overwrite its evidence or pending correction.')
 changes,mapping=candidate();(OUT/'properties').mkdir(parents=True,exist_ok=True)
 for c in changes:
  name=c['control']+'.'+c['property']+'.fx';c['property_file']='properties/'+name;(OUT/'properties'/name).write_text(c['after'][1:]+'\n')
 manifest=dict(state='PREPARED_FOR_STUDIO',baseVersion='1.18',targetVersion='1.19',changes=changes)
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(OUT/'field-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
 print('Prepared',len(changes),'property changes')
