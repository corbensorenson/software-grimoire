#!/usr/bin/env python3
"""Smoke-test the local adoption CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "grimoire.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_new_spell_validate_and_seal_round_trip(tmp_path: Path) -> None:
    spell_path = tmp_path / "local-spell.json"

    created = run_cli("new", "spell", str(spell_path))
    assert created.returncode == 0, created.stderr
    assert spell_path.exists()

    record = json.loads(spell_path.read_text(encoding="utf-8"))
    assert record["id"] == "spell.local-example.v1"
    assert record["working_seal"].startswith("spell://local-example/")

    validated = run_cli("validate", str(spell_path))
    assert validated.returncode == 0, validated.stderr
    assert "Validation passed" in validated.stdout

    sealed = run_cli("seal", str(spell_path))
    assert sealed.returncode == 0, sealed.stderr
    sealed_record = json.loads(sealed.stdout)
    assert sealed_record["working_seal"] == record["working_seal"]
    assert sealed_record["formal_sigil"]["digest"] == record["formal_sigil"]["digest"]


def test_export_command_lists_generated_assets() -> None:
    exported = run_cli("export", "--target", "cursor")
    assert exported.returncode == 0, exported.stderr
    assert "exports/cursor/rules/safe-refactoring.mdc" in exported.stdout
