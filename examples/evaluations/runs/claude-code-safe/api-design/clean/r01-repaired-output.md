## Billing API Design

**Assumptions (resource model is fully specified by ground truth):**
- Refunds reference a Payment; Invoices reference a Payment when settled
- Invoice lifecycle: `draft → open → paid | void`
- Payment lifecycle: `pending → succeeded | failed`
- Refund lifecycle: `pending → succeeded | failed`

---

### Endpoint Table

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/invoices` | Create invoice |
| GET | `/v1/invoices` | List invoices (paginated) |
| GET | `/v1/invoices/{id}` | Get invoice |
| POST | `/v1/invoices/{id}/payments` | Attempt payment on invoice |
| GET | `/v1/invoices/{id}/payments` | List payments for invoice |
| GET | `/v1/payments/{id}` | Get payment attempt |
| POST | `/v1/payments/{id}/refunds` | Create refund |
| GET | `/v1/refunds/{id}` | Get refund |

---

### Auth
OAuth 2.0 Bearer tokens on every request. Scope examples: `billing:read`, `billing:write`.

---

### Idempotency
All `POST` requests require `Idempotency-Key: <client-uuid>` header. Server stores key → response for 24h. Replaying an identical key returns the cached response with `Idempotency-Replayed: true`. Mismatched body on replay returns `409 Conflict`.

---

### Request/Response Examples

**POST /v1/invoices/{id}/payments**
```json
// Request
{ "amount_cents": 4999, "currency": "USD", "payment_method_id": "pm_abc" }

// Response 201
{
  "id": "pay_xyz",
  "invoice_id": "inv_abc",
  "status": "succeeded",
  "amount_cents": 4999,
  "currency": "USD",
  "created_at": "2026-07-02T00:00:00Z"
}
```

**Error schema (stable, machine-readable):**
```json
{ "error": { "code": "insufficient_funds", "message": "...", "param": null } }
```
`code` values are frozen per major version. Never remove or rename a code.

---

### Pagination
All list endpoints use cursor-based pagination:
```
GET /v1/invoices?limit=20&starting_after=inv_abc
```
Response includes `{ "data": [...], "has_more": true, "next_cursor": "inv_xyz" }`.
Never use offset pagination — it breaks under concurrent inserts.

---

### Versioning & Migration
- URL-versioned (`/v1/`). Additive changes (new fields, new statuses) are non-breaking.
- Breaking changes (removed fields, renamed codes) require `/v2/`.
- Run both versions in parallel during transition; sunset v1 only after client cadence allows (12+ months minimum given slow-upgrade constraint).
- New optional fields default to `null` on old records.

---

### Race Conditions & Retry Hazards

| Risk | Mitigation |
|------|------------|
| Double-charge on network retry | Idempotency key + DB unique constraint on key |
| Payment succeeded but webhook lost | Client polls `GET /v1/payments/{id}` before retrying |
| Refund on already-refunded payment | Check refunded amount ≤ captured amount in DB transaction |
| Invoice voided mid-payment | Pessimistic lock on invoice row during payment attempt |
