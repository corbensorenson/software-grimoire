#!/usr/bin/env python3
"""Validate canon-audit decision intake tooling."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_canon_audit_decision.py"
TEMPLATE = ROOT / "examples" / "canon" / "canon-audit-decision-template.json"
SCRATCH = ROOT / "tmp" / "tests" / "canon-audit-decision"


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


def test_pending_template_matches_schema_and_stays_pending() -> None:
    record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "canon-audit-decision.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(record)

    checked = run_script("validate", str(TEMPLATE.relative_to(ROOT)))
    assert checked.returncode == 0, checked.stderr
    assert "Maintainer decision remains pending" in checked.stdout
    assert record["status"] == "pending-human-maintainer"
    assert record["accepted_as_canonical"] is False
    assert record["blocks_canonical_promotion"] is True


def test_human_signed_decision_can_be_validated_and_normalized() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    decision_path = SCRATCH / "signed-decision.json"
    normalized_path = SCRATCH / "normalized-decision.json"
    record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    record.update(
        {
            "decision_id": "canon-audit.first-two-houses-human.v1",
            "generated_at": "2026-07-02T00:00:00Z",
            "status": "human-signed",
            "reviewer": "Maintainer Example",
            "review_date": "2026-07-02",
            "decision": "accept",
            "signoff_statement": "I reviewed the listed evidence and accept this tranche as canonical.",
            "maintainer_notes": "Example test record only; not committed as project evidence.",
            "accepted_as_canonical": True,
            "blocks_canonical_promotion": False,
        }
    )
    decision_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    try:
        checked = run_script(
            "validate",
            str(decision_path.relative_to(ROOT)),
            "--write-normalized",
            str(normalized_path.relative_to(ROOT)),
        )
        assert checked.returncode == 0, checked.stderr
        assert "Human decision: accept by Maintainer Example on 2026-07-02" in checked.stdout
        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        assert normalized["is_human_signed"] is True
        assert normalized["accepted_as_canonical"] is True
    finally:
        remove_scratch(SCRATCH)


def test_decision_validator_rejects_outside_output_path() -> None:
    outside = ROOT.parent / "outside-canon-decision.json"
    checked = run_script("validate", str(TEMPLATE.relative_to(ROOT)), "--write-normalized", str(outside))
    assert checked.returncode != 0
    assert "inside this repository" in checked.stderr


def test_decision_validator_rejects_fake_human_signed_pending_record() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    decision_path = SCRATCH / "invalid-human-signed.json"
    record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    record["status"] = "human-signed"
    record["decision"] = "pending"
    decision_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    try:
        checked = run_script("validate", str(decision_path.relative_to(ROOT)))
        assert checked.returncode != 0
        assert "human-signed records require a named reviewer" in checked.stderr
        assert "human-signed records require accept, revise, defer, or reject" in checked.stderr
    finally:
        remove_scratch(SCRATCH)
