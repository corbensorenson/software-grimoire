**Bottleneck Hypotheses**

Primary: N+1 database access. Current trace shows `/reports/account-summary` at `p95=9000ms` against a `1500ms` budget, with `8110ms` in DB time and `1842` queries. The largest patterns are repeated task, comment, and user lookups: `620`, `1100`, and `122` calls.

Secondary: inefficient query shapes or missing indexes may appear after batching. Python assembly is only `430ms`, so loop micro-optimization should wait until DB, I/O, allocation, and network effects are separated.

**What To Measure**

Track per-request `p50/p95/p99`, query count, duplicate query fingerprints, DB execution time versus connection wait time, rows scanned/returned, payload size, Python assembly time, memory allocation, DB CPU/I/O, connection pool saturation, and network RTT. Capture `EXPLAIN ANALYZE` for the repeated query patterns and benchmark against the large account scale: `120` projects and `6200` tasks.

**Ranked Optimizations**

1. Replace N+1 lookups with set-based loading: joins, eager loading, or `WHERE id IN (...)` batches. Highest expected benefit, medium risk around duplicate rows, ordering, and authorization filters.
2. Push report aggregation into fewer DB queries instead of hydrating all objects. High benefit, medium-high risk if business logic currently lives in Python.
3. Add request-scope memoization for repeated user/project/task lookups. Medium benefit, lower risk, but not a substitute for removing N+1.
4. Add or adjust indexes after validating query plans. Medium benefit, low-to-medium risk from write overhead and migration impact.
5. Consider cached/precomputed summaries or pagination if the report does not need fully fresh complete detail. High benefit, higher product/behavior risk.
6. Optimize Python assembly only after DB query count and DB time are reduced; current evidence does not justify starting there.

**Benchmark Plan**

Baseline the current endpoint with tracing enabled on representative large accounts. Then test each optimization independently on commodity-like hardware with cold and warm cache runs. Compare query count, DB time, total latency, throughput, correctness, DB CPU/I/O, connection pool wait, and memory. Run concurrency tests until p95 crosses the `1500ms` budget.

**Rollback Criteria**

Roll back or disable behind a feature flag if p95 exceeds budget, query count rises materially, DB CPU/I/O or connection wait worsens, error rate increases, report results differ from baseline, memory grows unexpectedly, or stale/incomplete report data appears.

Success means p95 under `1500ms`, materially lower query count, lower DB time, stable correctness, and no throughput regression under target load.
