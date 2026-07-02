#!/usr/bin/env python3
"""Build the Software Grimoire Quarto project from source extracts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MD = ROOT / "source_extracts" / "software_magic_grimoire_v3_public_release.md"
POCKET_MD = ROOT / "source_extracts" / "pocket_grimoire_software_spellcraft_final.md"
STACKS_MD = ROOT / "source_extracts" / "software_spellcraft_addendum_on_stacked_spells.md"


HOUSE_SPECS = [
    ("architecture-abstraction-and-design", "Architecture, Abstraction, and Design", 1, 112),
    ("language-semantics-and-formal-shape", "Language, Semantics, and Formal Shape", 113, 249),
    ("data-state-and-representation", "Data, State, and Representation", 250, 371),
    ("transformation-algorithms-and-working-verbs", "Transformation, Algorithms, and Working Verbs", 372, 511),
    ("control-flow-coordination-and-temporal-logic", "Control Flow, Coordination, and Temporal Logic", 512, 608),
    ("runtime-memory-and-execution", "Runtime, Memory, and Execution", 609, 684),
    ("systems-programming-and-operating-system-words", "Systems Programming and Operating-System Words", 685, 770),
    ("networking-and-distributed-systems", "Networking and Distributed Systems", 771, 886),
    ("databases-persistence-and-time-binding-words", "Databases, Persistence, and Time-Binding Words", 887, 968),
    ("security-trust-and-warding-words", "Security, Trust, and Warding Words", 969, 1063),
    ("build-tooling-versioning-and-release", "Build, Tooling, Versioning, and Release", 1064, 1139),
    ("testing-verification-and-observability", "Testing, Verification, and Observability", 1140, 1210),
    ("hardware-embedded-and-performance-near-words", "Hardware, Embedded, and Performance-Near Words", 1211, 1290),
    ("interface-ux-and-human-facing-words", "Interface, UX, and Human-Facing Words", 1291, 1350),
    ("promptcraft-ai-oriented-engineering-and-spell-structure", "Promptcraft, AI-Oriented Engineering, and Spell Structure", 1351, 1420),
    ("guarantee-words-quality-attributes-and-behavioral-adjectives", "Guarantee Words, Quality Attributes, and Behavioral Adjectives", 1421, 1512),
    ("failure-words-pathologies-and-counter-spells", "Failure Words, Pathologies, and Counter-Spells", 1513, 1582),
    ("compound-forms-prefixes-suffixes-and-naming-runes", "Compound Forms, Prefixes, Suffixes, and Naming Runes", 1583, 1645),
]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\{[^}]+\}", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def page(title: str, body: str, description: str | None = None) -> str:
    title = title.replace('"', '\\"')
    meta = ["---", f'title: "{title}"']
    if description:
        meta.append(f'description: "{description.replace(chr(34), chr(92) + chr(34))}"')
    meta.append("---")
    return "\n".join(meta) + "\n\n" + clean_markdown(body)


def clean_markdown(text: str) -> str:
    text = text.replace("Gödel", "Godel")
    text = text.replace("·", "-")
    text = re.sub(
        r'<img src="([^"]+)"[^>]*>',
        lambda m: "\n\n::: {.callout-note}\nDiagram placeholder from source document: `"
        + m.group(1)
        + "`.\n:::\n\n",
        text,
    )
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def section_between(text: str, start: str, end: str | None = None) -> str:
    s = text.index(start)
    e = text.index(end, s) if end else len(text)
    return text[s:e].strip()


def parse_entry_line(line: str):
    m = re.match(r"^\**\\\[(\d{4})\\\]\s*(.+?)(?:\*\*)?\s+[\u2014-]\s+(.+)$", line.strip())
    if not m:
        return None
    ident = int(m.group(1))
    term = m.group(2).replace("**", "").strip()
    gloss = m.group(3).strip()
    return ident, term, gloss


def split_term(term: str) -> tuple[str, str | None]:
    m = re.match(r"^(.*?)\s*\{([^}]+)\}$", term)
    if not m:
        return term.strip(), None
    return m.group(1).strip(), m.group(2).strip()


def canonical_stream(kind: str, record: dict) -> str:
    ignore = {"working_seal", "formal_sigil", "source_markdown"}
    parts = [kind.upper(), record.get("id", ""), f"v{record.get('version', 1)}"]
    for key in sorted(k for k in record if k not in ignore):
        parts.append(key.upper())
        value = record[key]
        if isinstance(value, (list, dict)):
            parts.append(json.dumps(value, sort_keys=True, ensure_ascii=False))
        else:
            parts.append(str(value))
    normalized = " ".join("|".join(parts).split())
    return normalized


def seal_for(kind: str, record: dict) -> dict:
    stream = canonical_stream(kind, record)
    digest = hashlib.sha256(stream.encode("utf-8")).hexdigest()[:10].upper()
    prefix = "spell" if kind == "spell" else "stack"
    name = record["id"].split(".")[1]
    return {
        "human_title": record["title"],
        "working_seal": f"{prefix}://{name}/{digest}",
        "formal_sigil": {
            "canonical_stream": stream,
            "digest_algorithm": "sha256-hex-truncated-10",
            "digest": digest,
        },
    }


def build_houses() -> list[dict]:
    houses = []
    for slug, name, start, end in HOUSE_SPECS:
        houses.append(
            {
                "id": slug,
                "name": name,
                "start": start,
                "end": end,
                "range": f"{start:04d}-{end:04d}",
                "expected_count": end - start + 1,
            }
        )
    return houses


def house_for_id(houses: list[dict], ident: int) -> dict:
    for house in houses:
        if house["start"] <= ident <= house["end"]:
            return house
    raise ValueError(f"No house for id {ident}")


def parse_major_entries(public_text: str) -> dict[int, dict]:
    block = section_between(public_text, "## The Fifty World-Running Words", "## Proof by Difference")
    current_cluster = None
    entries = {}
    for line in block.splitlines():
        if line.startswith("## ") and "World-Running" not in line:
            current_cluster = line[3:].strip()
        parsed = parse_entry_line(line)
        if parsed:
            ident, term, gloss = parsed
            entries[ident] = {
                "id": ident,
                "term": split_term(term)[0],
                "sense": split_term(term)[1],
                "cluster": current_cluster,
                "expanded_gloss": gloss,
            }
    return entries


def parse_pocket_entries(pocket_text: str) -> dict[int, dict]:
    block = section_between(pocket_text, "# VI. Pocket Lexicon of 300 High-Force Runes", "# Closing Note")
    current_house = None
    entries = {}
    for line in block.splitlines():
        if line.startswith("## "):
            current_house = line[3:].split(" - ")[0].strip()
        parsed = parse_entry_line(line)
        if parsed:
            ident, term, gloss = parsed
            entries[ident] = {
                "id": ident,
                "term": split_term(term)[0],
                "sense": split_term(term)[1],
                "house_label": current_house,
                "pocket_gloss": gloss,
            }
    return entries


def parse_lexicon(public_text: str, houses: list[dict], major: dict[int, dict], pocket: dict[int, dict]) -> list[dict]:
    block = section_between(public_text, "# VIII. The Lexicon of Houses", "# IX. Closing Note")
    house_names = {h["name"]: h for h in houses}
    current_house = None
    entries = []
    for line in block.splitlines():
        if line.startswith("# ") and not line.startswith("# VIII"):
            current_house = house_names.get(line[2:].strip())
        parsed = parse_entry_line(line)
        if not parsed:
            continue
        ident, raw_term, gloss = parsed
        surface, sense = split_term(raw_term)
        house = current_house or house_for_id(houses, ident)
        shadow = None
        force = gloss
        if "Shadow:" in gloss:
            force, shadow = [part.strip() for part in gloss.split("Shadow:", 1)]
        entry = {
            "id": ident,
            "sigil": f"{ident:04d}",
            "term": surface,
            "raw_term": raw_term,
            "sense": sense,
            "house": house["id"],
            "house_name": house["name"],
            "summary": gloss,
            "force": force,
            "shadow": shadow,
            "status": "canonical",
            "major": ident in major,
            "pocket": ident in pocket,
            "source": "software_magic_grimoire_v3_public_release",
        }
        if ident in major:
            entry["major_cluster"] = major[ident]["cluster"]
            entry["expanded_gloss"] = major[ident]["expanded_gloss"]
        if ident in pocket:
            entry["pocket_gloss"] = pocket[ident]["pocket_gloss"]
        entries.append(entry)
    return entries


def extract_named_sections(text: str, titles: list[str]) -> dict[str, str]:
    result = {}
    for idx, title in enumerate(titles):
        start = text.index(title)
        end = text.index(titles[idx + 1], start) if idx + 1 < len(titles) else len(text)
        result[title] = text[start:end].strip()
    return result


def parse_spell_limb_text(section: str) -> dict[str, str]:
    labels = [
        "ROLE:",
        "OBJECTIVE:",
        "CONTEXT:",
        "CONSTRAINTS:",
        "PROCEDURE:",
        "OUTPUT CONTRACT:",
        "VERIFICATION:",
        "FAILURE BEHAVIOR:",
    ]
    positions = []
    for label in labels:
        m = re.search(rf"(?m)^{re.escape(label)}\s*$", section)
        if m:
            positions.append((m.start(), m.end(), label))
    limbs = {}
    for idx, (start, end, label) in enumerate(positions):
        next_start = positions[idx + 1][0] if idx + 1 < len(positions) else len(section)
        key = label.lower().replace(":", "").replace(" ", "_")
        limbs[key] = section[end:next_start].strip()
    return limbs


def build_spells(public_text: str) -> list[dict]:
    titles = [
        "## Spell of Safe Refactoring",
        "## Spell of Bug Diagnosis from Logs",
        "## Spell of API Design",
        "## Spell of Migration Without Data Loss",
        "## Spell of Test Generation",
        "## Spell of Performance Tuning",
    ]
    block = section_between(public_text, "## Spell of Safe Refactoring", "# VII. The Public Canon")
    sections = extract_named_sections(block, titles)
    use_when = {
        "safe-refactoring": "Use when code quality must improve while public behavior stays fixed.",
        "bug-diagnosis-from-logs": "Use when logs are available but the failure mechanism is still uncertain.",
        "api-design": "Use when designing a public or durable JSON API surface.",
        "migration-without-data-loss": "Use when stored reality must change shape without losing correctness.",
        "test-generation": "Use when behavior needs focused tests and edge-case coverage.",
        "performance-tuning": "Use when latency or throughput needs disciplined measurement before optimization.",
    }
    spells = []
    for title, body in sections.items():
        clean_title = title.replace("## ", "").strip()
        slug = slugify(clean_title.replace("Spell of ", ""))
        limbs = parse_spell_limb_text(body)
        record = {
            "id": f"spell.{slug}.v1",
            "title": clean_title,
            "version": 1,
            "cast_level": "full",
            "status": "canonical",
            "use_when": use_when[slug],
            "role": limbs.get("role", ""),
            "objective": limbs.get("objective", ""),
            "context": limbs.get("context", ""),
            "constraints": limbs.get("constraints", ""),
            "procedure": limbs.get("procedure", ""),
            "output_contract": limbs.get("output_contract", ""),
            "verification": limbs.get("verification", ""),
            "failure_behavior": limbs.get("failure_behavior", ""),
            "source": "software_magic_grimoire_v3_public_release",
            "source_markdown": body,
        }
        record.update(seal_for("spell", record))
        spells.append(record)
    return spells


def stack_record(slug: str, title: str, use_when: str, frames: list[dict], loop: dict | None, on_fail: str, why: str) -> dict:
    record = {
        "id": f"stack.{slug}.v1",
        "title": title,
        "version": 1,
        "status": "canonical",
        "enter": use_when,
        "inputs": ["Task context", "Relevant artifacts", "Constraints", "Verification expectations"],
        "frames": frames,
        "loop": loop,
        "on_fail": on_fail,
        "exit": frames[-1].get("advance_when", "Exit condition holds"),
        "why_it_works": why,
        "source": "software_spellcraft_addendum_on_stacked_spells",
    }
    record.update(seal_for("stack", record))
    return record


def build_stacks(stacks_text: str) -> list[dict]:
    return [
        stack_record(
            "code-generation-and-repair-loop",
            "Code Generation and Repair Loop",
            "Use when an AI system is helping write or modify software and generation should stay tied to execution evidence.",
            [
                {"step": 1, "spell": "Specify", "artifact": "Precise task statement, constraints, interfaces, and non-goals", "advance_when": "The target is testable"},
                {"step": 2, "spell": "Draft", "artifact": "Smallest plausible implementation or patch", "advance_when": "The code compiles in principle and names assumptions"},
                {"step": 3, "spell": "Run", "artifact": "Build, test, lint, or type-check output", "advance_when": "Actual failures are captured verbatim"},
                {"step": 4, "spell": "Diagnose", "artifact": "Likely cause and repair surface", "advance_when": "The diagnosis uses only emitted evidence"},
                {"step": 5, "spell": "Repair", "artifact": "Smallest diff addressing the diagnosed cause", "advance_when": "The patch is explicit"},
                {"step": 6, "spell": "Verify", "artifact": "Check results and residual risk", "advance_when": "Checks pass or residual risk is clearly bounded"},
            ],
            {"steps": [3, 4, 5, 6], "until": "Checks pass, error surface stabilizes without progress, or attempt budget is exhausted"},
            "Escalate with spec, code diff, failing output, diagnostic notes, and unresolved assumptions.",
            "It separates invention from judgment and binds repair to execution evidence.",
        ),
        stack_record(
            "bug-hunt-stack",
            "Bug-Hunt Stack",
            "Use when a defect is real but the cause is not yet localized.",
            [
                {"step": 1, "spell": "Reproduce", "artifact": "Stable reproduction", "advance_when": "The failure can be triggered on demand"},
                {"step": 2, "spell": "Localize", "artifact": "Smaller suspect surface", "advance_when": "The search field is smaller"},
                {"step": 3, "spell": "Instrument", "artifact": "Logs, traces, asserts, or counters", "advance_when": "New evidence can distinguish hypotheses"},
                {"step": 4, "spell": "Hypothesize", "artifact": "Likely failure mechanism", "advance_when": "Repair surface is stated"},
                {"step": 5, "spell": "Patch", "artifact": "Minimal change", "advance_when": "Patch matches current hypothesis"},
                {"step": 6, "spell": "Verify", "artifact": "Regression sweep", "advance_when": "Defect is gone and neighboring behavior is checked"},
            ],
            {"steps": [2, 3, 4, 5, 6], "until": "The bug is eliminated or evidence stops improving"},
            "Escalate to a deeper diagnostic stack and preserve reproduction, traces, and rejected hypotheses.",
            "It prevents patching before localization.",
        ),
        stack_record(
            "safe-refactor-stack",
            "Safe Refactor Stack",
            "Use when structure must improve without changing externally visible behavior.",
            [
                {"step": 1, "spell": "Freeze invariants", "artifact": "Behavior and data contracts", "advance_when": "What must not change is named"},
                {"step": 2, "spell": "Characterize", "artifact": "Tests or characterization evidence", "advance_when": "Current behavior is pinned"},
                {"step": 3, "spell": "Reshape", "artifact": "Structural patch", "advance_when": "Structure improves without intentional behavior change"},
                {"step": 4, "spell": "Static verify", "artifact": "Type, lint, and architecture check output", "advance_when": "Static checks pass"},
                {"step": 5, "spell": "Behavior verify", "artifact": "Characterization test output", "advance_when": "Behavior evidence stays green"},
                {"step": 6, "spell": "Review", "artifact": "Human review notes", "advance_when": "No leaky abstractions, drift, or renamed confusion remain"},
            ],
            {"steps": [3, 4, 5], "until": "Desired structure is reached without invariant breakage"},
            "Revert to the last green state and restate invariants more precisely.",
            "It puts behavioral contracts in front of structural ambition.",
        ),
        stack_record(
            "live-migration-stack",
            "Live Migration Stack",
            "Use when data, schemas, or infrastructure are changing in a live environment.",
            [
                {"step": 1, "spell": "Inventory", "artifact": "Dependency and blast-radius map", "advance_when": "Moving parts are known"},
                {"step": 2, "spell": "Prepare rollback", "artifact": "Backup, snapshot, flag, or dual-read path", "advance_when": "Reversal is real"},
                {"step": 3, "spell": "Expand compatibly", "artifact": "Backward-compatible new structure", "advance_when": "Old paths still work"},
                {"step": 4, "spell": "Backfill", "artifact": "New representation", "advance_when": "Old path is not cut off"},
                {"step": 5, "spell": "Compare parity", "artifact": "Parity report", "advance_when": "Old and new paths agree"},
                {"step": 6, "spell": "Cut over", "artifact": "Read or write switch", "advance_when": "Parity holds and rollback is live"},
                {"step": 7, "spell": "Observe", "artifact": "Live metrics and divergence samples", "advance_when": "Safety window remains stable"},
                {"step": 8, "spell": "Contract", "artifact": "Removed old paths", "advance_when": "Safety window closes cleanly"},
            ],
            {"steps": [5, 6, 7], "until": "Confidence is sufficient for cutover and contraction"},
            "Rollback immediately using the prepared boundary and preserve divergence samples.",
            "It forces reversibility to exist before forward motion becomes expensive.",
        ),
        stack_record(
            "release-gate-stack",
            "Release Gate Stack",
            "Use when a change set is already built and the question is whether it is ready to ship.",
            [
                {"step": 1, "spell": "Assemble candidate", "artifact": "Frozen release artifact and config", "advance_when": "Candidate is exact"},
                {"step": 2, "spell": "Quality gate", "artifact": "Tests, static checks, scans, and prerequisites", "advance_when": "Quality gate is green"},
                {"step": 3, "spell": "Stage deploy", "artifact": "Staging or canary deployment", "advance_when": "Limited environment is live"},
                {"step": 4, "spell": "Observe", "artifact": "Metrics, logs, traces, dashboards, and critical-flow results", "advance_when": "Signals remain green"},
                {"step": 5, "spell": "Promote or rollback", "artifact": "Release decision", "advance_when": "Broad release happens only if guard remains green"},
            ],
            None,
            "Rollback the candidate and open a repair stack instead of arguing from hope.",
            "It resists shipping by narrative alone.",
        ),
        stack_record(
            "recursive-decomposition-stack",
            "Recursive Decomposition Stack",
            "Use when the task is too large for one spell or one session and scope can shrink recursively.",
            [
                {"step": 1, "spell": "Define contract", "artifact": "Parent contract", "advance_when": "Boundary and obligations are clear"},
                {"step": 2, "spell": "Split into children", "artifact": "Smaller scopes", "advance_when": "Every child is smaller than parent scope"},
                {"step": 3, "spell": "Call child stack", "artifact": "Solved child scope", "advance_when": "Child base case or child verification passes"},
                {"step": 4, "spell": "Integrate", "artifact": "Integrated parent scope", "advance_when": "Children compose under parent contract"},
                {"step": 5, "spell": "System verify", "artifact": "Parent verification evidence", "advance_when": "Children are green and parent contract holds"},
            ],
            {"recursive": True, "base_case": "Scope is small enough to understand, implement, and verify in one bounded pass"},
            "Stop descent if child scopes do not shrink or contract consistency is lost.",
            "It lets one choreography operate at several scales while preserving contracts at every boundary.",
        ),
    ]


def qmd_table(rows: list[list[str]]) -> str:
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    lines = []
    header = "| " + " | ".join(str(rows[0][i]).ljust(widths[i]) for i in range(len(widths))) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(widths))) + " |"
    lines.extend([header, sep])
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(widths))) + " |")
    return "\n".join(lines)


def write_chapters(public_text: str, pocket_text: str, stacks_text: str) -> None:
    write_text(
        ROOT / "index.qmd",
        page(
            "The Grimoire of Software Magic Words",
            """Every software system is a ritual of names. The names that merely describe are ordinary. The names that constrain, invoke, transform, verify, or guard are magic.

