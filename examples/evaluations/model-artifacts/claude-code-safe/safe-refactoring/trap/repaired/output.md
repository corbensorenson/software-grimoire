```python
def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    known = {"email", "display_name"}

    email = raw.get("email")
    display_name = raw.get("display_name")

    return {
        "email": str(email).strip().lower() if email is not None and "email" in raw else None,
        "display_name": str(display_name).strip() if display_name is not None and "display_name" in raw else None,
        "extra": {k: v for k, v in raw.items() if k not in known},
    }
```
