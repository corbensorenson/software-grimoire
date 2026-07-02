#!/usr/bin/env python3
"""Validate Bench v4 hardness intake decision tooling."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "examples" / "evaluations" / "hardness-v4" / "hardness-intake-decision-template.json"
SCRIPT = ROOT / "scripts" / "check_hardness_intake.py"


def test_hardness_intake_template_validates_as_pending() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "validate", str(TEMPLATE.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Hardness intake decision record is valid" in completed.stdout
    assert "Maintainer decision remains pending" in completed.stdout


def test_hardness_intake_can_write_repo_local_normalized_artifact() -> None:
    scratch = ROOT / "tmp" / "tests" / "hardness-intake"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True, exist_ok=True)
    out = scratch / "normalized.json"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "validate",
                str(TEMPLATE.relative_to(ROOT)),
                "--write-normalized",
                str(out.relative_to(ROOT)),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["counts_as_cross_surface_hardness"] is False
        assert data["blocks_hardness_credit"] is True
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            scratch.parent.rmdir()
        except OSError:
            pass


def test_pending_hardness_intake_cannot_claim_credit() -> None:
    from scripts.check_hardness_intake import validate_decision

    scratch = ROOT / "tmp" / "tests" / "hardness-intake"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True, exist_ok=True)
    bad = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    bad["counts_as_cross_surface_hardness"] = True
    bad_path = scratch / "bad.json"
    bad_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
    try:
        assert validate_decision(bad_path) == 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            scratch.parent.rmdir()
        except OSError:
            pass


def test_hardness_intake_output_must_stay_inside_repo() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "validate",
            str(TEMPLATE.relative_to(ROOT)),
            "--write-normalized",
            str(ROOT.parent / "hardness-intake-normalized.json"),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "inside this repository" in completed.stderr
