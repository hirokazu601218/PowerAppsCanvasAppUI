"""Mechanically retain current search/summary/navigation and replace detail subtrees."""
import copy,json,re
from pathlib import Path
import yaml
import build_payroll as pay
ROOT=Path(__file__).parent; OUT=ROOT/'candidate'
src=yaml.safe_load((ROOT/'baseline/Screen1.pa.yaml').read_text()); nodes={}
def index(xs):
 for x in xs:
  for n,v in x.items(): nodes[n]=v;index(v.get('Children',[]))
index(src['Screens']['Screen1']['Children'])
clone=lambda n:{n:copy.deepcopy(nodes[n])}
def props(x,**kwargs):
 next(iter(x.values()))['Properties'].update({k:'='+str(v) for k,v in kwargs.items()});return x
def label(n,text,x=0,y=0,w='Parent.Width',h=44):return pay.label(n,text,x,y,w,h)
def button(n,text,action,x=0,y=0,w=140):
 return pay.control(n,'ModernButton@1.0.0',{'Text':json.dumps(text,ensure_ascii=False),'AccessibleLabel':json.dumps(text,ensure_ascii=False),'OnSelect':action,'X':x,'Y':y,'Width':w,'Height':44,'BasePaletteColor':'ColorValue("#0F6CBD")','Font':'"Segoe UI"'})
def gallery(n,items,children,**p):
 return pay.control(n,'Gallery@2.15.0',dict(Items=items,Width='Parent.Width',TemplatePadding=0,**p),children,'BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0')

# All legacy PDF/modal state is removed from retained controls.
def clean(v):
 for k,x in v.get('Properties',{}).items():
  if k=='TabIndex' and ('varLedger' in str(x) or 'varReport111' in str(x)):v['Properties'][k]='=0'
  if k=='DisplayMode' and ('varLedger' in str(x) or 'varReport111' in str(x)):v['Properties'][k]='=DisplayMode.Edit'
 for c in v.get('Children',[]):clean(next(iter(c.values())))

sidebar=clone('conSearchSidebar111');clean(next(iter(sidebar.values())))
sn={}
def subindex(xs):
 for x in xs:
  for n,v in x.items():sn[n]=v;subindex(v.get('Children',[]))
subindex([sidebar])
def sp(n,**kw):sn[n]['Properties'].update({k:'='+str(v) for k,v in kw.items()})
props(sidebar,X=0,Y=72,Width='If(Coalesce(varSearchSidebarExpanded111,true),Min(320,Parent.Width*0.38),48)',Height='Parent.Height-Self.Y')
sp('conLeftSurface111',Width='Parent.Width-24')
sp('lblSidebarTitle111',Visible='Coalesce(varSearchSidebarExpanded111,true)',Width='Parent.Width-52')
sp('btnSidebarToggle111',OnSelect='Set(varSearchSidebarExpanded111,!Coalesce(varSearchSidebarExpanded111,true))')
sp('txtKeyword111',Placeholder='"職員を検索"',Y=28,Width='Parent.Width',Type='TextInputType.Search')
sp('lblOrg111',X=0,Y=80,Width='Parent.Width');sp('ddOrg111',X=0,Y=108,Width='Parent.Width')
sp('lblStatus111',X=0,Y=160,Width='Parent.Width');sp('ddStatus111',X=0,Y=188,Width='Parent.Width')
sp('btnSearch111',X=0,Y=240,Width='(Parent.Width-8)/2')
sp('btnClear111',X='(Parent.Width+8)/2',Y=240,Width='(Parent.Width-8)/2',Text='"クリア"')
sp('lblListTitle111',Y=292);sp('btnPrev111',Y=332);sp('btnNext111',Y=332);sp('lblPage111',Y=332)
sp('galStaff111',Y=384,TemplateSize='If(Coalesce(varLargeText111,false),92,84)',OnSelect='Set(varStaff111,ThisItem); Set(varStaffChosen111,true); Select(btnLoadDetails111)')
sp('btnPrev111',DisplayMode='If(Coalesce(varPage111,1)<=1,DisplayMode.Disabled,DisplayMode.Edit)')
sp('btnNext111',DisplayMode='If(Coalesce(varPage111,1)*20>=If(Coalesce(varResultsReady111,false),CountRows(colResult111),CountRows(StaffBasicView)),DisplayMode.Disabled,DisplayMode.Edit)')
sp('galStaff111',Height='Max(1,CountRows(Self.AllItems))*Self.TemplateHeight')
# Name above staff number; employment state above department abbreviation.
sp('lblListC1111',X=10,Y=8,Width='Parent.TemplateWidth-104',Height=34,Wrap='true')
sp('lblListC0111',Text='ThisItem.StaffId',X=10,Y=44,Width='Parent.TemplateWidth-104',Height=28,Visible='true')
sp('lblListC3111',X='Parent.TemplateWidth-94',Y=8,Width=90,Height=30)
sp('lblListC2111',X='Parent.TemplateWidth-94',Y=44,Width=90,Height=28)
sp('lblSelectedMarker111',Visible='false')
sp('btnRow111',Text='ThisItem.Name & " " & ThisItem.StaffId & " 詳細を表示"',X=0,Y=0,Width='Parent.TemplateWidth',Height='Parent.TemplateHeight')
search=sn['btnSearch111']['Properties']['OnSelect'].split('; Set(varReport111')[0]
sp('btnSearch111',OnSelect=search[1:]+'; Select(btnLoadDetails111)')
sp('btnClear111',OnSelect='Reset(txtKeyword111); Reset(ddOrg111); Reset(ddStatus111); Set(varResultsReady111,false); Set(varStaffChosen111,true); Set(varStaff111,First(StaffBasicView)); Set(varPage111,1); Reset(galStaff111); Select(btnLoadDetails111)')

