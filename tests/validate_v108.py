from pathlib import Path
from copy import deepcopy
import json,re,hashlib
from fx_check import parse,Engine
R=Path(__file__).resolve().parents[1];S=R/'src/staff-master';W=R/'docs/testing'
import preflight
ns=vars(preflight)
read,index,lint=ns['read'],ns['index'],ns['lint'];SS=ns['S']
ns['allowed']['Image@2.2.3']=ns['geo']|ns['border']|ns['pad']|ns['radius']|SS('Image ImagePosition AccessibleLabel TabIndex Fill Tooltip DisplayMode OnSelect')
ns['allowed']['PDFViewer@2.5.0']=ns['geo']|ns['border']|ns['pad']|SS('Document ShowControls Page Zoom Fill DisplayMode Tooltip OnSelect OnStateChange')
app=read(S/'scrStaffMasterSearch_v1.08.paste.yaml');nodes,parents=index(app)
assert lint(app)==([],[])
assert parents['pdfLedger108'] is None
assert not any('tmrInitialize' in n for n in nodes)
full=read(S/'scrStaffMasterSearch_v1.08.pa.yaml')
assert full['Screens']['scrStaffMasterSearch_v108']['Children']==app
assert 'OnVisible' not in full['Screens']['scrStaffMasterSearch_v108']['Properties']
total=0
for n,c in nodes.items():
 for p,s in c['Properties'].items():
  try:parse(s)
  except Exception as err:raise AssertionError((n,p,str(err)))
  clean=re.sub(r'"(?:""|[^"])*"','""',s)
  assert not re.search(r'\b(?:colStaff|colWork|colCommute|colSocial|colResident|colTax|colPayroll)108\b',clean),(n,p)
  for ref in re.findall(r'\b(?:con|lbl|btn|gal|tmr|txt|dd|img|pdf)[A-Za-z_0-9]*108[A-Za-z_0-9]*\b',clean):assert ref in nodes,(n,p,ref)
  assert not re.search(r'\b(?:con|lbl|btn|gal|tmr|txt|dd|col|var|scr|img|pdf)[A-Za-z_0-9]*107\b',clean)
  total+=1
# Geometry requires Studio layout testing; not evaluated here.
gchecks=0

props={n:c['Properties'] for n,c in nodes.items()}
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
def fresh():return Engine(props)
def act(e,control):return e.run(props[control]['OnSelect'])
def search(e,text='',org='すべて',status='すべて'):
 e.overrides['txtKeyword108','Text']=text
 e.overrides['ddOrg108','Selected']={'Value':org}
 e.overrides['ddStatus108','Selected']={'Value':status}
 act(e,'btnSearch108');return e.state['colResult108']
def prop(e,n,p='Text'):return e.prop(n,p)
e=fresh()
check('初期化イベント・変数・コレクションが空の状態',e.state=={})
check('初期件数25名',prop(e,'lblListTitle108')=='職員一覧　25件')
check('初期1ページ目20名',len(prop(e,'galStaff108','Items'))==20)
check('初期ページ1/2',prop(e,'lblPage108')=='1 / 2')
check('初期選択 山田 太郎',prop(e,'lblName108')=='山田 太郎')
check('初期職員番号 00990000001',prop(e,'lblBasicVal0108')=='00990000001')
check('職員詳細が表示状態',prop(e,'conPerson108','Visible') is True)
for section,count in [('Work',3),('Commute',1),('Social',1),('Resident',1),('Tax',1),('Payroll',1)]:
 check('初期履歴 '+section,len(prop(e,'gal'+section+'108','Items'))==count)
