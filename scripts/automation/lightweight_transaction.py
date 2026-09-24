"""Qualify an existing Studio-compiled lightweight baseline through the guarded bridge.

Structural authoring remains in Studio. This path refuses an old/unrecognized
published baseline, preserves a package for rollback, and supports only explicit
existing-property changes. It never treats YAML as a general compiler input.
"""
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

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


def verify_database_references(metadata, required):
    """Refuse a legacy solution template that silently drops Canvas data sources."""
    root = ET.parse(metadata).getroot()
    nodes = [node for node in root if node.tag == 'DatabaseReferences']
    bridge.require(len(nodes) == 1, 'solution Canvas database reference element missing')
    references = json.loads(nodes[0].text or '{}')
    sources = references.get('default.cds', {}).get('dataSources', {})
    bridge.require(isinstance(required, dict) and len(required) == 3, 'required data source manifest missing')
    bridge.require({name: sources.get(name) for name in required} == required,
                   'solution Canvas metadata lacks required Dataverse sources')
    return references


def published_without_newer_draft(props):
    """Studio save and publish are different timestamps; reject a later draft."""
    try:
        draft = datetime.fromisoformat(props['lastDraftVersion'].replace('Z', '+00:00'))
        published = datetime.fromisoformat(props['lastPublishTime'].replace('Z', '+00:00'))
        return props.get('status') == 'Ready' and draft.tzinfo is not None and published.tzinfo is not None and published >= draft
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


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
        bridge.require(apps[0].name.endswith('_DocumentUri.msapp'), 'unexpected solution Canvas document name')
        metadata = apps[0].with_name(apps[0].name.removesuffix('_DocumentUri.msapp') + '.meta.xml')
        bridge.require(metadata.is_file(), 'solution Canvas metadata is missing')
        app_metadata.normalize_display_name(metadata, cfg['display_name'])
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
            if published_without_newer_draft(props):
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
        bridge.require(expected.get('deployment_enabled') is True,
                       'deployment suspended: solution runtime metadata must be qualified on an isolated copy first')
        bridge.require(request.get('approved') is True and request.get('mode') in ('qualify', 'release'), 'request not approved')
        changes = request.get('changes')
        bridge.require(isinstance(changes, list) and len(changes) <= 100, 'invalid property changes')
        if request['mode'] == 'qualify':
            bridge.require(changes == [], 'qualification must preserve the Studio-verified application')
        else:
            bridge.require(bool(changes) and isinstance(request.get('issue'), int) and request['issue'] > 0,
                           'release requires explicit changes and an issue')
        bridge.require(os.environ.get('MS_AUTH_EMAIL') == cfg['test_user'], 'dedicated authenticated user required')
        solution_tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:powerapps/solution-src'], cwd=root, text=True).strip()
        bridge.require(solution_tree == expected['solution_tree_sha'], 'unapproved solution component or connection change')
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
        bridge.require(published_without_newer_draft(before), 'unpublished draft must not be overwritten')
        template_meta = root / 'powerapps/solution-src/CanvasApps/crb3c_v111_99a38.meta.xml'
        verify_database_references(template_meta, expected.get('required_database_sources'))
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
        manifest = {'approved': True, 'issue': request.get('issue', 73), 'target': cfg['target'], 'changes': changes}
        # Existing-property scope is checked again by bridge.build against the
        # untouched compiled baseline. A request cannot add controls or files.
        for change in changes:
            name = change['source']
            bridge.require(name in archive and name.startswith('Src/') and name.endswith('.pa.yaml'), 'unknown source')
            dest = work / 'powerapps/canvas-v3' / name
            document = yaml.safe_load(dest.read_bytes())
            matches = bridge.nodes(document, change['control'])
            bridge.require(len(matches) == 1, 'control must be unique')
            props = matches[0]['Properties']
            bridge.require(change['property'] in props and props[change['property']] == change['before'],
                           'existing property and exact before value required')
            props[change['property']] = change['after']
            dest.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False))
        built = out / 'candidate.msapp'
        result['build'] = bridge.build(work, built, manifest)
        built_runtime = runtime_hashes(bridge.read_archive(built))
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
        bridge.require(runtime_hashes(bridge.read_archive(readback)) == built_runtime,
                       'server compiled rules differ from built package')
        if not changes:
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
