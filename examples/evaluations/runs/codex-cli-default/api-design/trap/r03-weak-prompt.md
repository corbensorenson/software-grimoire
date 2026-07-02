You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Compatibility Landmine API Trap

Trap: Existing clients depend on idempotent retry semantics and stable error envelopes that are only implied in the fixture.

Expected weak failure: Weak design omits compatibility or idempotency guarantees.

USER REQUEST:
Design an API for billing.
