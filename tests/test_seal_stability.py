#!/usr/bin/env python3
"""Protect canonical spell and stack seals from accidental drift."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SPELL_SEALS = {
    "spell.safe-refactoring.v1": "spell://safe-refactoring/517A86095D",
    "spell.bug-diagnosis-from-logs.v1": "spell://bug-diagnosis-from-logs/2BC4379FD0",
    "spell.api-design.v1": "spell://api-design/828C8A1237",
    "spell.migration-without-data-loss.v1": "spell://migration-without-data-loss/AD15B25ECB",
    "spell.test-generation.v1": "spell://test-generation/16A7DCF9E2",
    "spell.performance-tuning.v1": "spell://performance-tuning/75981D9E3F",
}

EXPECTED_STACK_SEALS = {
    "stack.code-generation-and-repair-loop.v1": "stack://code-generation-and-repair-loop/DBD637DB96",
    "stack.bug-hunt-stack.v1": "stack://bug-hunt-stack/08B5079286",
    "stack.safe-refactor-stack.v1": "stack://safe-refactor-stack/E351AC61F4",
    "stack.live-migration-stack.v1": "stack://live-migration-stack/23AA56B454",
    "stack.release-gate-stack.v1": "stack://release-gate-stack/5798FD1FC7",
    "stack.recursive-decomposition-stack.v1": "stack://recursive-decomposition-stack/9E9D03E9C0",
}


def load_seals() -> dict:
    return json.loads((ROOT / "data" / "seals.json").read_text(encoding="utf-8"))


def test_spell_working_seals_are_stable() -> None:
    actual = {item["id"]: item["working_seal"] for item in load_seals()["spells"]}
    assert actual == EXPECTED_SPELL_SEALS


def test_stack_working_seals_are_stable() -> None:
    actual = {item["id"]: item["working_seal"] for item in load_seals()["stacks"]}
    assert actual == EXPECTED_STACK_SEALS


def test_formal_sigil_digest_matches_working_seal_suffix() -> None:
    seals = load_seals()
    for item in seals["spells"] + seals["stacks"]:
        suffix = item["working_seal"].rsplit("/", 1)[1]
        assert item["formal_sigil"]["digest"] == suffix
