"""Build the UI-only Canvas screen additions. Studio remains the compiler."""
from pathlib import Path
import json, yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'src/screen-ui/v1.22'
OUT.mkdir(parents=True, exist_ok=True)

def eq(v): return str(v) if str(v).startswith('=') else '=' + str(v)
def quoted(s): return '="' + s.replace('"', '""') + '"'
def node(name, kind, props, children=None, variant=None):
    d={'Control':kind, 'Properties':{k:eq(v) for k,v in props.items()}}
    if variant: d={'Control':kind,'Variant':variant,'Properties':d['Properties']}
    if children is not None: d['Children']=children
    return {name:d}
def label(name,text,height=36,**kw):
    p=dict(Text=text,Height=height,Width='Parent.Width',Font='"Segoe UI"',Size=11,Color='UiTheme.Text',PaddingLeft=12,PaddingRight=12,PaddingTop=4,PaddingBottom=4,FillPortions=0,LayoutMinWidth=0)
    p.update(kw);return node(name,'Label@2.5.1',p)
def button(name,text,action,**kw):
    p=dict(Text=text,AccessibleLabel=text,OnSelect=action,Height=44,Width=180,Font='"Segoe UI"',Size=14,BasePaletteColor='UiTheme.Primary',Appearance='ButtonAppearance.Primary',FillPortions=0,LayoutMinWidth=0)
    p.update(kw);return node(name,'ModernButton@1.0.0',p)
def container(name,children,height=100,horizontal=False,**kw):
    p=dict(Height=height,Width='Parent.Width',LayoutDirection='LayoutDirection.Horizontal' if horizontal else 'LayoutDirection.Vertical',LayoutAlignItems='LayoutAlignItems.Stretch',LayoutGap=8,FillPortions=0,LayoutMinHeight=0,LayoutMinWidth=0,PaddingTop=0,PaddingBottom=0,PaddingLeft=0,PaddingRight=0,DropShadow='DropShadow.None')
    p.update(kw);return node(name,'GroupContainer@1.5.0',p,children,'AutoLayout')
def dropdown(name,items,default,change,**kw):
    p=dict(Items=items,Default=default,OnChange=change,Height=44,Width=180,AccessibleLabel='"支給対象月"',Font='"Segoe UI"',Size=11,BorderColor='UiTheme.Border',BorderThickness=1,Color='UiTheme.Text',Fill='Color.White',ChevronBackground='Color.White',ChevronFill='UiTheme.Primary',SelectionFill='UiTheme.Selected',SelectionColor='UiTheme.Text',FillPortions=0,LayoutMinWidth=0)
    p.update(kw);return node(name,'Classic/DropDown@2.3.1',p)
def inputbox(name,default,**kw):
    p=dict(Default=default,Height=44,Width=160,AccessibleLabel=quoted(name),Font='"Segoe UI"',Size=11,BorderColor='UiTheme.Border',BorderThickness=1,Fill='Color.White',FillPortions=0,LayoutMinWidth=0)
    p.update(kw);return node(name,'Classic/TextInput@2.3.2',p)
def screen(name,title,num,body):
    head=container('con'+name+'Header',[
        label('lbl'+name+'Title',quoted('非常勤給与 ｜ '+title),56,Color='Color.White',Size=15,FontWeight='FontWeight.Semibold',FillPortions=1,Width=500),
        button('btn'+name+'Home',quoted('ホーム'),'Navigate(scrHome,ScreenTransition.None)',Appearance='ButtonAppearance.Outline',Color='Color.White',BorderColor='Color.White',Width=112),
        label('lbl'+name+'Id',quoted(num),56,Color='Color.White',Width=92,Align='Align.Right',Size=10),
    ],height=64,horizontal=True,Fill='UiTheme.Header',PaddingLeft=16,PaddingRight=16,LayoutAlignItems='LayoutAlignItems.Center')
    root=container('con'+name+'Root',[head]+body,height='Parent.Height',Fill='UiTheme.Background',LayoutGap=0)
    d={'Screens':{name:{'Properties':{'Fill':'=UiTheme.Background'},'Children':[root]}}}
    write(name+'.pa.yaml',d);write(name+'.paste.yaml',[root]);return d
