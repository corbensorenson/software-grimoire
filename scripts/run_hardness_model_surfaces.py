#!/usr/bin/env python3
"""Run Bench v4 hardness rungs against recorded model-surface outputs."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:  # pragma: no cover - exercised by direct script invocation
    from run_hardness_bench import CASES, TIMEOUT_SECONDS, artifact_files, normalize_pytest_output
    from surface_adapters import enrich_run_metadata, run_surface, surface_for_result
except ImportError:  # pragma: no cover - exercised by package imports in tests
    from scripts.run_hardness_bench import CASES, TIMEOUT_SECONDS, artifact_files, normalize_pytest_output
    from scripts.surface_adapters import enrich_run_metadata, run_surface, surface_for_result


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_DIR = ROOT / "tmp"
OUT_PATH = ROOT / "examples" / "evaluations" / "hardness-v4" / "model-surface-results.json"
RUN_ROOT = ROOT / "examples" / "evaluations" / "hardness-v4" / "model-runs"
GRADER_VERSION = "hardness-v4-model-surface-pytest-v1"
FENCE_RE = re.compile(r"```(?P<info>[^\n`]*)\n(?P<body>.*?)```", re.DOTALL)
PATH_RE = re.compile(r"(?:path|file|filename)\s*=\s*[\"']?(?P<path>[A-Za-z0-9_.\-/]+)[\"']?", re.IGNORECASE)
INLINE_PATH_RE = re.compile(r"^\s*(?:#|//|--|<!--)?\s*(?:file|path|filename)\s*:\s*(?P<path>[A-Za-z0-9_.\-/]+)\s*(?:-->)?\s*$", re.IGNORECASE)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def display(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_fixture_files(case: dict) -> str:
    fixture = ROOT / case["fixture"]
    chunks = []
    for path in sorted(fixture.iterdir()):
        if not path.is_file():
            continue
        if path.name == "context.md" or path.name.startswith("check_") or path.name == "ground_truth.json":
            continue
        chunks.append(f"### {path.name}\n\n```{path.suffix.removeprefix('.') or 'text'}\n{path.read_text(encoding='utf-8').rstrip()}\n```")
    return "\n\n".join(chunks)


def output_contract(case_slug: str) -> str:
    expected = artifact_files(CASES[case_slug])
    lines = [
        "Return only the replacement artifact files. Use one fenced block per file.",
        "Each fence must identify the path using `path=<filename>` in the fence info string.",
        "Do not include the hidden grader, shell commands, prose explanations, or files outside this list.",
        "Allowed output paths:",
    ]
    lines.extend(f"- `{item}`" for item in expected)
    if case_slug == "blast-radius-beta-flag":
        lines.append("For `change_manifest.json`, record only the files intentionally changed and the out-of-scope files preserved.")
    return "\n".join(lines)


def build_prompt(case_slug: str, variant: str) -> str:
    case = CASES[case_slug]
    context = (ROOT / case["fixture"] / "context.md").read_text(encoding="utf-8").strip()
    files = read_fixture_files(case)
    contract = output_contract(case_slug)
    if variant == "weak":
        return f"""You are helping with a small software task.

Task context:

{context}

Starting files:

{files}

{contract}
"""
    if variant == "repaired":
        return f"""ROLE
Act as a careful software engineer producing the smallest reviewable artifact that satisfies the task.

OBJECTIVE
Solve this Bench v4 hardness-rung task without changing behavior outside the stated artifact boundary.

CONTEXT
{context}

STARTING FILES
{files}

CONSTRAINTS
- Prefer the current task contract over stale comments or misleading local context.
- Preserve public function names and compatible behavior unless the task explicitly says otherwise.
- Keep blast radius narrow: change only the allowed artifact files and document preserved out-of-scope files when a manifest is requested.
- Do not invent human signoff, external approval, network access, or device-global scratch paths.
- If the task is underspecified, encode the safest bounded behavior rather than guessing hidden state.

OUTPUT CONTRACT
{contract}

