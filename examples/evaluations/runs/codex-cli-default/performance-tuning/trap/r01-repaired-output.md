**Bottleneck Hypotheses**

1. **Repeated database access / N+1 query pattern**: Most likely production bottleneck. Even if a Python loop appears slow locally, repeated DB round trips can dominate latency on commodity cloud hardware.
2. **I/O wait and network latency to the database**: Query count, connection reuse, lock waits, and result size may be driving tail latency.
3. **Inefficient data access shape**: Fetching too much data, missing indexes, or repeated lookups inside request paths.
4. **Allocation or serialization overhead**: Possible secondary cost if large result sets are materialized repeatedly.
5. **Python loop cost**: Do not optimize yet. Only consider after query count, DB time, network time, and allocation costs are isolated.

**What To Measure**

Need the following before recommending code-level tuning:

- Per-request query count.
- Total DB time per request.
- Individual query latency distribution: p50, p95, p99.
- Duplicate query fingerprints within a request.
- Rows scanned, rows returned, and execution plans.
- Connection pool wait time and saturation.
- Network round-trip time to DB.
- CPU time vs wall-clock time in the application.
- Allocation volume and serialization/deserialization time.
- End-to-end request traces with spans for app code, DB, cache, and network.

**Ranked Optimization Options**

1. **Eliminate repeated DB calls**
   - Batch queries, prefetch related records, or replace per-item lookups with set-based queries.
   - Expected benefit: very high.
   - Risk: medium, because data-shape changes can affect correctness.

2. **Add or fix database indexes based on query plans**
   - Only after confirming slow scans or poor plans.
   - Expected benefit: high.
   - Risk: medium; watch write amplification and migration impact.

3. **Cache stable or repeated reads**
   - Request-scoped cache first, then shared cache if safe.
   - Expected benefit: medium to high.
   - Risk: medium; stale data and invalidation complexity.

4. **Reduce payload and materialization cost**
   - Select only needed columns, paginate, stream large results.
   - Expected benefit: medium.
   - Risk: low to medium.

5. **Optimize Python loop**
   - Only after I/O, DB, allocation, and network effects are separated.
   - Expected benefit: unknown, likely lower.
   - Risk: low, but can waste effort and obscure the real issue.

**Benchmark Plan**

Create representative load tests with production-like data volume. Capture baseline p50/p95/p99 latency, throughput, query count, DB time, CPU, memory, and error rate. Test each optimization independently behind a feature flag or isolated branch. Compare against baseline under equal concurrency.

**Success Measurement**

Success means lower p95/p99 latency, fewer DB round trips, reduced DB time per request, and stable or improved throughput without increased errors.

**Regressions To Watch**

Watch correctness, stale reads, increased memory, connection pool saturation, DB CPU, lock waits, write latency, cache miss storms, and worse tail latency.

**Rollback Criteria**

Rollback if p95/p99 latency worsens, error rate rises, DB load increases materially, memory grows unexpectedly, or correctness checks fail.
