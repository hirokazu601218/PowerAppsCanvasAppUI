"""Deployment guards for the Studio-compiled lightweight baseline."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/automation'))
import bridge
import lightweight_transaction as lt

class LightweightGuardTests(unittest.TestCase):
    def setUp(self):
        self.archive = {'Src/scrStaffMasterSearch.pa.yaml': b'Screens: {}',
                        'Src/App.pa.yaml': b'App: {}',
                        'Controls/1.json': json.dumps({'Name':'label','Rules':[{'Property':'Text','InvariantScript':'"expected"'}]}).encode()}
        self.cfg = {'target': {'app_id':'362ac991-eead-4f07-8373-afdb3ebfdba1',
                               'environment_id':'68e00049-b7e5-eda6-9888-9a3cc493c5be'}}
        self.expected = {**self.cfg['target'], 'source_hashes':lt.source_hashes(self.archive),
                         'runtime_hashes':lt.runtime_hashes(self.archive)}
    def test_matching_baseline(self):
        lt.verify_baseline(self.archive, self.expected, self.cfg)
    def test_wrong_app_is_rejected(self):
        self.cfg['target']['app_id'] = 'another'
        with self.assertRaises(bridge.GateError): lt.verify_baseline(self.archive,self.expected,self.cfg)
    def test_wrong_environment_is_rejected(self):
        self.cfg['target']['environment_id'] = 'another'
        with self.assertRaises(bridge.GateError): lt.verify_baseline(self.archive,self.expected,self.cfg)
    def test_source_drift_is_rejected(self):
        self.archive['Src/App.pa.yaml'] += b'\n# changed'
        with self.assertRaises(bridge.GateError): lt.verify_baseline(self.archive,self.expected,self.cfg)
    def test_compiled_drift_is_rejected_even_if_source_matches(self):
        self.archive['Controls/1.json'] = json.dumps({'Name':'label','Rules':[{'Property':'Text','InvariantScript':'"wrong"'}]}).encode()
        with self.assertRaises(bridge.GateError): lt.verify_baseline(self.archive,self.expected,self.cfg)
    def test_legacy_structure_is_rejected_even_if_hashes_match(self):
        self.archive['Src/Screen1.pa.yaml'] = self.archive.pop('Src/scrStaffMasterSearch.pa.yaml')
        self.expected['source_hashes'] = lt.source_hashes(self.archive)
        with self.assertRaises(bridge.GateError): lt.verify_baseline(self.archive,self.expected,self.cfg)
    def test_legacy_solution_template_cannot_erase_dataverse_sources(self):
        legacy = Path(__file__).resolve().parents[2] / 'powerapps/solution-src/CanvasApps/crb3c_v111_99a38.meta.xml'
        required = json.loads((Path(__file__).resolve().parents[2] / 'automation/lightweight-expected.json').read_text())['required_database_sources']
        with self.assertRaises(bridge.GateError):
            lt.verify_database_references(legacy, required)

    def test_studio_published_after_save_is_valid(self):
        self.assertTrue(lt.published_without_newer_draft({'status':'Ready', 'lastDraftVersion':'2026-09-24T08:57:16Z', 'lastPublishTime':'2026-09-24T08:58:21.957018Z'}))
    def test_newer_draft_is_rejected(self):
        self.assertFalse(lt.published_without_newer_draft({'status':'Ready', 'lastDraftVersion':'2026-09-24T08:59:00Z', 'lastPublishTime':'2026-09-24T08:58:21.957018Z'}))
    def test_missing_or_non_ready_metadata_is_rejected(self):
        for props in ({}, {'status':'Ready','lastDraftVersion':None,'lastPublishTime':None}, {'status':'Saving','lastDraftVersion':'2026-09-24T08:57:16Z','lastPublishTime':'2026-09-24T08:58:21Z'}):
            self.assertFalse(lt.published_without_newer_draft(props))
if __name__ == '__main__':
    unittest.main()

