#!/usr/bin/env python3
"""Check new documents against the three-way routing policy on every PR."""
import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import sys

POLICY = "config/document-routing.json"
DOCUMENT_SUFFIXES = {".md", ".pdf", ".docx", ".pptx", ".xlsx"}


def route(path: str, policy: dict, migration: dict[str, str]) -> str:
    if path in policy["current_documents"] or any(
        re.fullmatch(pattern, path) for pattern in policy["current_dynamic_patterns"]
    ):
        return "current"
    if path.startswith("docs/"):
        raise ValueError(f"{path}: unknown current document; update {POLICY} in the same PR")
    if path == policy["legacy_migration_map"] or path in policy["record_index_paths"]:
        return "record"
    if path.startswith("records/changes/"):
        if not re.fullmatch(r"records/changes/[a-z0-9][a-z0-9-]*/(?:[0-9]+|manual-[0-9]{8}-[a-z0-9-]+)/[^/]+", path):
            raise ValueError(f"{path}: expected records/changes/<change-id>/<run-id>/<file>")
        return "record"
    if path.startswith("records/"):
        if path not in migration.values():
            raise ValueError(f"{path}: archival file requires a reviewed old-to-new entry")
        return "record"
    if path == "other/README.md":
        return "other"
    if path.startswith("other/"):
        if path in migration.values():
            return "other"
        if not re.fullmatch(r"other/[a-z0-9][a-z0-9-]*/.+", path):
            raise ValueError(f"{path}: new other material needs a named project directory")
        return "other"
    if Path(path).suffix.lower() in DOCUMENT_SUFFIXES and Path(path).name != "README.md" and path != "AGENTS.md":
        raise ValueError(f"{path}: standalone document belongs in docs/, records/, or other/")
    return "code"


def validate_record(repo: Path, path: str, app_id: str) -> None:
    parts = Path(path).parts
    folder = repo.joinpath(*parts[:4])
    metadata = folder / "record.json"
    if not metadata.is_file():
        raise ValueError(f"{path}: {metadata.relative_to(repo)} is required")
    data = json.loads(metadata.read_text(encoding="utf-8"))
    if data.get("change_id") != parts[2] or data.get("run_id") != parts[3]:
        raise ValueError(f"{metadata.relative_to(repo)}: ID mismatch")
    if data.get("app_id") != app_id or data.get("status") not in {
        "PASS", "FAIL", "BLOCKED", "NOT_RUN", "PARTIAL"
    }:
        raise ValueError(f"{metadata.relative_to(repo)}: App ID or status invalid")
    for field in ("observed_at", "source_commit", "version"):
        if not isinstance(data.get(field), str) or not data[field]:
            raise ValueError(f"{metadata.relative_to(repo)}: missing {field}")


def changed_paths(repo: Path, base: str, head: str) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "diff", "--name-status", "--find-renames=25%", f"{base}...{head}"],
        cwd=repo, text=True, capture_output=True, check=True,
    )
    changes = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if fields[0].startswith("R"):
            changes.append((fields[1], fields[2]))
        elif fields[0] != "D":
            changes.append(("", fields[1]))
    return changes


def validate(repo: Path, changes: list[tuple[str, str]]) -> dict:
    policy = json.loads((repo / POLICY).read_text(encoding="utf-8"))
    with (repo / policy["legacy_migration_map"]).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    migration = {row["source_path"]: row["proposed_path"] for row in rows}
    if len(migration) != len(rows) or len(set(migration.values())) != len(rows):
        raise ValueError("migration map has duplicate paths")
    counts = {"current": 0, "record": 0, "other": 0, "code": 0}
    for old, new in changes:
        category = route(new, policy, migration)
        if old and old in migration and migration[old] != new:
            raise ValueError(f"{old}: archived at {new}, but map says {migration[old]}")
        if category == "record" and new.startswith("records/changes/"):
            validate_record(repo, new, policy["current_app_id"])
        if category == "other" and new not in migration.values() and new != "other/README.md":
            project = new.split("/")[1]
            if not (repo / "other" / project / "README.md").is_file():
                raise ValueError(f"{new}: other/{project}/README.md is required")
        counts[category] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()
    try:
        result = validate(args.repo.resolve(), changed_paths(args.repo, args.base, args.head))
    except (ValueError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
