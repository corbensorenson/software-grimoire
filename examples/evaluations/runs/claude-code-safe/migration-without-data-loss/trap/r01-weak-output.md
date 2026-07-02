Before proposing a migration, I need to flag that this request is underspecified in ways that will cause silent data corruption if ignored.

## What's Missing

**1. Dirty-row audit hasn't been done**

Running `ALTER TABLE users ALTER COLUMN birthdate TYPE DATE USING birthdate::date` will fail or silently corrupt data if any rows contain:

- Partial dates (`"1990"`, `"1990-05"`) — valid ISO fragments, not valid `DATE` literals
- Sentinel unknowns (`"unknown"`, `"N/A"`, `""`, `"0000-00-00"`) — common in legacy imports
- Locale-formatted strings (`"07/04/1990"`, `"4th July 1990"`)
- Timezone-bearing strings (`"1990-07-04T00:00:00Z"`) — ambiguous when cast to `DATE` without an explicit `AT TIME ZONE`

**2. No policy defined for:**
- **Partial dates** — store as `NULL`? First of month? Reject?
- **Unknown values** — `NULL` or a sentinel date or quarantine?
- **Timezone** — assume UTC? Server local? User's locale?

---

## Safe Migration Shape (once policies are defined)

```sql
-- Step 1: quarantine dirty rows before touching the column
CREATE TABLE users_birthdate_quarantine AS
SELECT id, birthdate, 'reason' AS reason
FROM users
WHERE birthdate !~ '^\d{4}-\d{2}-\d{2}$'   -- partial or non-ISO
   OR birthdate IN ('unknown', 'N/A', '')
   OR birthdate = '0000-00-00';

-- Step 2: null out quarantined rows in source (or apply policy)
UPDATE users
SET birthdate = NULL
WHERE id IN (SELECT id FROM users_birthdate_quarantine);

-- Step 3: only now cast the clean rows
ALTER TABLE users
  ALTER COLUMN birthdate TYPE DATE
  USING birthdate::date;

-- Step 4: parity check — row counts must match
SELECT COUNT(*) FROM users;               -- must equal pre-migration count
SELECT COUNT(*) FROM users WHERE birthdate IS NULL;  -- compare to baseline nulls + quarantine size
```

---

## What I Need Before Proceeding

1. Run `SELECT DISTINCT birthdate FROM users WHERE birthdate !~ '^\d{4}-\d{2}-\d{2}$' LIMIT 50` and share the output.
2. Confirm the policy for partial dates, unknowns, and timezone assumption.
3. Confirm whether quarantined rows should be `NULL`ed, deleted, or blocked (migration fails if any exist).

Providing a migration without those answers would be the weak path — it works on clean fixtures and breaks silently on real data.
