I can’t safely patch this from the packet alone: the endpoint code, ORM/query layer, schema, indexes, and test harness are missing. Based on the trace, though, the target fix is clear.

Current baseline for `/reports/account-summary`:

- p95: `9000ms`
- budget: `1500ms`
- DB time: `8110ms`
- Python assembly: `430ms`
- query count: `1842`

The bottleneck is database query count/N+1 behavior, not Python loop work.

Ranked fix plan:

1. Eliminate N+1 queries first.
   - Replace per-project task fetches: `620` calls to `select * from tasks where project_id=$1`
   - Replace per-task comment fetches: `1100` calls to `select * from comments where task_id=$1`
   - Replace per-user fetches: `122` calls to `select * from users where id=$1`
   - Use batched `WHERE project_id IN (...)`, `WHERE task_id IN (...)`, and `WHERE id IN (...)`, or ORM eager loading with bounded prefetches.

2. Keep result shape unchanged.
   - Batch fetch rows, group them in memory by `project_id`, `task_id`, and `user_id`.
   - Python grouping is acceptable here: `430ms` is not the main cost.

3. Verify indexes before rollout.
   - Need indexes on `tasks.project_id`, `comments.task_id`, and `users.id`.
   - If missing, add them separately with normal migration safety.

Benchmark plan:

- Re-run the same representative large-account workload: `120` projects, `6200` tasks.
- Capture p50/p95, DB time, query count, and endpoint output equivalence.
- Success target: p95 below `1500ms`, query count reduced from `1842` to a small bounded number, ideally single digits to low tens.

Rollback/regression criteria:

- Roll back if output differs from the old endpoint for sampled accounts.
- Roll back if p95 exceeds budget, DB CPU/load spikes materially, memory use grows beyond acceptable limits, or query count regresses above the agreed ceiling.
- Add a regression test/assertion around maximum query count for the large-account fixture.
