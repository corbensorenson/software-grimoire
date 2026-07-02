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

SPELL_RUNES = {
    "safe-refactoring": [1172, 1088, 1152, 1445, 1430],
    "bug-diagnosis-from-logs": [1180, 1202, 1204, 598, 943],
    "api-design": [55, 347, 1461, 978, 1430],
    "migration-without-data-loss": [926, 943, 347, 1425, 1172],
    "test-generation": [1152, 1186, 1172, 1485, 1445],
    "performance-tuning": [1146, 825, 1281, 778, 615],
}

STACK_RUNES = {
    "code-generation-and-repair-loop": [1088, 1146, 1172, 1180, 1485],
    "bug-hunt-stack": [1180, 1204, 1172, 1562, 1445],
    "safe-refactor-stack": [1172, 1152, 1088, 1430, 1445],
    "live-migration-stack": [926, 943, 347, 1461, 1567],
    "release-gate-stack": [1073, 1086, 1146, 1180, 943],
    "recursive-decomposition-stack": [12, 55, 1172, 1437, 1445],
}

STACK_RELATED_SPELLS = {
    "code-generation-and-repair-loop": ["test-generation", "bug-diagnosis-from-logs", "safe-refactoring"],
    "bug-hunt-stack": ["bug-diagnosis-from-logs", "test-generation"],
    "safe-refactor-stack": ["safe-refactoring", "test-generation"],
    "live-migration-stack": ["migration-without-data-loss"],
    "release-gate-stack": ["bug-diagnosis-from-logs", "performance-tuning"],
    "recursive-decomposition-stack": ["api-design", "safe-refactoring", "test-generation"],
}

PROOF_CASES = {
    "safe-refactoring": {
        "title": "Refactor Without Breaking Behavior",
        "weak": "Clean up this Python module and make it nicer.",
        "repaired": """ROLE: Act as a senior Python engineer performing behavior-preserving refactoring.

OBJECTIVE: Remove duplication in the supplied module without changing public behavior.

CONTEXT: The module is imported by two API handlers and one CLI entry point. Existing tests cover only the happy path.

CONSTRAINTS: Do not change public function names, parameter order, return types, or raised exception classes. Touch only this module and its tests.

OUTPUT CONTRACT: Return a minimal patch plan, the proposed refactor, and tests that prove unchanged behavior.

VERIFICATION: State the invariants first; then show before/after test cases for edge inputs.

FAILURE BEHAVIOR: If the module boundary is too small for a safe refactor, say exactly what adjacent file must also move and why.""",
        "delta": "The repaired spell narrows blast radius, makes invariants reviewable, and forces proof through tests instead of relying on claims of cleanliness.",
    },
    "bug-diagnosis-from-logs": {
        "title": "Incident Diagnosis Without Fake Certainty",
        "weak": "Why are requests timing out?",
        "repaired": """ROLE: Act as a production incident analyst.

OBJECTIVE: Narrow the most likely causes of the timeout spike and say what evidence would distinguish them.

CONTEXT: A web API talks to Redis and PostgreSQL. Latency increased in the last hour. Logs are partial.

CONSTRAINTS: Do not claim a root cause unsupported by supplied evidence. Separate fact, hypothesis, and missing signal.

OUTPUT CONTRACT: Return ranked hypotheses, evidence already present, missing evidence, and the next three commands or dashboards to inspect.

VERIFICATION: Every factual claim must cite an observed symptom or be labeled hypothesis.

FAILURE BEHAVIOR: If the evidence is insufficient, say insufficient and identify the minimum additional signals needed.""",
        "delta": "The repaired spell prevents counterfeit certainty while still producing actionable next checks.",
    },
    "api-design": {
        "title": "API Design Without Hidden Compatibility Traps",
        "weak": "Design an API for billing.",
        "repaired": """ROLE: Act as a backend architect designing a public JSON API.

OBJECTIVE: Produce a boring, versionable billing API that supports invoices, payment attempts, refunds, and idempotent retries.

CONTEXT: Mobile and web clients; PostgreSQL storage; slow client upgrade cadence; OAuth-based auth.

CONSTRAINTS: Preserve backward compatibility, include pagination and error schema, prefer boring patterns over novelty.

OUTPUT CONTRACT: Return endpoint table, request/response examples, auth notes, idempotency notes, migration/versioning notes.

VERIFICATION: Call out race conditions, retry hazards, and compatibility risks.

FAILURE BEHAVIOR: If the resource model is underspecified, list assumptions explicitly before designing.""",
        "delta": "The repaired spell forces the design to expose compatibility, authorization, idempotency, and migration surfaces up front.",
    },
    "migration-without-data-loss": {
        "title": "Online Migration Without Data Loss",
        "weak": "Migrate users.birthdate from string to date.",
        "repaired": """ROLE: Act as a migration planner for a production PostgreSQL system.

OBJECTIVE: Move users.birthdate from VARCHAR to DATE without data loss and without breaking reads or writes during rollout.

CONTEXT: The table is large, writes continue during business hours, and some existing rows contain invalid or partial dates.

CONSTRAINTS: Use expand-and-contract. Preserve rollback until data quality is validated. Assume two application deploys are allowed.

OUTPUT CONTRACT: Return phased SQL and application steps: schema expand, dual write, backfill, validation queries, read switch, cleanup, rollback plan.

VERIFICATION: Include checks for invalid rows, null behavior, row-count parity, and post-cutover consistency.

FAILURE BEHAVIOR: If the data quality problem is too large for safe automatic cast, stop at quarantine and describe the manual decision boundary.""",
        "delta": "The repaired spell turns one risky command into a reversible campaign with validation and dirty-data handling.",
    },
    "test-generation": {
        "title": "Test Generation Without Overfitting To Implementation",
        "weak": "Write tests for this function.",
        "repaired": """ROLE: Act as a meticulous test engineer.

OBJECTIVE: Generate focused tests that capture observable behavior and important edge cases for the supplied function.

CONTEXT: Existing behavior is inferred from docstrings, examples, type hints, and current callers.

CONSTRAINTS: Prefer high-signal tests over high-count tests. Do not assert private implementation details unless no public behavior exists.

OUTPUT CONTRACT: Return inferred behaviors, ambiguities, the test file, and a rationale for each test group.

VERIFICATION: Include nominal cases, boundary cases, error cases, and one regression-style case.

FAILURE BEHAVIOR: If behavior is ambiguous, write characterization tests and label them as such.""",
        "delta": "The repaired spell makes tests protect behavior instead of freezing incidental implementation shape.",
    },
    "performance-tuning": {
        "title": "Performance Tuning Without Micro-Optimization Drift",
        "weak": "Make this faster.",
        "repaired": """ROLE: Act as a performance engineer.

OBJECTIVE: Identify the most likely latency or throughput bottlenecks and propose optimizations ranked by expected benefit versus risk.

CONTEXT: The service has a strict latency budget and runs on commodity cloud hardware. Profiling data may be incomplete.

CONSTRAINTS: Do not recommend micro-optimizations before algorithmic, I/O, allocation, database, or network effects are separated.

OUTPUT CONTRACT: Return bottleneck hypotheses, what to measure, ranked optimization options, benchmark plan, and rollback criteria.

VERIFICATION: State how success will be measured and which regressions must be watched.

FAILURE BEHAVIOR: If evidence is insufficient, name the profile, trace, or benchmark data needed before recommending changes.""",
        "delta": "The repaired spell forces measurement before optimization and keeps rollback criteria attached to speed claims.",
    },
}

