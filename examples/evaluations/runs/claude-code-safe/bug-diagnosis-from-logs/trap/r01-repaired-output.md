## Incident Analysis: API Timeout Spike

**Evidence supplied:** Latency increased in last hour. Logs are partial. System components: Redis, PostgreSQL.

---

### Ranked Hypotheses

**1. Redis connection pool exhaustion** *(primary suspect)*
- **Why ranked first:** Pool exhaustion causes synchronous blocking at the connection-acquire step, producing uniform latency increases across all endpoints that touch Redis — a pattern consistent with a broad timeout spike rather than isolated query slowness.
- **Observed support:** None cited yet — this is a **hypothesis** pending pool metric confirmation.

**2. PostgreSQL query degradation** *(secondary)*
- A warning near the timeout window is a **noted signal**, not a root cause. Warnings (e.g., slow query logs, lock waits) can be downstream effects of upstream saturation — if Redis blocks the app thread, open DB connections accumulate, producing secondary DB warnings.
- **Risk of misranking:** Treating this warning as the primary cause without ruling out Redis first is the classic correlation-causation trap.

**3. Application-level thread/worker starvation** *(tertiary)*
- If Redis blocks worker threads, the app appears slow globally regardless of DB state.

---

### Missing Evidence (minimum signals needed)

| Signal | Why critical |
|---|---|
| Redis `INFO stats` → `rejected_connections`, `connected_clients`, `blocked_clients` | Directly confirms/denies pool exhaustion |
| Redis pool config vs. observed concurrent connections | Establishes whether the limit was hit |
| PostgreSQL `pg_stat_activity` snapshot during spike | Distinguishes primary DB degradation from idle connections piling up |
| App-side connection wait time histogram | Shows where time is actually spent |

---

### Next Three Commands

```bash
# 1. Check Redis saturation
redis-cli INFO stats | grep -E 'connected_clients|blocked_clients|rejected_connections'
redis-cli INFO clients

# 2. Check PostgreSQL for lock contention vs. idle accumulation
psql -c "SELECT state, wait_event_type, wait_event, count(*) FROM pg_stat_activity GROUP BY 1,2,3 ORDER BY 4 DESC;"

# 3. Correlate app error logs with component
grep -E 'timeout|pool|exhausted|connection refused' /var/log/app/*.log | awk '{print $1, $2}' | sort | uniq -c | sort -rn | head -20
```

---

### Verdict

**Insufficient evidence to declare root cause.** Redis pool exhaustion is the highest-prior hypothesis given the symptom profile. The PostgreSQL warning is a **candidate red herring** — it must be shown to precede (not follow) the latency spike before it can be ranked above Redis saturation.
