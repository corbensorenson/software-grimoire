#!/usr/bin/env python3
"""Validate logical-conclusion acceptance status gates."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_all_roadmap_acceptance_criteria_are_tracked() -> None:
    status = load("data/logical_conclusion_status.json")
    criteria = status["criteria"]
    assert [item["id"] for item in criteria] == list(range(1, 91))
    assert status["summary"]["criteria_total"] == 90
    assert status["summary"]["proven"] == sum(1 for item in criteria if item["status"] == "proven")
    assert status["summary"]["pending_total"] == sum(1 for item in criteria if item["status"] != "proven")


def test_external_reality_gates_remain_honest() -> None:
    status = load("data/logical_conclusion_status.json")
    criteria = {item["id"]: item for item in status["criteria"]}

    assert criteria[69]["status"] == "pending_human"
    assert criteria[70]["status"] == "pending_human"
    assert criteria[72]["status"] == "pending_package_index"
    assert criteria[74]["status"] == "pending_external"
    assert criteria[79]["status"] == "pending_external"
    assert criteria[88]["status"] == "partial"
    for ident in [69, 70, 72, 74, 79, 88]:
        assert criteria[ident]["blockers"]


def test_logical_conclusion_evidence_paths_exist() -> None:
    status = load("data/logical_conclusion_status.json")
    records = list(status["criteria"]) + list(status["open_gates"])
    missing: list[str] = []
    for record in records:
        for evidence in record["evidence"]:
            if evidence["kind"] == "path" and not (ROOT / evidence["target"]).exists():
                missing.append(f"{record['id']} -> {evidence['target']}")
    assert not missing


def test_logical_conclusion_status_matches_current_external_counts() -> None:
    adoption = load("data/adoption_evidence.json")
    audit = load("data/canon_audit.json")
    hardness = load("examples/evaluations/hardness-v4/model-surface-results.json")
    status = load("data/logical_conclusion_status.json")
    criteria = {item["id"]: item for item in status["criteria"]}

    assert adoption["external_status"]["external_reports_published"] == 0
    assert criteria[74]["status"] != "proven"
    assert audit["status"] == "pending-human-maintainer-signoff"
    assert criteria[69]["status"] != "proven"
    assert criteria[70]["status"] != "proven"
    assert set(hardness["surfaces"]) == {"codex-cli-default"}
    assert criteria[79]["status"] != "proven"
