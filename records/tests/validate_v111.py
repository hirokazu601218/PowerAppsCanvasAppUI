"""Run: python tests/validate_v111.py. Local checks; Studio/PDF remain untested."""
from pathlib import Path
from copy import deepcopy
import json, re, hashlib
import preflight as pf
from fx_check import parse
from model_engine import ModelEngine

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'src/staff-master'
app=pf.read(SRC/'scrStaffMasterSearch_v1.11.paste.yaml'); nodes,parents=pf.index(app)
old,oldparents=pf.index(pf.read(SRC/'scrStaffMasterSearch_v1.08.paste.yaml'))
pf.allowed['Image@2.2.3']=pf.geo|pf.border|pf.pad|pf.radius|pf.S('Image ImagePosition AccessibleLabel TabIndex Fill Tooltip DisplayMode OnSelect')
pf.allowed['PDFViewer@2.5.0']=pf.geo|pf.border|pf.pad|pf.S('Document ShowControls Page Zoom Fill DisplayMode Tooltip OnSelect OnStateChange')
checks=[]
def check(name,value):
    assert value,name
    checks.append(name)
check('limited property/schema allowlist',pf.lint(app)==([],[]))
full=pf.read(SRC/'scrStaffMasterSearch_v1.11.pa.yaml')
check('screen and paste trees identical',full['Screens']['scrStaffMasterSearch_v111']['Children']==app)
check('no OnVisible initialization required','OnVisible' not in full['Screens']['scrStaffMasterSearch_v111']['Properties'])
check('PDF Viewer is a direct screen child',parents['pdfLedger111'] is None)
formulas=0
for n,c in nodes.items():
    for p,s in c['Properties'].items():
        try:parse(s)
        except Exception as exc:raise AssertionError((n,p,exc))
        formulas+=1
        if 'data:image/png;base64,' in s:continue
        clean=re.sub(r'"(?:""|[^"])*"','""',s)
        assert not re.search(r'\b(?:con|lbl|btn|gal|tmr|txt|dd|img|pdf|col|var|scr)[A-Za-z_0-9]*108[A-Za-z_0-9]*\b',clean),(n,p,'old ref')
        for ref in re.findall(r'\b(?:con|lbl|btn|gal|tmr|txt|dd|img|pdf)[A-Za-z_0-9]*111[A-Za-z_0-9]*\b',clean):
            assert ref in nodes,(n,p,ref)
check('every formula parsed and control reference resolved',True)
for n in old:
    if n.startswith(('lblBasicKey','lblBasicVal','lblCWork','lblCCommute','lblCSocial','lblCResident','lblCTax','lblCPayroll','lblLedger_')):
        nn=n.replace('108','111')
        assert nn in nodes,n
        assert nodes[nn]['Properties']['Text']==old[n]['Properties']['Text'].replace('108','111'),n
check('all baseline basic/history/payroll/69 ledger display fields retained',True)
for n,c in old.items():
    if c['Control'].startswith('Image'):
        assert nodes[n.replace('108','111')]['Properties']['Image']==c['Properties']['Image']
check('embedded ledger artwork byte-identical',True)
def fresh(w=1366,h=768):return ModelEngine(nodes,parents.copy(),w,h)
def act(e,n):return e.run(nodes[n]['Properties']['OnSelect'])
def prop(e,n,k='Text'):return e.prop(n,k)
def search(e,text='',org='すべて',status='すべて'):
    e.overrides['txtKeyword111','Text']=text
    e.overrides['ddOrg111','Selected']={'Value':org}
    e.overrides['ddStatus111','Selected']={'Value':status}
    act(e,'btnSearch111');return e.state['colResult111']
e=fresh()
check('initial variables/collections empty',e.state=={})
check('initial 25 records',prop(e,'lblListTitle111')=='職員一覧　25件')
check('initial 20 visible page records',len(prop(e,'galStaff111','Items'))==20)
check('initial selected employee',prop(e,'lblName111')=='山田 太郎' and prop(e,'lblBasicVal0111')=='00990000001')
check('initial paging',prop(e,'lblPage111')=='1 / 2' and prop(e,'btnPrev111','DisplayMode')=='DisplayMode.Disabled')
for section,count in [('Work',3),('Commute',1),('Social',1),('Resident',1),('Tax',1),('Payroll',1)]:
    check('initial history '+section,len(prop(e,'gal'+section+'111','Items'))==count)