# Common metadata retains original label/value expressions for synthetic histories.
sections={}
for section,key in [('Work','Work'),('Social','Social'),('Tax','Tax')]:
 vals=[]
 for item in nodes['gal'+key+'111']['Children']:
  name,node=next(iter(item.items()))
  header=nodes.get(name.replace('lblC','lblH',1))
  if header:
   expr=node['Properties']['Text'][1:].replace('ThisItem.','p.')
   lab=header['Properties']['Text'][1:]
   vals.append((lab,expr))
 vals.insert(0,('"レコードID"','p.RecordId'))
 sections[section]=vals
def record_table(section,values,idexpr):
 return 'Table('+','.join('{Section:"'+section+'",Order:'+str(i)+',Key:"'+str(i)+'",Label:'+lab+',DisplayText:Text('+expr+'),IsBlankValue:IsBlank('+expr+'),SourceRecordId:'+idexpr+'}' for i,(lab,expr) in enumerate(values,1))+')'
def dbfields(file,alias,exclude):
 values=[]
 for c in json.loads((ROOT/file).read_text()):
  if c['type'] in ['Virtual','Lookup','Uniqueidentifier'] or c['key'] in exclude:continue
  expr=alias+'.'+c['key']
  if c['type']=='DateTime':expr='If(IsBlank('+expr+'),Blank(),Text('+expr+',"yyyy/mm/dd"))'
  elif c['type'] in ['Integer','Decimal','Double','Money']:expr='If(IsBlank('+expr+'),Blank(),Text('+expr+',If(Mod('+expr+',1)=0,"#,##0","#,##0.####")))'
  else:expr='Text('+expr+')'
  values.append((json.dumps(c['label'],ensure_ascii=False),expr))
 return values
