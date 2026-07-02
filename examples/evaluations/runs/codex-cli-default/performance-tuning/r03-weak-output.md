I can’t patch the endpoint from this packet alone; the implementation, ORM/query code, schema, and indexes are missing. The trace is enough to rank the likely fix.

Baseline:

- `/reports/account-summary` p95: `9000 ms`
- Target p95: `1500 ms`
- DB time: `8110 ms`
- Python assembly: `430 ms`
- Queries: `1842`

The primary bottleneck is N+1 database access, not Python loop speed.

Recommended order:

1. Instrument first: capture query count, normalized SQL, DB time, account size, and p95 for this endpoint in staging/prod.
2. Remove N+1 queries:
   - Replace per-project `tasks where project_id=$1` calls with one batched query over project IDs.
   - Replace per-task `comments where task_id=$1` calls with one batched query over task IDs.
   - Batch user lookup by unique user IDs instead of `users where id=$1` repeatedly.
3. Verify indexes after query shape is known:
   - `tasks.project_id`
   - `comments.task_id`
   - user lookup should already use primary key; confirm with `EXPLAIN`.
4. Only after DB query count is fixed, consider Python assembly tuning. It is currently about 5% of p95, so it cannot close the gap alone.

Benchmark plan:

- Re-run against the large-account workload: `120` projects, `6200` tasks.
- Compare p95, DB time, total query count, and response correctness.
- Success criteria: p95 at or below `1500 ms`, query count no longer scales linearly with projects/tasks, and output matches baseline.

Rollback/regression criteria before release:

- Roll back if response data differs from baseline.
- Roll back if p95 remains above budget or worsens versus current baseline.
- Roll back if query count still grows with project/task count.
- Ship behind a flag or canary so the old query path can be restored quickly.
