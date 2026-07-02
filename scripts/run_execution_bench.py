#!/usr/bin/env python3
"""Run execution-graded clean/trap fixtures for Software Grimoire."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from bootstrap_project import EXECUTION_BENCH_DATA, PROOF_CASES, SURFACE_COMPARISON_DATA, execution_run_record
except ModuleNotFoundError:
    from scripts.bootstrap_project import EXECUTION_BENCH_DATA, PROOF_CASES, SURFACE_COMPARISON_DATA, execution_run_record


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_DIR = ROOT / "tmp"
TIMEOUT_SECONDS = 15


def run_safe_refactoring_fixture(tier: str, variant: str) -> bool:
    fixture = ROOT / "examples" / "evaluations" / "fixtures" / "safe-refactoring"
    if tier == "trap":
        fixture = ROOT / "examples" / "evaluations" / "fixtures" / "safe-refactoring-trap"
    artifact = ROOT / "examples" / "evaluations" / "artifacts" / "safe-refactoring" / tier / variant / "normalize_user.py"
    if not fixture.is_dir():
        raise FileNotFoundError(f"missing fixture: {fixture}")
    if not artifact.exists():
        raise FileNotFoundError(f"missing artifact: {artifact}")
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-exec-bench-", dir=SCRATCH_DIR) as raw_tmp:
        tmp = Path(raw_tmp)
        shutil.copytree(fixture, tmp, dirs_exist_ok=True)
        shutil.copy2(artifact, tmp / "normalize_user.py")
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "check_normalize_user.py"],
            cwd=tmp,
            check=False,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    return completed.returncode == 0


def build_results() -> dict:
    data = EXECUTION_BENCH_DATA
    cases = {}
    for slug, tiers in data["cases"].items():
        records = []
        for tier, meta in tiers.items():
            if slug == "safe-refactoring":
                for variant in ["weak", "repaired"]:
                    passed = run_safe_refactoring_fixture(tier, variant)
                    records.append(execution_run_record(slug, tier, variant, passed))
            else:
                reason = meta["documented_reason"]
                records.append(execution_run_record(slug, tier, "weak", None, reason))
                records.append(execution_run_record(slug, tier, "repaired", None, reason))
        cases[slug] = {
            "title": PROOF_CASES[slug]["title"],
            "clean_fixture": tiers["clean"]["fixture_path"],
            "trap_fixture": tiers["trap"]["fixture_path"],
            "trap": tiers["trap"].get("trap"),
            "runs": records,
        }
    return {
        "generated_at": "2026-07-02T00:00:00Z",
        "version": data["version"],
        "policy": data["policy"],
        "surfaces": SURFACE_COMPARISON_DATA["surfaces"],
        "cases": cases,
    }


def main() -> int:
    results = build_results()
    output = ROOT / "examples" / "evaluations" / "execution-results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    failures: list[str] = []
    safe_runs = results["cases"]["safe-refactoring"]["runs"]
    for run in safe_runs:
        tier = run["tier"]
        variant = run["variant"]
        passed = run["execution_result"]["passed"]
        if variant == "weak" and passed is not False:
            failures.append(f"safe-refactoring {tier} weak artifact should fail")
        if variant == "repaired" and passed is not True:
            failures.append(f"safe-refactoring {tier} repaired artifact should pass")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"Wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
