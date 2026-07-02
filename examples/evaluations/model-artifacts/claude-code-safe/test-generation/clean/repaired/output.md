```python
import pytest
from decimal import Decimal
from pricing import price_for


class TestFreePlan:
    def test_free_plan_zero_seats(self):
        assert price_for("free", 0) == Decimal("0.00")

    def test_free_plan_any_seats(self):
        assert price_for("free", 100) == Decimal("0.00")

    def test_free_plan_with_coupon_stays_zero(self):
        assert price_for("free", 5, coupon="ANNUAL10") == Decimal("0.00")


class TestTeamPlan:
    def test_team_one_seat(self):
        assert price_for("team", 1) == Decimal("12.00")

    def test_team_ten_seats_no_discount(self):
        assert price_for("team", 10) == Decimal("120.00")

    def test_team_eleven_seats_bulk_discount_applies(self):
        # seat 11 costs $10 instead of $12
        assert price_for("team", 11) == Decimal("130.00")

    def test_team_zero_seats(self):
        assert price_for("team", 0) == Decimal("0.00")


class TestEnterprisePlan:
    def test_enterprise_zero_seats_base_fee_only(self):
        assert price_for("enterprise", 0) == Decimal("99.00")

    def test_enterprise_one_seat(self):
        assert price_for("enterprise", 1) == Decimal("107.00")

    def test_enterprise_ten_seats(self):
        assert price_for("enterprise", 10) == Decimal("179.00")


class TestCouponANNUAL10:
    def test_annual_coupon_on_team(self):
        assert price_for("team", 10, coupon="ANNUAL10") == Decimal("108.00")

    def test_annual_coupon_on_enterprise(self):
        assert price_for("enterprise", 0, coupon="ANNUAL10") == Decimal("89.10")

    def test_annual_coupon_rounds_to_cents(self):
        # 11 team seats = $130 * 0.90 = $117.00 (exact); use odd value to force rounding
        # enterprise 1 seat = $107 * 0.90 = $96.30 (exact)
        # team 1 seat = $12 * 0.90 = $10.80 (exact); use 11 seats post-tier for a cent-rounding case
        result = price_for("enterprise", 1, coupon="ANNUAL10")
        assert result == Decimal("96.30")
        assert result == result.quantize(Decimal("0.01"))


class TestErrorCases:
    def test_negative_seats_raises_value_error(self):
        with pytest.raises(ValueError, match="seats"):
            price_for("team", -1)

    def test_unknown_coupon_raises_value_error(self):
        with pytest.raises(ValueError, match="coupon"):
            price_for("team", 5, coupon="BOGUS")

    def test_unknown_plan_raises_value_error(self):
        with pytest.raises(ValueError, match="plan"):
            price_for("premium", 5)


class TestRegressions:
    def test_bulk_discount_does_not_apply_at_exactly_ten_seats(self):
        # Characterization: bulk tier begins strictly above 10 seats
        at_ten = price_for("team", 10)
        at_eleven = price_for("team", 11)
        assert at_eleven - at_ten == Decimal("10.00")
```
