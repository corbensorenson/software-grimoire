I couldn’t write the file because this session is read-only, but the cleanup is straightforward: remove the truthiness filter so unknown metadata is preserved exactly.

Patch for [normalize_user.py](/Users/corbensorenson/Documents/software%20grimoire/examples/evaluations/fixtures/safe-refactoring-trap/normalize_user.py):

```python
def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    known_fields = {"email", "display_name"}

    email = raw.get("email")
    display_name = raw.get("display_name")

    return {
        "email": str(email).strip().lower() if email is not None else None,
        "display_name": str(display_name).strip() if display_name is not None else None,
        "extra": {
            key: value
            for key, value in raw.items()
            if key not in known_fields
        },
    }
```

The key fix is preserving `0`, `False`, `""`, `[]`, and `{}` in `extra`; the current `if value:` drops them. I verified the current fixture fails by returning `extra: {}` for those falsy metadata values.
