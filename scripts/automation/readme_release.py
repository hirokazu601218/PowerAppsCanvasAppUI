"""Update only README's delimited release record from verified tag evidence."""
import json
from pathlib import Path
import subprocess
import uuid

import policy

START='<!-- staff-master-release:start -->'
END='<!-- staff-master-release:end -->'


def render(text, receipt, repo):
    if receipt.get('state') != 'TESTED_RELEASE' or not policy.promotion(receipt.get('gates',{})):
        raise ValueError('README requires a verified release receipt')
    if text.count(START)!=1 or text.count(END)!=1 or text.index(START)>=text.index(END):
        raise ValueError('README release markers must be unique and ordered')
    version=receipt['version']
    block=(f'{START}\n'
           f'最新成功版：**[v{version}](https://github.com/{repo}/tree/v{version})**（隔離テストアプリ）。'
           '追加テスト・既存P0・公開後の読戻し照合が合格しています。\n\n'
           f'- [検証結果](https://github.com/{repo}/actions/runs/{receipt["run_id"]})\n'
           f'- [変更要求](https://github.com/{repo}/issues/{receipt["issue"]})\n'
           f'- 公開日時（UTC）：{receipt["published"]["version"]}\n'
           '- アプリ一覧名は `職員マスタ検索_自動テスト_v1_11`。画面内版表示と上記成功タグで版を確認します。\n'
           f'{END}')
    return text[:text.index(START)]+block+text[text.index(END)+len(END):]


def publish(root, receipt, repo):
    root=Path(root)
    evidence=root/'artifacts/release/readme-update.json'
    def record(state, **details):
        result={'state':state,'version':receipt['version'],**details}
        evidence.parent.mkdir(parents=True,exist_ok=True)
        evidence.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        return result
    path=root/'README.md'
    before=path.read_text()
    after=render(before,receipt,repo)
    if before==after:
        return record('UNCHANGED')
    # Keep AUT-007: generated documentation also travels through a branch and PR.
    # Only the exact generated documentation commit may be merged; no force push.
    branch=f'automation/readme-v{receipt["version"]}-{uuid.uuid4().hex[:8]}'
    subprocess.run(['git','checkout','-b',branch],cwd=root,check=True)
    path.write_text(after)
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=root,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=root,check=True)
    subprocess.run(['git','add','--','README.md'],cwd=root,check=True)
    subprocess.run(['git','commit','-m',f'docs: record verified v{receipt["version"]} in README'],cwd=root,check=True)
    subprocess.run(['git','push','origin',f'HEAD:refs/heads/{branch}'],cwd=root,check=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    body=root/'artifacts/release/readme-pr.md'
    body.parent.mkdir(parents=True,exist_ok=True)
    body.write_text(f'成功タグv{receipt["version"]}の検証済み受領記録から、READMEの成功版欄だけを更新します。\n\n'
                    f'検証run: https://github.com/{repo}/actions/runs/{receipt["run_id"]}\n'
                    'アプリ・テスト・手書きの説明は変更しません。\n')
    try:
        pr=subprocess.check_output(['gh','pr','create','--repo',repo,'--base','main','--head',branch,
                                    '--title',f'docs: READMEの成功版をv{receipt["version"]}へ更新',
                                    '--body-file',str(body)],cwd=root,text=True,stderr=subprocess.PIPE).strip()
    except subprocess.CalledProcessError as error:
        # A repository may forbid bot-created PRs while the authorized Work
        # connection can complete the same generated documentation branch.
        # Preserve the restriction and never report the pending README as merged.
        if 'GitHub Actions is not permitted to create or approve pull requests' not in (error.stderr or ''):
            raise
        return record('PENDING_WORK_PR',branch=branch,head=head,
                      reason='repository_disallows_actions_pull_requests')
    subprocess.run(['gh','pr','merge',pr,'--repo',repo,'--merge','--match-head-commit',head],cwd=root,check=True)
    return record('MERGED',branch=branch,head=head,pr=pr)
