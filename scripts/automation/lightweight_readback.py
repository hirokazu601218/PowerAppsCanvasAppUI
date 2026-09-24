"""Read-only capture of the existing stable Canvas baseline; never deploy."""
import hashlib,json,subprocess,urllib.request,zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[2]
cfg=json.loads((root/'config/apps/staff-master.json').read_text())
out=root/'artifacts/lightweight-readback'
out.mkdir(parents=True,exist_ok=True)
assert cfg['target']['app_id']=='362ac991-eead-4f07-8373-afdb3ebfdba1'
assert cfg['target']['environment_id']=='68e00049-b7e5-eda6-9888-9a3cc493c5be'
result={'operation':'read_only','target':cfg['target']['app_id']}
try:
 token=subprocess.check_output(['az','account','get-access-token','--resource','https://service.powerapps.com/','--query','accessToken','--output','tsv'],text=True).strip()
 url=f"https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{cfg['target']['app_id']}?api-version=2018-10-01&%24filter=environment%20eq%20%27{cfg['target']['environment_id']}%27"
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+token}),timeout=90) as response:
  info=json.load(response)
 p=info['properties']
 result['metadata']={k:p.get(k) for k in ['displayName','status','lastDraftVersion','lastPublishTime']}
 with (out/'pac.log').open('w') as log:
  subprocess.run(['pac','auth','create','--name','lightweight-readback','--githubFederated','--tenant',cfg['tenant_id'],'--applicationId',cfg['client_id'],'--environment',cfg['target']['dataverse_url']],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
  subprocess.run(['pac','canvas','download','--name',cfg['target']['app_id'],'--file-name',str(out/'baseline.msapp'),'--environment',cfg['target']['dataverse_url'],'--overwrite'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
 data=(out/'baseline.msapp').read_bytes()
 result['sha256']=hashlib.sha256(data).hexdigest()
 with zipfile.ZipFile(out/'baseline.msapp') as z:
  names=[n for n in z.namelist() if n.replace('\\','/').startswith('Src/') and n.endswith('.pa.yaml')]
  result['source_hashes']={n.replace('\\','/'):hashlib.sha256(z.read(n)).hexdigest() for n in names}
 expected=json.loads((root/'automation/lightweight-expected.json').read_text())
 assert expected['app_id']==cfg['target']['app_id'] and expected['environment_id']==cfg['target']['environment_id']
 actual={k:v for k,v in result['source_hashes'].items() if not k.endswith('/_EditorState.pa.yaml')}
 result['source_match']=actual==expected['source_hashes']
 assert result['source_match'], 'Downloaded published source does not match verified lightweight candidate'
 result['status']='success'
except Exception as error:
 result['status']='blocked'
 result['error_type']=type(error).__name__
 result['http_status']=getattr(error,'code',None)
 raise
finally:
 (out/'result.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result),flush=True)
