**Inferred Behaviors**

Only these obligations are inferable from the supplied context:

- Seat count must not allow negative values.
- Coupon rejection is observable behavior and should be tested.
- Monetary output likely involves rounding.
- A discount boundary exists between `10` and `11` seats.
- Tests should cover nominal, boundary, error, and regression-style behavior.

**Ambiguities / Missing Inputs**

I cannot generate an executable, accurate test file because the supplied function is missing:

- Function name and module path
- Signature and parameter names
- Return type and shape
- Valid coupon values and invalid coupon behavior
- Pricing formula
- Expected exception types/messages
- Exact rounding rule
- Exact discount rule at `10` vs `11` seats

Because those facts are not provided, asserting exact prices or exceptions would invent behavior.

**Test File**

```python
# test_pricing_behavior.py
"""
Characterization test scaffold.

Replace:
- `MODULE_UNDER_TEST`
- `FUNCTION_UNDER_TEST`
- expected return values
- expected exception types

with facts from the supplied function's public behavior.
"""

import pytest

from MODULE_UNDER_TEST import FUNCTION_UNDER_TEST


class TestPricingBehavior:
    def test_nominal_quote_without_coupon(self):
        """Nominal: valid positive seat count without coupon returns a stable public result."""
        result = FUNCTION_UNDER_TEST(seats=1)

        assert result == EXPECTED_ONE_SEAT_PRICE

    def test_nominal_quote_with_accepted_coupon(self):
        """Nominal: accepted coupon affects the observable quoted price."""
        result = FUNCTION_UNDER_TEST(seats=5, coupon=VALID_COUPON)

        assert result == EXPECTED_FIVE_SEAT_DISCOUNTED_PRICE

    def test_negative_seats_are_rejected(self):
        """Error: negative seats must not produce a quote."""
        with pytest.raises(EXPECTED_EXCEPTION_TYPE):
            FUNCTION_UNDER_TEST(seats=-1)

    def test_invalid_coupon_is_rejected(self):
        """Error: invalid coupons must not silently apply or be ignored if rejection is required."""
        with pytest.raises(EXPECTED_EXCEPTION_TYPE):
            FUNCTION_UNDER_TEST(seats=5, coupon=INVALID_COUPON)

    def test_discount_boundary_at_ten_seats(self):
        """Boundary: 10 seats should preserve pre-threshold pricing behavior."""
        result = FUNCTION_UNDER_TEST(seats=10)

        assert result == EXPECTED_TEN_SEAT_PRICE

    def test_discount_boundary_at_eleven_seats(self):
        """Boundary: 11 seats should exercise the post-threshold discount behavior."""
        result = FUNCTION_UNDER_TEST(seats=11)

        assert result == EXPECTED_ELEVEN_SEAT_PRICE

    def test_rounding_regression(self):
        """Regression-style: fractional monetary calculations round according to public behavior."""
        result = FUNCTION_UNDER_TEST(seats=ROUNDING_TRIGGER_SEATS, coupon=ROUNDING_TRIGGER_COUPON)

        assert result == EXPECTED_ROUNDED_PRICE
```

**Rationale**

These groups directly target the planted failure modes: negative seats, coupon rejection, rounding, and the `10` to `11` discount boundary. Exact assertions must wait for the actual function contract.
