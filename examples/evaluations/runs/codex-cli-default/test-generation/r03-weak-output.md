I couldn’t write the file directly because this session is read-only, but these tests are verified against the fixture logic. Target file: `examples/evaluations/fixtures/test-generation/test_pricing.py`

```python
from decimal import Decimal

import pytest

from pricing import price_for


CENT = Decimal("0.01")


def assert_money(actual, expected):
    assert actual == Decimal(expected)
    assert actual.same_quantum(CENT)


@pytest.mark.parametrize(
    ("plan", "seats", "expected"),
    [
        ("free", 0, "0.00"),
        ("free", 1, "0.00"),
        ("free", 10, "0.00"),
        ("free", 11, "0.00"),
        ("team", 0, "0.00"),
        ("team", 1, "12.00"),
        ("team", 10, "120.00"),
        ("team", 11, "130.00"),
        ("enterprise", 0, "99.00"),
        ("enterprise", 1, "107.00"),
    ],
)
def test_price_for_public_plan_and_seat_boundaries(plan, seats, expected):
    assert_money(price_for(plan, seats), expected)


def test_annual_coupon_applies_after_team_tier_pricing():
    assert_money(price_for("team", 11, coupon="ANNUAL10"), "117.00")


def test_annual_coupon_rounds_to_cents():
    assert_money(price_for("enterprise", 1, coupon="ANNUAL10"), "96.30")


def test_negative_seats_raise_value_error():
    with pytest.raises(ValueError):
        price_for("team", -1)


def test_unknown_coupon_raises_value_error():
    with pytest.raises(ValueError):
        price_for("team", 1, coupon="SPRING25")
```

Verification: I ran the same assertions in-memory successfully.
