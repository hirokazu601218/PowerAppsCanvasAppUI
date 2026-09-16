"""Staged setup in the existing isolated Dataverse environment.

preflight reads only; provision creates the approved table/key; seed5 adds fixtures.
No license, identity, access-role or app changes. Tokens are never logged.
"""
import json
import os
import subprocess
import time
import urllib.request
import urllib.error
import uuid
from staff_schema import table, attributes, payload, FIELDS
from staff_data_contract import validate
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]


def main():
    cfg = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
    request = json.loads((ROOT / 'automation/dataverse-run.json').read_text())
    started = datetime.fromisoformat(request['started_at']).timestamp()
    if time.time() - started >= 3600:
        raise RuntimeError('PAUSED_TIME_LIMIT: original Work deadline reached')
    if request['mode'] not in ('preflight','provision','seed5'):
        raise RuntimeError('Unsupported stage')
    url = cfg['target']['dataverse_url'].rstrip('/')
    token = subprocess.check_output(
        ['az', 'account', 'get-access-token', '--resource', url,
         '--query', 'accessToken', '--output', 'tsv'], text=True, timeout=60).strip()
    def api(path, method='GET', body=None):
        if time.time() - started >= 3540:
            raise RuntimeError('PAUSED_TIME_LIMIT: stopping before deadline')
        req = urllib.request.Request(url + '/api/data/v9.2/' + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json',
                     'Content-Type':'application/json','MSCRM.SolutionUniqueName':cfg['solution_name']})
        try:
            with urllib.request.urlopen(req, timeout=180 if method != 'GET' else 45) as res:
                data=res.read()
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as error:
            # Dataverse error code/message only; no headers, credentials or payload dump.
            data=json.loads(error.read())
            raise RuntimeError(str(error.code)+': '+data.get('error',{}).get('message','Dataverse error')) from None
    get=api
    result = {'stage': 3, 'mode': 'read-only', 'checked_at': datetime.now(timezone.utc).isoformat()}
    who = get('WhoAmI')
    result['identity_available'] = bool(who.get('UserId'))
    result['organization_id'] = who.get('OrganizationId')
    sol = get("solutions?$select=uniquename,ismanaged&$filter=uniquename%20eq%20'StaffMasterAutomation'&$expand=publisherid($select=customizationprefix)")
    result['solution'] = sol['value']
    if len(sol['value']) != 1 or sol['value'][0]['ismanaged']:
        raise RuntimeError('Expected existing unmanaged solution')
    if sol['value'][0]['publisherid']['customizationprefix'] != 'crb3c':
        raise RuntimeError('Publisher mismatch')
    tables = get("EntityDefinitions?$select=LogicalName,MetadataId,OwnershipType&$filter=LogicalName%20eq%20'crb3c_staffbasic'")
    result['existing_table'] = tables['value']
    org = get('organizations?$select=languagecode')
    result['base_language'] = org['value'][0]['languagecode']
    result['state'] = 'PREFLIGHT_PASSED'
    out = ROOT / 'artifacts/dataverse'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'preflight.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    summary = '工程3: Dataverse読取接続・既存ソリューション・発行者の確認成功。変更なし。\n'
    (out / 'summary.md').write_text(summary)
    print(json.dumps(result, ensure_ascii=False))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write(summary)
    if request['mode']=='preflight': return
    name='crb3c_staffbasic'
    entity="EntityDefinitions(LogicalName='"+name+"')"
    if not tables['value']:
        if request['mode']!='provision': raise RuntimeError('Table must be provisioned first')
        print('Stage 4: creating approved table',flush=True)
        api('EntityDefinitions','POST',table(result['base_language']))
    meta=get(entity+'?$select=LogicalName,OwnershipType,PrimaryNameAttribute,PrimaryIdAttribute,EntitySetName&$expand=Attributes')
    assert meta['OwnershipType']=='UserOwned'
    assert meta['PrimaryNameAttribute']=='crb3c_staffnumber'
    actual={a['LogicalName']:a for a in meta['Attributes']}
    for expected in attributes(result['base_language']):
        field=actual[expected['SchemaName'].lower()]
        assert field['RequiredLevel']['Value']==expected['RequiredLevel']['Value'], field['LogicalName']
        expected_type=expected['@odata.type'].split('.')[-1].replace('AttributeMetadata','')
        assert field['AttributeType']==expected_type, field['LogicalName']
        for prop in ('MaxLength','MinValue','MaxValue','Format'):
            if prop in expected: assert field[prop]==expected[prop], (field['LogicalName'],prop)
        if 'DateTimeBehavior' in expected:
            assert field['DateTimeBehavior']['Value']=='DateOnly'
        if 'OptionSet' in expected:
            option=get(entity+"/Attributes(LogicalName='"+field['LogicalName']+"')/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$expand=OptionSet")
            observed=[(v['Value'],v['Label']['LocalizedLabels'][0]['Label']) for v in option['OptionSet']['Options']]
            wanted=[(v['Value'],v['Label']['LocalizedLabels'][0]['Label']) for v in expected['OptionSet']['Options']]
            assert observed==wanted, field['LogicalName']
    keys=get(entity+'/Keys')['value']
    keyname='crb3c_staffnumber_key'
    if not any(k['SchemaName']==keyname for k in keys):
        api(entity+'/Keys','POST',{'SchemaName':keyname,'KeyAttributes':['crb3c_staffnumber'],
            'DisplayName':{'LocalizedLabels':[{'Label':'職員番号一意キー','LanguageCode':result['base_language']}]}})
    for _ in range(30):
        keys=get(entity+'/Keys')['value']
        key=next(k for k in keys if k['SchemaName']==keyname)
        if key['EntityKeyIndexStatus']=='Active': break
        if key['EntityKeyIndexStatus']=='Failed': raise RuntimeError('Alternate key index failed')
        time.sleep(2)
    else: raise RuntimeError('Alternate key not yet active; stop before data writes')
    api('PublishXml','POST',{'ParameterXml':'<importexportxml><entities><entity>'+name+'</entity></entities></importexportxml>'})
    result.update(stage=4,mode=request['mode'],state='TABLE_VERIFIED',columns=24,key_state='Active',entity_set=meta['EntitySetName'])
    (out/'table-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False),flush=True)
    if request['mode']=='provision': return
    rows=json.loads((ROOT/'tests/fixtures/staff-basic-5.json').read_text())
    validate(rows)
    for row in rows:
        record=payload(row)
        record_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'staff-basic-fixture/'+row['staffnumber']))
        existing=get(meta['EntitySetName']+"?$filter=crb3c_staffnumber%20eq%20'"+row['staffnumber']+"'")['value']
        if not existing:
            record[meta['PrimaryIdAttribute']]=record_id
            api(meta['EntitySetName'],'POST',record)
        actual_row=get(meta['EntitySetName']+'('+record_id+')')
        for key,value in record.items():
            actual_value=actual_row.get(key)
            if isinstance(value,str) and value.endswith('T00:00:00Z'):
                assert actual_value[:10]==value[:10],key
            else: assert actual_value==value,key
    result.update(stage=5,state='SEED5_VERIFIED',fixture_count=len(rows))
    (out/'seed-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