This site is a public field manual and formal reference for AI-assisted software engineering. It teaches spells as structured instruction artifacts, stacks as reusable workflows, and runes as high-force engineering word-senses.

Start with the preface if you want the premise. Use the spell and stack libraries if you want working forms immediately. Use the lexicon when you need stable vocabulary for prompts, reviews, migrations, incidents, and release gates.
""",
        ),
    )
    preface = """This project was built from three source manuscripts: the long public release, the pocket field edition, and the stacked-spells addendum. The public site keeps the manuscript readable while moving reusable structures into data files, schemas, generated pages, and validation tooling.

The grimoire metaphor is practical. It marks a simple engineering fact: language in software is operative. Some words allocate responsibility, trigger checks, narrow output shape, name failure surfaces, and decide what kind of work an AI assistant should attempt.

The goal is not ornate prompting. The goal is bounded, verifiable work.
"""
    write_text(ROOT / "preface.qmd", page("Preface", preface))

    chapter_defs = [
        ("01-operative-language.qmd", "Operative Language", section_between(public_text, "# I. On the Nature", "# II. What a Spell Is")),
        ("02-what-a-spell-is.qmd", "What a Spell Is", section_between(public_text, "# II. What a Spell Is", "# III. How to Craft")),
        ("03-crafting-spells.qmd", "Crafting Spells", section_between(public_text, "# III. How to Craft", "# IV. Numeric")),
        ("04-sigils-canonicalization-and-seals.qmd", "Sigils, Canonicalization, and Seals", section_between(public_text, "# IV. Numeric", "# V. Coil")),
        ("05-coil-inspection.qmd", "Coil Inspection", section_between(public_text, "# V. Coil", "# VI. Example Spells")),
        ("06-field-spells.qmd", "Field Spells", section_between(public_text, "# VI. Example Spells", "# VII. The Public Canon")),
        ("07-public-canon.qmd", "The Public Canon", section_between(public_text, "# VII. The Public Canon", "# VIII. The Lexicon")),
        ("08-stackcraft.qmd", "Stackcraft", stacks_text),
        (
            "09-tooling-and-formalization.qmd",
            "Tooling and Formalization",
            """# Tooling and Formalization

