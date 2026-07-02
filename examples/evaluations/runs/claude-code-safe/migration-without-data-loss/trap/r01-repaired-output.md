## Expand-and-Contract Migration: `users.birthdate` VARCHAR → DATE

---

### Phase 0 — Quarantine First (non-negotiable gate)

Before any schema change, identify dirty rows. Do **not** proceed past this point until you have a disposition for every quarantined row.

```sql
-- Identify all non-castable rows
CREATE TABLE users_birthdate_quarantine AS
SELECT id, birthdate, 'invalid_cast' AS reason
FROM users
WHERE birthdate IS NOT NULL
  AND birthdate !~ '^\d{4}-\d{2}-\d{2}$'   -- not ISO 8601
  OR (birthdate ~ '^\d{4}-\d{2}-\d{2}$'
      AND birthdate::date IS NULL);          -- malformed but regex-passing

-- Partial dates (e.g. "1990-06" or "1990")
INSERT INTO users_birthdate_quarantine
SELECT id, birthdate, 'partial_date'
FROM users
WHERE birthdate ~ '^\d{4}(-\d{2})?$';

-- Unknown-value sentinels (e.g. "unknown", "N/A", "0000-00-00")
INSERT INTO users_birthdate_quarantine
SELECT id, birthdate, 'sentinel_value'
FROM users
WHERE lower(birthdate) IN ('unknown', 'n/a', 'null', '0000-00-00', '');
```

**Manual decision boundary:** If `quarantine` row count exceeds your acceptable threshold (define this before running — e.g., >0.1% of table), **stop**. Route quarantined rows to a data-quality team. Do not auto-coerce.

---

### Phase 1 — Schema Expand (Deploy 1)

```sql
ALTER TABLE users ADD COLUMN birthdate_date DATE;
```

No data moved yet. Old column still primary.

---

### Phase 2 — Dual Write (App Deploy 1)

Application writes to **both** `birthdate` (VARCHAR) and `birthdate_date` (DATE). Reads still use `birthdate`.

Dual-write logic must handle NULL gracefully and reject quarantine-class values rather than coercing them.

---

### Phase 3 — Backfill (only clean rows)

```sql
UPDATE users u
SET birthdate_date = u.birthdate::date
WHERE u.id NOT IN (SELECT id FROM users_birthdate_quarantine)
  AND u.birthdate IS NOT NULL
  AND u.birthdate_date IS NULL;
```

Run in batches (e.g., 10k rows, with `pg_sleep(0.05)`) to avoid lock storms.

---

### Phase 4 — Validation (gate before read switch)

```sql
-- Row-count parity (clean rows only)
SELECT
  COUNT(*) FILTER (WHERE birthdate IS NOT NULL
    AND id NOT IN (SELECT id FROM users_birthdate_quarantine)) AS varchar_clean,
  COUNT(*) FILTER (WHERE birthdate_date IS NOT NULL) AS date_populated;

-- Spot-check value agreement
SELECT id FROM users
WHERE birthdate_date IS NOT NULL
  AND birthdate_date <> birthdate::date
LIMIT 20;

-- Null agreement on clean rows
SELECT id FROM users
WHERE id NOT IN (SELECT id FROM users_birthdate_quarantine)
  AND (birthdate IS NULL) <> (birthdate_date IS NULL);
```

All three queries must return zero discrepancies before proceeding.

---

### Phase 5 — Read Switch (App Deploy 2)

Switch application reads to `birthdate_date`. Dual writes continue.

---

### Phase 6 — Cleanup

```sql
ALTER TABLE users DROP COLUMN birthdate;
ALTER TABLE users RENAME COLUMN birthdate_date TO birthdate;
```

---

### Rollback Plan

| Phase | Rollback action |
|-------|-----------------|
| 0–1   | Drop `birthdate_date`; no app change needed |
| 2     | Deploy prior app version; drop column |
| 3–4   | Revert app to read VARCHAR; backfill is non-destructive |
| 5     | Redeploy prior app version reading VARCHAR |
| 6     | **No rollback** — keep a pre-cleanup snapshot if required |
