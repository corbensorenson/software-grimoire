Do not run `ALTER TABLE users ALTER COLUMN birthdate_text TYPE DATE`; it is destructive and will fail or silently encode bad assumptions.

Use expand-and-contract:

```sql
-- 1. Expand
ALTER TABLE users ADD COLUMN birthdate DATE;

CREATE TABLE users_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY,
  birthdate_text TEXT,
  reason TEXT NOT NULL,
  quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Backfill only values with an explicit accepted format. For this fixture, ISO `YYYY-MM-DD` is safe; `04/12/1990` is ambiguous, `unknown`/empty/null need business handling, and `31/02/1990` is invalid.

```sql
-- Safe ISO backfill, preferably batched by id ranges in production.
UPDATE users
SET birthdate = birthdate_text::date
WHERE birthdate_text ~ '^\d{4}-\d{2}-\d{2}$'
  AND birthdate IS NULL;

-- Quarantine unresolved non-empty values.
INSERT INTO users_birthdate_quarantine (user_id, birthdate_text, reason)
SELECT id, birthdate_text, 'unparsed_or_ambiguous_birthdate'
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND lower(btrim(birthdate_text)) <> 'unknown'
  AND birthdate IS NULL
ON CONFLICT (user_id) DO NOTHING;
```

Deploy app dual-write, or add a compatibility trigger, so writes keep `birthdate_text` and `birthdate` in sync during the migration window. Keep rollback available by leaving `birthdate_text` untouched until validation passes.

Required validation before cutover:

```sql
SELECT count(*) AS dirty_birthdate_text
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND lower(btrim(birthdate_text)) <> 'unknown'
  AND birthdate IS NULL;

SELECT count(*) AS parsed_rows
FROM users
WHERE birthdate IS NOT NULL;
```

Cut over reads to `users.birthdate` only after dirty rows are quarantined or resolved and parity is accepted. Contract later in a separate migration: remove compatibility trigger/dual-write, then drop `birthdate_text`. Rollback remains simple until that cleanup: switch reads back to `birthdate_text` and stop writing `birthdate`.
