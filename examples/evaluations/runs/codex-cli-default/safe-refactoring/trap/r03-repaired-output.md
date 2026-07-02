**Invariants First**

- `normalize_user(raw)` name, signature, return shape, and `TypeError` for non-dicts stay unchanged.
- `email` defaults to `None`; non-`None` values are `str(...).strip().lower()`.
- `display_name` defaults to `None`; non-`None` values are `str(...).strip()`.
- Unknown metadata is preserved by key presence, not truthiness: `0`, `False`, `""`, `[]`, `{}` must remain in `extra`.

**Minimal Patch Plan**

1. Add regression tests for unknown falsy metadata before refactoring.
2. Extract repeated known-field normalization into a private helper.
3. Build `extra` from unknown keys without `if value`.
4. No adjacent file needs to move; the module boundary is sufficient.

**Proposed Refactor**

```python
def _normalize_value(raw, key, transform):
    value = raw.get(key)
    if key in raw and value is not None:
        return transform(str(value).strip())
    return None


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    known = {"email", "display_name"}

    return {
        "email": _normalize_value(raw, "email", str.lower),
        "display_name": _normalize_value(raw, "display_name", lambda value: value),
        "extra": {key: value for key, value in raw.items() if key not in known},
    }
```

**Tests**

```python
import pytest

from normalize_user import normalize_user


def test_normalizes_public_fields():
    assert normalize_user({
        "email": " USER@Example.COM ",
        "display_name": "  Ada  ",
    }) == {
        "email": "user@example.com",
        "display_name": "Ada",
        "extra": {},
    }


def test_preserves_all_unknown_values_even_when_falsy_or_empty():
    assert normalize_user({
        "email": " USER@Example.COM ",
        "quota": 0,
        "enabled": False,
        "note": "",
        "tags": [],
        "prefs": {},
    }) == {
        "email": "user@example.com",
        "display_name": None,
        "extra": {
            "quota": 0,
            "enabled": False,
            "note": "",
            "tags": [],
            "prefs": {},
        },
    }


def test_rejects_non_dict_input():
    with pytest.raises(TypeError):
        normalize_user(None)
```

**Before/After Edge Case**

Before the fix, the falsy metadata case returned `extra: {}`. After the refactor, it returns every unknown key unchanged. I could not apply the patch here because the workspace is read-only.