def write(name,d): (OUT/name).write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True,width=120),encoding='utf8')

FORMULAS=r'''
// v1.22 UI prototype. All new monetary and access-profile values are synthetic.
UiTheme = {Header:ColorValue("#073B78"),Primary:ColorValue("#0F6CBD"),Text:ColorValue("#242424"),Background:ColorValue("#F7F9FC"),Band:ColorValue("#EDF2F7"),Border:ColorValue("#CBD5E1"),Selected:ColorValue("#DCEAFF")};
UiDepartment = Coalesce(varUiDepartment,"03会計課");
UiIsAdmin = Coalesce(varUiAdmin,false);
UiAccount = {Name:User().FullName,Email:User().Email,Department:UiDepartment,IsAdmin:UiIsAdmin};
UiMonth = Coalesce(varUiMonth,Date(2026,9,1));
UiStaff = ForAll(StaffBasicView As s,{StaffNo:s.StaffId,Name:s.Name,Org:s.Org,DailyRate:9750,AbsenceHourlyRate:1250,ScheduledMinutes:465});
UiSelected = LookUp(UiStaff,StaffNo=varUiStaffNo && Org=UiDepartment);
UiVersion = Coalesce(varUiRegistrationVersion,1);
UiTargetKey = Coalesce(varUiStaffNo,"") & "|" & Text(UiMonth,"yyyy-mm") & "|" & Text(UiVersion);
UiDays = If(Month(UiMonth)=11,0,20);
UiAbsence = If(Month(UiMonth)=11,0,Coalesce(varUiAbsenceMinutes,60));
UiCommute = If(Month(UiMonth)=11,0,6250);
UiRegistered = Month(UiMonth)<>10;
UiFixed = UiSelected.DailyRate * UiDays;
UiReduction = UiSelected.AbsenceHourlyRate * UiAbsence / 60;
UiSalary = UiFixed-UiReduction;
UiGross = UiSalary+UiCommute;
UiDeductionRows = Table(
 {Code:"mutual_short_current",Name:"共済短期掛金",Group:"社会保険関係",Basis:"短期・月額 200,000円 × 仮率4.50%",Amount:9000},
 {Code:"mutual_childcare_current",Name:"子ども・子育て支援掛金",Group:"社会保険関係",Basis:"算定基礎額 200,000円 × 仮率0.10%",Amount:200},
 {Code:"retirement_contribution_current",Name:"退職等年金掛金",Group:"社会保険関係",Basis:"適用区分：対象外（仮例）",Amount:0},
 {Code:"pension_insurance_current",Name:"厚生年金保険料",Group:"社会保険関係",Basis:"厚生年金・月額 200,000円 × 仮率9.00%",Amount:18000},
 {Code:"employment_insurance_current",Name:"雇用保険料",Group:"社会保険関係",Basis:"対象賃金 200,000円 × 仮率0.50%",Amount:1000},
 {Code:"income_tax_current",Name:"所得税",Group:"税・その他",Basis:"税額表参照（仮）：被課税金額165,550円・甲欄・扶養0人。表示用の仮値",Amount:3000},
 {Code:"resident_tax_current",Name:"住民税",Group:"税・その他",Basis:"税額通知書の当月額（仮）を適用",Amount:7000},
 {Code:"savings_current",Name:"貯金預入",Group:"税・その他",Basis:"本人申込額（仮）：毎月10,000円",Amount:10000}
);
UiSocial = If(Month(UiMonth)=11,0,Sum(Filter(UiDeductionRows,Group="社会保険関係"),Amount));
UiDeductions = If(Month(UiMonth)=11,0,Sum(UiDeductionRows,Amount));
UiNet = RoundDown(UiGross-UiDeductions,0);
UiStatus = If(IsBlank(UiSelected.StaffNo),"職員マスタ検索で対象職員を選択してください",!UiRegistered,"勤務時間報告が未登録です",UiGross-UiDeductions<0,"要確認：負の最終額は本試作の対象外です",varUiResultKey<>UiTargetKey,"対象または勤務登録版が変わりました。再計算してください","");
UiReady = IsBlank(UiStatus);
UiDailyRows = ForAll(Sequence(30) As d,{WorkDate:Date(2026,Month(UiMonth),d.Value),DayType:If(d.Value<=20,"勤務日",d.Value=21,"全日欠勤","非勤務日"),RegularMinutes:If(d.Value=1,465-UiAbsence,d.Value<=20,465,0),AbsenceMinutes:If(d.Value=1,UiAbsence,d.Value=21,465,0)});
'''.strip()
(OUT/'App.Formulas.add.fx').write_text(FORMULAS+'\n',encoding='utf8')

