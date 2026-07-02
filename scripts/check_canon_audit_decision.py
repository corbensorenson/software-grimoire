#!/usr/bin/env python3
"""Validate a human canon-audit decision record without claiming signoff."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema


SOURCE_ROOT = Path(__file__).resolve().parents[1]


def find_root() -> Path:
    if (SOURCE_ROOT / "schemas" / "canon-audit-decision.schema.json").exists():
        return SOURCE_ROOT
    cwd = Path.cwd().resolve()
    if (cwd / "schemas" / "canon-audit-decision.schema.json").exists():
        return cwd
    return SOURCE_ROOT


ROOT = find_root()
SCHEMA_PATH = ROOT / "schemas" / "canon-audit-decision.schema.json"
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
PENDING_REVIEWERS = {"", "pending", "pending-human-maintainer", "project-template"}


def display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def repo_path(value: str, *, must_exist: bool = True) -> tuple[Path | None, str | None]:
    raw = Path(value).expanduser()
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return None, f"path must stay inside this repository: {value}"
    if must_exist and not resolved.exists():
        return resolved, f"path does not exist: {value}"
    return resolved, None


def output_path(value: str) -> Path:
    path, error = repo_path(value, must_exist=False)
    if error:
        raise ValueError(error)
    assert path is not None
    return path


def schema_errors(record: dict) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def audit_queue_by_id() -> dict[str, dict]:
    path = ROOT / "data" / "canon_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"]: item for item in data.get("audit_queue", [])}


def logical_errors(record: dict) -> list[str]:
    errors: list[str] = []
    queue = audit_queue_by_id()
    audit_id = record.get("audit_id", "")
    item = queue.get(audit_id)
    if item is None:
        errors.append(f"audit_id is not present in data/canon_audit.json: {audit_id!r}")
    elif record.get("scope") != item.get("scope"):
        errors.append(f"scope must match audit queue scope {item.get('scope')!r}")

    for evidence in record.get("evidence_checked", []):
        path, error = repo_path(str(evidence.get("path", "")), must_exist=evidence.get("kind") not in {"issue", "pull_request"})
        if error:
            errors.append(f"evidence_checked path: {error}")
        elif path is not None and evidence.get("kind") not in {"issue", "pull_request"} and not path.is_file():
            errors.append(f"evidence_checked path must be a file: {evidence.get('path')}")

    status = record.get("status")
    decision = record.get("decision")
    reviewer = str(record.get("reviewer", "")).strip()
    review_date = str(record.get("review_date", "")).strip()
    accepted = record.get("accepted_as_canonical")
    blocks = record.get("blocks_canonical_promotion")

    if status == "pending-human-maintainer":
        if decision != "pending":
            errors.append("pending-human-maintainer records must use decision='pending'")
        if accepted is not False:
            errors.append("pending-human-maintainer records cannot set accepted_as_canonical=true")
        if blocks is not True:
            errors.append("pending-human-maintainer records must keep blocks_canonical_promotion=true")
    elif status == "human-signed":
        if reviewer.lower() in PENDING_REVIEWERS:
            errors.append("human-signed records require a named reviewer")
        if not DATE_RE.match(review_date):
            errors.append("human-signed records require review_date in YYYY-MM-DD form")
        if decision == "pending":
            errors.append("human-signed records require accept, revise, defer, or reject")
        if decision == "accept":
            if accepted is not True:
                errors.append("accepted human decisions must set accepted_as_canonical=true")
            if blocks is not False:
                errors.append("accepted human decisions must set blocks_canonical_promotion=false")
        else:
            if accepted is not False:
                errors.append("non-accept decisions cannot set accepted_as_canonical=true")
            if blocks is not True:
                errors.append("non-accept decisions must keep blocks_canonical_promotion=true")

    return errors


def normalized_record(path: Path, record: dict) -> dict:
    return {
        "schema_version": "4.0.0-canon-audit-decision-normalized",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": (
            "This normalized artifact validates a canon-audit decision record. "
            "It does not change canonical status unless a named maintainer commits "
            "the signed record and corresponding generated data update."
        ),
        "source_path": display(path.resolve()),
        "decision_record": record,
        "is_human_signed": record.get("status") == "human-signed",
        "accepted_as_canonical": bool(record.get("accepted_as_canonical")),
        "blocks_canonical_promotion": bool(record.get("blocks_canonical_promotion")),
    }


def validate_decision(path: Path, write_normalized: str | None = None) -> int:
    resolved, error = repo_path(str(path), must_exist=True)
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    assert resolved is not None
    record = json.loads(resolved.read_text(encoding="utf-8"))
    errors = schema_errors(record)
    errors.extend(logical_errors(record))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Canon audit decision record is valid: {display(resolved)}")
    if record["status"] == "human-signed":
        print(f"Human decision: {record['decision']} by {record['reviewer']} on {record['review_date']}")
    else:
        print("Maintainer decision remains pending; this template is not human signoff.")
    if write_normalized:
        try:
            out = output_path(write_normalized)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(normalized_record(resolved, record), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {display(out)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate one canon-audit decision JSON record")
    validate.add_argument("path", help="canon-audit decision JSON path")
    validate.add_argument("--write-normalized", help="optional repo-local output path for normalized validation artifact")
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate_decision(Path(args.path), args.write_normalized)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
