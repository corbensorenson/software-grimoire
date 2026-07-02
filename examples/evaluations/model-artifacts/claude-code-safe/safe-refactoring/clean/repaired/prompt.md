You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
clean longitudinal fixture

TASK CONTEXT:
The fixture is a Python module at `examples/evaluations/fixtures/safe-refactoring/normalize_user.py`.

Ground truth:

- Public function `normalize_user(raw)` must keep its name, one-argument signature, return type, and return keys.
- Email values are stripped and lowercased.
- `display_name` is stripped when present.
- Unknown fields must be preserved in `extra`.
- Falsy-but-valid values such as `0`, `False`, and empty strings in unknown fields must not be dropped.
- Invalid input still raises `TypeError`.

Use `python -m pytest examples/evaluations/fixtures/safe-refactoring/check_normalize_user.py` as the executable fixture check.

USER REQUEST:
ROLE: Act as a senior Python engineer performing behavior-preserving refactoring.

OBJECTIVE: Remove duplication in the supplied module without changing public behavior.

CONTEXT: The module is imported by two API handlers and one CLI entry point. Existing tests cover only the happy path.

CONSTRAINTS: Do not change public function names, parameter order, return types, or raised exception classes. Touch only this module and its tests.

OUTPUT CONTRACT: Return a minimal patch plan, the proposed refactor, and tests that prove unchanged behavior.

VERIFICATION: State the invariants first; then show before/after test cases for edge inputs.

FAILURE BEHAVIOR: If the module boundary is too small for a safe refactor, say exactly what adjacent file must also move and why.

You have all source needed below. Do not ask to read files.

CURRENT normalize_user.py:
```python
def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    result = {
        "email": None,
        "display_name": None,
        "extra": {},
    }

    if "email" in raw:
        email = raw.get("email")
        if email is not None:
            result["email"] = str(email).strip().lower()

    if "display_name" in raw:
        display_name = raw.get("display_name")
        if display_name is not None:
            result["display_name"] = str(display_name).strip()

    for key, value in raw.items():
        if key in ("email", "display_name"):
            continue
        if value:
            result["extra"][key] = value

    return result
```

EXECUTABLE CHECK check_normalize_user.py:
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


def test_rejects_non_dict_input():
    with pytest.raises(TypeError):
        normalize_user(None)
```

Return only a complete replacement for normalize_user.py in one fenced python code block.
Preserve the public function name, accepted inputs, return keys, and exception class behavior required by the check file.
