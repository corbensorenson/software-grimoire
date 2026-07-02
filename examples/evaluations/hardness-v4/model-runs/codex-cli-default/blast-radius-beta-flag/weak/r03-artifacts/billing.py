PRICES = {
    "basic": 1000,
    "pro": 2500,
}


def monthly_price_cents(plan, user=None):
    return PRICES[plan]
