I couldn’t apply the edit because the workspace is read-only. The target appears to be [normalize_user.py](/Users/corbensorenson/Documents/software%20grimoire/examples/evaluations/fixtures/safe-refactoring-trap/normalize_user.py).

The important fix is to preserve unknown metadata by key presence, not by truthiness:

```diff
     for key, value in raw.items():
         if key in ("email", "display_name"):
             continue
-        if value:
-            result["extra"][key] = value
+        result["extra"][key] = value
```

A slightly cleaner full version would be:

```python
KNOWN_FIELDS = {"email", "display_name"}


def _normalize_text(value, *, lowercase=False):
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized.lower() if lowercase else normalized


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    return {
        "email": _normalize_text(raw.get("email"), lowercase=True),
        "display_name": _normalize_text(raw.get("display_name")),
        "extra": {
            key: value
            for key, value in raw.items()
            if key not in KNOWN_FIELDS
        },
    }
```

Validation: the current module returns `extra: {}` for falsy unknowns. A direct assertion against the proposed implementation passes for `0`, `False`, `""`, `[]`, and `{}`. `pytest` itself could not run because the read-only sandbox has no usable temporary directory for capture.
