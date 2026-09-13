"""One-time, deterministic v1.08 -> v1.11 migration. Do not reuse for v1.12+.

Keeps embedded sample records and ledger artwork; changes layout and interaction.
YAML is serialized from a tree, not indentation/string surgery.
"""
from pathlib import Path
from copy import deepcopy
import re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from preflight import read, index

SOURCE = ROOT / 'src/staff-master'
baseline = read(SOURCE / 'scrStaffMasterSearch_v1.08.paste.yaml')
def rename(text):
    return re.sub(r'\b(?:con|lbl|btn|gal|tmr|txt|dd|img|pdf|col|var|scr)[A-Za-z_0-9]*',
                  lambda m: m[0].replace('108', '111'), text)
def migrate(v):
    if isinstance(v, dict): return {rename(k): migrate(x) for k, x in v.items()}
    if isinstance(v, list): return [migrate(x) for x in v]
    if isinstance(v, str):
        return v if 'data:image/png;base64,' in v else rename(v).replace('v1.08', 'v1.11')
    return v
app = migrate(deepcopy(baseline))
nodes, parents = index(app)
def put(name, **values):
    for k, v in values.items(): nodes[name]['Properties'][k] = '=' + str(v)
def move(name, parent):
    old = parents[name]
    children = nodes[old]['Children'] if old else app
    obj = next(x for x in children if name in x)
    children.remove(obj)
    nodes[parent].setdefault('Children', []).append(obj)
    parents[name] = parent
def add(name, control, parent, **values):
    obj = {'Control': control, 'Properties': {k: '=' + str(v) for k, v in values.items()}}
    nodes[name] = obj; parents[name] = parent
    nodes[parent].setdefault('Children', []).append({name: obj})
    return obj
def descend(n, ancestor):
    while n:
        if n == ancestor: return True
        n = parents[n]
    return False

LARGE = 'Coalesce(varLargeText111,false)'
OPEN = 'Coalesce(varSearchSidebarExpanded111,true)'
MODAL = 'Coalesce(varLedgerOpen111,false) || Coalesce(varPayroll111,false) || !IsBlank(varReport111)'
BODY = f'If({LARGE},12,10.5)'  # Size is points: approx 16/14 CSS px at 100%.
SECTION = f'If({LARGE},13.5,12)'
TITLE = f'If({LARGE},18,15)'
ROW = f'If({LARGE},56,48)'
FONT = '"Segoe UI"'
WHITE = 'ColorValue("#FFFFFF")'
TEXT = 'ColorValue("#242424")'
BRAND = 'ColorValue("#0F6CBD")'

# Keep the official two-page ledger at its existing scale. Do not enlarge form cells.
for n, c in list(nodes.items()):
    p = c['Properties']
    ledger_cell = descend(n, 'conLedgerPages111')
    if 'Font' in p and not ledger_cell: put(n, Font=FONT)
    if c['Control'] == 'Label@2.5.1' and not ledger_cell:
        put(n, Size=BODY, FontWeight='FontWeight.Normal', LineHeight='1.4',
            TabIndex='-1', PaddingTop='4', PaddingBottom='4')
        if p.get('Color') not in ['=Color.White', '=ColorValue("#FFFFFF")']:
            put(n, Color=TEXT)
    if c['Control'] == 'Classic/Button@2.2.0' and n != 'btnRow111':
        # Microsoft Learn: ModernButton@1.0.0. Classic state props are not portable.
        keep = set('X Y Width Height Visible Text OnSelect DisplayMode Tooltip Font Size FontWeight Color BorderColor BorderThickness PaddingLeft PaddingRight PaddingTop PaddingBottom RadiusTopLeft RadiusTopRight RadiusBottomLeft RadiusBottomRight'.split())
        c['Properties'] = {k: v for k, v in p.items() if k in keep}
        c['Control'] = 'ModernButton@1.0.0'
        put(n, Size=BODY, FontWeight='FontWeight.Semibold', BasePaletteColor=BRAND,
            Appearance='ButtonAppearance.Outline', Color=BRAND,
            AccessibleLabel=c['Properties']['Text'][1:], Height='44',
            RadiusTopLeft='4', RadiusTopRight='4', RadiusBottomLeft='4', RadiusBottomRight='4')

