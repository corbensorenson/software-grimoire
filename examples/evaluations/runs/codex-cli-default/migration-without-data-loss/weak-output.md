Do this as an expand/contract migration. Do **not** directly `ALTER birthdate_text TYPE date`; on 40M live rows that risks long locks/table rewrites and breaks mixed old/new app versions.

Missing decisions: how to treat invalid strings like `unknown`, whether to preserve the original text forever, and whether all write paths can be updated to dual-write.

**Plan**

1. Add the new nullable column:

```sql
ALTER TABLE users ADD COLUMN birthdate DATE;
```

2. Add safe parsing logic. Invalid, empty, and `unknown` should become `NULL` unless product requirements say otherwise.

```sql
CREATE OR REPLACE FUNCTION try_parse_birthdate(value text)
RETURNS date
LANGUAGE plpgsql
AS $$
BEGIN
  IF value IS NULL OR btrim(value) = '' OR lower(btrim(value)) = 'unknown' THEN
    RETURN NULL;
  END IF;

  IF value ~ '^\d{4}-\d{2}-\d{2}$' THEN
    RETURN to_date(value, 'YYYY-MM-DD');
  END IF;

  IF value ~ '^\d{2}/\d{2}/\d{4}$' THEN
    RETURN to_date(value, 'MM/DD/YYYY');
  END IF;

  RETURN NULL;
EXCEPTION WHEN others THEN
  RETURN NULL;
END;
$$;
```

3. Deploy app version A that is backward-compatible:
   - Reads from `birthdate` if present, otherwise falls back to `birthdate_text`.
   - On writes, writes both columns.
   - New writes should normalize to `DATE`.

4. Backfill in small batches during normal traffic. Use primary-key ranges or `FOR UPDATE SKIP LOCKED`; do not run one huge update.

Example batch shape:

```sql
WITH batch AS (
  SELECT id
  FROM users
  WHERE birthdate IS NULL
    AND birthdate_text IS NOT NULL
  ORDER BY id
  LIMIT 10000
)
UPDATE users u
SET birthdate = try_parse_birthdate(u.birthdate_text)
FROM batch
WHERE u.id = batch.id;
```

Run repeatedly from a worker/job, with throttling, monitoring lock waits, replication lag, dead tuples, and write latency.

5. Validate:

```sql
SELECT count(*) FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND lower(btrim(birthdate_text)) <> 'unknown'
  AND birthdate IS NULL;
```

Also sample parsed rows manually, especially around ambiguous `MM/DD/YYYY` values.

6. Deploy app version B:
   - Reads only `birthdate`.
   - Continues writing `birthdate`.
   - Stops depending on `birthdate_text`.

7. After old app versions are fully gone, contract:

```sql
ALTER TABLE users DROP COLUMN birthdate_text;
DROP FUNCTION try_parse_birthdate(text);
```

Only add `NOT NULL` or constraints after confirming business rules, since existing `unknown`, empty, and null values imply nullable data today.
