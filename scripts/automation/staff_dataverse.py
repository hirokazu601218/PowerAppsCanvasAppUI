"""Read-only preflight for the existing isolated Dataverse environment.

No environment, license, permission, table or application mutations.
Never writes access tokens to logs or artifacts.
"""
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]


def main():
    cfg = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
    request = json.loads((ROOT / 'automation/dataverse-run.json').read_text())
    started = datetime.fromisoformat(request['started_at']).timestamp()
    if time.time() - started >= 3600:
        raise RuntimeError('PAUSED_TIME_LIMIT: original Work deadline reached')
    if request['mode'] != 'preflight':
        raise RuntimeError('Only read-only preflight is implemented')
    url = cfg['target']['dataverse_url'].rstrip('/')
    token = subprocess.check_output(
        ['az', 'account', 'get-access-token', '--resource', url,
         '--query', 'accessToken', '--output', 'tsv'], text=True, timeout=60).strip()
    def get(path):
        if time.time() - started >= 3540:
            raise RuntimeError('PAUSED_TIME_LIMIT: stopping before deadline')
        req = urllib.request.Request(url + '/api/data/v9.2/' + path,
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=45) as res:
            return json.load(res)
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


if __name__ == '__main__':
    main()