act(e,'btnNext111')
check('next page 5 records',len(prop(e,'galStaff111','Items'))==5 and prop(e,'lblPage111')=='2 / 2')
check('last page next disabled',prop(e,'btnNext111','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnPrev111');check('previous page',len(prop(e,'galStaff111','Items'))==20)
check('blank search 25',len(search(e))==25)
check('name search 2',[r['Name'] for r in search(e,'山田')]==['山田 太郎','山田 花子'])
check('number search 1',[r['Name'] for r in search(e,'00990000003')]==['佐藤 一郎'])
check('selected employee follows search',prop(e,'lblName111')=='佐藤 一郎')
check('organisation search 9',len(search(e,org='01秘書課'))==9)
check('retired search 3',len(search(e,status='退職'))==3)
check('AND combination',[r['Name'] for r in search(e,'山田',org='02総務課',status='在籍')]==['山田 花子'])
check('no matches',search(e,'存在しない職員')==[])
check('zero results not replaced by initial fallback',prop(e,'conPerson111','Visible') is False and prop(e,'lblNoMatch111','Visible') is True)
check('zero results hide basic card and disable export',prop(e,'conBasic111','Visible') is False and prop(e,'btnExport111','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnClear111');check('clear restores all',prop(e,'lblListTitle111')=='職員一覧　25件' and prop(e,'txtKeyword111')=='')
row=prop(e,'galStaff111','Items')[1]
e.run(nodes['galStaff111']['Properties']['OnSelect'],{'ThisItem':row})
check('select staff member',prop(e,'lblName111')=='山田 花子')
check('histories join by selected id',all(r['StaffId']==row['StaffId'] for r in prop(e,'galWork111','Items')))
act(e,'btnCertificate111')
check('ledger opens',prop(e,'conLedgerModal111','Visible') is True)
check('ledger identity',prop(e,'lblLedger_employee_name111')=='山田 花子' and prop(e,'lblLedger_employee_number111')==row['StaffId'])
check('69 ledger fields',len(e.state['colLedgerFields111'])==69)
check('sample ledger total',prop(e,'lblLedger_monthly_amount_total111')=='10,480')
check('sidebar disabled under ledger',prop(e,'btnSidebarToggle111','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnSidebarToggle111');check('guarded toggle cannot change under modal','varSearchSidebarExpanded111' not in e.state)
act(e,'btnLedgerClose111');check('ledger closes and returns focus',prop(e,'pdfLedger111','Visible') is False and e.log[-1][0]=='SetFocus')
# Invalidate an intentionally stale PDF and modal after selecting a different employee.
for control in ['btnSearch111','btnClear111','galStaff111']:
    e.state.update(varLedgerPdf111='stale bytes',varLedgerPdfView111=True,varLedgerOpen111=True,varPayroll111=True,varReport111='stale')
    e.run(nodes[control]['Properties']['OnSelect'],{'ThisItem':row})
    check('stale output cleared by '+control,e.state['varLedgerPdf111'] is None and not e.state['varLedgerPdfView111'] and not e.state['varLedgerOpen111'] and not e.state['varPayroll111'] and e.state['varReport111']=='')
search(e,'00990000025')
check('no commute',prop(e,'galCommute111','Items')==[] and prop(e,'btnCertificate111','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnLoad111');act(e,'btnExport111')
check('export all 25 records, not just page',len(e.state['colReport111'])==25)
check('TSV 26 lines',len(e.state['varTsv111'].splitlines())==26)
check('copy view shows 5 printable rows',len(prop(e,'galReport111','Items'))==5)
act(e,'btnReportNext111');check('copy view next page',e.state['varReportPage111']==2 and len(prop(e,'galReport111','Items'))==5)
act(e,'btnReportClose111');check('copy view returns focus to origin',e.state['varReport111']=='' and e.log[-1]==('SetFocus',[('control','btnExport111')]))
e=fresh();act(e,'btnPayExport111');check('payroll export 15 fields',len(e.state['colReport111'])==15)

# Sidebar is manual and state-preserving. Never rename all controls after v1.11.
e=fresh();check('sidebar initial expanded',prop(e,'conSearchSidebar111','Width')==360 and prop(e,'conLeftScroll111','Visible') is True)
search(e);act(e,'btnNext111')
e.overrides['txtKeyword111','Text']='まだ確定していない入力'
before=deepcopy(e.state);input_before=deepcopy(e.overrides)
act(e,'btnSidebarToggle111')
check('collapsed 48px / inner controls hidden',prop(e,'conSearchSidebar111','Width')==48 and prop(e,'conLeftScroll111','Visible') is False)
check('search/page/selection/pending inputs retained on close',{k:v for k,v in e.state.items() if k!='varSearchSidebarExpanded111'}==before and e.overrides==input_before)
check('collapsed accessible name',prop(e,'btnSidebarToggle111','AccessibleLabel')=='職員検索を開く')
act(e,'btnSidebarToggle111');check('same page/selection on reopen',prop(e,'lblPage111')=='2 / 2' and prop(e,'lblName111')=='山田 太郎' and e.overrides==input_before)
check('only sidebar state modified by toggle',set(e.state)-set(before)=={'varSearchSidebarExpanded111'})
e=fresh();e.run(nodes['galStaff111']['Properties']['OnSelect'],{'ThisItem':row})
check('selection does not auto-collapse',prop(e,'conSearchSidebar111','Width')==360)
act(e,'btnTextSize111');check('large text mode increases body and rows',prop(e,'lblBasicVal0111','Size')==12 and prop(e,'galWork111','TemplateSize')==56)
check('modern controls used',nodes['btnSearch111']['Control']=='ModernButton@1.0.0' and nodes['txtKeyword111']['Control']=='ModernTextInput@1.0.0')
check('input commits output on keypress',prop(e,'txtKeyword111','TriggerOutput')=='TriggerOutput.Keypress')
e=fresh()
for item,label in zip(prop(e,'galWork111','Items'),['現行','過去','予定']):
    e.rows['galWork111']=item
    check('period state '+label,prop(e,'lblCWorkState111')==label)
e.rows.clear()

geometry=[]
for w,h in [(1366,768),(1920,1080)]:
    for expanded in [True,False]:
        for large in [False,True]:
            e=fresh(w,h);e.state.update(varSearchSidebarExpanded111=expanded,varLargeText111=large)
            rx,ry,rw,rh=e.rect('conRightScroll111');sx,sy,sw,sh=e.rect('conSearchSidebar111')
            assert rx==sx+sw+(16 if expanded else 0) and rx+rw==w-16
            assert ry+rh==h-16 and rh>400
            for name in ['conHeader111','conSearchSidebar111','conPerson111','conRightScroll111']:
                x,y,cw,ch=e.rect(name);assert x>=0 and y>=0 and cw>0 and ch>0 and x+cw<=w and y+ch<=h,(name,w,h)
            # Every basic field has room and never intersects its neighbour.
            rects=[]
            for i in range(9):
                k=e.rect(f'lblBasicKey{i}111');v=e.rect(f'lblBasicVal{i}111')
                assert k[1]+k[3]<=v[1] and v[0]+v[2]<=e.prop('conBasic111','Width')
                rects.extend([k,v])
            for i,a in enumerate(rects):
                for b in rects[i+1:]:assert min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])<0.01 or min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])<0.01
            previous='conBasic111'
            for s in ['Work','Commute','Social','Resident','Tax','Payroll']:
                n='conSection'+s+'111'
                assert e.prop(n,'Y')>=e.prop(previous,'Y')+e.prop(previous,'Height')+20
                assert e.prop('conHScroll'+s+'111','Height')>=e.prop('conSurface'+s+'111','Height')+20
                previous=n
                headers=[n for n in nodes if re.fullmatch('lblH'+s+'111[0-9]+',n)]
                for hn in headers:
                    cn=hn.replace('lblH','lblC',1)
                    assert e.prop(hn,'X')==e.prop(cn,'X') and e.prop(hn,'Width')==e.prop(cn,'Width') and e.prop(hn,'Width')>=128
            assert e.prop('lblPeriodLegend111','Y')>=e.prop(previous,'Y')+e.prop(previous,'Height')
            geometry.append({'width':w,'height':h,'expanded':expanded,'large':large,'sidebar_width':sw,'right_width':rw,'detail_viewport_height':rh})
