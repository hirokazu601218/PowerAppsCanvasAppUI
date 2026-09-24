"""Read-only qualification of a package built from the current live solution."""
import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge
import lightweight_transaction as lt

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / 'config/apps/staff-master.json').read_text())
EXPECTED = json.loads((ROOT / 'automation/lightweight-expected.json').read_text())
OUT = ROOT / 'artifacts/lightweight-solution-probe'
OUT.mkdir(parents=True, exist_ok=False)
RESULT = {'operation': 'read_only_package_probe', 'target': CFG['target'], 'state': 'started'}

def command(args, name, timeout=300):
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

def canvas_metadata(folder):
    files = list((folder / 'CanvasApps').glob('*.meta.xml'))
    bridge.require(len(files) == 1, 'solution must contain exactly one Canvas app')
    meta = files[0]
    root = ET.parse(meta).getroot()
    bridge.require(root.findtext('Name') == 'crb3c_v111_99a38', 'wrong Canvas component')
    return meta, root

def components(folder):
    root = ET.parse(folder / 'Other/Solution.xml').getroot()
    return sorted((e.get('type'), e.get('schemaName')) for e in root.iter('RootComponent'))

def file_hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}

try:
    bridge.require(CFG['target']['app_id'] == EXPECTED['app_id'], 'wrong app')
    bridge.require(CFG['target']['environment_id'] == EXPECTED['environment_id'], 'wrong environment')
    command(['pac', 'auth', 'create', '--name', 'probe', '--githubFederated',
             '--tenant', CFG['tenant_id'], '--applicationId', CFG['client_id'],
             '--environment', CFG['target']['dataverse_url']], 'auth', 120)
    app = OUT / 'published.msapp'
    command(['pac', 'canvas', 'download', '--name', CFG['target']['app_id'],
             '--file-name', str(app), '--environment', CFG['target']['dataverse_url'],
             '--overwrite'], 'download', 180)
    archive = bridge.read_archive(app)
    lt.verify_baseline(archive, EXPECTED, CFG)
    livezip = OUT / 'live.zip'
    command(['pac', 'solution', 'export', '--name', CFG['solution_name'],
             '--path', str(livezip), '--overwrite'], 'export', 300)
    live = OUT / 'live'
    command(['pac', 'solution', 'unpack', '--zipfile', str(livezip),
             '--folder', str(live), '--packagetype', 'Unmanaged'], 'unpack', 180)
    meta, root = canvas_metadata(live)
    refs = lt.verify_database_references(meta, EXPECTED['required_database_sources'])
    msapps = list((live / 'CanvasApps').glob('*_DocumentUri.msapp'))
    bridge.require(len(msapps) == 1, 'solution must contain exactly one Canvas document')
    bridge.require(root.findtext('DocumentUri', '').endswith('/' + msapps[0].name),
                   'Canvas document reference mismatch')
    bridge.require(lt.source_hashes(bridge.read_archive(msapps[0])) == EXPECTED['source_hashes'],
                   'solution Canvas source differs from published baseline')
    originals = file_hashes(live)
    staged = OUT / 'staged'
    shutil.copytree(live, staged)
    staged_msapp = staged / 'CanvasApps' / msapps[0].name
    shutil.copyfile(app, staged_msapp)
    staged_meta, _ = canvas_metadata(staged)
    bridge.require(staged_meta.read_bytes() == meta.read_bytes(), 'metadata changed during staging')
    package = OUT / 'roundtrip.zip'
    command(['pac', 'solution', 'pack', '--folder', str(staged), '--zipfile', str(package),
             '--packagetype', 'Unmanaged'], 'pack', 300)
    roundtrip = OUT / 'roundtrip'
    command(['pac', 'solution', 'unpack', '--zipfile', str(package), '--folder',
             str(roundtrip), '--packagetype', 'Unmanaged'], 'roundtrip', 180)
    repacked_meta, _ = canvas_metadata(roundtrip)
    bridge.require(lt.verify_database_references(repacked_meta, EXPECTED['required_database_sources']) == refs,
                   'Dataverse references changed in package roundtrip')
    bridge.require(components(roundtrip) == components(live), 'solution component list changed')
    pack_msapp = roundtrip / 'CanvasApps' / msapps[0].name
    bridge.require(lt.source_hashes(bridge.read_archive(pack_msapp)) == EXPECTED['source_hashes'],
                   'Canvas source changed in package roundtrip')
    before = {k: v for k, v in originals.items() if not k.endswith('.msapp')}
    after = {k: v for k, v in file_hashes(roundtrip).items() if not k.endswith('.msapp')}
    bridge.require(before == after, 'non-Canvas solution files changed in package roundtrip')
    RESULT.update(state='pass', published_sha256=lt.sha(app.read_bytes()),
                  package_sha256=lt.sha(package.read_bytes()),
                  database_sources=sorted(refs['default.cds']['dataSources']),
                  root_components=components(live), non_canvas_file_count=len(before),
                  client_version=root.findtext('CreatedByClientVersion'))
except Exception as error:
    RESULT.update(state='fail', error_type=type(error).__name__, error=str(error))
    raise
finally:
    (OUT / 'result.json').write_text(json.dumps(RESULT, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(RESULT, ensure_ascii=False), flush=True)
