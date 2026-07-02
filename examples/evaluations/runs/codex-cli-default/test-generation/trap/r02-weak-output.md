I can’t write the file in this read-only sandbox, but the test file should look like this:

```python
import pytest
from decimal import Decimal

from pricing import price_for


@pytest.mark.parametrize(
    ("plan", "seats", "coupon", "expected"),
    [
        ("free", 0, None, Decimal("0.00")),
        ("free", 25, "ANNUAL10", Decimal("0.00")),
        ("team", 0, None, Decimal("0.00")),
        ("team", 1, None, Decimal("12.00")),
        ("team", 10, None, Decimal("120.00")),
        ("team", 11, None, Decimal("130.00")),
        ("enterprise", 0, None, Decimal("99.00")),
        ("enterprise", 1, None, Decimal("107.00")),
        ("team", 10, "ANNUAL10", Decimal("108.00")),
        ("team", 11, "ANNUAL10", Decimal("117.00")),
        ("enterprise", 1, "ANNUAL10", Decimal("96.30")),
    ],
)
def test_price_for_public_pricing_cases(plan, seats, coupon, expected):
    assert price_for(plan, seats, coupon=coupon) == expected


def test_team_discount_starts_after_ten_seats():
    assert price_for("team", 10) == Decimal("120.00")
    assert price_for("team", 11) == Decimal("130.00")
    assert price_for("team", 11) - price_for("team", 10) == Decimal("10.00")


@pytest.mark.parametrize("seats", [-1, -10])
def test_negative_seats_raise_value_error(seats):
    with pytest.raises(ValueError, match="seats"):
        price_for("team", seats)


@pytest.mark.parametrize("coupon", ["SAVE10", "", "annual10"])
def test_unknown_coupons_raise_value_error(coupon):
    with pytest.raises(ValueError, match="coupon"):
        price_for("team", 1, coupon=coupon)


def test_unknown_plan_raises_value_error():
    with pytest.raises(ValueError, match="plan"):
        price_for("pro", 1)


def test_coupon_result_is_quantized_to_cents():
    result = price_for("enterprise", 1, coupon="ANNUAL10")

    assert result == Decimal("96.30")
    assert result.same_quantum(Decimal("0.01"))
```

This covers the trap cases: negative seats, coupon rejection, cent quantization, and the 10-to-11 team discount boundary.
