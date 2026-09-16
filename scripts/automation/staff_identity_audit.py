"""Read-only identity and app-role audit. Never logs credentials or raw app metadata."""
import json, subprocess, urllib.request, urllib.parse, os, time
from pathlib import Path

def main():
    deadline=float(os.environ['WORK_STARTED_EPOCH'])+3540
    def remaining():
        r=deadline-time.time()
        if r<10: raise RuntimeError('PAUSED_TIME_LIMIT')
        return min(45,r)
    cfg=json.loads(Path('config/apps/staff-master.json').read_text())
    def token(resource):
        return subprocess.check_output(['az','account','get-access-token','--resource',resource,'--query','accessToken','--output','tsv'],text=True,timeout=remaining()).strip()
    def get(url,bearer):
        req=urllib.request.Request(url,headers={'Authorization':'Bearer '+bearer,'Accept':'application/json'},method='GET')
        with urllib.request.urlopen(req,timeout=remaining()) as response: return json.load(response)
    dv=cfg['target']['dataverse_url'].rstrip('/')
    dvtoken=token(dv)
    base=dv+'/api/data/v9.2/'
    who=get(base+'WhoAmI',dvtoken)
    user=get(base+"systemusers("+who['UserId']+")?$select=fullname,applicationid",dvtoken)
    assert user['applicationid'].lower()==cfg['client_id'].lower(), 'Unexpected automation identity'
    query=urllib.parse.urlencode({'$select':'azureactivedirectoryobjectid,fullname','$filter':"internalemailaddress eq '"+cfg['test_user']+"'"})
    users=get(base+'systemusers?'+query,dvtoken)['value']
    assert len(users)==1,'Test user resolution not unique'
    principal=users[0]['azureactivedirectoryobjectid'].lower()
    appbase='https://api.powerapps.com/providers/Microsoft.PowerApps/apps/'+cfg['target']['app_id']
    filt={'api-version':'2016-11-01','$filter':"environment eq '"+cfg['target']['environment_id']+"'"}
    apptoken=token('https://service.powerapps.com/')
    permissions=get(appbase+'/permissions?'+urllib.parse.urlencode(filt),apptoken)
    roles=[]
    def walk(obj):
        if isinstance(obj,dict):
            p=obj.get('properties',obj)
            if isinstance(p,dict) and isinstance(p.get('principal'),dict):
                if str(p['principal'].get('id','')).lower()==principal and p.get('roleName'):
                    roles.append(p['roleName'])
            for value in obj.values(): walk(value)
        elif isinstance(obj,list):
            for value in obj: walk(value)
    walk(permissions)
    rows=get(base+'crb3c_staffbasics?'+urllib.parse.urlencode({'$select':'crb3c_staffnumber','$filter':"startswith(crb3c_staffnumber,'0099000000')",'$top':'26'}),dvtoken)['value']
    result={'state':'READ_ONLY_AUDIT_PASSED','automation_name':user['fullname'],'automation_application_id_matches':True,'test_user':cfg['test_user'],'test_user_app_roles':sorted(set(roles)),'fixture_rows_visible_to_automation':len(rows),'permission_changes':False,'app_changes':False}
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/identity-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
