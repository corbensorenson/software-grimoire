You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
clean longitudinal fixture

TASK CONTEXT:
The fixture describes a public billing API that must remain compatible with slow-upgrading clients.

Files:

- `requirements.json`: product and compatibility requirements.
- `client_contracts.json`: existing client assumptions.
- `ground_truth.json`: planted compatibility traps.

Ground truth:

- Payment attempts need idempotency keys.
- Error responses need stable machine-readable codes.
- List endpoints need pagination.
- Mobile clients require backward-compatible versioning.
- Refunds and invoices are separate resources with linked lifecycle state.

USER REQUEST:
ROLE: Act as a backend architect designing a public JSON API.

OBJECTIVE: Produce a boring, versionable billing API that supports invoices, payment attempts, refunds, and idempotent retries.

CONTEXT: Mobile and web clients; PostgreSQL storage; slow client upgrade cadence; OAuth-based auth.

CONSTRAINTS: Preserve backward compatibility, include pagination and error schema, prefer boring patterns over novelty.

OUTPUT CONTRACT: Return endpoint table, request/response examples, auth notes, idempotency notes, migration/versioning notes.

VERIFICATION: Call out race conditions, retry hazards, and compatibility risks.

FAILURE BEHAVIOR: If the resource model is underspecified, list assumptions explicitly before designing.
