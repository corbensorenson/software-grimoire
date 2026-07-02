#!/usr/bin/env python3
"""Smoke-test standalone adoption report generation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "tmp" / "tests" / "adoption-report"


def base_args(output: Path) -> list[str]:
    return [
        "--id",
        "adoption.example-hardness-review.v1",
        "--title",
        "Example Hardness Review",
        "--provenance",
        "reviewer-supplied",
        "--task",
        "Review a Bench v4 fixture for ambiguity and hidden invariant coverage.",
        "--spell-or-stack-used",
        "stack.release-gate-stack.v1",
        "--surface",
        "Local reviewer workflow",
        "--artifact-produced",
        "A schema-valid adoption report draft.",
        "--verification-performed",
        "Validated against schemas/adoption-report.schema.json.",
        "--time-cost",
        "Low; under ten minutes for a prepared reviewer.",
        "--failure-or-friction",
        "The report still requires maintainer review before publication.",
        "--reuse-decision",
        "reuse",
        "--write-report",
        str(output.relative_to(ROOT)),
    ]


def test_create_adoption_report_writes_schema_valid_record() -> None:
    shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    output = SCRATCH / "adoption-report.json"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "create_adoption_report.py"), *base_args(output)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        assert completed.returncode == 0, completed.stderr
        report = json.loads(output.read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "adoption-report.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(report)
        assert report["provenance"] == "reviewer-supplied"
        aggregate = json.loads((ROOT / "data" / "adoption_evidence.json").read_text(encoding="utf-8"))
        assert aggregate["external_status"]["external_reports_published"] == 0
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


def test_grimoire_adoption_report_wrapper_and_path_guard() -> None:
    shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    output = SCRATCH / "wrapped-adoption-report.json"
    wrapped = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "grimoire.py"), "adoption", "report", "--", *base_args(output)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    outside = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "create_adoption_report.py"),
            *base_args(output)[:-1],
            str(ROOT.parent / "outside-adoption-report.json"),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        assert wrapped.returncode == 0, wrapped.stderr
        assert output.exists()
        assert outside.returncode != 0
        assert "inside this repository" in outside.stderr
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
