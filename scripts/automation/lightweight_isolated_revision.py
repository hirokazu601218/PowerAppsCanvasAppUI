"""Exercise an actual one-property revision on the isolated Canvas copy, then restore it."""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge
from lightweight_transaction import source_hashes, runtime_hashes, verify_database_references

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
EXPECTED = json.loads((ROOT / 'automation/lightweight-expected.json').read_text())
APP_ID = 'bd256de5-c7a5-4487-9aef-91ee26d4c946'
SOLUTION = 'LightweightDeploymentProbe'
COMPONENT = 'cra05_deployprobe20260924_b51e3'
OUT = ROOT / 'artifacts/lightweight-isolated-revision'
OUT.mkdir(parents=True, exist_ok=False)
result = {'operation': 'isolated_property_revision_and_restore', 'app_id': APP_ID,
          'status': 'started', 'touched': False, 'restoration': 'not_needed'}

def run(args, name, timeout=600):
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

def unpack(path, folder, name):
    run(['pac', 'solution', 'unpack', '--zipfile', str(path), '--folder', str(folder),
         '--packagetype', 'Unmanaged'], name, 180)

def inspect(folder):
    root = ET.parse(folder / 'Other/Solution.xml').getroot()
    components = [(e.get('type'), e.get('schemaName')) for e in root.iter('RootComponent')]
    bridge.require(components == [('300', COMPONENT)], 'component scope expanded')
    apps = list((folder / 'CanvasApps').glob('*_DocumentUri.msapp'))
    metas = list((folder / 'CanvasApps').glob('*.meta.xml'))
    bridge.require(len(apps) == len(metas) == 1, 'expected one isolated app')
    refs = verify_database_references(metas[0], EXPECTED['required_database_sources'])
    archive = bridge.read_archive(apps[0])
    return {'app': apps[0], 'refs': refs, 'archive': archive,
            'sources': source_hashes(archive), 'runtime': runtime_hashes(archive)}

def export(name):
    path = OUT / (name + '.zip')
    run(['pac', 'solution', 'export', '--name', SOLUTION,
         '--path', str(path), '--overwrite'], name + '-export')
    folder = OUT / name
    unpack(path, folder, name + '-unpack')
    return path, inspect(folder)

def import_package(package, name):
    run(['pac', 'solution', 'import', '--path', str(package),
         '--environment', CFG['target']['dataverse_url'],
         '--force-overwrite'], name + '-import')

def same(a, b):
    return all(a[k] == b[k] for k in ('refs', 'sources', 'runtime'))

backup = None
baseline = None
try:
    bridge.require(APP_ID != CFG['target']['app_id'], 'cannot revise stable app')
    run(['pac', 'auth', 'create', '--name', 'isolated-revision', '--githubFederated',
         '--tenant', CFG['tenant_id'], '--applicationId', CFG['client_id'],
         '--environment', CFG['target']['dataverse_url']], 'auth', 120)
    backup, baseline = export('baseline')
    bridge.require(baseline['sources'] == EXPECTED['source_hashes'], 'copy source drift')
    bridge.require(baseline['runtime'] == EXPECTED['runtime_hashes'], 'copy compiled drift')
    source = 'Src/scrMaintenance.pa.yaml'
    control = 'lblMaintenanceVersion'
    before = '="UI試作 v1.26　／　画面要件定義書 v0.6"'
    after = '="UI試作 v1.26　／　画面要件定義書 v0.6 [隔離配布試験]"'
    changes = [{'source': source, 'control': control, 'property': 'Text',
                'before': before, 'after': after}]
    work = OUT / 'bridge-input'
    (work / 'config/apps').mkdir(parents=True)
    local_cfg = copy.deepcopy(CFG)
    local_cfg['target'] = {**CFG['target'], 'app_id': APP_ID}
    local_cfg.update(baseline_msapp='baseline.msapp',
                     baseline_sha256=hashlib.sha256(baseline['app'].read_bytes()).hexdigest())
    (work / 'config/apps/staff-master.json').write_text(json.dumps(local_cfg))
    shutil.copyfile(baseline['app'], work / 'baseline.msapp')
    for name, data in baseline['archive'].items():
        if name.startswith('Src/') and name.endswith('.pa.yaml'):
            dest = work / 'powerapps/canvas-v3' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    docpath = work / 'powerapps/canvas-v3' / source
    doc = yaml.safe_load(docpath.read_bytes())
    nodes = bridge.nodes(doc, control)
    bridge.require(len(nodes) == 1 and nodes[0]['Properties']['Text'] == before,
                   'revision before value mismatch')
    nodes[0]['Properties']['Text'] = after
    docpath.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
    manifest = {'approved': True, 'issue': 73, 'target': local_cfg['target'], 'changes': changes}
    candidate_app = OUT / 'candidate.msapp'
    result['build'] = bridge.build(work, candidate_app, manifest)
    candidate_archive = bridge.read_archive(candidate_app)
    candidate_sources = source_hashes(candidate_archive)
    candidate_runtime = runtime_hashes(candidate_archive)
    bridge.require({k for k in candidate_sources if candidate_sources[k] != baseline['sources'][k]}
                   == {source}, 'unexpected source change')
    bridge.require({k for k in candidate_runtime if candidate_runtime[k] != baseline['runtime'][k]}
                   == {control}, 'unexpected compiled rule change')
    staged = OUT / 'staged'
    shutil.copytree(OUT / 'baseline', staged)
    shutil.copyfile(candidate_app, staged / 'CanvasApps' / baseline['app'].name)
    candidate = OUT / 'candidate.zip'
    run(['pac', 'solution', 'pack', '--folder', str(staged), '--zipfile', str(candidate),
         '--packagetype', 'Unmanaged'], 'candidate-pack')
    checked = OUT / 'checked'
    unpack(candidate, checked, 'candidate-check')
    preflight = inspect(checked)
    bridge.require(preflight['refs'] == baseline['refs'] and
                   preflight['sources'] == candidate_sources and
                   preflight['runtime'] == candidate_runtime, 'candidate package drift')
    result['touched'] = True
    import_package(candidate, 'candidate')
    _, deployed = export('deployed')
    bridge.require(deployed['refs'] == baseline['refs'], 'deployed Dataverse reference drift')
    bridge.require(deployed['sources'] == candidate_sources and
                   deployed['runtime'] == candidate_runtime, 'revision failed readback')
    bridge.verify_download(deployed['app'], work, manifest)
    result['revision_readback'] = 'exact'
    import_package(backup, 'restoration')
    _, restored = export('restored')
    bridge.require(same(restored, baseline), 'restoration source/runtime/refs mismatch')
    result.update(status='pass', restoration='verified', changed_control=control,
                  changed_property='Text', database_sources=sorted(restored['refs']['default.cds']['dataSources']))
except Exception as error:
    result.update(status='fail', error_type=type(error).__name__, error=str(error))
    if result['touched'] and result['restoration'] != 'verified' and backup is not None:
        try:
            import_package(backup, 'failure-restoration')
            _, restored = export('failure-restored')
            result['restoration'] = 'verified' if same(restored, baseline) else 'mismatch'
        except Exception as restore_error:
            result['restoration'] = type(restore_error).__name__ + ': ' + str(restore_error)
    raise
finally:
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)
