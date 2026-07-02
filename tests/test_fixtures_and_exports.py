#!/usr/bin/env python3
"""Validate benchmark fixtures and generated installable exports."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "tmp" / "tests" / "install-assets"
EXPECTED_CASES = {
    "safe-refactoring",
    "bug-diagnosis-from-logs",
    "api-design",
    "migration-without-data-loss",
    "test-generation",
    "performance-tuning",
}
EXPECTED_SPELLS = {
    "safe-refactoring",
    "bug-diagnosis-from-logs",
    "api-design",
    "migration-without-data-loss",
    "test-generation",
    "performance-tuning",
    "jailbreak-resilience-review",
}
EXPECTED_STACKS = {
    "code-generation-and-repair-loop",
    "bug-hunt-stack",
    "safe-refactor-stack",
    "live-migration-stack",
    "release-gate-stack",
    "recursive-decomposition-stack",
    "ai-red-team-loop",
}


def remove_scratch(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass


def test_all_evaluation_fixtures_exist() -> None:
    for slug in EXPECTED_CASES:
        fixture_dir = ROOT / "examples" / "evaluations" / "fixtures" / slug
        assert fixture_dir.is_dir(), slug
        assert (fixture_dir / "context.md").exists(), slug
        assert any(path.name.startswith("ground_truth") or path.name.startswith("expected_behavior") for path in fixture_dir.iterdir()), slug


def test_safe_refactoring_fixture_is_executable() -> None:
    fixture_dir = ROOT / "examples" / "evaluations" / "fixtures" / "safe-refactoring"
    assert (fixture_dir / "normalize_user.py").exists()
    assert (fixture_dir / "check_normalize_user.py").exists()


def test_installable_exports_exist_and_trace_to_seals() -> None:
    spells = {item["id"].split(".")[1]: item for item in json.loads((ROOT / "data" / "spells.json").read_text(encoding="utf-8"))}
    stacks = {item["id"].split(".")[1]: item for item in json.loads((ROOT / "data" / "stacks.json").read_text(encoding="utf-8"))}
    assert set(spells) == EXPECTED_SPELLS
    assert set(stacks) == EXPECTED_STACKS
    for slug, spell in spells.items():
        for path in [
            ROOT / "exports" / "markdown" / "spells" / f"{slug}.md",
            ROOT / "exports" / "codex" / f"{slug}.md",
            ROOT / "exports" / "cursor" / "rules" / f"{slug}.mdc",
            ROOT / "exports" / "claude-code" / "skills" / f"{slug}.md",
        ]:
            text = path.read_text(encoding="utf-8")
            assert spell["id"] in text
            assert spell["working_seal"] in text
    for slug, stack in stacks.items():
        text = (ROOT / "exports" / "markdown" / "stacks" / f"{slug}.md").read_text(encoding="utf-8")
        assert stack["id"] in text
        assert stack["working_seal"] in text


def test_release_gate_dogfood_record_exists() -> None:
    record_path = ROOT / "examples" / "release-gate" / "release-gate-stack-run.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["stack_id"] == "stack.release-gate-stack.v1"
    assert record["workflow"] == "Publish Quarto Site"
    assert "validate data" in record["gates"]


def test_jailbreak_resilience_fixtures_exist() -> None:
    data = json.loads((ROOT / "data" / "jailbreak_resilience.json").read_text(encoding="utf-8"))
    assert data["payload_policy"] == "defanged-fixtures-only"
    assert len(data["cases"]) == 8
    for slug, case in data["cases"].items():
        fixture_dir = ROOT / case["fixture_path"]
        assert fixture_dir.is_dir(), slug
        assert (fixture_dir / "context.md").exists(), slug
        truth = json.loads((fixture_dir / "ground_truth.json").read_text(encoding="utf-8"))
        assert truth["payload_policy"] == "defanged"
        assert truth["attack_shape"] == case["attack_shape"]


def test_jailbreak_exports_exist_and_preserve_safety_scope() -> None:
    spell = json.loads((ROOT / "data" / "spells.json").read_text(encoding="utf-8"))
    warded = next(item for item in spell if item["id"] == "spell.jailbreak-resilience-review.v1")
    for key in ["trust_boundary", "allowed_tools", "forbidden_outputs", "refusal_contract", "audit_log"]:
        assert warded[key]
    for path in [
        ROOT / "exports" / "markdown" / "spells" / "jailbreak-resilience-review.md",
        ROOT / "exports" / "codex" / "jailbreak-resilience-review.md",
        ROOT / "exports" / "cursor" / "rules" / "jailbreak-resilience-review.mdc",
        ROOT / "exports" / "claude-code" / "skills" / "jailbreak-resilience-review.md",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "spell.jailbreak-resilience-review.v1" in text
        assert warded["working_seal"] in text
        assert "FORBIDDEN OUTPUTS" in text
        assert "working bypass" in text


def test_bench_v2_contract_and_import_template_exist() -> None:
    data = json.loads((ROOT / "data" / "bench_v2.json").read_text(encoding="utf-8"))
    assert "codex-cli-default" in data["surfaces"]
    assert "manual-reviewer-import" in data["surfaces"]
    assert data["deterministic_checks"]["safe-refactoring"]["kind"] == "executable-fixture"
    assert "pytest" in data["deterministic_checks"]["safe-refactoring"]["command"]
    assert "local-deterministic-grader" in data["surfaces"]
    assert "local-unwarded-control" in data["surfaces"]
    assert "local-warded-reviewer" in data["surfaces"]
    template = json.loads((ROOT / "examples" / "evaluations" / "manual-import-template.json").read_text(encoding="utf-8"))
    for field in data["manual_import_contract"]["required_fields"]:
        assert template[field]
    assert (ROOT / template["fixture_path"]).exists()
    assert (ROOT / template["prompt_path"]).exists()
    assert (ROOT / template["transcript_path"]).exists()


def test_adversarial_harness_contract_and_results_exist() -> None:
    data = json.loads((ROOT / "data" / "adversarial_harness.json").read_text(encoding="utf-8"))
    assert data["payload_policy"] == "defanged-fixtures-only"
    assert data["execution_policy"] == "local-read-only"
    for name in ["tool-mediator", "retrieval-taint", "multi-turn-state", "long-context-drift", "redaction", "overrefusal"]:
        assert name in data["harnesses"]
        fixture = data["harnesses"][name]["fixture"]
        assert (ROOT / "examples" / "jailbreak-resilience" / "fixtures" / fixture).is_dir()
    assert data["external_corpus_adapters"]["enabled_by_default"] is False
    results = json.loads((ROOT / "examples" / "jailbreak-resilience" / "harness-results.json").read_text(encoding="utf-8"))
    assert set(results["harnesses"]) == set(data["harnesses"])
    assert all(item["passed"] for item in results["harnesses"].values())


def test_execution_bench_trap_fixtures_and_results_exist() -> None:
    bench = json.loads((ROOT / "data" / "execution_bench.json").read_text(encoding="utf-8"))
    results = json.loads((ROOT / "examples" / "evaluations" / "execution-results.json").read_text(encoding="utf-8"))
    assert set(bench["cases"]) == EXPECTED_CASES
    assert set(results["cases"]) == EXPECTED_CASES
    for slug, tiers in bench["cases"].items():
        assert (ROOT / tiers["clean"]["fixture_path"]).exists()
        trap_fixture = ROOT / tiers["trap"]["fixture_path"]
        assert trap_fixture.is_dir(), slug
        assert (trap_fixture / "context.md").exists(), slug
        assert (trap_fixture / "ground_truth.json").exists(), slug
        assert tiers["trap"]["trap"]
        assert tiers["trap"]["expected_failure"]
    safe_runs = {
        (run["tier"], run["variant"]): run
        for run in results["cases"]["safe-refactoring"]["runs"]
    }
    assert safe_runs[("clean", "weak")]["execution_result"]["passed"] is False
    assert safe_runs[("clean", "repaired")]["execution_result"]["passed"] is True
    assert safe_runs[("trap", "weak")]["execution_result"]["passed"] is False
    assert safe_runs[("trap", "repaired")]["execution_result"]["passed"] is True


def test_surface_comparison_and_warded_baselines_exist() -> None:
    surface = json.loads((ROOT / "examples" / "evaluations" / "surface-comparison.json").read_text(encoding="utf-8"))
    assert {"codex-cli-default", "local-deterministic-grader"} <= set(surface["surfaces"])
    for item in surface["field_spell_matrix"].values():
        assert {"codex-cli-default", "local-deterministic-grader"} <= set(item["surfaces"])
        assert "not independent model evidence" in item["surfaces"]["local-deterministic-grader"]["limitation"]
        for model_surface in ["codex-cli-default", "claude-code-safe"]:
            if model_surface in item["surfaces"]:
                cells = item["surfaces"][model_surface]["cells"]
                assert cells
                assert all(cell["surface"] == model_surface for cell in cells)
                assert all("reviewability_delta" in cell and "outcome_delta" in cell for cell in cells)
        assert item["surfaces"]["local-deterministic-grader"]["cells"] == []

    baseline = json.loads((ROOT / "examples" / "jailbreak-resilience" / "baseline-results.json").read_text(encoding="utf-8"))
    assert baseline["payload_policy"] == "defanged-fixtures-only"
    assert baseline["baseline_failures"]
    for case in baseline["cases"].values():
        assert {run["variant"] for run in case["runs"]} == {"baseline", "warded"}
        for run in case["runs"]:
            assert run["total_score"] == sum(run["axis_totals"].values())
            output = run["output"].lower()
            assert "rm -rf" not in output
            assert "curl https://attacker.example" not in output


def test_semantic_promotion_ladder_has_reviewed_houses() -> None:
    promotion = json.loads((ROOT / "data" / "semantic_promotion.json").read_text(encoding="utf-8"))
    assert promotion["summary"]["reviewed_or_canonical_entries"] >= promotion["summary"]["target_reviewed_entries"]
    houses = {item["house"]: item for item in promotion["houses"]}
    for house in ["architecture-abstraction-and-design", "language-semantics-and-formal-shape"]:
        assert houses[house]["fully_reviewed"] is True
        assert houses[house]["generated_draft_entries"] == 0


def test_library_manifest_and_bundles_exist() -> None:
    manifest = json.loads((ROOT / "exports" / "library-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "software-grimoire-library-v1"
    assert len(manifest["spells"]) == len(EXPECTED_SPELLS)
    assert len(manifest["stacks"]) == len(EXPECTED_STACKS)
    bundle_names = {Path(item["path"]).name for item in manifest["bundles"]}
    assert {
        "software-grimoire-prompts.zip",
        "software-grimoire-codex-templates.zip",
        "software-grimoire-cursor-rules.zip",
        "software-grimoire-claude-code-skills.zip",
        "software-grimoire-stacks.zip",
    } <= bundle_names
    for item in manifest["bundles"]:
        path = ROOT / item["path"]
        assert path.exists()
        with zipfile.ZipFile(path) as archive:
            assert "MANIFEST.json" in archive.namelist()
            assert len(archive.namelist()) > 1


def test_visual_practice_diagrams_exist_and_placeholders_are_removed() -> None:
    visual = json.loads((ROOT / "data" / "visual_practice.json").read_text(encoding="utf-8"))
    for path in list(visual["spell_diagrams"].values()) + list(visual["stack_diagrams"].values()) + [visual["ward_diagram"]]:
        full = ROOT / path
        assert full.exists()
        text = full.read_text(encoding="utf-8")
        assert "<svg" in text
        assert "role=\"img\"" in text
        assert "check before cast" not in text
        assert "artifact gate" not in text
    for path in [ROOT / "chapters" / "05-coil-inspection.qmd", ROOT / "chapters" / "08-stackcraft.qmd"]:
        assert "Diagram placeholder" not in path.read_text(encoding="utf-8")


def test_adoption_evidence_contract_and_template_exist() -> None:
    evidence = json.loads((ROOT / "data" / "adoption_evidence.json").read_text(encoding="utf-8"))
    assert evidence["external_status"]["external_reports_published"] == 0
    assert "Do not fabricate external adoption" in evidence["external_status"]["policy"]
    assert {report["provenance"] for report in evidence["reports"]} == {"project-owned"}
    assert len(evidence["reports"]) >= 3

    template = json.loads((ROOT / "examples" / "adoption" / "adoption-report-template.json").read_text(encoding="utf-8"))
    for field in evidence["report_template"]["required_fields"]:
        assert template[field]
    assert template["provenance"] in evidence["report_template"]["provenance_values"]
    assert (ROOT / "adoption" / "evidence.qmd").exists()


def test_install_assets_dry_run_and_write() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        dry_run = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "install_assets.py"),
                "--target",
                "codex",
                "--dest",
                str(SCRATCH),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert dry_run.returncode == 0, dry_run.stderr
        assert "dry-run: exports/codex/safe-refactoring.md" in dry_run.stdout
        assert not (SCRATCH / "exports" / "codex" / "safe-refactoring.md").exists()

        written = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "install_assets.py"),
                "--target",
                "codex",
                "--dest",
                str(SCRATCH),
                "--write",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert written.returncode == 0, written.stderr
        installed = SCRATCH / "exports" / "codex" / "safe-refactoring.md"
        assert installed.exists()
        assert "spell.safe-refactoring.v1" in installed.read_text(encoding="utf-8")

        claude = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "install_assets.py"),
                "--target",
                "claude-code",
                "--dest",
                str(SCRATCH),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert claude.returncode == 0, claude.stderr
        assert "dry-run: exports/claude-code/skills/safe-refactoring.md" in claude.stdout
    finally:
        remove_scratch(SCRATCH)


def test_public_intake_issue_templates_exist() -> None:
    adoption = (ROOT / ".github" / "ISSUE_TEMPLATE" / "adoption-report.yml").read_text(encoding="utf-8")
    correction = (ROOT / ".github" / "ISSUE_TEMPLATE" / "canon-correction.yml").read_text(encoding="utf-8")
    audit = (ROOT / ".github" / "ISSUE_TEMPLATE" / "canon-audit-decision.yml").read_text(encoding="utf-8")
    assert "Adoption evidence report" in adoption
    assert "Failure or friction" in adoption
    assert "Canon correction" in correction
    assert "semantic change" in correction
    assert "Canon audit decision" in audit
    assert "Evidence checked" in audit
