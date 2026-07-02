#!/usr/bin/env python3
"""Smoke-test the local adoption CLI."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "grimoire.py"
SCRATCH = ROOT / "tmp" / "tests" / "grimoire-cli"


def remove_scratch(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_new_spell_validate_and_seal_round_trip() -> None:
    remove_scratch(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    spell_path = SCRATCH / "local-spell.json"

    try:
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
    finally:
        remove_scratch(SCRATCH)


def test_export_command_lists_generated_assets() -> None:
    exported = run_cli("export", "--target", "cursor")
    assert exported.returncode == 0, exported.stderr
    assert "exports/cursor/rules/safe-refactoring.mdc" in exported.stdout

    claude = run_cli("export", "--target", "claude-code")
    assert claude.returncode == 0, claude.stderr
    assert "exports/claude-code/skills/safe-refactoring.md" in claude.stdout


def test_install_command_dry_run_and_write() -> None:
    scratch = ROOT / "tmp" / "tests" / "grimoire-install"
    remove_scratch(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        dry_run = run_cli("install", "--target", "cursor", "--dest", str(scratch))
        assert dry_run.returncode == 0, dry_run.stderr
        assert "dry-run: exports/cursor/rules/safe-refactoring.mdc" in dry_run.stdout
        assert not (scratch / "exports" / "cursor" / "rules" / "safe-refactoring.mdc").exists()

        written = run_cli("install", "--target", "cursor", "--dest", str(scratch), "--write")
        assert written.returncode == 0, written.stderr
        assert (scratch / "exports" / "cursor" / "rules" / "safe-refactoring.mdc").exists()
    finally:
        remove_scratch(scratch)


def test_bench_import_command_validates_template() -> None:
    imported = run_cli("bench", "import", "examples/evaluations/manual-import-template.json")
    assert imported.returncode == 0, imported.stderr
    assert "Bench import record is valid" in imported.stdout


def test_bench_execution_command_runs_fixture() -> None:
    executed = run_cli("bench", "execution")
    assert executed.returncode == 0, executed.stderr
    assert "execution-results.json" in executed.stdout


def test_bench_hardness_command_runs_fixture() -> None:
    scratch = ROOT / "tmp" / "tests" / "grimoire-cli-hardness"
    remove_scratch(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    report = scratch / "grimoire-hardness.json"
    executed = run_cli("bench", "hardness", "--", "--write-report", str(report.relative_to(ROOT)))
    try:
        assert executed.returncode == 0, executed.stderr
        assert "grimoire-hardness.json" in executed.stdout
        assert report.exists()
    finally:
        remove_scratch(scratch)


def test_bench_hardness_model_command_is_exposed_without_running_model() -> None:
    helped = run_cli("bench", "hardness-model", "--", "--help")
    assert helped.returncode == 0, helped.stderr
    assert "run_hardness_model_surfaces.py" not in helped.stderr
    assert "--surface" in helped.stdout


def test_bench_hardness_import_command_validates_template() -> None:
    imported = run_cli("bench", "hardness-import", "examples/evaluations/hardness-v4/manual-import-template.json")
    assert imported.returncode == 0, imported.stderr
    assert "Hardness import record is valid" in imported.stdout
