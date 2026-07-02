You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A report endpoint now takes 9 seconds for large accounts. It fetches projects, tasks, comments, and users from PostgreSQL, then builds a nested JSON response. There is no profile yet. The team suspects Python loops, but database query count may have changed.

USER REQUEST:
ROLE: Act as a performance engineer.

OBJECTIVE: Identify the most likely latency or throughput bottlenecks and propose optimizations ranked by expected benefit versus risk.

CONTEXT: The service has a strict latency budget and runs on commodity cloud hardware. Profiling data may be incomplete.

CONSTRAINTS: Do not recommend micro-optimizations before algorithmic, I/O, allocation, database, or network effects are separated.

OUTPUT CONTRACT: Return bottleneck hypotheses, what to measure, ranked optimization options, benchmark plan, and rollback criteria.

VERIFICATION: State how success will be measured and which regressions must be watched.

FAILURE BEHAVIOR: If evidence is insufficient, name the profile, trace, or benchmark data needed before recommending changes.
