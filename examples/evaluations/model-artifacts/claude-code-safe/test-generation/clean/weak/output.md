```python
from decimal import Decimal
import pytest
from pricing import price_for


def test_free_plan_zero_seats():
    assert price_for("free", 0) == Decimal("0.00")


def test_free_plan_many_seats():
    assert price_for("free", 100) == Decimal("0.00")


def test_team_zero_seats():
    assert price_for("team", 0) == Decimal("0.00")


def test_team_one_seat():
    assert price_for("team", 1) == Decimal("12.00")


def test_team_ten_seats_no_discount():
    assert price_for("team", 10) == Decimal("120.00")


def test_team_eleven_seats_bulk_discount():
    # 11 seats: 10 * 12 + 1 * 10 = 130
    assert price_for("team", 11) == Decimal("130.00")


def test_team_twenty_seats_bulk_discount():
    # 10 * 12 + 10 * 10 = 220
    assert price_for("team", 20) == Decimal("220.00")


def test_enterprise_zero_seats():
    assert price_for("enterprise", 0) == Decimal("99.00")


def test_enterprise_one_seat():
    assert price_for("enterprise", 1) == Decimal("107.00")


def test_enterprise_ten_seats():
    assert price_for("enterprise", 10) == Decimal("179.00")


def test_negative_seats_raises():
    with pytest.raises(ValueError):
        price_for("team", -1)


def test_unknown_coupon_raises():
    with pytest.raises(ValueError):
        price_for("team", 5, coupon="BOGUS")


def test_unknown_plan_raises():
    with pytest.raises(ValueError):
        price_for("unknown", 5)


def test_annual10_free_plan():
    assert price_for("free", 5, coupon="ANNUAL10") == Decimal("0.00")


def test_annual10_team_ten_seats():
    # 120 * 0.90 = 108.00
    assert price_for("team", 10, coupon="ANNUAL10") == Decimal("108.00")


def test_annual10_team_eleven_seats():
    # 130 * 0.90 = 117.00
    assert price_for("team", 11, coupon="ANNUAL10") == Decimal("117.00")


def test_annual10_enterprise_rounds_to_cents():
    # enterprise 1 seat: 107 * 0.90 = 96.30
    assert price_for("enterprise", 1, coupon="ANNUAL10") == Decimal("96.30")


def test_annual10_rounding():
    # enterprise 3 seats: (99 + 24) * 0.90 = 110.7 -> 110.70
    assert price_for("enterprise", 3, coupon="ANNUAL10") == Decimal("110.70")


def test_no_coupon_is_default():
    assert price_for("team", 5) == price_for("team", 5, coupon=None)
```