sections['Basic']=dbfields('crb3c_studiostaffbasic-columns.json','p',{'crb3c_name'})
sections['Commute']=dbfields('crb3c_studiocommute-columns.json','p',{'crb3c_name','crb3c_staffbasicidname'})
fx=(ROOT/'baseline/App.Formulas.fx').read_text()
fx=re.sub(r'StaffLedgerFields = .*?\nStaffPayrollHistory =', 'StaffPayrollHistory =',fx,flags=re.S)
# Named formulas operate on cached records. The only Dataverse reads are behavior properties.
fx=fx.replace("CountIf('M_職員基本_STUDIO', true)", 'CountRows(colStaffSource111)')
fx=fx.replace("Filter('M_職員基本_STUDIO',crb3c_orgshort=UiDepartment)", 'colStaffSource111')
fx=fx.replace('StaffTestCount <= 100','StaffTestCount <= 2000')
fx=re.sub(r'StaffCommuteHistory = .*?;\n','StaffCommuteHistory = colCommute111;\n',fx,flags=re.S)
fx=re.sub(r'StaffPayrollHistory = .*?;\n','StaffPayrollHistory = colPayrollSource111;\n',fx,flags=re.S)
fx=fx.replace('UiMonth = Coalesce(varUiMonth,Date(2026,9,1));','UiMonth = Coalesce(varUiMonth,Date(Year(Today()),Month(Today()),1));')
fx=fx.replace('StaffSelected = If(Coalesce(varStaffChosen111,false),varStaff111,First(StaffBasicView));','StaffSelected = varStaff111;')
detail=['StaffDetailFields111 = Switch(Coalesce(varStaffDetailTab111,"Basic"),']
for section in ['Basic','Work','Commute','Social','Tax']:
 lookup={'Basic':'varStaffSource111','Work':'LookUp(colWork111,RecordId=varHistoryId111)','Commute':'LookUp(colCommute111,Text(crb3c_studiocommuteid)=varHistoryId111)','Social':'LookUp(colSocial111,RecordId=varHistoryId111)','Tax':'LookUp(colTax111,RecordId=varHistoryId111)'}[section]
 idexpr='StaffSelected.StaffId' if section=='Basic' else 'varHistoryId111'
 detail.append('"'+section+'",With({p:'+lookup+'},'+record_table(section,sections[section],idexpr)+'),')
detail.append('FirstN(Table({Section:"",Order:0,Key:"",Label:"",DisplayText:"",IsBlankValue:true,SourceRecordId:""}),0));')
fx+='\n'+'\n'.join(detail)+'\n'
(OUT/'App.Formulas.fx').write_text(fx)

tabitems='Table({Key:"Basic",Label:"基本情報"},{Key:"Work",Label:"勤務条件"},{Key:"Commute",Label:"通勤"},{Key:"Social",Label:"社会保険"},{Key:"Tax",Label:"税固定控除"},{Key:"Payroll",Label:"給与"})'
tabs=gallery('galDetailTabs111',tabitems,[props(button('btnDetailTab111','', 'Set(varStaffDetailTab111,ThisItem.Key); Set(varHistoryId111,First(Filter(colHistory111,Section=ThisItem.Key)).RecordId)',w='Parent.TemplateWidth-6'),Text='ThisItem.Label',AccessibleLabel='ThisItem.Label',Appearance='If(Coalesce(varStaffDetailTab111,"Basic")=ThisItem.Key,ButtonAppearance.Primary,ButtonAppearance.Outline)')],Height='RoundUp(6/Max(1,RoundDown(Self.Width/130,0)),0)*52',WrapCount='Max(1,RoundDown(Self.Width/130,0))',TemplateSize=52,Y='conPerson111.Y+conPerson111.Height+12',Selectable='false',ShowScrollbar='false')
history=gallery('galHistory111','Filter(colHistory111,Section=varStaffDetailTab111)',[label('lblHistory111','ThisItem.Title & Char(10) & ThisItem.Period & "  " & ThisItem.State',8,0,'Parent.TemplateWidth-16',72)],Height='If(Self.Visible,Min(3,CountRows(Self.AllItems))*80,0)',TemplateSize=80,Y='galDetailTabs111.Y+galDetailTabs111.Height+52',OnSelect='Set(varHistoryId111,ThisItem.RecordId)',Visible='varStaffDetailTab111 in ["Work","Commute","Social","Tax"]',TemplateFill='If(ThisItem.RecordId=varHistoryId111,ColorValue("#DCEAFF"),ColorValue("#FFFFFF"))')
history['galHistory111']['Children'][0]['lblHistory111']['Properties']['OnSelect']='=Select(Parent)'
detailgal=gallery('galDetailFields111','StaffDetailFields111',[props(label('lblDetailKey111','ThisItem.Label',12,8,'Parent.TemplateWidth-24',44),Fill='ColorValue("#EDF2F7")'),props(label('lblDetailValue111','If(ThisItem.IsBlankValue,"",ThisItem.DisplayText)',12,56,'Parent.TemplateWidth-24',100),AutoHeight='true',BorderThickness=0)],Y='galHistory111.Y+galHistory111.Height+8',Height='If(Self.Visible,RoundUp(CountRows(StaffDetailFields111)/2,0)*Self.TemplateHeight,0)',WrapCount=2,TemplateSize='Max(130,80+Max(StaffDetailFields111,RoundUp(Len(DisplayText)/Max(1,RoundDown((Self.Width/2-32)/If(Coalesce(varLargeText111,false),20,16),0)),0)+Len(DisplayText)-Len(Substitute(DisplayText,Char(10),"")))*If(Coalesce(varLargeText111,false),30,24))',ShowScrollbar='false',Selectable='false',Visible='!IsBlank(StaffSelected.StaffId) && varStaffDetailTab111<>"Payroll" && (varStaffDetailTab111="Basic" || !IsBlank(varHistoryId111))')

