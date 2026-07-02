Missing facts: actual PK name, write path count, and business policy for partial/unknown values. Plan below assumes `users.id` is PK and uses a conservative policy: only exact valid `YYYY-MM-DD` becomes `DATE`; empty/unknown/partial/timestamp/timezone-bearing values are quarantined, not guessed.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate_new DATE;

CREATE TABLE users_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY,
  original_birthdate VARCHAR,
  reason TEXT NOT NULL,
  quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Optional helper parser:

```sql
CREATE OR REPLACE FUNCTION parse_birthdate_strict(v TEXT)
RETURNS DATE
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE d DATE;
BEGIN
  IF v IS NULL OR btrim(v) = '' THEN
    RETURN NULL;
  END IF;

  IF v !~ '^\d{4}-\d{2}-\d{2}$' THEN
    RETURN NULL;
  END IF;

  d := v::date;

  IF to_char(d, 'YYYY-MM-DD') <> v THEN
    RETURN NULL;
  END IF;

  RETURN d;
EXCEPTION WHEN others THEN
  RETURN NULL;
END;
$$;
```

**2. App Deploy 1: Dual Write, Read Old**

On every create/update, write both columns.

App parsing policy must match SQL exactly:

```text
valid: exact YYYY-MM-DD calendar date
null: original value is null or blank
invalid/quarantine: partial dates, unknown markers, timestamps, timezone-bearing values, malformed dates
```

Reads still use `users.birthdate`.

**3. Backfill With Quarantine First**

Do not cast directly.

```sql
INSERT INTO users_birthdate_quarantine (user_id, original_birthdate, reason)
SELECT id, birthdate,
       CASE
         WHEN birthdate IS NULL OR btrim(birthdate) = '' THEN 'null_or_blank'
         WHEN birthdate !~ '^\d{4}-\d{2}-\d{2}$' THEN 'not_exact_yyyy_mm_dd'
         WHEN parse_birthdate_strict(birthdate) IS NULL THEN 'invalid_calendar_date'
       END
FROM users
WHERE birthdate_new IS NULL
  AND birthdate IS NOT NULL
  AND btrim(birthdate) <> ''
  AND parse_birthdate_strict(birthdate) IS NULL
ON CONFLICT (user_id) DO NOTHING;
```

Then backfill valid rows in batches:

```sql
UPDATE users
SET birthdate_new = parse_birthdate_strict(birthdate)
WHERE id IN (
  SELECT id
  FROM users
  WHERE birthdate_new IS NULL
    AND parse_birthdate_strict(birthdate) IS NOT NULL
  ORDER BY id
  LIMIT 10000
);
```

Repeat until zero rows remain.

**4. Validation Queries**

Invalid rows:

```sql
SELECT reason, count(*) FROM users_birthdate_quarantine GROUP BY reason;
```

Null behavior:

```sql
SELECT count(*) AS old_nullish
FROM users
WHERE birthdate IS NULL OR btrim(birthdate) = '';

SELECT count(*) AS new_null
FROM users
WHERE birthdate_new IS NULL;
```

Row-count parity:

```sql
SELECT
  count(*) AS total,
  count(birthdate) AS old_non_null,
  count(birthdate_new) AS new_non_null
FROM users;
```

Value parity for valid rows:

```sql
SELECT count(*) AS mismatches
FROM users
WHERE parse_birthdate_strict(birthdate) IS NOT NULL
  AND birthdate_new IS DISTINCT FROM parse_birthdate_strict(birthdate);
```

**Stop condition:** if quarantine count exceeds the agreed risk threshold, or includes partial/unknown values needing business interpretation, stop rollout before read switch.

**5. App Deploy 2: Read Switch**

After validation passes, switch reads to `birthdate_new`. Keep dual writes enabled.

Post-cutover consistency:

```sql
SELECT count(*)
FROM users
WHERE parse_birthdate_strict(birthdate) IS NOT NULL
  AND birthdate_new IS DISTINCT FROM parse_birthdate_strict(birthdate);
```

**6. Cleanup**

After a stable observation window:

```sql
ALTER TABLE users RENAME COLUMN birthdate TO birthdate_old;
ALTER TABLE users RENAME COLUMN birthdate_new TO birthdate;
```

Later, after rollback window:

```sql
ALTER TABLE users DROP COLUMN birthdate_old;
DROP FUNCTION parse_birthdate_strict(TEXT);
```

**Rollback**

Before cleanup, rollback is app-only: switch reads back to old `birthdate`; keep both columns. If bad data is found after read switch, stop cleanup, repair/quarantine rows, and rerun parity checks.
