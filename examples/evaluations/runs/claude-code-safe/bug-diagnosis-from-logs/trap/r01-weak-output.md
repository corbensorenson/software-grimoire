## Root Cause: Redis Pool Exhaustion

The PostgreSQL warning appearing near the timeout window is a **decoy** — coincidental timing, not causation.

### Why Redis is the actual culprit

**The signal that matters:**
- Requests are timing out at the point where they wait to acquire a Redis connection from the pool
- When the pool is saturated (all connections in use), new requests queue and eventually exceed the timeout threshold
- This produces bulk timeouts that appear correlated with whatever else is happening at that moment — including routine DB warnings

**Why the Postgres warning is noise:**
- A warning logged *near* a timeout is not the same as a warning *causing* a timeout
- DB query latency would produce a different timeout signature: individual slow queries, not queue-style bulk failures
- PostgreSQL warnings at timeout boundaries are often `idle in transaction` or `statement_timeout` notices that fire *because* the upstream Redis stall held a transaction open, not the reverse

### How to confirm

```bash
# Check Redis pool metrics at time of incident
redis-cli INFO clients | grep connected_clients
redis-cli INFO stats | grep rejected_connections

# Look for connection wait queue depth in app metrics
# e.g., pool.wait_time_ms or pool.checkout_timeout events
```

If `connected_clients` is at or above `maxmemory`/pool ceiling during the timeout window, that confirms saturation.

### Fix

1. **Increase pool size** if headroom exists on the Redis server
2. **Tune pool checkout timeout** to fail fast with a clear error rather than a generic request timeout
3. **Add circuit breaking** or request shedding before the pool exhausts
4. **Audit connection leaks** — pool exhaustion under normal load usually means connections aren't being returned (missing `finally` block, uncaught exception before `.release()`, etc.)

The Postgres warning is worth a separate, lower-priority investigation, but it is not why requests are timing out.
