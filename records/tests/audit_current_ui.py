"""Audit the actual v1.23 readbacks and approved fixture boundary; no deployment."""
import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/testing/regression-v123-remaining'
class StrictLoader(yaml.SafeLoader):
    pass
def mapping(loader, node, deep=False):
    result = {}
    for key, value in node.value:
        key = loader.construct_object(key, deep=deep)
        if key in result:
            raise ValueError('Duplicate YAML key: ' + str(key))
        result[key] = loader.construct_object(value, deep=deep)
    return result
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
files = {}
def read(name):
    data = (ROOT / name).read_bytes()
    files[name] = hashlib.sha256(data).hexdigest()
    return yaml.load(data, Loader=StrictLoader)
def index(children, parent):
    result = {}
    for item in children:
        assert len(item) == 1
        name, node = next(iter(item.items()))
        assert name not in result, name
        result[name] = (node, parent)
        descendants = index(node.get('Children', []), name)
        assert not result.keys() & descendants.keys()
        result.update(descendants)
    return result

nodes, counts, sources = {}, {}, {}
for screen in ['Screen1','scrHome','scrAttendance','scrBonus','scrPayroll','scrMaintenance']:
    version = '1.23' if screen in ['Screen1','scrHome','scrMaintenance'] else '1.22'
    name = f'src/screen-ui/v{version}/studio-readback/{screen}.pa.yaml'
    source = read(name)['Screens'][screen]
    current = index(source['Children'], screen)
    assert not nodes.keys() & current.keys()
    nodes.update(current)
    counts[screen] = len(current)
    sources[screen] = name

# The 5 distributed pairs remain the v1.22 base. v1.23 is a 7-property patch.
pairs = []
for screen in list(counts)[1:]:
    managed = read(f'src/screen-ui/v1.22/{screen}.pa.yaml')['Screens'][screen]['Children']
    pasted = read(f'src/screen-ui/v1.22/{screen}.paste.yaml')
    assert managed == pasted, screen
    pairs.append(screen)

base_name = 'src/staff-master/patches/v1.21/studio-readback/Screen1.pa.yaml'
base = index(read(base_name)['Screens']['Screen1']['Children'], 'Screen1')
assert base.keys() <= nodes.keys()
approved_changes = {'conStaffMaster111.Y','conStaffMaster111.Height','lblMeta111.Text',
                    'lblCPayrollModal111112.Text','lblCPayrollModal111113.Text'}
changes = set()
for name, (before, parent) in base.items():
    after, actual_parent = nodes[name]
    assert before['Control'] == after['Control'] and parent == actual_parent
    assert before.get('Variant') == after.get('Variant')
    for prop in before['Properties'].keys() | after['Properties'].keys():
        if before['Properties'].get(prop) != after['Properties'].get(prop):
            changes.add(name + '.' + prop)
assert changes == approved_changes, changes
for name,(node,parent) in nodes.items():
    assert not (node['Control']=='Classic/Button@2.2.0' and 'AccessibleLabel' in node['Properties'])
    if node['Control'].startswith('PDFViewer'):
        assert parent == 'Screen1'

patch = json.loads((ROOT/'src/screen-ui/v1.23/patches.json').read_text())
fx = (ROOT/'src/screen-ui/v1.23/studio-readback/App.Formulas.fx').read_text().strip().lstrip('=')
for target, expected in patch.items():
    name, prop = target.split('.')
    actual = fx if name == 'App' else nodes[name][0]['Properties'][prop].lstrip('=')
    assert actual.strip() == expected.strip(), target
assert {f'lblBasicVal{i}111' for i in range(9)} <= nodes.keys()
assert {f'lblCPayrollModal111{i}' for i in range(163)} <= nodes.keys()
fields = json.loads((ROOT/'src/staff-master/patches/v1.18/ledger-field-map.json').read_text())
expected = {f'lblLedger_{f["field"]}111' for f in fields}
assert len(expected) == 69 and expected <= nodes.keys()

staff = json.loads((ROOT/'tests/fixtures/staff-basic-25.json').read_text())
staff_ids = [r['staffnumber'] for r in staff]
assert len(staff_ids) == len(set(staff_ids)) == 25
assert all(isinstance(x,str) and re.fullmatch(r'\d{12}',x) for x in staff_ids)
fixture_counts = {'Staff':len(staff_ids)}
for name in ['commute-6','payrollledger-7']:
    rows = json.loads((ROOT/f'tests/fixtures/{name}.json').read_text())
    assert all(r['data']['crb3c_staffnumber'] in staff_ids for r in rows)
    fixture_counts[name] = len(rows)
hist = json.loads((ROOT/'tests/fixtures/staff-history-synthetic.json').read_text())
spec = importlib.util.spec_from_file_location('history_renderer', ROOT/'scripts/automation/render_staff_history.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
renderer.validate(hist)
for kind in renderer.KINDS:
    expected = f'Staff{kind}History = ' + renderer.table(hist[kind]) + ';'
    assert fx.count(f'Staff{kind}History =') == 1
    assert expected in fx, kind
    fixture_counts[kind] = len(hist[kind])
result = dict(version='1.23',status='PASS',sources=sources,screen_controls=counts,
              controls=len(nodes),duplicate_ids=0,base_controls_preserved=len(base),
              base_property_changes=sorted(changes),distributed_base_pairs_equal=pairs,
              patch_properties_equal=sorted(patch),pdf_parent='Screen1',basic_fields=9,
              payroll_fields=163,ledger_fields=69,fixture_counts=fixture_counts,
              control_versions=dict(collections.Counter(n['Control'] for n,p in nodes.values())),
              sha256=files,limitations=['Not a Microsoft compiler or complete property schema.','Does not execute Power Fx or replace live E2E.'])
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'source-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','controls','duplicate_ids','base_controls_preserved','fixture_counts']},ensure_ascii=False))
