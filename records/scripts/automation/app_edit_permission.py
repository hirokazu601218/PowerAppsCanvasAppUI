"""Grant only the explicitly approved existing app user CanEdit; no Dataverse role writes."""
import json, subprocess, time, urllib.request, urllib.parse, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def assignments(data):
    found={}
    def walk(obj):
        if isinstance(obj,dict):
            p=obj.get('properties',obj)
            if isinstance(p,dict) and isinstance(p.get('principal'),dict) and p.get('roleName'):
                principal=p['principal']
                key=(str(principal.get('id','')).lower(),p['roleName'])
                if not key[0]: raise ValueError('Permission principal has no ID')
                found[key]=p
            for v in obj.values(): walk(v)
        elif isinstance(obj,list):
            for v in obj: walk(v)
    walk(data)
    return found

def target_id(before,email):
    matches={key[0] for key,p in before.items()
             if str(p['principal'].get('email','')).lower()==email.lower()
             and p['principal'].get('type')=='User'}
    if len(matches)!=1: raise ValueError('Expected exactly one existing email-matched user')
    identity=matches.pop()
    uuid.UUID(identity)
    roles={key[1] for key in before if key[0]==identity}
    if not roles or not roles.issubset({'CanView','CanEdit'}):
        raise ValueError('Unexpected target role')
    return identity

def main():
    cfg=json.loads((ROOT/'config/apps/staff-master.json').read_text())
    request=json.loads((ROOT/'automation/app-edit-permission.json').read_text())
    assert request['email']=='hirokazu601218@govaca.onmicrosoft.com'
    assert request['role']=='CanEdit'
    assert request['app_id']==cfg['target']['app_id']
    deadline=request['started_epoch']+3540
    def budget():
        left=deadline-time.time()
        if left<60: raise RuntimeError('PAUSED_TIME_LIMIT')
        return min(left,45)
    token=subprocess.check_output(['az','account','get-access-token','--resource','https://service.powerapps.com/','--query','accessToken','--output','tsv'],text=True,timeout=budget()).strip()
    root='https://api.powerapps.com/providers/Microsoft.PowerApps/apps/'+cfg['target']['app_id']
    query=urllib.parse.urlencode({'api-version':'2016-11-01','$filter':"environment eq '"+cfg['target']['environment_id']+"'"})
    def api(suffix,body=None):
        req=urllib.request.Request(root+suffix+'?'+query,method='POST' if body is not None else 'GET',
             data=json.dumps(body).encode() if body is not None else None,
             headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=budget()) as response:
            raw=response.read()
            return json.loads(raw) if raw else {}
    before=assignments(api('/permissions'))
    identity=target_id(before,request['email'])
    principals=[p['principal'] for key,p in before.items() if key[0]==identity]
    chosen=next(p for p in principals if str(p.get('email','')).lower()==request['email'])
    action='already_present'
    if (identity,'CanEdit') not in before:
        principal={k:chosen[k] for k in ('id','type','email','tenantId') if k in chosen}
        body={'put':[{'properties':{'roleName':'CanEdit','capabilities':[],
                'NotifyShareTargetOption':'DoNotNotify','principal':principal}}]}
        api('/modifyPermissions',body)
        action='granted'
    for _ in range(12):
        after=assignments(api('/permissions'))
        if (identity,'CanEdit') in after: break
        time.sleep(2)
    else: raise RuntimeError('CanEdit not confirmed; inspect before retry')
    assert {k for k in before if k[0]!=identity}=={k for k in after if k[0]!=identity},'Other principal roles changed'
    result={'state':'APP_EDIT_PERMISSION_VERIFIED','email':request['email'],'app_id':cfg['target']['app_id'],
            'role':'CanEdit','action':action,'other_principal_roles_unchanged':True,
            'dataverse_roles_changed':False,'notification_sent':False}
    out=ROOT/'artifacts/app-edit-permission';out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
