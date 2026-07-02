You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Dirty Backfill Trap

Trap: A poisoned row looks parseable until timezone, partial-date, and unknown-value policy are made explicit.

Expected weak failure: Weak migration proposes direct conversion before dirty-row quarantine and parity checks.

USER REQUEST:
Migrate users.birthdate from string to date.
