"""One isolated transaction: build, deploy, acceptance tests and verified rollback.

Acceptance fixtures have predeclared remedies. Unrecognized failures stop and are
reported to Work for analysis; this runner never generates code or widens scope.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import xml.etree.ElementTree as ET

import bridge
import policy
import releases

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/automation'
OUT.mkdir(parents=True, exist_ok=True)
CFG = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
MANIFEST = json.loads((ROOT / 'automation/change.json').read_text())
REQUEST = json.loads((ROOT / 'automation/run.json').read_text())
RELEASE = json.loads((ROOT / 'automation/release.json').read_text())
TMP = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'staff-master-transaction'
TMP.mkdir(parents=True, exist_ok=True)
TEST_ROOT = ROOT.parent / 'power-platform-playwright/packages/e2e-tests'
LEDGER = OUT / 'attempts.jsonl'
SUMMARY = {'request': REQUEST, 'commit': os.environ.get('GITHUB_SHA'),
           'run_id': os.environ.get('GITHUB_RUN_ID'), 'target': CFG['target'], 'attempts': []}
TOUCHED = False
RESTORED = False
RESTORE_ATTEMPTED = False
STAGE = 'scope'
GOOD_REF = releases.last_good(ROOT,CFG['target'],RELEASE['last_good_commit'])
SUMMARY['last_good_ref']=GOOD_REF


def event(**row):
    result = policy.append(LEDGER, row)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    if os.environ.get('GH_TOKEN') and ('name' in row or row.get('state') in {'RESTORED','STOPPED','RESTORE_FAILED'}):
        note=OUT/'progress.md'
        note.write_text('Step 8/9 progress\n\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n')
        try:
            subprocess.run(['gh','issue','comment',str(REQUEST['issue']),'--repo',os.environ['GITHUB_REPOSITORY'],
                            '--body-file',str(note)],cwd=ROOT,stdout=subprocess.DEVNULL,timeout=30,check=True)
        except (subprocess.SubprocessError, OSError) as error:
            print(f'Progress comment deferred to final record: {type(error).__name__}',flush=True)
    return result


def command(args, log, cwd=ROOT, env=None):
    print(f'Executing: {args[0]} {args[1] if len(args)>1 else ""}; log={log.name}', flush=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('w') as file:
        result = subprocess.run(args, cwd=cwd, env=env, stdout=file, stderr=subprocess.STDOUT, timeout=900)
    if result.returncode:
        # Logs remain in artifacts; credentials are never command arguments.
        raise RuntimeError(f'{args[0]} failed; see {log.relative_to(OUT)}')


def api(suffix='', method='GET'):
    token = subprocess.check_output(['az','account','get-access-token','--resource',
                                    'https://service.powerapps.com/','--query','accessToken','--output','tsv'], text=True).strip()
    app_id = CFG['target']['app_id']
    env_id = CFG['target']['environment_id']
    url = (f'https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{app_id}{suffix}'
           f'?api-version=2018-10-01&%24filter=environment%20eq%20%27{env_id}%27')
    request = urllib.request.Request(url, method=method, data=b'{}' if method=='POST' else None,
                                    headers={'Authorization':f'Bearer {token}','Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
        return json.loads(data) if data else {}


def pack(root, directory, manifest=None):
    root, directory = Path(root), Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    solution = directory / 'solution'
    shutil.copytree(root / 'powerapps/solution-src', solution)
    matches = list((solution / 'CanvasApps').glob('*.msapp'))
    bridge.require(len(matches)==1, 'expected one Canvas app')
    if manifest is not None:
        result = bridge.build(root, matches[0], manifest)
        (directory/'build.json').write_text(json.dumps(result,indent=2))
        xml = solution/'Other/Solution.xml'
        # Preserve exact XML formatting except the Solution version.
        text = xml.read_text(encoding='utf-8-sig')
        current = ET.fromstring(text).find('SolutionManifest/Version').text
        text = text.replace(f'<Version>{current}</Version>', f"<Version>{manifest['candidate_version']}.0.0</Version>",1)
        xml.write_text(text,encoding='utf-8-sig')
    package = directory/'solution.zip'
    command(['pac','solution','pack','--folder',str(solution),'--zipfile',str(package),
             '--packagetype','Unmanaged'],directory/'pack.log')
    (directory/'package.sha256').write_text(bridge.digest(package.read_bytes())+'\n')
    return package


def deploy(package, directory, root=None, manifest=None):
    global TOUCHED, STAGE
    TOUCHED = True
    STAGE = 'import'
    command(['pac','solution','import','--path',str(package),'--environment',CFG['target']['dataverse_url'],
             '--force-overwrite','--publish-changes'],directory/'import.log')
    STAGE = 'publish'
    api('/publish','POST')
    info = {}
    for _ in range(12):
        info = api()
        props=info.get('properties',{})
        if props.get('status')=='Ready' and props.get('lastDraftVersion') and props['lastDraftVersion']==props.get('lastPublishTime'):
            break
        time.sleep(5)
    else:
        raise RuntimeError('Canvas publish did not reach Ready')
    props=info['properties']
    app_url=props.get('appOpenUri','')
    prefix=f"https://apps.powerapps.com/play/e/{CFG['target']['environment_id']}/a/{CFG['target']['app_id']}?"
    bridge.require(app_url.startswith(prefix), 'published App ID/environment mismatch')
    (directory/'published.json').write_text(json.dumps({
        'app_id':CFG['target']['app_id'],'version':props['lastPublishTime'],
        'draft_version':props['lastDraftVersion'],'status':props['status']},indent=2))
    STAGE='readback'
    download=directory/'readback.msapp'
    command(['pac','canvas','download','--name',CFG['target']['app_id'],'--file-name',str(download),
             '--environment',CFG['target']['dataverse_url'],'--overwrite'],directory/'readback.log')
    if root is not None:
        result=bridge.verify_download(download,root,manifest or {'changes':[]})
        (directory/'readback.json').write_text(json.dumps(result,indent=2))
    return app_url


def test_ui(directory, url, expected):
    global STAGE
    result={}
    for kind, filename in [('change_test','approved-property.test.ts'),('p0','staff-master-p0.test.ts')]:
        STAGE=kind
        dest=directory/kind
        dest.mkdir(parents=True,exist_ok=True)
        screenshot_root=TEST_ROOT/'test-results'
        if screenshot_root.exists():
            for screenshot in screenshot_root.glob('*.png'): screenshot.unlink()
        env={**os.environ,'CANVAS_APP_URL':url,'EXPECTED_LABEL':expected,
             'OUTPUT_DIRECTORY':str(dest),'RETRIES':'0'}
        with (dest/'playwright.log').open('w') as file:
            proc=subprocess.run(['npx','playwright','test',f'tests/northwind/canvas/{filename}',
                                 '--project=canvas-app','--retries=0','--reporter=line,json',f'--output={dest}/artifacts'],
                                cwd=TEST_ROOT,env={**env,'PLAYWRIGHT_JSON_OUTPUT_NAME':str(dest/'results.json')},
                                stdout=file,stderr=subprocess.STDOUT,timeout=300)
        for screenshot in screenshot_root.glob('*.png'):
            shutil.copy2(screenshot,dest/screenshot.name)
        result[kind]='success' if proc.returncode==0 else 'failure'
        event(stage=kind,outcome=result[kind],attempt=directory.name)
    return result


def actual_failure(name):
    report=json.loads((OUT/name/'change_test/results.json').read_text())
    messages=[]
    def visit(value):
        if isinstance(value,dict):
            for err in value.get('errors',[]):
                if isinstance(err,dict) and err.get('message'):
                    messages.append(err['message'])
            for child in value.values(): visit(child)
        elif isinstance(value,list):
            for child in value: visit(child)
    visit(report)
    message=next((m for m in messages if 'AUT-META-001: approved header value' in m),None)
    bridge.require(message is not None, 'fixture failed for an unexpected reason')
    # Preserve the actual assertion, locator, expected state and timeout; omit its repeated call log.
    error=policy.normalize(message).split('Call log:')[0].strip()
    return {'case_id':'AUT-META-001','stage':'change_test','error':error}


def attempt(name, fixture_formula=None):
    global RESTORED, STAGE
    RESTORED=False
    directory=OUT/name
    root=TMP/name
    root.mkdir()
    for path in ('config','powerapps','automation'):
        shutil.copytree(ROOT/path,root/path)
    manifest=copy.deepcopy(MANIFEST)
    if fixture_formula:
        manifest=bridge.retarget_fixture(root,manifest,fixture_formula)
    STAGE='build'
    package=pack(root,directory,manifest)
    url=deploy(package,directory,root,manifest)
    checks={'build':'success','auth':'success','import':'success','publish':'success','readback':'success'}
    checks.update(test_ui(directory,url,MANIFEST['acceptance']['expected_label']))
    row={'name':name,'gates':checks,'promotable':policy.promotion(checks),
         'effective_edit':manifest['changes'],'package_sha256':bridge.digest(package.read_bytes())}
    SUMMARY['attempts'].append(row)
    event(**row)
    return row


def restore():
    global RESTORED,RESTORE_ATTEMPTED,STAGE
    bridge.require(not RESTORE_ATTEMPTED,'RESTORE_FAILED: restoration already attempted')
    RESTORE_ATTEMPTED=True
    STAGE='restore'
    directory=OUT/'restoration'
    directory.mkdir(exist_ok=True)
    root=TMP/'last-good'
    ref=GOOD_REF
    sha=subprocess.check_output(['git','rev-parse',f'{ref}^{{commit}}'],text=True,cwd=ROOT).strip()
    SUMMARY['restored_commit']=sha
    if not root.exists():
        root.mkdir()
        tar=TMP/'last-good.tar'
        with tar.open('wb') as out:
            subprocess.run(['git','archive',sha],cwd=ROOT,stdout=out,check=True)
        with tarfile.open(tar) as archive:
            archive.extractall(root,filter='data')
    manifest_path=root/'automation/change.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    package=pack(root,directory,manifest)
    url=deploy(package,directory,root,manifest)
    expected=manifest['acceptance']['expected_label'] if manifest else 'v1.11 ／ B案・架空25名'
    checks=test_ui(directory,url,expected)
    bridge.require(all(x=='success' for x in checks.values()),'RESTORE_FAILED: restored tests did not pass')
    RESTORED=True
    SUMMARY['restoration']={'state':'RESTORED','commit':sha,'gates':checks}
    event(stage='restore',state='RESTORED',commit=sha)


def acceptance():
    # BAS-02: a known bad app value, unchanged UI expectation, distinct approved repair.
    bad=attempt('repair-defect','="自動修復試験・誤表示A"')
    bridge.require(bad['gates']['change_test']=='failure' and bad['gates']['p0']=='success',
                   'intentional defect must fail only the change test')
    failure=actual_failure('repair-defect')
    fp=policy.fingerprint(failure['case_id'],failure['stage'],failure['error'])
    remedy={'id':'apply-approved-source-formula','edit':MANIFEST['changes']}
    decision=policy.decide([],failure,[remedy])
    bridge.require(decision['state']=='REPAIRING','repair was not authorized')
    event(fingerprint=fp,failure=failure,**decision)
    fixed=attempt('repair-success')
    bridge.require(fixed['promotable'],'repair did not satisfy both tests')
    # BAS-03: two distinct remedies for the same failure; no rename can reset history.
    stop_history=[]
    for index, formula in enumerate(('="停止試験・誤表示A"','="停止試験・誤表示B"'),1):
        remedy={'id':f'stop-remedy-{index}','edit':{'control':'lblMeta111','property':'Text','formula':formula}}
        decision=policy.decide(stop_history,failure,[remedy])
        bridge.require(decision['state']=='REPAIRING','distinct remedy was not permitted')
        row=attempt(f'stop-defect-{index}',formula)
        bridge.require(row['gates']['change_test']=='failure' and row['gates']['p0']=='success',
                       'stop fixture must fail only the change test')
        failure=actual_failure(f'stop-defect-{index}')
        current_fp=policy.fingerprint(failure['case_id'],failure['stage'],failure['error'])
        if stop_history:
            bridge.require(current_fp==stop_history[-1]['fingerprint'],'stop fixture causes differ')
        stop_history.append(event(fingerprint=current_fp,failure=failure,**decision))
    exhausted=policy.decide(stop_history,failure,[remedy])
    bridge.require(exhausted['state']=='STOPPED','used remedy was repeated')
    event(fingerprint=fp,**exhausted)
    restore()
    SUMMARY['state']='ACCEPTANCE_PASSED'
    SUMMARY['scenarios']={'BAS-02':'live repair passed','BAS-03':'live stop and restoration passed',
                          'BAS-04':'unit tested: auth fails closed','BAS-05':'unit tested: scope guard',
                          'BAS-06':'unit tested: P0 failure denies promotion','BAS-07':'live change-only failure',
                          'BAS-08':'unit tested: restore failure state'}


try:
    bridge.require(REQUEST.get('approved') is True,'request not approved')
    bridge.require(MANIFEST['target']==CFG['target'],'manifest target mismatch')
    bridge.require(os.environ.get('POWER_PLATFORM_TEST_ENVIRONMENT_URL')==CFG['target']['dataverse_url'],
                   'workflow target mismatch')
    bridge.require(os.environ.get('POWER_PLATFORM_TARGET_APP_ID')==CFG['target']['app_id'],
                   'workflow App ID mismatch')
    baseline_delta=subprocess.check_output(['git','diff',CFG['bootstrap_good_commit'],'HEAD',
                                            '--','powerapps/solution-src'],cwd=ROOT,text=True)
    bridge.require(not baseline_delta,'unapproved Solution component or connection change')
    STAGE='auth'
    command(['pac','auth','create','--name','staff-master-oidc','--githubFederated','--tenant',CFG['tenant_id'],
             '--applicationId',CFG['client_id'],'--environment',CFG['target']['dataverse_url']],OUT/'auth.log')
    if REQUEST['mode']=='acceptance':
        bridge.require(REQUEST['issue']==7,'acceptance fixtures are restricted to setup Issue 7')
        acceptance()
    elif REQUEST['mode']=='release':
        row=attempt('release-candidate')
        bridge.require(row['promotable'],'candidate failed: Work must analyze and propose a new remedy')
        SUMMARY['state']='RELEASE_CANDIDATE_PASSED'
    elif REQUEST['mode']=='restore':
        restore()
        SUMMARY['state']='RESTORED'
    else:
        raise bridge.GateError('unsupported run mode')
except Exception as error:
    SUMMARY['state']='BLOCKED' if not TOUCHED else 'FAILED'
    SUMMARY['failure']={'stage':STAGE,'error':str(error)}
    event(state=SUMMARY['state'],**SUMMARY['failure'])
    if RESTORE_ATTEMPTED and not RESTORED:
        SUMMARY['state']='RESTORE_FAILED'
        SUMMARY['restore_error']=str(error)
    elif TOUCHED and not RESTORED:
        try:
            restore()
            SUMMARY['state']='RESTORED_AFTER_FAILURE'
        except Exception as restore_error:
            SUMMARY['state']='RESTORE_FAILED'
            SUMMARY['restore_error']=str(restore_error)
            event(state='RESTORE_FAILED',error=str(restore_error))
    raise
finally:
    (OUT/'result.json').write_text(json.dumps(SUMMARY,ensure_ascii=False,indent=2)+'\n')
    result_text=f"## Staff Master automation: {SUMMARY.get('state','INCOMPLETE')}\n\n"
    result_text+=f"Commit: {SUMMARY['commit']}\n\n"
    result_text+='| Attempt | Change test | P0 | Promotable |\n|---|---|---|---|\n'
    for row in SUMMARY['attempts']:
        result_text+=f"| {row['name']} | {row['gates']['change_test']} | {row['gates']['p0']} | {row['promotable']} |\n"
    result_text+=f"\nRestoration: {SUMMARY.get('restoration',{}).get('state','not required')}\n"
    result_text+=f"\n[Actions run](https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{SUMMARY['run_id']})\n"
    (OUT/'summary.md').write_text(result_text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as file: file.write(result_text)