select_action='Set(varUiStaffNo,StaffSelected.StaffId); Set(varUiResultKey,Blank()); Navigate(scrPayroll,ScreenTransition.None)'
recalc='Set(varUiResultKey,Blank()); If(!IsBlank(UiSelected.StaffNo) && UiRegistered,Set(varUiResultKey,UiTargetKey))'
money=lambda v:'If(UiReady,If(Mod('+v+',1)=0,Text('+v+',"#,##0"),"約 " & Text('+v+',"#,##0.000000")) & " 円","—")'
targets=lambda tag: container('con'+tag+'Targets',[
    label('lbl'+tag+'Month',quoted('支給対象月'),44,Width=116),
    dropdown('dd'+tag+'Month','["2026/09","2026/10","2026/11"]','Text(UiMonth,"yyyy/mm")','Set(varUiMonth,DateValue(Self.Selected.Value & "/01","ja-JP")); Set(varUiResultKey,Blank())',Width=150),
    label('lbl'+tag+'Staff','If(IsBlank(UiSelected.StaffNo),"対象職員：未選択",UiSelected.StaffNo & "　" & UiSelected.Name & "　｜　" & UiSelected.Org)',44,Width='Max(260,Parent.Width-650)',FillPortions=1),
    button('btn'+tag+'Search',quoted('職員マスタ検索'),'Navigate(Screen1,ScreenTransition.None)',Width=168),
],height='If(Parent.Width<900,108,60)',horizontal=True,LayoutWrap='true',PaddingLeft=16,PaddingRight=16,PaddingTop=8,PaddingBottom=8,Fill='Color.White')

homebody=[
 label('lblHomeAccount','UiAccount.Name & "　｜　" & UiAccount.Email & "　｜　" & UiDepartment',64,PaddingLeft=28,Size=12),
 label('lblHomePrototype',quoted('UI検討用 v1.22 ｜ 追加画面の金額・料率・権限区分は仮例です'),48,PaddingLeft=28,Color='UiTheme.Primary',Fill='ColorValue("#EAF4FF")'),
 container('conHomeActions',[
   button('btnHomeStaff',quoted('職員マスタ検索'),'Navigate(Screen1,ScreenTransition.None)',Width='Parent.Width-48',Height=62),
   button('btnHomeAttendance',quoted('勤務時間報告画面'),'Navigate(scrAttendance,ScreenTransition.None)',Width='Parent.Width-48',Height=62),
   button('btnHomeBonus',quoted('期末勤勉支給率登録画面'),'Navigate(scrBonus,ScreenTransition.None)',Width='Parent.Width-48',Height=62),
   button('btnHomePayroll',quoted('支給明細画面'),'Navigate(scrPayroll,ScreenTransition.None)',Width='Parent.Width-48',Height=62),
   button('btnHomeMaintenance',quoted('メンテナンス画面'),'If(UiIsAdmin,Navigate(scrMaintenance,ScreenTransition.None))',Width='Parent.Width-48',Height=62,DisplayMode='If(UiIsAdmin,DisplayMode.Edit,DisplayMode.Disabled)'),
 ],height=368,PaddingLeft=24,PaddingRight=24,PaddingTop=16,LayoutAlignItems='LayoutAlignItems.Start',LayoutOverflowY='LayoutOverflow.Scroll'),
 container('conHomeDemo',[
   label('lblHomeRole',quoted('確認用の権限区分'),44,Width=180),
   button('btnHomeRole','If(UiIsAdmin,"管理者 → 一般に切替","一般 → 管理者に切替")','Set(varUiAdmin,!UiIsAdmin)',Width=230,Appearance='ButtonAppearance.Outline'),
   label('lblHomeDepartment',quoted('確認用所属'),44,Width=100),
   dropdown('ddHomeDepartment','["01秘書課","02総務課","03会計課"]','UiDepartment','Set(varUiDepartment,Self.Selected.Value); Set(varUiStaffNo,Blank()); Set(varStaff111,Blank()); Set(varStaffChosen111,false); Set(varResultsReady111,false); Set(varPage111,1); Set(varUiResultKey,Blank()); Reset(txtKeyword111); Reset(ddOrg111); Reset(ddStatus111)',AccessibleLabel='"確認用所属"',Width=180),
 ],height=108,horizontal=True,LayoutWrap='true',PaddingLeft=28,PaddingTop=12),
]
screens={};screens.update(screen('scrHome','ホーム','SCR-001',homebody)['Screens'])