The grimoire becomes more useful when its structures are machine-readable. This repository treats spells, stacks, houses, runes, and seals as data.

## Structured Layers

- `data/lexicon.json` stores the full sigil canon.
- `data/major_arcana.json` stores the 50 expanded public words.
- `data/pocket_runes.json` stores the 300-entry field canon.
- `data/spells.json` stores reusable spell templates.
- `data/stacks.json` stores repeatable workflow choreography.
- `schemas/` documents the expected shape of each data file.

## Validation

The validation script checks uniqueness, house ranges, required fields, spell limbs, stack handoffs, loop exits, recursive base cases, and broken references.

## Seals

Working seals are short stable digests derived from canonical streams. They are meant for commits, prompt registries, dashboards, and experiment logs. Formal sigils preserve the exact canonical stream for tooling.
""",
        ),
        (
            "10-living-practice.qmd",
            "Living Practice",
            """# Living Practice

The project should stay useful under real engineering pressure. A spell that cannot be adapted to a live task is just decorative prose. A stack that does not move artifacts is just a checklist.

## Operating Rules

- Keep prompts bounded by artifacts, invariants, constraints, output contracts, verification, and failure behavior.
- Keep stacks tied to handoff artifacts and explicit guards.
- Keep loops evidence-driven.
- Keep recursive workflows tied to smaller scopes and base cases.
- Keep lexicon entries connected to both force and shadow.

