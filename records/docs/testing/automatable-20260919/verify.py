"""Readback audit; no network or browser control. Run in the evidence directory."""
import collections, hashlib, json, re
from pathlib import Path
import yaml

P=Path(__file__).parent
INPUTS={
 'staff-basic-25.json':'tests/fixtures/staff-basic-25.json',
 'staff-history-synthetic.json':'tests/fixtures/staff-history-synthetic.json',
 'commute-6.json':'tests/fixtures/commute-6.json',
 'payrollledger-7.json':'tests/fixtures/payrollledger-7.json',
 'commute-columns.json':'config/dataverse/commute-columns.json',
 'payrollledger-columns.json':'config/dataverse/payrollledger-columns.json',
 'ledger-field-map.json':'src/staff-master/patches/v1.18/ledger-field-map.json',
}
def read(n):
    path=P/n
    if not path.exists() and n in INPUTS:path=P.parents[2]/INPUTS[n]
    return json.loads(path.read_text())
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
class UniqueLoader(yaml.SafeLoader): pass
def unique(loader,node,deep=False):
    d={}
    for k,v in node.value:
        key=loader.construct_object(k,deep=deep)
        if key in d: raise ValueError('Duplicate YAML key: '+str(key))
        d[key]=loader.construct_object(v,deep=deep)
    return d
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique)
source=(P/'Screen1.pa.yaml').read_text()
screen=yaml.load(source,Loader=UniqueLoader)['Screens']['Screen1']
controls={}
def walk(items,parent):
    for item in items:
        for name,c in item.items():
            if name in controls: raise ValueError('Duplicate control '+name)
            controls[name]={**c,'parentPath':parent}
            walk(c.get('Children',[]),parent+'/'+name)
walk(screen['Children'],'Screen1')
catalog={}
for name,c in controls.items():
    v=c['Control']; cat=catalog.setdefault(v,{'controls':[],'properties':set(),'variants':set()})
    cat['controls'].append(name);cat['properties'].update(c.get('Properties',{}))
    if 'Variant' in c:cat['variants'].add(c['Variant'])
for c in catalog.values():c['properties']=sorted(c['properties']);c['variants']=sorted(c['variants'])
save('observed-control-catalog.json',{'authority':'Studio readback inventory, NOT an independent official supported-property catalog','types':catalog})
assert all('AccessibleLabel' not in c.get('Properties',{}) for c in controls.values() if c['Control'].startswith('Classic/Button@'))
assert all(c['parentPath']=='Screen1' for c in controls.values() if c['Control'].startswith('PDFViewer@'))
# Dedent the existing Children block; preserve every unchanged formula and image byte.
children_text=source.split('    Children:\n',1)[1]
paste='\n'.join(line[6:] if line.startswith('      ') else line for line in children_text.split('\n'))
(P/'Screen1.paste.yaml').write_text(paste)
paste_tree=yaml.load(paste,Loader=UniqueLoader)
assert paste_tree==screen['Children']
mutated=yaml.load(paste,Loader=UniqueLoader)
first=next(iter(mutated[0].values()));first.setdefault('Properties',{})['Width']='=-999'
assert mutated!=screen['Children']
save('source-comparison.json',{'screen':'Screen1 only; other five screens not regenerated','controlCount':len(controls),'typeCount':len(catalog),'managementPasteEqual':True,'changedWidthDetected':True,'duplicateControlNames':0,'invalidClassicAccessibleLabel':0,'pdfViewerAtScreenRoot':True,'managementSha256':hashlib.sha256(source.encode()).hexdigest(),'pasteSha256':hashlib.sha256(paste.encode()).hexdigest(),'studioPasteImportPerformed':False})
maps=[]
def add(group,index,key,header,kind,headerControl,valueControl,binding,provenance):
    maps.append(dict(group=group,index=index,key=key,header=header,kind=kind,headerControl=headerControl,valueControl=valueControl,binding=binding,provenance=provenance))