# New modern text input uses Default for input and Text for output (2026 contract).
keyword = nodes['txtKeyword111']
old = keyword['Properties']
keep = set('X Y Width Height Default OnChange OnSelect DisplayMode AccessibleLabel Font Size FontWeight Color BorderColor BorderThickness PaddingLeft PaddingRight PaddingTop PaddingBottom'.split())
keyword['Properties'] = {k: v for k, v in old.items() if k in keep}
keyword['Control'] = 'ModernTextInput@1.0.0'
put('txtKeyword111', Placeholder='"氏名・職員番号・項目を検索"',
    Type='TextInputType.Search', TriggerOutput='TriggerOutput.Keypress',
    Appearance='Appearance.Outline', BasePaletteColor=BRAND, Font=FONT,
    Size=BODY, Fill=WHITE, Color=TEXT, AccessibleLabel='"氏名・職員番号・項目を検索"')

put('conMain111', Width='Parent.Width', Fill='ColorValue("#F7F9FC")')
put('conHeader111', Height='64')
put('lblApp111', X='16', Y='0', Width='350', Height='64', Size=TITLE, FontWeight='FontWeight.Semibold')
put('lblMeta111', X='Parent.Width-686', Width='174', Y='0', Height='64', Size='9', Text='"v1.11  ／  B案・架空25名"')
put('btnLoad111', X='Parent.Width-354', Y='10', Width='150', Height='44', Color=WHITE, BorderColor=WHITE)
put('btnExport111', X='Parent.Width-194', Y='10', Width='178', Height='44',
    Text='"検索結果を出力"', AccessibleLabel='"検索結果をTSVで出力"', Color=WHITE, BorderColor=WHITE,
    DisplayMode='If(Coalesce(varResultsReady111,false) && IsEmpty(colResult111),DisplayMode.Disabled,DisplayMode.Edit)')
add('btnTextSize111', 'ModernButton@1.0.0', 'conHeader111',
    X='Parent.Width-502', Y='10', Width='138', Height='44',
    Text=f'If({LARGE},"文字：大","文字：標準")',
    OnSelect=f'Set(varLargeText111,!{LARGE})',
    Size=BODY, Font=FONT, FontWeight='FontWeight.Semibold',
    Appearance='ButtonAppearance.Outline', BasePaletteColor=BRAND,
    Color=WHITE, BorderColor=WHITE,
    AccessibleLabel=f'If({LARGE},"文字サイズを標準に戻す","文字サイズを大きくする")',
    Tooltip='Self.AccessibleLabel')
put('lblTestNote111', X='16', Y='72', Width='Parent.Width-32', Height='48',
    Text='"サンドボックス：架空25名。検索して職員を選択後、左上のボタンで検索欄を閉じられます。実データは保存されません。"',
    Size=SECTION, FontWeight='FontWeight.Normal', PaddingLeft='12', PaddingRight='12',
    Fill='ColorValue("#EDF2F7")', Color=TEXT)

sidebar = add('conSearchSidebar111', 'GroupContainer@1.5.0', 'conMain111',
    X='16', Y='128', Width=f'If({OPEN},360,48)', Height='Parent.Height-Self.Y-16',
    Fill=WHITE, DropShadow='DropShadow.None', BorderThickness='1',
    BorderColor='ColorValue("#CBD5E1")', RadiusTopLeft='4', RadiusTopRight='4', RadiusBottomLeft='4', RadiusBottomRight='4')
sidebar['Variant'] = 'ManualLayout'
move('conLeftScroll111', 'conSearchSidebar111')
add('lblSidebarTitle111', 'Label@2.5.1', 'conSearchSidebar111',
    X='12', Y='4', Width='Parent.Width-68', Height='44', Text='"職員検索"',
    Visible=OPEN, Font=FONT, Size=SECTION, FontWeight='FontWeight.Semibold',
    Color=TEXT, PaddingLeft='0', PaddingRight='0', PaddingTop='4', PaddingBottom='4', TabIndex='-1')
# One persistent button outside the hidden content keeps focus through both states.
add('btnSidebarToggle111', 'ModernButton@1.0.0', 'conSearchSidebar111',
    X=f'If({OPEN},Parent.Width-48,2)', Y='4', Width='44', Height='44',
    Text=f'If({OPEN},"‹","›")', Size='18', Font=FONT,
    FontWeight='FontWeight.Semibold', Appearance='ButtonAppearance.Outline',
    BasePaletteColor=BRAND, Color=BRAND,
    OnSelect=f'If(!({MODAL}),Set(varSearchSidebarExpanded111,!{OPEN}))',
    DisplayMode=f'If({MODAL},DisplayMode.Disabled,DisplayMode.Edit)',
    AccessibleLabel=f'If({OPEN},"職員検索を閉じる","職員検索を開く")',
    Tooltip='Self.AccessibleLabel')
