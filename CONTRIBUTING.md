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
- New spells need an output contract, verification clause, and failure behavior.
- New stacks need concrete handoff artifacts, guards, and exit rules.
- Loops need measurable termination criteria.
- Recursive stacks need a base case.
- Metaphor cannot substitute for technical content.

## Local Checks

Run:

```bash
make all
```

Before proposing a change, make sure validation and Quarto rendering both pass.

