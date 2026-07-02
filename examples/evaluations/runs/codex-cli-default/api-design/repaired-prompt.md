You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
Design the first public billing API for invoices, payment attempts, refunds, and account credits. Clients include web, mobile, and internal automations. Mobile clients update slowly. Auth uses OAuth scopes. Payments must support safe retries.

USER REQUEST:
ROLE: Act as a backend architect designing a public JSON API.

OBJECTIVE: Produce a boring, versionable billing API that supports invoices, payment attempts, refunds, and idempotent retries.

CONTEXT: Mobile and web clients; PostgreSQL storage; slow client upgrade cadence; OAuth-based auth.

CONSTRAINTS: Preserve backward compatibility, include pagination and error schema, prefer boring patterns over novelty.

OUTPUT CONTRACT: Return endpoint table, request/response examples, auth notes, idempotency notes, migration/versioning notes.

VERIFICATION: Call out race conditions, retry hazards, and compatibility risks.

FAILURE BEHAVIOR: If the resource model is underspecified, list assumptions explicitly before designing.
