## Billing API Design (v1)

### Assumptions (resource model was underspecified)

- Invoices are immutable once finalized; line items are set at creation.
- A PaymentAttempt is a child of Invoice; refunds are children of a PaymentAttempt.
- Idempotency keys are client-supplied, stored server-side for 24 hours minimum.
- OAuth scopes: `billing:read`, `billing:write`, `billing:admin`.

---

### Endpoint Table

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/v1/invoices` | billing:read | List invoices (paginated) |
| POST | `/v1/invoices` | billing:write | Create invoice |
| GET | `/v1/invoices/{id}` | billing:read | Get invoice |
| POST | `/v1/invoices/{id}/payment-attempts` | billing:write | Attempt payment |
| GET | `/v1/invoices/{id}/payment-attempts` | billing:read | List attempts |
| POST | `/v1/payment-attempts/{id}/refunds` | billing:admin | Issue refund |

---

### Error Envelope (stable contract — never change field names)

```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Card was declined by issuer.",
    "request_id": "req_abc123",
    "retryable": false
  }
}
```

`retryable: true` signals the client may safely replay. Always return this field — omission breaks retry logic in existing clients.

---

### Idempotency

- `POST` endpoints require `Idempotency-Key: <uuid>` header.
- Server stores (key → response) in PostgreSQL for **72 hours**.
- Replayed requests return the **exact original response** (same body, same HTTP status).
- If the same key arrives while the original is still processing: return `409 Conflict` with `code: IDEMPOTENCY_CONFLICT`.
- Keys are scoped to `(oauth_client_id, key)` — prevents cross-tenant collisions.

---

### Pagination

```json
{
  "data": [...],
  "pagination": {
    "cursor": "cur_xyz",
    "has_more": true
  }
}
```

Use cursor-based pagination only. Offset pagination is banned — it creates phantom/duplicate rows under concurrent writes.

---

### Race Conditions & Retry Hazards

| Risk | Mitigation |
|------|------------|
| Double-charge on network timeout | Idempotency key deduplication at DB level (unique constraint on key) |
| Refund on already-refunded attempt | Optimistic lock; check `status = 'succeeded'` before issuing |
| Concurrent payment attempts on same invoice | DB-level advisory lock on `invoice_id` during attempt creation |
| Stale status read mid-payment | Clients must poll; never trust local cache on terminal states |

---

### Versioning & Migration

- Version in URL path (`/v1/`). Never in headers — harder to route and log.
- **Additive-only changes** (new fields, new optional params) are non-breaking within v1.
- Removing or renaming fields requires `/v2/` with a **minimum 12-month v1 sunset window** — slow mobile upgrade cadence demands this.
- v1 and v2 run simultaneously behind the same gateway; both write to the same PostgreSQL schema using views to isolate breaking changes.
- Deprecation communicated via `Deprecation` and `Sunset` response headers on every v1 response once sunset is announced.
