I can’t safely complete this migration from the given context. The key missing decisions are exactly the risky ones:

- Accepted source formats for `users.birthdate`
- Timezone policy for any timestamp-like strings
- Policy for partial dates like `YYYY`, `YYYY-MM`, or missing day/month
- Policy for unknown placeholders like `unknown`, `N/A`, empty string, `0000-00-00`
- Whether invalid/ambiguous rows should become `NULL`, be rejected, or be quarantined
- Database engine and migration framework
- Whether `birthdate` is nullable and whether app code already depends on string values

A safe migration should not directly cast the column. The correct shape is:

1. Add a new nullable date column, e.g. `birthdate_date`.
2. Backfill only rows that pass an explicit strict parser.
3. Quarantine dirty or ambiguous rows into a separate table with:
   - `user_id`
   - original `birthdate`
   - failure reason
   - migration batch timestamp
4. Run parity checks:
   - total row count unchanged
   - parsed row count + quarantined row count = original non-null source count
   - no unexpected null inflation
   - sampled valid dates match expected parsed values
5. Fix or approve quarantined rows according to explicit policy.
6. Switch application reads/writes to the new date column.
7. Add constraints only after parity passes.
8. Drop or rename the old string column in a later migration.

Until timezone, partial-date, and unknown-value policies are defined, the migration should stop at quarantine/parity design rather than converting data destructively.
