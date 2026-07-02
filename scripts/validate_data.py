#!/usr/bin/env python3
"""Validate generated Software Grimoire data."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPLETION_STATUSES = {"authored", "stub", "needs_shadow", "needs_sense"}
SEMANTIC_STATUSES = {"generated_draft", "reviewed", "canonical", "deprecated"}
FORCE_SOURCES = {"major-canon", "pocket-canon", "master-lexicon"}
PROVENANCE_EVIDENCE_CLASS = {
    "project-owned": "project_owned_model_run",
    "reviewer-supplied": "reviewer_supplied_model_run",
    "external-user": "external_user_model_run",
}
EXPECTED_SPELL_COUNT = 7
EXPECTED_STACK_COUNT = 7
JAILBREAK_WARD_FIELDS = [
    "trust_boundary",
    "untrusted_inputs",
    "allowed_tools",
    "forbidden_outputs",
    "secret_handling",
    "refusal_contract",
    "audit_log",
]
GENERIC_LEXICON_PATTERNS = [
    "a shape-of-state word;",
    "an interface word;",
    "a release/tooling word;",
    "a verification word;",
    "a systems word;",
    "a network/distributed systems word;",
    "a security word;",
    "a failure word;",
    "a promptcraft word;",
    "a quality word;",
    "a hardware/performance word;",
]
GENERATED_TEMPLATE_RE = re.compile(r" rune for .*use it when the artifact needs", re.IGNORECASE)


def generated_template_text(value: str | None) -> bool:
    if not value:
        return False
    return bool(GENERATED_TEMPLATE_RE.search(value)) or value.strip().startswith("`")


def load(name: str):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_houses(errors: list[str]) -> list[dict]:
    houses = load("houses.json")
    seen = set()
    for house in houses:
        for key in ["id", "name", "start", "end", "range", "expected_count"]:
            if key not in house:
                fail(errors, f"House missing {key}: {house}")
        if house["id"] in seen:
            fail(errors, f"Duplicate house id: {house['id']}")
        seen.add(house["id"])
        expected = f"{house['start']:04d}-{house['end']:04d}"
        if house["range"] != expected:
            fail(errors, f"Bad range for {house['id']}: {house['range']} != {expected}")
        if house["expected_count"] != house["end"] - house["start"] + 1:
            fail(errors, f"Bad expected_count for {house['id']}")
    return houses


def validate_lexicon(errors: list[str], houses: list[dict]) -> list[dict]:
    lexicon = load("lexicon.json")
    house_by_id = {h["id"]: h for h in houses}
    ids = set()
    shadows = []
    for entry in lexicon:
        required = [
            "id",
            "sigil",
            "term",
            "raw_term",
            "house",
            "house_name",
            "anchor",
            "page",
            "summary",
            "force",
            "shadow",
            "status",
            "completion_status",
            "semantic_status",
            "is_stub",
            "major",
            "pocket",
            "source",
            "force_source",
            "prompt_uses",
            "examples",
        ]
        missing_required = False
        for key in required:
            if key not in entry or entry[key] in ("", None):
                fail(errors, f"Lexicon entry missing {key}: {entry.get('id')}")
                missing_required = True
        if missing_required:
            continue
        ident = entry["id"]
        if ident in ids:
            fail(errors, f"Duplicate lexicon id: {ident}")
        ids.add(ident)
        if entry["sigil"] != f"{ident:04d}":
            fail(errors, f"Bad sigil for lexicon id {ident}")
        if entry["anchor"] != f"rune-{ident:04d}":
            fail(errors, f"Bad anchor for lexicon id {ident}: {entry['anchor']}")
        if entry["page"] != f"reference/house-{entry['house']}.qmd":
            fail(errors, f"Bad page for lexicon id {ident}: {entry['page']}")
        if entry["completion_status"] not in COMPLETION_STATUSES:
            fail(errors, f"Bad completion_status for lexicon id {ident}: {entry['completion_status']}")
        if entry["semantic_status"] not in SEMANTIC_STATUSES:
            fail(errors, f"Bad semantic_status for lexicon id {ident}: {entry['semantic_status']}")
        if entry["completion_status"] != "authored":
            fail(errors, f"Lexicon entry is not fully authored: {ident} ({entry['completion_status']})")
        if entry["force_source"] not in FORCE_SOURCES:
            fail(errors, f"Bad force_source for lexicon id {ident}: {entry['force_source']}")
        if entry["is_stub"]:
            fail(errors, f"Lexicon entry still marked stub: {ident}")
        if not entry.get("shadow"):
            fail(errors, f"Authored lexicon entry missing shadow: {ident}")
        else:
            shadows.append(entry["shadow"])
        if entry.get("shadow", "").strip().lower().startswith("shadow:"):
            fail(errors, f"Lexicon entry has doubled shadow label: {ident}")
        summary_lower = entry.get("summary", "").strip().lower()
        force_lower = entry.get("force", "").strip().lower()
        for pattern in GENERIC_LEXICON_PATTERNS:
            if summary_lower.startswith(pattern) or force_lower.startswith(pattern):
                fail(errors, f"Lexicon entry retains generic boilerplate: {ident}")
        if entry["semantic_status"] in {"reviewed", "canonical"}:
            if generated_template_text(entry.get("summary")) or generated_template_text(entry.get("force")):
                fail(errors, f"Reviewed lexicon entry retains generated template language: {ident}")
            if not entry.get("prompt_uses"):
                fail(errors, f"Reviewed lexicon entry missing prompt_uses: {ident}")
            if not entry.get("examples"):
                fail(errors, f"Reviewed lexicon entry missing examples: {ident}")
        if entry.get("major") and entry["completion_status"] != "authored":
            fail(errors, f"Major canon entry is not authored: {ident}")
        if entry.get("pocket") and entry["completion_status"] != "authored":
            fail(errors, f"Pocket canon entry is not authored: {ident}")
        if entry.get("major") and entry["force_source"] != "major-canon":
            fail(errors, f"Major canon entry has wrong force_source: {ident}")
        if not entry.get("major") and entry.get("pocket") and entry["force_source"] != "pocket-canon":
            fail(errors, f"Pocket canon entry has wrong force_source: {ident}")
        house = house_by_id.get(entry["house"])
        if not house:
            fail(errors, f"Unknown house for lexicon id {ident}: {entry['house']}")
        elif not (house["start"] <= ident <= house["end"]):
            fail(errors, f"Lexicon id {ident} outside house range {house['range']}")
        elif entry["house_name"] != house["name"]:
            fail(errors, f"Bad house_name for lexicon id {ident}: {entry['house_name']}")
    if len(lexicon) != 1645:
        fail(errors, f"Expected 1645 lexicon entries, found {len(lexicon)}")
    if len(ids) != len(lexicon):
        fail(errors, "Lexicon ids are not unique")
    if len(shadows) != len(set(shadows)):
        fail(errors, "Lexicon shadows must be unique across the full canon")
    return lexicon


def validate_major_and_pocket(errors: list[str], lexicon: list[dict]) -> None:
    lex_by_id = {e["id"]: e for e in lexicon}
    lex_ids = set(lex_by_id)
    major = load("major_arcana.json")
    pocket = load("pocket_runes.json")
    if len(major) != 50:
        fail(errors, f"Expected 50 major canon entries, found {len(major)}")
    if len(pocket) != 300:
        fail(errors, f"Expected 300 pocket entries, found {len(pocket)}")
    for label, items in [("major", major), ("pocket", pocket)]:
        seen = set()
        shadows = []
        for item in items:
            ident = item.get("id")
            if ident in seen:
                fail(errors, f"Duplicate {label} id: {ident}")
            seen.add(ident)
            if ident not in lex_ids:
                fail(errors, f"{label} id missing from lexicon: {ident}")
            elif lex_by_id[ident]["completion_status"] != "authored":
                fail(errors, f"{label} id is not authored in lexicon: {ident}")
            elif label == "major":
                shadows.append(lex_by_id[ident].get("shadow"))
        if label == "major" and len(set(shadows)) != len(shadows):
            fail(errors, "Major canon shadows must be unique and term-specific")


def validate_canon_quality(errors: list[str], lexicon: list[dict]) -> None:
    path = ROOT / "data" / "canon_quality.json"
    if not path.exists():
        fail(errors, "Missing data/canon_quality.json")
        return
    report = json.loads(path.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    authored = sum(1 for entry in lexicon if entry.get("completion_status") == "authored")
    stub = sum(1 for entry in lexicon if entry.get("completion_status") == "stub")
    major = sum(1 for entry in lexicon if entry.get("major"))
    pocket = sum(1 for entry in lexicon if entry.get("pocket"))
    expected = {
        "total_entries": len(lexicon),
        "authored_entries": authored,
        "stub_entries": stub,
        "major_entries": major,
        "pocket_entries": pocket,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            fail(errors, f"Canon quality summary mismatch for {key}: {summary.get(key)} != {value}")
    authored_layer = report.get("authored_layer", {})
    semantic_layer = report.get("semantic_layer", {})
    if summary.get("authored_entries") != len(lexicon) or summary.get("stub_entries") != 0:
        fail(errors, "Canon quality report must show the full lexicon authored with zero stubs")
    reviewed = sum(1 for entry in lexicon if entry.get("semantic_status") in {"reviewed", "canonical"})
    generated_draft = sum(1 for entry in lexicon if entry.get("semantic_status") == "generated_draft")
    generated_template = sum(1 for entry in lexicon if generated_template_text(entry.get("summary")))
    if semantic_layer.get("reviewed_entries", 0) + semantic_layer.get("canonical_entries", 0) != reviewed:
        fail(errors, "Canon quality semantic reviewed/canonical count mismatch")
    if semantic_layer.get("generated_draft_entries") != generated_draft:
        fail(errors, "Canon quality generated_draft count mismatch")
    if semantic_layer.get("generated_template_summaries") != generated_template:
        fail(errors, "Canon quality generated-template summary count mismatch")
    if semantic_layer.get("reviewed_entries_with_prompt_uses") != reviewed:
        fail(errors, "Every reviewed/canonical entry must have prompt uses")
    if semantic_layer.get("reviewed_entries_with_examples") != reviewed:
        fail(errors, "Every reviewed/canonical entry must have examples")
    if authored_layer.get("doubled_shadow_labels") != 0:
        fail(errors, "Canon quality report found doubled shadow labels")
    major_canon = report.get("major_canon", {})
    if major_canon.get("entries_with_reviewed_shadow") != 50:
        fail(errors, "Canon quality report must show 50 reviewed major-canon shadows")


def validate_spells(errors: list[str], lexicon: list[dict]) -> list[dict]:
    spells = load("spells.json")
    lex_ids = {entry["id"] for entry in lexicon}
    required = [
        "id",
        "title",
        "version",
        "cast_level",
        "status",
        "use_when",
        "role",
        "objective",
        "context",
        "constraints",
        "procedure",
        "output_contract",
        "verification",
        "failure_behavior",
        "runes",
        "source",
        "human_title",
        "working_seal",
        "formal_sigil",
    ]
    ids = set()
    for spell in spells:
        missing_required = False
        for key in required:
            if key not in spell or spell[key] in ("", None):
                fail(errors, f"Spell {spell.get('id')} missing {key}")
                missing_required = True
        if missing_required:
            continue
        if spell["id"] in ids:
            fail(errors, f"Duplicate spell id: {spell['id']}")
        ids.add(spell["id"])
        if spell["cast_level"] == "full":
            for limb in ["role", "objective", "context", "constraints", "procedure", "output_contract", "verification", "failure_behavior"]:
                if not spell.get(limb):
                    fail(errors, f"Full spell {spell['id']} missing limb {limb}")
        if not re.match(r"^spell://[a-z0-9-]+/[A-F0-9]{10}$", spell.get("working_seal", "")):
            fail(errors, f"Bad spell seal: {spell.get('working_seal')}")
        if not spell.get("runes"):
            fail(errors, f"Spell {spell['id']} has no rune references")
        for ident in spell.get("runes", []):
            if ident not in lex_ids:
                fail(errors, f"Spell {spell['id']} references missing rune {ident}")
        if spell["id"] == "spell.jailbreak-resilience-review.v1":
            for key in JAILBREAK_WARD_FIELDS:
                if key not in spell or spell[key] in ("", None, [], {}):
                    fail(errors, f"Warded spell missing {key}")
            boundary = spell.get("trust_boundary", {})
            if not boundary.get("trusted") or not boundary.get("untrusted"):
                fail(errors, "Warded spell trust_boundary must include trusted and untrusted lists")
            refusal = spell.get("refusal_contract", {})
            if not refusal.get("refuse_when") or not refusal.get("preserve_utility"):
                fail(errors, "Warded spell refusal_contract must include refuse_when and preserve_utility")
    if len(spells) != EXPECTED_SPELL_COUNT:
        fail(errors, f"Expected {EXPECTED_SPELL_COUNT} spells, found {len(spells)}")
    return spells


def validate_stacks(errors: list[str], lexicon: list[dict], spells: list[dict]) -> list[dict]:
    stacks = load("stacks.json")
    lex_ids = {entry["id"] for entry in lexicon}
    spell_slugs = {spell["id"].split(".")[1] for spell in spells}
    ids = set()
    for stack in stacks:
        missing_required = False
        for key in [
            "id",
            "title",
            "version",
            "status",
            "enter",
            "inputs",
            "frames",
            "on_fail",
            "exit",
            "why_it_works",
            "source",
            "human_title",
            "working_seal",
            "formal_sigil",
            "runes",
            "related_spells",
        ]:
            if key not in stack or stack[key] in ("", None, []):
                fail(errors, f"Stack {stack.get('id')} missing {key}")
                missing_required = True
        if missing_required:
            continue
        if stack["id"] in ids:
            fail(errors, f"Duplicate stack id: {stack['id']}")
        ids.add(stack["id"])
        for frame in stack["frames"]:
            for key in ["step", "spell", "artifact", "advance_when"]:
                if key not in frame or frame[key] in ("", None):
                    fail(errors, f"Stack frame missing {key}: {stack['id']} step {frame.get('step')}")
        loop = stack.get("loop")
        if loop:
            if loop.get("recursive") and not loop.get("base_case"):
                fail(errors, f"Recursive stack missing base case: {stack['id']}")
            if not loop.get("recursive") and not loop.get("until"):
                fail(errors, f"Loop stack missing until rule: {stack['id']}")
        if not re.match(r"^stack://[a-z0-9-]+/[A-F0-9]{10}$", stack.get("working_seal", "")):
            fail(errors, f"Bad stack seal: {stack.get('working_seal')}")
        if not stack.get("runes"):
            fail(errors, f"Stack {stack['id']} has no rune references")
        if not stack.get("related_spells"):
            fail(errors, f"Stack {stack['id']} has no related spell references")
        for ident in stack.get("runes", []):
            if ident not in lex_ids:
                fail(errors, f"Stack {stack['id']} references missing rune {ident}")
        for slug in stack.get("related_spells", []):
            if slug not in spell_slugs:
                fail(errors, f"Stack {stack['id']} references missing spell slug {slug}")
    if len(stacks) != EXPECTED_STACK_COUNT:
        fail(errors, f"Expected {EXPECTED_STACK_COUNT} stacks, found {len(stacks)}")
    return stacks


def validate_jailbreak_resilience(errors: list[str]) -> None:
    path = ROOT / "data" / "jailbreak_resilience.json"
    if not path.exists():
        fail(errors, "Missing data/jailbreak_resilience.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("payload_policy") != "defanged-fixtures-only":
        fail(errors, "Jailbreak resilience payload_policy must be defanged-fixtures-only")
    if len(data.get("sources", [])) < 8:
        fail(errors, "Jailbreak resilience source map is too small")
    axes = data.get("scoring_axes", {})
    for axis in ["attack_resistance", "utility_preservation", "audit_quality"]:
        if not axes.get(axis):
            fail(errors, f"Missing jailbreak scoring axis: {axis}")
    cases = data.get("cases", {})
    if len(cases) != 8:
        fail(errors, f"Expected 8 jailbreak-resilience cases, found {len(cases)}")
    for slug, case in cases.items():
        for key in [
            "title",
            "attack_shape",
            "fixture_path",
            "benign_task",
            "expected_behavior",
            "utility_keywords",
            "resistance_keywords",
            "audit_keywords",
            "forbidden_strings",
            "forbidden_tools",
        ]:
            if key not in case or case[key] in ("", None, []):
                if key == "forbidden_tools" and case.get(key) == []:
                    continue
                fail(errors, f"Jailbreak case {slug} missing {key}")
        fixture_dir = ROOT / case.get("fixture_path", "")
        if not fixture_dir.is_dir():
            fail(errors, f"Missing jailbreak fixture directory: {slug}")
            continue
        for fixture_file in ["context.md", "ground_truth.json"]:
            if not (fixture_dir / fixture_file).exists():
                fail(errors, f"Jailbreak fixture {slug} missing {fixture_file}")
        ground_truth_path = fixture_dir / "ground_truth.json"
        if ground_truth_path.exists():
            ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
            if ground_truth.get("attack_shape") != case.get("attack_shape"):
                fail(errors, f"Jailbreak fixture {slug} attack_shape mismatch")
            if ground_truth.get("payload_policy") != "defanged":
                fail(errors, f"Jailbreak fixture {slug} must be defanged")


def validate_bench_v2(errors: list[str]) -> None:
    path = ROOT / "data" / "bench_v2.json"
    if not path.exists():
        fail(errors, "Missing data/bench_v2.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    surfaces = data.get("surfaces", {})
    if "codex-cli-default" not in surfaces:
        fail(errors, "Bench v2 must declare codex-cli-default surface")
    if "manual-reviewer-import" not in surfaces:
        fail(errors, "Bench v2 must declare manual-reviewer-import surface")
    required = set(data.get("manual_import_contract", {}).get("required_fields", []))
    for field in ["surface_id", "benchmark", "case_slug", "prompt_path", "transcript_path", "provenance"]:
        if field not in required:
            fail(errors, f"Bench v2 manual import contract missing {field}")
    checks = data.get("deterministic_checks", {})
    for slug in [
        "safe-refactoring",
        "bug-diagnosis-from-logs",
        "api-design",
        "migration-without-data-loss",
        "test-generation",
        "performance-tuning",
    ]:
        if slug not in checks:
            fail(errors, f"Bench v2 missing deterministic check for {slug}")
    safe = checks.get("safe-refactoring", {})
    if safe.get("kind") != "executable-fixture" or "pytest" not in safe.get("command", ""):
        fail(errors, "Bench v2 safe-refactoring check must be executable pytest fixture")
    for surface in ["claude-code-safe", "local-deterministic-grader", "local-unwarded-control", "local-warded-reviewer"]:
        if surface not in surfaces:
            fail(errors, f"Bench v2 must declare {surface} surface")


def validate_execution_bench(errors: list[str]) -> None:
    path = ROOT / "data" / "execution_bench.json"
    results_path = ROOT / "examples" / "evaluations" / "execution-results.json"
    if not path.exists():
        fail(errors, "Missing data/execution_bench.json")
        return
    if not results_path.exists():
        fail(errors, "Missing examples/evaluations/execution-results.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    results = json.loads(results_path.read_text(encoding="utf-8"))
    expected_cases = {
        "safe-refactoring",
        "bug-diagnosis-from-logs",
        "api-design",
        "migration-without-data-loss",
        "test-generation",
        "performance-tuning",
    }
    if set(data.get("cases", {})) != expected_cases:
        fail(errors, "Execution bench must include all six field-spell cases")
    if set(results.get("cases", {})) != expected_cases:
        fail(errors, "Execution results must include all six field-spell cases")
    if "local-deterministic-grader" not in results.get("surfaces", {}):
        fail(errors, "Execution results must declare local-deterministic-grader")
    for slug, tiers in data.get("cases", {}).items():
        for tier in ["clean", "trap"]:
            fixture = ROOT / tiers.get(tier, {}).get("fixture_path", "")
            if not fixture.exists():
                fail(errors, f"Execution bench fixture missing: {slug} {tier}")
        trap = tiers.get("trap", {})
        if not trap.get("trap") or not trap.get("expected_failure"):
            fail(errors, f"Execution bench trap missing failure description: {slug}")
    safe_runs = {
        (run["tier"], run["variant"]): run
        for run in results.get("cases", {}).get("safe-refactoring", {}).get("runs", [])
    }
    for tier in ["clean", "trap"]:
        weak = safe_runs.get((tier, "weak"))
        repaired = safe_runs.get((tier, "repaired"))
        if not weak or not repaired:
            fail(errors, f"Safe-refactoring execution missing {tier} weak/repaired pair")
            continue
        if weak.get("execution_result", {}).get("passed") is not False:
            fail(errors, f"Safe-refactoring {tier} weak artifact must fail execution")
        if repaired.get("execution_result", {}).get("passed") is not True:
            fail(errors, f"Safe-refactoring {tier} repaired artifact must pass execution")
        for run in [weak, repaired]:
            artifact = run.get("artifact_path")
            if artifact and not (ROOT / artifact).exists():
                fail(errors, f"Execution artifact missing: {artifact}")


def validate_surface_comparison(errors: list[str]) -> None:
    path = ROOT / "examples" / "evaluations" / "surface-comparison.json"
    if not path.exists():
        fail(errors, "Missing examples/evaluations/surface-comparison.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    surfaces = data.get("surfaces", {})
    for surface in ["codex-cli-default", "local-deterministic-grader"]:
        if surface not in surfaces:
            fail(errors, f"Surface comparison missing {surface}")
    for slug, item in data.get("field_spell_matrix", {}).items():
        surface_items = item.get("surfaces", {})
        if "codex-cli-default" not in surface_items or "local-deterministic-grader" not in surface_items:
            fail(errors, f"Surface comparison case missing required surfaces: {slug}")
        limitation = surface_items.get("local-deterministic-grader", {}).get("limitation", "")
        if "not independent model evidence" not in limitation:
            fail(errors, f"Local deterministic grader limitation must be explicit: {slug}")


def validate_jailbreak_baselines(errors: list[str]) -> None:
    path = ROOT / "examples" / "jailbreak-resilience" / "baseline-results.json"
    if not path.exists():
        fail(errors, "Missing examples/jailbreak-resilience/baseline-results.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("payload_policy") != "defanged-fixtures-only":
        fail(errors, "Warded baseline payload policy must be defanged-fixtures-only")
    if not data.get("baseline_failures"):
        fail(errors, "Warded baseline matrix must preserve at least one baseline failure")
    for slug, case in data.get("cases", {}).items():
        variants = {run.get("variant") for run in case.get("runs", [])}
        if variants != {"baseline", "warded"}:
            fail(errors, f"Warded baseline case must include baseline and warded variants: {slug}")
        for run in case.get("runs", []):
            for key in ["fixture_path", "prompt_path", "transcript_path"]:
                value = run.get(key)
                if value and not (ROOT / value).exists():
                    fail(errors, f"Warded baseline {key} missing: {value}")
            if run.get("total_score") != sum(run.get("axis_totals", {}).values()):
                fail(errors, f"Warded baseline total score mismatch: {slug} {run.get('variant')}")
            output = run.get("output", "").lower()
            if "rm -rf" in output or "curl https://attacker.example" in output:
                fail(errors, f"Warded baseline output contains forbidden operational string: {slug} {run.get('variant')}")


def validate_semantic_promotion(errors: list[str], lexicon: list[dict], houses: list[dict]) -> None:
    path = ROOT / "data" / "semantic_promotion.json"
    if not path.exists():
        fail(errors, "Missing data/semantic_promotion.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    reviewed = sum(1 for entry in lexicon if entry.get("semantic_status") in {"reviewed", "canonical"})
    drafts = sum(1 for entry in lexicon if entry.get("semantic_status") == "generated_draft")
    if summary.get("total_entries") != len(lexicon):
        fail(errors, "Semantic promotion total_entries mismatch")
    if summary.get("reviewed_or_canonical_entries") != reviewed:
        fail(errors, "Semantic promotion reviewed/canonical count mismatch")
    if summary.get("generated_draft_entries") != drafts:
        fail(errors, "Semantic promotion generated_draft count mismatch")
    if reviewed < summary.get("target_reviewed_entries", 450):
        fail(errors, "Semantic promotion reviewed/canonical count is below target")
    house_rows = {item.get("house"): item for item in data.get("houses", [])}
    if set(house_rows) != {house["id"] for house in houses}:
        fail(errors, "Semantic promotion must include every house")
    for house in houses[:2]:
        item = house_rows.get(house["id"], {})
        if item.get("fully_reviewed") is not True:
            fail(errors, f"Semantic promotion first-pass house is not fully reviewed: {house['id']}")
        if item.get("generated_draft_entries") != 0:
            fail(errors, f"Semantic promotion reviewed house still has drafts: {house['id']}")


def validate_adversarial_harness(errors: list[str]) -> None:
    path = ROOT / "data" / "adversarial_harness.json"
    if not path.exists():
        fail(errors, "Missing data/adversarial_harness.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("payload_policy") != "defanged-fixtures-only":
        fail(errors, "Adversarial harness payload_policy must be defanged-fixtures-only")
    if data.get("execution_policy") != "local-read-only":
        fail(errors, "Adversarial harness execution_policy must be local-read-only")
    required = {"tool-mediator", "retrieval-taint", "multi-turn-state", "long-context-drift", "redaction", "overrefusal"}
    harnesses = data.get("harnesses", {})
    missing = required - set(harnesses)
    if missing:
        fail(errors, f"Adversarial harness missing required harnesses: {sorted(missing)}")
    for name, harness in harnesses.items():
        fixture = harness.get("fixture")
        if fixture and not (ROOT / "examples" / "jailbreak-resilience" / "fixtures" / fixture).is_dir():
            fail(errors, f"Adversarial harness {name} references missing fixture: {fixture}")
    adapter = data.get("external_corpus_adapters", {})
    if adapter.get("enabled_by_default") is not False:
        fail(errors, "External corpus adapters must be disabled by default")
    for field in ["source_url", "license", "fetch_date", "transformation_policy", "defanging_policy", "local_opt_in"]:
        if field not in adapter.get("required_metadata", []):
            fail(errors, f"External corpus adapter metadata missing {field}")


def validate_library_manifest(errors: list[str]) -> None:
    path = ROOT / "exports" / "library-manifest.json"
    if not path.exists():
        fail(errors, "Missing exports/library-manifest.json")
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "software-grimoire-library-v1":
        fail(errors, "Library manifest schema mismatch")
    for section in ["assets", "bundles"]:
        for item in manifest.get(section, []):
            file_path = ROOT / item.get("path", "")
            if not file_path.exists():
                fail(errors, f"Library manifest {section} path missing: {item.get('path')}")
                continue
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if digest != item.get("sha256"):
                fail(errors, f"Library manifest checksum mismatch: {item.get('path')}")
            if file_path.stat().st_size != item.get("bytes"):
                fail(errors, f"Library manifest byte count mismatch: {item.get('path')}")
    bundle_names = {Path(item.get("path", "")).name for item in manifest.get("bundles", [])}
    required_bundles = {
        "software-grimoire-prompts.zip",
        "software-grimoire-codex-templates.zip",
        "software-grimoire-cursor-rules.zip",
        "software-grimoire-claude-code-skills.zip",
        "software-grimoire-stacks.zip",
    }
    missing = required_bundles - bundle_names
    if missing:
        fail(errors, f"Library manifest missing release bundles: {sorted(missing)}")


def validate_generator_architecture(errors: list[str]) -> None:
    path = ROOT / "data" / "generator_architecture.json"
    if not path.exists():
        fail(errors, "Missing data/generator_architecture.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    components = {item.get("component") for item in data.get("components", [])}
    for required in ["sources", "lexicon", "spells", "stacks", "bench", "exports", "site", "seals"]:
        if required not in components:
            fail(errors, f"Generator architecture missing component: {required}")
    if not data.get("determinism_policy"):
        fail(errors, "Generator architecture missing determinism policy")


def validate_visual_practice(errors: list[str]) -> None:
    path = ROOT / "data" / "visual_practice.json"
    if not path.exists():
        fail(errors, "Missing data/visual_practice.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    spells = load("spells.json")
    stacks = load("stacks.json")
    if set(data.get("spell_diagrams", {})) != {spell["id"] for spell in spells}:
        fail(errors, "Visual practice must include one diagram per spell")
    if set(data.get("stack_diagrams", {})) != {stack["id"] for stack in stacks}:
        fail(errors, "Visual practice must include one diagram per stack")
    for diagram in list(data.get("spell_diagrams", {}).values()) + list(data.get("stack_diagrams", {}).values()) + [data.get("ward_diagram", "")]:
        if diagram and not (ROOT / diagram).exists():
            fail(errors, f"Visual practice diagram missing: {diagram}")


def validate_adoption_evidence(errors: list[str]) -> None:
    path = ROOT / "data" / "adoption_evidence.json"
    if not path.exists():
        fail(errors, "Missing data/adoption_evidence.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    required_fields = set(data.get("report_template", {}).get("required_fields", []))
    for field in [
        "id",
        "title",
        "provenance",
        "task",
        "spell_or_stack_used",
        "surface",
        "artifact_produced",
        "verification_performed",
        "time_cost",
        "failure_or_friction",
        "reuse_decision",
    ]:
        if field not in required_fields:
            fail(errors, f"Adoption evidence template missing required field: {field}")
    provenance_values = set(data.get("report_template", {}).get("provenance_values", []))
    for value in ["project-owned", "reviewer-supplied", "external-user"]:
        if value not in provenance_values:
            fail(errors, f"Adoption evidence missing provenance value: {value}")
    reports = data.get("reports", [])
    if len(reports) < 3:
        fail(errors, "Adoption evidence must include at least three project-owned dogfood reports")
    for report in reports:
        for field in required_fields:
            if field not in report or report[field] in ("", None):
                fail(errors, f"Adoption evidence report {report.get('id')} missing {field}")
        if report.get("provenance") not in provenance_values:
            fail(errors, f"Adoption evidence report {report.get('id')} has invalid provenance")
    status = data.get("external_status", {})
    policy = status.get("policy", "")
    if status.get("external_reports_published", 0) == 0 and "Do not fabricate external adoption" not in policy:
        fail(errors, "Adoption evidence must state the no-fabricated-external-adoption policy")
    template_path = ROOT / "examples" / "adoption" / "adoption-report-template.json"
    intake_path = ROOT / "examples" / "adoption" / "adoption-intake-decision-template.json"
    if not template_path.exists():
        fail(errors, "Missing examples/adoption/adoption-report-template.json")
        return
    template = json.loads(template_path.read_text(encoding="utf-8"))
    for field in required_fields:
        if field not in template or template[field] in ("", None):
            fail(errors, f"Adoption report template missing {field}")
    if template.get("provenance") not in provenance_values:
        fail(errors, "Adoption report template provenance is not allowed")
    if not intake_path.exists():
        fail(errors, "Missing examples/adoption/adoption-intake-decision-template.json")
    else:
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
        if intake.get("status") != "pending-maintainer":
            fail(errors, "Adoption intake decision template must remain pending-maintainer")
        if intake.get("decision") != "pending":
            fail(errors, "Adoption intake decision template must not contain a real decision")
        if intake.get("counts_as_external_adoption") is not False:
            fail(errors, "Adoption intake decision template cannot count as external adoption")
        if intake.get("blocks_external_adoption_credit") is not True:
            fail(errors, "Adoption intake decision template must block external adoption credit")
        if intake.get("report_path") != "examples/adoption/adoption-report-template.json":
            fail(errors, "Adoption intake decision template must reference the adoption report template")


def validate_v3_evidence_layer(errors: list[str]) -> None:
    taxonomy_path = ROOT / "data" / "evidence_taxonomy.json"
    index_path = ROOT / "data" / "evidence_index.json"
    audit_path = ROOT / "data" / "canon_audit.json"
    usage_path = ROOT / "data" / "rune_usage_graph.json"
    for path in [taxonomy_path, index_path, audit_path, usage_path]:
        if not path.exists():
            fail(errors, f"Missing {path.relative_to(ROOT)}")
            return

    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    for evidence_class in [
        "calibration_fixture",
        "project_owned_model_run",
        "reviewer_supplied_model_run",
        "local_deterministic_execution",
        "local_deterministic_control",
        "packaging_or_release_check",
        "human_audit_pending",
        "roadmap_acceptance_status",
        "adoption_report",
    ]:
        if evidence_class not in taxonomy.get("evidence_classes", {}):
            fail(errors, f"Evidence taxonomy missing class: {evidence_class}")
    rules = "\n".join(taxonomy.get("promotion_rules", []))
    if "Do not use local deterministic graders as independent model evidence" not in rules:
        fail(errors, "Evidence taxonomy must separate deterministic graders from model evidence")

    index = json.loads(index_path.read_text(encoding="utf-8"))
    artifacts = {artifact.get("id"): artifact for artifact in index.get("artifacts", [])}
    for artifact_id in [
        "field-spell-model-runs",
        "fixture-local-execution",
        "model-produced-artifact-execution",
        "jailbreak-resilience-model-runs",
        "local-warded-baseline",
        "real-warded-ab",
        "hardness-intake-decision-template",
        "adoption-intake-decision-template",
        "canon-audit-decision-template",
        "package-check",
        "package-index-smoke-template",
        "logical-conclusion-status",
        "public-smoke-check",
    ]:
        artifact = artifacts.get(artifact_id)
        if not artifact:
            fail(errors, f"Evidence index missing artifact: {artifact_id}")
            continue
        if not artifact.get("exists"):
            fail(errors, f"Evidence artifact is missing on disk: {artifact_id}")
    summary = index.get("summary", {})
    if summary.get("project_owned_model_surface_count", 0) < 2:
        fail(errors, "Evidence index must include at least two project-owned model surfaces")
    if summary.get("recorded_model_runs", 0) <= 0:
        fail(errors, "Evidence index must include recorded model runs")

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("status") != "pending-human-maintainer-signoff":
        fail(errors, "Canon audit must honestly preserve pending human signoff status")
    if not audit.get("audit_queue"):
        fail(errors, "Canon audit must include an audit queue")
    decision_path = ROOT / "examples" / "canon" / "canon-audit-decision-template.json"
    if not decision_path.exists():
        fail(errors, "Missing examples/canon/canon-audit-decision-template.json")
    else:
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("status") != "pending-human-maintainer":
            fail(errors, "Canon audit decision template must remain pending-human-maintainer")
        if decision.get("decision") != "pending":
            fail(errors, "Canon audit decision template must not contain a real decision")
        if decision.get("accepted_as_canonical") is not False:
            fail(errors, "Canon audit decision template cannot accept canonical status")
        if decision.get("blocks_canonical_promotion") is not True:
            fail(errors, "Canon audit decision template must keep canonical promotion blocked")
        audit_ids = {item.get("id") for item in audit.get("audit_queue", [])}
        if decision.get("audit_id") not in audit_ids:
            fail(errors, "Canon audit decision template audit_id must exist in canon audit queue")

    usage = json.loads(usage_path.read_text(encoding="utf-8"))
    if usage.get("summary", {}).get("canonical_review_candidates", 0) <= 0:
        fail(errors, "Usage graph must nominate canonical review candidates")
    for candidate in usage.get("canonical_review_candidates", []):
        if candidate.get("promotion_blocker") != "human maintainer signoff required":
            fail(errors, f"Usage candidate missing human signoff blocker: {candidate.get('sigil')}")


def validate_model_artifact_execution(errors: list[str]) -> None:
    path = ROOT / "examples" / "evaluations" / "model-execution-results.json"
    if not path.exists():
        fail(errors, "Missing examples/evaluations/model-execution-results.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for case in ["safe-refactoring", "test-generation"]:
        if case not in data.get("cases", {}):
            fail(errors, f"Model artifact execution missing case: {case}")
    if "claude-code-safe" not in data.get("surfaces", {}):
        fail(errors, "Model artifact execution should include claude-code-safe as the real second surface")
    for slug, case in data.get("cases", {}).items():
        for run in case.get("runs", []):
            for key in ["fixture_path", "prompt_path", "transcript_path", "artifact_path"]:
                value = run.get(key)
                if not value or not (ROOT / value).exists():
                    fail(errors, f"Model artifact execution {slug} missing {key}: {value}")
            result = run.get("execution_result", {})
            if result.get("passed") not in {True, False}:
                fail(errors, f"Model artifact execution {slug} has no boolean pass/fail")
            if run.get("execution_command", "").find("pytest") == -1:
                fail(errors, f"Model artifact execution {slug} must run pytest")


def validate_real_warded_ab(errors: list[str]) -> None:
    path = ROOT / "examples" / "jailbreak-resilience" / "ab-results.json"
    if not path.exists():
        fail(errors, "Missing examples/jailbreak-resilience/ab-results.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("payload_policy") != "defanged-fixtures-only":
        fail(errors, "Real warded A/B payload policy must be defanged-fixtures-only")
    if not any(surface.startswith("claude-code-safe") for surface in data.get("surfaces", {})):
        fail(errors, "Real warded A/B should include claude-code-safe as the real second surface")
    if not any(surface.startswith("codex-cli-default") for surface in data.get("surfaces", {})):
        fail(errors, "Real warded A/B should include codex-cli-default as the primary Codex surface")
    if not data.get("baseline_failures"):
        fail(errors, "Real warded A/B should preserve baseline failures or weak baseline audit losses")
    for slug, case in data.get("cases", {}).items():
        variants = {run.get("variant") for run in case.get("runs", [])}
        if variants != {"baseline", "warded"}:
            fail(errors, f"Real warded A/B case must include baseline and warded variants: {slug}")
        for surface in ["claude-code-safe", "codex-cli-default"]:
            for variant in ["baseline", "warded"]:
                surface_runs = [
                    run
                    for run in case.get("runs", [])
                    if run.get("base_surface") == surface and run.get("variant") == variant
                ]
                if len(surface_runs) < 3:
                    fail(errors, f"Real warded A/B {slug} needs at least 3 {surface} {variant} runs")
        for run in case.get("runs", []):
            for key in ["fixture_path", "prompt_path", "transcript_path"]:
                value = run.get(key)
                if value and not (ROOT / value).exists():
                    fail(errors, f"Real warded A/B {key} missing: {value}")
            output = run.get("output", "").lower()
            for forbidden in ["canary-secret-671", "canary-indirect-724", "rm -rf", "curl https://attacker.example"]:
                if forbidden in output:
                    fail(errors, f"Real warded A/B output contains unredacted forbidden string: {slug}")
            if run.get("total_score") != sum(run.get("axis_totals", {}).values()):
                fail(errors, f"Real warded A/B total score mismatch: {slug}")


def validate_hardness_model_surface(errors: list[str]) -> None:
    path = ROOT / "examples" / "evaluations" / "hardness-v4" / "model-surface-results.json"
    if not path.exists():
        fail(errors, "Missing examples/evaluations/hardness-v4/model-surface-results.json")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if "codex-cli-default" not in data.get("surfaces", {}):
        fail(errors, "Bench v4 model-surface hardness results must include codex-cli-default")
    if data.get("minimum_repetitions_per_surface_variant", 0) < 5:
        fail(errors, "Bench v4 model-surface hardness results need at least 5 repetitions per surface/variant cell")
    required_rungs = {"ambiguity", "hidden-invariant", "misleading-context", "blast-radius", "agentic"}
    observed_rungs = {case.get("rung") for case in data.get("cases", {}).values()}
    if not required_rungs <= observed_rungs:
        fail(errors, "Bench v4 model-surface hardness results must cover all five hardness rungs")
    for slug, case in data.get("cases", {}).items():
        for key in ["fixture_path", "ground_truth_path"]:
            value = case.get(key)
            if not value or not (ROOT / value).exists():
                fail(errors, f"Bench v4 model-surface {slug} missing {key}: {value}")
        for variant in ["weak", "repaired"]:
            runs = [
                run
                for run in case.get("runs", [])
                if run.get("surface") == "codex-cli-default" and run.get("variant") == variant
            ]
            if len(runs) < 5:
                fail(errors, f"Bench v4 model-surface {slug} needs at least 5 Codex {variant} runs")
        for run in case.get("runs", []):
            for key in ["prompt_path", "transcript_path", "artifact_root"]:
                value = run.get(key)
                if not value or not (ROOT / value).exists():
                    fail(errors, f"Bench v4 model-surface {slug} missing {key}: {value}")
            for artifact in run.get("artifact_paths", []):
                if not (ROOT / artifact).exists():
                    fail(errors, f"Bench v4 model-surface extracted artifact missing: {artifact}")
            if run.get("execution_result", {}).get("passed") not in {True, False}:
                fail(errors, f"Bench v4 model-surface {slug} run has no boolean execution result")
            if run.get("extraction_result", {}).get("complete") not in {True, False}:
                fail(errors, f"Bench v4 model-surface {slug} run has no extraction status")
    template_path = ROOT / "examples" / "evaluations" / "hardness-v4" / "manual-import-template.json"
    decision_path = ROOT / "examples" / "evaluations" / "hardness-v4" / "hardness-intake-decision-template.json"
    if not template_path.exists():
        fail(errors, "Missing examples/evaluations/hardness-v4/manual-import-template.json")
        return
    template = json.loads(template_path.read_text(encoding="utf-8"))
    required_fields = [
        "schema_version",
        "surface_id",
        "surface_label",
        "surface_kind",
        "tool_name",
        "tool_version",
        "model_name",
        "provenance",
        "evidence_class",
        "redaction_statement",
        "reviewer_id",
        "reviewer_date",
        "benchmark",
        "case_slug",
        "variant",
        "fixture_path",
        "prompt_path",
        "transcript_path",
        "artifact_root",
        "artifact_files",
        "execution_command",
        "safety_statement",
        "maintainer_decision",
    ]
    for field in required_fields:
        if template.get(field) in ("", None, [], {}):
            fail(errors, f"Bench v4 manual import template missing {field}")
    if template.get("schema_version") != "4.0.0-hardness-manual-import":
        fail(errors, "Bench v4 manual import template schema_version mismatch")
    if template.get("benchmark") != "hardness-v4-model-surface":
        fail(errors, "Bench v4 manual import template benchmark mismatch")
    if template.get("maintainer_decision") != "pending":
        fail(errors, "Bench v4 manual import template must remain pending")
    if template.get("evidence_class") != PROVENANCE_EVIDENCE_CLASS.get(template.get("provenance")):
        fail(errors, "Bench v4 manual import template evidence_class/provenance mismatch")
    for key in ["fixture_path", "prompt_path", "transcript_path", "artifact_root"]:
        value = template.get(key)
        if value and not (ROOT / value).exists():
            fail(errors, f"Bench v4 manual import template missing path {key}: {value}")
    if not decision_path.exists():
        fail(errors, "Missing examples/evaluations/hardness-v4/hardness-intake-decision-template.json")
    else:
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        if decision.get("status") != "pending-maintainer":
            fail(errors, "Bench v4 hardness intake decision template must remain pending-maintainer")
        if decision.get("decision") != "pending":
            fail(errors, "Bench v4 hardness intake decision template must not contain a real decision")
        if decision.get("counts_as_cross_surface_hardness") is not False:
            fail(errors, "Bench v4 hardness intake decision template cannot count as cross-surface hardness")
        if decision.get("blocks_hardness_credit") is not True:
            fail(errors, "Bench v4 hardness intake decision template must block hardness credit")
        if decision.get("import_path") != "examples/evaluations/hardness-v4/manual-import-template.json":
            fail(errors, "Bench v4 hardness intake decision template must reference the manual import template")


def validate_public_package_and_smoke(errors: list[str]) -> None:
    package_path = ROOT / "examples" / "adoption" / "package-check.json"
    package_index_plan_path = ROOT / "examples" / "adoption" / "package-index-release-plan.json"
    package_index_smoke_path = ROOT / "examples" / "adoption" / "package-index-smoke-template.json"
    package_publish_workflow_path = ROOT / ".github" / "workflows" / "publish-package.yml"
    smoke_path = ROOT / "examples" / "release-gate" / "public-smoke-check.json"
    if not package_path.exists():
        fail(errors, "Missing examples/adoption/package-check.json")
    else:
        package = json.loads(package_path.read_text(encoding="utf-8"))
        if package.get("passed") is not True:
            fail(errors, "Package check must pass")
        step_names = {step.get("name") for step in package.get("steps", [])}
        for expected in ["build wheel and sdist", "install wheel"]:
            if expected not in step_names:
                fail(errors, f"Package check missing step: {expected}")
        if not any("grimoire-check-package-index --help" in step.get("name", "") for step in package.get("steps", [])):
            fail(errors, "Package check must verify grimoire-check-package-index entry point")
        if not any("grimoire-check-adoption-intake --help" in step.get("name", "") for step in package.get("steps", [])):
            fail(errors, "Package check must verify grimoire-check-adoption-intake entry point")
        if not any("grimoire-check-hardness-intake --help" in step.get("name", "") for step in package.get("steps", [])):
            fail(errors, "Package check must verify grimoire-check-hardness-intake entry point")
        if not any("grimoire-check-canon-decision --help" in step.get("name", "") for step in package.get("steps", [])):
            fail(errors, "Package check must verify grimoire-check-canon-decision entry point")
        if not any("grimoire-check-package-publish-workflow --help" in step.get("name", "") for step in package.get("steps", [])):
            fail(errors, "Package check must verify grimoire-check-package-publish-workflow entry point")
    if not package_index_plan_path.exists():
        fail(errors, "Missing examples/adoption/package-index-release-plan.json")
    else:
        plan = json.loads(package_index_plan_path.read_text(encoding="utf-8"))
        trusted = plan.get("trusted_publishing_workflow", {})
        if trusted.get("path") != ".github/workflows/publish-package.yml":
            fail(errors, "Package-index release plan must point to the manual package publish workflow")
        if trusted.get("authentication") != "PyPI Trusted Publishing via GitHub OIDC":
            fail(errors, "Package-index release plan must use PyPI Trusted Publishing via GitHub OIDC")
        if "id-token: write" not in trusted.get("required_permissions", []):
            fail(errors, "Package-index release plan must record id-token: write")
        for upload_key in ["testpypi_upload", "pypi_upload"]:
            command = plan.get(upload_key, {}).get("command", "")
            if ".github/workflows/publish-package.yml" not in command:
                fail(errors, f"Package-index release plan {upload_key} must dispatch the manual publish workflow")
            check = plan.get(upload_key, {}).get("post_upload_check", "")
            if "scripts/check_package_index.py" not in check:
                fail(errors, f"Package-index release plan {upload_key} must use scripts/check_package_index.py")
        if not any("check_package_index.py" in item and "--dry-run" in item for item in plan.get("preflight_checks", [])):
            fail(errors, "Package-index release plan must include a dry-run checker preflight")
        if not any("check_package_publish_workflow.py" in item for item in plan.get("preflight_checks", [])):
            fail(errors, "Package-index release plan must validate the publish workflow")
    if not package_publish_workflow_path.exists():
        fail(errors, "Missing .github/workflows/publish-package.yml")
    else:
        workflow = package_publish_workflow_path.read_text(encoding="utf-8")
        if "workflow_dispatch:" not in workflow:
            fail(errors, "Package publish workflow must be manually dispatched")
        if "pypa/gh-action-pypi-publish@release/v1" not in workflow:
            fail(errors, "Package publish workflow must use the PyPA trusted publishing action")
        if "id-token: write" not in workflow:
            fail(errors, "Package publish workflow must request id-token: write")
        if "password: ${{ secrets." in workflow or "twine upload" in workflow:
            fail(errors, "Package publish workflow must not use secret/token upload commands")
    if not package_index_smoke_path.exists():
        fail(errors, "Missing examples/adoption/package-index-smoke-template.json")
    else:
        package_index_smoke = json.loads(package_index_smoke_path.read_text(encoding="utf-8"))
        if package_index_smoke.get("status") != "pending_upload":
            fail(errors, "Package-index smoke template must remain pending_upload")
        if package_index_smoke.get("passed") is not False:
            fail(errors, "Package-index smoke template cannot pass before public upload")
    if not smoke_path.exists():
        fail(errors, "Missing examples/release-gate/public-smoke-check.json")
    else:
        smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
        if smoke.get("passed") is not True:
            fail(errors, "Public smoke check must pass")
        targets = {item.get("target") for item in smoke.get("checks", [])}
        for expected in ["index.html", "reference/evidence-browser.html", "exports/library-manifest.json"]:
            if expected not in targets:
                fail(errors, f"Public smoke check missing target: {expected}")
        if "examples/canon/canon-audit-decision-template.json" not in targets:
            fail(errors, "Public smoke check missing canon audit decision template")
        if "examples/evaluations/hardness-v4/hardness-intake-decision-template.json" not in targets:
            fail(errors, "Public smoke check missing Bench v4 hardness intake decision template")
        if "examples/adoption/adoption-intake-decision-template.json" not in targets:
            fail(errors, "Public smoke check missing adoption intake decision template")
        if "examples/adoption/package-index-smoke-template.json" not in targets:
            fail(errors, "Public smoke check missing package-index smoke template")


def validate_logical_conclusion_status(errors: list[str]) -> None:
    path = ROOT / "data" / "logical_conclusion_status.json"
    if not path.exists():
        fail(errors, "Missing data/logical_conclusion_status.json")
        return
    status = json.loads(path.read_text(encoding="utf-8"))
    criteria = status.get("criteria", [])
    summary = status.get("summary", {})
    if len(criteria) != 90:
        fail(errors, f"Logical conclusion status must track 90 criteria, found {len(criteria)}")
        return
    ids = [item.get("id") for item in criteria]
    if sorted(ids) != list(range(1, 91)):
        fail(errors, "Logical conclusion criteria ids must be exactly 1..90")
    allowed_statuses = {"proven", "partial", "pending_human", "pending_package_index", "pending_external"}
    counts = {key: 0 for key in allowed_statuses}
    criteria_by_id = {}
    for item in criteria:
        ident = item.get("id")
        criteria_by_id[ident] = item
        item_status = item.get("status")
        if item_status not in allowed_statuses:
            fail(errors, f"Logical conclusion criterion {ident} has invalid status: {item_status}")
            continue
        counts[item_status] += 1
        if item_status != "proven" and not item.get("blockers"):
            fail(errors, f"Logical conclusion criterion {ident} is not proven but has no blocker")
        if item_status == "proven" and item.get("blockers"):
            fail(errors, f"Logical conclusion criterion {ident} is proven but still lists blockers")
        for evidence in item.get("evidence", []):
            if evidence.get("kind") == "path" and not (ROOT / evidence.get("target", "")).exists():
                fail(errors, f"Logical conclusion criterion {ident} evidence path missing: {evidence.get('target')}")
    expected_summary = {
        "criteria_total": len(criteria),
        "proven": counts["proven"],
        "partial": counts["partial"],
        "pending_human": counts["pending_human"],
        "pending_package_index": counts["pending_package_index"],
        "pending_external": counts["pending_external"],
        "pending_total": counts["partial"] + counts["pending_human"] + counts["pending_package_index"] + counts["pending_external"],
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            fail(errors, f"Logical conclusion summary {key}={summary.get(key)} does not match computed {value}")
    if summary.get("external_claims_fabricated") is not False:
        fail(errors, "Logical conclusion status must not fabricate external claims")

    hard_gates = {
        69: "pending_human",
        70: "pending_human",
        72: "pending_package_index",
        74: "pending_external",
        79: "pending_external",
        88: "partial",
    }
    for ident, required_status in hard_gates.items():
        actual = criteria_by_id.get(ident, {}).get("status")
        if actual != required_status:
            fail(errors, f"Logical conclusion criterion {ident} must remain {required_status}, found {actual}")

    adoption = load("adoption_evidence.json")
    if adoption.get("external_status", {}).get("external_reports_published") == 0 and criteria_by_id[74]["status"] == "proven":
        fail(errors, "External adoption criterion cannot be proven while external_reports_published is 0")
    audit = load("canon_audit.json")
    if audit.get("status") == "pending-human-maintainer-signoff":
        for ident in [69, 70]:
            if criteria_by_id[ident]["status"] == "proven":
                fail(errors, f"Human canon criterion {ident} cannot be proven while canon audit is pending")
    model = json.loads((ROOT / "examples" / "evaluations" / "hardness-v4" / "model-surface-results.json").read_text(encoding="utf-8"))
    if set(model.get("surfaces", {})) == {"codex-cli-default"} and criteria_by_id[79]["status"] == "proven":
        fail(errors, "Bench v4 cross-surface criterion cannot be proven with only codex-cli-default accepted")
    for gate in status.get("open_gates", []):
        if not gate.get("criteria"):
            fail(errors, f"Logical conclusion open gate has no criteria: {gate.get('id')}")
        if gate.get("status") == "proven":
            fail(errors, f"Logical conclusion open gate cannot be proven: {gate.get('id')}")
        for ident in gate.get("criteria", []):
            if ident not in criteria_by_id:
                fail(errors, f"Logical conclusion open gate references missing criterion {ident}")
        for evidence in gate.get("evidence", []):
            if evidence.get("kind") == "path" and not (ROOT / evidence.get("target", "")).exists():
                fail(errors, f"Logical conclusion open gate evidence path missing: {evidence.get('target')}")


def main() -> int:
    errors: list[str] = []
    houses = validate_houses(errors)
    lexicon = validate_lexicon(errors, houses)
    validate_major_and_pocket(errors, lexicon)
    validate_canon_quality(errors, lexicon)
    validate_semantic_promotion(errors, lexicon, houses)
    spells = validate_spells(errors, lexicon)
    validate_stacks(errors, lexicon, spells)
    validate_jailbreak_resilience(errors)
    validate_bench_v2(errors)
    validate_execution_bench(errors)
    validate_surface_comparison(errors)
    validate_jailbreak_baselines(errors)
    validate_adversarial_harness(errors)
    validate_library_manifest(errors)
    validate_generator_architecture(errors)
    validate_visual_practice(errors)
    validate_adoption_evidence(errors)
    validate_model_artifact_execution(errors)
    validate_real_warded_ab(errors)
    validate_hardness_model_surface(errors)
    validate_public_package_and_smoke(errors)
    validate_logical_conclusion_status(errors)
    validate_v3_evidence_layer(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
