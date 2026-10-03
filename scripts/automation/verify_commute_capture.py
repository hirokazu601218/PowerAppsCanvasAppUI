"""Read-only verification of parallel report resources and fixed app buttons."""
import base64,hashlib,json,os,re,subprocess,sys,urllib.request,zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def find(o,name):
    if isinstance(o,dict):
        if name in o:return o[name]
        for v in o.values():
            x=find(v,name)
            if x is not None:return x
    if isinstance(o,list):
        for v in o:
            x=find(v,name)
            if x is not None:return x

def normalized(v):
    return re.sub(r'\s+','',str(v))
with zipfile.ZipFile(sys.argv[1]) as z:
    n=next(n for n in z.namelist() if n.replace('\\','/').endswith('Src/scrStaffMasterSearch.pa.yaml'))
    screen=yaml.safe_load(z.read(n))
new=find(yaml.safe_load((ROOT/'src/commute-ledger/v1.02/test-button.paste.yaml').read_text()),'btnCertificateOfficial102')
old=json.loads((ROOT/'records/changes/change-20261003-commute-official/manual-20261004-deployment/old-button.expected.json').read_text())
for name,expected in [('btnCertificateOfficial102',new),('btnCertificate111',old)]:
    actual=find(screen,name)
    assert actual is not None,name+' missing'
    for key,value in expected['Properties'].items():
        assert normalized(actual['Properties'].get(key))==normalized(value),(name,key)
    print(name+': all authored properties MATCH')
url=os.environ['DATAVERSE_URL'].rstrip('/')
token=subprocess.check_output(['az','account','get-access-token','--resource',url,'--query','accessToken','--output','tsv'],text=True).strip()
from urllib.parse import urlencode
for name,digest in [('crb3c_reports/commute-ledger-studio.html','593a5d72d92bbfda05cc225d997676b413af309123bdf4677ea7d4428ded50be'),('new_reports/commute-ledger-official-v102.html','7466bb790056d948a68c08f23872fcaba28a1c3fe6f754d752c9261cf04b0ef1')]:
    query=urlencode({'$select':'name,content','$filter':"name eq '"+name+"'"})
    req=urllib.request.Request(url+'/api/data/v9.2/webresourceset?'+query,headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(req,timeout=60) as res:rows=json.load(res)['value']
    assert len(rows)==1,name
    actual=hashlib.sha256(base64.b64decode(rows[0]['content'])).hexdigest()
    assert actual==digest,name+' hash mismatch'
    print(name+': SHA-256 MATCH '+actual)
