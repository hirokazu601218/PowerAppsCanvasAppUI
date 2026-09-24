"""Qualify an existing Studio-compiled lightweight baseline through the guarded bridge.

Structural authoring remains in Studio. This path refuses an old/unrecognized
published baseline, preserves a package for rollback, and supports only explicit
existing-property changes. It never treats YAML as a general compiler input.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

import yaml
import bridge
import app_metadata


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_hashes(archive):
    return {n: sha(b) for n, b in archive.items()
            if n.startswith('Src/') and n.endswith('.pa.yaml')
            and not n.endswith('/_EditorState.pa.yaml')}


def runtime_hashes(archive):
    controls = {}
    def visit(value):
        if isinstance(value, dict):
            if 'Name' in value and 'Rules' in value:
                name = value['Name']
                bridge.require(name not in controls, 'duplicate compiled control')
                rules = {r['Property']: r['InvariantScript'] for r in value['Rules']}
                controls[name] = sha(json.dumps(rules, sort_keys=True, ensure_ascii=False).encode())
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for name, data in archive.items():
        if name.startswith('Controls/') and name.endswith('.json'):
            visit(json.loads(data))
    return controls


def verify_baseline(archive, expected, cfg):
    bridge.require(cfg['target']['app_id'] == '362ac991-eead-4f07-8373-afdb3ebfdba1', 'wrong app')
    bridge.require(cfg['target']['environment_id'] == '68e00049-b7e5-eda6-9888-9a3cc493c5be', 'wrong environment')
    bridge.require(expected['app_id'] == cfg['target']['app_id'], 'manifest app mismatch')
    bridge.require(expected['environment_id'] == cfg['target']['environment_id'], 'manifest environment mismatch')
    bridge.require(source_hashes(archive) == expected['source_hashes'], 'published baseline source drift')
    bridge.require(runtime_hashes(archive) == expected['runtime_hashes'], 'published compiled rule drift')
    bridge.require('Src/scrStaffMasterSearch.pa.yaml' in archive and 'Src/Screen1.pa.yaml' not in archive,
                   'legacy structure is not a lightweight baseline')


def main():
    root = Path(__file__).resolve().parents[2]
    cfg = json.loads((root / 'config/apps/staff-master.json').read_text())
    expected = json.loads((root / 'automation/lightweight-expected.json').read_text())
    request = json.loads((root / 'automation/lightweight-transaction.json').read_text())
    out = root / 'artifacts/lightweight-transaction'
    out.mkdir(parents=True, exist_ok=False)
    test_root = root.parent / 'power-platform-playwright/packages/e2e-tests'
    result = {'request_id': request.get('request_id'), 'target': cfg['target'],
              'commit': os.environ.get('GITHUB_SHA'), 'gates': {}, 'touched': False}
    stage = 'scope'

    def command(args, name, cwd=root, env=None, timeout=900):
        with (out / (name + '.log')).open('w') as log:
            subprocess.run(args, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=timeout)

    def api(publish=False):
        token = subprocess.check_output(['az', 'account', 'get-access-token', '--resource',
            'https://service.powerapps.com/', '--query', 'accessToken', '--output', 'tsv'], text=True).strip()
        suffix = '/publish' if publish else ''
        url = (f"https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{cfg['target']['app_id']}{suffix}"
               f"?api-version=2018-10-01&%24filter=environment%20eq%20%27{cfg['target']['environment_id']}%27")
        req = urllib.request.Request(url, data=b'{}' if publish else None,
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
            method='POST' if publish else 'GET')
        with urllib.request.urlopen(req, timeout=90) as response:
            data = response.read()
        return json.loads(data) if data else {}

    def download(name):
        path = out / (name + '.msapp')
        command(['pac', 'canvas', 'download', '--name', cfg['target']['app_id'], '--file-name', str(path),
                 '--environment', cfg['target']['dataverse_url'], '--overwrite'], name, timeout=180)
        return path

    def pack(msapp, name):
        folder = out / name
        shutil.copytree(root / 'powerapps/solution-src', folder)
        apps = list((folder / 'CanvasApps').glob('*.msapp'))
        bridge.require(len(apps) == 1, 'expected exactly one solution Canvas app')
        app_metadata.normalize_display_name(apps[0].with_suffix('.meta.xml'), cfg['display_name'])
        shutil.copyfile(msapp, apps[0])
        package = out / (name + '.zip')
        command(['pac', 'solution', 'pack', '--folder', str(folder), '--zipfile', str(package),
                 '--packagetype', 'Unmanaged'], name + '-pack')
        return package

    def deploy(package, name):
        nonlocal stage
        if name == 'candidate':
            stage = 'import'
        command(['pac', 'solution', 'import', '--path', str(package), '--environment',
                 cfg['target']['dataverse_url'], '--force-overwrite', '--publish-changes'], name + '-import')
        if name == 'candidate':
            result['gates']['import'] = 'success'
            stage = 'publish'
        api(True)
        for _ in range(18):
            props = api()['properties']
            if props.get('status') == 'Ready' and props.get('lastDraftVersion') == props.get('lastPublishTime'):
                return {k: props.get(k) for k in ('status', 'lastDraftVersion', 'lastPublishTime')}
            time.sleep(5)
        raise RuntimeError('publish did not reach matching Ready state')

    def test(kind, restoration=False):
        name = ('restoration-' if restoration else '') + kind
        path = out / name
        path.mkdir()
        filename = 'lightweight-p0.test.ts' if kind == 'p0' else 'lightweight.test.ts'
        url = (f"https://apps.powerapps.com/play/e/{cfg['target']['environment_id']}/a/{cfg['target']['app_id']}"
               f"?tenantId={cfg['tenant_id']}")
        env = {**os.environ, 'CANVAS_APP_URL': url, 'OUTPUT_DIRECTORY': str(path),
               'PLAYWRIGHT_JSON_OUTPUT_NAME': str(path / 'results.json'), 'RETRIES': '0'}
        command(['npx', 'playwright', 'test', 'tests/northwind/canvas/' + filename,
                 '--project=canvas-app', '--retries=0', '--reporter=line,json'], name,
                cwd=test_root, env=env, timeout=300)

    try:
        bridge.require(request.get('approved') is True and request.get('mode') == 'qualify', 'request not approved')
        bridge.require(request.get('changes') == [], 'qualification must preserve the Studio-verified application')
        bridge.require(os.environ.get('MS_AUTH_EMAIL') == cfg['test_user'], 'dedicated authenticated user required')
        stage = 'auth'
        command(['pac', 'auth', 'create', '--name', 'lightweight-transaction', '--githubFederated',
                 '--tenant', cfg['tenant_id'], '--applicationId', cfg['client_id'],
                 '--environment', cfg['target']['dataverse_url']], 'oidc', timeout=120)
        result['gates']['auth'] = 'success'
        original = download('baseline')
        archive = bridge.read_archive(original)
        verify_baseline(archive, expected, cfg)
        result['baseline_sha256'] = sha(original.read_bytes())
        before = api()['properties']
        result['before'] = {k: before.get(k) for k in ('status', 'lastDraftVersion', 'lastPublishTime')}
        bridge.require(before.get('lastDraftVersion') == before.get('lastPublishTime'), 'unpublished draft must not be overwritten')
        stage = 'build'
        work = out / 'bridge-input'
        (work / 'config/apps').mkdir(parents=True)
        local_cfg = copy.deepcopy(cfg)
        local_cfg.update(baseline_msapp='baseline.msapp', baseline_sha256=result['baseline_sha256'])
        shutil.copyfile(original, work / 'baseline.msapp')
        (work / 'config/apps/staff-master.json').write_text(json.dumps(local_cfg))
        for name, data in archive.items():
            if name.startswith('Src/') and name.endswith('.pa.yaml'):
                dest = work / 'powerapps/canvas-v3' / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
        manifest = {'approved': True, 'issue': 73, 'target': cfg['target'], 'changes': []}
        built = out / 'candidate.msapp'
        result['build'] = bridge.build(work, built, manifest)
        baseline_package = pack(original, 'rollback')
        package = pack(built, 'candidate')
        result['package_sha256'] = sha(package.read_bytes())
        result['gates']['build'] = 'success'
        stage = 'import'
        result['touched'] = True
        result['published'] = deploy(package, 'candidate')
        result['gates'].update({'import': 'success', 'publish': 'success'})
        stage = 'readback'
        readback = download('readback')
        result['readback'] = bridge.verify_download(readback, work, manifest)
        verify_baseline(bridge.read_archive(readback), expected, cfg)
        result['gates']['readback'] = 'success'
        for stage in ('change_test', 'p0'):
            test(stage)
            result['gates'][stage] = 'success'
        result['status'] = 'qualified'
    except Exception as error:
        result['status'] = 'blocked' if not result['touched'] else 'failed'
        result['failure'] = {'stage': stage, 'type': type(error).__name__, 'message': str(error)}
        if result['touched']:
            try:
                result['restored'] = deploy(baseline_package, 'restoration')
                restored = download('restoration')
                verify_baseline(bridge.read_archive(restored), expected, cfg)
                test('p0', restoration=True)
                result['restoration'] = 'verified'
            except Exception as restore_error:
                result['restoration'] = 'failed'
                result['restoration_error'] = type(restore_error).__name__ + ': ' + str(restore_error)
        raise
    finally:
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