VERIFICATION
The replacement files will be applied to a disposable repo-local fixture copy and checked by a private deterministic grader. Return only artifacts that should pass that check.
"""
    raise ValueError(f"unknown variant: {variant}")


def normalize_path(path: str, expected: set[str]) -> str | None:
    clean = path.strip().strip("`'\"")
    clean = clean.removeprefix("./")
    if clean in expected:
        return clean
    basename = Path(clean).name
    if basename in expected:
        return basename
    return None


def path_from_fence(info: str, body: str, expected: set[str]) -> tuple[str | None, str, bool]:
    match = PATH_RE.search(info)
    if match:
        return normalize_path(match.group("path"), expected), body, True
    lines = body.splitlines()
    if lines:
        inline = INLINE_PATH_RE.match(lines[0])
        if inline:
            return normalize_path(inline.group("path"), expected), "\n".join(lines[1:]).lstrip("\n"), True
    return None, body, False


def extract_json_document(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start : end + 1]
    try:
        json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return candidate


def extract_artifacts(output: str, expected_files: list[str]) -> tuple[dict[str, str], list[str]]:
    expected = set(expected_files)
    artifacts: dict[str, str] = {}
    errors: list[str] = []
    fences = list(FENCE_RE.finditer(output))
    for fence in fences:
        info = fence.group("info").strip()
        body = fence.group("body").strip()
        path, body, declared_path = path_from_fence(info, body, expected)
        if path is None and declared_path:
            errors.append(f"ignored fenced block with disallowed path: {info or 'inline-path'}")
            continue
        if path is None and len(expected_files) == 1:
            path = expected_files[0]
        if path is None:
            errors.append(f"ignored fenced block with missing or disallowed path: {info or 'no-info'}")
            continue
        artifacts[path] = body.rstrip() + "\n"

    if not artifacts and len(expected_files) == 1 and expected_files[0].endswith(".json"):
        candidate = extract_json_document(output)
        if candidate is not None:
            artifacts[expected_files[0]] = candidate.rstrip() + "\n"

    missing = [path for path in expected_files if path not in artifacts]
    if missing:
        errors.append("missing expected artifact file(s): " + ", ".join(missing))
    return artifacts, errors


def write_artifacts(artifact_root: Path, artifacts: dict[str, str]) -> list[str]:
    written = []
    for relative, text in artifacts.items():
        destination = artifact_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        written.append(display(destination))
    return written


def run_extracted_artifacts(case_slug: str, artifact_root: Path) -> dict:
    case = CASES[case_slug]
    fixture = ROOT / case["fixture"]
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-hardness-model-", dir=SCRATCH_DIR) as raw_tmp:
        sandbox = Path(raw_tmp)
        shutil.copytree(fixture, sandbox, dirs_exist_ok=True)
        for relative_artifact in artifact_files(case):
            artifact = artifact_root / relative_artifact
            if not artifact.exists():
                return {
                    "status": "failed",
                    "passed": False,
                    "exit_code": 2,
                    "stdout": "",
                    "stderr": f"missing extracted artifact: {relative_artifact}",
                    "timeout_seconds": TIMEOUT_SECONDS,
                }
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
        "stdout": normalize_pytest_output(completed.stdout.strip())[-4000:],
        "stderr": normalize_pytest_output(completed.stderr.strip())[-4000:],
        "timeout_seconds": TIMEOUT_SECONDS,
    }


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {
            "generated_at": None,
            "version": "4.0.0-hardness-model-surfaces",
            "policy": (
                "Bench v4 model-surface hardness runs preserve prompts, transcripts, extracted artifacts, "
                "and fixture-local execution results. Hidden graders are not included in prompts. "
                "Scratch execution stays under repo-local tmp/."
            ),
            "surfaces": {},
            "cases": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def next_repetition(runs: list[dict], surface: str, variant: str) -> int:
    prior = [run.get("repetition", 0) for run in runs if run.get("surface") == surface and run.get("variant") == variant]
    return (max(prior) if prior else 0) + 1


def summarize_runs(runs: list[dict]) -> dict:
    weak = [run for run in runs if run.get("variant") == "weak"]
    repaired = [run for run in runs if run.get("variant") == "repaired"]
    weak_passes = sum(1 for run in weak if run.get("execution_result", {}).get("passed") is True)
    repaired_passes = sum(1 for run in repaired if run.get("execution_result", {}).get("passed") is True)
    extraction_failures = sum(1 for run in runs if run.get("extraction_result", {}).get("complete") is not True)
    pairs = []
    repetitions = sorted({run.get("repetition") for run in runs})
    for repetition in repetitions:
        weak_run = next((run for run in weak if run.get("repetition") == repetition), None)
        repaired_run = next((run for run in repaired if run.get("repetition") == repetition), None)
        if weak_run is None or repaired_run is None:
            continue
        weak_pass = bool(weak_run.get("execution_result", {}).get("passed"))
        repaired_pass = bool(repaired_run.get("execution_result", {}).get("passed"))
        if repaired_pass and not weak_pass:
            pairs.append("repaired_win")
        elif weak_pass and not repaired_pass:
            pairs.append("weak_win")
        else:
            pairs.append("tie")
    return {
        "weak_runs": len(weak),
        "repaired_runs": len(repaired),
        "weak_passes": weak_passes,
        "repaired_passes": repaired_passes,
        "extraction_failures": extraction_failures,
        "execution_delta": f"weak passed {weak_passes}/{len(weak)}; repaired passed {repaired_passes}/{len(repaired)}",
        "paired_signs": {
            "repaired_wins": pairs.count("repaired_win"),
            "weak_wins": pairs.count("weak_win"),
            "ties": pairs.count("tie"),
        },
    }


def recompute_summaries(results: dict) -> None:
    total_runs = 0
    for case in results.get("cases", {}).values():
        case["summary"] = summarize_runs(case.get("runs", []))
        total_runs += len(case.get("runs", []))
    results["run_count"] = total_runs
    repetitions = [
        len([run for run in case.get("runs", []) if run.get("surface") == surface and run.get("variant") == variant])
        for case in results.get("cases", {}).values()
        for surface in results.get("surfaces", {})
        for variant in ["weak", "repaired"]
    ]
    results["minimum_repetitions_per_surface_variant"] = min(repetitions) if repetitions else 0


def run_one(surface: str, case_slug: str, variant: str, repetition: int) -> dict:
    case = CASES[case_slug]
    prompt = build_prompt(case_slug, variant)
    run_dir = RUN_ROOT / surface / case_slug / variant
    artifact_root = run_dir / f"r{repetition:02d}-artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / f"r{repetition:02d}-prompt.md"
    transcript_path = run_dir / f"r{repetition:02d}-output.md"
    prompt_path.write_text(prompt.rstrip() + "\n", encoding="utf-8")
    output = run_surface(surface, prompt)
    transcript_path.write_text(output.rstrip() + "\n", encoding="utf-8")

    expected = artifact_files(case)
    artifacts, extraction_errors = extract_artifacts(output, expected)
    written = write_artifacts(artifact_root, artifacts)
    complete = not extraction_errors and set(artifacts) == set(expected)
    execution_result = (
        run_extracted_artifacts(case_slug, artifact_root)
        if complete
        else {
            "status": "failed",
            "passed": False,
            "exit_code": 2,
            "stdout": "",
            "stderr": "; ".join(extraction_errors),
            "timeout_seconds": TIMEOUT_SECONDS,
        }
    )
    run = {
        **enrich_run_metadata(surface),
        "case_slug": case_slug,
        "title": case["title"],
        "rung": case["rung"],
        "hardness_axis": case["hardness_axis"],
        "variant": variant,
        "repetition": repetition,
        "run_timestamp": iso_now(),
        "fixture_path": case["fixture"],
        "ground_truth_path": f"{case['fixture']}/ground_truth.json",
        "prompt_path": display(prompt_path),
        "transcript_path": display(transcript_path),
        "artifact_root": display(artifact_root),
        "artifact_paths": written,
        "execution_command": f"python -m pytest -q {case['test_file']}",
        "execution_result": execution_result,
        "extraction_result": {
            "complete": complete,
            "expected_files": expected,
            "extracted_files": sorted(artifacts),
            "errors": extraction_errors,
        },
        "grader_version": GRADER_VERSION,
    }
    return run


def run_matrix(surfaces: list[str], case_slugs: list[str], repetitions: int, out_path: Path, append: bool) -> dict:
    results = load_existing(out_path) if append else load_existing(Path("__missing__"))
    results["generated_at"] = iso_now()
    for surface in surfaces:
        surface_meta = surface_for_result(surface)
        results["surfaces"][surface] = {
            "kind": surface_meta["kind"],
            "label": surface_meta["label"],
            "provenance": surface_meta["ownership"],
            "execution": surface_meta["execution"],
            "tool_name": surface_meta["tool_name"],
            "tool_version": surface_meta["tool_version"],
            "model_name": surface_meta["model_name"],
            "evidence_class": surface_meta["evidence_class"],
            "limitation": "Model-produced artifacts are graded by fixture-local hidden tests; failures and extraction errors are preserved.",
        }
    for case_slug in case_slugs:
        case = CASES[case_slug]
        record = results["cases"].setdefault(
            case_slug,
            {
                "title": case["title"],
                "rung": case["rung"],
                "hardness_axis": case["hardness_axis"],
                "fixture_path": case["fixture"],
                "ground_truth_path": f"{case['fixture']}/ground_truth.json",
                "artifact": case["artifact"],
                "artifact_files": artifact_files(case),
                "test_file": case["test_file"],
                "runs": [],
                "summary": {},
            },
        )
        for surface in surfaces:
            for variant in ["weak", "repaired"]:
                for _ in range(repetitions):
                    repetition = next_repetition(record["runs"], surface, variant) if append else len(
                        [run for run in record["runs"] if run.get("surface") == surface and run.get("variant") == variant]
                    ) + 1
                    print(f"Running hardness model surface {surface} {case_slug} {variant} r{repetition:02d}...")
                    record["runs"].append(run_one(surface, case_slug, variant, repetition))
    recompute_summaries(results)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", action="append", help="surface id to run; repeatable")
    parser.add_argument("--case", choices=sorted(CASES), action="append", help="case to run; repeatable")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--append", action="store_true", help="append repetitions to an existing report")
    parser.add_argument("--write-report", default=str(OUT_PATH.relative_to(ROOT)))
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")

    out_path = ROOT / args.write_report
    case_slugs = args.case or list(CASES)
    surfaces = args.surface or ["codex-cli-default"]
    results = run_matrix(surfaces, case_slugs, args.repetitions, out_path, args.append)
    print(f"Wrote {display(out_path)} with {results['run_count']} model-surface hardness runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
