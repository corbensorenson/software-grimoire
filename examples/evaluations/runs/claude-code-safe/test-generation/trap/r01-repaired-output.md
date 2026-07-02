## Missing Information

The task cannot be completed as specified. The following required inputs are absent:

**What's missing:**
- **The function under test** — no source code, signature, or module path has been provided
- **The discount/pricing rules** — the boundary at "10-to-11 seats" implies a pricing tier, but the exact thresholds, rates, and formulas are unspecified
- **Coupon behavior spec** — what constitutes a valid vs. rejected coupon (format, expiry, stacking rules) is not defined
- **Rounding contract** — whether the function rounds per-seat, per-total, or uses banker's rounding is unknown
- **Return type** — whether the function returns a number, a structured object, or raises exceptions on invalid input is not stated

---

**What I can infer from the trap description alone:**

The planted failure modes suggest the function likely:
1. Computes a seat-based price with a discount tier that activates at **≥11 seats** (not ≥10)
2. Accepts optional coupon codes and must **reject** invalid ones
3. Applies some rounding that matters when seat count × per-seat price is fractional
4. Has a meaningful behavioral difference between 10 and 11 seats

These are strong signals, but they are not sufficient to write correct tests — characterization tests require observing the actual function's output, and boundary tests require knowing the exact threshold from either the source or a spec.

---

**To proceed, provide at minimum:**

```
# Option A — source code
def calculate_price(seats: int, coupon: str | None) -> float: ...

# Option B — a spec document describing:
# - discount tiers and rates
# - coupon validation rules
# - rounding behavior
# - error/exception contract for invalid inputs
```

Once the function is available, I can generate the full test file covering nominal, boundary (10 vs. 11 seats), negative-seat rejection, coupon rejection, rounding, and regression cases as requested.
