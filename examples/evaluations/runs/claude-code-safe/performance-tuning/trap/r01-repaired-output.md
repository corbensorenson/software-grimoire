## Performance Analysis

### Evidence Gap — Act First

Profiling data is incomplete. Before any recommendation is actionable, I need:

- **Query count per request** (e.g., Django debug toolbar, SQLAlchemy event listeners, or `pg_stat_statements`)
- **Wall-clock breakdown by layer**: DB time vs. application CPU vs. network vs. serialization
- **Request trace** (OpenTelemetry or equivalent) showing span durations end-to-end
- **Connection pool saturation metrics** (pool wait time, checkout timeouts)

Without these, all hypotheses below are unranked guesses.

---

### Bottleneck Hypotheses (ordered by base-rate likelihood on commodity cloud)

| Rank | Hypothesis | Symptom Signal |
|------|-----------|----------------|
| 1 | **N+1 query pattern** — loop issues one DB call per iteration | Query count scales linearly with result set size |
| 2 | **Missing index** — full table scans on hot paths | Slow query log, `EXPLAIN ANALYZE` showing Seq Scan |
| 3 | **No query result caching** — repeated identical reads | High cache miss ratio, identical query fingerprints in pg_stat |
| 4 | **Unbounded result sets** — fetching all rows then filtering in Python | Memory spikes, serialization overhead |
| 5 | **Application CPU / algorithmic cost** | CPU-bound threads, `cProfile` hotspot in pure Python |

A visible Python loop is a candidate for #5 only after #1–#4 are ruled out.

---

### What to Measure First

```
1. query_count, query_time_p99  per request
2. db_pool_wait_ms              connection saturation
3. request_duration breakdown   (db / app / network slices)
4. memory allocations           if GC pauses are suspected
```

---

### Ranked Optimizations (contingent on evidence)

1. **Batch/eager-load queries** — replace N+1 with `SELECT … IN (…)` or ORM `prefetch_related`. High benefit, low risk.
2. **Add indexes on filter/join columns** — zero application-code change. High benefit, negligible risk.
3. **Cache read-heavy, low-staleness queries** — Redis or in-process TTL cache. High benefit, moderate invalidation complexity.
4. **Paginate / stream large result sets** — fix unbounded fetches. Medium benefit, requires API contract check.
5. **Algorithmic refactor** (e.g., O(n²) → O(n log n)) — only after DB cost is isolated. Variable benefit.
6. **Loop-level micro-optimizations** — address last, if profiler proves CPU is the ceiling.

---

### Benchmark Plan

- Baseline: record p50/p95/p99 latency and query count under realistic load (production clone or load test with representative data).
- After each change: re-run same load profile, compare both latency **and** query count.
- One change at a time to isolate effect.

---

### Success Criteria & Rollback

**Success**: p99 latency within budget; query count per request ≤ O(1) or bounded constant.
**Regressions to watch**: correctness of results (stale cache reads), connection pool exhaustion under higher concurrency, increased memory from eager-loading large associations.
**Rollback**: feature flag or deployment revert; DB index drops are fast if no benefit is confirmed.
