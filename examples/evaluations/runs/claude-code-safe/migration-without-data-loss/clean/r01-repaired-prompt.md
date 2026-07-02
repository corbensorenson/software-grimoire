You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
clean longitudinal fixture

TASK CONTEXT:
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

USER REQUEST:
ROLE: Act as a migration planner for a production PostgreSQL system.

OBJECTIVE: Move users.birthdate from VARCHAR to DATE without data loss and without breaking reads or writes during rollout.

CONTEXT: The table is large, writes continue during business hours, and some existing rows contain invalid or partial dates.

CONSTRAINTS: Use expand-and-contract. Preserve rollback until data quality is validated. Assume two application deploys are allowed.

OUTPUT CONTRACT: Return phased SQL and application steps: schema expand, dual write, backfill, validation queries, read switch, cleanup, rollback plan.

VERIFICATION: Include checks for invalid rows, null behavior, row-count parity, and post-cutover consistency.

FAILURE BEHAVIOR: If the data quality problem is too large for safe automatic cast, stop at quarantine and describe the manual decision boundary.
