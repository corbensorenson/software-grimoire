#!/usr/bin/env python3
"""Validate a reviewer-supplied Bench v4 hardness model-run import."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

try:  # pragma: no cover - exercised by direct script invocation
    from run_hardness_bench import CASES, artifact_files
    from run_hardness_model_surfaces import GRADER_VERSION, run_extracted_artifacts
except ImportError:  # pragma: no cover - exercised by package imports in tests
    from scripts.run_hardness_bench import CASES, artifact_files
    from scripts.run_hardness_model_surfaces import GRADER_VERSION, run_extracted_artifacts


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "hardness-v4-import.schema.json"
PROVENANCE_EVIDENCE_CLASS = {
    "project-owned": "project_owned_model_run",
    "reviewer-supplied": "reviewer_supplied_model_run",
    "external-user": "external_user_model_run",
}
PROMPT_HIDDEN_MARKERS = ("ground_truth.json", "check_")


def display(path: Path) -> str:
    return str(path.relative_to(ROOT))


def repo_path(value: str, *, must_exist: bool = True, directory: bool | None = None) -> tuple[Path | None, str | None]:
    raw = Path(value).expanduser()
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return None, f"path must stay inside this repository: {value}"
    if must_exist and not resolved.exists():
        return resolved, f"path does not exist: {value}"
    if directory is True and resolved.exists() and not resolved.is_dir():
        return resolved, f"path must be a directory: {value}"
    if directory is False and resolved.exists() and not resolved.is_file():
        return resolved, f"path must be a file: {value}"
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


def text_contains_hidden_prompt_material(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    found = []
    for marker in PROMPT_HIDDEN_MARKERS:
        if marker in text:
            found.append(marker)
    return found


def artifact_file_list(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


def logical_errors(record: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    resolved: dict[str, Path] = {}
    case_slug = record.get("case_slug")
    case = CASES.get(case_slug)
    if case is None:
        errors.append(f"unknown Bench v4 case_slug: {case_slug!r}")
        return errors, resolved

    expected_fixture = case["fixture"]
    if record.get("fixture_path") != expected_fixture:
        errors.append(f"fixture_path must be {expected_fixture!r} for {case_slug}")

    expected_artifacts = artifact_files(case)
    if record.get("artifact_files") != expected_artifacts:
        errors.append(f"artifact_files must be {expected_artifacts!r} for {case_slug}")

    expected_command = f"python -m pytest -q {case['test_file']}"
    if record.get("execution_command") != expected_command:
        errors.append(f"execution_command must be {expected_command!r}")

    expected_evidence = PROVENANCE_EVIDENCE_CLASS.get(record.get("provenance"))
    if record.get("evidence_class") != expected_evidence:
        errors.append(
            f"evidence_class {record.get('evidence_class')!r} does not match provenance {record.get('provenance')!r}"
        )

    for key, is_dir in [
        ("fixture_path", True),
        ("prompt_path", False),
        ("transcript_path", False),
        ("artifact_root", True),
    ]:
        path, error = repo_path(str(record.get(key, "")), directory=is_dir)
        if error:
            errors.append(f"{key}: {error}")
        elif path is not None:
            resolved[key] = path

    prompt = resolved.get("prompt_path")
    if prompt is not None:
        markers = text_contains_hidden_prompt_material(prompt)
        if markers:
            errors.append(f"prompt_path appears to include hidden grader material: {', '.join(markers)}")

    artifact_root = resolved.get("artifact_root")
    if artifact_root is not None:
        found = artifact_file_list(artifact_root)
        if found != expected_artifacts:
            errors.append(f"artifact_root must contain exactly {expected_artifacts!r}; found {found!r}")

    if record.get("maintainer_decision") != "pending":
        errors.append("manual imports must enter as maintainer_decision='pending'; acceptance is a separate review step")

    return errors, resolved


def normalized_record(record: dict, execution_result: dict) -> dict:
    case = CASES[record["case_slug"]]
    return {
        "schema_version": "4.0.0-hardness-manual-import-normalized",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": (
            "Normalized manual imports are validation artifacts only. They do not update official evidence "
            "or count as accepted reviewer-supplied runs until a maintainer reviews and publishes them."
        ),
        "import_record": record,
        "execution_result": execution_result,
        "extraction_result": {
            "complete": True,
            "expected_files": artifact_files(case),
            "extracted_files": artifact_files(case),
            "errors": [],
        },
        "grader_version": GRADER_VERSION,
    }


def validate_import(path: Path, write_normalized: str | None = None) -> int:
    record = json.loads(path.read_text(encoding="utf-8"))
    errors = schema_errors(record)
    logical, resolved = logical_errors(record)
    errors.extend(logical)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    execution = run_extracted_artifacts(record["case_slug"], resolved["artifact_root"])
    print(f"Hardness import record is valid: {display(path.resolve())}")
    print(f"Execution result: {execution['status']} (exit_code={execution['exit_code']})")
    print("Maintainer decision remains pending; this command validates intake only.")
    if write_normalized:
        out = output_path(write_normalized)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(normalized_record(record, execution), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {display(out)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate and execute-check one manual hardness import record")
    validate.add_argument("path", help="manual hardness import JSON path")
    validate.add_argument("--write-normalized", help="optional repo-local output path for a normalized validation artifact")
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate_import(Path(args.path), args.write_normalized)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
