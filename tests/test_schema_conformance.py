#!/usr/bin/env python3
"""Validate generated JSON data against repository schemas."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def collect_errors(schema_path: str, items: list[dict], label: str) -> list[str]:
    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for index, item in enumerate(items):
        for error in sorted(validator.iter_errors(item), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{label}[{index}].{location}: {error.message}")
    return errors


def test_houses_match_schema() -> None:
    errors = collect_errors("schemas/house.schema.json", load_json("data/houses.json"), "house")
    assert not errors, "\n".join(errors[:25])


def test_lexicon_entries_match_schema() -> None:
    errors = collect_errors("schemas/lexicon-entry.schema.json", load_json("data/lexicon.json"), "lexicon")
    assert not errors, "\n".join(errors[:25])


def test_spells_match_schema() -> None:
    errors = collect_errors("schemas/spell.schema.json", load_json("data/spells.json"), "spell")
    assert not errors, "\n".join(errors[:25])


def test_stacks_match_schema() -> None:
    errors = collect_errors("schemas/stack.schema.json", load_json("data/stacks.json"), "stack")
    assert not errors, "\n".join(errors[:25])


def test_seals_match_schema() -> None:
    seals = load_json("data/seals.json")
    items = seals["spells"] + seals["stacks"]
    errors = collect_errors("schemas/seal.schema.json", items, "seal")
    assert not errors, "\n".join(errors[:25])


def test_canon_quality_matches_schema() -> None:
    errors = collect_errors("schemas/canon-quality.schema.json", [load_json("data/canon_quality.json")], "canon_quality")
    assert not errors, "\n".join(errors[:25])


def test_jailbreak_cases_match_schema() -> None:
    data = load_json("data/jailbreak_resilience.json")
    errors = collect_errors("schemas/jailbreak-case.schema.json", list(data["cases"].values()), "jailbreak_case")
    assert not errors, "\n".join(errors[:25])


def test_bench_v2_matches_schema() -> None:
    errors = collect_errors("schemas/bench-v2.schema.json", [load_json("data/bench_v2.json")], "bench_v2")
    assert not errors, "\n".join(errors[:25])


def test_execution_bench_matches_schema() -> None:
    errors = collect_errors("schemas/execution-bench.schema.json", [load_json("data/execution_bench.json")], "execution_bench")
    assert not errors, "\n".join(errors[:25])


def test_surface_comparison_matches_schema() -> None:
    errors = collect_errors("schemas/surface-comparison.schema.json", [load_json("examples/evaluations/surface-comparison.json")], "surface_comparison")
    assert not errors, "\n".join(errors[:25])


def test_warded_baseline_matches_schema() -> None:
    errors = collect_errors("schemas/warded-baseline.schema.json", [load_json("examples/jailbreak-resilience/baseline-results.json")], "warded_baseline")
    assert not errors, "\n".join(errors[:25])


def test_ward_science_matches_schema() -> None:
    errors = collect_errors("schemas/ward-science.schema.json", [load_json("examples/jailbreak-resilience/ward-science-results.json")], "ward_science")
    assert not errors, "\n".join(errors[:25])


def test_semantic_promotion_matches_schema() -> None:
    errors = collect_errors("schemas/semantic-promotion.schema.json", [load_json("data/semantic_promotion.json")], "semantic_promotion")
    assert not errors, "\n".join(errors[:25])


def test_adversarial_harness_matches_schema() -> None:
    errors = collect_errors("schemas/adversarial-harness.schema.json", [load_json("data/adversarial_harness.json")], "adversarial_harness")
    assert not errors, "\n".join(errors[:25])


def test_library_manifest_matches_schema() -> None:
    errors = collect_errors("schemas/library-manifest.schema.json", [load_json("exports/library-manifest.json")], "library_manifest")
    assert not errors, "\n".join(errors[:25])


def test_generator_architecture_matches_schema() -> None:
    errors = collect_errors("schemas/generator-architecture.schema.json", [load_json("data/generator_architecture.json")], "generator_architecture")
    assert not errors, "\n".join(errors[:25])


def test_visual_practice_matches_schema() -> None:
    errors = collect_errors("schemas/visual-practice.schema.json", [load_json("data/visual_practice.json")], "visual_practice")
    assert not errors, "\n".join(errors[:25])


def test_adoption_evidence_matches_schema() -> None:
    errors = collect_errors("schemas/adoption-evidence.schema.json", [load_json("data/adoption_evidence.json")], "adoption_evidence")
    assert not errors, "\n".join(errors[:25])


def test_adoption_report_template_matches_schema() -> None:
    errors = collect_errors("schemas/adoption-report.schema.json", [load_json("examples/adoption/adoption-report-template.json")], "adoption_report")
    assert not errors, "\n".join(errors[:25])


def test_package_index_release_plan_matches_schema() -> None:
    errors = collect_errors("schemas/package-index-release-plan.schema.json", [load_json("examples/adoption/package-index-release-plan.json")], "package_index_release")
    assert not errors, "\n".join(errors[:25])


def test_evidence_taxonomy_matches_schema() -> None:
    errors = collect_errors("schemas/evidence-taxonomy.schema.json", [load_json("data/evidence_taxonomy.json")], "evidence_taxonomy")
    assert not errors, "\n".join(errors[:25])


def test_evidence_index_matches_schema() -> None:
    errors = collect_errors("schemas/evidence-index.schema.json", [load_json("data/evidence_index.json")], "evidence_index")
    assert not errors, "\n".join(errors[:25])


def test_canon_audit_matches_schema() -> None:
    errors = collect_errors("schemas/canon-audit.schema.json", [load_json("data/canon_audit.json")], "canon_audit")
    assert not errors, "\n".join(errors[:25])


def test_rune_usage_graph_matches_schema() -> None:
    errors = collect_errors("schemas/rune-usage-graph.schema.json", [load_json("data/rune_usage_graph.json")], "rune_usage_graph")
    assert not errors, "\n".join(errors[:25])


def test_canon_review_queue_matches_schema() -> None:
    errors = collect_errors("schemas/canon-review-queue.schema.json", [load_json("data/canon_review_queue.json")], "canon_review_queue")
    assert not errors, "\n".join(errors[:25])


def test_model_execution_results_match_schema() -> None:
    errors = collect_errors("schemas/model-execution-results.schema.json", [load_json("examples/evaluations/model-execution-results.json")], "model_execution")
    assert not errors, "\n".join(errors[:25])


def test_hardness_v4_results_match_schema() -> None:
    errors = collect_errors("schemas/hardness-v4-results.schema.json", [load_json("examples/evaluations/hardness-v4/results.json")], "hardness_v4")
    assert not errors, "\n".join(errors[:25])


def test_hardness_v4_model_results_match_schema() -> None:
    errors = collect_errors(
        "schemas/hardness-v4-model-results.schema.json",
        [load_json("examples/evaluations/hardness-v4/model-surface-results.json")],
        "hardness_v4_model",
    )
    assert not errors, "\n".join(errors[:25])


def test_hardness_v4_manual_import_template_matches_schema() -> None:
    errors = collect_errors(
        "schemas/hardness-v4-import.schema.json",
        [load_json("examples/evaluations/hardness-v4/manual-import-template.json")],
        "hardness_v4_import",
    )
    assert not errors, "\n".join(errors[:25])


def test_warded_ab_matches_schema() -> None:
    errors = collect_errors("schemas/warded-ab.schema.json", [load_json("examples/jailbreak-resilience/ab-results.json")], "warded_ab")
    assert not errors, "\n".join(errors[:25])


def test_package_check_matches_schema() -> None:
    errors = collect_errors("schemas/package-check.schema.json", [load_json("examples/adoption/package-check.json")], "package_check")
    assert not errors, "\n".join(errors[:25])


def test_public_smoke_check_matches_schema() -> None:
    errors = collect_errors("schemas/public-smoke-check.schema.json", [load_json("examples/release-gate/public-smoke-check.json")], "public_smoke")
    assert not errors, "\n".join(errors[:25])
