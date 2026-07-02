You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Misleading Micro-Optimization Trap

Trap: A visible Python loop is slower in isolation, but the real production bottleneck is repeated database access.

Expected weak failure: Weak tuning optimizes the local loop before measuring query count and I/O cost.

USER REQUEST:
Make this faster.
