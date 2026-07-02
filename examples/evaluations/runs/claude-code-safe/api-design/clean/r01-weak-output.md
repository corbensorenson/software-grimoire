## Billing API Design

### Versioning

All endpoints are versioned via URL prefix: `/v1/`. Breaking changes increment the major version. Mobile clients on older versions continue to receive responses in their requested schema via `Accept: application/vnd.billing.v1+json`.

---

### Payments

```
POST /v1/payments
Headers: Idempotency-Key: <uuid>   # required; server rejects duplicates within 24h
Body: { amount, currency, source, metadata }
Response: { id, status, created_at }
```

Idempotency keys are **required** — the server returns `400 MISSING_IDEMPOTENCY_KEY` if absent. Replaying the same key within the TTL returns the original response without side effects.

---

### Invoices

```
POST   /v1/invoices
GET    /v1/invoices/{id}
GET    /v1/invoices?cursor=&limit=   # paginated
PATCH  /v1/invoices/{id}             # draft updates only
```

Invoice lifecycle states: `draft → open → paid | void`. The `status` field is stable and machine-readable.

---

### Refunds

```
POST  /v1/refunds
Headers: Idempotency-Key: <uuid>   # required
Body: { payment_id, amount, reason }

GET   /v1/refunds/{id}
GET   /v1/refunds?cursor=&limit=
```

Refunds are a **separate resource** linked to a payment, not a sub-action of `Invoice`. A refund transitions through `pending → succeeded | failed`. When a refund succeeds, the linked invoice transitions to `refunded` — this is the lifecycle link between the two resources.

---

### Pagination

All list endpoints use cursor-based pagination:

```json
{
  "data": [...],
  "next_cursor": "opaque_token",
  "has_more": true
}
```

No offset pagination — it breaks under concurrent writes and is incompatible with the slow-upgrading client guarantee.

---

### Error Responses

Every error returns a stable, machine-readable `code`:

```json
{
  "error": {
    "code": "CARD_DECLINED",
    "message": "Human-readable detail.",
    "request_id": "req_abc123"
  }
}
```

`message` may change; `code` is a **stable contract**. Error codes are documented and semver-protected. Example codes: `MISSING_IDEMPOTENCY_KEY`, `INVALID_AMOUNT`, `INVOICE_NOT_FOUND`, `REFUND_EXCEEDS_ORIGINAL`.

---

### Compatibility Contract

| Concern | Mechanism |
|---|---|
| Slow-upgrading mobile clients | URL versioning + additive-only field changes |
| Duplicate payment prevention | Required `Idempotency-Key` header |
| Stable error handling | Machine-readable `code` field, never removed |
| Large result sets | Cursor pagination on all list endpoints |
| Refund/invoice coupling | Separate resources with shared `status` transitions |