put('conLeftScroll111', X='1', Y='56', Width='Parent.Width-2',
    Height='Parent.Height-57', Visible=OPEN,
    PaddingLeft='12', PaddingRight='28', PaddingTop='0', PaddingBottom='12')
put('conLeftSurface111', Width='Parent.Width-40', Height='galStaff111.Y+galStaff111.Height+12',
    LayoutMinWidth='Self.Width', LayoutMinHeight='Self.Height', FillPortions='0')
put('lblSearchTitle111', X='0', Y='0', Width='Parent.Width', Height='32',
    Text='"氏名・番号で検索できます"', Size=BODY)
put('lblKeyword111', X='0', Y='36', Width='Parent.Width', Height='24')
put('txtKeyword111', X='0', Y='64', Width='Parent.Width', Height='44')
put('lblOrg111', X='0', Y='116', Width='Parent.Width', Height='24')
put('ddOrg111', X='0', Y='144', Width='Parent.Width', Height='44', Size=BODY)
put('lblStatus111', X='0', Y='196', Width='Parent.Width', Height='24')
put('ddStatus111', X='0', Y='224', Width='Parent.Width', Height='44', Size=BODY)
put('btnSearch111', X='0', Y='280', Width='112', Height='44',
    Appearance='ButtonAppearance.Primary', Color=WHITE)
put('btnClear111', X='124', Y='280', Width='Parent.Width-124', Height='44')
put('lblListTitle111', X='0', Y='340', Width='Parent.Width', Height='40', Size=SECTION, FontWeight='FontWeight.Semibold', Live='Live.Polite')
put('btnPrev111', X='0', Y='388', Width='72', Height='44')
put('lblPage111', X='80', Y='388', Width='Parent.Width-160', Height='44')
put('btnNext111', X='Parent.Width-72', Y='388', Width='72', Height='44')
# Compact the filter block without reducing input hit targets: organisation/status share a row.
put('lblSearchTitle111', Text='"氏名・職員番号・項目"', Y='0', Height='24')
put('lblKeyword111', Visible='false')
put('txtKeyword111', Y='28')
put('lblOrg111', X='0', Y='84', Width='(Parent.Width-12)/2')
put('lblStatus111', X='(Parent.Width+12)/2', Y='84', Width='(Parent.Width-12)/2')
put('ddOrg111', X='0', Y='112', Width='(Parent.Width-12)/2')
put('ddStatus111', X='(Parent.Width+12)/2', Y='112', Width='(Parent.Width-12)/2')
put('btnSearch111', Y='168')
put('btnClear111', Y='168')
put('lblListTitle111', Y='228')
put('btnPrev111', Y='276')
put('lblPage111', Y='276')
put('btnNext111', Y='276')
for name in ['lblSearchTitle111','lblOrg111','lblStatus111']:
    put(name,PaddingTop='0',PaddingBottom='0',Fill=WHITE)
# Remove only obsolete column heading controls; all four row fields are retained.
for i in range(4):
    name=f'lblListH{i}111'; par=parents.pop(name)
    nodes[par]['Children']=[x for x in nodes[par]['Children'] if name not in x]
    nodes.pop(name)
put('galStaff111', X='0', Y='332', Width='Parent.Width',
    Height=f'Min(20,Max(1,CountRows(Self.Items)))*If({LARGE},80,72)',
    TemplateSize=f'If({LARGE},80,72)', ShowScrollbar='false',
    AccessibleLabel='"職員検索結果。氏名、在籍状態、職員番号、所属の順"',
    ItemAccessibleLabel='ThisItem.Name & "、" & ThisItem.Status & "、職員番号" & ThisItem.StaffId & "、" & ThisItem.Org')
for i in range(4):
    put(f'lblListC{i}111', BorderThickness='0', PaddingLeft='8', PaddingRight='4', Color=TEXT,
        PaddingTop='2',PaddingBottom='2',Size=BODY, Fill='If(ThisItem.StaffId=galStaff111.Selected.StaffId,ColorValue("#DCEAFF"),Color.White)')
