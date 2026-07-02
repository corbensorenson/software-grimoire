#!/usr/bin/env python3
"""Run Proof by Difference evaluations against configured model/tool surfaces."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from bootstrap_project import EVALUATION_CONTEXTS, PROOF_CASES, ROOT
from surface_adapters import enrich_run_metadata, runnable_surfaces, run_surface, surface_for_result


SURFACES = {surface_id: surface_for_result(surface_id) for surface_id in runnable_surfaces()}

REVIEWABILITY_RUBRIC = {
    "artifact_boundary": ["artifact", "module", "file", "endpoint", "table", "boundary", "scope", "function"],
    "invariants": ["invariant", "preserve", "must not", "unchanged", "compatibility", "correctness"],
    "output_contract": ["return", "section", "table", "plan", "format", "output", "checklist"],
    "verification": ["verify", "test", "measure", "check", "query", "evidence", "benchmark", "validate"],
    "failure_behavior": ["if", "fallback", "rollback", "insufficient", "unsafe", "risk", "cannot"],
    "assumption_control": ["assumption", "hypothesis", "unknown", "missing", "evidence", "uncertain", "insufficient"],
}
CRITERION_KEYWORDS = REVIEWABILITY_RUBRIC

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


def fixture_context(slug: str, tier: str) -> str:
    fixture_slug = slug if tier == "clean" else f"{slug}-trap"
    context_path = ROOT / "examples" / "evaluations" / "fixtures" / fixture_slug / "context.md"
    if context_path.exists():
        return context_path.read_text(encoding="utf-8").strip()
    if tier != "clean":
        raise FileNotFoundError(f"missing trap fixture context: {context_path}")
    return EVALUATION_CONTEXTS[slug]


def build_prompt(slug: str, variant: str, tier: str) -> str:
    case = PROOF_CASES[slug]
    request = case["weak"] if variant == "weak" else case["repaired"]
    tier_note = "clean longitudinal fixture" if tier == "clean" else "trap-tier fixture with planted failure mode"
    return f"""You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
{tier_note}

TASK CONTEXT:
{fixture_context(slug, tier)}

