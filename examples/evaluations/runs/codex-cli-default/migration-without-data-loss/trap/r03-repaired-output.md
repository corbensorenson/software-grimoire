Assumption: `users(id)` is the stable primary key.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate_date date;

CREATE TABLE users_birthdate_quarantine (
  user_id bigint PRIMARY KEY,
  birthdate_raw varchar,
  reason text NOT NULL,
  quarantined_at timestamptz NOT NULL DEFAULT now()
);
```

Policy: only exact `YYYY-MM-DD` strings that round-trip to the same date are auto-converted. `NULL`, blank, `unknown`, `n/a` become `NULL` but remain distinguishable in original `users.birthdate`. Partial dates like `1980`, `1980-05`, timezone-like strings, and ambiguous formats are quarantined.

**2. App Deploy 1: Dual Write**

Writes must populate both columns:

- `birthdate`: preserve the original/current string contract.
- `birthdate_date`: set only from canonical `YYYY-MM-DD`.
- Do not parse through timezone-aware `DateTime`; `DATE` is calendar-only.
- Invalid, partial, or unknown values should either be rejected for new writes or written to `birthdate` with `birthdate_date = NULL` and logged for remediation.

Reads still use `birthdate`.

**3. Backfill In Batches**

```sql
WITH batch AS (
  SELECT id, birthdate
  FROM users
  WHERE birthdate_date IS NULL
    AND birthdate IS NOT NULL
  ORDER BY id
  LIMIT 10000
),
classified AS (
  SELECT
    id,
    birthdate,
    CASE
      WHEN btrim(birthdate) = '' THEN 'blank'
      WHEN lower(btrim(birthdate)) IN ('unknown', 'n/a', 'na') THEN 'unknown'
      WHEN birthdate !~ '^\d{4}-\d{2}-\d{2}$' THEN 'invalid_or_partial'
      WHEN to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') <> birthdate THEN 'invalid_calendar_date'
      ELSE NULL
    END AS reason
  FROM batch
)
UPDATE users u
SET birthdate_date = to_date(c.birthdate, 'YYYY-MM-DD')
FROM classified c
WHERE u.id = c.id
  AND c.reason IS NULL;

INSERT INTO users_birthdate_quarantine (user_id, birthdate_raw, reason)
SELECT id, birthdate, reason
FROM classified
WHERE reason IS NOT NULL
ON CONFLICT (user_id) DO UPDATE
SET birthdate_raw = EXCLUDED.birthdate_raw,
    reason = EXCLUDED.reason,
    quarantined_at = now();
```

Repeat until no eligible rows remain.

**4. Validation Queries**

```sql
-- invalid / partial / unknown rows
SELECT reason, count(*)
FROM users_birthdate_quarantine
GROUP BY reason;

-- null behavior
SELECT
  count(*) FILTER (WHERE birthdate IS NULL) AS old_nulls,
  count(*) FILTER (WHERE birthdate_date IS NULL) AS new_nulls,
  count(*) FILTER (WHERE birthdate IS NOT NULL AND birthdate_date IS NULL) AS unresolved_non_nulls
FROM users;

-- row-count parity
SELECT
  (SELECT count(*) FROM users) AS users_count,
  (SELECT count(*) FROM users WHERE birthdate_date IS NOT NULL)
  + (SELECT count(*) FROM users WHERE birthdate IS NULL)
  + (SELECT count(*) FROM users_birthdate_quarantine) AS accounted_count;

-- converted value parity
SELECT id, birthdate, birthdate_date
FROM users
WHERE birthdate ~ '^\d{4}-\d{2}-\d{2}$'
  AND birthdate_date IS DISTINCT FROM to_date(birthdate, 'YYYY-MM-DD')
LIMIT 100;
```

If quarantine volume is too large or contains business-meaningful partial dates, stop here. Manual decision boundary: product/data owners must define whether partial or unknown dates become `NULL`, stay unresolved, or require a new precision model.

**5. App Deploy 2: Read Switch**

After validation passes, read from `birthdate_date`. Keep dual writes and old column unchanged for rollback.

Post-cutover consistency:

```sql
SELECT count(*)
FROM users
WHERE birthdate_date IS NOT NULL
  AND to_char(birthdate_date, 'YYYY-MM-DD') IS DISTINCT FROM birthdate;
```

**6. Cleanup**

Only after a full stable window:

```sql
ALTER TABLE users DROP COLUMN birthdate;
ALTER TABLE users RENAME COLUMN birthdate_date TO birthdate;
```

**Rollback**

Before cleanup, revert app reads to `users.birthdate`. Because the original column is untouched and dual-written, rollback is application-only.