put('lblListC1111', X='4', Y='4', Width='Parent.TemplateWidth-84', Height='28', FontWeight='FontWeight.Semibold')
put('lblListC3111', X='Parent.TemplateWidth-80', Y='4', Width='80', Height='28', Align='Align.Right')
put('lblListC0111', X='4', Y='36', Width='132', Height='28')
put('lblListC2111', X='136', Y='36', Width='Parent.TemplateWidth-136', Height='28')
put('btnRow111', Width='Parent.TemplateWidth', Height='Parent.TemplateHeight', Size=BODY)
marker=add('lblSelectedMarker111','Label@2.5.1','galStaff111',
    X='0',Y='0',Width='4',Height='Parent.TemplateHeight',Text='""',
    Fill='If(ThisItem.StaffId=galStaff111.Selected.StaffId,ColorValue("#0F6CBD"),Color.Transparent)',
    TabIndex='-1',OnSelect='Select(Parent)')
put('lblNoMatch111', X='0', Y='332', Width='Parent.Width', Height='88', Size=SECTION)

# Fixed summary, independently scrollable detail. Do not keep the collapsed 360px gap.
move('conPerson111', 'conMain111')
DETAIL_X = f'conSearchSidebar111.X+conSearchSidebar111.Width+If({OPEN},16,0)'
put('conPerson111', X=DETAIL_X, Y='128', Width='Parent.Width-Self.X-16', Height=f'If({LARGE},104,96)')
put('lblName111', X='16', Y='8', Width='Parent.Width-120', Height='44', Size=TITLE, FontWeight='FontWeight.Semibold')
put('lblPersonSub111', X='16', Y='52', Width='Parent.Width-32', Height='36', Size=BODY)
put('lblBadge111', X='Parent.Width-96', Y='16', Width='80', Height='32', Size=BODY)
put('conRightScroll111', X=DETAIL_X, Y='conPerson111.Y+conPerson111.Height+12',
    Width='Parent.Width-Self.X-16', Height='Parent.Height-Self.Y-16',
    PaddingLeft='0', PaddingRight='20', PaddingTop='0', PaddingBottom='16')
put('conRightSurface111', Width='Parent.Width-20', Height='conSectionPayroll111.Y+conSectionPayroll111.Height+16',
    LayoutMinWidth='Self.Width', LayoutMinHeight='Self.Height', FillPortions='0')
put('conBasic111', X='0', Y='0', Width='Parent.Width-2', Height=f'52+3*If({LARGE},72,64)',Visible='conPerson111.Visible')
put('lblBasicTitle111', Width='Parent.Width', Height='52', Size=SECTION, FontWeight='FontWeight.Semibold')
for i in range(9):
    column, row = i%3, i//3
    pos=f'8+(Parent.Width-16)/3*{column}'
    y=f'52+{row}*If({LARGE},72,64)'
    put(f'lblBasicKey{i}111', X=pos, Y=y, Width='(Parent.Width-16)/3', Height=f'If({LARGE},32,28)',
        Size=BODY, FontWeight='FontWeight.Semibold', BorderThickness='0', PaddingLeft='12', PaddingRight='12', Fill=WHITE)
    put(f'lblBasicVal{i}111', X=pos, Y=y+f'+If({LARGE},32,28)', Width='(Parent.Width-16)/3',
        Height=f'If({LARGE},40,36)', Size=BODY, BorderThickness='0', PaddingLeft='12', PaddingRight='12', Fill=WHITE)

