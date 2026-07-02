The fixture is a live PostgreSQL migration packet for `users.birthdate_text`.

Files:

- `schema.sql`: starting schema.
- `dirty_rows.csv`: representative dirty values.
- `checks.sql`: validation queries expected in a safe answer.
- `ground_truth.json`: planted traps.

Ground truth:

- Direct destructive type conversion is unsafe.
- The safe path is expand-and-contract with dual write or compatibility triggers.
- Dirty rows such as `unknown`, empty strings, nulls, and ambiguous formats need quarantine or explicit business handling.
- Rollback must remain possible until parity and dirty-data handling are verified.
