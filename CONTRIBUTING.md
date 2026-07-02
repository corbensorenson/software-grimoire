# Contributing

Contributions should strengthen the public canon without turning it into an
unstructured prompt dump.

## Contribution Types

- Rune correction or addition.
- Spell template addition.
- Stack workflow addition.
- Proof-by-difference case.
- Tooling or schema improvement.
- Documentation fix.

## Canon Rules

- New runes need a distinct word-sense, not only a synonym.
- Stub runes should move to `authored` only when they have term-specific force,
  shadow, and sense.
- New spells need an output contract, verification clause, and failure behavior.
- New stacks need concrete handoff artifacts, guards, and exit rules.
- Loops need measurable termination criteria.
- Recursive stacks need a base case.
- Metaphor cannot substitute for technical content.

## Source of Truth

- Generated `.qmd` reference, spell, stack, and house pages should be changed
  through `scripts/bootstrap_project.py` or structured data, then regenerated.
- Schema or seal changes should include matching validation and changelog notes.
- Proof by Difference cases should include a weak request, repaired spell, and
  expected delta.

## Local Checks

Run:

```bash
make all
```

Before proposing a change, make sure validation and Quarto rendering both pass.
