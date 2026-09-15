"""Validated success tags are the durable source for the last good version."""
import json
from decimal import Decimal
import re
import subprocess


def git(root, *args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def successes(root, target):
    records=[]
    for tag in git(root,'tag','--list','v*').splitlines():
        if not re.fullmatch(r'v\d+\.\d{2}',tag): continue
        if git(root,'cat-file','-t',f'refs/tags/{tag}')!='tag': continue
        try:
            receipt=json.loads(git(root,'for-each-ref','--format=%(contents)',f'refs/tags/{tag}'))
        except (ValueError,subprocess.SubprocessError): continue
        if (receipt.get('state')=='TESTED_RELEASE' and receipt.get('version')==tag[1:]
            and receipt.get('target')==target and receipt.get('run_id')
            and receipt.get('main_commit')==git(root,'rev-parse',f'{tag}^{{commit}}')):
            records.append((Decimal(tag[1:]),tag,receipt))
    return sorted(records,key=lambda row:row[0])


def last_good(root, target, bootstrap):
    records=successes(root,target)
    return records[-1][1] if records else bootstrap
