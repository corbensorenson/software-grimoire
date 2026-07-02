The fixture is a report endpoint performance packet.

Files:

- `trace.json`: representative trace showing query count and timing.
- `workload.json`: target latency budget and data scale.
- `ground_truth.json`: planted bottlenecks and misleading path.

Ground truth:

- The planted primary bottleneck is database query count/N+1 behavior, not Python loop micro-optimization.
- A good answer measures first, asks for profiling/tracing, and ranks optimizations by risk and expected benefit.
- A good answer names rollback or regression criteria before changing production behavior.
