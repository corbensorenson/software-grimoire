You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A containerized API had p95 latency jump from 180 ms to 2.4 s after a deploy. Logs show repeated `redis timeout after 250ms`, occasional PostgreSQL queries over 900 ms, and a new feature flag `profile_cache_v2=true`. Error rate is low, but checkout requests are timing out.

USER REQUEST:
ROLE: Act as a production incident analyst.

OBJECTIVE: Narrow the most likely causes of the timeout spike and say what evidence would distinguish them.

CONTEXT: A web API talks to Redis and PostgreSQL. Latency increased in the last hour. Logs are partial.

CONSTRAINTS: Do not claim a root cause unsupported by supplied evidence. Separate fact, hypothesis, and missing signal.

OUTPUT CONTRACT: Return ranked hypotheses, evidence already present, missing evidence, and the next three commands or dashboards to inspect.

VERIFICATION: Every factual claim must cite an observed symptom or be labeled hypothesis.

FAILURE BEHAVIOR: If the evidence is insufficient, say insufficient and identify the minimum additional signals needed.