USER REQUEST:
{request}
"""


def score_reviewability(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for criterion, keywords in REVIEWABILITY_RUBRIC.items():
        hits = sum(1 for keyword in keywords if keyword in lowered)
        scores[criterion] = 2 if hits >= 2 else 1 if hits == 1 else 0
    return scores


def score_outcome(slug: str, text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for item in OUTCOME_RUBRICS[slug]:
        scores[item["id"]] = 1 if any(keyword in lowered for keyword in item["keywords"]) else 0
    return scores


def reviewability_total(run: dict) -> int:
    return run.get("reviewability_total", run.get("structural_total", run.get("total_score", 0)))


def observed_reviewability_delta(runs: list[dict]) -> str:
    weak = [reviewability_total(run) for run in runs if run["variant"] == "weak"]
    repaired = [reviewability_total(run) for run in runs if run["variant"] == "repaired"]
    if not weak or not repaired:
        return "pending"
    weak_avg = sum(weak) / len(weak)
    repaired_avg = sum(repaired) / len(repaired)
    delta = repaired_avg - weak_avg
    if delta > 0:
        return f"repaired prompts scored {delta:.1f} reviewability points higher on average"
    if delta < 0:
        return f"weak prompts scored {-delta:.1f} reviewability points higher on average"
    return "weak and repaired prompts tied on the reviewability score"


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


def default_results(surfaces: list[str]) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "surfaces": {name: SURFACES[name] for name in surfaces},
        "reviewability_rubric": REVIEWABILITY_RUBRIC,
        "structural_rubric": REVIEWABILITY_RUBRIC,
        "outcome_rubric": OUTCOME_RUBRICS,
        "cases": {},
    }


def load_existing_results() -> dict | None:
    path = ROOT / "examples" / "evaluations" / "results.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_path_for(slug: str, tier: str) -> str:
    fixture_slug = slug if tier == "clean" else f"{slug}-trap"
    return f"examples/evaluations/fixtures/{fixture_slug}"


def next_repetition(existing_runs: list[dict], surface: str, tier: str, variant: str, requested_repetition: int, append: bool) -> int:
    if not append:
        return requested_repetition
    prior = [
        run.get("repetition", 0)
        for run in existing_runs
        if run.get("surface") == surface and run.get("tier", "clean") == tier and run.get("variant") == variant
    ]
    return (max(prior) if prior else 0) + 1


def recompute_case_summary(results: dict) -> None:
    for slug, case in results["cases"].items():
        runs = case.get("runs", [])
        case["observed_reviewability_delta"] = observed_reviewability_delta(runs)
        case["observed_delta"] = case["observed_reviewability_delta"]
        case["observed_outcome_delta"] = observed_outcome_delta(runs)
        delta_summaries = []
        tier_summaries = {}
        for tier in sorted({run.get("tier", "clean") for run in runs}):
            tier_runs = [run for run in runs if run.get("tier", "clean") == tier]
            tier_summaries[tier] = {
                "observed_reviewability_delta": observed_reviewability_delta(tier_runs),
                "observed_delta": observed_reviewability_delta(tier_runs),
                "observed_outcome_delta": observed_outcome_delta(tier_runs),
                "runs": len(tier_runs),
            }
        for surface in sorted({run.get("surface", "unknown") for run in runs}):
            for tier in sorted({run.get("tier", "clean") for run in runs if run.get("surface", "unknown") == surface}):
                cell_runs = [
                    run
                    for run in runs
                    if run.get("surface", "unknown") == surface and run.get("tier", "clean") == tier
                ]
                weak = [run for run in cell_runs if run.get("variant") == "weak"]
                repaired = [run for run in cell_runs if run.get("variant") == "repaired"]
                def avg(items: list[dict], key: str):
                    values = [
                        reviewability_total(item) if key == "reviewability" else item.get("outcome_total")
                        for item in items
                    ]
                    values = [value for value in values if value is not None]
                    return sum(values) / len(values) if values else None

                weak_review = avg(weak, "reviewability")
                repaired_review = avg(repaired, "reviewability")
                weak_outcome = avg(weak, "outcome")
                repaired_outcome = avg(repaired, "outcome")
                delta_summaries.append(
                    {
                        "surface": surface,
                        "tier": tier,
                        "weak_runs": len(weak),
                        "repaired_runs": len(repaired),
                        "weak_reviewability_avg": weak_review,
                        "repaired_reviewability_avg": repaired_review,
                        "reviewability_delta": None if weak_review is None or repaired_review is None else repaired_review - weak_review,
                        "weak_outcome_avg": weak_outcome,
                        "repaired_outcome_avg": repaired_outcome,
                        "outcome_delta": None if weak_outcome is None or repaired_outcome is None else repaired_outcome - weak_outcome,
                    }
                )
        case["tier_summaries"] = tier_summaries
        case["delta_summaries"] = delta_summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=sorted(SURFACES), action="append", help="surface to run; repeatable")
    parser.add_argument("--case", choices=sorted(PROOF_CASES), action="append", help="case to run; repeatable")
    parser.add_argument("--tier", choices=["clean", "trap"], action="append", help="tier to run; repeatable")
    parser.add_argument("--repetitions", type=int, default=1, help="number of runs per variant")
    parser.add_argument("--append", action="store_true", help="append to existing results instead of replacing them")
    args = parser.parse_args()

    surfaces = args.surface or list(SURFACES)
    slugs = args.case or list(PROOF_CASES)
    tiers = args.tier or ["clean"]
    results = load_existing_results() if args.append and load_existing_results() else default_results(surfaces)
    results["generated_at"] = datetime.now(timezone.utc).isoformat()
    results.setdefault("reviewability_rubric", REVIEWABILITY_RUBRIC)
    results.setdefault("structural_rubric", REVIEWABILITY_RUBRIC)
    results.setdefault("outcome_rubric", OUTCOME_RUBRICS)
    results.setdefault("cases", {})
    results.setdefault("surfaces", {})
    for surface in surfaces:
        results["surfaces"][surface] = SURFACES[surface]

    for slug in slugs:
        existing_case = results["cases"].setdefault(
            slug,
            {
                "title": PROOF_CASES[slug]["title"],
                "input_context": fixture_context(slug, "clean"),
                "fixture_path": fixture_path_for(slug, "clean"),
                "expected_delta": PROOF_CASES[slug]["delta"],
                "observed_delta": "pending",
                "observed_outcome_delta": "pending",
                "runs": [],
            },
        )
        if not args.append:
            existing_case["runs"] = [
                run
                for run in existing_case.get("runs", [])
                if run.get("surface") not in surfaces or run.get("tier", "clean") not in tiers
            ]
        for surface in surfaces:
            for tier in tiers:
                for repetition in range(1, args.repetitions + 1):
                    for variant in ["weak", "repaired"]:
                        run_repetition = next_repetition(existing_case["runs"], surface, tier, variant, repetition, args.append)
                        prompt = build_prompt(slug, variant, tier)
                        run_dir = ROOT / "examples" / "evaluations" / "runs" / surface / slug / tier
                        run_dir.mkdir(parents=True, exist_ok=True)
                        prefix = f"r{run_repetition:02d}-{variant}"
                        prompt_path = run_dir / f"{prefix}-prompt.md"
                        transcript_path = run_dir / f"{prefix}-output.md"
                        prompt_path.write_text(prompt, encoding="utf-8")
                        print(f"Running {surface} {slug} {tier} {variant} repetition {run_repetition}...")
                        output = run_surface(surface, prompt)
                        run_timestamp = datetime.now(timezone.utc).isoformat()
                        transcript_path.write_text(output.rstrip() + "\n", encoding="utf-8")
                        reviewability_scores = score_reviewability(output)
                        outcome_scores = score_outcome(slug, output)
                        metadata = enrich_run_metadata(surface)
                        existing_case["runs"].append(
                            {
                                **metadata,
                                "surface_label": SURFACES[surface]["label"],
                                "tier": tier,
                                "variant": variant,
                                "repetition": run_repetition,
                                "run_timestamp": run_timestamp,
                                "fixture_path": fixture_path_for(slug, tier),
                                "fixture_version": "v2.2-clean-and-trap-fixtures",
                                "prompt_path": str(prompt_path.relative_to(ROOT)),
                                "transcript_path": str(transcript_path.relative_to(ROOT)),
                                "output": output.rstrip(),
                                "scores": reviewability_scores,
                                "reviewability_scores": reviewability_scores,
                                "reviewability_total": sum(reviewability_scores.values()),
                                "structural_scores": reviewability_scores,
                                "structural_total": sum(reviewability_scores.values()),
                                "outcome_scores": outcome_scores,
                                "outcome_total": sum(outcome_scores.values()),
                                "total_score": sum(reviewability_scores.values()),
                                "evaluator_notes": "Auto-scored with outcome checks and a secondary reviewability rubric; transcript remains the primary evidence.",
                            }
                        )

    recompute_case_summary(results)
    out = ROOT / "examples" / "evaluations" / "results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