HOUSE_SENSES = {
    "architecture-abstraction-and-design": "architecture",
    "language-semantics-and-formal-shape": "language",
    "data-state-and-representation": "data",
    "transformation-algorithms-and-working-verbs": "transformation",
    "control-flow-coordination-and-temporal-logic": "control",
    "runtime-memory-and-execution": "runtime",
    "systems-programming-and-operating-system-words": "operating-system",
    "networking-and-distributed-systems": "distributed-systems",
    "databases-persistence-and-time-binding-words": "database",
    "security-trust-and-warding-words": "security",
    "build-tooling-versioning-and-release": "release",
    "testing-verification-and-observability": "verification",
    "hardware-embedded-and-performance-near-words": "hardware",
    "interface-ux-and-human-facing-words": "interface-ux",
    "promptcraft-ai-oriented-engineering-and-spell-structure": "promptcraft",
    "guarantee-words-quality-attributes-and-behavioral-adjectives": "quality",
    "failure-words-pathologies-and-counter-spells": "failure",
    "compound-forms-prefixes-suffixes-and-naming-runes": "naming",
}

SHADOW_TEMPLATES = {
    "architecture-abstraction-and-design": "the boundary or abstraction can hide the failure that actually needs ownership.",
    "language-semantics-and-formal-shape": "the form can look precise while still carrying ambiguous or invalid meaning.",
    "data-state-and-representation": "stored or transported shape can drift from the world the code thinks it is reading.",
    "transformation-algorithms-and-working-verbs": "the transformation can silently lose information, reorder meaning, or amplify cost.",
    "control-flow-coordination-and-temporal-logic": "timing assumptions can turn coordination into stalls, races, retries, or dead paths.",
    "runtime-memory-and-execution": "runtime convenience can hide allocation, lifetime, contention, or stale-state costs.",
    "systems-programming-and-operating-system-words": "the host boundary can leak resources, permissions, descriptors, or platform assumptions.",
    "networking-and-distributed-systems": "distance can turn a local-looking operation into partial failure, delay, or split authority.",
    "databases-persistence-and-time-binding-words": "durable state can preserve the wrong truth longer than the code remembers why it changed.",
    "security-trust-and-warding-words": "misplaced trust can grant authority, expose secrets, or make identity look stronger than it is.",
    "build-tooling-versioning-and-release": "the release machinery can ship unreviewed drift faster than people can inspect it.",
    "testing-verification-and-observability": "the evidence surface can reward passing checks while missing the property that matters.",
    "hardware-embedded-and-performance-near-words": "physical constraints can turn clean software assumptions into timing, heat, or bandwidth failures.",
    "interface-ux-and-human-facing-words": "the human-facing surface can make the wrong action easier than the safe one.",
    "promptcraft-ai-oriented-engineering-and-spell-structure": "the model can satisfy the shape of the request while inventing unsupported substance.",
    "guarantee-words-quality-attributes-and-behavioral-adjectives": "the quality claim can become theater if no invariant or measurement backs it.",
    "failure-words-pathologies-and-counter-spells": "naming the failure can create false closure before the mechanism is actually understood.",
    "compound-forms-prefixes-suffixes-and-naming-runes": "the modifier can imply a guarantee the underlying design does not actually provide.",
}


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


