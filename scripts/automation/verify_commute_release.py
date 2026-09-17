"""Read-only verification of the Studio-compiled v1.18 release.

Studio stores gallery template rules on its generated direct template child and
omits Selectable=true from YAML. Validate those representations explicitly.
"""
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.automation.bridge import read_archive, nodes, digest, require

def controls(value, name):
    result = []
    if isinstance(value, dict):
        if value.get('Name') == name and 'Rules' in value:
            result.append(value)
        for child in value.values():
            result.extend(controls(child, name))
    elif isinstance(value, list):
        for child in value:
            result.extend(controls(child, name))
    return result

def verify(path, root=ROOT):
    root = Path(root)
    archive = read_archive(path)
    config = json.loads((root / 'config/apps/staff-master.json').read_text())
    baseline_path = root / config['baseline_msapp']
    require(digest(baseline_path.read_bytes()) == config['baseline_sha256'], 'baseline digest')
    baseline = read_archive(baseline_path)
    manifest = json.loads((root / 'src/staff-master/patches/v1.18/manifest.json').read_text())
    documents = {k: yaml.safe_load(v) for k,v in archive.items() if k.startswith('Src/') and k.endswith('.pa.yaml')}
    compiled = [json.loads(v) for k,v in archive.items() if k.startswith('Controls/') and k.endswith('.json')]
    for change in manifest['changes']:
        name, prop, expected = change['control'], change['property'], change['after']
        ns = nodes(documents[change['source']], name)
        require(len(ns) == 1, 'source control not unique: '+name)
        actual = ns[0]['Properties'].get(prop)
        if (name,prop) == ('galCommute111','Selectable') and actual is None:
            require(expected == '=true', 'unexpected omitted default')
        else:
            require(actual == expected, 'source formula mismatch: '+name+'.'+prop)
        cs = [c for value in compiled for c in controls(value,name)]
        require(len(cs)==1, 'runtime control not unique: '+name)
        owner = cs[0]
        if (name,prop) in {('galCommute111','ItemAccessibleLabel'),('galCommute111','TemplateFill'),('galStaff111','OnSelect')}:
            children = [c for c in owner.get('Children',[]) if c.get('Template',{}).get('Name') == 'galleryTemplate']
            require(len(children)==1, 'gallery template not unique: '+name)
            owner=children[0]
        rules=[r for r in owner.get('Rules',[]) if r['Property']==prop]
        require(len(rules)==1 and rules[0]['InvariantScript']==expected[1:], 'runtime formula mismatch: '+name+'.'+prop)
    for name, doc in documents.items():
        if not name.endswith('_EditorState.pa.yaml'):
            require(doc==yaml.safe_load((root/'powerapps/canvas-v3'/name).read_bytes()),'source drift: '+name)
    # All compiled rules, data-source metadata and connections must match the
    # immutable Studio-published baseline, including untouched controls.
    exact = [n for n in baseline if n.startswith(('Controls/','Connections/','References/')) and n.endswith('.json')]
    require(set(exact)=={n for n in archive if n.startswith(('Controls/','Connections/','References/')) and n.endswith('.json')}, 'metadata file set changed')
    for name in exact:
        require(json.loads(archive[name])==json.loads(baseline[name]),'runtime/metadata drift: '+name)
    return {'server_sha256':digest(Path(path).read_bytes()),'properties':len(manifest['changes']),'source_and_rules':'exact','runtime_and_connections':'exact'}

if __name__=='__main__':
    result=verify(Path(sys.argv[1]))
    print(json.dumps(result,indent=2))
    if len(sys.argv)>2:
        Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
