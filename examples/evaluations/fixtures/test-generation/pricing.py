from decimal import Decimal, ROUND_HALF_UP


def price_for(plan, seats, coupon=None):
    """Return monthly price in dollars for a plan and seat count."""
    if seats < 0:
        raise ValueError("seats must be non-negative")
    if coupon not in (None, "ANNUAL10"):
        raise ValueError("unknown coupon")
    if plan == "free":
        base = Decimal("0")
    elif plan == "team":
        base = Decimal("12") * Decimal(seats)
        if seats > 10:
            base -= Decimal(seats - 10) * Decimal("2")
    elif plan == "enterprise":
        base = Decimal("99") + Decimal("8") * Decimal(seats)
    else:
        raise ValueError("unknown plan")
    if coupon == "ANNUAL10":
        base *= Decimal("0.90")
    return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
