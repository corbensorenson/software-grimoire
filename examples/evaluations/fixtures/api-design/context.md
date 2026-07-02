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
