Based on the fixture, the likely bottleneck is database I/O from N+1 query behavior.

**Bottleneck Hypotheses**
- Primary: N+1 database access. Trace shows `/reports/account-summary` at `p95=9000ms` against a `1500ms` budget, with `8110ms` in DB time and `1842` queries.
- Query patterns strongly indicate fanout:
  - `tasks where project_id=$1`: `620` calls
  - `comments where task_id=$1`: `1100` calls
  - `users where id=$1`: `122` calls
- Secondary: Python assembly is only `430ms`, so loop micro-optimization should wait until DB, network, allocation, and algorithmic effects are separated.

**What To Measure First**
- Full trace by account size: query count, DB time, row counts, payload bytes, connection pool wait, and endpoint p50/p95/p99.
- `EXPLAIN ANALYZE` for repeated task/comment/user queries.
- DB CPU, I/O, lock waits, cache hit rate, and network round trips.
- Python CPU/allocation profile only after DB query count is reduced.

**Ranked Optimization Options**
1. **Collapse N+1 queries into batched/set-based queries**
   Expected benefit: very high. Risk: medium.
   Fetch tasks with `WHERE project_id IN (...)`, comments with `WHERE task_id IN (...)`, and users with `WHERE id IN (...)`. Preserve ordering and authorization semantics.

2. **Move report aggregation into SQL or pre-aggregated summaries**
   Expected benefit: high. Risk: medium-high.
   Avoid loading full comment/task graphs if the report only needs counts, statuses, or totals.

3. **Add/verify indexes on join/filter columns**
   Expected benefit: medium if missing. Risk: low-medium.
   Check `tasks(project_id)`, `comments(task_id)`, and relevant user/account foreign keys.

4. **Cache or materialize account report snapshots**
   Expected benefit: high for repeated reads. Risk: medium-high due staleness/invalidation.
   Only after correctness and freshness requirements are explicit.

5. **Optimize Python assembly**
   Expected benefit: low until DB is fixed. Risk: low.
   Current assembly time is not the budget breaker.

**Benchmark Plan**
- Baseline current endpoint on representative large account: `120` projects, `6200` tasks.
- Record p50/p95/p99, throughput, query count, DB time, app CPU, memory, and correctness output.
- Test each optimization behind a flag against identical data and concurrency on commodity cloud hardware.
- Success: p95 below `1500ms`, query count reduced by orders of magnitude, DB time no longer dominant, output unchanged.

**Rollback / Regression Criteria**
- Roll back if p95/p99 exceeds budget, error rate rises, report output differs, query count regresses, DB CPU/I/O saturates, pool wait increases, memory spikes, or cache/materialized data becomes stale beyond accepted limits.
