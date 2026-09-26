"""Apply only the user's approved T_通勤 Read privilege, then verify exact delta."""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
import commute_access_audit as audit

proposal = json.loads(Path('automation/commute-read-permission-proposal.json').read_text())
assert proposal['approved'] is True
assert proposal['environment_id'] == audit.cfg['target']['environment_id']
assert proposal['target_user'] == audit.cfg['test_user']
assert len(audit.role_scope) == 1 and audit.role_scope[0]['only_target_user']
rid = proposal['existing_role_id']
assert audit.roles[0]['roleid'] == rid and audit.roles[0]['name'] == proposal['existing_role_name']
priv = proposal['proposed_addition']
assert priv['table'] == 'crb3c_commute' and priv['depth'] == 'Global'
assert audit.tables['crb3c_commute']['read_privilege_id'] == priv['privilege_id']
assert audit.tables['crb3c_commute']['read_privilege_name'] == priv['privilege_name']
def privileges():
    rows = audit.get('RetrieveRolePrivilegesRole(RoleId=' + rid + ')')['RolePrivileges']
    return {r['PrivilegeId']: r for r in rows}
before = privileges()
if priv['privilege_id'] not in before or before[priv['privilege_id']]['Depth'] != 'Global':
    assert time.time() < audit.deadline
    body = {'Privileges': [{'PrivilegeId': priv['privilege_id'], 'Depth': 'Global'}]}
    req = urllib.request.Request(audit.url + '/api/data/v9.2/roles(' + rid + ')/Microsoft.Dynamics.CRM.AddPrivilegesRole', data=json.dumps(body).encode(), method='POST', headers={'Authorization': 'Bearer ' + audit.token, 'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as response:
        response.read()
after = privileges()
assert after[priv['privilege_id']]['Depth'] == 'Global'
assert {k: v for k, v in before.items() if k != priv['privilege_id']} == {k: v for k, v in after.items() if k != priv['privilege_id']}, 'Unexpected privilege change'
effective = audit.get('systemusers(' + audit.uid + ')/Microsoft.Dynamics.CRM.RetrieveUserPrivileges()')['RolePrivileges']
assert any(r['PrivilegeId'] == priv['privilege_id'] and r['Depth'] == 'Global' for r in effective)
rows = audit.get('crb3c_commutes?$select=crb3c_commuteid,crb3c_recognitionid')['value']
assert len(rows) == 6
for row in rows:
    target = urllib.parse.quote(json.dumps({'@odata.id': 'crb3c_commutes(' + row['crb3c_commuteid'] + ')'}))
    rights = audit.get('systemusers(' + audit.uid + ')/Microsoft.Dynamics.CRM.RetrievePrincipalAccess(Target=@p1)?@p1=' + target)['AccessRights']
    assert 'ReadAccess' in rights
    assert not any(s in rights for s in ['WriteAccess', 'DeleteAccess', 'AssignAccess', 'ShareAccess'])
result = {'state': 'APPROVED_READ_GRANTED_AND_VERIFIED', 'user': proposal['target_user'], 'role': proposal['existing_role_name'], 'table': priv['table'], 'depth': 'Global', 'only_read_privilege_changed': True, 'readable_fixture_count': len(rows), 'app_changes': False, 'billing_changes': False}
Path('artifacts/commute-read-grant.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