work=[('Start','適用開始日','date'),('End','適用終了日','date'),('Daily','日額単価','number'),('Scheduled','所定勤務時間','text'),('Hours','勤務時間','text'),('Overtime','超勤基礎単価（参考）','number'),('Change','異動区分','text'),('Reason','発令事由区分','text'),('Finish','勤務時間終了','text'),('DailyHours','1日あたり勤務時間','decimal2')]
social=[('Category','職員雇用区分','text'),('Birth','生年月日','text'),('AgeApril','4/1時点年齢','integer'),('AgeMarch','3/1時点年齢','integer'),('Care','介護徴収該当','text'),('PensionExempt','厚生年金免除該当','text'),('Elderly','後期高齢者徴収該当','text'),('Grade','厚生、級','integer'),('Monthly','厚生月額','number')]
tax=[('Start','適用開始日','date'),('End','適用終了日','date'),('TaxClass','税表区分','text'),('Employment','雇用保険加入区分','text'),('Saving','共済貯金月額','number'),('Loan','共済貸付月額','number'),('Dependents','扶養控除人数','integer'),('Note','備考','text')]
for group,fields in [('Work',work),('Social',social),('Tax',tax)]:
    for i,(key,label,kind) in enumerate(fields):add(group,i,key,label,kind,f'lblH{group}111{i}',f'lblC{group}111{i}',key,'Synthetic fixture keys/types independent; Japanese label mapping manually documented from existing UI contract, not a production dictionary')
add('Work',-1,'state','適用状態','derived','lblHWorkState111','lblCWorkState111','Start','Existing fixed reference-date history status contract; prior independent 011 expected value')
basic=[('staffnumber','StaffId','職員番号'),('fullname','Name','氏名'),('orgfull','OrgFull','組織・所属（正式名称）'),('orgshort','Org','組織名略称'),('birthdate','Birth','生年月日'),('sex','Sex','性別'),('hiredate','Hire','採用日'),('leavedate','Leave','退職日'),('status','Status','在籍状態')]
for i,(key,binding,label) in enumerate(basic):add('Basic',i,key,label,'text',f'lblBasicKey{i}111',f'lblBasicVal{i}111',binding,'staff-basic-25 fixture / basic9 contract; status derived from dates')
commute=[('crb3c_startdate','適用開始日 / 認定ID','date_id','適用開始日'),('crb3c_enddate','適用終了日','date','適用終了日'),('crb3c_method','支給方式','text','支給方式'),('crb3c_month04','通勤4月','number','通勤4月'),('crb3c_month10','通勤10月','number','通勤10月')]
for i,(key,label,kind,binding) in enumerate(commute):add('Commute',i,key,label,kind,f'lblHCommute111{i}',f'lblCCommute111{i}',binding,'commute-columns.json original workbook mapping; composite first column adds recognition ID')
columns=read('payrollledger-columns.json')['fields']
for i,col in enumerate(columns):add('PayrollModal',i,col['logical_name'],col['display_name'],col['kind'],f'lblHPayrollModal111{i}',f'lblCPayrollModal111{i}',col['logical_name'],'payrollledger-columns.json source workbook rows')
keys=['period_year','payment_date','basepay_current','basepay_adjustment','commuting_allowance_current','commuting_allowance_adjustment','telework_allowance_current','telework_allowance_adjustment','overtime_allowance_current','overtime_allowance_adjustment','gross','deduction_total_current','deduction_total_adjustment','net','remarks']
for i,key in enumerate(keys):
    col=next(x for x in columns if x['logical_name']=='crb3c_'+key)
    label='現金支給額' if key=='net' else col['display_name']
    add('Payroll',i,col['logical_name'],label,col['kind'],f'lblHPayroll111{i}',f'lblCPayroll111{i}',col['logical_name'],'Original HTML overview15 order / independent payroll column definition; net intentionally shown as 現金支給額')
checks=[]
for m in maps:
    h=controls[m['headerControl']]['Properties']['Text'];v=controls[m['valueControl']]['Properties']['Text']
    checks.append({'control':m['valueControl'],'headerMatch':h=='="'+m['header']+'"','bindingMatch':bool(re.search(r'\.'+re.escape(m['binding'])+r'(?![\w])',v)),'formula':v})
