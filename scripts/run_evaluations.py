#!/usr/bin/env python3
"""Run Proof by Difference evaluations against local Codex."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from bootstrap_project import EVALUATION_CONTEXTS, PROOF_CASES, ROOT


SURFACES = {
    "codex-cli-default": {
        "kind": "codex",
        "label": "Codex CLI default model",
    },
}

CRITERION_KEYWORDS = {
    "artifact_boundary": ["artifact", "module", "file", "endpoint", "table", "boundary", "scope", "function"],
    "invariants": ["invariant", "preserve", "must not", "unchanged", "compatibility", "correctness"],
    "output_contract": ["return", "section", "table", "plan", "format", "output", "checklist"],
    "verification": ["verify", "test", "measure", "check", "query", "evidence", "benchmark", "validate"],
    "failure_behavior": ["if", "fallback", "rollback", "insufficient", "unsafe", "risk", "cannot"],
    "assumption_control": ["assumption", "hypothesis", "unknown", "missing", "evidence", "uncertain", "insufficient"],
}

OUTCOME_RUBRICS = {
    "safe-refactoring": [
        {"id": "preserves_public_api", "description": "Names public function and return-key compatibility.", "keywords": ["public function", "return key", "return schema", "signature"]},
        {"id": "covers_behavior_trap", "description": "Protects unknown fields and falsy-but-valid values.", "keywords": ["unknown field", "unknown fields", "0", "false", "empty string", "falsy"]},
        {"id": "requires_tests", "description": "Requires executable tests for unchanged behavior.", "keywords": ["pytest", "test", "characterization", "edge"]},
    ],
    "bug-diagnosis-from-logs": [
        {"id": "names_planted_cause", "description": "Identifies Redis connection-pool saturation from the cache feature.", "keywords": ["redis", "connection pool", "pool", "profile_cache_v2", "cache"]},
        {"id": "separates_hypothesis", "description": "Separates facts, hypotheses, and missing signals.", "keywords": ["hypothesis", "fact", "missing", "evidence"]},
        {"id": "next_checks", "description": "Gives concrete next checks or commands.", "keywords": ["command", "dashboard", "check", "inspect"]},
    ],
    "api-design": [
        {"id": "idempotency", "description": "Handles idempotent retries for payment attempts.", "keywords": ["idempotency", "idempotent", "retry"]},
        {"id": "compatibility", "description": "Names versioning and backward compatibility.", "keywords": ["version", "backward", "compatibility"]},
        {"id": "error_contract", "description": "Defines durable error and pagination contracts.", "keywords": ["error", "pagination", "schema"]},
    ],
    "migration-without-data-loss": [
        {"id": "expand_contract", "description": "Uses expand-and-contract rather than destructive ALTER.", "keywords": ["expand", "contract", "dual", "backfill"]},
        {"id": "dirty_data", "description": "Handles invalid, unknown, empty, and null birthdate values.", "keywords": ["invalid", "unknown", "empty", "null", "quarantine"]},
        {"id": "rollback", "description": "Keeps rollback and validation before cleanup.", "keywords": ["rollback", "validation", "parity", "cleanup"]},
    ],
    "test-generation": [
        {"id": "observable_behavior", "description": "Tests public behavior rather than implementation details.", "keywords": ["observable", "behavior", "public", "implementation"]},
        {"id": "boundary_cases", "description": "Covers boundary seats, coupons, and invalid input.", "keywords": ["boundary", "coupon", "negative", "invalid", "seat"]},
        {"id": "rounding", "description": "Protects currency rounding to cents.", "keywords": ["round", "cent", "currency"]},
    ],
    "performance-tuning": [
        {"id": "measure_first", "description": "Requires profiling or tracing before optimizing.", "keywords": ["profile", "trace", "measure", "benchmark"]},
        {"id": "database_path", "description": "Considers N+1/query-count and database bottlenecks.", "keywords": ["n+1", "query", "database", "sql", "postgres"]},
        {"id": "rollback_budget", "description": "Names success metric and rollback or regression criteria.", "keywords": ["rollback", "regression", "latency", "budget"]},
    ],
}


def fixture_context(slug: str) -> str:
    context_path = ROOT / "examples" / "evaluations" / "fixtures" / slug / "context.md"
    if context_path.exists():
        return context_path.read_text(encoding="utf-8").strip()
    return EVALUATION_CONTEXTS[slug]


def build_prompt(slug: str, variant: str) -> str:
    case = PROOF_CASES[slug]
    request = case["weak"] if variant == "weak" else case["repaired"]
    return f"""You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
{fixture_context(slug)}

