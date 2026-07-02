"""Export bundle and library manifest contracts."""

from __future__ import annotations

from pathlib import Path


def library_bundle_specs(root: Path) -> dict[str, list[Path]]:
    return {
        "software-grimoire-prompts.zip": [root / "prompts"],
        "software-grimoire-codex-templates.zip": [root / "exports" / "codex"],
        "software-grimoire-cursor-rules.zip": [root / "exports" / "cursor" / "rules"],
        "software-grimoire-stacks.zip": [root / "exports" / "markdown" / "stacks", root / "prompts" / "stacks"],
    }


def library_asset_roots(root: Path) -> list[Path]:
    return [
        root / "prompts",
        root / "exports" / "markdown",
        root / "exports" / "codex",
        root / "exports" / "cursor",
        root / "exports" / "README.md",
    ]