check('初回前へ無効',prop(e,'btnPrev108','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnNext108')
check('初回次へで2ページ目5名',len(prop(e,'galStaff108','Items'))==5 and prop(e,'lblPage108')=='2 / 2')
check('末尾ページ次へ無効',prop(e,'btnNext108','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnPrev108');check('前へで20名に戻る',len(prop(e,'galStaff108','Items'))==20)
check('空欄検索25名',len(search(e))==25)
check('山田検索2名',[r['Name'] for r in search(e,'山田')]==['山田 太郎','山田 花子'])
check('職員番号検索1名',[r['Name'] for r in search(e,'00990000003')]==['佐藤 一郎'])
check('検索後の詳細切替',prop(e,'lblName108')=='佐藤 一郎')
check('組織絞込9名',len(search(e,org='01秘書課'))==9)
check('退職絞込3名',len(search(e,status='退職'))==3)
check('複合絞込1名',[r['Name'] for r in search(e,'山田',org='02総務課',status='在籍')]==['山田 花子'])
check('存在しない検索0名',len(search(e,'存在しない職員'))==0)
check('0件時に初期職員を誤表示しない',prop(e,'conPerson108','Visible') is False and prop(e,'lblNoMatch108','Visible') is True)
check('0件時のリスト空',prop(e,'galStaff108','Items')==[])
act(e,'btnClear108')
check('条件クリアで25名と山田太郎',prop(e,'lblListTitle108')=='職員一覧　25件' and prop(e,'lblName108')=='山田 太郎')
check('入力欄のクリア',prop(e,'txtKeyword108')=='')
row=prop(e,'galStaff108','Items')[1]
e.run(props['galStaff108']['OnSelect'],{'ThisItem':row})
check('一覧選択で山田花子に切替',prop(e,'lblName108')=='山田 花子')
check('選択と履歴の職員番号一致',all(r['StaffId']==row['StaffId'] for r in prop(e,'galWork108','Items')))
act(e,'btnCertificate108')
check('認定簿モーダルが開く',prop(e,'conLedgerModal108','Visible') is True)
check('認定簿氏名が選択職員と一致',prop(e,'lblLedger_employee_name108')=='山田 花子')
check('認定簿職員番号が選択職員と一致',prop(e,'lblLedger_employee_number108')==row['StaffId'])
check('認定簿69フィールド',len(e.state['colLedgerFields108'])==69)
check('認定簿月額合計10,480',prop(e,'lblLedger_monthly_amount_total108')=='10,480')
act(e,'btnLedgerClose108')
check('閉じるとPDF Viewer非表示',prop(e,'pdfLedger108','Visible') is False)
search(e,'00990000025')
check('通勤なし職員は0行',prop(e,'galCommute108','Items')==[])
check('通勤なし職員の認定簿ボタン無効',prop(e,'btnCertificate108','DisplayMode')=='DisplayMode.Disabled')
act(e,'btnLoad108')
check('テスト表示に戻すで全件復元',prop(e,'lblListTitle108')=='職員一覧　25件' and prop(e,'lblName108')=='山田 太郎')
act(e,'btnExport108')
check('検索出力全25行',len(e.state['colReport108'])==25)
check('検索出力TSVヘッダー＋25行',len(e.state['varTsv108'].splitlines())==26)
e2=fresh();act(e2,'btnPayExport108')
check('初期化なし給与出力15項目',len(e2.state['colReport108'])==15)

# Deliberately restore the reported causes; the new checks must reject them.
bad=deepcopy(app);bn,_=index(bad);bn['btnSearch108']['Properties']['AccessibleLabel']='="検索"'
check('不正AccessibleLabelの再導入を検出',bool(lint(bad)[0]))
bad=deepcopy(app);bn,_=index(bad);viewer=next(x for x in bad if 'pdfLedger108' in x);bad.remove(viewer);bn['conStaffMaster108']['Children'].append(viewer)
check('PDF Viewerの不正親を検出',index(bad)[1]['pdfLedger108'] is not None)
try:parse('=Notify("test",NotificationType.Success)\nSet(varTest,true)')
except ValueError:check('セミコロン欠落を構文検査で検出',True)
else:raise AssertionError('Missing separator passed')
badprops=deepcopy(props);badprops['galStaff108']['Items']='=colMissing108'
check('空コレクションへの依存を検出',len(Engine(badprops).prop('galStaff108','Items'))!=20)
report={'controls':len(nodes),'formulas_parsed':total,'local_dataflow_tests':len(checks),'passed_cases':checks,'validation_scope':'Limited local parser/evaluator; not Microsoft Power Fx compiler or Studio runtime','studio_tested':False,'pdf_runtime_tested':False,'outputs':[]}
for path in [S/'scrStaffMasterSearch_v1.08.paste.yaml',S/'scrStaffMasterSearch_v1.08.pa.yaml']:
 report['outputs'].append({'name':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(W/'v1.08-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
