# Field Spell Evaluation Matrix

Use this matrix to replay the six public Proof by Difference cases across
models, tools, or prompt variants. Copy `evaluation-template.md` for each run.

| Spell | Case | Weak request | Primary expected delta | Rubric emphasis |
|---|---|---|---|---|
| `spell.safe-refactoring.v1` | `../weak-vs-repaired/safe-refactoring.qmd` | Clean up this Python module and make it nicer. | Invariants and blast radius become explicit. | Artifact boundary, invariants, verification |
| `spell.bug-diagnosis-from-logs.v1` | `../weak-vs-repaired/bug-diagnosis-from-logs.qmd` | Why are requests timing out? | Diagnosis separates observations from hypotheses. | Assumption control, verification, failure behavior |
| `spell.api-design.v1` | `../weak-vs-repaired/api-design.qmd` | Design an API for billing. | Compatibility, authorization, idempotency, and migration surfaces appear early. | Output contract, invariants, assumption control |
| `spell.migration-without-data-loss.v1` | `../weak-vs-repaired/migration-without-data-loss.qmd` | Migrate users.birthdate from string to date. | A risky command becomes a reversible campaign. | Failure behavior, verification, artifact boundary |
| `spell.test-generation.v1` | `../weak-vs-repaired/test-generation.qmd` | Write tests for this function. | Tests target behavior instead of incidental implementation. | Invariants, output contract, verification |
| `spell.performance-tuning.v1` | `../weak-vs-repaired/performance-tuning.qmd` | Make this faster. | Measurement precedes optimization and rollback criteria stay attached. | Verification, assumption control, failure behavior |

## Run Notes

- Keep weak and repaired runs on the same input context.
- Record the exact spell working seal.
- Preserve outputs verbatim in result notes or linked artifacts.
- Do not score a repaired spell as successful merely because it is longer.
- Treat a weak request as competitive if it produces equally inspectable
  obligations with less structure, then record that as a model/tool finding.
