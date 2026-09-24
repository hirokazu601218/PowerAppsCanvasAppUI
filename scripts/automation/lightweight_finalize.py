"""Attest a merged, qualified Studio baseline without reusing legacy release tags."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

import bridge
import lightweight_transaction as lt

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    repo = os.environ['GITHUB_REPOSITORY']
    head = os.environ['GITHUB_SHA']
    bridge.require(os.environ['GITHUB_REF'] == 'refs/heads/main', 'main only')
    parents = git('show', '-s', '--format=%P', head).split()
    bridge.require(len(parents) == 2, 'reviewed merge commit required')
    candidate = parents[1]
    bridge.require(git('rev-parse', candidate + '^{tree}') == git('rev-parse', head + '^{tree}'), 'candidate tree differs from main')
    cfg = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
    expected = json.loads((ROOT / 'automation/lightweight-expected.json').read_text())
    request = json.loads((ROOT / 'automation/lightweight-transaction.json').read_text())
    bridge.require(request['mode'] == 'qualify' and request['approved'] is True and request['changes'] == [], 'compiled baseline qualification only')
    runs = json.loads(subprocess.check_output(['gh', 'api', f'repos/{repo}/actions/runs?head_sha={candidate}&per_page=100'], text=True))['workflow_runs']
    runs = [r for r in runs if r['path'] == '.github/workflows/lightweight-transaction.yml' and r['head_sha'] == candidate and r['event'] == 'push']
    bridge.require(bool(runs), 'exact candidate qualification not found')
    run = max(runs, key=lambda r: r['id'])
    bridge.require(run['status'] == 'completed' and run['conclusion'] == 'success', 'latest qualification did not pass')
    out = ROOT / 'artifacts/lightweight-finalize'
    out.mkdir(parents=True)
    subprocess.run(['gh', 'run', 'download', str(run['id']), '--repo', repo, '--name', f"lightweight-transaction-{run['id']}", '--dir', str(out / 'evidence')], check=True, timeout=180)
    result_paths = list((out / 'evidence').rglob('lightweight-transaction/result.json'))
    bridge.require(len(result_paths) == 1, 'unique transaction evidence required')
    evidence = result_paths[0].parent
    result = json.loads(result_paths[0].read_text())
    bridge.require(result['status'] == 'qualified' and result['commit'] == candidate and result['request_id'] == request['request_id'], 'evidence candidate mismatch')
    bridge.require(result['target'] == cfg['target'] and 'restoration' not in result, 'target or restoration mismatch')
    gates = {'build', 'auth', 'import', 'publish', 'readback', 'change_test', 'p0'}
    bridge.require(set(result['gates']) == gates and all(v == 'success' for v in result['gates'].values()), 'all seven gates required')
    bridge.require(lt.sha((evidence / 'candidate.zip').read_bytes()) == result['package_sha256'], 'solution digest mismatch')
    lt.verify_baseline(bridge.read_archive(evidence / 'readback.msapp'), expected, cfg)
    token = subprocess.check_output(['az', 'account', 'get-access-token', '--resource', 'https://service.powerapps.com/', '--query', 'accessToken', '--output', 'tsv'], text=True).strip()
    url = f"https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{cfg['target']['app_id']}?api-version=2018-10-01&%24filter=environment%20eq%20%27{cfg['target']['environment_id']}%27"
    with urllib.request.urlopen(urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token}), timeout=90) as response:
        props = json.load(response)['properties']
    bridge.require(lt.published_without_newer_draft(props), 'current app has unpublished changes')
    bridge.require(all(props.get(k) == v for k, v in result['published'].items()), 'publication moved since qualification')
    version = expected['candidate_version']
    tag = 'lightweight-v' + version
    bridge.require(not git('tag', '--list', tag), 'do not overwrite an existing qualification tag')
    branch = 'docs/lightweight-qualified-' + str(run['id'])
    subprocess.run(['git', 'checkout', '-b', branch], cwd=ROOT, check=True)
    readme = ROOT / 'README.md'
    text = readme.read_text()
    start = '<!-- lightweight-release:start -->'
    end = '<!-- lightweight-release:end -->'
    bridge.require(text.count(start) == text.count(end) == 1, 'README markers required')
    block = (f'\n軽量版の検証済み基準：**[{tag}](https://github.com/{repo}/tree/{tag})**。\n\n'
             f'- [全7ゲートの検証結果](https://github.com/{repo}/actions/runs/{run["id"]})\n'
             f'- 公開日時（UTC）：{result["published"]["lastPublishTime"]}\n'
             '- Studioで構造移行し、既存bridgeによる再配布・公開・読戻し・追加試験・独立P0を確認。\n'
             '- 旧標準フローのv1.14タグとは別の軽量版基準。実端末・200%・業務受入の未実施項目は残る。\n')
    readme.write_text(text.split(start)[0] + start + block + end + text.split(end)[1])
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], cwd=ROOT, check=True)
    subprocess.run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], cwd=ROOT, check=True)
    subprocess.run(['git', 'add', 'README.md'], cwd=ROOT, check=True)
    subprocess.run(['git', 'commit', '-m', f'docs: record qualified {tag}'], cwd=ROOT, check=True)
    release = git('rev-parse', 'HEAD')
    bridge.require(git('diff', '--name-only', head, release) == 'README.md', 'documentation snapshot widened payload')
    receipt = {'schema': 'lightweight-baseline-1', 'state': 'QUALIFIED_STUDIO_BASELINE', 'version': version,
               'tag': tag, 'repository': repo, 'candidate_commit': candidate, 'main_commit': head,
               'release_commit': release, 'readme_branch': branch, 'readme_sha256': lt.sha(readme.read_bytes()),
               'run_id': run['id'], 'run_attempt': run['run_attempt'], 'request': request,
               'target': cfg['target'], 'published': result['published'], 'gates': result['gates'],
               'package_sha256': result['package_sha256'], 'expected': expected}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    subprocess.run(['git', 'tag', '-a', tag, release, '-F', str(out / 'receipt.json')], cwd=ROOT, check=True)
    subprocess.run(['git', 'push', '--atomic', 'origin', f'HEAD:refs/heads/{branch}', f'refs/tags/{tag}'], cwd=ROOT, check=True)
    print(json.dumps({'state': 'PENDING_WORK_DOCUMENTATION_PR', 'tag': tag, 'branch': branch, 'head': release, 'run_id': run['id']}))
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
        f.write(f'Qualified {tag}. Work must merge README branch `{branch}` at `{release}` through a documentation PR. No app deployment is performed by this finalizer.\n')


if __name__ == '__main__':
    main()
