"""Prepare the v1.24 UI-only regression fixtures and property patches."""
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'src/screen-ui/v1.24'
OUT.mkdir(exist_ok=True)
fx=(ROOT/'records/src/screen-ui/v1.23/studio-readback/App.Formulas.fx').read_text()
start=fx.index('StaffBasicView = ')
end=fx.index('// Commute records',start)
baseline=fx[start+len('StaffBasicView = '):end].strip().removesuffix(';')
fixture='''UiFixtureMode = Coalesce(varUiFixtureMode,"通常データ");
UiFixtureCount = Switch(UiFixtureMode,"0件",0,"1件",1,"20件",20,"21件",21,"40件",40,"長文・負数",3,-1);
UiRegressionStaff = ForAll(Sequence(40) As n,{
 StaffId:"008800000" & Text(n.Value,"000"),
 Name:If(UiFixtureMode="長文・負数" && n.Value=1,"表示試験 非常に長い氏名の折返しと全文確認のための職員", "表示試験 職員" & Text(n.Value,"00")),
 Org:UiDepartment,OrgFull:If(UiFixtureMode="長文・負数" && n.Value=1,"表示試験専用の非常に長い組織所属名称・管理部門・担当部門・補足名称","表示試験 " & UiDepartment),
 Birth:"1980/01/01",Sex:"男",Hire:"2026/04/01",Leave:"",Status:"在籍",WorkReg:"登録済",
 Daily:If(UiFixtureMode="長文・負数",Switch(n.Value,1,-12345,2,0,Blank()),12000+n.Value),Hours:"7:45",
 CommuteReg:"未登録",Method:"支給なし",Pass:Blank(),Fare:Blank(),SocialReg:"",Health:"",Pension:"",ResidentReg:"",
 TaxMay:Blank(),TaxJune:Blank(),TaxJuly:Blank(),FixedReg:"登録済",TaxClass:"甲",Employment:"加入"
});
'''
fx=fixture+fx[:start]+'StaffBasicView = If(UiFixtureCount>=0,FirstN(UiRegressionStaff,UiFixtureCount),'+baseline+');\n'+fx[end:]
# Fixtures use isolated 0088 IDs and never write to Dataverse.
for group,body in {
 'Work':'{StaffId:s.StaffId,RecordId:"UI-W-" & s.StaffId,Start:Date(2026,4,1),End:Date(2099,3,31),Daily:s.Daily,Scheduled:"7:45",Hours:"7:45",Overtime:0,Change:"表示試験",Reason:"内蔵試験専用",Finish:"17:00",DailyHours:7.75}',
 'Social':'{StaffId:s.StaffId,RecordId:"UI-S-" & s.StaffId,Category:"表示試験",Birth:"1980/01/01",AgeApril:46,AgeMarch:46,Care:"試験",PensionExempt:"試験",Elderly:"試験",Grade:0,Monthly:0}',
 'Tax':'{StaffId:s.StaffId,RecordId:"UI-T-" & s.StaffId,Start:Date(2026,4,1),End:Date(2099,3,31),TaxClass:"甲",Employment:"加入",Saving:0,Loan:0,Dependents:0,Note:If(UiFixtureMode="長文・負数","長文表示試験。全文を確認できることを検証するための補足説明です。これは架空のデータで実際の給与・税・保険の計算を表しません。","内蔵表示試験")}'
}.items():
 marker=f'Staff{group}History = '
 i=fx.index(marker)+len(marker);j=fx.index('\n);',i)+2
 original=fx[i:j]
 fx=fx[:i]+'If(UiFixtureCount>=0,ForAll(UiRegressionStaff As s,'+body+'),'+original+')'+fx[j:]
(OUT/'App.Formulas.fx').write_text(fx)
reset='Set(varUiFixtureMode,Self.Selected.Value); Set(varResultsReady111,false); Set(varStaffChosen111,false); Set(varStaff111,Blank()); Set(varPage111,1); Set(varReport111,""); Set(varPayroll111,false); Set(varLedgerOpen111,false); Set(varUiResultKey,Blank()); Reset(txtKeyword111); Reset(ddOrg111); Reset(ddStatus111)'
nodes=[{'lblUiFixture124':{'Control':'Label@2.5.1','Properties':{'Text':'="画面確認用データ（アプリ内のみ）"','Height':'=36','Width':'=Parent.Width-32','Size':'=12','Font':'="Segoe UI"','Color':'=UiTheme.Text','LayoutMinWidth':'=0','FillPortions':'=0'}}},
 {'ddUiFixture124':{'Control':'Classic/DropDown@2.3.1','Properties':{'Items':'=["通常データ","0件","1件","20件","21件","40件","長文・負数"]','Default':'=UiFixtureMode','OnChange':'='+reset,'AccessibleLabel':'="画面確認用データ"','DisplayMode':'=If(UiIsAdmin,DisplayMode.Edit,DisplayMode.Disabled)','Height':'=44','Width':'=260','Size':'=12','Font':'="Segoe UI"','Color':'=UiTheme.Text','Fill':'=Color.White','BorderColor':'=UiTheme.Border','ChevronBackground':'=Color.White','ChevronFill':'=UiTheme.Primary','SelectionFill':'=UiTheme.Selected','SelectionColor':'=UiTheme.Text','LayoutMinWidth':'=0','FillPortions':'=0'}}}]
(OUT/'fixture-selector.paste.yaml').write_text(yaml.safe_dump(nodes,sort_keys=False,allow_unicode=True))
p=json.loads((OUT/'patches.json').read_text())
p=[x for x in p if x['control'] not in ['App','btnHomeStaff','lblHomePrototype','lblMaintenanceVersion','lblMeta111']]
p.extend([
 {'control':'App','property':'Formulas','file':'App.Formulas.fx'},
 {'control':'btnHomeStaff','property':'DisplayMode','after':'=If(UiFixtureCount<0 && (IsBlank(StaffTestCount) || IsEmpty(StaffBasicView)),DisplayMode.Disabled,DisplayMode.Edit)'},
 {'control':'lblHomePrototype','property':'Text','after':'="UI検討用 v1.24 ｜ 追加画面の金額・料率・権限区分は仮例です"'},
 {'control':'lblMaintenanceVersion','property':'Text','after':'="UI試作 v1.24　／　画面要件定義書 v0.6"'},
 {'control':'lblMeta111','property':'Text','after':'="v1.24 UI試作 ／ " & UiDepartment'}
])
(OUT/'patches.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
print('Prepared App.Formulas and fixture selector; Studio validation required.')
