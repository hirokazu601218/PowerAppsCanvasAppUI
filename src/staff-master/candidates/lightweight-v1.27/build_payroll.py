import copy, hashlib, json, re
from pathlib import Path
import yaml

ROOT=Path(__file__).parent
OUT=ROOT/'candidate'; OUT.mkdir(exist_ok=True)
source=yaml.safe_load((ROOT/'baseline/Screen1.pa.yaml').read_text())
nodes={}
def index(children):
    for item in children:
        for name,node in item.items():
            nodes[name]=node
            index(node.get('Children',[]))
index(source['Screens']['Screen1']['Children'])
fields=re.findall(r'\{Key:"([^"]+)",Value:(.*?)\}',nodes['btnPayExport111']['Properties']['OnSelect'])
assert len(fields)==163
metadata=[]
for i,(label,expr) in enumerate(fields,1):
    keys=set(re.findall(r'p\.(crb3c_\w+)',expr)); assert len(keys)==1
    metadata.append({'Order':i,'Key':keys.pop(),'Label':label,'Expression':expr})
(OUT/'payroll-fields.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')

def control(name,kind,props,children=None,variant=None):
    node={'Control':kind,'Properties':{k:'='+str(v) for k,v in props.items()}}
    if variant: node['Variant']=variant
    if children is not None: node['Children']=children
    return {name:node}
def label(name,text,x,y,w,h=48):
    return control(name,'Label@2.5.1',{'Text':text,'X':x,'Y':y,'Width':w,'Height':h,'Size':'If(Coalesce(varLargeText111,false),12,10.5)','Color':'ColorValue("#242424")','Fill':'ColorValue("#FFFFFF")','BorderColor':'ColorValue("#CBD5E1")','BorderThickness':1,'PaddingLeft':8,'Tooltip':'Self.Text','Wrap':'true'})
def group(name,props,children,auto=False):
    return control(name,'GroupContainer@1.5.0',dict(DropShadow='DropShadow.None',Fill='ColorValue("#FFFFFF")',**props),children,'AutoLayout' if auto else 'ManualLayout')

# Preserve one row for every source GUID. Never group or deduplicate by month.
# Japanese era dates are matched completely and round-tripped to reject rollover.
parse='''With({m:Match(Trim(Coalesce(p.crb3c_payment_date,"")),"(?<Era>令和|平成|昭和|R|H|S)(?<EraYear>元|[0-9]{1,2})[年./-](?<M>[0-9]{1,2})[月./-](?<D>[0-9]{1,2})日?",MatchOptions.Complete)},
 If(IsBlank(m.FullMatch),Blank(),With({y:Switch(m.Era,"令和",2018,"R",2018,"平成",1988,"H",1988,"昭和",1925,"S",1925)+If(m.EraYear="元",1,Value(m.EraYear)),mo:Value(m.M),dy:Value(m.D)},
 With({dt:Date(y,mo,dy)},If(Year(dt)=y && Month(dt)=mo && Day(dt)=dy && Value(Substitute(m.EraYear,"元","1"))>0 && Switch(m.Era,"令和",dt>=Date(2019,5,1),"R",dt>=Date(2019,5,1),"平成",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"H",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"昭和",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),"S",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),false),dt,Blank())))))'''
build='''Clear(colPayrollColumns111); Clear(colPayrollExceptions111);
ForAll(colPayrollSource111 As p,With({dt:IfError('''+parse+''',Blank())},
 If(IsBlank(dt),Collect(colPayrollExceptions111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentText:p.crb3c_payment_date}),
 dt>=varPayrollStart111 && dt<DateAdd(varPayrollEnd111,1,TimeUnit.Months),
 Collect(colPayrollColumns111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentDate:dt,Sequence:p.crb3c_sequence,Record:p}))));'''
fetch='''Clear(colPayrollSource111); Clear(colPayrollColumns111); Clear(colPayrollExceptions111); Set(varPayrollFetched111,Blank());
If(!IsBlank(StaffSelected.StaffId),IfError(
 ClearCollect(colPayrollSource111,Filter('T_基準給与簿_STUDIO',crb3c_staffnumber=StaffSelected.StaffId));
 '''+build+'''
 Set(varPayrollFetched111,Now()),
 Clear(colPayrollSource111); Clear(colPayrollColumns111); Clear(colPayrollExceptions111); Notify("給与データを取得できませんでした。",NotificationType.Error)));'''
