"""Render approved synthetic histories into the single App.Formulas data boundary.

Without --write this only checks fixture/source consistency. It never deploys.
"""
import argparse
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
KINDS = ('Work', 'Social', 'Tax', 'Payroll')
MARKER = '// Synthetic histories: source is tests/fixtures/staff-history-synthetic.json.\n'

def literal(value, key):
    if isinstance(value, str):
        if key in {'Start', 'End', 'PayDate'}:
            return 'Date(' + ','.join(str(int(n)) for n in value.split('-')) + ')'
        return '"' + value.replace('"', '""') + '"'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    raise ValueError(f'Unsupported fixture type: {key}')

def table(rows):
    return 'Table(\n' + ',\n'.join('    {' + ', '.join(k + ':' + literal(v, k) for k, v in r.items()) + '}' for r in rows) + '\n)'

def render(fixtures):
    result = MARKER
    for kind in KINDS:
        result += f'Staff{kind}History = ' + table(fixtures[kind]) + ';\n'
    result += 'StaffResidentHistory = FirstN(Table({StaffId:"",Amount:0,Period:"",Start:Date(2000,1,1),End:Date(2000,1,1)}),0);\n'
    return result.rstrip()

def validate(fixtures):
    parents = {r['staffnumber'] for r in json.loads((ROOT / 'tests/fixtures/staff-basic-25.json').read_text())}
    for kind in KINDS:
        rows = fixtures[kind]
        assert len({r['RecordId'] for r in rows}) == len(rows), kind + ': duplicate record ID'
        for row in rows:
            assert re.fullmatch(r'[0-9]{12}', row['StaffId']) and row['StaffId'] in parents
    for row in fixtures['Payroll']:
        assert row['Gross'] - row['Deduct'] - row['DeductAdj'] == row['Net']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    fixtures = json.loads((ROOT / 'tests/fixtures/staff-history-synthetic.json').read_text())
    validate(fixtures)
    path = ROOT / 'powerapps/canvas-v3/Src/App.pa.yaml'
    text = path.read_text()
    current = yaml.safe_load(text)['App']['Properties']['Formulas']
    assert current.count(MARKER) == 1, 'explicit history boundary required'
    desired = current.split(MARKER)[0] + render(fixtures)
    fx = ROOT / 'powerapps/test-data/staff-history.fx'
    if args.write:
        old_block = '    Formulas: |-\n' + '\n'.join('      ' + line for line in current.splitlines())
        new_block = '    Formulas: |-\n' + '\n'.join('      ' + line for line in desired.splitlines())
        assert text.count(old_block) == 1
        path.write_text(text.replace(old_block, new_block))
        fx.write_text(desired[1:] + '\n')
    else:
        assert current == desired, 'run with --write to regenerate'
        assert fx.read_text() == desired[1:] + '\n', 'generated review artifact is stale'
    print('Synthetic fixture validation and source consistency passed:', {k:len(fixtures[k]) for k in KINDS})
