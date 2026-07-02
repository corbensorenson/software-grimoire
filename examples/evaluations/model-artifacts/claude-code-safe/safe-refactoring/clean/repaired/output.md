```python
def _normalize_str(value):
    if value is None:
        return None
    return str(value).strip()


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    result = {
        "email": None,
        "display_name": None,
        "extra": {},
    }

    if "email" in raw:
        normalized = _normalize_str(raw["email"])
        if normalized is not None:
            result["email"] = normalized.lower()

    if "display_name" in raw:
        result["display_name"] = _normalize_str(raw["display_name"])

    for key, value in raw.items():
        if key not in ("email", "display_name"):
            result["extra"][key] = value

    return result
```

**What changed and why:**

- Extracted `_normalize_str` to eliminate the duplicated `None`-guard + `str().strip()` pattern shared by `email` and `display_name`.
- Fixed the latent bug: `if value:` in the original `extra` loop silently dropped `0`, `False`, and `""`. Replaced with unconditional assignment — all unknown fields are now preserved regardless of truthiness, matching the stated ground truth.
- No public names, signatures, return keys, or exception classes were touched.
