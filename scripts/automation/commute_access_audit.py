"""Read-only, exact-user privilege audit before adding the commute data source."""
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

cfg = json.loads(Path('config/apps/staff-master.json').read_text())
deadline = float(os.environ['WORK_STARTED_EPOCH']) + 3480
url = cfg['target']['dataverse_url'].rstrip('/')
token = subprocess.check_output(['az', 'account', 'get-access-token', '--resource', url, '--query', 'accessToken', '--output', 'tsv'], text=True, timeout=45).strip()

def get(path):
    assert time.time() < deadline, 'PAUSED_TIME_LIMIT'
    req = urllib.request.Request(url + '/api/data/v9.2/' + path, headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)

who = get('WhoAmI')
assert who['OrganizationId'] == '9efe0732-a9b0-f111-8ade-002248f061b1'
query = urllib.parse.urlencode({'$select': 'systemuserid,internalemailaddress,isdisabled', '$filter': "internalemailaddress eq '" + cfg['test_user'] + "'"})
users = get('systemusers?' + query)['value']
assert len(users) == 1 and not users[0]['isdisabled'], 'Resolve active dedicated user first'
uid = users[0]['systemuserid']
privileges = get('systemusers(' + uid + ')/Microsoft.Dynamics.CRM.RetrieveUserPrivileges()')['RolePrivileges']
roles = get('systemusers(' + uid + ')/systemuserroles_association?$select=name,roleid')['value']
tables = {}
for name in ('crb3c_staffbasic', 'crb3c_commute'):
    meta = get("EntityDefinitions(LogicalName='" + name + "')?$select=LogicalName,Privileges")
    needed = next(p for p in meta['Privileges'] if p['PrivilegeType'] == 'Read')
    granted = [p for p in privileges if p['PrivilegeId'] == needed['PrivilegeId']]
    tables[name] = {'read_privilege_id': needed['PrivilegeId'], 'read_privilege_name': needed['Name'], 'granted': bool(granted), 'returned_depths': [p['Depth'] for p in granted]}
result = {'user': cfg['test_user'], 'roles': [{'name': r['name'], 'id': r['roleid']} for r in roles], 'tables': tables, 'permission_changes': False, 'app_changes': False, 'state': 'ACCESS_PRESENT' if tables['crb3c_commute']['granted'] else 'PERMISSION_APPROVAL_REQUIRED'}
Path('artifacts').mkdir(exist_ok=True)
Path('artifacts/commute-access-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
