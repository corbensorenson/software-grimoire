#!/usr/bin/env python3
"""Create a schema-valid standalone adoption evidence report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_VALUES = ["project-owned", "reviewer-supplied", "external-user"]
REQUIRED_FIELDS = [
    "id",
    "title",
    "provenance",
    "task",
    "spell_or_stack_used",
    "surface",
    "artifact_produced",
    "verification_performed",
    "time_cost",
    "failure_or_friction",
    "reuse_decision",
]


def output_path(value: str) -> Path:
    path = Path(value).expanduser()
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("Adoption report output must stay inside this repository; use tmp/... for drafts.") from exc
    return resolved


def validate_report(report: dict) -> list[str]:
    schema = json.loads((ROOT / "schemas" / "adoption-report.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(report), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def report_from_args(args: argparse.Namespace) -> dict:
    report = {
        "id": args.id,
        "title": args.title,
        "provenance": args.provenance,
        "task": args.task,
        "spell_or_stack_used": args.spell_or_stack_used,
        "surface": args.surface,
        "artifact_produced": args.artifact_produced,
        "verification_performed": args.verification_performed,
        "time_cost": args.time_cost,
        "failure_or_friction": args.failure_or_friction,
        "reuse_decision": args.reuse_decision,
    }
    if args.notes:
        report["notes"] = args.notes
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="stable id like adoption.team-task.v1")
    parser.add_argument("--title", required=True)
    parser.add_argument("--provenance", required=True, choices=PROVENANCE_VALUES)
    parser.add_argument("--task", required=True)
    parser.add_argument("--spell-or-stack-used", dest="spell_or_stack_used", required=True)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--artifact-produced", dest="artifact_produced", required=True)
    parser.add_argument("--verification-performed", dest="verification_performed", required=True)
    parser.add_argument("--time-cost", dest="time_cost", required=True)
    parser.add_argument("--failure-or-friction", dest="failure_or_friction", required=True)
    parser.add_argument("--reuse-decision", dest="reuse_decision", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--write-report", default="tmp/adoption-report.json")
    args = parser.parse_args(argv)

    report = report_from_args(args)
    errors = validate_report(report)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    try:
        out = output_path(args.write_report)
    except ValueError as exc:
        parser.error(str(exc))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    if report["provenance"] == "project-owned":
        print("Note: project-owned reports do not count as external adoption.")
    else:
        print("Note: generated report still requires maintainer review before publication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
