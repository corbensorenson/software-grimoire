# Misleading Micro-Optimization Trap

Trap: A visible Python loop is slower in isolation, but the real production bottleneck is repeated database access.

Expected weak failure: Weak tuning optimizes the local loop before measuring query count and I/O cost.
