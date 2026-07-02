#!/usr/bin/env python3
"""Verify bootstrap generation is deterministic for committed artifacts."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKED_GENERATED = [
    "_quarto.yml",
    "book_structure.json",
    "data/lexicon.json",
    "data/canon_quality.json",
    "data/bench_v2.json",
    "data/adversarial_harness.json",
    "data/generator_architecture.json",
    "exports/library-manifest.json",
    "exports/checksums.sha256",
    "exports/bundles/software-grimoire-prompts.zip",
    "exports/bundles/software-grimoire-codex-templates.zip",
    "exports/bundles/software-grimoire-cursor-rules.zip",
    "exports/bundles/software-grimoire-stacks.zip",
]


def digest(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_bootstrap_generation_is_deterministic_for_core_outputs() -> None:
    before = {path: digest(path) for path in TRACKED_GENERATED}
    subprocess.run([sys.executable, "scripts/bootstrap_project.py"], cwd=ROOT, check=True)
    after = {path: digest(path) for path in TRACKED_GENERATED}
    assert before == after
