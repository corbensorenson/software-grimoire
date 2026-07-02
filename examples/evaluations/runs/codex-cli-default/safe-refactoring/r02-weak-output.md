I couldn’t apply the cleanup because this session’s filesystem is read-only: `apply_patch` was rejected. The requested pytest command also could not start because pytest could not create a temporary file in any temp directory.

The needed change is to remove the truthiness filter that drops falsy unknown fields. This is the patch I would apply to `examples/evaluations/fixtures/safe-refactoring/normalize_user.py`:

```python
_PUBLIC_FIELDS = {"email", "display_name"}


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    email = raw.get("email")
    display_name = raw.get("display_name")

    return {
        "email": _normalize_email(email),
        "display_name": _normalize_display_name(display_name),
        "extra": _extra_fields(raw),
    }


def _normalize_email(value):
    if value is None:
        return None

    return str(value).strip().lower()


def _normalize_display_name(value):
    if value is None:
        return None

    return str(value).strip()


def _extra_fields(raw):
    return {
        key: value
        for key, value in raw.items()
        if key not in _PUBLIC_FIELDS
    }
```

This keeps `normalize_user(raw)` unchanged publicly, preserves the return keys, keeps invalid input raising `TypeError`, and preserves `0`, `False`, and `""` in `extra`.
