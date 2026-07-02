Missing: exact primary key and final column names. SQL below assumes `users.id`, source `users.birthdate_text`, and target `users.birthdate`.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate DATE;

CREATE TABLE users_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY,
  raw_birthdate_text TEXT,
  reason TEXT NOT NULL,
  quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**2. App Deploy 1: Dual Write**

Application writes both:

- `birthdate_text`: legacy value for rollback/read compatibility
- `birthdate`: parsed `DATE` only when business rules say the value is valid
- invalid, partial, ambiguous, empty, or `unknown` values go to quarantine/manual handling

Optional compatibility trigger for legacy writers:

```sql
CREATE OR REPLACE FUNCTION sync_users_birthdate()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.birthdate_text IS NULL THEN
    NEW.birthdate := NULL;

  ELSIF btrim(NEW.birthdate_text) ~ '^\d{4}-\d{2}-\d{2}$'
    AND to_char(to_date(btrim(NEW.birthdate_text), 'YYYY-MM-DD'), 'YYYY-MM-DD')
        = btrim(NEW.birthdate_text)
  THEN
    NEW.birthdate := to_date(btrim(NEW.birthdate_text), 'YYYY-MM-DD');
    DELETE FROM users_birthdate_quarantine WHERE user_id = NEW.id;

  ELSE
    NEW.birthdate := NULL;
    INSERT INTO users_birthdate_quarantine (user_id, raw_birthdate_text, reason)
    VALUES (NEW.id, NEW.birthdate_text, 'invalid_or_ambiguous_birthdate')
    ON CONFLICT (user_id) DO UPDATE
      SET raw_birthdate_text = EXCLUDED.raw_birthdate_text,
          reason = EXCLUDED.reason,
          quarantined_at = now();
  END IF;

  RETURN NEW;
END $$;

CREATE TRIGGER trg_sync_users_birthdate
BEFORE INSERT OR UPDATE OF birthdate_text ON users
FOR EACH ROW EXECUTE FUNCTION sync_users_birthdate();
```

**3. Backfill**

```sql
UPDATE users
SET birthdate = to_date(btrim(birthdate_text), 'YYYY-MM-DD')
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) ~ '^\d{4}-\d{2}-\d{2}$'
  AND to_char(to_date(btrim(birthdate_text), 'YYYY-MM-DD'), 'YYYY-MM-DD')
      = btrim(birthdate_text)
  AND birthdate IS NULL;

INSERT INTO users_birthdate_quarantine (user_id, raw_birthdate_text, reason)
SELECT id, birthdate_text, 'invalid_or_ambiguous_birthdate'
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND NOT (
    btrim(birthdate_text) ~ '^\d{4}-\d{2}-\d{2}$'
    AND to_char(to_date(btrim(birthdate_text), 'YYYY-MM-DD'), 'YYYY-MM-DD')
        = btrim(birthdate_text)
  )
ON CONFLICT (user_id) DO NOTHING;
```

**4. Validation Queries**

```sql
-- invalid rows
SELECT * FROM users_birthdate_quarantine ORDER BY quarantined_at DESC;

-- null behavior
SELECT count(*) FROM users
WHERE birthdate_text IS NULL AND birthdate IS NOT NULL;

-- row-count parity for valid source rows
SELECT
  count(*) FILTER (WHERE birthdate IS NOT NULL) AS date_rows,
  count(*) FILTER (
    WHERE birthdate_text IS NOT NULL
      AND btrim(birthdate_text) ~ '^\d{4}-\d{2}-\d{2}$'
  ) AS parse_candidate_rows
FROM users;

-- post-cutover consistency
SELECT id, birthdate_text, birthdate
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) ~ '^\d{4}-\d{2}-\d{2}$'
  AND birthdate IS DISTINCT FROM to_date(btrim(birthdate_text), 'YYYY-MM-DD');
```

**5. App Deploy 2: Read Switch**

Switch reads to `users.birthdate`. Keep dual write and old column until quarantine is empty or explicitly accepted.

If quarantine volume is large or includes ambiguous formats like `01/02/03`, stop here. Do not auto-cast. Product/legal/data owners must decide whether to reject, null, infer locale, or request user correction.

**6. Cleanup**

Only after parity and dirty-data handling are verified:

```sql
DROP TRIGGER trg_sync_users_birthdate ON users;
DROP FUNCTION sync_users_birthdate();

ALTER TABLE users DROP COLUMN birthdate_text;
```

**Rollback**

Before cleanup, rollback is app-only: switch reads back to `birthdate_text`; writes still populate both columns. Do not drop `birthdate_text` until rollback is no longer required.
