#!/usr/bin/env python3
"""Fail closed when a current-app documentation update lacks release evidence."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.testing.validate_selection import APP_ID, ENV_ID, SelectionError, select_record, source_path

TARGET = {"environment_id": ENV_ID, "app_id": APP_ID}
DOCS = (
    "docs/requirements/requirements.md",
    "docs/design/basic-design.md",
    "docs/design/detailed-design.md",
)
SPEC = "docs/testing/test-specification.md"


class ReconcileError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReconcileError(message)


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path}: expected JSON object")
    return data


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, text=True,
                          capture_output=True).stdout.strip()


def stamp(value: str) -> datetime:
    require(isinstance(value, str) and bool(value.strip()), "publication timestamp missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ReconcileError("invalid publication timestamp") from error
    require(parsed.tzinfo is not None, "publication timestamp needs a timezone")
    return parsed


def preflight(repo: Path, change_id: str) -> dict:
    require(bool(re.fullmatch(r"[A-Z0-9][A-Z0-9-]{2,60}", change_id)), "invalid change ID")
    basename = change_id.lower()
    request_path = f"docs/changes/requests/{basename}.json"
    selection_path = f"docs/testing/change-records/{basename}.json"
    record_path = f"docs/verification/postpublish/{basename}.json"
    request, selection, record = (load(repo / p) for p in (request_path, selection_path, record_path))
    plan = select_record(repo, selection_path)
    for name, data in (("request", request), ("selection", selection), ("release record", record)):
        require(data.get("schema_version") == 1 and data.get("change_id") == change_id,
                f"{name}: change ID/schema mismatch")
        require(data.get("target") == TARGET, f"{name}: wrong current App ID/environment")
    source_commit = record.get("source_commit")
    require(isinstance(source_commit, str) and bool(re.fullmatch(r"[0-9a-f]{40}", source_commit)),
            "source_commit must be the published source commit SHA")
    base = record.get("documentation_base_commit")
    require(isinstance(base, str) and bool(re.fullmatch(r"[0-9a-f]{40}", base)),
            "documentation_base_commit must be a SHA")
    require(git(repo, "rev-parse", "--verify", "HEAD^{commit}") != base,
            "documentation must be committed after the source commit")
    for earlier, later in ((source_commit, base), (base, "HEAD")):
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", earlier, later], cwd=repo)
        require(ancestor.returncode == 0, "source and documentation base must precede this document commit")
    changed_since_source = set(git(repo, "diff", "--name-only", f"{source_commit}..HEAD").splitlines())
    require(not any(source_path(p) for p in changed_since_source),
            "app source changed since publication; read back and test the new candidate")
    require(not (({request_path, selection_path} | set(plan["test_files"])) & changed_since_source),
            "request, selection or test code changed since publication; select and test again")
    changed = set(git(repo, "diff", "--name-only", f"{base}..HEAD").splitlines())
    require(record_path in changed, "post-publication release record must be committed after source")
    require(set(DOCS).issubset(changed), "requirements, basic and detailed design must all be updated after publication")
    require(record.get("requirement_ids") == request.get("requirement_ids"),
            "release requirement IDs differ from the recorded request")
    require(record.get("selected_case_ids") == plan["case_ids"],
            "release case IDs differ from selected executable cases")
    comparison = record.get("source_comparison")
    require(isinstance(comparison, dict) and comparison.get("result") == "MATCH",
            "published package/source comparison must be recorded")
    require(comparison.get("checked_paths") == plan["source_paths"],
            "published comparison must cover every selected source path")
    require(isinstance(comparison.get("method_and_findings"), str)
            and len(comparison["method_and_findings"].strip()) >= 20,
            "describe how published behavior/source was compared with the Git candidate")
    published = record.get("publication")
    require(isinstance(published, dict), "publication evidence required")
    version = published.get("version")
    published_at = stamp(version)
    integration = selection["integration"]
    if integration["required"]:
        require(SPEC in changed, "integration case specification must be updated after publication")
        content = (repo / SPEC).read_text(encoding="utf-8")
        require(all(case_id in content for case_id in integration["case_ids"])
                and change_id in content and version in content,
                "integration case IDs, change ID and published version must appear in the updated specification")
    else:
        reason = record.get("integration_spec_not_changed_reason")
        require(isinstance(reason, str) and len(reason.strip()) >= 10,
                "record why the integration case specification was not changed")
    for path in DOCS:
        content = (repo / path).read_text(encoding="utf-8")
        require(change_id in content and version in content,
                f"{path}: missing change ID or published version in the updated document")
    observed = stamp(published.get("player_observed_at"))
    require(observed >= published_at, "Player observation precedes publication")
    require(published.get("player_app_id") == APP_ID and published.get("player_result") == "PASS",
            "current App ID and a successful Player observation required")
    require(isinstance(published.get("player_observation"), str)
            and len(published["player_observation"].strip()) >= 20,
            "record the actual Player behavior and remaining gaps")
    digest = published.get("download_sha256")
    require(isinstance(digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", digest)),
            "readback package SHA-256 required")
    return {"source_commit": source_commit, "documentation_base_commit": base,
            "record_path": record_path,
            "selection_path": selection_path, "case_ids": plan["case_ids"], "version": version,
            "download_sha256": digest, "change_id": change_id}


def verify_readback(repo: Path, change_id: str, package: Path, before: Path, after: Path) -> dict:
    state = preflight(repo, change_id)
    expected_uri = f"https://apps.powerapps.com/play/e/{ENV_ID}/a/{APP_ID}?"
    for path in (before, after):
        metadata = load(path)
        require(metadata.get("status") == "Ready", "app is not Ready")
        require(metadata.get("lastPublishTime") == state["version"]
                and metadata.get("lastDraftVersion") == state["version"],
                "published/draft version differs from recorded Player release")
        require(str(metadata.get("appOpenUri", "")).startswith(expected_uri),
                "Power Apps metadata points to another app/environment")
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    require(actual == state["download_sha256"], "PAC readback differs from recorded package")
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--change-id", required=True)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--metadata-before", type=Path)
    parser.add_argument("--metadata-after", type=Path)
    args = parser.parse_args()
    if any((args.package, args.metadata_before, args.metadata_after)) and not all(
        (args.package, args.metadata_before, args.metadata_after)
    ):
        parser.error("--package and both metadata snapshots must be supplied together")
    try:
        state = (verify_readback(args.repo, args.change_id, args.package,
                                 args.metadata_before, args.metadata_after)
                 if all((args.package, args.metadata_before, args.metadata_after)) else
                 preflight(args.repo, args.change_id))
    except (ReconcileError, SelectionError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    print(json.dumps(state, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
