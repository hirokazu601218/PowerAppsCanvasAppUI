"""Keep the PR gate fail-closed on missing coverage and wrong app IDs."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.testing.validate_selection import APP_ID, ENV_ID, SelectionError, validate


class TestSelectionGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        script = self.repo / 'e2e/current-app/search.test.ts'
        script.parent.mkdir(parents=True)
        script.write_text("test('UT-SRCH-001 checks search', () => {});\n"
                          "test('IT-SRCH-DETAIL-001 checks detail', () => {});\n", encoding='utf-8')
        self.source = 'src/staff-master/Screen1.pa.yaml'
        self.record = 'docs/testing/change-records/change-123.json'
        record = self.repo / self.record
        record.parent.mkdir(parents=True)
        self.data = {
            'schema_version': 1, 'change_id': 'CHANGE-123',
            'target': {'environment_id': ENV_ID, 'app_id': APP_ID},
            'changes': [{'path': self.source, 'component': 'btnSearch111.OnSelect',
                         'unit_case_ids': ['UT-SRCH-001'], 'expected_result': 'one staff'}],
            'integration': {'required': True, 'reason': 'Search passes selection to detail',
                            'case_ids': ['IT-SRCH-DETAIL-001']},
            'system_test': {'status': 'deferred', 'reason': 'business scenarios pending'},
            'cases': [
                {'id': 'UT-SRCH-001', 'level': 'unit', 'test_file': 'e2e/current-app/search.test.ts'},
                {'id': 'IT-SRCH-DETAIL-001', 'level': 'integration', 'test_file': 'e2e/current-app/search.test.ts'},
            ],
        }
        self.save()

    def save(self):
        (self.repo / self.record).write_text(json.dumps(self.data), encoding='utf-8')

    def test_valid_selection_runs_only_its_named_cases(self):
        result = validate(self.repo, {self.source, self.record})
        self.assertEqual(result['case_ids'], ['IT-SRCH-DETAIL-001', 'UT-SRCH-001'])
        self.assertEqual(result['test_files'], ['e2e/current-app/search.test.ts'])

    def test_test_code_change_runs_its_own_cases(self):
        result = validate(self.repo, {'e2e/current-app/search.test.ts'}, smoke_if_tests_changed=True)
        self.assertEqual(result['case_ids'], ['IT-SRCH-DETAIL-001', 'UT-SRCH-001'])
        self.assertEqual(result['test_files'], ['e2e/current-app/search.test.ts'])

    def test_changed_test_file_is_not_hidden_by_another_selected_case(self):
        navigation = self.repo / 'e2e/current-app/navigation.test.ts'
        navigation.write_text("test('UT-HOME-001 opens staff list', () => {});\n", encoding='utf-8')
        result = validate(self.repo, {self.source, self.record, 'e2e/current-app/navigation.test.ts'},
                          smoke_if_tests_changed=True)
        self.assertEqual(result['test_files'], ['e2e/current-app/navigation.test.ts',
                                                'e2e/current-app/search.test.ts'])
        self.assertIn('UT-HOME-001', result['case_ids'])

    def test_deleted_test_file_cannot_silently_pass(self):
        with self.assertRaisesRegex(SelectionError, 'changed test file is missing'):
            validate(self.repo, {'e2e/current-app/missing.test.ts'}, smoke_if_tests_changed=True)

    def test_missing_record_does_not_mark_app_change_as_tested(self):
        with self.assertRaisesRegex(SelectionError, 'without a changed selection record'):
            validate(self.repo, {self.source})

    def test_additional_changed_file_must_be_covered(self):
        with self.assertRaisesRegex(SelectionError, 'without test selection'):
            validate(self.repo, {self.source, 'src/staff-master/Other.pa.yaml', self.record})

    def test_unit_test_cannot_be_omitted(self):
        self.data['changes'][0]['unit_case_ids'] = []
        self.save()
        with self.assertRaisesRegex(SelectionError, 'every changed component needs a unit case'):
            validate(self.repo, {self.source, self.record})

    def test_integration_is_required_when_impact_is_declared(self):
        self.data['integration']['case_ids'] = []
        self.save()
        with self.assertRaisesRegex(SelectionError, 'must match required flag'):
            validate(self.repo, {self.source, self.record})

    def test_wrong_app_id_fails_before_live_execution(self):
        self.data['target']['app_id'] = '362ac991-eead-4f07-8373-afdb3ebfdba1'
        self.save()
        with self.assertRaisesRegex(SelectionError, 'wrong environment or App ID'):
            validate(self.repo, {self.source, self.record})

    def test_comment_only_case_id_does_not_count(self):
        (self.repo / 'e2e/current-app/search.test.ts').write_text('// UT-SRCH-001\n', encoding='utf-8')
        with self.assertRaisesRegex(SelectionError, 'missing test title'):
            validate(self.repo, {self.source, self.record})


if __name__ == '__main__':
    unittest.main()
