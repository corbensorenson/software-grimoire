Do not run `ALTER COLUMN birthdate_text TYPE DATE`. This needs expand-and-contract.

```sql
ALTER TABLE users ADD COLUMN birthdate DATE;

CREATE TABLE user_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY,
  birthdate_text TEXT,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Backfill in batches. Only auto-parse unambiguous ISO dates; quarantine everything else requiring policy.

```sql
UPDATE users
SET birthdate = birthdate_text::date
WHERE birthdate IS NULL
  AND birthdate_text ~ '^\d{4}-\d{2}-\d{2}$';

INSERT INTO user_birthdate_quarantine (user_id, birthdate_text, reason)
SELECT id, birthdate_text,
       CASE
         WHEN birthdate_text IS NULL OR btrim(birthdate_text) = '' THEN 'blank_or_null'
         WHEN lower(btrim(birthdate_text)) = 'unknown' THEN 'unknown'
         ELSE 'ambiguous_or_invalid'
       END
FROM users
WHERE birthdate_text IS NULL
   OR btrim(birthdate_text) = ''
   OR lower(btrim(birthdate_text)) = 'unknown'
   OR birthdate IS NULL
ON CONFLICT (user_id) DO NOTHING;
```

`04/12/1990` is ambiguous and `31/02/1990` is invalid, so the missing requirement is the business rule for non-ISO dates. Until that is defined, quarantine them.

Add dual-write in the application, or a compatibility trigger during rollout:

```sql
CREATE OR REPLACE FUNCTION sync_users_birthdate()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.birthdate IS NOT NULL THEN
    NEW.birthdate_text := NEW.birthdate::text;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER users_birthdate_sync
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_users_birthdate();
```

Before cutover, run the required checks:

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

Only after parity is verified and dirty rows are resolved should readers switch to `birthdate`. Keep `birthdate_text` and the trigger until rollback is no longer needed, then drop the trigger and old column in a later cleanup migration.
