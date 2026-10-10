#!/usr/bin/env python3
"""Read-only, exact payroll screen comparison with one documented serializer rule.

Only conscrPayrollRoot.LayoutAlignItems=Start may be omitted by the reader.
No other missing, added, reordered or changed source is accepted.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import yaml


def compare(expected, actual):
    result = copy.deepcopy(actual)
    e = expected['Screens']['scrPayroll']
    a = result['Screens']['scrPayroll']
    def root(screen):
        entries = [v['conscrPayrollRoot'] for v in screen['Children'] if 'conscrPayrollRoot' in v]
        if len(entries) != 1:
            raise ValueError('Expected exactly one payroll root')
        return entries[0]
    er, ar = root(e), root(a)
    expected_children = {name:node for entry in er.get('Children', []) for name,node in entry.items()}
    for name in ['conscrPayrollHeader','conPayrollTargets','conPaySummary','conPayBody']:
        if expected_children.get(name,{}).get('Properties',{}).get('AlignInContainer') != '=AlignInContainer.SetByContainer':
            raise ValueError('Expected source must explicitly declare four child inheritance properties')
    props = ar.get('Properties', {})
    if er.get('Properties', {}).get('LayoutAlignItems') != '=LayoutAlignItems.Start':
        raise ValueError('Expected source must explicitly declare root Start')
    normalized = []
    if 'LayoutAlignItems' not in props:
        props['LayoutAlignItems'] = '=LayoutAlignItems.Start'
        normalized.append('conscrPayrollRoot.LayoutAlignItems: omitted -> =LayoutAlignItems.Start')
    if result != expected:
        raise ValueError('Payroll readback differs beyond the single documented root Start omission')
    return {'status': 'PASS', 'normalized': normalized, 'other_differences': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected', required=True, type=Path)
    p.add_argument('--actual', required=True, type=Path)
    args = p.parse_args()
    result = compare(yaml.safe_load(args.expected.read_text()), yaml.safe_load(args.actual.read_text()))
    for label,path in [('expected',args.expected),('actual',args.actual)]:
        result[label+'_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__ == '__main__': main()
