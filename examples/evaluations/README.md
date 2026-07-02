# Evaluation Scaffolds

Use this folder for replayable comparisons between weak requests and structured
spells.

Start with:

- `evaluation-template.md` for one replayable run.
- `field-spell-eval-matrix.md` for the six public field-spell cases.

Each evaluation should include:

- Weak request.
- Repaired spell.
- Input context.
- Expected output contract.
- Verification rubric.
- Model/tool version.
- Result notes.

Suggested metrics:

- Instruction adherence.
- Artifact completeness.
- Verification quality.
- Hallucinated assumptions.
- Blast-radius control.
- Reversibility.
- Reviewer effort.

Minimum passing standard:

- The repaired spell must make at least one success obligation inspectable that
  the weak request left implicit.
- The output contract must be checkable by a reviewer who did not write the
  prompt.
- The result notes must separate observed behavior from interpretation.