# A table has one shared column geometry for its header and every data row.
previous='conBasic111'
for section in ['Work','Commute','Social','Resident','Tax','Payroll','PayrollModal']:
    surface=f'conSurface{section}111'; scroll=f'conHScroll{section}111'; gallery=f'gal{section}111'
    headers=[n for n in nodes if re.fullmatch(f'lblH{section}111[0-9]+',n)]
    headers.sort(key=lambda n:int(n.split('111')[-1]))
    x='112' if section=='Work' else '0'
    headheight=f'If({LARGE},72,64)' if section.startswith('Payroll') else f'If({LARGE},64,56)'
    for header in headers:
        i=header.split('111')[-1]; cell=f'lblC{section}111{i}'
        oldwidth=int(float(nodes[header]['Properties']['Width'][1:]))
        width=max(oldwidth,128)
        # Allow up to 3 lines for long payroll headings, never shrink Japanese text.
        if section.startswith('Payroll') and width==145:width=192
        widthexpr=f'If({LARGE},{round(width*1.16)},{width})'
        put(header,X=x,Y='0',Width=widthexpr,Height=headheight,Size=BODY,
            FontWeight='FontWeight.Semibold',PaddingLeft='12',PaddingRight='12',
            Color=TEXT,Fill='ColorValue("#EDF2F7")',BorderThickness='1')
        put(cell,X=f'{header}.X',Y='0',Width=f'{header}.Width',Height=ROW,
            Size=BODY,PaddingLeft='12',PaddingRight='12',FontWeight='FontWeight.Normal',
            Fill=WHITE,Color=TEXT,BorderThickness='1')
        x=f'{header}.X+{header}.Width'
    # Work dates previously communicated only by green/grey fill; add text status.
    if section=='Work':
        h='lblHWorkState111'
        c='lblCWorkState111'
        add(h,'Label@2.5.1',surface,**{k:v[1:] for k,v in nodes[headers[0]]['Properties'].items()})
        put(h,X='0',Width='112',Text='"適用状態"')
        add(c,'Label@2.5.1',gallery,**{k:v[1:] for k,v in nodes[f'lblCWork1110']['Properties'].items()})
        put(c,X=f'{h}.X',Width=f'{h}.Width',Text='If(ThisItem.End<Date(2026,9,11),"過去",If(ThisItem.Start>Date(2026,9,11),"予定","現行"))')
    put(surface,Width=x,Height=f'{headheight}+Max(1,Min(4,CountRows({gallery}.Items)))*({ROW})',
        LayoutMinWidth='Self.Width',LayoutMinHeight='Self.Height',FillPortions='0')
    put(scroll,X='1',Y='52',Width='Parent.Width-2',Height=f'{surface}.Height+20',
        PaddingLeft='0',PaddingRight='0',PaddingTop='0',PaddingBottom='20')
    put(gallery,X='0',Y=headheight,Width='Parent.Width',Height='Parent.Height-Self.Y',
        TemplateSize=ROW,TemplatePadding='0',ShowScrollbar='false',Selectable='false',
        AccessibleLabel='"'+section+' 履歴"')
    if section!='PayrollModal':
        container=f'conSection{section}111'
        put(container,X='0',Y=f'{previous}.Y+{previous}.Height+20',Width='Parent.Width-2',Height=f'52+{scroll}.Height+2')
        put(f'lblSection{section}111',Height='52',Size=SECTION,FontWeight='FontWeight.Semibold',
            Width='Parent.Width-160' if section in ['Commute','Payroll'] else 'Parent.Width')
        put(f'lblEmpty{section}111',X='1',Y='108',Width='Parent.Width-2',Height=ROW)
        previous=container
for n in ['btnCertificate111','btnPayrollOpen111']:
    put(n,X='Parent.Width-152',Y='4',Width='144',Height='44')
put('btnCertificate111',Text='"認定簿を表示"',AccessibleLabel='"選択職員の認定簿を表示"')
put('lblPeriodLegend111',Y='conSectionPayroll111.Y+conSectionPayroll111.Height+12',Height='48',
    Text='"適用状態の判定基準日：2026/09/11（テスト固定）。給与・勤務条件の表で現行・過去・予定を文字表示します。"',Size=BODY)
put('conRightSurface111',Height='lblPeriodLegend111.Y+lblPeriodLegend111.Height+16',LayoutMinHeight='Self.Height')

# Ensure previous employee data/PDF cannot leak after a new search or selection.
clear_old='; Set(varReport111,""); Set(varPayroll111,false); Set(varLedgerOpen111,false); Set(varLedgerPdfView111,false); Set(varLedgerPdfRequested111,false); Set(varLedgerExport111,false); Set(varLedgerPdf111,Blank()); Set(varLedgerSavedUrl111,"")'
for n in ['btnSearch111','btnClear111','btnLoad111','galStaff111']:
    nodes[n]['Properties']['OnSelect']+=clear_old

# Modal ergonomics. The generated PDF viewer remains a top-level Screen child.
put('lblPayrollModalTitle111',Height='64',Width='Parent.Width-348',Size=SECTION,FontWeight='FontWeight.Semibold')
put('btnPayExport111',X='Parent.Width-336',Y='10',Width='224',Height='44',Text='"給与項目を出力"',AccessibleLabel='"給与項目をTSVで出力"')
put('btnPayClose111',X='Parent.Width-104',Y='10',Width='96',Height='44')
put('conHScrollPayrollModal111',Y='76')
put('lblPayrollCaution111',Y='conHScrollPayrollModal111.Y+conHScrollPayrollModal111.Height+16',Height='64',Size=SECTION)
put('lblLedgerTitle111',Size=TITLE)
put('lblLedgerStaff111',Size=BODY)
for n in ['btnLedgerClose111','btnLedgerFit111','btnLedgerZoom111','btnLedgerPdf111','btnLedgerSaved111']:
    put(n,Height='44')
