Requests are timing out because the new deploy likely put a Redis-dependent path in the request flow, probably via `profile_cache_v2=true`, and Redis is repeatedly hitting its `250ms` timeout.

That creates latency amplification:

- Each Redis timeout costs ~250 ms before the app can continue.
- If checkout performs multiple profile/cache reads, or retries them, those timeouts stack.
- When Redis misses/fails, the app may fall back to PostgreSQL, where some queries are already taking `900ms+`.
- The combined Redis wait + fallback DB latency pushes checkout past its request deadline, raising p95 from `180 ms` to `2.4 s`.

The low error rate fits this: the app may be recovering from Redis failures instead of returning errors, but it is doing so too slowly. So users see timeouts even though the service is technically handling many failures internally.

Most likely cause: `profile_cache_v2=true` introduced or changed synchronous Redis usage on the checkout path, and Redis timeouts/fallback behavior are exhausting the latency budget.

What is missing to prove it definitively: traces per checkout request, Redis command latency, retry counts, connection pool metrics, and whether disabling `profile_cache_v2` restores latency.