def term_specific_shadow(entry: dict) -> str:
    template = SHADOW_TEMPLATES.get(entry["house"], "Shadow: the term can imply more structure than the artifact actually carries.")
    term = entry["term"]
    if entry["house"] == "failure-words-pathologies-and-counter-spells":
        return f"Shadow: treating {term} as the root cause too early can freeze the investigation around a symptom."
    if entry["house"] == "guarantee-words-quality-attributes-and-behavioral-adjectives":
        return f"Shadow: calling something {term} can hide the missing invariant, test, or operating envelope."
    if entry["house"] == "promptcraft-ai-oriented-engineering-and-spell-structure":
        return f"Shadow: {term} can become a prompt-shaped decoration unless it changes output, evidence, or tool behavior."
    if entry["house"] == "compound-forms-prefixes-suffixes-and-naming-runes":
        return f"Shadow: {term} can smuggle in a guarantee the base design has not earned."
    return template


def refresh_force_shadow(entry: dict) -> None:
    shadow = None
    force = entry["summary"]
    if "Shadow:" in entry["summary"]:
        force, shadow = [part.strip() for part in entry["summary"].split("Shadow:", 1)]
    entry["force"] = force.strip()
    entry["shadow"] = (shadow.strip() if shadow else entry.get("shadow") or term_specific_shadow(entry))


def add_completion_status(lexicon: list[dict], major: dict[int, dict], pocket: dict[int, dict]) -> list[dict]:
    original_counts = {}
    for entry in lexicon:
        original_counts[entry["summary"]] = original_counts.get(entry["summary"], 0) + 1

    for entry in lexicon:
        ident = entry["id"]
        if not entry.get("sense"):
            entry["sense"] = HOUSE_SENSES.get(entry["house"])

        original_summary = entry["summary"]
        was_duplicate = original_counts[original_summary] > 1

        if ident in major:
            entry["summary"] = major[ident]["expanded_gloss"]
            entry["force_source"] = "major-canon"
        elif ident in pocket:
            entry["summary"] = pocket[ident]["pocket_gloss"]
            entry["force_source"] = "pocket-canon"
        else:
            entry["force_source"] = "master-lexicon"

        refresh_force_shadow(entry)

        if ident in major or ident in pocket:
            entry["completion_status"] = "authored"
        elif was_duplicate:
            entry["completion_status"] = "stub"
        elif not entry.get("shadow"):
            entry["completion_status"] = "needs_shadow"
        elif not entry.get("sense"):
            entry["completion_status"] = "needs_sense"
        else:
            entry["completion_status"] = "authored"

        entry["is_stub"] = entry["completion_status"] == "stub"

    return lexicon


def completion_counts(entries: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        status = entry.get("completion_status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def count_summary_table(counts: dict[str, int]) -> str:
    order = ["authored", "stub", "needs_shadow", "needs_sense", "unknown"]
    rows = [["Status", "Count"]]
    for status in order:
        if counts.get(status):
            rows.append([status, str(counts[status])])
    return qmd_table(rows)


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


def rune_href(entry: dict, prefix: str = "") -> str:
    return f"{prefix}reference/house-{entry['house']}.qmd#rune-{entry['sigil']}"


def rune_link(entry: dict, prefix: str = "") -> str:
    label = f"{entry['sigil']} {entry['raw_term']}"
    return f"[{label}]({rune_href(entry, prefix)})"


def links_list(links: list[tuple[str, str]]) -> str:
    return "\n".join(f"- [{label}]({href})" for label, href in links)


def related_section(links: list[tuple[str, str]], heading: str = "Related Pages") -> str:
    if not links:
        return ""
    return f"\n\n## {heading}\n\n" + links_list(links) + "\n"


def rune_section(ids: list[int], lex_by_id: dict[int, dict], prefix: str = "", heading: str = "Related Runes") -> str:
    if not ids:
        return ""
    lines = []
    for ident in ids:
        entry = lex_by_id.get(ident)
        if entry:
            lines.append(f"- {rune_link(entry, prefix)} - {entry['force']}")
    if not lines:
        return ""
    return f"\n\n## {heading}\n\n" + "\n".join(lines) + "\n"


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
            "anchor": f"rune-{ident:04d}",
            "page": f"reference/house-{house['id']}.qmd",
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
            "runes": SPELL_RUNES.get(slug, []),
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
    stacks = [
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
    for stack in stacks:
        slug = stack["id"].split(".")[1]
        stack["runes"] = STACK_RUNES.get(slug, [])
        stack["related_spells"] = STACK_RELATED_SPELLS.get(slug, [])
        stack.update(seal_for("stack", stack))
    return stacks


def qmd_table(rows: list[list[str]]) -> str:
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    lines = []
    header = "| " + " | ".join(str(rows[0][i]).ljust(widths[i]) for i in range(len(widths))) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(widths))) + " |"
    lines.extend([header, sep])
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(widths))) + " |")
    return "\n".join(lines)


def proof_case_markdown(slug: str, case: dict, qmd: bool = False) -> str:
    repaired = "```text\n" + case["repaired"].strip() + "\n```"
    link = f"\n\n[Back to spell](../../spells/{slug}.qmd)\n" if not qmd else ""
    return f"""# {case['title']}

## Weak Request

{case['weak']}

## Repaired Spell

{repaired}

## Expected Delta

{case['delta']}
{link}"""


def write_proof_examples() -> None:
    for slug, case in PROOF_CASES.items():
        write_text(ROOT / "examples" / "weak-vs-repaired" / f"{slug}.qmd", page(case["title"], proof_case_markdown(slug, case)))


