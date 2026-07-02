Below is a safe expand-and-contract plan. Policy: `birthdate` is a civil date, so no timezone conversion. Automatic backfill only accepts complete ISO `YYYY-MM-DD` dates that round-trip exactly. Partial dates, empty strings, `unknown`, `0000-00-00`, locale dates, and invalid dates are quarantined unless product/data owners approve a rule.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate_date date;

CREATE TABLE users_birthdate_quarantine (
  user_id bigint PRIMARY KEY,
  raw_birthdate varchar,
  reason text NOT NULL,
  quarantined_at timestamptz NOT NULL DEFAULT now()
);
```

Optional, only if reads/filtering need it:

```sql
CREATE INDEX CONCURRENTLY idx_users_birthdate_date
ON users (birthdate_date);
```

**2. Deploy 1: Dual Write, Read Old**

Application writes both columns for new/updated users.

Rules:

```text
input full ISO date -> write users.birthdate = raw string, users.birthdate_date = parsed DATE
input NULL -> write both NULL
partial/unknown/invalid input -> reject write or store old varchar only and emit validation error
reads continue from users.birthdate
```

**3. Backfill In Batches**

First quarantine dirty rows before casting:

```sql
INSERT INTO users_birthdate_quarantine (user_id, raw_birthdate, reason)
SELECT id, birthdate,
  CASE
    WHEN birthdate IS NULL THEN 'null'
    WHEN btrim(birthdate) = '' THEN 'blank'
    WHEN lower(btrim(birthdate)) IN ('unknown', 'n/a', 'na', 'null') THEN 'unknown-token'
    WHEN birthdate !~ '^\d{4}-\d{2}-\d{2}$' THEN 'not-full-iso-date'
    WHEN to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') <> birthdate THEN 'invalid-date'
    ELSE 'unexpected'
  END
FROM users
WHERE birthdate_date IS NULL
  AND birthdate IS NOT NULL
  AND (
    btrim(birthdate) = ''
    OR lower(btrim(birthdate)) IN ('unknown', 'n/a', 'na', 'null')
    OR birthdate !~ '^\d{4}-\d{2}-\d{2}$'
    OR to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') <> birthdate
  )
ON CONFLICT (user_id) DO NOTHING;
```

Then backfill only clean rows, repeatedly in small batches:

```sql
WITH batch AS (
  SELECT id
  FROM users
  WHERE birthdate_date IS NULL
    AND birthdate ~ '^\d{4}-\d{2}-\d{2}$'
    AND to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') = birthdate
  ORDER BY id
  LIMIT 10000
)
UPDATE users u
SET birthdate_date = u.birthdate::date
FROM batch
WHERE u.id = batch.id;
```

**4. Validation Queries**

Invalid/quarantine count:

```sql
SELECT reason, count(*) FROM users_birthdate_quarantine GROUP BY reason;
```

Null behavior:

```sql
SELECT
  count(*) FILTER (WHERE birthdate IS NULL) AS old_nulls,
  count(*) FILTER (WHERE birthdate_date IS NULL) AS new_nulls
FROM users;
```

Row-count parity for clean parseable rows:

```sql
SELECT
  count(*) AS clean_old_rows,
  count(birthdate_date) AS populated_new_rows
FROM users
WHERE birthdate ~ '^\d{4}-\d{2}-\d{2}$'
  AND to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') = birthdate;
```

Mismatch check:

```sql
SELECT id, birthdate, birthdate_date
FROM users
WHERE birthdate ~ '^\d{4}-\d{2}-\d{2}$'
  AND to_char(to_date(birthdate, 'YYYY-MM-DD'), 'YYYY-MM-DD') = birthdate
  AND birthdate::date IS DISTINCT FROM birthdate_date
LIMIT 100;
```

If quarantine volume is too large, or contains business-significant partial dates such as `1980-05` or `1980`, stop here. Do not auto-cast. Decide manually whether to preserve partial precision elsewhere, normalize to a chosen date, or leave `birthdate_date` NULL.

**5. Deploy 2: Read Switch**

After zero mismatches and accepted quarantine policy, read from `birthdate_date`. Keep dual writes and old column for rollback.

Post-cutover consistency:

```sql
SELECT count(*)
FROM users
WHERE birthdate_date IS DISTINCT FROM birthdate::date
  AND birthdate ~ '^\d{4}-\d{2}-\d{2}$';
```

**6. Cleanup**

After observation window:

```sql
ALTER TABLE users DROP COLUMN birthdate;
ALTER TABLE users RENAME COLUMN birthdate_date TO birthdate;
```

**Rollback**

Before cleanup, rollback app reads to old `users.birthdate`. Keep dual writes enabled. If needed:

```sql
UPDATE users
SET birthdate_date = NULL
WHERE id IN (SELECT user_id FROM users_birthdate_quarantine);
```
