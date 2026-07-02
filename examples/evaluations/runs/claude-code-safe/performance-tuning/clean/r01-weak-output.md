Before touching any code, I need more information. "Make this faster" without measurement context is how you optimize the wrong thing.

## What's missing

I have the fixture file names but not their contents. Please share:
- The actual `trace.json` content (query counts, timing breakdown)
- The actual `workload.json` content (target latency budget, data scale)
- The relevant endpoint code

## How I'd proceed once I have them

**Step 1 — Measure, don't guess.**
Read the trace to find where time is actually spent. A profiler output or query log beats intuition every time. Without this, you risk spending effort on Python loop micro-optimization while an N+1 query pattern burns 80% of your wall time.

**Step 2 — Form a ranked hypothesis list.**
From the fixture description (report endpoint, performance packet), likely candidates in order of expected impact:

| Rank | Candidate | Why it matters |
|------|-----------|----------------|
| 1 | Query count / N+1 behavior | Report endpoints frequently iterate over records and fire per-row queries; multiplicative cost |
| 2 | Missing indexes on filter/join columns | Linear scans on large tables |
| 3 | Serialization / large payload size | Sending more data than the caller needs |
| 4 | Python-side computation loops | Almost never the primary bottleneck vs. DB round-trips |

**Step 3 — Define regression criteria before touching anything.**
For each change, state up front:
- What metric proves it worked (p95 latency, query count, row scan count)
- What rollback looks like (revert the migration, re-enable the old code path, feature flag off)
- What "worse" means so you catch it in staging (e.g., query count increases, or p99 crosses the budget in `workload.json`)

**Step 4 — Change one thing at a time, measure after each.**
If you batch changes and something regresses, you won't know which fix caused it.

---

**Share the trace and endpoint code and I'll give you a concrete diff with the above framework applied.**
