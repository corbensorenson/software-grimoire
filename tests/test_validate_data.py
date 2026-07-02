#!/usr/bin/env python3
"""Smoke-test wrapper for repository validation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_validate_data_script_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/validate_data.py"], cwd=ROOT, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