## Contribution Standard

New additions should improve the public canon, a working template, an executable schema, or a verification practice. The contribution guide explains how to propose additions without weakening the structure.
""",
        ),
    ]
    for filename, title, body in chapter_defs:
        write_text(ROOT / "chapters" / filename, page(title, body))

    pocket_quickstart = section_between(pocket_text, "# How to Use This Book", "# VI. Pocket Lexicon")
    write_text(ROOT / "reference" / "pocket-field-guide.qmd", page("Pocket Field Guide", pocket_quickstart))


def write_reference_pages(houses: list[dict], lexicon: list[dict], major: dict[int, dict], pocket: dict[int, dict], spells: list[dict], stacks: list[dict]) -> None:
    rows = [["House", "Range", "Entries"]]
    by_house = {h["id"]: [] for h in houses}
    for entry in lexicon:
        by_house[entry["house"]].append(entry)
    for house in houses:
        rows.append([f"[{house['name']}](house-{house['id']}.qmd)", house["range"], str(len(by_house[house["id"]]))])

    write_text(
        ROOT / "reference" / "index.qmd",
        page(
            "Reference",
            "The reference section is generated from structured data. Use it to browse the canon by house, spell, stack, cast level, and failure mode.\n\n"
            + qmd_table(rows)
            + "\n",
        ),
    )
    write_text(
        ROOT / "reference" / "cast-levels.qmd",
        page(
            "Cast Levels",
            """# Cast Levels