save('field-map.json',maps)
save('field-source-checks.json',{'count':len(checks),'checks':checks,'mismatches':[x for x in checks if not x['headerMatch'] or not x['bindingMatch']]})
# Full fixture type validation is separate from display-string verification.
typechecks=[]
for filename,fields in [('payrollledger-7.json',columns),('commute-6.json',read('commute-columns.json')['fields'])]:
    for row in read(filename):
        for f in fields:
            val=row['data'].get(f['logical_name']);kind=f['kind']
            valid=val is None or (isinstance(val,(int,float)) and not isinstance(val,bool) if kind in ('integer','decimal','money','number') else isinstance(val,str))
            typechecks.append({'fixture':filename,'row':row['id'],'column':f['logical_name'],'kind':kind,'valid':valid})
save('fixture-type-checks.json',{'count':len(typechecks),'mismatches':[x for x in typechecks if not x['valid']]})
live=read('live-011.json'); live_by={x['name']:x['text'] for x in live}
staff=next(x for x in read('staff-basic-25.json') if x['staffnumber'].endswith('011'))
history=read('staff-history-synthetic.json')
actual=[]
for m in maps:
    g=m['group'];key=m['key']
    if g=='PayrollModal':continue
    if g=='Basic':
        value=('在籍' if staff.get('hiredate') and not staff.get('leavedate') else '') if key=='status' else staff.get(key)
        if key.endswith('date') and value:value=value.replace('-','/')
    elif g in history:
        value=next(x for x in history[g] if x['StaffId'].endswith('011')).get(key)
        if key=='state':value=next(x['text'] for x in read('prior-independent-011.json') if x['name']==m['valueControl'])
    else:
        records=read('commute-6.json' if g=='Commute' else 'payrollledger-7.json')
        row=next(x['data'] for x in records if x['data']['crb3c_staffnumber'].endswith('011'))
        value=row.get(key)
        if m['kind']=='date_id':value=value.replace('-','/')+row['crb3c_recognitionid']
    if value is None:value=''
    elif m['kind']=='date':
        value=str(value).replace('-','/')
        # Existing independent expected-value evidence defines sentinel End as blank.
        prior=next((x for x in read('prior-independent-011.json') if x['name']==m['valueControl']),None)
        if key=='End' and value=='2099/03/31' and prior and prior['text']=='':value=''
    elif m['kind']=='decimal2':value=f'{value:.2f}'
    elif m['kind'] in ('number','integer','money','decimal') and isinstance(value,(int,float)):value=f'{value:,}'
    value=str(value)
    actual.append({'control':m['valueControl'],'expected':value,'actual':live_by.get(m['valueControl']),'match':live_by.get(m['valueControl'])==value,'headerMatch':live_by.get(m['headerControl'])==m['header']})
save('live-011-comparison.json',{'count':len(actual),'checks':actual,'mismatches':[x for x in actual if not x['match'] or not x['headerMatch']]})
print(json.dumps({'controls':len(controls),'fieldMappings':len(maps),'sourceMismatches':sum(not x['headerMatch'] or not x['bindingMatch'] for x in checks),'fixtureTypeChecks':len(typechecks),'fixtureTypeMismatches':sum(not x['valid'] for x in typechecks),'liveChecks':len(actual),'liveMismatches':[x for x in actual if not x['match'] or not x['headerMatch']]},ensure_ascii=False))

paylive={x['name']:x['text'] for x in read('live-payroll-011.json')}
payrow=next(x['data'] for x in read('payrollledger-7.json') if x['data']['crb3c_staffnumber'].endswith('011'))
pc=[]
for f in maps:
    if f['group']!='PayrollModal':continue
    v=payrow.get(f['key']);expected='' if v is None else f'{v:,}' if isinstance(v,(int,float)) else v
    pc.append({'control':f['valueControl'],'expected':expected,'actual':paylive.get(f['valueControl']),'valueMatch':paylive.get(f['valueControl'])==expected,'headerMatch':paylive.get(f['headerControl'])==f['header']})
