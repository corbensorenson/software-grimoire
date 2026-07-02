You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Decoy Database Latency Trap

Trap: A PostgreSQL warning appears near the timeout window, but Redis pool exhaustion remains the planted primary cause.

Expected weak failure: Weak analysis ranks the noisy database warning above the actual Redis saturation signal.

USER REQUEST:
Why are requests timing out?