| Level | Form | Use |
|---|---|---|
| Quick cast | Role, objective, context, verify | Low-risk explanation, bounded review, small drafting task. |
| Working cast | Role, objective, context, constraints, output, verify | Daily software work: code edits, test writing, API sketches, benchmarking requests. |
| Full ritual | Role, objective, context, constraints, procedure, output, verify, failure | Migrations, refactors, incidents, security work, releases, and agentic pipelines. |

Minimum adequate ritual means paying only the structural cost required by the risk.
""",
        ),
    )
    write_text(
        ROOT / "reference" / "spell-skeleton.qmd",
        page(
            "Canonical Spell Skeleton",
            """# Canonical Spell Skeleton

```text
ROLE:
OBJECTIVE:
CONTEXT:
CONSTRAINTS:
PROCEDURE:
OUTPUT CONTRACT:
VERIFICATION:
FAILURE BEHAVIOR:
```

A risky spell should make every limb explicit. A smaller task may compress limbs, but verification should stay visible.
""",
        ),
    )
    write_text(
        ROOT / "reference" / "stack-grammar.qmd",
        page(
            "Stack Grammar",
            """# Stack Grammar

```text
STACK <Name> v<Version>
ENTER: <when this stack is appropriate>
IN: <artifacts or context required>
1. <Spell Name> [cast level]
OUT: <artifact emitted>
ADVANCE WHEN: <guard or transition rule>
LOOP <steps a..b> UNTIL <exit condition>
CALL <Stack Name>(<smaller scope>)
ON FAIL -> <Recovery Spell or Recovery Stack>
EXIT: <success condition>
```

