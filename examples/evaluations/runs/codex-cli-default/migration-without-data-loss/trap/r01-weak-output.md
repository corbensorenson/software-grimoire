This is underspecified for a safe migration.

Do **not** directly convert `users.birthdate` from string to date yet. The dirty-row policy has to be explicit first, because birthdates are calendar dates and dirty strings can look parseable until timezone, partial-date, and unknown-value handling are defined.

Missing requirements:

- Database/ORM migration system
- Existing `birthdate` formats in production
- Accepted canonical format going forward
- Timezone policy for datetime-like strings
- Partial-date policy for values like `1990` or `1990-05`
- Unknown-value policy for `unknown`, `N/A`, empty string, `0000-00-00`, etc.
- Whether `birthdate` may be `NULL`
- Whether original raw values must be retained
- Rollout constraints and rollback expectations

Safe migration shape:

1. Add a new nullable date column, e.g. `users.birthdate_date`.
2. Backfill only rows that match explicitly accepted full-date formats.
3. Quarantine dirty rows into a separate table/report with `user_id`, raw value, and failure reason.
4. Run parity checks:
   - total users unchanged
   - valid parsed count + quarantined count + null/empty count equals source count
   - sampled valid rows match expected calendar dates
   - no timezone-derived date shifts
5. Update reads/writes to use the new date column.
6. After verification, rename/drop the old string column in a later migration.

Policy examples that need confirmation:

```text
YYYY-MM-DD          -> accepted
datetime + timezone -> rejected or converted using explicit timezone rule
YYYY or YYYY-MM     -> quarantined unless partial dates are supported separately
unknown/N/A/empty   -> NULL or quarantined, depending on product policy
invalid dates       -> quarantined
```

Once those policies and the database stack are known, the actual migration can be written.
