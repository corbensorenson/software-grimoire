**Evidence Gap**

Do not change code yet beyond instrumentation. Needed data: endpoint trace with per-stage timing, SQL query count, per-query duration, `EXPLAIN ANALYZE` for slow queries, payload size, Python CPU profile, allocation profile, DB connection-pool wait time, and p50/p95/p99 latency under representative large accounts.

**Bottleneck Hypotheses**

1. **Database round trips / N+1 queries**
   Query count may have changed. Fetching projects, tasks, comments, and users separately can become many queries or repeated lookups.

2. **Slow SQL plans or missing indexes**
   Large-account filters, joins, ordering, or comment lookups may now scan too many rows.

3. **Row explosion / over-fetching**
   Joining nested entities can multiply rows, increasing DB work, network transfer, Python allocation, and JSON size.

4. **Python assembly complexity**
   Nested loops may be `O(projects * tasks * comments)` instead of using keyed maps/grouping.

5. **Serialization and memory pressure**
   Building one large nested object before encoding can cause high allocation, GC pressure, and latency spikes.

6. **Connection-pool or DB saturation**
   Under load, throughput may be limited by pool waits, DB CPU, I/O, or lock contention.

**What To Measure**

- Request latency split: DB time, Python build time, JSON serialization time, network response time.
- Query count per request and duplicate query signatures.
- Slowest queries with row counts and plans.
- Response size and number of projects/tasks/comments/users.
- CPU profile and allocation profile during report generation.
- DB CPU, I/O, buffer cache hit rate, locks, and pool wait time.
- p50/p95/p99 latency and max RSS under concurrent load.

**Ranked Optimization Options**

1. **Add tracing and query instrumentation**
   Highest benefit-to-risk. Required to separate DB, CPU, allocation, and network effects.

2. **Eliminate N+1 queries and duplicate user/comment/project fetches**
   High benefit, moderate risk. Batch by IDs, use bounded eager loading, or consolidate queries carefully.

3. **Tune SQL plans and indexes**
   High benefit, moderate risk. Add/adjust composite indexes around account ID, project/task/comment foreign keys, and sort/filter columns.

4. **Reduce over-fetching and row explosion**
   High benefit, moderate risk. Fetch only required columns, avoid multiplicative joins, batch child records and group in memory.

5. **Fix Python assembly algorithm**
   Medium-to-high benefit, low-to-moderate risk. Build dictionaries keyed by IDs and append children in linear time.

6. **Optimize serialization/allocation**
   Medium benefit, moderate risk. Stream JSON or use a faster encoder only after DB and algorithmic costs are understood.

7. **Caching or precomputed reports**
   Potentially high benefit, higher product risk. Requires freshness rules and invalidation strategy.

**Benchmark Plan**

Create a representative large-account fixture. Capture baseline p50/p95/p99, query count, DB time, CPU time, memory, and payload size. Test each optimization independently and under realistic concurrency. Verify byte-level or schema-level response equivalence.

**Rollback Criteria**

Rollback if p95/p99 worsens, DB load increases materially, memory grows, connection-pool waits increase, error rate rises, or report JSON changes unexpectedly.

**Success Measures**

Success means the endpoint meets the strict latency budget on large accounts, reduces query count or DB time if DB-bound, reduces CPU/allocation if Python-bound, and does not regress correctness, throughput, memory, or DB health.
