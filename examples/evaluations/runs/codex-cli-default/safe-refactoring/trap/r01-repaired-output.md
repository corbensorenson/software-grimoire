**Invariants First**

- Keep public API: `normalize_user(raw)` name, parameter order, return shape, and `TypeError`.
- Known fields stay out of `extra`.
- `email` is stripped/lowercased when not `None`; `display_name` is stripped when not `None`.
- Unknown metadata is preserved by key presence, including `0`, `False`, `""`, `[]`, and `{}`.
- Unknown mutable values are not copied.

**Patch Plan**

1. Add private constants/helpers inside `normalize_user.py`.
2. Replace duplicated known-field normalization with one helper.
3. Build `extra` from all unknown keys without truthiness filtering.
4. Add edge tests around falsy unknown metadata and known-field normalization.

No adjacent file needs to move; the module boundary is sufficient.

**Proposed Refactor**

```python
_KNOWN_FIELDS = {"email", "display_name"}


def _normalize_known(value, *, lower=False):
    if value is None:
        return None

    normalized = str(value).strip()
    if lower:
        return normalized.lower()
    return normalized


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    return {
        "email": _normalize_known(raw.get("email"), lower=True),
        "display_name": _normalize_known(raw.get("display_name")),
        "extra": {
            key: value
            for key, value in raw.items()
            if key not in _KNOWN_FIELDS
        },
    }
```

**Before/After Edge Tests**

```python
import pytest

from normalize_user import normalize_user


def test_preserves_all_unknown_values_even_when_falsy_or_empty():
    tags = []
    prefs = {}

    result = normalize_user({
        "email": " USER@Example.COM ",
        "quota": 0,
        "enabled": False,
        "note": "",
        "tags": tags,
        "prefs": prefs,
    })

    assert result == {
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
    assert result["extra"]["tags"] is tags
    assert result["extra"]["prefs"] is prefs


@pytest.mark.parametrize(
    "raw, expected",
    [
        ({}, {"email": None, "display_name": None, "extra": {}}),
        (
            {"email": None, "display_name": None},
            {"email": None, "display_name": None, "extra": {}},
        ),
        (
            {"email": 0, "display_name": False},
            {"email": "0", "display_name": "False", "extra": {}},
        ),
    ],
)
def test_known_field_behavior_is_unchanged(raw, expected):
    assert normalize_user(raw) == expected


def test_non_dict_still_raises_type_error():
    with pytest.raises(TypeError, match="raw must be a dict"):
        normalize_user([])
```

I could not run `pytest` in this read-only sandbox because Python had no writable temp directory. A direct check confirmed the current planted failure returns `extra: {}` for falsy unknown metadata; the refactor above preserves those values.