summary=clone('conPerson111');props(summary,X=0,Y='conStaffActions111.Height+12',Width='Parent.Width',Visible='!IsBlank(StaffSelected.StaffId)')
nav=[]
for c in nodes['conStaffNavigation122']['Children']:
 n,v=next(iter(c.items()))
 if n in ['lblStaffId122','lblStaffAccount122']:continue
 q=copy.deepcopy(c);clean(next(iter(q.values())));nav.append(q)
nav.append(clone('btnTextSize111'));clean(next(iter(nav[-1].values())))
props(nav[-1],Color='ColorValue("#0F6CBD")',BorderColor='ColorValue("#0F6CBD")')
nav.append(button('btnDetailShow111','詳細表示','Set(varStaffDetailTab111,"Basic")'))
# Baseline SCR-002 has no editable controls. Do not introduce unapproved master updates.
nav.append(props(button('btnDiscard111','変更を破棄','false'),DisplayMode='DisplayMode.Disabled',Tooltip='"この画面は表示専用です"'))
nav.append(props(button('btnSave111','保存','false'),DisplayMode='DisplayMode.Disabled',Tooltip='"この画面は表示専用です"'))
for c in nav:
 n,v=next(iter(c.items()));v['Properties'].pop('X',None);v['Properties'].pop('Y',None);v['Properties']['Width']='=140'
 if n=='ddStaffMonth122':
  v['Properties']['Items']='=ForAll(Sequence(61),Text(DateAdd(Date(Year(Today()),Month(Today()),1),Value-31,TimeUnit.Months),"yyyy/mm"))'
  v['Properties']['Default']='=Text(UiMonth,"yyyy/mm")'
actions=pay.group('conStaffActions111',{'Width':'Parent.Width','Height':'RoundUp(7/Max(1,RoundDown(Self.Width/148,0)),0)*52','LayoutDirection':'LayoutDirection.Horizontal','LayoutWrap':'true','LayoutGap':8,'LayoutAlignItems':'LayoutAlignItems.Start'},nav,True)

payroot=copy.deepcopy(pay.root)
props(payroot,Y='galDetailTabs111.Y+galDetailTabs111.Height+8',Width='Parent.Width',Height=800,Visible='varStaffDetailTab111="Payroll" && !IsBlank(StaffSelected.StaffId)')
# Explicit stable relative dimensions, then verify all formulas after paste.
pnode=payroot['conPayrollLight111']
for c in pnode['Children']:
 n,v=next(iter(c.items()))
 if n.startswith('dpPayroll'):v['Properties']['EndYear']='=Year(Today())+100'
 if n=='conPayrollScroll111':
  v['Properties']['Height']='=640';v['Properties']['Y']='=lblPayrollState111.Y+lblPayrollState111.Height+8'
  grid=v['Children'][0]['conPayrollGrid111'];grid['Properties']['Height']='=616'
  for k in grid['Children']:
   if 'galPayrollRows111' in k:k['galPayrollRows111']['Properties']['Height']='=536'
