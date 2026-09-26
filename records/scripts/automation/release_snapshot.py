"""Verify a README-corrected release without widening the tested app payload."""
import copy
import hashlib
import json
import re
import subprocess

import policy

START='<!-- staff-master-release:start -->'
END='<!-- staff-master-release:end -->'


def git(root, *args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def read(root, ref, path):
    return subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=root)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root, receipt, release_commit):
    require(receipt.get('schema')==2 and receipt.get('state')=='TESTED_RELEASE','invalid snapshot receipt')
    require(policy.promotion(receipt.get('gates',{})),'all seven gates must pass')
    version=receipt['version']
    require(re.fullmatch(r'\d+\.\d{2}',version),'invalid version')
    require(receipt.get('release_commit')==release_commit,'tag and release commit differ')
    main=receipt['main_commit']; candidate=receipt['candidate_commit']
    require(git(root,'rev-parse',f'{main}^{{tree}}')==git(root,'rev-parse',f'{candidate}^{{tree}}'),
            'tested candidate and main trees differ')
    subprocess.run(['git','merge-base','--is-ancestor',main,release_commit],cwd=root,check=True)
    changed=set(git(root,'diff','--name-only',main,release_commit).splitlines())
    require(changed<={'README.md'},'release snapshot changed files other than README.md')
    manifest=json.loads(read(root,release_commit,'automation/change.json'))
    require(manifest['candidate_version']==version,'manifest and release versions differ')
    raw=read(root,release_commit,'README.md')
    require(hashlib.sha256(raw).hexdigest()==receipt['readme_sha256'],'README digest differs')
    text=raw.decode('utf-8')
    require(text.count(START)==text.count(END)==1 and text.index(START)<text.index(END),'invalid README markers')
    block=text.split(START,1)[1].split(END,1)[0]
    labels=re.findall(r'^最新成功版：\*\*\[v([^\]]+)\]\(([^)]+)\)',block,re.M)
    require(labels==[(version,f'https://github.com/{receipt["repository"]}/tree/v{version}')],
            'README and tag versions differ')
    require(f'https://github.com/{receipt["repository"]}/actions/runs/{receipt["run_id"]}' in block,
            'README verification run differs')
    return {'state':'VERIFIED','version':version,'changed_files':sorted(changed),
            'main_commit':main,'candidate_commit':candidate,'release_commit':release_commit,
            'readme_sha256':receipt['readme_sha256']}


def create_receipt(root, tested_receipt, release_commit, repository, readme_branch):
    receipt=copy.deepcopy(tested_receipt)
    receipt.update(schema=2,repository=repository,release_commit=release_commit,
                   readme_branch=readme_branch,
                   readme_sha256=hashlib.sha256(read(root,release_commit,'README.md')).hexdigest())
    verify(root,receipt,release_commit)
    return receipt
