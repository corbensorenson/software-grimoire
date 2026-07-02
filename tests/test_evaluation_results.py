#!/usr/bin/env python3
"""Validate preserved Proof by Difference evaluation evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "examples" / "evaluations" / "results.json"
EXPECTED_CASES = {
    "safe-refactoring",
    "bug-diagnosis-from-logs",
    "api-design",
    "migration-without-data-loss",
    "test-generation",
    "performance-tuning",
}
EXPECTED_CRITERIA = {
    "artifact_boundary",
    "invariants",
    "output_contract",
    "verification",
    "failure_behavior",
    "assumption_control",
}


def load_results() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_evaluations_are_codex_owned() -> None:
    results = load_results()
    blocked_surface = "cl" + "aude"
    surface_names = set(results.get("surfaces", {}))
    assert surface_names == {"codex-cli-default"}
    assert blocked_surface not in RESULTS.read_text(encoding="utf-8").lower()
    for path in (ROOT / "examples" / "evaluations" / "runs").rglob("*"):
        assert blocked_surface not in str(path.relative_to(ROOT)).lower()


def test_all_field_spells_have_weak_and_repaired_runs() -> None:
    results = load_results()
    assert set(results.get("cases", {})) == EXPECTED_CASES
    for slug, case in results["cases"].items():
        variants = {(run["surface"], run["variant"]) for run in case.get("runs", [])}
        assert variants == {("codex-cli-default", "weak"), ("codex-cli-default", "repaired")}, slug
        assert case.get("observed_delta") and case["observed_delta"] != "pending", slug
        for run in case["runs"]:
            assert set(run["scores"]) == EXPECTED_CRITERIA
            assert all(score in {0, 1, 2} for score in run["scores"].values())
            assert run["total_score"] == sum(run["scores"].values())
            assert run.get("run_timestamp")
            assert run.get("evaluator_notes")
            assert (ROOT / run["prompt_path"]).exists()
            transcript = ROOT / run["transcript_path"]
            assert transcript.exists()
            assert transcript.read_text(encoding="utf-8").strip() == run["output"].strip()


def test_results_include_honest_non_win() -> None:
    results = load_results()
    losses = [case for case in results["cases"].values() if case.get("observed_delta", "").startswith("weak prompts scored")]
    assert losses, "evaluation evidence should preserve losses instead of requiring perfect wins"
