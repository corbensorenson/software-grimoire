## Expand-and-Contract Migration: `users.birthdate_text` → DATE

---

### Phase 1 — Schema Expand (Deploy 0, no app change needed)

```sql
-- Add the new DATE column, nullable, no constraints yet
ALTER TABLE users ADD COLUMN birthdate DATE;

-- Compatibility trigger: dual-write on INSERT/UPDATE
CREATE OR REPLACE FUNCTION sync_birthdate() RETURNS trigger AS $$
BEGIN
  NEW.birthdate := CASE
    WHEN NEW.birthdate_text ~ '^\d{4}-\d{2}-\d{2}$'
      THEN NEW.birthdate_text::DATE
    ELSE NULL  -- quarantine invalid values; do not error
  END;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_birthdate
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_birthdate();
```

---

### Phase 2 — Backfill (batched, off-peak)

```sql
-- Quarantine table for dirty rows
CREATE TABLE users_birthdate_quarantine AS
SELECT id, birthdate_text, NOW() AS quarantined_at
FROM users
WHERE birthdate_text IS NOT DISTINCT FROM ''
   OR birthdate_text = 'unknown'
   OR (birthdate_text IS NOT NULL
       AND birthdate_text !~ '^\d{4}-\d{2}-\d{2}$');

-- Backfill valid rows in batches (repeat until 0 rows updated)
UPDATE users
SET birthdate = birthdate_text::DATE
WHERE birthdate IS NULL
  AND birthdate_text ~ '^\d{4}-\d{2}-\d{2}$'
  AND id IN (SELECT id FROM users WHERE birthdate IS NULL LIMIT 10000);
```

**Stop here if quarantine is non-trivial.** Report dirty row count to stakeholders; require explicit business decision (default null, reject, or impute) before proceeding.

---

### Phase 3 — Validation Queries

```sql
-- Row-count parity: backfilled + quarantined must equal total
SELECT
  (SELECT COUNT(*) FROM users) AS total,
  (SELECT COUNT(*) FROM users WHERE birthdate IS NOT NULL) AS backfilled,
  (SELECT COUNT(*) FROM users_birthdate_quarantine) AS quarantined;

-- No silent data drift: valid source rows without a DATE value
SELECT COUNT(*) AS missed
FROM users
WHERE birthdate_text ~ '^\d{4}-\d{2}-\d{2}$'
  AND birthdate IS NULL;

-- Spot-check round-trip fidelity
SELECT id FROM users
WHERE birthdate IS NOT NULL
  AND birthdate::TEXT <> birthdate_text
LIMIT 20;
```

---

### Phase 4 — Read Switch (Deploy 1)

Update application queries to read `birthdate` (DATE column). Keep writing to both columns via the trigger. Monitor for one full business day.

---

### Phase 5 — Cleanup (Deploy 2, after validation sign-off)

```sql
DROP TRIGGER trg_sync_birthdate ON users;
DROP FUNCTION sync_birthdate();
ALTER TABLE users DROP COLUMN birthdate_text;
```

---

### Rollback Plan

| Phase | Rollback action |
|---|---|
| After Phase 1 | `DROP TRIGGER`, `DROP COLUMN birthdate` |
| After Phase 4 | Revert app to read `birthdate_text`; trigger still writing both |
| After Phase 5 | No rollback — commit point; restore from pre-cleanup snapshot |

**Do not drop `birthdate_text` until validation queries pass and quarantine rows have a documented resolution.**
