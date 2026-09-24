"""Import an unchanged package into the isolated copy and verify export readback."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge
from lightweight_transaction import verify_database_references, source_hashes, runtime_hashes

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
EXPECTED = json.loads((ROOT / 'automation/lightweight-expected.json').read_text())
APP_ID = 'bd256de5-c7a5-4487-9aef-91ee26d4c946'
SOLUTION = 'LightweightDeploymentProbe'
COMPONENT = 'cra05_deployprobe20260924_b51e3'
OUT = ROOT / 'artifacts/lightweight-isolated-import'
OUT.mkdir(parents=True, exist_ok=False)
result = {'operation': 'isolated_unchanged_import', 'app_id': APP_ID,
          'solution': SOLUTION, 'status': 'started', 'touched': False}

def command(args, name, timeout=300):
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

def unpack(zipfile, folder, name):
    command(['pac', 'solution', 'unpack', '--zipfile', str(zipfile),
             '--folder', str(folder), '--packagetype', 'Unmanaged'], name, 180)

def inspect(folder):
    root = ET.parse(folder / 'Other/Solution.xml').getroot()
    components = [(e.get('type'), e.get('schemaName')) for e in root.iter('RootComponent')]
    bridge.require(components == [('300', COMPONENT)],
                   'solution must contain exactly the isolated Canvas component')
    metadata = list((folder / 'CanvasApps').glob('*.meta.xml'))
    msapps = list((folder / 'CanvasApps').glob('*_DocumentUri.msapp'))
    bridge.require(len(metadata) == len(msapps) == 1, 'expected one isolated Canvas document')
    refs = verify_database_references(metadata[0], EXPECTED['required_database_sources'])
    archive = bridge.read_archive(msapps[0])
    bridge.require('Src/scrStaffMasterSearch.pa.yaml' in archive and
                   'Src/Screen1.pa.yaml' not in archive, 'unexpected Canvas structure')
    bridge.require(source_hashes(archive) == EXPECTED['source_hashes'],
                   'isolated app is not the verified source baseline')
    return {'refs': refs, 'sources': source_hashes(archive), 'runtime': runtime_hashes(archive),
            'metadata_sha256': hashlib.sha256(metadata[0].read_bytes()).hexdigest()}

def same_semantics(left, right):
    return all(left[key] == right[key] for key in ('refs', 'sources', 'runtime'))

def export(name):
    path = OUT / (name + '.zip')
    command(['pac', 'solution', 'export', '--name', SOLUTION,
             '--path', str(path), '--overwrite'], name + '-export')
    folder = OUT / name
    unpack(path, folder, name + '-unpack')
    return path, inspect(folder)

try:
    bridge.require(APP_ID != CFG['target']['app_id'], 'stable app cannot be an isolated target')
    env = CFG['target']['dataverse_url']
    try:
        command(['pac', 'auth', 'create', '--name', 'isolated-import', '--githubFederated',
                 '--tenant', CFG['tenant_id'], '--applicationId', CFG['client_id'],
                 '--environment', env], 'auth', 120)
    except subprocess.CalledProcessError:
        diagnostic = re.sub(r'https?://\\S+', '[URL]', (OUT / 'auth.log').read_text()[-1200:])
        raise RuntimeError('PAC auth failed: ' + diagnostic)
    backup, before = export('before')
    candidate = OUT / 'unchanged.zip'
    command(['pac', 'solution', 'pack', '--folder', str(OUT / 'before'),
             '--zipfile', str(candidate), '--packagetype', 'Unmanaged'], 'pack')
    check = OUT / 'checked'
    unpack(candidate, check, 'check-package')
    bridge.require(same_semantics(inspect(check), before), 'package roundtrip mismatch')
    result['backup_sha256'] = hashlib.sha256(backup.read_bytes()).hexdigest()
    result['candidate_sha256'] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    result['touched'] = True
    command(['pac', 'solution', 'import', '--path', str(candidate),
             '--environment', env, '--force-overwrite'], 'import', 600)
    _, after = export('after')
    result['metadata_hash_changed'] = after['metadata_sha256'] != before['metadata_sha256']
    bridge.require(same_semantics(after, before), 'isolated app references/source/runtime changed after import')
    result.update(status='pass', root_component=COMPONENT,
                  database_sources=sorted(after['refs']['default.cds']['dataSources']),
                  source_hashes_equal=True, runtime_hashes_equal=True)
except Exception as error:
    result.update(status='fail', error_type=type(error).__name__, error=str(error))
    if result['touched']:
        try:
            command(['pac', 'solution', 'import', '--path', str(backup),
                     '--environment', CFG['target']['dataverse_url'],
                     '--force-overwrite'], 'restore', 600)
            _, restored = export('restored')
            result['restoration'] = 'verified' if same_semantics(restored, before) else 'mismatch'
        except Exception as restore_error:
            result['restoration'] = type(restore_error).__name__ + ': ' + str(restore_error)
    raise
finally:
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)
