# Codex Task Template: Spell of API Design

Use this as a local instruction snippet for a Codex task. Keep the artifact boundary, verification, and failure behavior visible.

Source: `spell.api-design.v1`

Seal: `spell://api-design/828C8A1237`

```text
ROLE:
Act as a backend architect designing a public JSON API.

OBJECTIVE:
Design an API for the described resource model that is clean, versionable, secure, and observable.

CONTEXT:
Clients include web, mobile, and internal automation. The system uses OAuth-based authorization and PostgreSQL storage.

Backward compatibility matters because mobile clients update slowly.

CONSTRAINTS:
Prefer boring, maintainable patterns over novelty. Include pagination, error schema, idempotency where appropriate,

authorization notes, and migration considerations. Do not hand-wave failure modes.

PROCEDURE:
Start from the resource model and operations. Then define endpoints, request and response schemas,

error codes, pagination, filtering, authorization checks, and observability requirements.

OUTPUT CONTRACT:
Return:

1\. resource model,

2\. endpoint table,

3\. example requests and responses,

4\. error format,

5\. auth model,

6\. migration and versioning notes.

VERIFICATION:
Call out edge cases, race conditions, and compatibility risks.

FAILURE BEHAVIOR:
If the resource model is underspecified, list the assumptions explicitly before designing.
```
