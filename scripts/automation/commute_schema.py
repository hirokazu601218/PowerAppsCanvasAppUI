"""Exact 84-column workbook mapping plus Dataverse primary name and parent lookup."""
import json,re,uuid
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/'config/dataverse/commute-columns.json').read_text())
FIELDS=SPEC['fields']
def label(text,lcid):return {'LocalizedLabels':[{'Label':text,'LanguageCode':lcid}]}
def attributes(lcid):
 attrs=[]
 for f in FIELDS:
  a={'SchemaName':f['logical_name'],'DisplayName':label(f['display_name'],lcid),'Description':label(f['source_constraint'],lcid),'RequiredLevel':{'Value':'None'}}
  kind=f['kind']
  if kind=='text':a.update({'@odata.type':'Microsoft.Dynamics.CRM.StringAttributeMetadata','MaxLength':f['max_length'],'FormatName':{'Value':'Text'}})
  elif kind=='date':a.update({'@odata.type':'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata','Format':'DateOnly','DateTimeBehavior':{'Value':'DateOnly'}})
  elif kind=='integer':a.update({'@odata.type':'Microsoft.Dynamics.CRM.IntegerAttributeMetadata','MinValue':f['min'],'MaxValue':f['max'],'Format':'None'})
  elif kind=='decimal':a.update({'@odata.type':'Microsoft.Dynamics.CRM.DecimalAttributeMetadata','MinValue':f['min'],'MaxValue':f['max'],'Precision':f['precision']})
  attrs.append(a)
 attrs.append({'@odata.type':'Microsoft.Dynamics.CRM.StringAttributeMetadata','SchemaName':'crb3c_name','DisplayName':label('通勤レコード名',lcid),'RequiredLevel':{'Value':'ApplicationRequired'},'MaxLength':100,'IsPrimaryName':True,'FormatName':{'Value':'Text'}})
 return attrs

def table(lcid):
 return {'@odata.type':'Microsoft.Dynamics.CRM.EntityMetadata','SchemaName':'crb3c_Commute','DisplayName':label('T_通勤',lcid),'DisplayCollectionName':label('T_通勤',lcid),'Description':label('添付T_通勤_テーブル定義書84項目。職員基本1件に通勤0件以上。テスト専用。',lcid),'OwnershipType':'UserOwned','IsActivity':False,'HasActivities':False,'HasNotes':False,'Attributes':attributes(lcid)}

def relationship(lcid,parent_id):
 return {'@odata.type':'Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata','SchemaName':'crb3c_staffbasic_commute','ReferencedEntity':'crb3c_staffbasic','ReferencedAttribute':parent_id,'ReferencingEntity':'crb3c_commute','ReferencingEntityNavigationPropertyName':'crb3c_StaffBasic','ReferencedEntityNavigationPropertyName':'crb3c_StaffBasic_Commutes','AssociatedMenuConfiguration':{'Behavior':'UseCollectionName','Group':'Details','Label':label('通勤',lcid),'Order':10000},'CascadeConfiguration':{'Assign':'NoCascade','Delete':'Restrict','Merge':'NoCascade','Reparent':'NoCascade','Share':'NoCascade','Unshare':'NoCascade','RollupView':'NoCascade'},'Lookup':{'@odata.type':'Microsoft.Dynamics.CRM.LookupAttributeMetadata','SchemaName':'crb3c_StaffBasicId','DisplayName':label('職員基本',lcid),'Description':label('職員番号の代替キーで照合した親レコードへの参照。職員に通勤0件を許容。',lcid),'RequiredLevel':{'Value':'ApplicationRequired'}}}