attbody=[targets('Attendance'),label('lblAttendanceNote',quoted('画面確認用の仮例 ｜ 日別データと登録操作はアプリ内だけに保持します'),44,PaddingLeft=24,Color='UiTheme.Primary'),
 container('conAttendanceScroll',[
  label('lblAttendanceSummary','"勤務日数 " & Text(UiDays) & "日　｜　控除対象の欠勤 " & Text(UiAbsence/60,If(Mod(UiAbsence,60)=0,"0","0.######")) & "時間　｜　" & If(UiRegistered,"登録済み","未登録")',52,Size=13,FontWeight='FontWeight.Semibold',Fill='UiTheme.Band'),
  label('lblAttendanceColumns',quoted('勤務日　　　　　　　　日区分　　　　　通常勤務　　　　欠勤記録'),40,Fill='UiTheme.Band'),
  node('galAttendanceDays','Gallery@2.15.0',dict(Items='If(!IsBlank(UiSelected.StaffNo) && UiRegistered && Month(UiMonth)<>11,UiDailyRows)',Height=380,Width='Parent.Width',TemplateSize=44,TemplatePadding=0,AccessibleLabel='"勤務時間報告の日別一覧"',Selectable='false',FillPortions=1,LayoutMinHeight=200),[
   label('lblAttendanceDay','Text(ThisItem.WorkDate,"yyyy/mm/dd") & "　　　" & ThisItem.DayType & "　　　" & Text(ThisItem.RegularMinutes) & " 分　　　" & Text(ThisItem.AbsenceMinutes) & " 分"',44,Width='Parent.TemplateWidth',Fill='If(Mod(Day(ThisItem.WorkDate),2)=0,UiTheme.Background,Color.White)')
  ],'Vertical'),
  label('lblAttendanceEmpty','If(IsBlank(UiSelected.StaffNo),"職員マスタ検索から対象職員を選択してください",!UiRegistered,"この月の勤務は未登録です",Month(UiMonth)=11,"登録済みの勤務0日です","")',44),
  container('conAttendanceEdit',[
   label('lblAttendanceAbsence',quoted('勤務日の欠勤（確認用）'),44,Width=215),
   dropdown('ddAttendanceAbsence','["0","30","60","1"]','Text(UiAbsence)','false',AccessibleLabel='"欠勤時間（分）"',Width=100),
   label('lblAttendanceMinutes',quoted('分'),44,Width=40),
   button('btnAttendanceRegister',quoted('月分を登録（仮）'),'If(!IsBlank(UiSelected.StaffNo) && UiRegistered,Set(varUiAbsenceMinutes,Value(ddAttendanceAbsence.Selected.Value)); Set(varUiRegistrationVersion,UiVersion+1); Set(varUiResultKey,Blank()); Notify("アプリ内に登録しました",NotificationType.Success))',Width=195,DisplayMode='If(!IsBlank(UiSelected.StaffNo) && UiRegistered && Month(UiMonth)<>11,DisplayMode.Edit,DisplayMode.Disabled)'),
  ],height=100,horizontal=True,LayoutWrap='true'),
 ],height='Parent.Height-168',PaddingLeft=24,PaddingRight=24,PaddingBottom=16,LayoutOverflowY='LayoutOverflow.Scroll')]
