"""Benchmark and adoption evidence template contracts."""

BENCH_MANUAL_IMPORT_TEMPLATE = {
    "surface_id": "manual-reviewer-import",
    "benchmark": "field-spell-evaluations",
    "case_slug": "safe-refactoring",
    "variant": "repaired",
    "fixture_path": "examples/evaluations/fixtures/safe-refactoring",
    "prompt_path": "examples/evaluations/runs/codex-cli-default/safe-refactoring/r01-repaired-prompt.md",
    "transcript_path": "examples/evaluations/runs/codex-cli-default/safe-refactoring/r01-repaired-output.md",
    "run_timestamp": "2026-07-02T04:25:50Z",
    "evaluator_notes": "Example import record using an existing project-owned run; reviewer-supplied imports must declare their own model/tool surface and redactions.",
    "provenance": "project-owned",
}

HARDNESS_MANUAL_IMPORT_TEMPLATE = {
    "schema_version": "4.0.0-hardness-manual-import",
    "surface_id": "manual-reviewer-import",
    "surface_label": "Reviewer supplied model/tool transcript",
    "surface_kind": "manual-import",
    "tool_name": "declared-by-reviewer",
    "tool_version": "declared-by-reviewer",
    "model_name": "declared-by-reviewer",
    "provenance": "project-owned",
    "evidence_class": "project_owned_model_run",
    "redaction_policy": "Public fixtures only; no secrets intentionally supplied.",
    "redaction_statement": "Template uses an existing public project-owned run. Real reviewer imports must declare any redactions.",
    "reviewer_id": "project-template",
    "reviewer_date": "2026-07-02",
    "benchmark": "hardness-v4-model-surface",
    "case_slug": "ambiguity-disabled-status",
    "variant": "weak",
    "repetition": 1,
    "run_timestamp": "2026-07-02T14:36:00Z",
    "fixture_path": "examples/evaluations/hardness-v4/fixtures/ambiguity-disabled-status",
    "prompt_path": "examples/evaluations/hardness-v4/model-runs/codex-cli-default/ambiguity-disabled-status/weak/r01-prompt.md",
    "transcript_path": "examples/evaluations/hardness-v4/model-runs/codex-cli-default/ambiguity-disabled-status/weak/r01-output.md",
    "artifact_root": "examples/evaluations/hardness-v4/model-runs/codex-cli-default/ambiguity-disabled-status/weak/r01-artifacts",
    "artifact_files": ["account_status.py"],
    "execution_command": "python -m pytest -q check_account_status.py",
    "safety_statement": "No private code, credentials, live jailbreak payloads, or device-global scratch paths are included.",
    "maintainer_decision": "pending",
    "evaluator_notes": "Template validates the import contract only. It does not count as reviewer-supplied evidence.",
}

HARDNESS_INTAKE_DECISION_TEMPLATE = {
    "schema_version": "4.0.0-hardness-intake-decision",
    "decision_id": "hardness-intake.manual-reviewer-import-template.v1",
    "generated_at": "pending-maintainer",
    "status": "pending-maintainer",
    "policy": "This template validates Bench v4 hardness-import acceptance structure. It does not count as cross-surface hardness evidence until a named maintainer accepts and publishes a real non-Codex, reviewer-supplied, or external-user bundle.",
    "import_path": "examples/evaluations/hardness-v4/manual-import-template.json",
    "surface_id": "manual-reviewer-import",
    "benchmark": "hardness-v4-model-surface",
    "case_slug": "ambiguity-disabled-status",
    "variant": "weak",
    "repetition": 1,
    "provenance": "project-owned",
    "maintainer": "",
    "review_date": "",
    "decision": "pending",
    "evidence_checked": [
        {
            "kind": "import_record",
            "path_or_url": "examples/evaluations/hardness-v4/manual-import-template.json",
            "notes": "Schema-valid project-owned template only; replace with a real reviewer/non-Codex import before acceptance.",
        },
        {
            "kind": "artifact",
            "path_or_url": "examples/evaluations/hardness-v4/model-surface-results.json",
            "notes": "Current accepted Bench v4 model-surface ledger; currently Codex-only.",
        },
    ],
    "publication": {
        "status": "not-published",
        "url_or_path": "",
    },
    "acceptance_notes": "Pending maintainer review; this is not accepted cross-surface hardness evidence.",
    "counts_as_cross_surface_hardness": False,
    "blocks_hardness_credit": True,
}

ADOPTION_REPORT_TEMPLATE = {
    "id": "adoption.example-reviewer-run.v1",
    "title": "Example Reviewer Adoption Report",
    "provenance": "reviewer-supplied",
    "task": "Describe the real task, repository, artifact boundary, and risk level.",
    "spell_or_stack_used": "spell.safe-refactoring.v1",
    "surface": "Name the AI tool, model surface, CLI, IDE, or manual review path used.",
    "artifact_produced": "Describe or link the code, design, test, review, or decision artifact produced.",
    "verification_performed": "Name the tests, review checks, commands, screenshots, or human review performed.",
    "time_cost": "Estimate setup time and runtime; include whether the structure was worth the overhead.",
    "failure_or_friction": "Record failures, overkill, unclear clauses, missing examples, or adoption friction.",
    "reuse_decision": "reuse | revise | retire | keep-as-reference",
    "notes": "Optional free-form notes. Do not include secrets or private customer data.",
}


def bench_manual_import_template() -> dict:
    return dict(BENCH_MANUAL_IMPORT_TEMPLATE)


def hardness_manual_import_template() -> dict:
    return dict(HARDNESS_MANUAL_IMPORT_TEMPLATE)


def hardness_intake_decision_template() -> dict:
    return dict(HARDNESS_INTAKE_DECISION_TEMPLATE)


def adoption_report_template() -> dict:
    return dict(ADOPTION_REPORT_TEMPLATE)
