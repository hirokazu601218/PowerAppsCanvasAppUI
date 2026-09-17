"""Staged payrollledger setup. Existing OIDC only; no permissions, billing or app edits."""
import json, os, subprocess, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]

def main():
 cfg=json.loads((ROOT/'config/apps/staff-master.json').read_text())
 request=json.loads((ROOT/'automation/payrollledger-run.json').read_text())
 started=datetime.fromisoformat(request['started_at']).timestamp()
 assert request['mode'] in ('preflight','provision','seed','verify')
 assert request['approved'] is True
 assert cfg['target']['environment_id']=='68e00049-b7e5-eda6-9888-9a3cc493c5be'
 url=cfg['target']['dataverse_url'].rstrip('/')
 assert url=='https://orge762dd9e.crm7.dynamics.com'
 token=subprocess.check_output(['az','account','get-access-token','--resource',url,'--query','accessToken','--output','tsv'],text=True,timeout=45).strip()
 def api(path,method='GET',body=None,headers=None):
  assert time.time()-started<3480,'PAUSED_TIME_LIMIT'
  req=urllib.request.Request(url+'/api/data/v9.2/'+path,method=method,data=json.dumps(body).encode() if body is not None else None,headers={'Authorization':'Bearer '+token,'Accept':'application/json','Content-Type':'application/json','OData-Version':'4.0','OData-MaxVersion':'4.0','MSCRM.SolutionUniqueName':cfg['solution_name'],**(headers or {})})
  try:
   with urllib.request.urlopen(req,timeout=90) as r:
    data=r.read();return json.loads(data) if data else {}
  except urllib.error.HTTPError as e:
   data=e.read()
   try:msg=json.loads(data).get('error',{}).get('message','Dataverse error')
   except ValueError:msg='Non-JSON Dataverse error'
   raise RuntimeError(f'{e.code}: {msg}') from None
 out=ROOT/'artifacts/payrollledger';out.mkdir(parents=True,exist_ok=True)
 result={'mode':request['mode'],'checked_at':datetime.now(timezone.utc).isoformat()}
 def save(name,data):
  (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 who=api('WhoAmI'); assert who['OrganizationId']=='9efe0732-a9b0-f111-8ade-002248f061b1'
 sol=api("solutions?$select=uniquename,ismanaged&$filter=uniquename%20eq%20'StaffMasterAutomation'&$expand=publisherid($select=customizationprefix)")['value']
 assert len(sol)==1 and not sol[0]['ismanaged'] and sol[0]['publisherid']['customizationprefix']=='crb3c'
 pm=api("EntityDefinitions(LogicalName='crb3c_staffbasic')?$select=LogicalName,EntitySetName,PrimaryIdAttribute&$expand=Keys")
 assert any(k['KeyAttributes']==['crb3c_staffnumber'] and k['EntityKeyIndexStatus']=='Active' for k in pm['Keys'])
 fields=['crb3c_staffnumber','crb3c_fullname','crb3c_hiredate','crb3c_leavedate','crb3c_orgfull','crb3c_orgshort',pm['PrimaryIdAttribute']]
 parents=api(pm['EntitySetName']+'?$select='+','.join(fields)+'&$orderby=crb3c_staffnumber')['value']
 assert len(parents)==25 and all(p['crb3c_staffnumber'].startswith('009900') for p in parents),'Unexpected parent dataset; no writes'
 assert len({p['crb3c_staffnumber'] for p in parents})==25
 tables=api("EntityDefinitions?$select=LogicalName,MetadataId&$filter=LogicalName%20eq%20'crb3c_payrollledger'")['value']
 lcid=api('organizations?$select=languagecode')['value'][0]['languagecode']
 result.update(state='PREFLIGHT_PASSED',parent_count=len(parents),parent_entity_set=pm['EntitySetName'],parent_primary_id=pm['PrimaryIdAttribute'],child_exists=bool(tables),base_language=lcid,organization_id=who['OrganizationId'])
 save('preflight.json',result);save('parents.json',parents);print(json.dumps(result),flush=True)
 if request['mode']=='preflight':return
 from payrollledger_schema import table, attributes, relationship, validate_rows, build_fixtures
 entity="EntityDefinitions(LogicalName='crb3c_payrollledger')"
 if not tables:
  assert request['mode']=='provision','Provision table first'
  api('EntityDefinitions','POST',table(lcid));print('TABLE_CREATED',flush=True)
 meta=api(entity+'?$select=LogicalName,MetadataId,OwnershipType,PrimaryNameAttribute,PrimaryIdAttribute,EntitySetName&$expand=Attributes')
 actual={a['LogicalName']:a for a in meta['Attributes']}
 assert meta['OwnershipType']=='UserOwned' and meta['PrimaryNameAttribute']=='crb3c_name'
 for exp in attributes(lcid):
  a=actual[exp['SchemaName'].lower()]
  typ=exp['@odata.type'].split('.')[-1].replace('AttributeMetadata','')
  assert a['AttributeType']==typ and a['RequiredLevel']['Value']==exp['RequiredLevel']['Value'],a['LogicalName']
  for key in ('MaxLength','MinValue','MaxValue','Precision','Format'):
   if key in exp:assert a[key]==exp[key],(a['LogicalName'],key)
  if 'DateTimeBehavior' in exp:assert a['DateTimeBehavior']['Value']=='DateOnly'
 relname='crb3c_staffbasic_payrollledger'
 found=api("RelationshipDefinitions/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata?$filter=SchemaName%20eq%20'"+relname+"'")['value']
 if not found:
  assert request['mode']=='provision','Provision relationship first'
  api('RelationshipDefinitions','POST',relationship(lcid,pm['PrimaryIdAttribute']));print('RELATIONSHIP_CREATED',flush=True)
 rel=api("RelationshipDefinitions(SchemaName='"+relname+"')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
 assert rel['ReferencedEntity']=='crb3c_staffbasic' and rel['ReferencingEntity']=='crb3c_payrollledger'
 assert rel['ReferencedAttribute']==pm['PrimaryIdAttribute'] and rel['ReferencingAttribute']=='crb3c_staffbasicid'
 assert rel['CascadeConfiguration']['Delete']=='Restrict'
 for name in ('Assign','Reparent','Share','Unshare'):assert rel['CascadeConfiguration'][name]=='NoCascade'
 lookup=api(entity+"/Attributes(LogicalName='crb3c_staffbasicid')/Microsoft.Dynamics.CRM.LookupAttributeMetadata")
 assert lookup['Targets']==['crb3c_staffbasic'] and lookup['RequiredLevel']['Value']=='ApplicationRequired'
 if request['mode']=='provision':
  api('PublishXml','POST',{'ParameterXml':'<importexportxml><entities><entity>crb3c_payrollledger</entity><entity>crb3c_staffbasic</entity></entities></importexportxml>'})
 result.update(state='TABLE_AND_RELATIONSHIP_VERIFIED',business_columns=163,child_entity_set=meta['EntitySetName'],relationship=relname,delete_behavior='Restrict')
 save('schema-result.json',result);save('relationship.json',rel)
 print(json.dumps(result),flush=True)
 if request['mode']=='provision':return
 rows=build_fixtures(parents,pm['PrimaryIdAttribute'])
 validate_rows(rows,parents)
 nav=rel['ReferencingEntityNavigationPropertyName']
 for fixture in rows:
  key=fixture['id'];data=fixture['data']; sid=data['crb3c_staffnumber']
  path=meta['EntitySetName']+'('+key+')'
  existing=api(meta['EntitySetName']+'?$filter='+meta['PrimaryIdAttribute']+'%20eq%20'+key)['value']
  if not existing:
   assert request['mode']=='seed','Missing seed row'
   payload={**data,meta['PrimaryIdAttribute']:key,nav+'@odata.bind':'/'+pm['EntitySetName']+"(crb3c_staffnumber='"+sid+"')"}
   api(path,'PATCH',payload,{'If-None-Match':'*'})
  read=api(path+'?$expand='+nav+'($select=crb3c_staffnumber,crb3c_fullname)')
  assert read['_crb3c_staffbasicid_value']==fixture['parent_id']
  assert read[nav]['crb3c_staffnumber']==sid and read[nav]['crb3c_fullname']==data['crb3c_fullname']
  for field,value in data.items():
   observed=read.get(field)
   if value is not None and field.endswith(('startdate','enddate','eventdate','submitteddate','receiveddate','recognitionstart')):
    assert observed[:10]==value[:10],field
   else:assert observed==value,(sid,field)
 # Query all linked rows; show zero/one/many through parent expansion.
 pnav=rel['ReferencedEntityNavigationPropertyName']
 expanded=api(pm['EntitySetName']+'?$select=crb3c_staffnumber&$expand='+pnav+'($select='+meta['PrimaryIdAttribute']+')')['value']
 counts={p['crb3c_staffnumber']:len(p[pnav]) for p in expanded}
 expected={p['crb3c_staffnumber']:sum(r['data']['crb3c_staffnumber']==p['crb3c_staffnumber'] for r in rows) for p in parents}
 assert counts==expected,(counts,expected)
 # Parents remain unchanged by this operation.
 after=api(pm['EntitySetName']+'?$select='+','.join(fields)+'&$orderby=crb3c_staffnumber')['value']
 assert after==parents,'Parent data changed'
 result.update(state='SEED_AND_RELATIONSHIP_VERIFIED',seed_count=len(rows),child_counts=counts,parents_unchanged=True,all_163_values_verified=True)
 save('seed-fixtures.json',rows);save('result.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
