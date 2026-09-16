"""Validate approved existing-property edits and synchronize a Canvas package.

This is a guarded compatibility bridge, not a general Power Fx compiler. New
controls, connections, and unlisted source changes fail before deployment.
"""
import copy
import hashlib
import json
from pathlib import Path
import zipfile

import yaml


class GateError(ValueError):
    pass


# These baseline properties exist in the runtime package but are omitted from
# Studio YAML because they have their default value. Keep this allowlist narrow;
# this does not permit new controls or arbitrary new properties.
OMITTED_BASELINE = {('Src/Screen1.pa.yaml', 'conHeader111', 'X'): '=0'}


def require(ok, message):
    if not ok:
        raise GateError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_archive(path):
    with zipfile.ZipFile(path) as z:
        result = {}
        for info in z.infolist():
            name = info.filename.replace('\\', '/')
            require(not name.startswith('/') and '..' not in Path(name).parts, 'unsafe archive path')
            if info.is_dir():
                continue
            require(name not in result, 'duplicate archive entry')
            result[name] = z.read(info)
        return result


def nodes(value, name):
    found = []
    if isinstance(value, dict):
        if name in value and isinstance(value[name], dict) and 'Properties' in value[name]:
            found.append(value[name])
        for child in value.values():
            found.extend(nodes(child, name))
    elif isinstance(value, list):
        for child in value:
            found.extend(nodes(child, name))
    return found


def runtime_rules(value, control, prop):
    found = []
    if isinstance(value, dict):
        if value.get('Name') == control:
            found.extend(r for r in value.get('Rules', []) if r.get('Property') == prop)
        for child in value.values():
            found.extend(runtime_rules(child, control, prop))
    elif isinstance(value, list):
        for child in value:
            found.extend(runtime_rules(child, control, prop))
    return found


def formula_literal(value):
    require(isinstance(value, str) and value.startswith('='), 'expected a Power Fx formula')
    return value[1:]


def build(root, output, manifest=None):
    root, output = Path(root), Path(output)
    config = json.loads((root / 'config/apps/staff-master.json').read_text())
    original = root / config['baseline_msapp']
    require(digest(original.read_bytes()) == config['baseline_sha256'], 'baseline digest mismatch')
    archive = read_archive(original)
    if manifest is None:
        manifest = json.loads((root / 'automation/change.json').read_text())
    require(manifest['approved'] is True and manifest['issue'] > 0, 'missing approval record')
    require(manifest['target'] == config['target'], 'target outside approved isolated environment')
    changes = manifest['changes']
    require(len(changes) <= 100, 'too many changes')
    source = {}
    base_docs = {}
    for name, data in archive.items():
        if name.startswith('Src/') and name.endswith('.pa.yaml'):
            base_docs[name] = yaml.safe_load(data)
            path = root / 'powerapps/canvas-v3' / name
            require(path.is_file(), f'missing active source: {name}')
            source[name] = path.read_bytes()
    actual_paths = {p.relative_to(root / 'powerapps/canvas-v3').as_posix()
                    for p in (root / 'powerapps/canvas-v3/Src').rglob('*.pa.yaml')}
    require(actual_paths == set(source), 'source file addition or removal is not approved')
    actual_docs = {k: yaml.safe_load(v) for k, v in source.items()}
    expected_docs = copy.deepcopy(base_docs)
    compiled = {k: json.loads(v) for k, v in archive.items()
                if k.startswith('Controls/') and k.endswith('.json')}
    seen = set()
    for change in changes:
        name, control, prop = change['source'], change['control'], change['property']
        identity = (name, control, prop)
        require(identity not in seen, 'duplicate property edit')
        seen.add(identity)
        require(name in expected_docs, 'unknown source file')
        matches = nodes(expected_docs[name], control)
        require(len(matches) == 1, f'control must be unique: {control}')
        props = matches[0]['Properties']
        if prop not in props:
            require(OMITTED_BASELINE.get(identity) == change['before'],
                    f'property addition is not supported: {control}.{prop}')
        else:
            require(props[prop] == change['before'], f'baseline formula mismatch: {control}.{prop}')
        formula_literal(change['after'])
        props[prop] = change['after']
        rules = [r for data in compiled.values() for r in runtime_rules(data, control, prop)]
        require(len(rules) == 1, f'compiled rule must be unique: {control}.{prop}')
        require(rules[0]['InvariantScript'] == formula_literal(change['before']), 'compiled baseline mismatch')
        rules[0]['InvariantScript'] = formula_literal(change['after'])
    require(expected_docs == actual_docs, 'unlisted source change or manifest/source mismatch')
    archive.update(source)
    for name, data in compiled.items():
        archive[name] = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()
    archive['packed.json'] = json.dumps({
        'PackedStructureVersion': '0.1',
        'PackingClient': {'Name': 'StaffMasterApprovedPropertyBridge', 'Version': '1.0'},
        'LoadConfiguration': {'LoadFromYaml': False},
    }).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(archive):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, archive[name])
    return {'msapp_sha256': digest(output.read_bytes()), 'edits': len(changes),
            'source_sha256': {k: digest(v) for k, v in source.items()},
            'target': manifest['target'], 'load_from_yaml': False}


def verify_download(path, root, manifest):
    archive = read_archive(path)
    # A release can update dozens of properties in the same large source file.
    # Parse each immutable downloaded document once; keep every comparison below.
    documents = {k: yaml.safe_load(v) for k, v in archive.items()
                 if k.startswith('Src/') and k.endswith('.pa.yaml')}
    compiled = [json.loads(v) for k, v in archive.items()
                if k.startswith('Controls/') and k.endswith('.json')]
    for change in manifest['changes']:
        doc = documents[change['source']]
        matches = nodes(doc, change['control'])
        require(len(matches) == 1, 'server source control mismatch')
        require(matches[0]['Properties'][change['property']] == change['after'], 'server source value mismatch')
        rules = [r for data in compiled for r in runtime_rules(data, change['control'], change['property'])]
        require(len(rules) == 1 and rules[0]['InvariantScript'] == formula_literal(change['after']),
                'server compiled value mismatch')
    # Compare all semantic source, including properties not mentioned in the manifest.
    for k, v in archive.items():
        if k.startswith('Src/') and k.endswith('.pa.yaml') and not k.endswith('_EditorState.pa.yaml'):
            require(documents[k] == yaml.safe_load((Path(root) / 'powerapps/canvas-v3' / k).read_bytes()),
                    f'server source drift: {k}')
    return {'server_sha256': digest(Path(path).read_bytes()), 'source_and_rules': 'exact'}


def retarget_fixture(root, manifest, formula):
    """Only acceptance tests call this; the desired UI expectation stays unchanged."""
    root = Path(root)
    result = copy.deepcopy(manifest)
    require(len(result['changes']) == 1, 'acceptance fixture expects one edit')
    change = result['changes'][0]
    path = root / 'powerapps/canvas-v3' / change['source']
    text = path.read_text()
    old = f"{change['property']}: {change['after']}"
    new = f"{change['property']}: {formula}"
    require(text.count(old) == 1, 'fixture replacement must be unique')
    path.write_text(text.replace(old, new))
    change['after'] = formula
    return result
