#!/usr/bin/env python3
"""Validate defensive jailbreak-resilience bench evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "examples" / "jailbreak-resilience" / "results.json"
EXPECTED_AXES = {"attack_resistance", "utility_preservation", "audit_quality"}


def load_results() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_jailbreak_results_have_declared_surfaces_and_axes() -> None:
    results = load_results()
    assert results["payload_policy"] == "defanged-fixtures-only"
    assert results["surfaces"]
    assert set(results["scoring_axes"]) == EXPECTED_AXES
    for name, surface in results["surfaces"].items():
        assert name
        assert surface["kind"]
        assert surface["label"]


def test_all_jailbreak_cases_have_repeated_runs() -> None:
    data = json.loads((ROOT / "data" / "jailbreak_resilience.json").read_text(encoding="utf-8"))
    results = load_results()
    assert set(results["cases"]) == set(data["cases"])
    for slug, case in results["cases"].items():
        assert len(case["runs"]) >= 3, slug
        assert (ROOT / case["fixture_path"]).exists()
        for run in case["runs"]:
            assert run["surface"] in results["surfaces"]
            assert run["repetition"] >= 1
            assert run["run_timestamp"]
            assert set(run["scores"]) == EXPECTED_AXES
            assert set(run["axis_totals"]) == EXPECTED_AXES
            assert run["total_score"] == sum(run["axis_totals"].values())
            assert run["evaluator_notes"]
            assert (ROOT / run["fixture_path"]).exists()
            assert (ROOT / run["prompt_path"]).exists()
            transcript = ROOT / run["transcript_path"]
            assert transcript.exists()
            assert transcript.read_text(encoding="utf-8").strip() == run["output"].strip()


def test_jailbreak_runs_preserve_utility_not_blanket_refusal() -> None:
    results = load_results()
    utility_scores = [
        run["axis_totals"]["utility_preservation"]
        for case in results["cases"].values()
        for run in case["runs"]
    ]
    assert any(score > 0 for score in utility_scores)


def test_no_canary_values_leak_in_recorded_outputs() -> None:
    data = json.loads((ROOT / "data" / "jailbreak_resilience.json").read_text(encoding="utf-8"))
    results = load_results()
    forbidden_by_case = {
        slug: case["forbidden_strings"]
        for slug, case in data["cases"].items()
    }
    leaks = []
    for slug, case in results["cases"].items():
        forbidden = [item.lower() for item in forbidden_by_case[slug]]
        for run in case["runs"]:
            lowered = run["output"].lower()
            for value in forbidden:
                if value and value in lowered:
                    leaks.append((slug, run["repetition"], value))
    assert not leaks
