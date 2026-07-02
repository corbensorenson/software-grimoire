You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
The fixture is a report endpoint performance packet.

Files:

- `trace.json`: representative trace showing query count and timing.
- `workload.json`: target latency budget and data scale.
- `ground_truth.json`: planted bottlenecks and misleading path.

Ground truth:

- The planted primary bottleneck is database query count/N+1 behavior, not Python loop micro-optimization.
- A good answer measures first, asks for profiling/tracing, and ranks optimizations by risk and expected benefit.
- A good answer names rollback or regression criteria before changing production behavior.

USER REQUEST:
ROLE: Act as a performance engineer.

OBJECTIVE: Identify the most likely latency or throughput bottlenecks and propose optimizations ranked by expected benefit versus risk.

CONTEXT: The service has a strict latency budget and runs on commodity cloud hardware. Profiling data may be incomplete.

CONSTRAINTS: Do not recommend micro-optimizations before algorithmic, I/O, allocation, database, or network effects are separated.

OUTPUT CONTRACT: Return bottleneck hypotheses, what to measure, ranked optimization options, benchmark plan, and rollback criteria.

VERIFICATION: State how success will be measured and which regressions must be watched.

FAILURE BEHAVIOR: If evidence is insufficient, name the profile, trace, or benchmark data needed before recommending changes.
