#!/usr/bin/env python3
"""Validate a Bench v4 hardness-import intake decision."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

try:  # pragma: no cover - direct script invocation
    from import_hardness_model_run import logical_errors as import_logical_errors
    from import_hardness_model_run import schema_errors as import_schema_errors
except ImportError:  # pragma: no cover - package imports
    from scripts.import_hardness_model_run import logical_errors as import_logical_errors
    from scripts.import_hardness_model_run import schema_errors as import_schema_errors


SOURCE_ROOT = Path(__file__).resolve().parents[1]
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
PENDING_MAINTAINERS = {"", "pending", "pending-maintainer", "project-template"}
EXTERNAL_PROVENANCE = {"reviewer-supplied", "external-user"}
PROJECT_PRIMARY_SURFACES = {"codex-cli-default"}


def find_root() -> Path:
    if (SOURCE_ROOT / "schemas" / "hardness-intake-decision.schema.json").exists():
        return SOURCE_ROOT
    cwd = Path.cwd().resolve()
    if (cwd / "schemas" / "hardness-intake-decision.schema.json").exists():
        return cwd
    return SOURCE_ROOT


ROOT = find_root()
DECISION_SCHEMA_PATH = ROOT / "schemas" / "hardness-intake-decision.schema.json"


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
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"decision.{location}: {error.message}")
    return errors


def load_import(decision: dict) -> tuple[dict | None, list[str]]:
    import_path, error = repo_path(str(decision.get("import_path", "")), must_exist=True)
    if error:
        return None, [f"import_path: {error}"]
    assert import_path is not None
    if not import_path.is_file():
        return None, [f"import_path must be a file: {decision.get('import_path')}"]
    record = json.loads(import_path.read_text(encoding="utf-8"))
    errors = [f"import.{error}" for error in import_schema_errors(record)]
    logical, _resolved = import_logical_errors(record)
    errors.extend(f"import.{error}" for error in logical)
    return record, errors


def local_evidence_errors(decision: dict) -> list[str]:
    errors: list[str] = []
    for evidence in decision.get("evidence_checked", []):
        value = str(evidence.get("path_or_url", ""))
        if value.startswith(("http://", "https://")):
            continue
        path, error = repo_path(value, must_exist=evidence.get("kind") not in {"issue", "pull_request"})
        if error:
            errors.append(f"evidence_checked path_or_url: {error}")
        elif path is not None and evidence.get("kind") not in {"issue", "pull_request"} and not path.exists():
            errors.append(f"evidence_checked path_or_url does not exist: {value}")
    publication = decision.get("publication", {})
    url_or_path = str(publication.get("url_or_path", ""))
    if url_or_path and not url_or_path.startswith(("http://", "https://")):
        path, error = repo_path(url_or_path, must_exist=publication.get("status") == "published")
        if error:
            errors.append(f"publication url_or_path: {error}")
    return errors


def should_count(decision: dict) -> bool:
    publication = decision.get("publication", {})
    published = publication.get("status") == "published" and bool(str(publication.get("url_or_path", "")).strip())
    non_codex_or_external = (
        decision.get("surface_id") not in PROJECT_PRIMARY_SURFACES
        or decision.get("provenance") in EXTERNAL_PROVENANCE
    )
    return decision.get("decision") == "accept" and published and non_codex_or_external


def logical_errors(decision: dict, import_record: dict | None) -> list[str]:
    errors: list[str] = []
    if import_record is None:
        return errors

    for key in ["surface_id", "benchmark", "case_slug", "variant", "repetition", "provenance"]:
        if decision.get(key) != import_record.get(key):
            errors.append(f"{key} must match import record value {import_record.get(key)!r}")

    status = decision.get("status")
    review_decision = decision.get("decision")
    maintainer = str(decision.get("maintainer", "")).strip()
    review_date = str(decision.get("review_date", "")).strip()
    counts = should_count(decision)
    publication = decision.get("publication", {})

    if status == "pending-maintainer":
        if review_decision != "pending":
            errors.append("pending-maintainer records must use decision='pending'")
        if decision.get("counts_as_cross_surface_hardness") is not False:
            errors.append("pending-maintainer records cannot count as cross-surface hardness evidence")
        if decision.get("blocks_hardness_credit") is not True:
            errors.append("pending-maintainer records must keep blocks_hardness_credit=true")
    elif status == "maintainer-reviewed":
        if maintainer.lower() in PENDING_MAINTAINERS:
            errors.append("maintainer-reviewed records require a named maintainer")
        if not DATE_RE.match(review_date):
            errors.append("maintainer-reviewed records require review_date in YYYY-MM-DD form")
        if review_decision == "pending":
            errors.append("maintainer-reviewed records require accept, revise, defer, or reject")
        if decision.get("counts_as_cross_surface_hardness") is not counts:
            errors.append(
                "counts_as_cross_surface_hardness must be true only for accepted, published non-Codex/reviewer/external imports"
            )
        if decision.get("blocks_hardness_credit") is counts:
            errors.append("blocks_hardness_credit must be the inverse of counts_as_cross_surface_hardness")

    if publication.get("status") == "published" and not str(publication.get("url_or_path", "")).strip():
        errors.append("published hardness decisions require publication.url_or_path")

    return errors


def normalized_record(path: Path, decision: dict, import_record: dict | None) -> dict:
    return {
        "schema_version": "4.0.0-hardness-intake-decision-normalized",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": (
            "This normalized artifact validates hardness-import acceptance only. It does not update "
            "examples/evaluations/hardness-v4/model-surface-results.json or increment cross-surface claims "
            "until a maintainer publishes the accepted import."
        ),
        "source_path": display(path.resolve()),
        "decision_record": decision,
        "import_record": import_record,
        "is_maintainer_reviewed": decision.get("status") == "maintainer-reviewed",
        "counts_as_cross_surface_hardness": bool(decision.get("counts_as_cross_surface_hardness")),
        "blocks_hardness_credit": bool(decision.get("blocks_hardness_credit")),
    }


def validate_decision(path: Path, write_normalized: str | None = None) -> int:
    resolved, error = repo_path(str(path), must_exist=True)
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    assert resolved is not None
    decision = json.loads(resolved.read_text(encoding="utf-8"))
    errors = schema_errors(decision)
    import_record, import_errors = load_import(decision)
    errors.extend(import_errors)
    errors.extend(local_evidence_errors(decision))
    errors.extend(logical_errors(decision, import_record))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Hardness intake decision record is valid: {display(resolved)}")
    if decision["status"] == "maintainer-reviewed":
        print(f"Maintainer decision: {decision['decision']} by {decision['maintainer']} on {decision['review_date']}")
        print(f"Counts as cross-surface hardness: {decision['counts_as_cross_surface_hardness']}")
    else:
        print("Maintainer decision remains pending; this template is not accepted hardness evidence.")
    if write_normalized:
        try:
            out = output_path(write_normalized)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(normalized_record(resolved, decision, import_record), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {display(out)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate one hardness intake decision JSON record")
    validate.add_argument("path", help="hardness intake decision JSON path")
    validate.add_argument("--write-normalized", help="optional repo-local output path for normalized validation artifact")
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate_decision(Path(args.path), args.write_normalized)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