def build_fixtures(parents,parent_id):
 by={p['crb3c_staffnumber']:p for p in parents};rows=[]
 # Keep parent values unchanged; paid examples only where parent commute fields are blank.
 cases=[(3,'TK-910001','2026-04-01','2026-09-30','半年定期',1300),(3,'TK-910002','2026-10-01','2027-03-31','半年定期',1400),(4,'TK-910003','2025-04-01','2026-03-31','毎月精算',16800),(11,'TK-910004','2026-04-01','2027-03-31','支給なし',0),(13,'TK-910005','2026-04-01','2027-03-31','支給なし',0),(25,'TK-910006','2099-04-01','2100-03-31','支給なし',0)]
 for n,rid,start,end,method,monthly in cases:
  sid=f'0099000000{n:02}';p=by[sid]
  data={f['logical_name']:None for f in FIELDS}
  def put(**kw):data.update({'crb3c_'+k:v for k,v in kw.items()})
  put(name=rid+' '+sid,recognitionid=rid,staffnumber=sid,fullname=p['crb3c_fullname'],startdate=start,enddate=end,method=method,monthly=monthly,icfare=420 if method=='毎月精算' else 0,sixmonthpass=int(method=='半年定期'),monthlyfixed=0,monthlyactual=int(method=='毎月精算'),matchcount=int(method!='支給なし'),target1=method,targetcombined=method,eventdate=start,submitteddate=start,receiveddate=start,monthlytotal=monthly)
  for m in [4,5,6,7,8,9,10,11,12,1,2,3]:
   amount=monthly if method=='毎月精算' else monthly*6 if method=='半年定期' and m==int(start[5:7]) else 0
   data['crb3c_month'+str(m).zfill(2)]=amount
  if monthly:
   put(route1_operator='架空テスト鉄道',route1_from=f'架空{n:02}駅',route1_to='テスト中央駅',route1_tickettype='6箇月定期券' if method=='半年定期' else '回数券他',route1_ticketbasis=0 if method=='半年定期' else 40,route1_distancekm=12.5,route1_ticketamount=monthly if method=='毎月精算' else 0,route1_passamount=monthly*6 if method=='半年定期' else 0,route1_passmonths=6 if method=='半年定期' else None,route1_amount=monthly,route1_recognitionstart=start,route1_paymonth=int(start[5:7]),route1_remarks='合成テスト。正式認定には使用不可。')
  rows.append({'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'staff-commute-fixture/'+rid)),'parent_id':p[parent_id],'data':data})
 return rows

def validate_rows(rows,parents):
 by={p['crb3c_staffnumber']:p for p in parents}
 assert len({r['id'] for r in rows})==len(rows)
 for row in rows:
  d=row['data'];sid=d['crb3c_staffnumber'];assert re.fullmatch(r'[0-9]{12}',sid) and sid in by
  assert re.fullmatch(r'TK-[0-9]{6}',d['crb3c_recognitionid'])
  p=by[sid];assert d['crb3c_fullname']==p['crb3c_fullname']
  assert d['crb3c_startdate']<=d['crb3c_enddate']
  if p.get('crb3c_hiredate'):assert d['crb3c_startdate']>=p['crb3c_hiredate'][:10]
  if p.get('crb3c_leavedate'):assert d['crb3c_enddate']<=p['crb3c_leavedate'][:10]
  if p.get('crb3c_commutemethod') is not None:assert d['crb3c_method']==p['crb3c_commutemethod']
  if p.get('crb3c_passamount') is not None:assert (d['crb3c_route1_passamount'] or 0)==p['crb3c_passamount']
  if p.get('crb3c_onewayfare') is not None:assert d['crb3c_icfare']==p['crb3c_onewayfare']
  for f in FIELDS:
   v=d[f['logical_name']]
   if v is None:continue
   if f['kind']=='text':assert isinstance(v,str) and len(v)<=f['max_length']
   elif f['kind']=='date':date.fromisoformat(v)
   elif f['kind']=='integer':assert type(v) is int and f['min']<=v<=f['max']
   elif f['kind']=='decimal':assert isinstance(v,(int,float)) and f['min']<=v<=f['max']
