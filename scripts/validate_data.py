#!/usr/bin/env python3
"""Validate generated Software Grimoire data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPLETION_STATUSES = {"authored", "stub", "needs_shadow", "needs_sense"}
FORCE_SOURCES = {"major-canon", "pocket-canon", "master-lexicon"}
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
            "is_stub",
            "major",
            "pocket",
            "source",
            "force_source",
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
    if summary.get("authored_entries") != len(lexicon) or summary.get("stub_entries") != 0:
        fail(errors, "Canon quality report must show the full lexicon authored with zero stubs")
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
    if len(spells) != 6:
        fail(errors, f"Expected 6 spells, found {len(spells)}")
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
    if len(stacks) != 6:
        fail(errors, f"Expected 6 stacks, found {len(stacks)}")
    return stacks


def main() -> int:
    errors: list[str] = []
    houses = validate_houses(errors)
    lexicon = validate_lexicon(errors, houses)
    validate_major_and_pocket(errors, lexicon)
    validate_canon_quality(errors, lexicon)
    spells = validate_spells(errors, lexicon)
    validate_stacks(errors, lexicon, spells)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
