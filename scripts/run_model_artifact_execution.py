#!/usr/bin/env python3
"""Ask model surfaces for executable artifacts and grade them in fixture-local sandboxes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from bootstrap_project import PROOF_CASES, ROOT
from run_evaluations import build_prompt
from surface_adapters import enrich_run_metadata, runnable_surfaces, run_surface, surface_for_result


SURFACES = {surface_id: surface_for_result(surface_id) for surface_id in runnable_surfaces()}
TIMEOUT_SECONDS = 20


def extract_code(text: str, language: str = "python") -> str:
    pattern = rf"```(?:{language}|py)?\s*(.*?)```"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def fixture_file_text(case: str, tier: str, filename: str) -> str:
    fixture = ROOT / "examples" / "evaluations" / "fixtures" / (case if tier == "clean" else f"{case}-trap")
    return (fixture / filename).read_text(encoding="utf-8").strip()


def safe_refactoring_prompt(tier: str, variant: str) -> str:
    return (
        build_prompt("safe-refactoring", variant, tier)
        + f"""
You have all source needed below. Do not ask to read files.

CURRENT normalize_user.py:
```python
{fixture_file_text("safe-refactoring", tier, "normalize_user.py")}
```

EXECUTABLE CHECK check_normalize_user.py:
```python
{fixture_file_text("safe-refactoring", tier, "check_normalize_user.py")}
```

Return only a complete replacement for normalize_user.py in one fenced python code block.
Preserve the public function name, accepted inputs, return keys, and exception class behavior required by the check file.
"""
    )


def test_generation_prompt(variant: str) -> str:
    return (
        build_prompt("test-generation", variant, "clean")
        + f"""
You have all source needed below. Do not ask to read files.

CURRENT pricing.py:
```python
{fixture_file_text("test-generation", "clean", "pricing.py")}
```

EXPECTED BEHAVIOR:
```json
{fixture_file_text("test-generation", "clean", "expected_behavior.json")}
```

Return only a complete pytest file for pricing.py in one fenced python code block.
The tests must import `price_for` from `pricing` and must not assert private implementation details.
Do not include prose outside the code block.
"""
    )


def run_pytest(fixture: Path, files: dict[str, str], test_file: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="grimoire-model-artifact-") as raw_tmp:
        tmp = Path(raw_tmp)
        shutil.copytree(fixture, tmp, dirs_exist_ok=True)
        for rel, content in files.items():
            target = tmp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", test_file],
            cwd=tmp,
            check=False,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    return {
        "status": "passed" if completed.returncode == 0 else "failed",
        "passed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "timeout_seconds": TIMEOUT_SECONDS,
    }


def evaluate_safe_refactoring(surface: str, tier: str, variant: str) -> dict:
    prompt = safe_refactoring_prompt(tier, variant)
    output = run_surface(surface, prompt)
    code = extract_code(output)
    fixture = ROOT / "examples" / "evaluations" / "fixtures" / ("safe-refactoring" if tier == "clean" else "safe-refactoring-trap")
    out_dir = ROOT / "examples" / "evaluations" / "model-artifacts" / surface / "safe-refactoring" / tier / variant
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = out_dir / "prompt.md"
    transcript_path = out_dir / "output.md"
    artifact_path = out_dir / "normalize_user.py"
    prompt_path.write_text(prompt, encoding="utf-8")
    transcript_path.write_text(output.rstrip() + "\n", encoding="utf-8")
    artifact_path.write_text(code, encoding="utf-8")
    execution_result = run_pytest(fixture, {"normalize_user.py": code}, "check_normalize_user.py")
    return {
        **enrich_run_metadata(surface),
        "case_slug": "safe-refactoring",
        "tier": tier,
        "variant": variant,
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "fixture_path": str(fixture.relative_to(ROOT)),
        "prompt_path": str(prompt_path.relative_to(ROOT)),
        "transcript_path": str(transcript_path.relative_to(ROOT)),
        "artifact_path": str(artifact_path.relative_to(ROOT)),
        "execution_command": "python -m pytest -q check_normalize_user.py",
        "execution_result": execution_result,
        "grader_version": "model-artifact-execution-v3.0.0",
    }


def evaluate_test_generation(surface: str, variant: str) -> dict:
    prompt = test_generation_prompt(variant)
    output = run_surface(surface, prompt)
    code = extract_code(output)
    fixture = ROOT / "examples" / "evaluations" / "fixtures" / "test-generation"
    out_dir = ROOT / "examples" / "evaluations" / "model-artifacts" / surface / "test-generation" / "clean" / variant
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = out_dir / "prompt.md"
    transcript_path = out_dir / "output.md"
    artifact_path = out_dir / "test_pricing.py"
    prompt_path.write_text(prompt, encoding="utf-8")
    transcript_path.write_text(output.rstrip() + "\n", encoding="utf-8")
    artifact_path.write_text(code, encoding="utf-8")
    execution_result = run_pytest(fixture, {"test_pricing.py": code}, "test_pricing.py")
    return {
        **enrich_run_metadata(surface),
        "case_slug": "test-generation",
        "tier": "clean",
        "variant": variant,
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "fixture_path": str(fixture.relative_to(ROOT)),
        "prompt_path": str(prompt_path.relative_to(ROOT)),
        "transcript_path": str(transcript_path.relative_to(ROOT)),
        "artifact_path": str(artifact_path.relative_to(ROOT)),
        "execution_command": "python -m pytest -q test_pricing.py",
        "execution_result": execution_result,
        "grader_version": "model-artifact-execution-v3.0.0",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=sorted(SURFACES), action="append", help="surface to run; repeatable")
    parser.add_argument("--case", choices=["safe-refactoring", "test-generation"], action="append", help="case to run; repeatable")
    parser.add_argument("--tier", choices=["clean", "trap"], action="append", help="safe-refactoring tier to run; repeatable")
    args = parser.parse_args()

    surfaces = args.surface or list(SURFACES)
    cases = args.case or ["safe-refactoring", "test-generation"]
    tiers = args.tier or ["clean", "trap"]
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "3.0.0-model-artifact-execution",
        "policy": "Model outputs are saved as artifacts and graded only inside fixture-local temporary directories.",
        "surfaces": {surface: SURFACES[surface] for surface in surfaces},
        "cases": {},
    }

    for case in cases:
        runs = []
        for surface in surfaces:
            if case == "safe-refactoring":
                for tier in tiers:
                    for variant in ["weak", "repaired"]:
                        print(f"Running model artifact {surface} safe-refactoring {tier} {variant}...")
                        runs.append(evaluate_safe_refactoring(surface, tier, variant))
            elif case == "test-generation":
                for variant in ["weak", "repaired"]:
                    print(f"Running model artifact {surface} test-generation clean {variant}...")
                    runs.append(evaluate_test_generation(surface, variant))
        results["cases"][case] = {
            "title": PROOF_CASES[case]["title"],
            "runs": runs,
        }

    out = ROOT / "examples" / "evaluations" / "model-execution-results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