USER REQUEST:
{request}
"""


def run_codex(prompt: str) -> str:
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [
                "/Applications/Codex.app/Contents/Resources/codex",
                "exec",
                "--ephemeral",
                "--ignore-rules",
                "-s",
                "read-only",
                "-o",
                str(out_path),
                prompt,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
        return out_path.read_text(encoding="utf-8").strip()
    finally:
        out_path.unlink(missing_ok=True)


def score_output(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for criterion, keywords in CRITERION_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword in lowered)
        scores[criterion] = 2 if hits >= 2 else 1 if hits == 1 else 0
    return scores


def score_outcome(slug: str, text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for item in OUTCOME_RUBRICS[slug]:
        scores[item["id"]] = 1 if any(keyword in lowered for keyword in item["keywords"]) else 0
    return scores


def observed_delta(runs: list[dict]) -> str:
    weak = [run["structural_total"] for run in runs if run["variant"] == "weak"]
    repaired = [run["structural_total"] for run in runs if run["variant"] == "repaired"]
    if not weak or not repaired:
        return "pending"
    weak_avg = sum(weak) / len(weak)
    repaired_avg = sum(repaired) / len(repaired)
    delta = repaired_avg - weak_avg
    if delta > 0:
        return f"repaired prompts scored {delta:.1f} points higher on average"
    if delta < 0:
        return f"weak prompts scored {-delta:.1f} points higher on average"
    return "weak and repaired prompts tied on the structural rubric"


def observed_outcome_delta(runs: list[dict]) -> str:
    weak = [run["outcome_total"] for run in runs if run["variant"] == "weak"]
    repaired = [run["outcome_total"] for run in runs if run["variant"] == "repaired"]
    if not weak or not repaired:
        return "pending"
    weak_avg = sum(weak) / len(weak)
    repaired_avg = sum(repaired) / len(repaired)
    delta = repaired_avg - weak_avg
    if delta > 0:
        return f"repaired prompts satisfied {delta:.1f} more outcome checks on average"
    if delta < 0:
        return f"weak prompts satisfied {-delta:.1f} more outcome checks on average"
    return "weak and repaired prompts tied on outcome checks"


def run_surface(kind: str, prompt: str) -> str:
    if kind == "codex":
        return run_codex(prompt)
    raise ValueError(kind)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=sorted(SURFACES), action="append", help="surface to run; repeatable")
    parser.add_argument("--case", choices=sorted(PROOF_CASES), action="append", help="case to run; repeatable")
    parser.add_argument("--repetitions", type=int, default=1, help="number of runs per variant")
    args = parser.parse_args()

    surfaces = args.surface or list(SURFACES)
    slugs = args.case or list(PROOF_CASES)
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "surfaces": {name: SURFACES[name] for name in surfaces},
        "structural_rubric": CRITERION_KEYWORDS,
        "outcome_rubric": OUTCOME_RUBRICS,
        "cases": {},
    }

    for slug in slugs:
        case_runs = []
        for surface in surfaces:
            for repetition in range(1, args.repetitions + 1):
                for variant in ["weak", "repaired"]:
                    prompt = build_prompt(slug, variant)
                    run_dir = ROOT / "examples" / "evaluations" / "runs" / surface / slug
                    run_dir.mkdir(parents=True, exist_ok=True)
                    prefix = f"r{repetition:02d}-{variant}"
                    prompt_path = run_dir / f"{prefix}-prompt.md"
                    transcript_path = run_dir / f"{prefix}-output.md"
                    prompt_path.write_text(prompt, encoding="utf-8")
                    print(f"Running {surface} {slug} {variant} repetition {repetition}...")
                    output = run_surface(SURFACES[surface]["kind"], prompt)
                    run_timestamp = datetime.now(timezone.utc).isoformat()
                    transcript_path.write_text(output.rstrip() + "\n", encoding="utf-8")
                    structural_scores = score_output(output)
                    outcome_scores = score_outcome(slug, output)
                    case_runs.append(
                        {
                            "surface": surface,
                            "surface_label": SURFACES[surface]["label"],
                            "variant": variant,
                            "repetition": repetition,
                            "run_timestamp": run_timestamp,
                            "fixture_path": f"examples/evaluations/fixtures/{slug}",
                            "prompt_path": str(prompt_path.relative_to(ROOT)),
                            "transcript_path": str(transcript_path.relative_to(ROOT)),
                            "output": output.rstrip(),
                            "scores": structural_scores,
                            "structural_scores": structural_scores,
                            "structural_total": sum(structural_scores.values()),
                            "outcome_scores": outcome_scores,
                            "outcome_total": sum(outcome_scores.values()),
                            "total_score": sum(structural_scores.values()),
                            "evaluator_notes": "Auto-scored with outcome checks and a secondary structural rubric; transcript remains the primary evidence.",
                        }
                    )
        results["cases"][slug] = {
            "title": PROOF_CASES[slug]["title"],
            "input_context": fixture_context(slug),
            "fixture_path": f"examples/evaluations/fixtures/{slug}",
            "expected_delta": PROOF_CASES[slug]["delta"],
            "observed_delta": observed_delta(case_runs),
            "observed_outcome_delta": observed_outcome_delta(case_runs),
            "runs": case_runs,
        }

    out = ROOT / "examples" / "evaluations" / "results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
