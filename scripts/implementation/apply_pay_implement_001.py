#!/usr/bin/env python3
"""Apply the PAY-IMPLEMENT-001 delta to an explicitly supplied local readback.

Offline helper only. Never imports, saves, publishes, authenticates, or writes back
into the readback directory. Exact before-state checks fail closed. Source output
may contain tenant-specific existing values and is local verification material,
not a GitHub artifact.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
DELTA = ROOT / 'src/screen-ui/v1.31'

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def semantic_sha(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')))

def control(root, name):
    for entry in root.get('Children', []):
        if name in entry:
            return entry[name]
        for child in entry.values():
            found = control(child, name)
            if found is not None:
                return found
    return None

def property_owner(screen, screen_name, name):
    owner = screen if name == screen_name else control(screen, name)
    if owner is None:
        raise ValueError(f'Missing expected control: {name}')
    return owner

def inventory(screens):
    """Index all controls globally, refusing ambiguous duplicate names."""
    result = {}
    def visit(root, parent, screen):
        for entry in root.get('Children', []):
            for name, value in entry.items():
                if name in result:
                    raise ValueError(f'Duplicate control name: {name}')
                if name in screens:
                    raise ValueError(f'Screen/control name collision: {name}')
                result[name] = {'screen': screen, 'parent': parent,
                                'properties': value.get('Properties', {}),
                                'control_type': value.get('Control'),
                                'variant': value.get('Variant')}
                visit(value, name, screen)
    for name, screen in screens.items():
        visit(screen, name, name)
    return result

def load_readback(directory, manifest):
    """Require the exact reviewed source file set, including EditorState."""
    documents = {}
    screens = {}
    expected_names = set(manifest['baseline']['source_files'])
    actual_names = {path.name for path in directory.glob('*.pa.yaml')}
    if actual_names != expected_names:
        raise ValueError(f'Unexpected readback source set: added={sorted(actual_names-expected_names)}, missing={sorted(expected_names-actual_names)}')
    for filename, expected in manifest['baseline']['source_files'].items():
        path = directory / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Full readback baseline mismatch: {filename}; review the current source before applying')
        document = yaml.safe_load(path.read_text())
        documents[filename] = document
        for name, screen in document.get('Screens', {}).items():
            if name in screens:
                raise ValueError(f'Duplicate screen name: {name}')
            screens[name] = screen
    inventory(screens)
    return documents, screens

def change_evidence(before, after, manifest):
    old, new = inventory(before), inventory(after)
    if set(old) != set(new):
        raise ValueError('Unexpected control addition or removal')
    approved = {(c['screen'], c['control'], c['property']) for c in manifest['changes'] if 'property' in c}
    changes = []
    for name in old:
        if old[name]['control_type'] != new[name]['control_type'] or old[name]['variant'] != new[name]['variant']:
            raise ValueError(f'Unexpected control type change: {name}')
        if old[name]['parent'] != new[name]['parent']:
            if (name, old[name]['parent'], new[name]['parent']) != ('conPaySummary', 'conPayBody', 'conscrPayrollRoot'):
                raise ValueError(f'Unexpected parent change: {name}')
            changes.append({'control': name, 'property': 'parent', 'before': old[name]['parent'], 'after': new[name]['parent']})
        for prop in set(old[name]['properties']) | set(new[name]['properties']):
            a, b = old[name]['properties'].get(prop), new[name]['properties'].get(prop)
            if a != b:
                if (old[name]['screen'], name, prop) not in approved:
                    raise ValueError(f'Unexpected property change: {name}.{prop}')
                changes.append({'control': name, 'property': prop, 'before_sha256': sha(str(a)), 'after_sha256': sha(str(b))})
    for name in before:
        for prop in set(before[name].get('Properties', {})) | set(after[name].get('Properties', {})):
            a, b = before[name].get('Properties', {}).get(prop), after[name].get('Properties', {}).get(prop)
            if a != b:
                if (name, name, prop) not in approved:
                    raise ValueError(f'Unexpected screen property change: {name}.{prop}')
                changes.append({'control': name, 'property': prop, 'before_sha256': sha(str(a)), 'after_sha256': sha(str(b))})
    return {'control_count': len(old), 'changes': changes, 'unapproved_changes': 0}

def apply(screens, manifest):
    """Return changed copies; validate every baseline before mutating any copy."""
    inventory(screens)
    for entry in manifest['changes']:
        screen = screens[entry['screen']]
        if 'property' not in entry:
            continue
        owner = property_owner(screen, entry['screen'], entry['control'])
        if entry.get('before_absent'):
            if entry['property'] in owner.get('Properties', {}):
                raise ValueError(f"Expected absent baseline property: {entry['control']}.{entry['property']}")
            continue
        current = owner['Properties'][entry['property']]
        if entry.get('mode') == 'preserve_first_statement_replace_tail':
            prefix, sep, tail = current.partition(';')
            if not sep or not prefix.startswith('=Set(varCommuteReportBase111,'):
                raise ValueError('Unexpected commute URL statement; refuse replacement')
            if sha(tail) != entry['before_tail_sha256']:
                raise ValueError('Changed current OnVisible tail; reconcile before applying')
        elif 'before_sha256' in entry:
            if sha(current) != entry['before_sha256']:
                raise ValueError(f"Baseline mismatch: {entry['control']}.{entry['property']}")
        elif current != entry['before']:
            raise ValueError(f"Baseline mismatch: {entry['control']}.{entry['property']}")
    payroll_root = control(screens['scrPayroll'], 'conscrPayrollRoot')
    if semantic_sha(payroll_root) != manifest['baseline']['payroll_root_semantic_sha256']:
        raise ValueError('Payroll root differs from reviewed baseline; reconcile first')
    result = copy.deepcopy(screens)
    for entry in manifest['changes']:
        if 'property' not in entry:
            continue
        owner = property_owner(result[entry['screen']], entry['screen'], entry['control'])
        value = ((DELTA / entry['after_file']).read_text().rstrip()
                 if 'after_file' in entry else entry['after'])
        if entry.get('mode') == 'preserve_first_statement_replace_tail':
            value = owner['Properties'][entry['property']].partition(';')[0] + ';' + value.removeprefix('=')
        owner['Properties'][entry['property']] = value
    root = control(result['scrPayroll'], 'conscrPayrollRoot')
    body = control(root, 'conPayBody')
    matches = [x for x in body['Children'] if 'conPaySummary' in x]
    if len(matches) != 1:
        raise ValueError('Expected exactly one existing summary')
    body['Children'].remove(matches[0])
    position = next(i for i, x in enumerate(root['Children']) if 'conPayBody' in x)
    root['Children'].insert(position, matches[0])
    change_evidence(screens, result, manifest)
    return result

class SourceDumper(yaml.SafeDumper):
    pass

def _str(dumper, value):
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='|' if '\n' in value else None)
SourceDumper.add_representer(str, _str)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--readback', type=Path, required=True, help='Verified current Src folder')
    parser.add_argument('--output', type=Path, required=True, help='New empty local output directory')
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output already exists; use a new empty directory (no overwrite).')
    manifest = json.loads((DELTA / 'manifest.json').read_text())
    documents, originals = load_readback(args.readback, manifest)
    changed = apply(originals, manifest)
    args.output.mkdir(parents=True)
    for name in ['scrStaffMasterSearch', 'scrPayroll']:
        document = documents[f'{name}.pa.yaml']
        document['Screens'][name] = changed[name]
        (args.output / f'{name}.pa.yaml').write_text(yaml.dump(
            document, Dumper=SourceDumper, sort_keys=False, allow_unicode=True, width=100000))
    (args.output / 'delta-verification.json').write_text(json.dumps(change_evidence(originals, changed, manifest), indent=2) + '\n')
    print('Local before-state checks passed. Wrote two candidate screens. No app changes performed.')
if __name__ == '__main__':
    main()
