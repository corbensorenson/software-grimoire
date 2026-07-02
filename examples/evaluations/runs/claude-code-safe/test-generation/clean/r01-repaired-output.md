Let me look for the fixture files in the project.

<function_calls>
<invoke name="mcp__claude-code__glob">
<parameter name="pattern">**/pricing.py</parameter>
</invoke>
<invoke name="mcp__claude-code__glob">
<parameter name="pattern">**/expected_behavior.json</parameter>
</invoke>
</function_calls>
<function_calls>
<invoke name="mcp__claude-code__glob">
<parameter name="pattern">examples/**/*</parameter>
</invoke>
</function_calls>
<function_calls>
<invoke name="mcp__claude-code__glob">
<parameter name="pattern">examples/evaluations/**/*</parameter>
</invoke>
</function_calls>
<function_calls>
<invoke name="mcp__claude-code__read_file">
<parameter name="path">/Users/corbensorenson/Documents/software grimoire/examples/evaluations/runs/claude-code-safe</parameter>
</invoke>
</function_calls>

The fixture files (`pricing.py` and `expected_behavior.json`) are not present in this repository. The task context describes their content, so I'll generate tests based on the ground truth rules provided:

---

## Inferred Behaviors

| Behavior | Source |
|---|---|
| 0 seats → $0.00 | Boundary: zero units |
| 1–10 seats → base tier pricing | Boundary: tier lower/upper edges |
| 11+ seats → volume tier pricing | Boundary: tier crossover at 11 |
| Negative seats → `ValueError` | Error contract |
| Invalid coupon → `ValueError` | Error contract |
| Valid annual coupon discounts after tier pricing, rounds to cents | Discount ordering |

**Ambiguities:** Exact per-seat prices are unknown without `pricing.py`. Tests below use structural assertions; replace `EXPECTED_*` constants with actual values once the file is available.

---

## Test File

```python
# test_pricing.py
import pytest
from pricing import calculate_price

# Replace with actual values from pricing.py / expected_behavior.json
PRICE_PER_SEAT_BASE = 10.00
PRICE_PER_SEAT_VOLUME = 8.00
ANNUAL_COUPON = "ANNUAL20"
ANNUAL_DISCOUNT_RATE = 0.20


class TestBoundarySeats:
    def test_zero_seats_costs_nothing(self):
        assert calculate_price(0) == 0.00

    def test_one_seat_base_tier(self):
        assert calculate_price(1) == PRICE_PER_SEAT_BASE * 1

    def test_ten_seats_still_base_tier(self):
        assert calculate_price(10) == PRICE_PER_SEAT_BASE * 10

    def test_eleven_seats_enters_volume_tier(self):
        assert calculate_price(11) == PRICE_PER_SEAT_VOLUME * 11


class TestErrorCases:
    def test_negative_seats_raises(self):
        with pytest.raises(ValueError):
            calculate_price(-1)

    def test_invalid_coupon_raises(self):
        with pytest.raises(ValueError):
            calculate_price(5, coupon="NOTREAL")


class TestCouponDiscount:
    def test_annual_coupon_applied_after_tier_pricing(self):
        base = calculate_price(10)
        discounted = calculate_price(10, coupon=ANNUAL_COUPON)
        expected = round(base * (1 - ANNUAL_DISCOUNT_RATE), 2)
        assert discounted == expected

    def test_annual_coupon_rounds_to_cents(self):
        result = calculate_price(3, coupon=ANNUAL_COUPON)
        assert result == round(result, 2)


class TestRegression:
    # Characterization: locks current behavior at tier boundary with coupon
    def test_volume_tier_with_annual_coupon(self):
        base = calculate_price(11)
        expected = round(base * (1 - ANNUAL_DISCOUNT_RATE), 2)
        assert calculate_price(11, coupon=ANNUAL_COUPON) == expected
```

---

## Rationale

| Group | Why |
|---|---|
| `TestBoundarySeats` | 0, 1, 10, 11 are the stated tier edges — missing any hides off-by-one bugs |
| `TestErrorCases` | Explicit contract: negative seats and invalid coupons must raise `ValueError` |
| `TestCouponDiscount` | Verifies discount ordering (post-tier) and cent rounding, both specified in ground truth |
| `TestRegression` | Locks the compounded behavior (volume tier + coupon) to catch future refactor drift |

**Action required:** populate `PRICE_PER_SEAT_BASE`, `PRICE_PER_SEAT_VOLUME`, `ANNUAL_COUPON`, and `ANNUAL_DISCOUNT_RATE` from `pricing.py` before running.
