**Invariants**

- `normalize_user(raw)` name, parameter order, return type, return keys, and exception classes stay unchanged.
- Emails continue to be lowercased.
- Unknown input fields continue to be preserved.
- Existing happy-path behavior remains byte-for-byte equivalent where observable.
- API handlers and CLI imports require no call-site changes.

The supplied context is missing the actual module and current tests, so I can’t produce a safe concrete diff without inventing behavior. I would need the source file containing `normalize_user(raw)` and its test file.

**Minimal Patch Plan**

1. Add characterization tests for current edge behavior before refactoring.
2. Extract duplicated validation logic into one private helper inside the same module.
3. Keep `normalize_user(raw)` as the only public entry point.
4. Run the same characterization tests before and after the refactor to prove behavior is unchanged.

**Proposed Refactor**

Refactor shape only, pending source:

```python
def normalize_user(raw):
    validated = _validate_user_payload(raw)
    return _normalize_validated_user(validated)


def _validate_user_payload(raw):
    # Move the currently duplicated validation branches here.
    # Preserve exact exception classes and messages if tests assert them.
    return raw


def _normalize_validated_user(raw):
    # Preserve existing return keys.
    # Lowercase email exactly as current code does.
    # Preserve unknown fields exactly as current code does.
    ...
```

No adjacent file should move based on the provided context. If validation is currently split between this module and an API handler or CLI entry point, then the specific adjacent handler/CLI file containing normalization-side validation must also be characterized or moved, because otherwise this module alone is not the complete behavior boundary.

**Before/After Edge Tests**

These should be written as characterization tests first, run against the current implementation, then run unchanged after the refactor:

```python
import pytest

from module_under_test import normalize_user


def test_lowercases_email_and_preserves_unknown_fields():
    raw = {
        "email": "USER@Example.COM",
        "display_name": "User",
        "role": "admin",
    }

    assert normalize_user(raw) == {
        "email": "user@example.com",
        "display_name": "User",
        "role": "admin",
    }


@pytest.mark.parametrize(
    "raw",
    [
        None,
        {},
        {"display_name": "No Email"},
        {"email": None, "display_name": "User"},
        {"email": "", "display_name": "User"},
    ],
)
def test_edge_inputs_preserve_current_exception_behavior(raw):
    with pytest.raises(Exception) as exc:
        normalize_user(raw)

    # Replace Exception with the exact current exception class after observing it.
    assert exc.type is CURRENT_EXCEPTION_CLASS
```

I can make the actual patch once the module and existing tests are supplied.