check('8 layout combinations: bounds, spacing, fields, shared columns',len(geometry)==8)

# Negative controls demonstrate detection of previously reported failures.
bad=deepcopy(app);bn,_=pf.index(bad);bn['btnRow111']['Properties']['AccessibleLabel']='="bad"'
check('reject unknown Classic/Button AccessibleLabel',bool(pf.lint(bad)[0]))
bad=deepcopy(app);bn,_=pf.index(bad);viewer=next(x for x in bad if 'pdfLedger111' in x);bad.remove(viewer);bn['conStaffMaster111']['Children'].append(viewer)
check('reject PDF Viewer container nesting',pf.index(bad)[1]['pdfLedger111'] is not None)
try:parse('=Notify("test",NotificationType.Success)\nSet(varTest,true)')
except ValueError:check('reject missing behavior separator',True)
else:raise AssertionError('Missing separator accepted')
report={'version':'1.11','controls':len(nodes),'formulas_parsed':formulas,'checks_passed':len(checks),'passed_cases':checks,'geometry':geometry,
        'scope':'Local YAML allowlist, limited Power Fx evaluator and geometry model. Not Microsoft compiler or Studio renderer.',
        'studio_tested':False,'pdf_runtime_tested':False,'outputs':[]}
for path in [SRC/'scrStaffMasterSearch_v1.11.paste.yaml',SRC/'scrStaffMasterSearch_v1.11.pa.yaml']:
    report['outputs'].append({'name':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT/'docs/testing/v1.11-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['version','controls','formulas_parsed','checks_passed','studio_tested','pdf_runtime_tested']},ensure_ascii=False))
