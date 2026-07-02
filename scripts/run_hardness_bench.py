#!/usr/bin/env python3
"""Run Bench v4 hardness-ladder artifacts in repo-local sandboxes."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_DIR = ROOT / "tmp"
TIMEOUT_SECONDS = 15
DEFAULT_REPETITIONS = 5

CASES = {
    "ambiguity-disabled-status": {
        "title": "Disabled Account Status Ambiguity",
        "rung": "ambiguity",
        "hardness_axis": "conflicting docstring versus caller contract",
        "fixture": "examples/evaluations/hardness-v4/fixtures/ambiguity-disabled-status",
        "artifact": "account_status.py",
        "test_file": "check_account_status.py",
    },
    "hidden-invariant-event-order": {
        "title": "Event Deduplication Hidden Order Invariant",
        "rung": "hidden-invariant",
        "hardness_axis": "order and replay semantics hidden behind simple dedupe wording",
        "fixture": "examples/evaluations/hardness-v4/fixtures/hidden-invariant-event-order",
        "artifact": "events.py",
        "test_file": "check_events.py",
    },
    "misleading-context-tax-discount": {
        "title": "Tax Discount Misleading Context",
        "rung": "misleading-context",
        "hardness_axis": "stale inline comment contradicts current merchant contract",
        "fixture": "examples/evaluations/hardness-v4/fixtures/misleading-context-tax-discount",
        "artifact": "pricing.py",
        "test_file": "check_pricing.py",
    },
    "blast-radius-beta-flag": {
        "title": "Beta Flag Blast Radius",
        "rung": "blast-radius",
        "hardness_axis": "narrow feature-flag change versus tempting billing overreach",
        "fixture": "examples/evaluations/hardness-v4/fixtures/blast-radius-beta-flag",
        "artifact": "change_manifest.json",
        "artifact_files": ["feature_flags.py", "billing.py", "change_manifest.json"],
        "test_file": "check_blast_radius.py",
    },
    "agentic-release-handoff": {
        "title": "Agentic Release Handoff",
        "rung": "agentic",
        "hardness_axis": "multi-step stack handoff with repo-local scratch and gate evidence",
        "fixture": "examples/evaluations/hardness-v4/fixtures/agentic-release-handoff",
        "artifact": "handoff.json",
        "test_file": "check_handoff.py",
    },
}


def artifact_files(case: dict) -> list[str]:
    return list(case.get("artifact_files", [case["artifact"]]))


def artifact_path(case_slug: str, variant: str, case: dict) -> str:
    base = f"examples/evaluations/hardness-v4/artifacts/{case_slug}/{variant}"
    files = artifact_files(case)
    if len(files) == 1:
        return f"{base}/{files[0]}"
    return base


def run_artifact(case_slug: str, variant: str) -> dict:
    case = CASES[case_slug]
    fixture = ROOT / case["fixture"]
    artifact_root = ROOT / "examples" / "evaluations" / "hardness-v4" / "artifacts" / case_slug / variant
    if not fixture.is_dir():
        raise FileNotFoundError(f"missing fixture: {fixture}")
    for relative_artifact in artifact_files(case):
        artifact = artifact_root / relative_artifact
        if not artifact.exists():
            raise FileNotFoundError(f"missing artifact: {artifact}")

    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-hardness-v4-", dir=SCRATCH_DIR) as raw_tmp:
        sandbox = Path(raw_tmp)
        shutil.copytree(fixture, sandbox, dirs_exist_ok=True)
        for relative_artifact in artifact_files(case):
            artifact = artifact_root / relative_artifact
            destination = sandbox / relative_artifact
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(artifact, destination)
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", case["test_file"]],
            cwd=sandbox,
            check=False,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        )
    return {
        "status": "passed" if completed.returncode == 0 else "failed",
        "passed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip()[-4000:],
        "stderr": completed.stderr.strip()[-4000:],
        "timeout_seconds": TIMEOUT_SECONDS,
    }


def summarize_runs(runs: list[dict]) -> dict:
    weak = [run for run in runs if run["variant"] == "weak"]
    repaired = [run for run in runs if run["variant"] == "repaired"]
    weak_passes = sum(1 for run in weak if run["execution_result"]["passed"] is True)
    repaired_passes = sum(1 for run in repaired if run["execution_result"]["passed"] is True)
    return {
        "weak_runs": len(weak),
        "repaired_runs": len(repaired),
        "weak_passes": weak_passes,
        "repaired_passes": repaired_passes,
        "execution_delta": f"weak passed {weak_passes}/{len(weak)}; repaired passed {repaired_passes}/{len(repaired)}",
    }


def build_results(case_slugs: list[str], repetitions: int) -> dict:
    results = {
        "generated_at": "2026-07-02T00:00:00Z",
        "version": "4.0.0-hardness-ladder-seed",
        "policy": "Bench v4 hardness fixtures run only local deterministic tests inside repo-local tmp/ sandboxes. Model-surface runs are not simulated.",
        "repetitions_per_variant": repetitions,
        "surfaces": {
            "local-deterministic-grader": {
                "kind": "local-tool",
                "label": "Fixture-local deterministic pytest grader",
                "provenance": "project-owned",
                "limitation": "Execution evidence for seed artifacts, not independent model-provider evidence.",
            }
        },
        "cases": {},
    }
    for case_slug in case_slugs:
        case = CASES[case_slug]
        runs = []
        for variant in ["weak", "repaired"]:
            for repetition in range(1, repetitions + 1):
                execution_result = run_artifact(case_slug, variant)
                runs.append(
                    {
                        "case_slug": case_slug,
                        "title": case["title"],
                        "rung": case["rung"],
                        "hardness_axis": case["hardness_axis"],
                        "variant": variant,
                        "repetition": repetition,
                        "surface": "local-deterministic-grader",
                        "fixture_path": case["fixture"],
                        "ground_truth_path": f"{case['fixture']}/ground_truth.json",
                        "artifact_path": artifact_path(case_slug, variant, case),
                        "execution_command": f"python -m pytest -q {case['test_file']}",
                        "execution_result": execution_result,
                        "grader_version": "hardness-v4-pytest-v1",
                    }
                )
        results["cases"][case_slug] = {
            "title": case["title"],
            "rung": case["rung"],
            "hardness_axis": case["hardness_axis"],
            "fixture_path": case["fixture"],
            "ground_truth_path": f"{case['fixture']}/ground_truth.json",
            "artifact": case["artifact"],
            "test_file": case["test_file"],
            "runs": runs,
            "summary": summarize_runs(runs),
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), action="append", help="case to run; repeatable")
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS)
    parser.add_argument("--write-report", default="examples/evaluations/hardness-v4/results.json")
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")

    case_slugs = args.case or list(CASES)
    results = build_results(case_slugs, args.repetitions)
    out = ROOT / args.write_report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    failures = []
    for case_slug, case in results["cases"].items():
        summary = case["summary"]
        if summary["weak_passes"] != 0:
            failures.append(f"{case_slug}: weak artifacts should fail all repetitions")
        if summary["repaired_passes"] != summary["repaired_runs"]:
            failures.append(f"{case_slug}: repaired artifacts should pass all repetitions")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
