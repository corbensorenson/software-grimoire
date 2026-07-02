# Decoy Database Latency Trap

Trap: A PostgreSQL warning appears near the timeout window, but Redis pool exhaustion remains the planted primary cause.

Expected weak failure: Weak analysis ranks the noisy database warning above the actual Redis saturation signal.
