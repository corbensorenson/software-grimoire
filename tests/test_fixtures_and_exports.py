#!/usr/bin/env python3
"""Validate benchmark fixtures and generated installable exports."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


def test_install_assets_dry_run_and_write(tmp_path: Path) -> None:
    dry_run = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "install_assets.py"),
            "--target",
            "codex",
            "--dest",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert dry_run.returncode == 0, dry_run.stderr
    assert "dry-run: exports/codex/safe-refactoring.md" in dry_run.stdout
    assert not (tmp_path / "exports" / "codex" / "safe-refactoring.md").exists()

    written = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "install_assets.py"),
            "--target",
            "codex",
            "--dest",
            str(tmp_path),
            "--write",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert written.returncode == 0, written.stderr
    installed = tmp_path / "exports" / "codex" / "safe-refactoring.md"
    assert installed.exists()
    assert "spell.safe-refactoring.v1" in installed.read_text(encoding="utf-8")


def test_public_intake_issue_templates_exist() -> None:
    adoption = (ROOT / ".github" / "ISSUE_TEMPLATE" / "adoption-report.yml").read_text(encoding="utf-8")
    correction = (ROOT / ".github" / "ISSUE_TEMPLATE" / "canon-correction.yml").read_text(encoding="utf-8")
    assert "Adoption evidence report" in adoption
    assert "Failure or friction" in adoption
    assert "Canon correction" in correction
    assert "semantic change" in correction
