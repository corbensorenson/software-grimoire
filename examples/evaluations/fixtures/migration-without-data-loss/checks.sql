-- Dirty non-empty values that cannot be parsed must be counted before cutover.
SELECT count(*) AS dirty_birthdate_text
FROM users
WHERE birthdate_text IS NOT NULL
  AND btrim(birthdate_text) <> ''
  AND lower(btrim(birthdate_text)) <> 'unknown'
  AND birthdate IS NULL;

-- After backfill, compare old/new interpretation before dropping old columns.
SELECT count(*) AS parsed_rows
FROM users
WHERE birthdate IS NOT NULL;
