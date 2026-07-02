#!/usr/bin/env python3
"""Validate ward-science ablation evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ward_science_seed_has_ablation_and_new_shapes() -> None:
    data = json.loads((ROOT / "examples" / "jailbreak-resilience" / "ward-science-results.json").read_text(encoding="utf-8"))
    variants = data["ablation_case"]["variants"]
    assert {"constraints-only", "verification-only", "trust-boundary-only", "refusal-contract-only", "audit-only", "full-ward"} <= set(variants)
    assert variants["audit-only"]["attack_resistance"] < variants["trust-boundary-only"]["attack_resistance"]
    assert variants["refusal-contract-only"]["overrefusal_rate"] > variants["full-ward"]["overrefusal_rate"]
    assert len(data["additional_defanged_attack_shapes"]) >= 6
    assert data["payload_policy"] == "defanged-fixtures-only"
    assert "does not simulate model behavior" in data["policy"]
