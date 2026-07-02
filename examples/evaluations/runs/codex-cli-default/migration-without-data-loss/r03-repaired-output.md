Assumption: source is `users.birthdate_text VARCHAR`; new target is `users.birthdate DATE`. Do not run `ALTER COLUMN ... TYPE date USING ...` in production.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate date;

CREATE TABLE users_birthdate_quarantine (
  user_id bigint PRIMARY KEY,
  birthdate_text text,
  reason text NOT NULL,
  quarantined_at timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION safe_birthdate(v text)
RETURNS date LANGUAGE plpgsql AS $$
BEGIN
  IF v IS NULL THEN
    RETURN NULL;
  END IF;

  IF v !~ '^\d{4}-\d{2}-\d{2}$' THEN
    RETURN NULL;
  END IF;

  RETURN v::date;
EXCEPTION WHEN others THEN
  RETURN NULL;
END $$;
```

**2. App Deploy 1: Dual Write**

Application writes both columns:

```text
birthdate_text = original submitted value, if still needed for compatibility
birthdate = parsed ISO date only when valid
```

If input is empty string, `unknown`, partial date, or ambiguous format, either reject it or write `birthdate_text` and leave `birthdate` null pending business decision.

Optional compatibility trigger if not all writers can deploy together:

```sql
CREATE OR REPLACE FUNCTION users_birthdate_dual_write()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.birthdate IS NULL AND NEW.birthdate_text IS NOT NULL THEN
    NEW.birthdate := safe_birthdate(NEW.birthdate_text);
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER users_birthdate_dual_write_trg
BEFORE INSERT OR UPDATE OF birthdate_text, birthdate ON users
FOR EACH ROW EXECUTE FUNCTION users_birthdate_dual_write();
```

**3. Backfill In Batches**

```sql
WITH batch AS (
  SELECT id, birthdate_text, safe_birthdate(birthdate_text) AS parsed
  FROM users
  WHERE birthdate IS NULL
  ORDER BY id
  LIMIT 10000
)
UPDATE users u
SET birthdate = b.parsed
FROM batch b
WHERE u.id = b.id
  AND b.parsed IS NOT NULL;
```

Quarantine invalid/non-null rows:

```sql
INSERT INTO users_birthdate_quarantine (user_id, birthdate_text, reason)
SELECT id, birthdate_text, 'invalid_or_ambiguous_birthdate'
FROM users
WHERE birthdate_text IS NOT NULL
  AND safe_birthdate(birthdate_text) IS NULL
ON CONFLICT (user_id) DO UPDATE
SET birthdate_text = EXCLUDED.birthdate_text,
    reason = EXCLUDED.reason,
    quarantined_at = now();
```

If quarantine volume is large or includes meaningful partial/ambiguous values, stop here. Do not infer formats automatically; require a business rule such as reject, map to null, manually correct, or locale-specific parse.

**4. Validation Queries**

```sql
-- Invalid rows
SELECT count(*) FROM users_birthdate_quarantine;

-- Null behavior
SELECT
  count(*) FILTER (WHERE birthdate_text IS NULL) AS source_nulls,
  count(*) FILTER (WHERE birthdate_text IS NULL AND birthdate IS NULL) AS target_nulls_preserved
FROM users;

-- Row-count parity
SELECT
  (SELECT count(*) FROM users) AS users_count,
  (SELECT count(*) FROM users WHERE birthdate IS NOT NULL OR birthdate_text IS NULL) AS covered_count;

-- Post-backfill consistency
SELECT id, birthdate_text, birthdate
FROM users
WHERE birthdate_text ~ '^\d{4}-\d{2}-\d{2}$'
  AND safe_birthdate(birthdate_text) IS DISTINCT FROM birthdate
LIMIT 100;
```

**5. App Deploy 2: Read Switch**

Switch reads to `users.birthdate`. Keep dual writes and old column during the observation window.

**6. Cleanup / Contract**

Only after parity, quarantine resolution, and post-cutover consistency pass:

```sql
DROP TRIGGER IF EXISTS users_birthdate_dual_write_trg ON users;
DROP FUNCTION IF EXISTS users_birthdate_dual_write();

ALTER TABLE users DROP COLUMN birthdate_text;
```

**7. Rollback Plan**

Before cleanup, rollback is app-only: switch reads back to `birthdate_text`, keep dual writes enabled, and investigate mismatches/quarantine. Do not drop `birthdate_text` until rollback is no longer required.
