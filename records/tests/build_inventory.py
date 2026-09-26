"""Snapshot current test record keys and literal labels; not a production schema."""
from pathlib import Path
import json
from preflight import read, index
from fx_check import Engine
root = Path(__file__).resolve().parents[1]
nodes, _ = index(read(root / 'src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml'))
props = {n:c['Properties'] for n,c in nodes.items()}
engine = Engine(props)
groups = {}
for group in ['Staff','Work','Commute','Social','Resident','Tax','Payroll']:
    rows = engine.prop('gal'+group+'111', 'Items')
    groups[group] = {'initial_visible_records':len(rows), 'keys': sorted({k for r in rows for k in r})}
labels = {}
for n,p in props.items():
    t=p.get('Text','')
    if t.startswith('="') and t.endswith('"') and '&' not in t:
        labels[n]=t[2:-1].replace('""','"')
out={'version':'v1.11','scope':'Initial visible test records and literal control labels; production and HTML unknown columns require separate reconciliation','groups':groups,'literal_labels':labels}
(root/'docs/design/field-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Inventory:',len(groups),'groups,',len(labels),'literal labels')