screens.update(screen('scrAttendance','勤務時間報告画面','SCR-003',attbody)['Screens'])

bonusbody=[targets('Bonus'),label('lblBonusNote',quoted('UI検討用の仮入力 ｜ 支給率の業務ルールは未確定です'),48,PaddingLeft=24,Color='UiTheme.Primary'),
 container('conBonusContent',[
  label('lblBonusPeriod',quoted('対象期　2026年12月期'),48,FontWeight='FontWeight.Semibold',Fill='UiTheme.Band'),
  label('lblBonusK',quoted('期末手当 支給率（%）'),36),inputbox('txtBonusK','Coalesce(varUiBonusK,"100")',AccessibleLabel='"期末手当支給率（パーセント）"',Format='TextFormat.Number'),
  label('lblBonusD',quoted('勤勉手当 支給率（%）'),36),inputbox('txtBonusD','Coalesce(varUiBonusD,"100")',AccessibleLabel='"勤勉手当支給率（パーセント）"',Format='TextFormat.Number'),
  button('btnBonusSave',quoted('登録（仮）'),'If(!IsBlank(UiSelected.StaffNo),Set(varUiBonusK,txtBonusK.Text); Set(varUiBonusD,txtBonusD.Text); Notify("画面確認用の値を登録しました",NotificationType.Success))',DisplayMode='If(IsBlank(UiSelected.StaffNo),DisplayMode.Disabled,DisplayMode.Edit)'),
  label('lblBonusSaved','"登録値：期末 " & Coalesce(varUiBonusK,"—") & "% ／ 勤勉 " & Coalesce(varUiBonusD,"—") & "%"',48),
 ],height='Parent.Height-172',PaddingLeft=24,PaddingRight=24,PaddingTop=16,LayoutOverflowY='LayoutOverflow.Scroll',LayoutAlignItems='LayoutAlignItems.Start')]
screens.update(screen('scrBonus','期末勤勉支給率登録画面','SCR-004',bonusbody)['Screens'])

def section_head(name,title,amount):
 return container(name,[label(name+'Title',quoted(title),48,FillPortions=1,Width=700,FontWeight='FontWeight.Semibold',Size=13,Color='UiTheme.Header'),label(name+'Amount',money(amount),48,Width=230,Align='Align.Right',FontWeight='FontWeight.Semibold',Size=14,Color='UiTheme.Primary')],48,True,Fill='UiTheme.Band')
