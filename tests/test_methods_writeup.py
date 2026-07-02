#!/usr/bin/env python3
"""Validate the generated methods write-up keeps evidence limits visible."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_methods_writeup_foregrounds_nulls_and_limits() -> None:
    page = (ROOT / "reference" / "methods-structure-reviewability-warding.qmd").read_text(encoding="utf-8")
    assert "does not yet separate weak from repaired" in page
    assert "not model-provider evidence" in page
    assert "ties and regressions" in page
    assert "pending human maintainer signoff" in page
