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
ROLE: Act as a backend architect designing a public JSON API.

OBJECTIVE: Produce a boring, versionable billing API that supports invoices, payment attempts, refunds, and idempotent retries.

CONTEXT: Mobile and web clients; PostgreSQL storage; slow client upgrade cadence; OAuth-based auth.

CONSTRAINTS: Preserve backward compatibility, include pagination and error schema, prefer boring patterns over novelty.

OUTPUT CONTRACT: Return endpoint table, request/response examples, auth notes, idempotency notes, migration/versioning notes.

VERIFICATION: Call out race conditions, retry hazards, and compatibility risks.

FAILURE BEHAVIOR: If the resource model is underspecified, list assumptions explicitly before designing.