save('live-payroll-comparison.json',{'count':len(pc),'checks':pc,'mismatches':[c for c in pc if not c['valueMatch'] or not c['headerMatch']]})
import datetime
ledger=read('ledger-field-map.json');ll={x['name']:x['text'] for x in read('live-ledger-011.json')}
cr=next(x['data'] for x in read('commute-6.json') if x['data']['crb3c_staffnumber'].endswith('011'))
lc=[]
for f in ledger:
    v={'Name':staff['fullname'],'StaffId':staff['staffnumber'],'Org':staff['orgshort']}.get(f['column']) if f['source']=='staff' else cr.get(f['column'])
    kind=f['format']
    if v is None:expected=''
    elif kind in ('year','month','day'):
        dt=datetime.date.fromisoformat(v[:10]);expected=str({'year':dt.year-2018,'month':dt.month,'day':dt.day}[kind])
    elif kind in ('amount','integer'):expected=f'{v:,.0f}'
    elif kind in ('decimal','text'):expected=str(v)
    else:raise ValueError('Unsupported nonempty ledger formatter '+kind)
    name='lblLedger_'+f['field']+'111'
    lc.append({'control':name,'expected':expected,'actual':ll.get(name),'match':ll.get(name)==expected,'bindingMatch':'Field="'+f['field']+'"' in controls[name]['Properties']['Text']})
save('live-ledger-comparison.json',{'count':len(lc),'checks':lc,'mismatches':[c for c in lc if not c['match'] or not c['bindingMatch']]})
save('integrated-summary.json',{'mappedDisplayFields':len(maps)+len(ledger),'liveComparedValues':len(actual)+len(pc)+len(lc),'liveMismatches':sum(not c['match'] or not c['headerMatch'] for c in actual)+sum(not c['valueMatch'] or not c['headerMatch'] for c in pc)+sum(not c['match'] or not c['bindingMatch'] for c in lc),'independentBusinessHeaderApprovalForSyntheticHistory':False,'productionUnknownColumnsCovered':False})
print('Payroll',len(pc),'Ledger',len(lc),'total',len(actual)+len(pc)+len(lc))

all_controls={};six=[]
def collect(items,parent):
    for item in items:
        for name,c in item.items():
            if name in all_controls:raise ValueError('Cross-screen duplicate '+name)
            all_controls[name]={**c,'parentPath':parent}
            collect(c.get('Children',[]),parent+'/'+name)
for path in sorted(P.glob('*.pa.yaml')):
    raw=path.read_text();doc=yaml.load(raw,Loader=UniqueLoader);sn=next(iter(doc['Screens']));sc=doc['Screens'][sn]
    chunk=raw.split('    Children:\n',1)[1];txt='\n'.join(line[6:] if line.startswith('      ') else line for line in chunk.split('\n'))
    assert yaml.load(txt,Loader=UniqueLoader)==sc['Children']
    path.with_name(path.name.replace('.pa.yaml','.paste.yaml')).write_text(txt)
    collect(sc['Children'],sn)
    six.append({'screen':sn,'equal':True,'managementSha256':hashlib.sha256(raw.encode()).hexdigest(),'pasteSha256':hashlib.sha256(txt.encode()).hexdigest()})
all_catalog={}
for n,c in all_controls.items():
    entry=all_catalog.setdefault(c['Control'],{'controls':[],'properties':set(),'variants':set()})
    entry['controls'].append(n);entry['properties'].update(c.get('Properties',{}))
    if 'Variant' in c:entry['variants'].add(c['Variant'])
    if c['Control'].startswith('Classic/Button@'):assert 'AccessibleLabel' not in c.get('Properties',{})
    if c['Control'].startswith('PDFViewer@'):assert '/' not in c['parentPath']
for e in all_catalog.values():e['properties']=sorted(e['properties']);e['variants']=sorted(e['variants'])
save('observed-control-catalog.json',{'authority':'Current Studio readback inventory of six screens; NOT independent official version-property support catalog','controlCount':len(all_controls),'types':all_catalog})
save('six-screen-comparison.json',{'screens':six,'controlCount':len(all_controls),'duplicateNames':0,'managementPasteEqual':all(x['equal'] for x in six),'pasteImported':False})
print('Current screens',len(six),'controls',len(all_controls),'types',len(all_catalog))
