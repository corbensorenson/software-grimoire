#!/usr/bin/env python3
"""Validate adoption-report intake decision tooling."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_adoption_intake.py"
TEMPLATE = ROOT / "examples" / "adoption" / "adoption-intake-decision-template.json"
SCRATCH = ROOT / "tmp" / "tests" / "adoption-intake"


def remove_scratch(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def report_record() -> dict:
    return {
        "id": "adoption.external-fixture-review.v1",
        "title": "External Fixture Review",
        "provenance": "external-user",
        "task": "Apply the safe-refactoring spell to a real maintenance patch.",
        "spell_or_stack_used": "spell.safe-refactoring.v1",
        "surface": "External maintainer workflow",
        "artifact_produced": "Patch and review notes.",
        "verification_performed": "Unit tests and reviewer readback.",
        "time_cost": "Low; the template added a few minutes of setup.",
        "failure_or_friction": "The verification clause needed local translation.",
        "reuse_decision": "reuse",
    }


def decision_record(report_path: Path, report: dict) -> dict:
    return {
        "schema_version": "4.0.0-adoption-intake-decision",
        "decision_id": "adoption-intake.external-fixture-review.v1",
        "generated_at": "2026-07-02T00:00:00Z",
        "status": "maintainer-reviewed",
        "policy": "Only accepted and published non-maintainer reports count as external adoption.",
        "report_path": str(report_path.relative_to(ROOT)),
        "report_id": report["id"],
        "provenance": report["provenance"],
        "maintainer": "Maintainer Example",
        "review_date": "2026-07-02",
        "decision": "accept",
        "evidence_checked": [
            {
                "kind": "report",
                "path_or_url": str(report_path.relative_to(ROOT)),
                "notes": "Schema-valid external-user report.",
            }
        ],
        "publication": {
            "status": "published",
            "url_or_path": "https://github.com/corbensorenson/software-grimoire/issues/1",
        },
        "acceptance_notes": "Example accepted report used only in tests.",
        "counts_as_external_adoption": True,
        "blocks_external_adoption_credit": False,
    }


def test_pending_intake_template_matches_schema_and_stays_pending() -> None:
    record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "adoption-intake-decision.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(record)

    checked = run_script("validate", str(TEMPLATE.relative_to(ROOT)))
    assert checked.returncode == 0, checked.stderr
    assert "Maintainer decision remains pending" in checked.stdout
    assert record["counts_as_external_adoption"] is False
    assert record["blocks_external_adoption_credit"] is True


def test_accepted_external_report_can_be_validated_and_normalized() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    report_path = SCRATCH / "external-report.json"
    decision_path = SCRATCH / "accepted-decision.json"
    normalized_path = SCRATCH / "normalized-decision.json"
    report = report_record()
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    decision = decision_record(report_path, report)
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    try:
        checked = run_script(
            "validate",
            str(decision_path.relative_to(ROOT)),
            "--write-normalized",
            str(normalized_path.relative_to(ROOT)),
        )
        assert checked.returncode == 0, checked.stderr
        assert "Counts as external adoption: True" in checked.stdout
        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        assert normalized["counts_as_external_adoption"] is True
        assert normalized["report"]["provenance"] == "external-user"
    finally:
        remove_scratch(SCRATCH)


def test_intake_validator_rejects_outside_normalized_output() -> None:
    outside = ROOT.parent / "outside-adoption-intake.json"
    checked = run_script("validate", str(TEMPLATE.relative_to(ROOT)), "--write-normalized", str(outside))
    assert checked.returncode != 0
    assert "inside this repository" in checked.stderr


def test_intake_validator_rejects_unpublished_external_count() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    report_path = SCRATCH / "external-report.json"
    decision_path = SCRATCH / "bad-decision.json"
    report = report_record()
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    decision = decision_record(report_path, report)
    decision["publication"] = {"status": "not-published", "url_or_path": ""}
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    try:
        checked = run_script("validate", str(decision_path.relative_to(ROOT)))
        assert checked.returncode != 0
        assert "counts_as_external_adoption must be true only" in checked.stderr
    finally:
        remove_scratch(SCRATCH)