nohistory=props(label('lblHistoryEmpty111','If(IsBlank(StaffSelected.StaffId),"職員を選択してください", "登録されている履歴はありません")',0,'galDetailTabs111.Y+galDetailTabs111.Height+8'),Visible='IsBlank(StaffSelected.StaffId) || (varStaffDetailTab111 in ["Work","Commute","Social","Tax"] && IsEmpty(Filter(colHistory111,Section=varStaffDetailTab111)))')
htmlbtn=props(button('btnCertificate111','認定簿表示','If(varHistoryStaff111=StaffSelected.StaffId && !IsBlank(varHistoryId111) && !IsBlank(LookUp(colCommute111,Text(crb3c_studiocommuteid)=varHistoryId111 && 職員基本.職員番号=StaffSelected.StaffId)),Launch(varCommuteReportBase111 & "?id=" & EncodeUrl(varHistoryId111),{},LaunchTarget.New),Notify("通勤認定レコードを選び直してください。",NotificationType.Error))',x='Max(0,Parent.Width-150)',y='galDetailTabs111.Y+galDetailTabs111.Height+4',w=150),Visible='varStaffDetailTab111="Commute"',DisplayMode='If(IsBlank(varHistoryId111)||IsBlank(varCommuteReportBase111),DisplayMode.Disabled,DisplayMode.Edit)')
body=pay.group('conRightSurface111',{'Width':'Parent.Width-16','Height':'Max(conStaffActions111.Height+100,If(varStaffDetailTab111="Payroll",conPayrollLight111.Y+conPayrollLight111.Height,galDetailFields111.Y+galDetailFields111.Height))+24','LayoutMinHeight':'Self.Height','FillPortions':0,'AlignInContainer':'AlignInContainer.Start'},[actions,summary,tabs,history,detailgal,nohistory,htmlbtn,payroot])
right=pay.group('conRightScroll111',{'X':'conSearchSidebar111.Width+12','Y':72,'Width':'Parent.Width-Self.X','Height':'Parent.Height-Self.Y','LayoutDirection':'LayoutDirection.Vertical','LayoutOverflowY':'LayoutOverflow.Scroll','PaddingRight':16},[body],True)
header=pay.group('conHeader111',{'Width':'Parent.Width','Height':64},[props(label('lblApp111','"非常勤職員マスタ検索  |  SCR-002"',0,0,'Parent.Width',32),Fill='ColorValue("#073B78")',Color='ColorValue("#FFFFFF")'),props(label('lblMeta111','If(IsBlank(varFetched111),Coalesce(varFetchError111,"データ取得中"),"取得日時：" & Text(varFetched111,"yyyy/mm/dd hh:mm:ss"))',0,32,'Parent.Width',32),Fill='ColorValue("#073B78")',Color='ColorValue("#FFFFFF")')])
historybuild='''ClearCollect(colHistory111,
 ForAll(colWork111 As p,{Section:"Work",RecordId:p.RecordId,Title:p.RecordId,Period:Text(p.Start,"yyyy/mm/dd") & " ～ " & If(p.End=Date(2099,3,31),"",Text(p.End,"yyyy/mm/dd")),State:If(p.Start>Today(),"予定",p.End<Today(),"過去","現行")}),
 ForAll(colSocial111 As p,{Section:"Social",RecordId:p.RecordId,Title:p.RecordId,Period:p.Category,State:"登録済"}),
 ForAll(colTax111 As p,{Section:"Tax",RecordId:p.RecordId,Title:p.RecordId,Period:Text(p.Start,"yyyy/mm/dd") & " ～ " & If(p.End=Date(2099,3,31),"",Text(p.End,"yyyy/mm/dd")),State:If(p.Start>Today(),"予定",p.End<Today(),"過去","現行")}),
 ForAll(colCommute111 As p,{Section:"Commute",RecordId:Text(p.crb3c_studiocommuteid),Title:p.crb3c_recognitionid & " / " & p.crb3c_method,Period:Text(p.crb3c_startdate,"yyyy/mm/dd") & " ～ " & Text(p.crb3c_enddate,"yyyy/mm/dd"),State:If(p.crb3c_startdate>Today(),"予定",!IsBlank(p.crb3c_enddate)&&p.crb3c_enddate<Today(),"過去","現行")}));
Set(varHistoryId111,First(Filter(colHistory111,Section=varStaffDetailTab111)).RecordId);'''
fetch='''Set(varFetched111,Blank()); Set(varFetchError111,Blank()); Set(varHistoryId111,Blank()); Set(varHistoryStaff111,StaffSelected.StaffId);
Clear(colCommute111);Clear(colWork111);Clear(colSocial111);Clear(colTax111);Clear(colHistory111);Clear(colPayrollSource111);Clear(colPayrollColumns111);Clear(colPayrollExceptions111);
Set(varStaffSource111,LookUp(colStaffSource111,crb3c_staffnumber=StaffSelected.StaffId));
If(!IsBlank(StaffSelected.StaffId),IfError(
 ClearCollect(colCommute111,Filter('T_通勤_STUDIO',職員基本.職員番号=StaffSelected.StaffId));
 ClearCollect(colWork111,Filter(StaffWorkHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colSocial111,Filter(StaffSocialHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colTax111,Filter(StaffTaxHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colPayrollSource111,Filter('T_基準給与簿_STUDIO',crb3c_staffnumber=StaffSelected.StaffId));
 '''+historybuild+pay.build+'''
 Set(varFetched111,Now()),
 Clear(colCommute111);Clear(colHistory111);Clear(colPayrollSource111);Clear(colPayrollColumns111);Clear(colPayrollExceptions111);Set(varHistoryId111,Blank());Set(varFetchError111,"詳細データを取得できませんでした");Notify(varFetchError111,NotificationType.Error)),Set(varFetched111,Now()));'''