def write_chapters(public_text: str, pocket_text: str, stacks_text: str, lexicon: list[dict], houses: list[dict]) -> None:
    counts = completion_counts(lexicon)
    authored = counts.get("authored", 0)
    stub = counts.get("stub", 0)
    per_house_rows = [["House", "Authored", "Stub", "Needs Shadow", "Needs Sense"]]
    by_house = {h["id"]: [] for h in houses}
    for entry in lexicon:
        by_house[entry["house"]].append(entry)
    for house in houses:
        h_counts = completion_counts(by_house[house["id"]])
        per_house_rows.append(
            [
                house["name"],
                str(h_counts.get("authored", 0)),
                str(h_counts.get("stub", 0)),
                str(h_counts.get("needs_shadow", 0)),
                str(h_counts.get("needs_sense", 0)),
            ]
        )
    write_text(
        ROOT / "index.qmd",
        page(
            "The Grimoire of Software Magic Words",
            """Every software system is a ritual of names. The names that merely describe are ordinary. The names that constrain, invoke, transform, verify, or guard are magic.

This site is a public field manual and formal reference for AI-assisted software engineering. It teaches spells as structured instruction artifacts, stacks as reusable workflows, and runes as high-force engineering word-senses.

Start with [the guided reader path](reader_path.qmd) if you want an ordered route. Check [porting status](porting-status.qmd) if you want to see what moved from the source manuscripts into the public site. Use the spell and stack libraries if you want working forms immediately. Use the lexicon when you need stable vocabulary for prompts, reviews, migrations, incidents, and release gates.
""",
        ),
    )
    write_text(
        ROOT / "reader_path.qmd",
        page(
            "Guided Reader Path",
            """# Guided Reader Path

The site can be read three ways.

## Learn the Theory

1. [Preface](preface.qmd)
2. [Operative Language](chapters/01-operative-language.qmd)
3. [What a Spell Is](chapters/02-what-a-spell-is.qmd)
4. [Crafting Spells](chapters/03-crafting-spells.qmd)
5. [Sigils, Canonicalization, and Seals](chapters/04-sigils-canonicalization-and-seals.qmd)
6. [Coil Inspection](chapters/05-coil-inspection.qmd)

## Use It Today

1. [Cast Levels](reference/cast-levels.qmd)
2. [Canonical Spell Skeleton](reference/spell-skeleton.qmd)
3. [Spell Library](spells/index.qmd)
4. [Stack Library](stacks/index.qmd)
5. [Failure Modes](reference/failure-modes.qmd)

## Build On It

1. [Stack Grammar](reference/stack-grammar.qmd)
2. [Seals and Sigils](reference/seals-and-sigils.qmd)
3. [Tooling and Formalization](chapters/09-tooling-and-formalization.qmd)
4. [Term Index](reference/term-index.qmd)
5. [Master Lexicon](reference/lexicon.qmd)

## Reference Fast Path

- Start with [the 50 world-running words](reference/major-canon.qmd).
- Use [the 300-rune pocket canon](reference/pocket-canon.qmd) for daily vocabulary.
- Use [the canon map](reference/canon-map.qmd) when moving from a task to the right spell, stack, and rune cluster.
""",
        ),
    )
    write_text(
        ROOT / "porting-status.qmd",
        page(
            "Porting Status",
            f"""# Porting Status

The grimoire source corpus has been ported into the public Quarto site and repository.

| Source | Ported form | Status |
|---|---|---|
| `software_magic_grimoire_v3_public_release.docx` | Main book chapters, public canon, full lexicon data, generated reference pages | Structurally ported; lexicon authoring in progress |
| `pocket_grimoire_software_spellcraft_final.docx` | Pocket field guide, 300-rune pocket canon, quick-reference pages | Ported |
| `software_spellcraft_addendum_on_stacked_spells.docx` | Stackcraft chapter, stack grammar, six generated stack pages | Ported |

The first public seed was a complete structural port. The reader-linking pass improved the reading layer: guided paths, rune anchors, term index links, spell-to-rune links, stack-to-spell links, and canon maps. The current integrity layer is honest about lexicon authoring state.

## Lexicon Completion

The master lexicon currently has `{authored}` authored entries and `{stub}` stub entries.

{count_summary_table(counts)}

## Completion by House

{qmd_table(per_house_rows)}

## What Counts As Complete

- Source text is preserved.
- Every lexicon entry has a stable sigil, structured data record, generated reference page location, and direct anchor.
- Major and pocket canon entries link into the master house pages.
- Spell templates link to relevant runes and supporting reference pages.
- Stack workflows link to relevant spell templates, runes, and stack grammar.
- Stub lexicon entries are explicitly marked as stubs until they receive term-specific summaries, shadows, and sense disambiguation.
- The roadmap distinguishes archival completeness from reader experience completeness.
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

The grimoire becomes more useful when its structures are machine-readable. This repository treats spells, stacks, houses, runes, and seals as data rather than decorative prose. The book is the reader surface. The JSON files are the working surface. The schemas and tests are the guardrails that keep the two from drifting apart.

## Structured Layers

- `data/lexicon.json` stores the full sigil canon.
- `data/major_arcana.json` stores the 50 expanded public words.
- `data/pocket_runes.json` stores the 300-entry field canon.
- `data/spells.json` stores reusable spell templates.
- `data/stacks.json` stores repeatable workflow choreography.
- `data/seals.json` stores the public digest layer for spells and stacks.
- `schemas/` documents the expected shape of each data file.

The source manuscripts remain in `source_docs/` and the extraction layer remains in `source_extracts/`. Generated pages should be treated as build artifacts derived from those sources and from the structured data. When the same concept appears in several places, the durable version should live in data or in the generator, then render outward into the site.

## Data Contracts

The minimum useful data contract is not "has text." It is "has enough structure to be checked."

Lexicon entries carry:

- a stable numeric `id`;
- a zero-padded `sigil`;
- a normalized `term` and display `raw_term`;
- a `house` whose numeric range contains the entry;
- a generated `anchor` and page path;
- a summary, force, shadow, source, and completion status;
- major-canon and pocket-canon membership flags.

Spells carry:

- title, version, status, and cast level;
- the eight working limbs: role, objective, context, constraints, procedure, output contract, verification, and failure behavior;
- referenced runes;
- working seal and formal sigil.

Stacks carry:

- title, version, status, entry condition, exit condition, and failure behavior;
- ordered frames with handoff artifacts and advance conditions;
- related spell slugs and supporting runes;
- optional loop or recursion metadata;
- working seal and formal sigil.

## Validation

The validation script checks uniqueness, house ranges, required fields, completion status, spell limbs, stack handoffs, loop exits, recursive base cases, and broken references. The tests add schema conformance, seal stability, and rendered internal-link auditing. These checks are intentionally plain: the project should be easy to clone, regenerate, inspect, and trust.

Validation should prevent four kinds of drift:

- **Shape drift:** a required field disappears or changes type.
- **Reference drift:** a spell, stack, rune, anchor, or page path points nowhere.
- **Canon drift:** a working seal changes without an intentional release note.
- **Integrity drift:** a scaffolded lexicon entry is presented as finished canon.

The current lexicon integrity layer is deliberately honest. Major and pocket entries are authored canon. Remaining scaffold entries are marked as stubs until they receive term-specific summaries, shadows, and sense disambiguation.

## Seals

Working seals are short stable digests derived from canonical streams. They are meant for commits, prompt registries, dashboards, and experiment logs. Formal sigils preserve the exact canonical stream for tooling.

A seal is not a security primitive. It is a change detector. If the canonical stream for a spell or stack changes, the seal should change. If a page is reformatted without changing the canonical stream, the seal should remain stable. This gives maintainers a practical way to distinguish editorial movement from behavioral movement.

## Registry and Replay

The natural next tool is a local spell registry. A registry entry should record:

- spell or stack id;
- version and working seal;
- input artifacts;
- model or assistant surface used;
- output artifact path;
- verification command or evidence;
- failure notes and repair path.

That registry makes replay possible. A team can ask whether a prompt worked once, whether it keeps working, which rune cluster improved it, and which output contract caught a bad answer. The public site does not need to run a large platform to support this practice. It needs stable data, stable seals, and examples that show how to record evidence.

## Evaluation Logs

Evaluation in this project should stay close to engineering evidence. A useful eval record compares a weak request with a repaired spell, then records the expected delta: fewer invented assumptions, clearer output shape, explicit verification, better failure handling, or safer execution plan. The [Proof by Difference](../reference/proof-by-difference.qmd) examples are the first public version of that evaluation layer.
""",
        ),
        (
            "10-living-practice.qmd",
            "Living Practice",
            """# Living Practice

The project should stay useful under real engineering pressure. A spell that cannot be adapted to a live task is just decorative prose. A stack that does not move artifacts is just a checklist. Living practice is the discipline of keeping the metaphor subordinate to engineering evidence.

## Operating Rules

- Keep prompts bounded by artifacts, invariants, constraints, output contracts, verification, and failure behavior.
- Keep stacks tied to handoff artifacts and explicit guards.
- Keep loops evidence-driven.
- Keep recursive workflows tied to smaller scopes and base cases.
- Keep lexicon entries connected to both force and shadow.

## Solo Use

For an individual practitioner, the fastest adoption path is:

1. Start with a weak request that you would normally send to an assistant.
2. Choose the closest field spell.
3. Fill only the limbs that affect risk.
4. Add one verification instruction.
5. Save the final prompt and result when it worked.

This is not meant to slow down simple work. It is meant to make expensive work legible before it runs. A quick cast is enough for low-risk explanation. A full ritual is appropriate when the work touches migrations, incidents, security, releases, or broad refactors.

## Team Use

For a team, the grimoire becomes useful when repeated work gets named. A prompt that solves an incident class should become a spell. A sequence that safely moves code through analysis, edit, tests, review, and release should become a stack. A term that repeatedly changes model behavior should become a rune candidate.

A team prompt registry should track:

- approved spell templates;
- current working seals;
- owner or review group;
- allowed artifact scopes;
- required verification commands;
- known failure modes;
- retirement notes.

The registry does not need to be heavy. A folder of versioned Markdown or JSON files is enough until the work demands more.

## Adoption Ladder

The practice should grow in this order:

1. Use the existing spells as examples.
2. Create local variants for repeated tasks.
3. Record weak-vs-repaired cases when a variant clearly improves output.
4. Promote stable variants into team templates.
5. Add stack choreography only after single spells become too small.
6. Add tooling only after humans already agree on the contract.

This order matters because premature tooling can fossilize vague habits. The formal layer should capture practice that already works, then make it easier to repeat.

## Contribution Standard

New additions should improve the public canon, a working template, an executable schema, or a verification practice. The contribution guide explains how to propose additions without weakening the structure.

Good contributions usually do one of these things:

- turn a vague prompt into a bounded spell;
- add an example with an expected verification delta;
- improve a stub lexicon entry into authored canon;
- add a stack that moves real artifacts through guarded steps;
- strengthen a schema or test without making contribution awkward.

Weak contributions usually add vocabulary without force, examples without evidence, or metaphor without a working contract.

## Canon Governance

The public canon should change slowly. New terms can be proposed freely, but canon promotion should require a useful force description, a failure shadow, a sense disambiguator, and at least one working example. A spell or stack change that changes behavior should update the seal and changelog. Editorial-only changes should not pretend to be behavioral releases.

The goal is a living book that can accept new practice without losing its spine.
""",
        ),
    ]
    chapter_links = {
        "01-operative-language.qmd": [
            ("The Fifty World-Running Words", "../reference/major-canon.qmd"),
            ("Master Lexicon", "../reference/lexicon.qmd"),
            ("Term Index", "../reference/term-index.qmd"),
        ],
        "02-what-a-spell-is.qmd": [
            ("Canonical Spell Skeleton", "../reference/spell-skeleton.qmd"),
            ("Cast Levels", "../reference/cast-levels.qmd"),
            ("Spell Library", "../spells/index.qmd"),
        ],
        "03-crafting-spells.qmd": [
            ("Failure Modes", "../reference/failure-modes.qmd"),
            ("Spell Library", "../spells/index.qmd"),
            ("Proof by Difference", "../reference/proof-by-difference.qmd"),
        ],
        "04-sigils-canonicalization-and-seals.qmd": [
            ("Seals and Sigils", "../reference/seals-and-sigils.qmd"),
            ("Tooling and Formalization", "../chapters/09-tooling-and-formalization.qmd"),
        ],
        "05-coil-inspection.qmd": [
            ("Canonical Spell Skeleton", "../reference/spell-skeleton.qmd"),
            ("Failure Modes", "../reference/failure-modes.qmd"),
        ],
        "06-field-spells.qmd": [
            ("Spell Library", "../spells/index.qmd"),
            ("Stack Library", "../stacks/index.qmd"),
            ("Related Runes", "../reference/canon-map.qmd"),
        ],
        "07-public-canon.qmd": [
            ("The Fifty World-Running Words", "../reference/major-canon.qmd"),
            ("Pocket Canon", "../reference/pocket-canon.qmd"),
            ("Term Index", "../reference/term-index.qmd"),
        ],
        "08-stackcraft.qmd": [
            ("Stack Grammar", "../reference/stack-grammar.qmd"),
            ("Stack Library", "../stacks/index.qmd"),
            ("Failure Modes", "../reference/failure-modes.qmd"),
        ],
        "09-tooling-and-formalization.qmd": [
            ("Seals and Sigils", "../reference/seals-and-sigils.qmd"),
            ("Proof by Difference", "../reference/proof-by-difference.qmd"),
            ("Canon Map", "../reference/canon-map.qmd"),
        ],
        "10-living-practice.qmd": [
            ("Contribution Guide", "https://github.com/corbensorenson/software-grimoire/blob/main/CONTRIBUTING.md"),
            ("Proof by Difference", "../reference/proof-by-difference.qmd"),
            ("Failure Modes", "../reference/failure-modes.qmd"),
        ],
    }
    for filename, title, body in chapter_defs:
        body = body + related_section(chapter_links.get(filename, []))
        write_text(ROOT / "chapters" / filename, page(title, body))

    pocket_quickstart = section_between(pocket_text, "# How to Use This Book", "# VI. Pocket Lexicon")
    write_text(ROOT / "reference" / "pocket-field-guide.qmd", page("Pocket Field Guide", pocket_quickstart))


