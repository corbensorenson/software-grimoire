You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A containerized API had p95 latency jump from 180 ms to 2.4 s after a deploy. Logs show repeated `redis timeout after 250ms`, occasional PostgreSQL queries over 900 ms, and a new feature flag `profile_cache_v2=true`. Error rate is low, but checkout requests are timing out.

USER REQUEST:
Why are requests timing out?
