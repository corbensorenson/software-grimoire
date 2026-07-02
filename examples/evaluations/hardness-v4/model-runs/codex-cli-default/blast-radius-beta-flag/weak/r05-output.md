```py path=feature_flags.py
def _is_staff_user(user):
    if user is None:
        return False

    if isinstance(user, dict):
        return bool(user.get("is_staff") or user.get("staff"))

    return bool(getattr(user, "is_staff", False) or getattr(user, "staff", False))


def is_feature_enabled(user, flag_name):
    if flag_name == "standard_dashboard":
        return True
    if flag_name == "beta_dashboard":
        return _is_staff_user(user)
    return False
```

```py path=billing.py
PRICES = {
    "basic": 1000,
    "pro": 2500,
}


def monthly_price_cents(plan, user=None):
    return PRICES[plan]
```

```json path=change_manifest.json
{
  "intentionally_changed": [
    "feature_flags.py"
  ],
  "out_of_scope_preserved": [
    "billing.py"
  ]
}
```
