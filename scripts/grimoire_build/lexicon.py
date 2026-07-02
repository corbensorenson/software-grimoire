"""Shared lexicon quality helpers."""

from __future__ import annotations

import re


GENERATED_TEMPLATE_RE = re.compile(r" rune for .*use it when the artifact needs", re.IGNORECASE)


def generated_template_text(value: str | None) -> bool:
    if not value:
        return False
    lowered = value.lower()
    return (
        bool(GENERATED_TEMPLATE_RE.search(value))
        or (
            " rune for " in lowered
            and "use it when the artifact needs" in lowered
        )
        or value.strip().startswith("`")
    )


def semantic_counts(entries: list[dict]) -> dict[str, int]:
    counts = {"generated_draft": 0, "reviewed": 0, "canonical": 0, "deprecated": 0}
    for entry in entries:
        status = entry.get("semantic_status", "generated_draft")
        counts[status] = counts.get(status, 0) + 1
    return counts
