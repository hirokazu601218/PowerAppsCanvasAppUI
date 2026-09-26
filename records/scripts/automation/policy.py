"""Failure identity, distinct remedies and strict promotion decisions."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def normalize(error):
    text = re.sub(r'\x1b\[[0-9;]*m', '', error)
    text = re.sub(r'\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b', '<uuid>', text)
    text = re.sub(r'\b\d{4}-\d{2}-\d{2}T[\d:.]+Z\b', '<time>', text)
    text = re.sub(r'/home/runner/work/_temp/[^\s]+', '<temp>', text)
    return ' '.join(text.split())


def fingerprint(case_id, stage, error):
    raw = json.dumps([case_id, stage, normalize(error)], ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def remedy_key(remedy):
    # The effective edit, not its human label, determines whether a remedy is new.
    return hashlib.sha256(json.dumps(remedy['edit'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def decide(history, failure, remedies):
    if failure['stage'] in {'auth', 'scope', 'restore'}:
        return {'state': 'RESTORE_FAILED' if failure['stage'] == 'restore' else 'BLOCKED'}
    used = {h.get('remedy_key') for h in history}
    for remedy in remedies:
        key = remedy_key(remedy)
        if key not in used:
            return {'state': 'REPAIRING', 'remedy': remedy['id'], 'remedy_key': key}
    return {'state': 'STOPPED', 'reason': 'no_untried_remedy'}


def promotion(gates):
    required = ('build', 'auth', 'import', 'publish', 'readback', 'change_test', 'p0')
    return all(gates.get(key) == 'success' for key in required)


def append(path, event):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {'at': datetime.now(timezone.utc).isoformat(), **event}
    with path.open('a', encoding='utf-8') as file:
        file.write(json.dumps(row, ensure_ascii=False) + '\n')
    return row
