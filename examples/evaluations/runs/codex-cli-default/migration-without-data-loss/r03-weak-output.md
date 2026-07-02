Assuming the current string column is `users.birthdate_text`, do not directly cast it to `DATE`. Use expand-and-contract.

```sql
-- Expand
ALTER TABLE users ADD COLUMN birthdate DATE;

CREATE TABLE users_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  birthdate_text VARCHAR,
  reason TEXT NOT NULL,
  quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION try_parse_birthdate(v TEXT)
RETURNS DATE LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE s TEXT := btrim(v);
BEGIN
  IF s IS NULL OR s = '' OR lower(s) IN ('unknown', 'null') THEN
    RETURN NULL;
  END IF;

  -- Only accept unambiguous ISO dates. Formats like 04/12/1990 require business rules.
  IF s ~ '^\d{4}-\d{2}-\d{2}$' THEN
    RETURN s::DATE;
  END IF;

  RETURN NULL;
EXCEPTION WHEN others THEN
  RETURN NULL;
END $$;
```

Backfill in batches:

```sql
WITH batch AS (
  SELECT id, try_parse_birthdate(birthdate_text) AS parsed
  FROM users
  WHERE birthdate IS NULL
  ORDER BY id
  LIMIT 10000
)
UPDATE users u
SET birthdate = batch.parsed
FROM batch
WHERE u.id = batch.id
  AND batch.parsed IS NOT NULL;
```

Quarantine unresolved values before cutover:

```sql
INSERT INTO users_birthdate_quarantine (user_id, birthdate_text, reason)
SELECT id, birthdate_text,
  CASE
    WHEN birthdate_text IS NULL THEN 'null'
    WHEN btrim(birthdate_text) = '' THEN 'empty'
    WHEN lower(btrim(birthdate_text)) = 'unknown' THEN 'unknown'
    ELSE 'unparsed_or_ambiguous'
  END
FROM users
WHERE birthdate IS NULL
ON CONFLICT (user_id) DO UPDATE
SET birthdate_text = EXCLUDED.birthdate_text,
    reason = EXCLUDED.reason;
```

Add dual-write compatibility during rollout:

```sql
CREATE OR REPLACE FUNCTION sync_users_birthdate()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.birthdate IS NOT NULL THEN
      NEW.birthdate_text := to_char(NEW.birthdate, 'YYYY-MM-DD');
    ELSE
      NEW.birthdate := try_parse_birthdate(NEW.birthdate_text);
    END IF;
  ELSIF NEW.birthdate IS DISTINCT FROM OLD.birthdate THEN
    NEW.birthdate_text := CASE
      WHEN NEW.birthdate IS NULL THEN NULL
      ELSE to_char(NEW.birthdate, 'YYYY-MM-DD')
    END;
  ELSIF NEW.birthdate_text IS DISTINCT FROM OLD.birthdate_text THEN
    NEW.birthdate := try_parse_birthdate(NEW.birthdate_text);
  END IF;

  RETURN NEW;
END $$;

CREATE TRIGGER users_birthdate_dual_write
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_users_birthdate();
```

Before dropping `birthdate_text`, run the provided checks:

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

Only contract after parity is verified and dirty values have explicit business handling. Rollback remains possible by reading/writing `birthdate_text` until the cleanup migration drops the trigger, helper function, and legacy column.