Operators:

| Operator | Meaning |
|---|---|
| `->` | Then / hand off |
| `[guard]` | Gate before advance |
| `LOOP` | Repeat substack |
| `CALL` | Recursive descent |
| `ON FAIL` | Recovery path |
""",
        ),
    )
    write_text(
        ROOT / "reference" / "seals-and-sigils.qmd",
        page(
            "Seals and Sigils",
            """# Seals and Sigils

The public system separates three layers:

- Human title: readable name for conversation and documentation.
- Working seal: short digest for tools, commits, registries, and replay logs.
- Formal sigil: canonical stream and exact digest metadata.

The mathematics is not a burden for daily use. Humans should usually exchange titles and working seals. Tooling should preserve formal sigils.
""",
        ),
    )
    write_text(
        ROOT / "reference" / "failure-modes.qmd",
        page(
            "Failure Modes",
            """# Failure Modes

Common spell failures:

- Vague target.
- Hidden constraints.
- Missing artifact boundary.
- No output contract.
- No truth test.
- No fallback behavior.
- False certainty.
- Overbroad autonomy.

Common stack failures:

- Monolithic relapse.
- Invisible handoffs.
- Gate skipping.
- Spin loops.
- Infinite descent.
- Process bloat.
- Seal drift.
""",
        ),
    )

    major_rows = [["Sigil", "Term", "Cluster", "Gloss"]]
    for ident in sorted(major):
        item = major[ident]
        major_rows.append([f"{ident:04d}", item["term"], item.get("cluster") or "", item["expanded_gloss"]])
    write_text(ROOT / "reference" / "major-canon.qmd", page("The Fifty World-Running Words", qmd_table(major_rows)))

    pocket_rows = [["Sigil", "Term", "Gloss"]]
    for ident in sorted(pocket):
        item = pocket[ident]
        pocket_rows.append([f"{ident:04d}", item["term"], item["pocket_gloss"]])
    write_text(ROOT / "reference" / "pocket-canon.qmd", page("Pocket Canon", qmd_table(pocket_rows)))

    lex_rows = [["Sigil", "Term", "House", "Summary"]]
    for entry in lexicon:
        lex_rows.append([entry["sigil"], entry["term"], entry["house_name"], entry["summary"]])
    write_text(ROOT / "reference" / "lexicon.qmd", page("Master Lexicon", qmd_table(lex_rows)))

    for house in houses:
        entries = by_house[house["id"]]
        rows = [["Sigil", "Term", "Summary"]]
        for entry in entries:
            rows.append([entry["sigil"], entry["raw_term"], entry["summary"]])
        body = f"# {house['name']}\n\nRange: `{house['range']}`.\n\n" + qmd_table(rows)
        write_text(ROOT / "reference" / f"house-{house['id']}.qmd", page(house["name"], body))

    write_text(
        ROOT / "spells" / "index.qmd",
        page("Spell Library", "\n".join(f"- [{s['title']}]({slugify(s['title'].replace('Spell of ', ''))}.qmd)" for s in spells)),
    )
    for spell in spells:
        slug = slugify(spell["title"].replace("Spell of ", ""))
        body = f"# {spell['title']}\n\n**Working seal:** `{spell['working_seal']}`\n\n**Use when:** {spell['use_when']}\n\n" + spell["source_markdown"]
        write_text(ROOT / "spells" / f"{slug}.qmd", page(spell["title"], body))

    write_text(
        ROOT / "stacks" / "index.qmd",
        page("Stack Library", "\n".join(f"- [{s['title']}]({slugify(s['title'])}.qmd)" for s in stacks)),
    )
    for stack in stacks:
        rows = [["Step", "Spell", "Artifact", "Advance when"]]
        for frame in stack["frames"]:
            rows.append([str(frame["step"]), frame["spell"], frame["artifact"], frame["advance_when"]])
        loop = stack.get("loop")
        loop_text = ""
        if loop:
            loop_text = "\n\n## Loop or Recursion\n\n```json\n" + json.dumps(loop, indent=2, ensure_ascii=False) + "\n```\n"
        body = (
            f"# {stack['title']}\n\n"
            f"**Working seal:** `{stack['working_seal']}`\n\n"
            f"**Enter:** {stack['enter']}\n\n"
            + qmd_table(rows)
            + loop_text
            + f"\n\n## On Fail\n\n{stack['on_fail']}\n\n## Why It Works\n\n{stack['why_it_works']}\n"
        )
        write_text(ROOT / "stacks" / f"{slugify(stack['title'])}.qmd", page(stack["title"], body))


def write_quarto_config(houses: list[dict]) -> None:
    house_pages = [f"        - reference/house-{h['id']}.qmd" for h in houses]
    structure = {
        "chapters": [
            "index.qmd",
            "preface.qmd",
            "chapters/01-operative-language.qmd",
            "chapters/02-what-a-spell-is.qmd",
            "chapters/03-crafting-spells.qmd",
            "chapters/04-sigils-canonicalization-and-seals.qmd",
            "chapters/05-coil-inspection.qmd",
            "chapters/06-field-spells.qmd",
            "chapters/07-public-canon.qmd",
            "chapters/08-stackcraft.qmd",
            "chapters/09-tooling-and-formalization.qmd",
            "chapters/10-living-practice.qmd",
        ],
        "spell_pages": ["spells/index.qmd"] + [f"spells/{name}.qmd" for name in [
            "safe-refactoring",
            "bug-diagnosis-from-logs",
            "api-design",
            "migration-without-data-loss",
            "test-generation",
            "performance-tuning",
        ]],
        "stack_pages": ["stacks/index.qmd"] + [f"stacks/{name}.qmd" for name in [
            "code-generation-and-repair-loop",
            "bug-hunt-stack",
            "safe-refactor-stack",
            "live-migration-stack",
            "release-gate-stack",
            "recursive-decomposition-stack",
        ]],
        "reference_pages": [
            "reference/index.qmd",
            "reference/cast-levels.qmd",
            "reference/spell-skeleton.qmd",
            "reference/stack-grammar.qmd",
            "reference/seals-and-sigils.qmd",
            "reference/failure-modes.qmd",
            "reference/major-canon.qmd",
            "reference/pocket-canon.qmd",
            "reference/pocket-field-guide.qmd",
            "reference/lexicon.qmd",
        ] + [f"reference/house-{h['id']}.qmd" for h in houses],
    }
    write_json(ROOT / "book_structure.json", structure)
    refs = "\n".join(["        - " + p for p in structure["reference_pages"]])
    spells = "\n".join(["        - " + p for p in structure["spell_pages"]])
    stacks = "\n".join(["        - " + p for p in structure["stack_pages"]])
    chapters = "\n".join(["    - " + p for p in structure["chapters"][:2]])
    main_chapters = "\n".join(["        - " + p for p in structure["chapters"][2:]])
    q = f"""project:
  type: book
  output-dir: _site
  resources:
    - .nojekyll
    - data/*.json

lang: en-US

book:
  title: "The Grimoire of Software Magic Words"
  subtitle: "Operative Vocabulary, Prompt-Spells, and Stackcraft for AI-Assisted Software Engineering"
  author: "Corben Sorenson"
  site-url: "https://corbensorenson.github.io/software-grimoire/"
  repo-url: "https://github.com/corbensorenson/software-grimoire"
  repo-actions: [issue, source]
  chapters:
{chapters}
    - part: "Core Grimoire"
      chapters:
{main_chapters}
    - part: "Spell Library"
      chapters:
{spells}
    - part: "Stack Library"
      chapters:
{stacks}
    - part: "Reference"
      chapters:
{refs}

format:
  html:
    toc: true
    number-sections: true
    code-fold: true
    theme:
      - cosmo
      - assets/styles.scss
    link-external-newwindow: true

execute:
  freeze: auto
"""
    write_text(ROOT / "_quarto.yml", q)
    write_text(
        ROOT / "assets" / "styles.scss",
        """/*-- scss:defaults --*/
