```py path=feature_flags.py
def is_feature_enabled(user, flag_name):
    if flag_name == "standard_dashboard":
        return True
    if flag_name == "beta_dashboard":
        if user is None:
            return False
        if isinstance(user, dict):
            return bool(user.get("is_staff", False))
        return bool(getattr(user, "is_staff", False))
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
  "files_intentionally_changed": [
    "feature_flags.py"
  ],
  "files_preserved_out_of_scope": [
    "billing.py"
  ]
}
```
