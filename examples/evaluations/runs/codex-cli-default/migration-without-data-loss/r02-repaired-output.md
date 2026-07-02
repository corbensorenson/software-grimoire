Missing specifics: primary key column name and accepted legacy date formats. SQL below uses `<pk>` and only auto-converts strict ISO `YYYY-MM-DD`; everything else is quarantined.

**1. Schema Expand**

```sql
ALTER TABLE users ADD COLUMN birthdate_date date;

CREATE TABLE users_birthdate_quarantine (
  user_pk bigint,
  birthdate_text text,
  reason text,
  captured_at timestamptz DEFAULT now()
);

CREATE OR REPLACE FUNCTION parse_birthdate_iso(v text)
RETURNS date
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT CASE
    WHEN v IS NULL OR btrim(v) = '' THEN NULL
    WHEN v ~ '^\d{4}-\d{2}-\d{2}$'
     AND to_char(to_date(v, 'YYYY-MM-DD'), 'YYYY-MM-DD') = v
      THEN to_date(v, 'YYYY-MM-DD')
    ELSE NULL
  END
$$;
```

**2. Deploy 1: Dual Write**

Application writes both columns. For new/updated rows, write canonical `birthdate_date`; keep `birthdate_text` populated for rollback/read compatibility.

Optional compatibility trigger:

```sql
CREATE OR REPLACE FUNCTION users_birthdate_dual_write()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.birthdate_date IS NULL THEN
    NEW.birthdate_date := parse_birthdate_iso(NEW.birthdate_text);
  END IF;

  IF NEW.birthdate_date IS NOT NULL THEN
    NEW.birthdate_text := NEW.birthdate_date::text;
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER users_birthdate_dual_write_trg
BEFORE INSERT OR UPDATE OF birthdate_text, birthdate_date ON users
FOR EACH ROW EXECUTE FUNCTION users_birthdate_dual_write();
```

**3. Backfill + Quarantine**

Run in batches by `<pk>` range.

```sql
UPDATE users
SET birthdate_date = parse_birthdate_iso(birthdate_text)
WHERE birthdate_date IS NULL
  AND birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND parse_birthdate_iso(birthdate_text) IS NOT NULL;

INSERT INTO users_birthdate_quarantine (user_pk, birthdate_text, reason)
SELECT <pk>, birthdate_text, 'invalid_or_ambiguous'
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND parse_birthdate_iso(birthdate_text) IS NULL;
```

If quarantine volume is too large, stop here. Manual decision boundary: define accepted formats, partial-date policy, invalid-value policy, and whether unknown/empty means `NULL`.

**4. Validation Queries**

```sql
-- Invalid non-empty rows
SELECT count(*) FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND parse_birthdate_iso(birthdate_text) IS NULL;

-- Null behavior
SELECT
  count(*) FILTER (WHERE birthdate_text IS NULL) AS text_nulls,
  count(*) FILTER (WHERE btrim(coalesce(birthdate_text, '')) = '') AS blank_or_null_text,
  count(*) FILTER (WHERE birthdate_date IS NULL) AS date_nulls
FROM users;

-- Row-count parity
SELECT
  (SELECT count(*) FROM users) AS users_count,
  (SELECT count(*) FROM users WHERE birthdate_date IS NOT NULL) AS converted_count;

-- Post-cutover consistency
SELECT count(*)
FROM users
WHERE birthdate_date IS DISTINCT FROM parse_birthdate_iso(birthdate_text)
  AND birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> '';
```

**5. Deploy 2: Read Switch**

Switch reads to `birthdate_date`. Keep dual writes and old column until validation passes.

**6. Cleanup**

```sql
DROP TRIGGER users_birthdate_dual_write_trg ON users;
DROP FUNCTION users_birthdate_dual_write();

ALTER TABLE users RENAME COLUMN birthdate_text TO birthdate_text_legacy;
ALTER TABLE users RENAME COLUMN birthdate_date TO birthdate;
```

Drop legacy only after a retention window.

**7. Rollback**

Before cleanup: switch reads back to `birthdate_text`; keep writes dual. After cleanup, rollback requires renaming `birthdate` back or restoring from `birthdate_text_legacy`.
