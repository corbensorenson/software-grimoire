**Bottleneck Hypotheses**

Primary: N+1 database access on `/reports/account-summary`.

Evidence: p95 is `9000ms` against a `1500ms` budget. DB time is `8110ms`, while Python assembly is only `430ms`. Query count is `1842`, dominated by repeated calls:

- `tasks where project_id=$1`: `620` calls
- `comments where task_id=$1`: `1100` calls
- `users where id=$1`: `122` calls

This points to per-project/per-task/per-user fetching, not Python loop cost. Python micro-optimization should wait until DB/query behavior is isolated.

**What To Measure**

- Full trace by request size: query count, DB time, Python time, serialization time.
- Per-query latency, rows returned, and total bytes returned.
- `EXPLAIN ANALYZE` for the task, comment, and user queries.
- DB CPU, I/O wait, lock wait, connection pool wait, cache hit rate.
- Request p50/p95/p99 under accounts near `120` projects and `6200` tasks.
- Result correctness before and after query-shape changes.

**Ranked Optimization Options**

1. **Batch/eager-load report data**
   Highest benefit, moderate risk. Replace per-project task queries and per-task comment queries with bounded batch queries: fetch tasks for all project IDs, comments for all task IDs, users for all referenced IDs. Expected to collapse query count from `1842` toward a small fixed number.

2. **Aggregate in SQL where report shape allows**
   High benefit, moderate-to-high risk. If the endpoint only needs counts/summaries, avoid loading every comment/task row. Use grouped aggregates by account/project/task as appropriate. Risk is semantic drift in report calculations.

3. **Add or verify indexes**
   Medium-to-high benefit, lower risk if missing. Check indexes on `tasks.project_id`, `comments.task_id`, and `users.id`. Validate with query plans before adding.

4. **Cache stable report subcomponents**
   Medium benefit, moderate risk. Useful if reports are frequently requested and tolerate staleness. Only after query shape is fixed.

5. **Python assembly optimization**
   Low expected benefit now. `430ms` is not the dominant cost and should be revisited only after DB time is reduced.

**Benchmark Plan**

Create a representative benchmark using the large-account shape: `120` projects, `6200` tasks. Capture baseline p50/p95/p99, query count, DB ms, Python ms, errors, and result checksum. Run each optimization behind a flag/canary and compare against baseline under commodity cloud conditions.

**Success And Rollback Criteria**

Success: p95 under `1500ms`, query count reduced materially from `1842`, DB time no longer dominates, and report output matches baseline.

Rollback if p95/p99 worsens, errors/timeouts increase, DB CPU/I/O spikes, query count regresses, memory rises materially, or report totals differ from baseline.
