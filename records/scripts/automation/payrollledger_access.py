"""Grant only payroll Read to the already-scoped test reader role, if approved."""
import urllib.parse

def ensure_read_access(api,cfg,request,meta,rows,save):
    query=urllib.parse.urlencode({'$select':'systemuserid,internalemailaddress,isdisabled',
                                '$filter':"internalemailaddress eq '"+cfg['test_user']+"'"})
    users=api('systemusers?'+query)['value']
    assert len(users)==1 and not users[0]['isdisabled']
    uid=users[0]['systemuserid']
    roles=api('systemusers('+uid+')/systemuserroles_association?$select=name,roleid')['value']
    matches=[r for r in roles if r['name']=='StaffMaster Test Reader']
    assert len(matches)==1
    rid=matches[0]['roleid']
    direct=api('roles('+rid+')/systemuserroles_association?$select=systemuserid')['value']
    teams=api('roles('+rid+')/teamroles_association?$select=teamid')['value']
    assert len(direct)==1 and direct[0]['systemuserid']==uid and not teams, 'Reader role assignment scope changed'
    metadata=api("EntityDefinitions(LogicalName='crb3c_payrollledger')?$select=LogicalName,Privileges")
    needed=next(p for p in metadata['Privileges'] if p['PrivilegeType']=='Read')
    pid=needed['PrivilegeId']
    def privileges():
        return {r['PrivilegeId']:r for r in api('RetrieveRolePrivilegesRole(RoleId='+rid+')')['RolePrivileges']}
    before=privileges()
    needs_grant=pid not in before or before[pid]['Depth']!='Global'
    proposal={'table':'crb3c_payrollledger','privilege_id':pid,'privilege_name':needed['Name'],
              'depth':'Global','role_id':rid,'role_name':matches[0]['name'],
              'direct_user_count':1,'direct_team_count':0,'needs_grant':needs_grant}
    save('read-proposal.json',proposal)
    if needs_grant:
        assert request['mode']=='seed' and request.get('read_permission_approved') is True, 'Read permission approval missing'
        api('roles('+rid+')/Microsoft.Dynamics.CRM.AddPrivilegesRole','POST',
            {'Privileges':[{'PrivilegeId':pid,'Depth':'Global'}]})
    after=privileges()
    assert after[pid]['Depth']=='Global'
    assert {k:v for k,v in before.items() if k!=pid}=={k:v for k,v in after.items() if k!=pid}, 'Unexpected privilege delta'
    effective=api('systemusers('+uid+')/Microsoft.Dynamics.CRM.RetrieveUserPrivileges()')['RolePrivileges']
    assert any(p['PrivilegeId']==pid and p['Depth']=='Global' for p in effective)
    row_rights=[]
    for row in rows:
        target=urllib.parse.quote(__import__('json').dumps({'@odata.id':meta['EntitySetName']+'('+row['id']+')'}))
        rights=api('systemusers('+uid+')/Microsoft.Dynamics.CRM.RetrievePrincipalAccess(Target=@p1)?@p1='+target)['AccessRights']
        assert 'ReadAccess' in rights
        assert not any(r in rights for r in ('WriteAccess','DeleteAccess','AssignAccess','ShareAccess','AppendAccess','AppendToAccess'))
        row_rights.append({'id':row['id'],'rights':rights})
    result={'state':'READ_ACCESS_VERIFIED','table':'crb3c_payrollledger','role':'StaffMaster Test Reader',
            'permission_changed':needs_grant,'only_payroll_read_changed':True,'depth':'Global',
            'readable_rows':len(row_rights),'rights':row_rights,'billing_changes':False}
    save('read-access.json',result)
    print('READ_ACCESS_VERIFIED',flush=True)
    return result
