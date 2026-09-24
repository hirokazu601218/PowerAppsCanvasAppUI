"""Deploy the isolated HTML report and prepare/remove deterministic UI fixtures.

No original-table writes, schema changes, grants, or Canvas publication.
The user waived the Work session's 60-minute interruption for this release;
individual requests and workflow execution remain bounded.
"""
import base64
import hashlib
import json
import subprocess
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = 'crb3c_reports/commute-ledger-studio.html'
MARKER = 'LT-20260924-'
SID = '009900000011'

def main():
    mode = sys.argv[1]
    assert mode in ('prepare', 'cleanup')
    cfg = json.loads((ROOT/'config/apps/staff-master.json').read_text())
    assert cfg['target']['environment_id'] == '68e00049-b7e5-eda6-9888-9a3cc493c5be'
    origin = cfg['target']['dataverse_url'].rstrip('/')
    token = subprocess.check_output(['az','account','get-access-token','--resource',origin,'--query','accessToken','--output','tsv'],text=True,timeout=45).strip()
    def api(path, method='GET', body=None, extra=None):
        headers = {'Authorization':'Bearer '+token,'Accept':'application/json','Content-Type':'application/json','OData-Version':'4.0','OData-MaxVersion':'4.0','MSCRM.SolutionUniqueName':cfg['solution_name']}
        headers.update(extra or {})
        request=urllib.request.Request(origin+'/api/data/v9.2/'+path,method=method,headers=headers,data=None if body is None else json.dumps(body).encode())
        with urllib.request.urlopen(request,timeout=90) as response:
            raw=response.read()
            return json.loads(raw) if raw else {}
    assert api('WhoAmI')['OrganizationId']=='9efe0732-a9b0-f111-8ade-002248f061b1'
    def rows(path):
        result=[]
        while path:
            page=api(path); result.extend(page['value'])
            nxt=page.get('@odata.nextLink')
            if nxt:
                assert nxt.startswith(origin+'/api/data/v9.2/')
                path=nxt.split('/api/data/v9.2/',1)[1]
            else: path=None
        return result
    def original_hashes():
        result={}
        for logical in ('crb3c_staffbasic','crb3c_commute','crb3c_payrollledger'):
            meta=api("EntityDefinitions(LogicalName='"+logical+"')?$select=EntitySetName,PrimaryIdAttribute")
            data=rows(meta['EntitySetName']+'?$orderby='+meta['PrimaryIdAttribute'])
            result[logical]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
        return result
    before=original_hashes()
    state={'mode':mode,'original_hashes_before':before}
    logical='crb3c_studiopayrollledger'
    meta=api("EntityDefinitions(LogicalName='"+logical+"')?$select=LogicalName,EntitySetName,PrimaryIdAttribute&$expand=Attributes")
    assert meta['LogicalName']==logical
    entity=meta['EntitySetName']; pk=meta['PrimaryIdAttribute']
    keys=[str(uuid.uuid5(uuid.NAMESPACE_URL,MARKER+str(i))) for i in range(3)]
    if mode=='prepare':
        html=(ROOT/'src/staff-master/candidates/commute-html-v1.01/src/commute-ledger.html').read_text()
        for old,new in [('crb3c_commutes','crb3c_studiocommutes'),('crb3c_staffbasics','crb3c_studiostaffbasics'),('crb3c_commuteid','crb3c_studiocommuteid')]:
            assert old in html; html=html.replace(old,new)
        # Preserve the child lookup logical name. Only parent primary-key references change.
        html=html.replace('s.crb3c_staffbasicid','s.crb3c_studiostaffbasicid').replace('$select=crb3c_staffbasicid,','$select=crb3c_studiostaffbasicid,')
        assert '/crb3c_commutes(' not in html and '/crb3c_staffbasics(' not in html
        encoded=base64.b64encode(html.encode()).decode()
        found=rows("webresourceset?$select=webresourceid,name,content&$filter=name%20eq%20'"+NAME+"'")
        assert len(found)<=1
        if found:
            # Never overwrite an unrelated resource with the same name.
            assert base64.b64decode(found[0]['content']).decode()==html
            rid=found[0]['webresourceid']
        else:
            rid=str(uuid.uuid5(uuid.NAMESPACE_URL,MARKER+NAME))
            api('webresourceset','POST',{'webresourceid':rid,'name':NAME,'displayname':'通勤認定簿 1.01 Studio隔離版','webresourcetype':1,'content':encoded})
        api('PublishXml','POST',{'ParameterXml':'<importexportxml><webresources><webresource>'+rid+'</webresource></webresources></importexportxml>'})
        assert api('webresourceset('+rid+')?$select=content')['content']==encoded
        state['html_sha256']=hashlib.sha256(html.encode()).hexdigest()
        state['html_resource']=NAME
        base=rows(entity+"?$filter=crb3c_staffnumber%20eq%20'"+SID+"'")
        base=[r for r in base if not r.get('crb3c_name','').startswith(MARKER)]
        assert len(base)==1
        editable={a['LogicalName'] for a in meta['Attributes'] if a.get('IsValidForCreate') and a['LogicalName'].startswith('crb3c_') and a['AttributeType'] not in ('Lookup','Uniqueidentifier','Virtual')}
        relationship=api("RelationshipDefinitions(SchemaName='crb3c_studiostaffbasic_payrollledger')/Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata")
        assert relationship['ReferencedEntity']=='crb3c_studiostaffbasic' and relationship['ReferencingEntity']==logical
        parent=base[0]['_crb3c_staffbasicid_value']
        nav=relationship['ReferencingEntityNavigationPropertyName']
        for i,key in enumerate(keys):
            payload={k:v for k,v in base[0].items() if k in editable}
            payload.update({pk:key,'crb3c_name':MARKER+str(i),'crb3c_sequence':900+i,'crb3c_payment_date':['令和08年04月23日','令和08年04月30日','日付未確定'][i], 'crb3c_remarks':('長文確認。'*45+'末尾確認') if i==1 else '軽量版の一時試験レコード'})
            payload[nav+'@odata.bind']='/crb3c_studiostaffbasics('+parent+')'
            existing=rows(entity+'?$filter='+pk+'%20eq%20'+key)
            if existing: assert existing[0]['crb3c_name']==MARKER+str(i)
            else: api(entity+'('+key+')','PATCH',payload,{'If-None-Match':'*'})
            read=api(entity+'('+key+')')
            assert read['crb3c_name']==payload['crb3c_name'] and read['crb3c_payment_date']==payload['crb3c_payment_date']
        state['fixtures_prepared']=3
    else:
        for i,key in enumerate(keys):
            existing=rows(entity+'?$filter='+pk+'%20eq%20'+key)
            if existing:
                assert existing[0]['crb3c_name']==MARKER+str(i) and existing[0]['crb3c_staffnumber']==SID
                api(entity+'('+key+')','DELETE')
            assert not rows(entity+'?$filter='+pk+'%20eq%20'+key)
        state['fixtures_remaining']=0
    after=original_hashes()
    assert before==after,'Original table content changed'
    state['original_hashes_after']=after
    out=ROOT/'artifacts/lightweight';out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
    print(json.dumps(state,ensure_ascii=False))

if __name__=='__main__': main()