def write_reference_pages(houses: list[dict], lexicon: list[dict], major: dict[int, dict], pocket: dict[int, dict], spells: list[dict], stacks: list[dict]) -> None:
    global_counts = completion_counts(lexicon)
    rows = [["House", "Range", "Entries"]]
    by_house = {h["id"]: [] for h in houses}
    lex_by_id = {entry["id"]: entry for entry in lexicon}
    for entry in lexicon:
        by_house[entry["house"]].append(entry)
    for house in houses:
        rows.append([f"[{house['name']}](house-{house['id']}.qmd)", house["range"], str(len(by_house[house["id"]]))])

    write_text(
        ROOT / "reference" / "index.qmd",
        page(
            "Reference",
            "The reference section is generated from structured data. Use it to browse the canon by house, spell, stack, cast level, and failure mode.\n\n"
            "- [Guided Reader Path](../reader_path.qmd)\n"
            "- [Canon Map](canon-map.qmd)\n"
            "- [Term Index](term-index.qmd)\n"
            "- [Master Lexicon](lexicon.qmd)\n\n"
            "## Lexicon Completion\n\n"
            + count_summary_table(global_counts)
            + "\n\n"
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
    proof_rows = [["Spell", "Case", "Weak Request", "Expected Delta"]]
    for slug, case in PROOF_CASES.items():
        spell_title = next((s["title"] for s in spells if s["id"].split(".")[1] == slug), slug)
        proof_rows.append(
            [
                f"[{spell_title}](../spells/{slug}.qmd)",
                f"[{case['title']}](../examples/weak-vs-repaired/{slug}.qmd)",
                case["weak"],
                case["delta"],
            ]
        )
    proof_body = """# Proof by Difference

Proof by Difference is the grimoire's evidence discipline. It compares a weak request and a repaired spell against the same task. The claim is not that the repaired spell guarantees a perfect answer. The claim is that it makes success obligations inspectable: artifact boundary, invariant, output contract, verification, and failure behavior.

Use each case as a replayable prompt-design test. If a future model or workflow makes the weak request perform as well as the repaired spell, record that. If the repaired spell fails, inspect which limb was underspecified.

Replay templates and the six-case evaluation matrix live in the repository's [evaluation examples](https://github.com/corbensorenson/software-grimoire/tree/main/examples/evaluations).

""" + qmd_table(proof_rows)
    write_text(ROOT / "reference" / "proof-by-difference.qmd", page("Proof by Difference", proof_body))

    major_rows = [["Sigil", "Term", "Cluster", "Gloss"]]
    for ident in sorted(major):
        item = major[ident]
        entry = lex_by_id[ident]
        major_rows.append([f"{ident:04d}", rune_link(entry, "../"), item.get("cluster") or "", item["expanded_gloss"]])
    write_text(ROOT / "reference" / "major-canon.qmd", page("The Fifty World-Running Words", qmd_table(major_rows)))

    pocket_rows = [["Sigil", "Term", "Gloss"]]
    for ident in sorted(pocket):
        item = pocket[ident]
        entry = lex_by_id[ident]
        pocket_rows.append([f"{ident:04d}", rune_link(entry, "../"), item["pocket_gloss"]])
    write_text(ROOT / "reference" / "pocket-canon.qmd", page("Pocket Canon", qmd_table(pocket_rows)))

    lex_rows = [["Sigil", "Term", "House", "Completion", "Summary"]]
    for entry in lexicon:
        lex_rows.append([entry["sigil"], rune_link(entry, "../"), f"[{entry['house_name']}](house-{entry['house']}.qmd)", entry["completion_status"], entry["summary"]])
    write_text(ROOT / "reference" / "lexicon.qmd", page("Master Lexicon", qmd_table(lex_rows)))

    term_rows = [["Term", "Sigil", "House", "Canon", "Completion"]]
    for entry in sorted(lexicon, key=lambda e: (e["term"].lower(), e["id"])):
        canon_status = ", ".join(label for label, flag in [("major", entry["major"]), ("pocket", entry["pocket"])] if flag) or "master"
        term_rows.append([rune_link(entry, "../"), entry["sigil"], entry["house_name"], canon_status, entry["completion_status"]])
    write_text(ROOT / "reference" / "term-index.qmd", page("Term Index", qmd_table(term_rows)))

    canon_map = """# Canon Map

Use this map to jump from intent to the right reading surface.

## If You Need To Ask An AI To Change Code

- Read [What a Spell Is](../chapters/02-what-a-spell-is.qmd).
- Use [Canonical Spell Skeleton](spell-skeleton.qmd).
- Start from [Spell of Safe Refactoring](../spells/safe-refactoring.qmd), [Spell of Test Generation](../spells/test-generation.qmd), or [Code Generation and Repair Loop](../stacks/code-generation-and-repair-loop.qmd).
- Relevant runes: {safe_refactor_runes}

## If You Need To Diagnose A Failure

- Use [Spell of Bug Diagnosis from Logs](../spells/bug-diagnosis-from-logs.qmd).
- Use [Bug-Hunt Stack](../stacks/bug-hunt-stack.qmd).
- Check [Failure Modes](failure-modes.qmd).
- Relevant runes: {bug_runes}

## If You Need To Change Stored Reality

- Use [Spell of Migration Without Data Loss](../spells/migration-without-data-loss.qmd).
- Use [Live Migration Stack](../stacks/live-migration-stack.qmd).
- Relevant runes: {migration_runes}

## If You Need To Ship

- Use [Release Gate Stack](../stacks/release-gate-stack.qmd).
- Check [Stack Grammar](stack-grammar.qmd).
- Relevant runes: {release_runes}

## If You Need Vocabulary

- Start with [The Fifty World-Running Words](major-canon.qmd).
- Use [Pocket Canon](pocket-canon.qmd) for daily vocabulary.
- Use [Term Index](term-index.qmd) when you know the word.
- Use [Master Lexicon](lexicon.qmd) when you know the sigil or house.
""".format(
        safe_refactor_runes=", ".join(rune_link(lex_by_id[i], "../") for i in [1172, 1088, 1152, 1445]),
        bug_runes=", ".join(rune_link(lex_by_id[i], "../") for i in [1180, 1204, 1562, 1546]),
        migration_runes=", ".join(rune_link(lex_by_id[i], "../") for i in [926, 943, 347, 1567]),
        release_runes=", ".join(rune_link(lex_by_id[i], "../") for i in [1073, 1086, 1180, 943]),
    )
    write_text(ROOT / "reference" / "canon-map.qmd", page("Canon Map", canon_map))

    for house in houses:
        entries = by_house[house["id"]]
        h_counts = completion_counts(entries)
        rows = [["Sigil", "Term", "Completion", "Summary"]]
        for entry in entries:
            term_label = f"[{entry['raw_term']}](#rune-{entry['sigil']})"
            if entry["completion_status"] == "stub":
                term_label = f"`STUB` {term_label}"
            rows.append([entry["sigil"], term_label, entry["completion_status"], entry["summary"]])
        details = []
        for entry in entries:
            badges = []
            if entry["major"]:
                badges.append("major canon")
            if entry["pocket"]:
                badges.append("pocket canon")
            badge_text = f" ({', '.join(badges)})" if badges else ""
            detail = [
                f"### [{entry['sigil']}] {entry['raw_term']} {{#rune-{entry['sigil']}}}",
                "",
                f"**Status:** {entry['status']}{badge_text}",
                "",
                f"**Completion:** {entry['completion_status']}",
                "",
                f"**Force:** {entry['force']}",
            ]
            if entry.get("shadow"):
                detail.extend(["", f"**Shadow:** {entry['shadow']}"])
            if entry.get("expanded_gloss") and entry["expanded_gloss"] != entry["summary"]:
                detail.extend(["", f"**Major canon note:** {entry['expanded_gloss']}"])
            if entry.get("pocket_gloss"):
                detail.extend(["", f"**Pocket gloss:** {entry['pocket_gloss']}"])
            details.append("\n".join(detail))
        body = (
            f"# {house['name']}\n\n"
            f"Range: `{house['range']}`.\n\n"
            "## Completion\n\n"
            + count_summary_table(h_counts)
            + "\n\n"
            "Use the summary table for scanning. Each row links to the detailed anchored entry below.\n\n"
            + qmd_table(rows)
            + "\n\n## Entries\n\n"
            + "\n\n".join(details)
        )
        write_text(ROOT / "reference" / f"house-{house['id']}.qmd", page(house["name"], body))

    write_text(
        ROOT / "spells" / "index.qmd",
        page(
            "Spell Library",
            "Use these as reusable working forms. Each spell page links back to relevant runes and reference pages.\n\n"
            + "\n".join(f"- [{s['title']}]({slugify(s['title'].replace('Spell of ', ''))}.qmd)" for s in spells),
        ),
    )
    for spell in spells:
        slug = slugify(spell["title"].replace("Spell of ", ""))
        body = (
            f"# {spell['title']}\n\n"
            f"**Working seal:** `{spell['working_seal']}`\n\n"
            f"**Use when:** {spell['use_when']}\n"
            + rune_section(spell.get("runes", []), lex_by_id, "../")
            + related_section(
                [
                    ("Canonical Spell Skeleton", "../reference/spell-skeleton.qmd"),
                    ("Cast Levels", "../reference/cast-levels.qmd"),
                    ("Failure Modes", "../reference/failure-modes.qmd"),
                    ("Proof by Difference Case", f"../examples/weak-vs-repaired/{slug}.qmd"),
                    ("Canon Map", "../reference/canon-map.qmd"),
                ]
            )
            + "\n"
            + spell["source_markdown"]
        )
        write_text(ROOT / "spells" / f"{slug}.qmd", page(spell["title"], body))

    write_text(
        ROOT / "stacks" / "index.qmd",
        page(
            "Stack Library",
            "Stacks turn isolated spells into repeatable operations with handoffs, guards, loops, and recovery paths.\n\n"
            + "\n".join(f"- [{s['title']}]({slugify(s['title'])}.qmd)" for s in stacks),
        ),
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
            + rune_section(stack.get("runes", []), lex_by_id, "../")
            + related_section(
                [(title.replace("-", " ").title(), f"../spells/{title}.qmd") for title in stack.get("related_spells", [])]
                + [
                    ("Stack Grammar", "../reference/stack-grammar.qmd"),
                    ("Failure Modes", "../reference/failure-modes.qmd"),
                    ("Canon Map", "../reference/canon-map.qmd"),
                ],
                heading="Related Spell Templates and References",
            )
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
            "reader_path.qmd",
            "porting-status.qmd",
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
        "proof_pages": [f"examples/weak-vs-repaired/{slug}.qmd" for slug in PROOF_CASES],
        "reference_pages": [
            "reference/index.qmd",
            "reference/cast-levels.qmd",
            "reference/spell-skeleton.qmd",
            "reference/stack-grammar.qmd",
            "reference/seals-and-sigils.qmd",
            "reference/failure-modes.qmd",
            "reference/proof-by-difference.qmd",
            "reference/canon-map.qmd",
            "reference/major-canon.qmd",
            "reference/pocket-canon.qmd",
            "reference/pocket-field-guide.qmd",
            "reference/term-index.qmd",
            "reference/lexicon.qmd",
        ] + [f"reference/house-{h['id']}.qmd" for h in houses],
    }
    write_json(ROOT / "book_structure.json", structure)
    refs = "\n".join(["        - " + p for p in structure["reference_pages"]])
    spells = "\n".join(["        - " + p for p in structure["spell_pages"]])
    stacks = "\n".join(["        - " + p for p in structure["stack_pages"]])
    proof_pages = "\n".join(["        - " + p for p in structure["proof_pages"]])
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
    - part: "Proof by Difference Cases"
      chapters:
{proof_pages}
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
    lexicon = add_completion_status(lexicon, major, pocket)
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

    write_chapters(public_text, pocket_text, stacks_text, lexicon, houses)
    write_proof_examples()
    write_reference_pages(houses, lexicon, major, pocket, spells, stacks)
    write_quarto_config(houses)

    print(f"Generated {len(lexicon)} lexicon entries, {len(major)} major entries, {len(pocket)} pocket runes.")
    print(f"Generated {len(spells)} spells and {len(stacks)} stacks.")


if __name__ == "__main__":
    main()
