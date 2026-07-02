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


def adoption_report_template() -> dict:
    return dict(ADOPTION_REPORT_TEMPLATE)
