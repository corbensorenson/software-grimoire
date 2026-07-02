#!/usr/bin/env python3
"""Validate Bench v4 hardness-ladder evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "examples" / "evaluations" / "hardness-v4" / "results.json"


def load_results() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_hardness_v4_has_two_executable_seed_rungs() -> None:
    results = load_results()
    assert results["repetitions_per_variant"] >= 5
    assert {case["rung"] for case in results["cases"].values()} >= {"ambiguity", "hidden-invariant"}
    for slug, case in results["cases"].items():
        assert (ROOT / case["fixture_path"]).is_dir(), slug
        assert (ROOT / case["ground_truth_path"]).exists(), slug
        assert case["summary"]["weak_runs"] >= 5
        assert case["summary"]["repaired_runs"] >= 5
        assert case["summary"]["weak_passes"] == 0
        assert case["summary"]["repaired_passes"] == case["summary"]["repaired_runs"]
        for run in case["runs"]:
            assert run["surface"] == "local-deterministic-grader"
            assert (ROOT / run["artifact_path"]).exists()
            assert "tmp/" in results["policy"]


def test_hardness_v4_runner_replays_seed_cases() -> None:
    report = ROOT / "tmp" / "hardness-v4-test-results.json"
    report.unlink(missing_ok=True)
    executed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_hardness_bench.py"),
            "--write-report",
            str(report.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        assert executed.returncode == 0, executed.stderr
        replayed = json.loads(report.read_text(encoding="utf-8"))
        assert set(replayed["cases"]) == set(load_results()["cases"])
    finally:
        report.unlink(missing_ok=True)