fetchbtn=props(button('btnLoadDetails111','',fetch),Visible='false')
root=pay.group('conStaffMaster111',{'X':'Parent.Width*4/64','Y':'Parent.Height*2/30','Width':'Parent.Width*56/64','Height':'Parent.Height*26/30'},[header,sidebar,right,fetchbtn])
onvisible='''Set(varCommuteReportBase111,"");Set(varStaffDetailTab111,Coalesce(varStaffDetailTab111,"Basic"));
Set(varPayrollStart111,Coalesce(varPayrollStart111,Date(Year(Today()),1,1)));Set(varPayrollEnd111,Coalesce(varPayrollEnd111,Date(Year(Today()),12,1)));
Set(varFetched111,Blank());Set(varFetchError111,Blank());Set(varStaffChosen111,true);
IfError(Refresh('M_職員基本_STUDIO');Refresh('T_通勤_STUDIO');Refresh('T_基準給与簿_STUDIO');ClearCollect(colStaffSource111,Filter('M_職員基本_STUDIO',crb3c_orgshort=UiDepartment));
Set(varStaff111,Coalesce(LookUp(StaffBasicView,StaffId=varStaff111.StaffId),First(StaffBasicView)));Set(varResultsReady111,false);Select(btnLoadDetails111),
Clear(colStaffSource111);Set(varStaff111,Blank());Select(btnLoadDetails111);Set(varFetchError111,"職員データを取得できませんでした");Set(varFetched111,Blank()));'''
(OUT/'Screen.OnVisible.fx').write_text(onvisible)
screen={'Screens':{'scrStaffMasterSearch':{'Properties':dict(src['Screens']['Screen1']['Properties'],OnVisible='='+onvisible),'Children':[root]}}}
def dump(p,v):(OUT/p).write_text(yaml.dump(v,Dumper=pay.Dumper,allow_unicode=True,sort_keys=False,width=100000))
dump('scrStaffMasterSearch.pa.yaml',screen);dump('scrStaffMasterSearch.paste.yaml',[root])
allnames=[]
def names(xs):
 for x in xs:
  for n,v in x.items():allnames.append(n);names(v.get('Children',[]))
names([root]);assert len(allnames)==len(set(allnames));print('controls',len(allnames),'details',{k:len(v) for k,v in sections.items()})
(OUT/'control-inventory.json').write_text(json.dumps({'before':657,'after':len(allnames),'retained':sorted(set(allnames)&set(nodes)),'removed':sorted(set(nodes)-set(allnames)),'added':sorted(set(allnames)-set(nodes))},ensure_ascii=False,indent=2))
