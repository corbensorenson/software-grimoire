# Spell of Performance Tuning

- id: `spell.performance-tuning.v1`
- version: `1`
- working seal: `spell://performance-tuning/75981D9E3F`
- use when: Use when latency or throughput needs disciplined measurement before optimization.

## Template

```text
ROLE:
Act as a performance engineer.

OBJECTIVE:
Identify the most likely causes of latency or throughput loss in the supplied code or system description and propose optimizations ranked by expected benefit versus risk.

CONTEXT:
The service has a strict latency budget and runs on commodity cloud hardware. A profiler or benchmark may or may not be available.

CONSTRAINTS:
Do not recommend micro-optimizations before addressing algorithmic or I/O-bound issues.

Separate CPU, memory, allocation, database, and network effects. Mention measurement strategy.

PROCEDURE:
First classify the probable bottleneck class. Then propose measurement steps. After that, list optimization candidates in descending order of expected value.

Note when an optimization trades readability, portability, or safety for speed.

OUTPUT CONTRACT:
Return:

1\. bottleneck hypotheses,

2\. what to measure,

3\. optimization options ranked by expected payoff,

4\. benchmark plan,

5\. rollback criteria.

VERIFICATION:
State how success will be measured and what regression risks need to be watched.

FAILURE BEHAVIOR:
If evidence is insufficient, say what profile, trace, or benchmark data would most improve the recommendation.
```
