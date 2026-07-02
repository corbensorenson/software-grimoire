You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Falsy Metadata Refactor Trap

Trap: Naive cleanup drops falsy unknown metadata such as 0, False, empty string, empty list, and empty dict.

Expected weak failure: Weak artifact fails invariant tests for preserving unknown falsy values.

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
from normalize_user import normalize_user


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
```

Return only a complete replacement for normalize_user.py in one fenced python code block.
Preserve the public function name, accepted inputs, return keys, and exception class behavior required by the check file.
