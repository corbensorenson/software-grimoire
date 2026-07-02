#!/usr/bin/env python3
"""Validate the usage-earned canon review queue."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_canon_review_queue_is_bounded_and_pending_human_review() -> None:
    queue = json.loads((ROOT / "data" / "canon_review_queue.json").read_text(encoding="utf-8"))
    usage = json.loads((ROOT / "data" / "rune_usage_graph.json").read_text(encoding="utf-8"))
    candidates = queue["batches"][0]["candidates"]

    assert 0 < len(candidates) <= 20
    assert queue["summary"]["source_candidates"] == usage["summary"]["canonical_review_candidates"]
    assert queue["summary"]["accepted_candidates"] == 0
    assert queue["summary"]["human_signoff_status"] == "pending-human-maintainer-signoff"
    assert all(item["decision"] == "pending-human-maintainer" for item in candidates)
    assert all(item["use_count"] >= 3 for item in candidates)
    assert all(item["usage_evidence"] for item in candidates)
