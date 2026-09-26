"""One authorized README-only correction; archive the old tag atomically."""
import json
import os
from pathlib import Path
import subprocess

import readme_release
import release_snapshot
from releases import git

REPO='hirokazu601218/PowerAppsCanvasAppUI'
TAG='v1.14'
OLD_TAG='5137c995c2760e9da94f6ec4d82779054eee5e89'
OLD_MAIN='d0809b9f32325c37a86ab0265c26e04aaa0f1717'
ARCHIVE='archive/v1.14-before-readme-fix'
ISSUE=29


def main():
    root=Path(__file__).resolve().parents[2]
    out=root/'artifacts/tag-documentation-repair';out.mkdir(parents=True,exist_ok=True)
    require=release_snapshot.require
    require(os.environ['GITHUB_REPOSITORY']==REPO,'wrong repository')
    require(os.environ['GITHUB_REF']=='refs/heads/main','repair only after PR merge to main')
    obj=git(root,'rev-parse',f'refs/tags/{TAG}')
    receipt=json.loads(git(root,'for-each-ref','--format=%(contents)',f'refs/tags/{TAG}'))
    if obj!=OLD_TAG:
        require(receipt.get('documentation_correction',{}).get('previous_tag_object')==OLD_TAG,
                'v1.14 changed unexpectedly; refusing overwrite')
        check=release_snapshot.verify(root,receipt,git(root,'rev-parse',f'{TAG}^{{commit}}'))
        require(git(root,'rev-parse',f'refs/tags/{ARCHIVE}')==OLD_TAG,'archive differs')
        (out/'verification.json').write_text(json.dumps(check,indent=2)+'\n')
        print('v1.14 is already corrected and verified; no tag write')
        return
    require(receipt['main_commit']==OLD_MAIN and receipt['version']=='1.14','unexpected original receipt')
    require(git(root,'rev-parse',f'{TAG}^{{commit}}')==OLD_MAIN,'unexpected original target')
    (out/'original-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # Freeze all original files; only the README release block may change.
    subprocess.run(['git','checkout','--detach',OLD_MAIN],cwd=root,check=True)
    prepared=readme_release.prepare(root,receipt,REPO)
    require(prepared['state']=='PREPARED','expected a README correction commit')
    corrected=release_snapshot.create_receipt(root,receipt,prepared['head'],REPO,prepared['branch'])
    corrected['documentation_correction']={'issue':ISSUE,'previous_tag_object':OLD_TAG,
        'archive_ref':ARCHIVE,'workflow_run':os.environ['GITHUB_RUN_ID'],
        'reason':'README version was updated after tagging; app payload unchanged'}
    check=release_snapshot.verify(root,corrected,prepared['head'])
    require(check['changed_files']==['README.md'],'correction must change only README')
    (out/'verification.json').write_text(json.dumps(check,indent=2)+'\n')
    file=out/'corrected-receipt.json';file.write_text(json.dumps(corrected,indent=2)+'\n')
    existing=git(root,'tag','--list',ARCHIVE)
    if existing:
        require(git(root,'rev-parse',f'refs/tags/{ARCHIVE}')==OLD_TAG,'archive already has a different object')
    else:
        subprocess.run(['git','update-ref',f'refs/tags/{ARCHIVE}',OLD_TAG],cwd=root,check=True)
    subprocess.run(['git','tag','-f','-a',TAG,prepared['head'],'-F',str(file)],cwd=root,check=True)
    # Both backup and correction succeed together; an unexpected remote change stops both.
    subprocess.run(['git','push','--atomic',f'--force-with-lease=refs/tags/{TAG}:{OLD_TAG}',
                    'origin',f'refs/tags/{ARCHIVE}',f'refs/tags/{TAG}'],cwd=root,check=True)
    remote=git(root,'ls-remote','origin',f'refs/tags/{TAG}',f'refs/tags/{ARCHIVE}')
    refs={line.split()[1]:line.split()[0] for line in remote.splitlines()}
    require(refs.get(f'refs/tags/{TAG}')==git(root,'rev-parse',f'refs/tags/{TAG}'),'remote tag differs')
    require(refs.get(f'refs/tags/{ARCHIVE}')==OLD_TAG,'remote archive differs')
    check['remote_refs']=refs
    (out/'verification.json').write_text(json.dumps(check,indent=2)+'\n')
    summary=(f'v1.14のREADMEをv1.14へ訂正しました。アプリ本体の差分・再公開はありません。\n\n'
             f'- 修正後: https://github.com/{REPO}/blob/{TAG}/README.md\n'
             f'- 元タグ保全: https://github.com/{REPO}/tree/{ARCHIVE}\n'
             f'- 試験済みmain: `{OLD_MAIN}`\n- 文書訂正commit: `{prepared["head"]}`\n'
             f'- 元の検証run: {receipt["run_id"]}\n- 差分: README.mdのみ\n'
             f'- 修正run: https://github.com/{REPO}/actions/runs/{os.environ["GITHUB_RUN_ID"]}\n')
    (out/'summary.md').write_text(summary)
    with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as file:file.write(summary)
    subprocess.run(['gh','issue','comment',str(ISSUE),'--repo',REPO,'--body-file',str(out/'summary.md')],cwd=root,check=True)


if __name__=='__main__':
    main()
