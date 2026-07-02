## Safe Migration: `users.birthdate_text` → `DATE`

A direct `ALTER COLUMN … TYPE DATE USING birthdate_text::date` is **unsafe** — it will fail on any dirty row and has no rollback path once committed.

### Phase 1 — Expand (add the new column)

```sql
-- Add the target column as nullable, leaving the source untouched
ALTER TABLE users ADD COLUMN birthdate DATE;
```

### Phase 2 — Quarantine dirty rows before touching production data

```sql
-- Identify rows that cannot be cleanly cast
CREATE TABLE users_birthdate_quarantine AS
SELECT id, birthdate_text, now() AS quarantined_at
FROM users
WHERE birthdate_text IS NULL
   OR trim(birthdate_text) = ''
   OR birthdate_text ILIKE 'unknown'
   OR birthdate_text !~ '^\d{4}-\d{2}-\d{2}$';  -- adjust pattern to your known formats
```

Review and get business sign-off on quarantined rows before proceeding. Do **not** silently coerce or discard them.

### Phase 3 — Backfill clean rows

```sql
UPDATE users
SET birthdate = birthdate_text::date
WHERE id NOT IN (SELECT id FROM users_birthdate_quarantine)
  AND birthdate IS NULL;
```

### Phase 4 — Dual-write trigger (keep parity during transition)

```sql
CREATE OR REPLACE FUNCTION sync_birthdate() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.birthdate_text IS NOT NULL AND trim(NEW.birthdate_text) <> ''
     AND NEW.birthdate_text !~ '(?i)^unknown$' THEN
    NEW.birthdate := NEW.birthdate_text::date;
  ELSE
    NEW.birthdate := NULL;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sync_birthdate
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_birthdate();
```

### Phase 5 — Validate parity before contracting

Run these checks (mirror `checks.sql`):

```sql
-- No clean rows left with a NULL target
SELECT count(*) FROM users
WHERE id NOT IN (SELECT id FROM users_birthdate_quarantine)
  AND birthdate IS NULL;

-- No future or obviously invalid dates slipped through
SELECT id, birthdate FROM users
WHERE birthdate > current_date OR birthdate < '1900-01-01';
```

Both must return zero rows before continuing.

### Phase 6 — Contract (only after parity is confirmed)

```sql
DROP TRIGGER trg_sync_birthdate ON users;
DROP FUNCTION sync_birthdate();
ALTER TABLE users DROP COLUMN birthdate_text;
```

---

### Rollback

Until Phase 6, rollback is trivial: `DROP COLUMN birthdate; DROP TABLE users_birthdate_quarantine;`. After Phase 6 there is no rollback — that is the gate.

**Do not run Phase 6 until:**
1. Quarantine table is reviewed and resolved by the business.
2. All parity checks pass.
3. Application code reads from `birthdate`, not `birthdate_text`.