paydetail=[
 section_head('conPayGrossHeading','給与支給総額の内訳','UiGross'),
 container('conPayEarnings',[
  label('lblPayGrossEquation','If(UiReady,"俸給支給額 " & Text(UiSalary,If(Mod(UiSalary,1)=0,"#,##0","#,##0.000000")) & "円 ＋ 通勤手当 " & Text(UiCommute,"#,##0") & "円 ＝ " & Text(UiGross,If(Mod(UiGross,1)=0,"#,##0","#,##0.000000")) & "円","—")',64,Size=12,AutoHeight='true',Fill='Color.White'),
  section_head('conPaySalaryHeading','俸給支給額','UiSalary'),
  label('lblPaySalaryEquation','If(UiReady,"固定額 " & Text(UiFixed,"#,##0") & "円 − 欠勤減額 " & Text(UiReduction,If(Mod(UiReduction,1)=0,"#,##0","#,##0.000000")) & "円 ＝ " & Text(UiSalary,If(Mod(UiSalary,1)=0,"#,##0","#,##0.000000")) & "円","—")',56,AutoHeight='true'),
  label('lblPayFixed','If(UiReady,"固定額　　　　日額単価 " & Text(UiSelected.DailyRate,"#,##0") & "円　×　勤務日数 " & Text(UiDays) & "日　＝　" & Text(UiFixed,"#,##0") & "円","固定額　—")',64,AutoHeight='true',Fill='Color.White'),
  label('lblPayAbsence','If(UiReady,"欠勤減額　　　欠勤時間単価 " & Text(UiSelected.AbsenceHourlyRate,"#,##0") & "円/時　×　" & If(Mod(UiAbsence,3)<>0,"約 ","") & Text(UiAbsence/60,If(Mod(UiAbsence,60)=0,"0","0.######")) & "時間　＝　" & If(Mod(UiAbsence,3)<>0,"約 ","") & Text(UiReduction,If(Mod(UiReduction,1)=0,"#,##0","#,##0.000000")) & "円","欠勤減額　—")',64,AutoHeight='true',Fill='Color.White'),
  label('lblPayAbsenceNote',quoted('全日欠勤は勤務日数・欠勤減額に含めません'),36,Size=10),
  section_head('conPayCommuteHeading','通勤手当','UiCommute'),
  label('lblPayCommuteBasis','If(UiReady,"支給方式：毎月固定　｜　適用期間：2026/04/01 ～ 2027/03/31" & Char(10) & "通勤毎月 " & Text(UiCommute,"#,##0") & "円 → 通勤" & Text(Month(UiMonth)) & "月 " & Text(UiCommute,"#,##0") & "円" & Char(10) & "認定済みの当月支給額を使用（仮例）。","通勤手当の根拠　—")',104,AutoHeight='true'),
 ],height='If(Coalesce(varUiEarningsOpen,true),lblPayGrossEquation.Height+48+lblPaySalaryEquation.Height+lblPayFixed.Height+lblPayAbsence.Height+36+48+lblPayCommuteBasis.Height+56,0)',Visible='Coalesce(varUiEarningsOpen,true)',LayoutOverflowY='LayoutOverflow.Scroll',Fill='Color.White',PaddingLeft=12,PaddingRight=12),
 section_head('conPayDeductionHeading','控除額計の内訳　｜　当給与期間分','UiDeductions'),
]
deductchildren=[]
for group in ['社会保険関係','税・その他']:
 tag='Social' if group=='社会保険関係' else 'Tax'
 deductchildren.append(label('lblPay'+tag+'Heading',quoted(group),44,Fill='UiTheme.Band',FontWeight='FontWeight.Semibold',Size=12))
 rows=[('共済短期掛金',0),('子ども・子育て支援掛金',1),('退職等年金掛金',2),('厚生年金保険料',3),('雇用保険料',4)] if group=='社会保険関係' else [('所得税',5),('住民税',6),('貯金預入',7)]
 for title,i in rows:
  rec=f'Index(UiDeductionRows,{i+1})'
  deductchildren.append(container('conPayDeduction'+str(i),[
    label('lblPayDeductionName'+str(i),quoted(title),64,Width='If(Parent.Width<750,Parent.Width*0.4,260)',FontWeight='FontWeight.Semibold'),
    label('lblPayDeductionBasis'+str(i),'If(Month(UiMonth)=11,"登録済み0円（仮例）",'+rec+'.Basis)',64,Width='Max(180,Parent.Width-410)',FillPortions=1,Size=10),
    label('lblPayDeductionAmount'+str(i),money('If(Month(UiMonth)=11,0,'+rec+'.Amount)'),64,Width=138,Align='Align.Right',FontWeight='FontWeight.Semibold'),
  ],height='If(Parent.Width<750,128,64)',horizontal=True,LayoutWrap='true',Fill='Color.White'))
 if group=='社会保険関係':deductchildren.append(section_head('conPaySocialTotal','社会保険料計','UiSocial'))
