PRICES = {
    "basic": 1000,
    "pro": 2500,
}


def monthly_price_cents(plan, user=None):
    price = PRICES[plan]
    if user and user.get("staff"):
        return price - 500
    return price
