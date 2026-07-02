#!/usr/bin/env python3
"""Validate benchmark fixtures and generated installable exports."""

from __future__ import annotations

import json
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
}
EXPECTED_STACKS = {
    "code-generation-and-repair-loop",
    "bug-hunt-stack",
    "safe-refactor-stack",
    "live-migration-stack",
    "release-gate-stack",
    "recursive-decomposition-stack",
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
