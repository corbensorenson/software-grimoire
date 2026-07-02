Assumption: `users.id` exists. Replace with the real stable primary key if not.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate DATE;

CREATE TABLE users_birthdate_quarantine (
  user_id BIGINT PRIMARY KEY,
  birthdate_text VARCHAR,
  reason TEXT NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Create a safe parser:

```sql
CREATE OR REPLACE FUNCTION parse_user_birthdate(v TEXT)
RETURNS DATE
LANGUAGE plpgsql
AS $$
DECLARE d DATE;
BEGIN
  IF v IS NULL OR btrim(v) = '' THEN
    RETURN NULL;
  END IF;

  IF v ~ '^\d{4}-\d{2}-\d{2}$' THEN
    d := to_date(v, 'YYYY-MM-DD');
    IF to_char(d, 'YYYY-MM-DD') = v THEN RETURN d; END IF;
  END IF;

  IF v ~ '^\d{2}/\d{2}/\d{4}$' THEN
    d := to_date(v, 'MM/DD/YYYY');
    IF to_char(d, 'MM/DD/YYYY') = v THEN RETURN d; END IF;
  END IF;

  RETURN NULL;
END $$;
```

Add trigger so old app writes still populate the new column:

```sql
CREATE OR REPLACE FUNCTION users_birthdate_dual_write()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.birthdate IS NULL THEN
    NEW.birthdate := parse_user_birthdate(NEW.birthdate_text);
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER users_birthdate_dual_write_trg
BEFORE INSERT OR UPDATE OF birthdate_text, birthdate ON users
FOR EACH ROW
EXECUTE FUNCTION users_birthdate_dual_write();
```

**2. App Deploy 1: Dual Write**

New app writes both:

```text
birthdate_text = original submitted string or canonical YYYY-MM-DD
birthdate = validated DATE or NULL
```

Reads still use `birthdate_text`.

Old app versions remain safe because the trigger handles their writes.

**3. Backfill In Batches**

Do not run one 40M-row transaction.

```sql
UPDATE users
SET birthdate = parse_user_birthdate(birthdate_text)
WHERE id BETWEEN :start_id AND :end_id
  AND birthdate IS NULL;
```

Quarantine invalid non-empty values:

```sql
INSERT INTO users_birthdate_quarantine (user_id, birthdate_text, reason)
SELECT id, birthdate_text, 'unparseable birthdate_text'
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND parse_user_birthdate(birthdate_text) IS NULL
ON CONFLICT (user_id) DO UPDATE
SET birthdate_text = EXCLUDED.birthdate_text,
    reason = EXCLUDED.reason,
    recorded_at = now();
```

If quarantine volume is too large for business tolerance, stop here. Manual decision boundary: decide whether invalid/partial dates become `NULL`, require user remediation, get corrected from another source, or block the cutover.

**4. Validation**

Invalid rows:

```sql
SELECT count(*) FROM users_birthdate_quarantine;
```

Null behavior:

```sql
SELECT
  count(*) FILTER (WHERE birthdate_text IS NULL) AS old_nulls,
  count(*) FILTER (WHERE btrim(birthdate_text) = '') AS old_empty_strings,
  count(*) FILTER (WHERE birthdate IS NULL) AS new_nulls
FROM users;
```

Row-count parity:

```sql
SELECT
  (SELECT count(*) FROM users) AS users_count,
  (SELECT count(*) FROM users WHERE birthdate IS NOT NULL) AS parsed_count,
  (SELECT count(*) FROM users_birthdate_quarantine) AS invalid_count;
```

Expected:

```text
users_count = parsed_count + invalid_count + null_or_empty_count
```

**5. App Deploy 2: Read Switch**

Switch reads to `users.birthdate`.

Keep writing both columns. Keep trigger and `birthdate_text` for rollback.

Post-cutover consistency:

```sql
SELECT count(*)
FROM users
WHERE birthdate IS DISTINCT FROM parse_user_birthdate(birthdate_text)
  AND birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> '';
```

**6. Rollback Plan**

If app issues occur, redeploy reads back to `birthdate_text`. No data loss because old text remains and dual writes continued.

If data issues occur, keep app on old reads, fix quarantine, rerun targeted backfill.

**7. Cleanup**

Only after validated production stability:

```sql
DROP TRIGGER users_birthdate_dual_write_trg ON users;
DROP FUNCTION users_birthdate_dual_write();

ALTER TABLE users DROP COLUMN birthdate_text;
```

Optionally rename:

```sql
ALTER TABLE users RENAME COLUMN birthdate TO birthdate_date;
```
