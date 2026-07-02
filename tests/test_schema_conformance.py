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
