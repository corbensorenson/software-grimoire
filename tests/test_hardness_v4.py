#!/usr/bin/env python3
"""Validate Bench v4 hardness-ladder evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "examples" / "evaluations" / "hardness-v4" / "results.json"
MODEL_RESULTS = ROOT / "examples" / "evaluations" / "hardness-v4" / "model-surface-results.json"


def load_results() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def load_model_results() -> dict:
    return json.loads(MODEL_RESULTS.read_text(encoding="utf-8"))


def test_hardness_v4_has_five_executable_seed_rungs() -> None:
    results = load_results()
    assert results["repetitions_per_variant"] >= 5
    assert {case["rung"] for case in results["cases"].values()} >= {
        "ambiguity",
        "hidden-invariant",
        "misleading-context",
        "blast-radius",
        "agentic",
    }
    assert len(results["cases"]) >= 5
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


def test_hardness_v4_model_surface_results_cover_all_rungs() -> None:
    results = load_model_results()
    assert "codex-cli-default" in results["surfaces"]
    assert results["run_count"] >= 50
    assert results["minimum_repetitions_per_surface_variant"] >= 5
    assert {case["rung"] for case in results["cases"].values()} >= {
        "ambiguity",
        "hidden-invariant",
        "misleading-context",
        "blast-radius",
        "agentic",
    }
    for slug, case in results["cases"].items():
        assert (ROOT / case["fixture_path"]).is_dir(), slug
        assert (ROOT / case["ground_truth_path"]).exists(), slug
        assert case["summary"]["weak_runs"] >= 5
        assert case["summary"]["repaired_runs"] >= 5
        for variant in {"weak", "repaired"}:
            runs = [
                run
                for run in case["runs"]
                if run["surface"] == "codex-cli-default" and run["variant"] == variant
            ]
            assert len(runs) >= 5, f"{slug} {variant}"
            assert sorted(run["repetition"] for run in runs)[:5] == [1, 2, 3, 4, 5]
        for run in case["runs"]:
            assert run["evidence_class"] == "project_owned_model_run"
            assert run["tool_version"].startswith("codex-cli")
            assert (ROOT / run["prompt_path"]).exists()
            assert (ROOT / run["transcript_path"]).exists()
            assert (ROOT / run["artifact_root"]).exists()
            assert run["execution_result"]["passed"] in {True, False}
            for path in run["artifact_paths"]:
                assert (ROOT / path).exists()


def test_hardness_model_extraction_rejects_disallowed_paths() -> None:
    from scripts.run_hardness_model_surfaces import extract_artifacts

    output = """```path=../escape.py
print("bad")
```

```path=account_status.py
def classify_account(last_seen_at, disabled_at=None, now=None):
    return "unknown"
```
"""
    artifacts, errors = extract_artifacts(output, ["account_status.py"])
    assert set(artifacts) == {"account_status.py"}
    assert any("disallowed path" in error for error in errors)
