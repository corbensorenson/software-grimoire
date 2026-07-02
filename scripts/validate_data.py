#!/usr/bin/env python3
"""Validate generated Software Grimoire data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    for entry in lexicon:
        for key in ["id", "sigil", "term", "raw_term", "house", "summary", "status", "source"]:
            if key not in entry or entry[key] in ("", None):
                fail(errors, f"Lexicon entry missing {key}: {entry.get('id')}")
        ident = entry["id"]
        if ident in ids:
            fail(errors, f"Duplicate lexicon id: {ident}")
        ids.add(ident)
        if entry["sigil"] != f"{ident:04d}":
            fail(errors, f"Bad sigil for lexicon id {ident}")
        house = house_by_id.get(entry["house"])
        if not house:
            fail(errors, f"Unknown house for lexicon id {ident}: {entry['house']}")
        elif not (house["start"] <= ident <= house["end"]):
            fail(errors, f"Lexicon id {ident} outside house range {house['range']}")
    if len(lexicon) != 1645:
        fail(errors, f"Expected 1645 lexicon entries, found {len(lexicon)}")
    if len(ids) != len(lexicon):
        fail(errors, "Lexicon ids are not unique")
    return lexicon


def validate_major_and_pocket(errors: list[str], lexicon: list[dict]) -> None:
    lex_ids = {e["id"] for e in lexicon}
    major = load("major_arcana.json")
    pocket = load("pocket_runes.json")
    if len(major) != 50:
        fail(errors, f"Expected 50 major canon entries, found {len(major)}")
    if len(pocket) != 300:
        fail(errors, f"Expected 300 pocket entries, found {len(pocket)}")
    for label, items in [("major", major), ("pocket", pocket)]:
        seen = set()
        for item in items:
            ident = item.get("id")
            if ident in seen:
                fail(errors, f"Duplicate {label} id: {ident}")
            seen.add(ident)
            if ident not in lex_ids:
                fail(errors, f"{label} id missing from lexicon: {ident}")


def validate_spells(errors: list[str]) -> list[dict]:
    spells = load("spells.json")
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
        "working_seal",
        "formal_sigil",
    ]
    ids = set()
    for spell in spells:
        for key in required:
            if key not in spell or spell[key] in ("", None):
                fail(errors, f"Spell {spell.get('id')} missing {key}")
        if spell["id"] in ids:
            fail(errors, f"Duplicate spell id: {spell['id']}")
        ids.add(spell["id"])
        if spell["cast_level"] == "full":
            for limb in ["role", "objective", "context", "constraints", "procedure", "output_contract", "verification", "failure_behavior"]:
                if not spell.get(limb):
                    fail(errors, f"Full spell {spell['id']} missing limb {limb}")
        if not re.match(r"^spell://[a-z0-9-]+/[A-F0-9]{10}$", spell.get("working_seal", "")):
            fail(errors, f"Bad spell seal: {spell.get('working_seal')}")
    if len(spells) != 6:
        fail(errors, f"Expected 6 spells, found {len(spells)}")
    return spells


def validate_stacks(errors: list[str]) -> list[dict]:
    stacks = load("stacks.json")
    ids = set()
    for stack in stacks:
        for key in ["id", "title", "version", "status", "enter", "frames", "on_fail", "exit", "working_seal", "formal_sigil"]:
            if key not in stack or stack[key] in ("", None, []):
                fail(errors, f"Stack {stack.get('id')} missing {key}")
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
    if len(stacks) != 6:
        fail(errors, f"Expected 6 stacks, found {len(stacks)}")
    return stacks


def main() -> int:
    errors: list[str] = []
    houses = validate_houses(errors)
    lexicon = validate_lexicon(errors, houses)
    validate_major_and_pocket(errors, lexicon)
    validate_spells(errors)
    validate_stacks(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

