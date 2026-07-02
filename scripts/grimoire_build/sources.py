"""Source manuscript loading for generated builds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceCorpus:
    public_text: str
    pocket_text: str
    stacks_text: str


def source_paths(root: Path) -> dict[str, Path]:
    extracts = root / "source_extracts"
    return {
        "public": extracts / "software_magic_grimoire_v3_public_release.md",
        "pocket": extracts / "pocket_grimoire_software_spellcraft_final.md",
        "stacks": extracts / "software_spellcraft_addendum_on_stacked_spells.md",
    }


def read_source_corpus(root: Path) -> SourceCorpus:
    paths = source_paths(root)
    return SourceCorpus(
        public_text=paths["public"].read_text(encoding="utf-8"),
        pocket_text=paths["pocket"].read_text(encoding="utf-8"),
        stacks_text=paths["stacks"].read_text(encoding="utf-8"),
    )