$font-family-sans-serif: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
$headings-font-weight: 650;

/*-- scss:rules --*/
.callout-note {
  border-radius: 6px;
}

table {
  font-size: 0.92rem;
}

td, th {
  vertical-align: top;
}
""",
    )
    write_text(
        ROOT / "scripts" / "sync_scaffold.py",
        """#!/usr/bin/env python3
\"\"\"Regenerate Quarto scaffold and generated pages.\"\"\"

from bootstrap_project import main

if __name__ == "__main__":
    main()
""",
    )


def main() -> None:
    public_text = PUBLIC_MD.read_text(encoding="utf-8")
    pocket_text = POCKET_MD.read_text(encoding="utf-8")
    stacks_text = STACKS_MD.read_text(encoding="utf-8")

    houses = build_houses()
    major = parse_major_entries(public_text)
    pocket = parse_pocket_entries(pocket_text)
    lexicon = parse_lexicon(public_text, houses, major, pocket)
    spells = build_spells(public_text)
    stacks = build_stacks(stacks_text)

    write_json(ROOT / "data" / "houses.json", houses)
    write_json(ROOT / "data" / "major_arcana.json", [major[k] for k in sorted(major)])
    write_json(ROOT / "data" / "pocket_runes.json", [pocket[k] for k in sorted(pocket)])
    write_json(ROOT / "data" / "lexicon.json", lexicon)
    write_json(ROOT / "data" / "spells.json", [{k: v for k, v in s.items() if k != "source_markdown"} for s in spells])
    write_json(ROOT / "data" / "stacks.json", stacks)
    write_json(
        ROOT / "data" / "seals.json",
        {
            "spells": [{"id": s["id"], "working_seal": s["working_seal"], "formal_sigil": s["formal_sigil"]} for s in spells],
            "stacks": [{"id": s["id"], "working_seal": s["working_seal"], "formal_sigil": s["formal_sigil"]} for s in stacks],
        },
    )

    write_chapters(public_text, pocket_text, stacks_text)
    write_reference_pages(houses, lexicon, major, pocket, spells, stacks)
    write_quarto_config(houses)

    print(f"Generated {len(lexicon)} lexicon entries, {len(major)} major entries, {len(pocket)} pocket runes.")
    print(f"Generated {len(spells)} spells and {len(stacks)} stacks.")


if __name__ == "__main__":
    main()

