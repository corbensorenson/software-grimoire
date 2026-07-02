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


def test_evaluations_have_declared_surfaces() -> None:
    results = load_results()
    surface_names = set(results.get("surfaces", {}))
    assert surface_names
    for name, surface in results["surfaces"].items():
        assert name
        assert surface.get("label")
        assert surface.get("kind")


def test_all_field_spells_have_weak_and_repaired_runs() -> None:
    results = load_results()
    assert set(results.get("cases", {})) == EXPECTED_CASES
    for slug, case in results["cases"].items():
        variants = {run["variant"] for run in case.get("runs", [])}
        assert variants == {"weak", "repaired"}, slug
        assert case.get("observed_delta") and case["observed_delta"] != "pending", slug
        assert case.get("observed_outcome_delta") and case["observed_outcome_delta"] != "pending", slug
        assert (ROOT / case["fixture_path"]).exists()
        for run in case["runs"]:
            assert run["surface"] in results["surfaces"]
            structural = run.get("structural_scores") or run["scores"]
            assert set(structural) == EXPECTED_CRITERIA
            assert all(score in {0, 1, 2} for score in structural.values())
            assert run["structural_total"] == sum(structural.values())
            assert run["outcome_scores"]
            assert run["outcome_total"] == sum(run["outcome_scores"].values())
            assert run.get("run_timestamp")
            assert run.get("evaluator_notes")
            assert run.get("repetition", 0) >= 1
            assert (ROOT / run["fixture_path"]).exists()
            assert (ROOT / run["prompt_path"]).exists()
            transcript = ROOT / run["transcript_path"]
            assert transcript.exists()
            assert transcript.read_text(encoding="utf-8").strip() == run["output"].strip()


def test_results_include_honest_non_perfect_outcomes() -> None:
    results = load_results()
    non_perfect = [
        case
        for case in results["cases"].values()
        if "tied" in case.get("observed_outcome_delta", "")
        or case.get("observed_outcome_delta", "").startswith("weak prompts satisfied")
    ]
    assert non_perfect, "evaluation evidence should preserve ties and losses instead of requiring perfect wins"
