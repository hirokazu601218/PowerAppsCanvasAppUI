import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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

    def test_preview_order_requires_approval_and_exact_compiled_layers(self):
        # Fixed synthetic v1.17 repair fixture: independent of the current release.
        import zipfile
        manifest=json.loads((ROOT/'automation/change.json').read_text())
        manifest.update(changes=[],ledger_preview_to_front=True)
        children=[{n:{'Properties':{}}} for n in ['ScreenContainer1','pdfLedger111','conStaffMaster111']]
        document={'Screens':{'Screen1':{'Properties':{},'Children':children}}}
        compiled={'Name':'Screen1','Children':[{'Name':n,'Rules':[{'Property':'ZIndex','InvariantScript':v}]} for n,v in [('pdfLedger111','3'),('conStaffMaster111','4')]]}
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'config/apps').mkdir(parents=True);(root/'powerapps/canvas-v3/Src').mkdir(parents=True)
            original=root/'baseline.msapp'
            with zipfile.ZipFile(original,'w') as z:
                z.writestr('Src/Screen1.pa.yaml',bridge.yaml.safe_dump(document))
                z.writestr('Controls/Screen1.json',json.dumps(compiled))
            (root/'config/apps/staff-master.json').write_text(json.dumps({'target':manifest['target'],'baseline_msapp':'baseline.msapp','baseline_sha256':bridge.digest(original.read_bytes())}))
            desired=copy.deepcopy(document);cs=desired['Screens']['Screen1']['Children'];cs[1],cs[2]=cs[2],cs[1]
            (root/'powerapps/canvas-v3/Src/Screen1.pa.yaml').write_text(bridge.yaml.safe_dump(desired))
            altered=copy.deepcopy(manifest);altered.pop('ledger_preview_to_front')
            with self.assertRaisesRegex(bridge.GateError,'unlisted source change'):
                bridge.build(root,root/'unapproved.msapp',altered)
            package=root/'approved.msapp';bridge.build(root,package,manifest)
            archive=bridge.read_archive(package)
            docs={k:bridge.yaml.safe_load(v) for k,v in archive.items() if k.startswith('Src/') and k.endswith('.pa.yaml')}
            ruleset=[json.loads(v) for k,v in archive.items() if k.startswith('Controls/') and k.endswith('.json')]
            bridge.ledger_preview_order(docs,ruleset,manifest)
            rules=[r for d in ruleset for r in bridge.runtime_rules(d,'pdfLedger111','ZIndex')]
            rules[0]['InvariantScript']='2'
            with self.assertRaisesRegex(bridge.GateError,'compiled layer mismatch'):
                bridge.ledger_preview_order(docs,ruleset,manifest)

    def test_manifest_scope_before_value_and_unlisted_change_are_rejected(self):
        manifest=json.loads((ROOT/'automation/change.json').read_text())
        doc=bridge.yaml.safe_load((ROOT/'powerapps/canvas-v3/Src/Screen1.pa.yaml').read_text())
        value=bridge.nodes(doc,'lblMeta111')[0]['Properties']['Text']
        manifest['changes']=[{'source':'Src/Screen1.pa.yaml','control':'lblMeta111','property':'Text','before':value,'after':value}]
        with tempfile.TemporaryDirectory() as t:
            for variation in ('target','before','after','duplicate'):
                altered=copy.deepcopy(manifest)
                if variation=='target': altered['target']['app_id']='another-app'
                elif variation=='duplicate': altered['changes']*=2
                else: altered['changes'][0][variation]='="unexpected"'
                with self.assertRaises(bridge.GateError, msg=variation):
                    bridge.build(ROOT,Path(t)/'bad.msapp',altered)


    def test_omitted_baseline_property_is_not_a_general_addition_permission(self):
        manifest=json.loads((ROOT/'automation/change.json').read_text())
        # Keep this regression independent of the current release manifest.
        # The original v1.11 fixture omits X=0 from YAML but carries its runtime rule.
        baseline=ROOT/'powerapps/solution-src/CanvasApps/crb3c_v111_99a38_DocumentUri.msapp'
        archive=bridge.read_archive(baseline)
        header={'source':'Src/Screen1.pa.yaml','control':'conHeader111','property':'X',
                'before':'=0','after':'=16'}
        with tempfile.TemporaryDirectory() as t, patch.object(bridge,'read_archive',return_value=archive):
            for variation in ('wrong_default','unknown_property'):
                altered=copy.deepcopy(manifest);edit=copy.deepcopy(header)
                if variation=='wrong_default':edit['before']='=1'
                else:edit['property']='UnapprovedProperty'
                altered['changes']=[edit]
                with self.assertRaisesRegex(bridge.GateError,'property addition is not supported'):
                    bridge.build(ROOT,Path(t)/'bad.msapp',altered)



if __name__ == '__main__':
    unittest.main()
