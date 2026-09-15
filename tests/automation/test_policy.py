import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/automation'))
import bridge
import policy


class PolicyTests(unittest.TestCase):
    def test_failure_identity_ignores_only_volatile_fields(self):
        self.assertEqual(policy.fingerprint('A', 'e2e', 'failure 2026-09-15T10:00:00Z'),
                         policy.fingerprint('A', 'e2e', 'failure 2026-09-16T10:02:00Z'))
        self.assertNotEqual(policy.fingerprint('A', 'e2e', 'expected 25, got 0'),
                            policy.fingerprint('A', 'e2e', 'expected 25, got 2'))
        self.assertNotEqual(policy.fingerprint('A', 'auth', 'x'), policy.fingerprint('A', 'e2e', 'x'))

    def test_two_failures_allow_materially_new_remedy(self):
        old = {'id': 'first', 'edit': {'Text': 'bad'}}
        renamed = {'id': 'renamed', 'edit': {'Text': 'bad'}}
        new = {'id': 'new', 'edit': {'Text': 'fixed'}}
        history = [{'remedy_key': policy.remedy_key(old)}] * 2
        failure = {'stage': 'change_test'}
        self.assertEqual(policy.decide(history, failure, [renamed, new])['remedy'], 'new')
        self.assertEqual(policy.decide(history, failure, [renamed])['state'], 'STOPPED')

    def test_auth_scope_and_restore_fail_closed(self):
        for stage in ('auth', 'scope'):
            self.assertEqual(policy.decide([], {'stage': stage}, [{'id':'x','edit':{}}])['state'], 'BLOCKED')
        self.assertEqual(policy.decide([], {'stage':'restore'}, [])['state'], 'RESTORE_FAILED')

    def test_no_partial_success_promotes(self):
        all_ok = dict.fromkeys(('build','auth','import','publish','readback','change_test','p0'), 'success')
        self.assertTrue(policy.promotion(all_ok))
        for gate in all_ok:
            for state in ('failure', 'skipped', 'cancelled', None):
                self.assertFalse(policy.promotion({**all_ok, gate: state}))

    def test_build_is_deterministic_and_roundtrips(self):
        manifest=json.loads((ROOT/'automation/change.json').read_text())
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'a.msapp',Path(t)/'b.msapp'
            self.assertEqual(bridge.build(ROOT,a),bridge.build(ROOT,b))
            bridge.verify_download(a,ROOT,manifest)

    def test_manifest_scope_before_value_and_unlisted_change_are_rejected(self):
        manifest=json.loads((ROOT/'automation/change.json').read_text())
        with tempfile.TemporaryDirectory() as t:
            for variation in ('target','before','after','duplicate'):
                altered=copy.deepcopy(manifest)
                if variation=='target': altered['target']['app_id']='another-app'
                elif variation=='duplicate': altered['changes']*=2
                else: altered['changes'][0][variation]='="unexpected"'
                with self.assertRaises(bridge.GateError, msg=variation):
                    bridge.build(ROOT,Path(t)/'bad.msapp',altered)


if __name__ == '__main__':
    unittest.main()
