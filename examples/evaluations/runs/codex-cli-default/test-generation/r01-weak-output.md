I can’t write the file directly because this workspace is read-only. Add this as `examples/evaluations/fixtures/test-generation/test_pricing.py`:

```python
from decimal import Decimal

import pytest

from pricing import price_for


@pytest.mark.parametrize(
    ("plan", "seats", "expected"),
    [
        ("free", 0, Decimal("0.00")),
        ("free", 1, Decimal("0.00")),
        ("free", 10, Decimal("0.00")),
        ("free", 11, Decimal("0.00")),
        ("team", 0, Decimal("0.00")),
        ("team", 1, Decimal("12.00")),
        ("team", 10, Decimal("120.00")),
        ("team", 11, Decimal("130.00")),
        ("enterprise", 0, Decimal("99.00")),
        ("enterprise", 1, Decimal("107.00")),
        ("enterprise", 10, Decimal("179.00")),
        ("enterprise", 11, Decimal("187.00")),
    ],
)
def test_price_for_supported_plans_at_boundary_seat_counts(plan, seats, expected):
    assert price_for(plan, seats) == expected


def test_price_for_rejects_negative_seats():
    with pytest.raises(ValueError):
        price_for("team", -1)


def test_price_for_rejects_invalid_coupon():
    with pytest.raises(ValueError):
        price_for("team", 1, "NOT_A_COUPON")


def test_annual_coupon_discounts_after_team_tier_pricing():
    assert price_for("team", 11, "ANNUAL10") == Decimal("117.00")


def test_annual_coupon_result_is_rounded_to_cents():
    result = price_for("enterprise", 1, "ANNUAL10")

    assert result == Decimal("96.30")
    assert result.as_tuple().exponent == -2
```

I validated the expected prices against `pricing.py` with an inline import.
