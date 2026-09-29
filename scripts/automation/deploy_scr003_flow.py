"""Replace only the disabled SCR003 draft, retaining its approved connections.

No activation, sharing, roles, business rows or other flows are changed.
Uses the documented Dataverse workflow clientdata API.
"""
import copy, hashlib, json, subprocess, urllib.request, urllib.error
from pathlib import Path
from provision_scr003_attendance import URL, ORG
from build_scr003_flow import build

FLOW='ad3e498e-aabb-f111-aaae-e4fade05837b'
NAME='SCR003_勤務時間報告_Excel取込_開発中'

def walk(group):
    for a in group.values():
        yield a
        yield from walk(a.get('actions',{}))
        yield from walk(a.get('else',{}).get('actions',{}))

def main():
    token=subprocess.check_output(['az','account','get-access-token','--resource',URL,'--query','accessToken','-o','tsv'],text=True).strip()
    def request(path, body=None, etag=None):
        headers={'Authorization':'Bearer '+token,'Accept':'application/json','Content-Type':'application/json'}
        if etag: headers['If-Match']=etag
        req=urllib.request.Request(URL+'/api/data/v9.2/'+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method='GET' if body is None else 'PATCH')
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                data=r.read()
                return json.loads(data) if data else None
        except urllib.error.HTTPError as e:
            error=json.loads(e.read()).get('error',{})
            print('Dataverse error',error.get('code'),str(error.get('message',''))[:3000])
            raise
    assert request('WhoAmI')['OrganizationId'].lower()==ORG
    path='workflows('+FLOW+')'
    original=request(path+'?$select=workflowid,name,statecode,clientdata,ismanaged')
    assert original['name']==NAME and original['statecode']==0 and not original['ismanaged']
    current=json.loads(original['clientdata'])
    refs=current['properties']['connectionReferences']
    by_api={v['api']['name']:k for k,v in refs.items()}
    expected={'shared_commondataserviceforapps','shared_excelonlinebusiness','shared_onedriveforbusiness'}
    assert expected<=set(by_api),'Approved connection missing; stop without modification'
    old_actions=list(walk(current['properties']['definition']['actions']))
    excel=[a for a in old_actions if a.get('inputs',{}).get('host',{}).get('operationId')=='GetItems']
    assert len(excel)==1,'Expected one Excel reader'
    drive=excel[0]['inputs']['parameters']['drive']
    definition=build()
    for a in walk(definition['actions']):
        if a['type']=='OpenApiConnection':
            host=a['inputs']['host']; host['connectionName']=by_api[host['connectionName']]
            if host['operationId']=='GetItems': a['inputs']['parameters']['drive']=drive
    desired=copy.deepcopy(current);desired['properties']['definition']=definition
    # Retain the original recovery material only in the authenticated job artifact.
    out=Path('scr003-draft-backup');out.mkdir(exist_ok=True)
    (out/'clientdata.json').write_text(original['clientdata'])
    request(path,{'clientdata':json.dumps(desired,ensure_ascii=False)},original['@odata.etag'])
    after=request(path+'?$select=statecode,clientdata')
    assert after['statecode']==0,'Draft unexpectedly enabled'
    read=json.loads(after['clientdata'])
    assert read['properties']['definition']==definition,'Definition readback differs'
    assert read['properties']['connectionReferences']==refs,'Connection references changed'
    print('PASS: exact disabled draft updated; definition and existing connection references read back')
    print('Definition SHA256',hashlib.sha256(json.dumps(definition,sort_keys=True).encode()).hexdigest())
    print('Actions',len(list(walk(definition['actions']))))

if __name__=='__main__': main()