put('conLedgerToolbar111',Height='108')
put('conLedgerScroll111',Y='188',Height='Parent.Height-200')
put('lblLedgerStatus111',Y='58',Height='44',Size=BODY)
put('btnLedgerFit111',Width='144',X='12')
put('btnLedgerZoom111',Width='144',X='164')
put('lblLedgerPaper111',X='324',Width='64',Height='44')
put('ddLedgerPaper111',X='392',Width='88',Height='44',Size=BODY)
put('btnLedgerPdf111',X='496',Width='136')
put('btnLedgerSaved111',X='644',Width='200')

# Keep export viewport above the manual-copy box at both supported screen heights.
put('lblReportTitle111',Y='8',Size=TITLE,Height='40')
put('lblReportPerson111',Y='52',Height='28')
put('lblReportDisclaimer111',Y='84',Size=SECTION,Height='44')
for n in ['btnCopy111','btnPrint111','btnReportPrev111','btnReportNext111','btnReportClose111']:
    put(n,Y='136',Height='44')
put('galReport111',Y='236',Height=f'Max(44,Parent.Height-440)',TemplateSize='44')
for n in ['lblReportKey111','lblReportValue111']:
    if n in nodes:put(n,Y='188',Height='44',Size=BODY)
for n,c in nodes.items():
    if parents[n]=='galReport111':put(n,Height='44',Size=BODY)
for name,property in [('galReport111','Items'),('btnReportNext111','DisplayMode'),('lblReportPage111','Text')]:
    nodes[name]['Properties'][property]=re.sub(r'\b12\b','5',nodes[name]['Properties'][property])
put('galReport111',TemplateSize='64')
for n,c in nodes.items():
    if parents[n]=='galReport111':put(n,Height='64',Size=BODY)
put('txtManualCopy111',Y='Parent.Height-124',Height='108',Size=BODY)
if 'lblReportPage111' in nodes:put('lblReportPage111',Y='galReport111.Y+galReport111.Height+8',Height='28')
for name in ['btnExport111','btnPayExport111']:
    nodes[name]['Properties']['OnSelect']+='; SetFocus(btnReportClose111)'
nodes['btnPayrollOpen111']['Properties']['OnSelect']+='; SetFocus(btnPayClose111)'
nodes['btnPayClose111']['Properties']['OnSelect']+='; SetFocus(btnPayrollOpen111)'
put('btnReportClose111',OnSelect='With({returnToPayroll:StartsWith(Coalesce(varReport111,""),"基準給与簿")},Set(varReport111,"");If(returnToPayroll,SetFocus(btnPayrollOpen111),SetFocus(btnExport111)))')

for n,c in nodes.items():
    if descend(n,'conMain111') and c['Control'] in ['ModernButton@1.0.0','ModernTextInput@1.0.0','Classic/Button@2.2.0','Classic/DropDown@2.3.1','Gallery@2.15.0']:
        current=c['Properties'].get('DisplayMode','=DisplayMode.Edit')[1:]
        put(n,DisplayMode=f'If({MODAL},DisplayMode.Disabled,{current})')
        if c['Control'].startswith('Classic/'):
            put(n,TabIndex=f'If({MODAL},-1,0)')

class Dumper(yaml.SafeDumper):
    def ignore_aliases(self,data):return True
    def increase_indent(self,flow=False,indentless=False):return super().increase_indent(flow,False)
def scalar(dumper,s):
    return dumper.represent_scalar('tag:yaml.org,2002:str',s,style='|' if '\n' in s else None)
Dumper.add_representer(str,scalar)
def dump(data,path):
    path.write_text(yaml.dump(data,Dumper=Dumper,allow_unicode=True,sort_keys=False,width=2000000),encoding='utf-8')
dump(app,SOURCE/'scrStaffMasterSearch_v1.11.paste.yaml')
dump({'Screens':{'scrStaffMasterSearch_v111':{'Properties':{'Fill':'=ColorValue("#F7F9FC")'},'Children':app}}},SOURCE/'scrStaffMasterSearch_v1.11.pa.yaml')
fx=(SOURCE/'CommuteLedger_v1.08_SavePDF_OnTimerEnd.fx').read_text()
(SOURCE/'CommuteLedger_v1.11_SavePDF_OnTimerEnd.fx').write_text(rename(fx).replace('v1.08','v1.11'),encoding='utf-8')
print('Built v1.11:',len(index(app)[0]),'controls')