paydetail.append(container('conPayDeductions',deductchildren,height='If(Coalesce(varUiDeductionsOpen,true),If(Parent.Width<750,1210,698),0)',Visible='Coalesce(varUiDeductionsOpen,true)',Fill='Color.White',PaddingLeft=12,PaddingRight=12))
summary=[]
for tag,title,value in [('Gross','給与支給総額','UiGross'),('Deduct','控除額計','UiDeductions'),('Net','現金支給額','UiNet')]:
 summary.append(container('conPaySummary'+tag,[label('lblPaySummary'+tag+'Title',quoted(title),32,Align='Align.Center',Size=12),label('lblPaySummary'+tag+'Value',money(value),58,Align='Align.Center',Size=24 if tag=='Net' else 21,Color='UiTheme.Primary' if tag=='Net' else 'UiTheme.Text',FontWeight='FontWeight.Semibold')],104,FillPortions=1,Width=350,Fill='ColorValue("#EAF4FF")' if tag=='Net' else 'Color.White'))
 if tag!='Net':summary.append(label('lblPaySummary'+tag+'Operator',quoted('−' if tag=='Gross' else '＝'),104,Width=28,Align='Align.Center',Size=21))
paybody=[targets('Payroll'),label('lblPayPrototype',quoted('画面確認用の仮例｜金額・料率・適用区分は未確定'),40,PaddingLeft=24,Color='UiTheme.Primary',Fill='ColorValue("#EAF4FF")'),
 container('conPaySummary',summary,104,True,PaddingLeft=16,PaddingRight=16,LayoutGap=0),
 container('conPayActions',[
  button('btnPayEarnings','If(Coalesce(varUiEarningsOpen,true),"▼ 支給の内訳","▶ 支給の内訳")','Set(varUiEarningsOpen,!Coalesce(varUiEarningsOpen,true))',Width=190),
  button('btnPayDeductions','If(Coalesce(varUiDeductionsOpen,true),"▼ 控除の内訳","▶ 控除の内訳")','Set(varUiDeductionsOpen,!Coalesce(varUiDeductionsOpen,true))',Width=190,Appearance='ButtonAppearance.Outline'),
  button('btnPayRecalculate',quoted('再計算'),recalc,Width=136,DisplayMode='If(IsBlank(UiSelected.StaffNo),DisplayMode.Disabled,DisplayMode.Edit)'),
 ],56,True,PaddingLeft=24,PaddingTop=6,LayoutWrap='true'),
 label('lblPayState','UiStatus', 'If(UiReady,0,40)',Visible='!UiReady',Color='ColorValue("#9F3A00")',PaddingLeft=24),
 container('conPayBody',paydetail,'Parent.Height-64-If(Parent.Width<900,108,60)-40-104-56-If(UiReady,0,40)',PaddingLeft=20,PaddingRight=20,PaddingTop=12,PaddingBottom=20,LayoutGap=12,LayoutOverflowY='LayoutOverflow.Scroll'),
]
screens.update(screen('scrPayroll','支給明細画面','SCR-005',paybody)['Screens'])
screens['scrPayroll']['Properties']['OnVisible']='='+recalc

