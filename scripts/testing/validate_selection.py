#!/usr/bin/env python3
"""Check test selection against a PR diff; emit the Playwright files to run."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

APP_ID = "204a48dc-7f23-43dd-b934-4654a3cfa306"
ENV_ID = "68e00049-b7e5-eda6-9888-9a3cc493c5be"
RECORD_PREFIX = "docs/testing/change-records/"
REQUEST_PREFIX = "docs/changes/requests/"
TEST_PREFIX = "e2e/current-app/"
SOURCE_PREFIXES = ("powerapps/canvas-v3/Src/", "powerapps/test-data/", "src/screen-ui/v1.24/", "config/dataverse/")
SOURCE_FILES = {"powerapps/canvas-v3/baseline.msapr"}


class SelectionError(ValueError):
    pass


def changed_paths(repo: Path, base: str, head: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTD", f"{base}...{head}"],
        cwd=repo, check=True, capture_output=True, text=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def source_path(path: str) -> bool:
    return (path.startswith(SOURCE_PREFIXES) and not path.endswith('/README.md')) or path in SOURCE_FILES


def check_case(repo: Path, case: dict) -> None:
    case_id = case.get("id")
    level = case.get("level")
    file = case.get("test_file")
    if not isinstance(case_id, str) or not re.fullmatch(r"(?:UT|IT)-[A-Z0-9-]+", case_id):
        raise SelectionError(f"invalid case ID: {case_id!r}")
    if level not in ("unit", "integration"):
        raise SelectionError(f"{case_id}: level must be unit or integration")
    if not isinstance(file, str) or not file.startswith(TEST_PREFIX) or not re.fullmatch(r"e2e/current-app/[a-z0-9-]+\.test\.ts", file):
        raise SelectionError(f"{case_id}: test_file must be under {TEST_PREFIX}")
    test_file = repo / file
    if not test_file.is_file():
        raise SelectionError(f"{case_id}: missing {file}")
    # A reference to a case in a comment is not sufficient: it must be a test title.
    if not re.search(r"\btest\s*\(\s*['\"`]" + re.escape(case_id) + r"\b", test_file.read_text(encoding="utf-8")):
        raise SelectionError(f"{case_id}: missing test title in {file}")


def validate(repo: Path, changed: set[str], *, smoke_if_tests_changed: bool = False) -> dict:
    source = {path for path in changed if source_path(path)}
    records = sorted(
        path for path in changed
        if path.startswith(RECORD_PREFIX) and path.endswith(".json")
    )
    if source and not records:
        raise SelectionError("app source changed without a changed selection record")
    if records and not source:
        raise SelectionError("selection record changed without an app source change")
    if len(records) > 1:
        raise SelectionError("use one selection record per PR, covering all changed components")

    covered: set[str] = set()
    tests: set[str] = set()
    all_ids: set[str] = set()
    for record in records:
        path = repo / record
        if not path.is_file():
            raise SelectionError(f"missing or deleted record: {record}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1 or not data.get("change_id"):
            raise SelectionError(f"{record}: schema_version=1 and change_id required")
        if data.get("target") != {"environment_id": ENV_ID, "app_id": APP_ID}:
            raise SelectionError(f"{record}: wrong environment or App ID")
        request_path = REQUEST_PREFIX + Path(record).name
        if request_path not in changed:
            raise SelectionError(f"{record}: change request must be updated with the selection record: {request_path}")
        request_file = repo / request_path
        if not request_file.is_file():
            raise SelectionError(f"{record}: missing change request: {request_path}")
        request = json.loads(request_file.read_text(encoding="utf-8"))
        if request.get("schema_version") != 1 or request.get("change_id") != data["change_id"]:
            raise SelectionError(f"{request_path}: change ID or schema mismatch")
        if request.get("target") != data["target"]:
            raise SelectionError(f"{request_path}: wrong environment or App ID")
        if not isinstance(request.get("request_text"), str) or len(request["request_text"].strip()) < 10:
            raise SelectionError(f"{request_path}: record the original request and its scope")
        for key in ("requirement_ids", "acceptance_criteria"):
            values = request.get(key)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
                raise SelectionError(f"{request_path}: {key} must be a nonempty list")
        changes = data.get("changes")
        cases = data.get("cases")
        integration = data.get("integration")
        system = data.get("system_test")
        if not isinstance(changes, list) or not changes or not isinstance(cases, list) or not cases:
            raise SelectionError(f"{record}: changes and cases must be nonempty lists")
        if not isinstance(integration, dict) or type(integration.get("required")) is not bool:
            raise SelectionError(f"{record}: integration.required must be boolean")
        if not isinstance(integration.get("reason"), str) or len(integration["reason"].strip()) < 10:
            raise SelectionError(f"{record}: integration.reason must explain impact")
        if not isinstance(system, dict) or system.get("status") != "deferred" or not system.get("reason"):
            raise SelectionError(f"{record}: document deferred system test and reason")

        by_id: dict[str, dict] = {}
        for case in cases:
            if not isinstance(case, dict):
                raise SelectionError(f"{record}: case must be an object")
            check_case(repo, case)
            if case["id"] in by_id or case["id"] in all_ids:
                raise SelectionError(f"{record}: duplicate case {case['id']}")
            by_id[case["id"]] = case
            all_ids.add(case["id"])
            tests.add(case["test_file"])

        used: set[str] = set()
        for change in changes:
            if not isinstance(change, dict):
                raise SelectionError(f"{record}: change must be an object")
            file = change.get("path")
            if file not in source:
                raise SelectionError(f"{record}: {file!r} is not a changed app source path")
            covered.add(file)
            if not change.get("component") or not change.get("expected_result"):
                raise SelectionError(f"{record}: {file}: component and expected_result required")
            ids = change.get("unit_case_ids")
            if not isinstance(ids, list) or not ids:
                raise SelectionError(f"{record}: {file}: every changed component needs a unit case")
            for case_id in ids:
                if case_id not in by_id or by_id[case_id]["level"] != "unit":
                    raise SelectionError(f"{record}: {file}: invalid unit case {case_id}")
                used.add(case_id)

        integration_ids = integration.get("case_ids")
        if not isinstance(integration_ids, list):
            raise SelectionError(f"{record}: integration.case_ids must be a list")
        if integration["required"] != bool(integration_ids):
            raise SelectionError(f"{record}: integration cases must match required flag")
        for case_id in integration_ids:
            if case_id not in by_id or by_id[case_id]["level"] != "integration":
                raise SelectionError(f"{record}: invalid integration case {case_id}")
            used.add(case_id)
        if used != set(by_id):
            raise SelectionError(f"{record}: unselected case IDs: {sorted(set(by_id) - used)}")

    if covered != source:
        raise SelectionError(f"app source without test selection: {sorted(source - covered)}")
    if smoke_if_tests_changed:
        for file in sorted(p for p in changed if p.startswith(TEST_PREFIX) and p.endswith('.test.ts')):
            test_file = repo / file
            if not test_file.is_file():
                raise SelectionError(f"changed test file is missing: {file}")
            ids = re.findall(r"\btest\s*\(\s*['\"`]((?:UT|IT)-[A-Z0-9-]+)\b", test_file.read_text(encoding="utf-8"))
            if not ids:
                raise SelectionError(f"changed test file has no executable unit/integration case: {file}")
            tests.add(file)
            all_ids.update(ids)
    return {"source_paths": sorted(source), "record_paths": records,
            "request_paths": [REQUEST_PREFIX + Path(p).name for p in records],
            "test_files": sorted(tests), "case_ids": sorted(all_ids)}


def select_record(repo: Path, record: str) -> dict:
    """Select exactly the recorded cases for a post-publication run."""
    if not re.fullmatch(r"docs/testing/change-records/[a-z0-9][a-z0-9-]*\.json", record):
        raise SelectionError("invalid selection record path")
    file = repo / record
    if not file.is_file():
        raise SelectionError(f"missing selection record: {record}")
    data = json.loads(file.read_text(encoding="utf-8"))
    changes = data.get("changes")
    if not isinstance(changes, list) or not changes:
        raise SelectionError(f"{record}: changes required")
    source = {entry.get("path") for entry in changes if isinstance(entry, dict)}
    if not source or any(not isinstance(p, str) or not source_path(p) or not (repo / p).is_file() for p in source):
        raise SelectionError(f"{record}: source paths must be current app files")
    request = REQUEST_PREFIX + Path(record).name
    return validate(repo, source | {record, request})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", help="merge base for PR/push selection")
    parser.add_argument("--record", help="post-publication: run only the named selection record")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.record and not args.base:
        parser.error("--base is required unless --record is supplied")
    try:
        repo = args.repo.resolve()
        plan = (select_record(repo, args.record) if args.record else
                validate(repo, changed_paths(repo, args.base, args.head), smoke_if_tests_changed=True))
    except (SelectionError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    encoded = json.dumps(plan, ensure_ascii=False)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
