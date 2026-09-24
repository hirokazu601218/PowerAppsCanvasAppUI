"""Read-only qualification of the isolated Canvas solution and its package."""
import hashlib
import json
import re
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
OUT = ROOT / 'artifacts/lightweight-isolated-probe'
OUT.mkdir(parents=True, exist_ok=False)
result = {'operation': 'isolated_read_only_package_probe', 'app_id': APP_ID, 'solution': SOLUTION, 'status': 'started'}

def command(args, name, timeout=300):
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       timeout=timeout, check=True)

try:
    bridge.require(APP_ID != CFG['target']['app_id'], 'isolated app must differ from stable app')
    env = CFG['target']['dataverse_url']
    command(['pac', 'auth', 'create', '--name', 'isolated-probe', '--githubFederated',
             '--tenant', CFG['tenant_id'], '--applicationId', CFG['client_id'],
             '--environment', env], 'auth', 120)
    livezip = OUT / 'live.zip'
    command(['pac', 'solution', 'export', '--name', SOLUTION,
             '--path', str(livezip), '--overwrite'], 'export', 300)
    live = OUT / 'live'
    command(['pac', 'solution', 'unpack', '--zipfile', str(livezip),
             '--folder', str(live), '--packagetype', 'Unmanaged'], 'unpack', 180)
    solution = ET.parse(live / 'Other/Solution.xml').getroot()
    components = [(e.get('type'), e.get('schemaName')) for e in solution.iter('RootComponent')]
    bridge.require(len(components) == 1 and components[0][0] == '300',
                   'isolated solution contains components other than its Canvas app')
    metadata = list((live / 'CanvasApps').glob('*.meta.xml'))
    msapps = list((live / 'CanvasApps').glob('*_DocumentUri.msapp'))
    bridge.require(len(metadata) == len(msapps) == 1, 'isolated solution must contain one Canvas document')
    refs = verify_database_references(metadata[0], EXPECTED['required_database_sources'])
    solution_archive = bridge.read_archive(msapps[0])
    bridge.require('Src/scrStaffMasterSearch.pa.yaml' in solution_archive and
                   'Src/Screen1.pa.yaml' not in solution_archive, 'not the lightweight app structure')
    app_sources = source_hashes(solution_archive)
    roundtrip_zip = OUT / 'roundtrip.zip'
    command(['pac', 'solution', 'pack', '--folder', str(live), '--zipfile', str(roundtrip_zip),
             '--packagetype', 'Unmanaged'], 'pack', 300)
    roundtrip = OUT / 'roundtrip'
    command(['pac', 'solution', 'unpack', '--zipfile', str(roundtrip_zip),
             '--folder', str(roundtrip), '--packagetype', 'Unmanaged'], 'roundtrip', 180)
    meta2 = list((roundtrip / 'CanvasApps').glob('*.meta.xml'))
    bridge.require(len(meta2) == 1 and verify_database_references(meta2[0],
                   EXPECTED['required_database_sources']) == refs, 'roundtrip data source drift')
    component2 = ET.parse(roundtrip / 'Other/Solution.xml').getroot()
    bridge.require([(e.get('type'), e.get('schemaName')) for e in component2.iter('RootComponent')]
                   == components, 'roundtrip component drift')
    result.update(status='pass', app_sha256=hashlib.sha256(msapps[0].read_bytes()).hexdigest(),
                  package_sha256=hashlib.sha256(roundtrip_zip.read_bytes()).hexdigest(),
                  components=components, sources=sorted(refs['default.cds']['dataSources']),
                  source_match_stable=app_sources == EXPECTED['source_hashes'],
                  runtime_match_stable=runtime_hashes(solution_archive) == EXPECTED['runtime_hashes'],
                  runtime_control_count=len(runtime_hashes(solution_archive)),
                  metadata_sha256=hashlib.sha256(metadata[0].read_bytes()).hexdigest(),
                  client_version=ET.parse(metadata[0]).getroot().findtext('CreatedByClientVersion'))
except Exception as error:
    result.update(status='fail', error_type=type(error).__name__, error=str(error))
    raise
finally:
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)