maintbody=[label('lblMaintenanceNote',quoted('管理者用 ｜ UI検討用のメンテナンス画面'),56,PaddingLeft=24,Color='UiTheme.Primary'),
 container('conMaintenanceBody',[
  label('lblMaintenanceAccess','If(UiIsAdmin,"確認用所属：" & UiDepartment & " ／ 管理者","この画面は管理者のみ利用できます")',52,Fill='UiTheme.Band',FontWeight='FontWeight.Semibold'),
  label('lblMaintenanceData',quoted('内蔵テストデータ'),40,FontWeight='FontWeight.Semibold',Size=13),
  label('lblMaintenanceHelp',quoted('登録した仮の勤務時間・支給率と選択状態を初期状態に戻します。'),56),
  button('btnMaintenanceReset',quoted('仮入力を初期化'),'If(UiIsAdmin,Set(varUiAbsenceMinutes,60); Set(varUiRegistrationVersion,UiVersion+1); Set(varUiBonusK,Blank()); Set(varUiBonusD,Blank()); Set(varUiStaffNo,Blank()); Set(varUiResultKey,Blank()); Notify("仮入力を初期化しました",NotificationType.Success))',DisplayMode='If(UiIsAdmin,DisplayMode.Edit,DisplayMode.Disabled)',Width=220),
  label('lblMaintenanceVersion',quoted('UI試作 v1.22　／　画面要件定義書 v0.6'),52),
 ],'Parent.Height-120',PaddingLeft=24,PaddingRight=24,PaddingTop=16,LayoutAlignItems='LayoutAlignItems.Start',Visible='UiIsAdmin')]
screens.update(screen('scrMaintenance','メンテナンス画面','SCR-006',maintbody)['Screens'])
screens['scrMaintenance']['Properties']['OnVisible']='=If(!UiIsAdmin,Notify("この画面は管理者のみ利用できます",NotificationType.Warning))'

nav=container('conStaffNavigation122',[
 button('btnStaffHome122',quoted('ホーム'),'Navigate(scrHome,ScreenTransition.None)',Width=110),
 label('lblStaffAccount122','UiAccount.Name & "　｜　" & UiDepartment',44,FillPortions=1,Width=340),
 dropdown('ddStaffMonth122','["2026/09","2026/10","2026/11"]','Text(UiMonth,"yyyy/mm")','Set(varUiMonth,DateValue(Self.Selected.Value & "/01","ja-JP")); Set(varUiResultKey,Blank())',Width=145),
 button('btnStaffPayroll122',quoted('支給明細画面'),select_action,Width=180,DisplayMode='If(Coalesce(varStaffChosen111,false) && StaffSelected.Org=UiDepartment,DisplayMode.Edit,DisplayMode.Disabled)'),
 label('lblStaffId122',quoted('SCR-002'),44,Width=92,Align='Align.Right'),
 ],60,True,X=0,Y=0,Fill='UiTheme.Band',PaddingLeft=16,PaddingRight=16,PaddingTop=8,LayoutWrap='true')
write('Screen1.navigation.paste.yaml',[nav])
write('Screens.pa.yaml',{'Screens':screens})
for name,d in screens.items(): write(name+'.pa.yaml',{'Screens':{name:d}})

base=yaml.safe_load((ROOT/'src/staff-master/patches/v1.21/studio-readback/App.pa.yaml').read_text())
original=base['App']['Properties']['Formulas']
updated=original.replace('SortByColumns(\'M_職員基本\', "crb3c_staffnumber", SortOrder.Ascending)','SortByColumns(Filter(\'M_職員基本\',crb3c_orgshort=UiDepartment), "crb3c_staffnumber", SortOrder.Ascending)')
assert updated!=original
updated+='\n'+FORMULAS
base['App']['Properties']['Formulas']=updated
base['App']['Properties']['StartScreen']='=scrHome'
write('App.pa.yaml',base)
(OUT/'App.Formulas.fx').write_text(updated.removeprefix('='),encoding='utf8')
(OUT/'App.StartScreen.fx').write_text('scrHome\n')
manifest={'version':'1.22','requirements':'screen-requirements.md v0.6','issue':52,'baseline':'src/staff-master/patches/v1.21/studio-readback','new_screens':list(screens),'existing_screen':'Screen1','existing_changes':{'conStaffMaster111.Y':'=60','conStaffMaster111.Height':'=Parent.Height-60','lblMeta111.Text':'="v1.22 UI試作 ／ " & UiDepartment'},'studio_required':True,'calculation_scope':'UI-only dummy model; new payroll, access profile, attendance, bonus rates are synthetic. No Dataverse write.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'screens':list(screens),'files':len(list(OUT.glob('*')))},ensure_ascii=False))
