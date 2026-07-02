**Invariants**

- `normalize_user(raw)` name, one-argument signature, return type, return keys unchanged.
- Non-`dict` input raises `TypeError`.
- Email is `str(value).strip().lower()` when present and non-`None`.
- `display_name` is `str(value).strip()` when present and non-`None`.
- Unknown fields go under `extra`, including `0`, `False`, and `""`.

**Minimal Patch Plan**

1. Add one private helper for repeated string normalization.
2. Build `extra` with a dict comprehension that excludes only public keys.
3. Keep tests focused on public contract and edge values.

**Proposed Refactor**

```python
PUBLIC_FIELDS = {"email", "display_name"}


def _normalize_text(value, *, lowercase=False):
    if value is None:
        return None

    normalized = str(value).strip()
    if lowercase:
        return normalized.lower()
    return normalized


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    return {
        "email": _normalize_text(raw.get("email"), lowercase=True),
        "display_name": _normalize_text(raw.get("display_name")),
        "extra": {
            key: value
            for key, value in raw.items()
            if key not in PUBLIC_FIELDS
        },
    }
```

**Tests**

```python
import pytest

from normalize_user import normalize_user


def test_normalizes_public_fields():
    assert normalize_user({"email": " USER@Example.COM ", "display_name": "  Ada  "}) == {
        "email": "user@example.com",
        "display_name": "Ada",
        "extra": {},
    }


def test_preserves_unknown_falsy_values():
    assert normalize_user({"quota": 0, "enabled": False, "note": ""})["extra"] == {
        "quota": 0,
        "enabled": False,
        "note": "",
    }


def test_preserves_unknown_truthy_values():
    assert normalize_user({"role": "admin", "score": 7})["extra"] == {
        "role": "admin",
        "score": 7,
    }


def test_missing_and_none_public_fields_return_none():
    assert normalize_user({}) == {"email": None, "display_name": None, "extra": {}}
    assert normalize_user({"email": None, "display_name": None}) == {
        "email": None,
        "display_name": None,
        "extra": {},
    }


def test_rejects_non_dict_input():
    with pytest.raises(TypeError):
        normalize_user(None)
```

**Before/After Edge Cases**

- `{"quota": 0, "enabled": False, "note": ""}`: before fails, after preserves all in `extra`.
- `{}`: before and after return all expected keys with `None` public fields.
- `None`: before and after raise `TypeError`.

I ran the fixture check against the current module: `2 passed, 1 failed`; the failure is the falsy unknown-field case.
