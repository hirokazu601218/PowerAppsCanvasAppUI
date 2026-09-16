"""Tag only a merged tree whose exact candidate passed all deployment gates."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from decimal import Decimal

import policy
import readme_release
from releases import git, successes

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/release'
OUT.mkdir(parents=True,exist_ok=True)
REPO=os.environ['GITHUB_REPOSITORY']
SHA=os.environ['GITHUB_SHA']
CFG=json.loads((ROOT/'config/apps/staff-master.json').read_text())
CHANGE=json.loads((ROOT/'automation/change.json').read_text())
REQUEST=json.loads((ROOT/'automation/run.json').read_text())
RELEASE=json.loads((ROOT/'automation/release.json').read_text())


def require(value,message):
    if not value: raise RuntimeError(message)


def api(path):
    return json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/{path}'],cwd=ROOT,text=True))


require(os.environ['GITHUB_REF']=='refs/heads/main','only main may receive a success tag')
require(REQUEST['mode']=='release' and REQUEST.get('approved') is True,'release was not requested')
parents=git(ROOT,'show','-s','--format=%P',SHA).split()
require(len(parents)==2,'expected the reviewed PR merge commit')
candidate=parents[1]
require(git(ROOT,'rev-parse',f'{candidate}^{{tree}}')==git(ROOT,'rev-parse',f'{SHA}^{{tree}}'),
        'merged tree differs from tested candidate; rerun the candidate')
runs=api(f'actions/runs?head_sha={candidate}&per_page=100')['workflow_runs']
runs=[r for r in runs if r['path']=='.github/workflows/staff-master-transaction.yml'
      and r['head_sha']==candidate and r['event']=='push']
require(runs,'candidate has no transaction run')
run=max(runs,key=lambda r:r['id'])
require(run['status']=='completed' and run['conclusion']=='success','latest candidate run did not succeed')
name=f"staff-master-transaction-{run['id']}-{run['run_attempt']}"
evidence=OUT/'candidate'
subprocess.run(['gh','run','download',str(run['id']),'--repo',REPO,'--name',name,'--dir',str(evidence)],
               cwd=ROOT,check=True,timeout=180)
result=json.loads((evidence/'result.json').read_text())
require(result['state']=='RELEASE_CANDIDATE_PASSED' and result['commit']==candidate,
        'evidence does not attest the candidate')
require(result['target']==CFG['target'] and result['request']==REQUEST,'evidence scope mismatch')
require(len(result['attempts'])==1,'unexpected release attempt history')
attempt=result['attempts'][0]
require(attempt['name']=='release-candidate' and policy.promotion(attempt['gates']),
        'one or more required gates did not pass')
package=evidence/'release-candidate/solution.zip'
require(hashlib.sha256(package.read_bytes()).hexdigest()==attempt['package_sha256'],'package digest mismatch')
published=json.loads((evidence/'release-candidate/published.json').read_text())
require(published['app_id']==CFG['target']['app_id'] and published['status']=='Ready'
        and published['version']==published['draft_version'],'publish evidence mismatch')
version=CHANGE['candidate_version']
tag=f'v{version}'
records=successes(ROOT,CFG['target'])
existing=[receipt for _,name,receipt in records if name==tag]
if existing:
    receipt=existing[0]
    require(receipt['main_commit']==SHA and receipt['candidate_commit']==candidate,'tag already belongs to another release')
else:
    previous=records[-1][0] if records else Decimal(RELEASE['last_success_version'])
    require(Decimal(version)==previous+Decimal('0.01'),'success version must increment by 0.01')
    require(not git(ROOT,'tag','--list',tag),'an unverified tag already uses this version')
    receipt={'schema':1,'state':'TESTED_RELEASE','version':version,'main_commit':SHA,
             'candidate_commit':candidate,'run_id':run['id'],'run_attempt':run['run_attempt'],
             'issue':REQUEST['issue'],'target':CFG['target'],'published':published,
             'package_sha256':attempt['package_sha256'],'gates':attempt['gates']}
    (OUT/'release.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=ROOT,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=ROOT,check=True)
    subprocess.run(['git','tag','-a',tag,SHA,'-F',str(OUT/'release.json')],cwd=ROOT,check=True)
    subprocess.run(['git','push','origin',f'refs/tags/{tag}'],cwd=ROOT,check=True)
(OUT/'release.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
readme_result=readme_release.publish(ROOT,receipt,REPO)
readme_message=f"README update: **{readme_result['state']}**.\n"
if readme_result['state']=='PENDING_WORK_PR':
    print('::warning::Release is verified; README still requires the authorized Work PR handoff.')
    readme_message+=(f"Work must finish the generated branch `{readme_result['branch']}` "
                     f"at `{readme_result['head']}` through a documentation PR. "
                     "Do not report the entire request complete until main README is verified.\n")
elif readme_result.get('pr'):
    readme_message+=f"Documentation PR: {readme_result['pr']}\n"
message=(f"Success version **{tag}** is finalized.\n\n"
         f"- [Verified transaction](https://github.com/{REPO}/actions/runs/{run['id']})\n"
         f"- [Success tag](https://github.com/{REPO}/tree/{tag})\n"
         f"- Main commit: `{SHA}`\n- Candidate commit: `{candidate}`\n"
         f"- Published isolated App ID: `{published['app_id']}`\n"
         f"- Change acceptance and existing P0: passed\n"
         f"- Solution SHA-256: `{attempt['package_sha256']}`\n\n"
         f"{readme_message}\n"
         "The annotated tag stores the permanent release receipt. Detailed artifacts are retained for 14 days.\n")
(OUT/'summary.md').write_text(message)
subprocess.run(['gh','issue','comment',str(REQUEST['issue']),'--repo',REPO,'--body-file',str(OUT/'summary.md')],
               cwd=ROOT,check=True,timeout=60)
with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as file: file.write(message)
