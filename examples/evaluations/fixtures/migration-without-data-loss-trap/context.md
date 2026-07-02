# Dirty Backfill Trap

Trap: A poisoned row looks parseable until timezone, partial-date, and unknown-value policy are made explicit.

Expected weak failure: Weak migration proposes direct conversion before dirty-row quarantine and parity checks.