initialize='''Set(varPayrollStart111,Coalesce(varPayrollStart111,Date(Year(Today()),1,1)));
Set(varPayrollEnd111,Coalesce(varPayrollEnd111,Date(Year(Today()),12,1)));
'''+fetch
(OUT/'payroll-refresh.fx').write_text(initialize)
change='''If(IsBlank(dpPayrollStart111.SelectedDate)||IsBlank(dpPayrollEnd111.SelectedDate),Notify("表示開始月と終了月を選択してください。",NotificationType.Error),
With({startMonth:Date(Year(dpPayrollStart111.SelectedDate),Month(dpPayrollStart111.SelectedDate),1),endMonth:Date(Year(dpPayrollEnd111.SelectedDate),Month(dpPayrollEnd111.SelectedDate),1)},
If(startMonth>endMonth,Notify("表示開始月は終了月以前を選択してください。",NotificationType.Error),
Set(varPayrollStart111,startMonth); Set(varPayrollEnd111,endMonth); '''+fetch+''')));'''
children=[label('lblPayrollRange111','"基準給与簿：表示開始月 ～ 表示終了月"',0,0,'Parent.Width',40)]
for name,var,x in [('dpPayrollStart111','varPayrollStart111',0),('dpPayrollEnd111','varPayrollEnd111',220)]:
    children.append(control(name,'Classic/DatePicker@2.6.0',{'DefaultDate':var,'Format':'"yyyy/mm"','Language':'"ja-JP"','StartYear':1900,'EndYear':9999,'X':x,'Y':44,'Width':200,'Height':44,'OnChange':change,'AccessibleLabel':'"'+('表示開始月' if x==0 else '表示終了月')+'"'}))
children.append(label('lblPayrollState111','If(IsEmpty(colPayrollColumns111),"選択範囲に登録済み給与はありません",Text(CountRows(colPayrollColumns111)) & " レコード") & If(IsEmpty(colPayrollExceptions111),"",Char(10) & "支給日を確認してください：" & Concat(colPayrollExceptions111,RecordId & " [" & Coalesce(PaymentText,"空欄") & "]",Char(10)))',0,96,'Parent.Width','Max(48,24*(1+CountRows(colPayrollExceptions111)))'))
rows='Table('+','.join('{Order:'+str(f['Order'])+',Key:"'+f['Key']+'",Label:'+json.dumps(f['Label'],ensure_ascii=False)+'}' for f in metadata)+')'
switch='With({p:ThisItem.Record},Switch(row.Key,'+','.join('"'+f['Key']+'",'+f['Expression'] for f in metadata)+',Blank()))'
columns='SortByColumns(colPayrollColumns111,"PaymentDate",SortOrder.Ascending,"Sequence",SortOrder.Ascending,"RecordId",SortOrder.Ascending)'
cells=control('galPayrollCells111','Gallery@2.15.0',{'Items':columns,'X':260,'Width':'Max(1,CountRows(colPayrollColumns111))*220','Height':'Parent.TemplateHeight','TemplateSize':220,'TemplatePadding':0,'ShowScrollbar':'false','Selectable':'false'},[label('lblPayrollCell111',switch,0,0,220,'Parent.TemplateHeight')],'BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0')
rowgallery=control('galPayrollRows111','Gallery@2.15.0',{'Items':rows+' As row','X':0,'Y':80,'Width':'Parent.Width','Height':'Parent.Height-Self.Y','TemplateSize':'If(Coalesce(varLargeText111,false),88,72)','TemplatePadding':0,'Selectable':'false','ShowScrollbar':'true'},[label('lblPayrollField111','row.Label',0,0,260,'Parent.TemplateHeight'),cells],'BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0')
heads=control('galPayrollHeads111','Gallery@2.15.0',{'Items':columns,'X':260,'Y':0,'Width':'Max(1,CountRows(colPayrollColumns111))*220','Height':80,'TemplateSize':220,'TemplatePadding':0,'ShowScrollbar':'false','Selectable':'false'},[label('lblPayrollHead111','Text(ThisItem.PaymentDate,"yyyy/mm/dd") & " / " & Text(ThisItem.Sequence) & Char(10) & ThisItem.RecordId',0,0,220,80)],'BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0')
surface=group('conPayrollGrid111',{'Width':'260+Max(1,CountRows(colPayrollColumns111))*220','Height':'Parent.Height-24','LayoutMinWidth':'Self.Width','LayoutMinHeight':'Self.Height','FillPortions':0,'AlignInContainer':'AlignInContainer.Start'},[label('lblPayrollFieldHead111','"項目（163項目）"',0,0,260,80),heads,rowgallery])
children.append(group('conPayrollScroll111',{'X':0,'Y':'lblPayrollState111.Y+lblPayrollState111.Height+8','Width':'Parent.Width','Height':'Parent.Height-Self.Y','LayoutDirection':'LayoutDirection.Horizontal','LayoutOverflowX':'LayoutOverflow.Scroll','PaddingBottom':24},[surface],True))
root=group('conPayrollLight111',{'X':0,'Y':0,'Width':'Parent.Width','Height':'Parent.Height'},children)
class Dumper(yaml.SafeDumper): pass
def string(d,s):
    return d.represent_scalar('tag:yaml.org,2002:str',s,style='|' if '\n' in s else None)
Dumper.add_representer(str,string)
(OUT/'conPayrollLight111.paste.yaml').write_text(yaml.dump([root],Dumper=Dumper,allow_unicode=True,sort_keys=False,width=100000))
print('163 fields retained; standalone payroll component generated')
