"""Exercise the boundary between recorded publication and verified documents."""

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.automation.validate_current_app_postpublish import (
    ReconcileError, preflight, verify_readback,
)
from scripts.testing.validate_selection import APP_ID, ENV_ID


class PostpublishGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        for args in (("init", "-q"), ("config", "user.email", "test@example.invalid"),
                     ("config", "user.name", "Test")):
            subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)
        self.change_id = "CHANGE-123"
        self.target = {"environment_id": ENV_ID, "app_id": APP_ID}
        self.source = "src/staff-master/Screen1.pa.yaml"
        self.write(self.source, "Screen1: {}\n")
        self.write("e2e/current-app/search.test.ts",
                   "test('UT-SRCH-001 search', () => {});\n"
                   "test('IT-SRCH-DETAIL-001 detail', () => {});\n")
        self.request = "docs/changes/requests/change-123.json"
        self.selection = "docs/testing/change-records/change-123.json"
        self.evidence = "docs/verification/postpublish/change-123.json"
        self.write(self.request, json.dumps({
            "schema_version": 1, "change_id": self.change_id, "target": self.target,
            "request_text": "Search a staff number and display the same staff in detail",
            "requirement_ids": ["SCR002-LT-007"],
            "acceptance_criteria": ["The selected number agrees with the detail"],
        }))
        self.write(self.selection, json.dumps({
            "schema_version": 1, "change_id": self.change_id, "target": self.target,
            "changes": [{"path": self.source, "component": "btnSearch.OnSelect",
                         "unit_case_ids": ["UT-SRCH-001"], "expected_result": "found"}],
            "integration": {"required": True, "reason": "Pass selected staff from list to detail",
                            "case_ids": ["IT-SRCH-DETAIL-001"]},
            "system_test": {"status": "deferred", "reason": "business scenarios pending"},
            "cases": [
                {"id": "UT-SRCH-001", "level": "unit", "test_file": "e2e/current-app/search.test.ts"},
                {"id": "IT-SRCH-DETAIL-001", "level": "integration", "test_file": "e2e/current-app/search.test.ts"},
            ],
        }))
        self.commit("published source")
        self.source_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        self.package = self.repo / "readback.msapp"
        self.package.write_bytes(b"synthetic readback")
        self.record = {
            "schema_version": 1, "change_id": self.change_id, "target": self.target,
            "source_commit": self.source_commit,
            "documentation_base_commit": self.source_commit,
            "requirement_ids": ["SCR002-LT-007"],
            "selected_case_ids": ["IT-SRCH-DETAIL-001", "UT-SRCH-001"],
            "source_comparison": {
                "result": "MATCH", "checked_paths": [self.source],
                "method_and_findings": "Compared selected screen formula and staff detail with readback",
            },
            "publication": {
                "version": "2026-09-26T09:00:00Z",
                "player_observed_at": "2026-09-26T09:05:00Z",
                "player_app_id": APP_ID, "player_result": "PASS",
                "player_observation": "Searched staff 011 and observed matching detail in Player",
                "download_sha256": hashlib.sha256(self.package.read_bytes()).hexdigest(),
            },
        }
        self.write(self.evidence, json.dumps(self.record))
        for path in ("docs/requirements/requirements.md", "docs/design/basic-design.md",
                     "docs/design/detailed-design.md"):
            self.write(path, f"# {self.change_id} - 2026-09-26T09:00:00Z documented after publication\n")
        self.spec = "docs/testing/test-specification.md"
        self.write(self.spec, "CHANGE-123: 2026-09-26T09:00:00Z IT-SRCH-DETAIL-001: list selection goes to matching detail\n")
        self.commit("postpublish documents")
        self.metadata = {
            "status": "Ready", "lastPublishTime": self.record["publication"]["version"],
            "lastDraftVersion": self.record["publication"]["version"],
            "appOpenUri": f"https://apps.powerapps.com/play/e/{ENV_ID}/a/{APP_ID}?tenantId=example",
        }
        self.before = self.repo / "before.json"
        self.after = self.repo / "after.json"
        self.before.write_text(json.dumps(self.metadata))
        self.after.write_text(json.dumps(self.metadata))

    def write(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self, message):
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=self.repo, check=True, capture_output=True)

    def test_verified_release_and_documents(self):
        state = verify_readback(self.repo, self.change_id, self.package, self.before, self.after)
        self.assertEqual(state["source_commit"], self.source_commit)
        self.assertEqual(state["case_ids"], ["IT-SRCH-DETAIL-001", "UT-SRCH-001"])

    def test_rejects_missing_updated_integration_specification(self):
        self.write(self.spec, "Old unrelated specification\n")
        self.commit("drop integration coverage")
        with self.assertRaisesRegex(ReconcileError, "integration case IDs"):
            preflight(self.repo, self.change_id)

    def test_rejects_unrecorded_app_source_change_after_publication(self):
        self.write(self.source, "Screen1: changed after publication\n")
        self.commit("unrecorded source")
        with self.assertRaisesRegex(ReconcileError, "app source changed"):
            preflight(self.repo, self.change_id)

    def test_rejects_wrong_readback_even_with_ready_metadata(self):
        self.package.write_bytes(b"different package")
        with self.assertRaisesRegex(ReconcileError, "PAC readback differs"):
            verify_readback(self.repo, self.change_id, self.package, self.before, self.after)

    def test_rejects_missing_published_source_coverage(self):
        self.record["source_comparison"]["checked_paths"] = []
        self.write(self.evidence, json.dumps(self.record))
        self.commit("omit source comparison")
        with self.assertRaisesRegex(ReconcileError, "cover every selected source path"):
            preflight(self.repo, self.change_id)

    def test_rejects_saved_version_newer_than_published_version(self):
        metadata = dict(self.metadata, lastDraftVersion="2026-09-26T09:10:00Z")
        self.after.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ReconcileError, "published/draft version"):
            verify_readback(self.repo, self.change_id, self.package, self.before, self.after)


if __name__ == "__main__":
    unittest.main()
