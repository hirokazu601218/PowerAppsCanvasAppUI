import json
from pathlib import Path
import tempfile
import unittest

from scripts.governance.validate_document_placement import route, validate_record


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.policy = {
            "current_documents": ["docs/requirements/requirements.md"],
            "current_dynamic_patterns": [r"^docs/changes/requests/[a-z0-9-]+\.json$"],
            "legacy_migration_map": "records/operations/migration/source-map.csv",
            "record_index_paths": ["records/README.md"],
        }
        self.migration = {"docs/testing/old.md": "records/docs/testing/old.md"}

    def test_three_categories(self):
        self.assertEqual(route("docs/requirements/requirements.md", self.policy, self.migration), "current")
        self.assertEqual(route("records/docs/testing/old.md", self.policy, self.migration), "record")
        self.assertEqual(route("records/README.md", self.policy, self.migration), "record")
        self.assertEqual(route("AGENTS.md", self.policy, self.migration), "code")
        self.assertEqual(route("other/README.md", self.policy, self.migration), "other")
        self.assertEqual(route("other/docs/reference/old.md", self.policy,
                               {"x": "other/docs/reference/old.md"}), "other")

    def test_unknown_current_or_archive_is_rejected(self):
        for path in ("docs/testing/random.md", "records/docs/new.md", "misc/plan.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                route(path, self.policy, self.migration)

    def test_run_record_needs_matching_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            folder = repo / "records/changes/change-123/457"
            folder.mkdir(parents=True)
            (folder / "record.json").write_text(json.dumps({
                "change_id": "change-123", "run_id": "457",
                "app_id": "204a48dc-7f23-43dd-b934-4654a3cfa306",
                "status": "PARTIAL", "observed_at": "2026-09-26T14:00:00Z",
                "source_commit": "abc", "version": "v1.26"
            }), encoding="utf-8")
            validate_record(repo, "records/changes/change-123/457/results.md",
                            "204a48dc-7f23-43dd-b934-4654a3cfa306")
            (folder / "record.json").unlink()
            with self.assertRaises(ValueError):
                validate_record(repo, "records/changes/change-123/457/results.md",
                                "204a48dc-7f23-43dd-b934-4654a3cfa306")


if __name__ == "__main__":
    unittest.main()
