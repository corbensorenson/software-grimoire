## Missing Information

The task does not supply the actual module source code. Without it I cannot produce a patch plan or a safe refactor. What is needed:

- The module file path and its current contents
- The public API surface (function signatures, return types)

---

## What I Can State Now: The Core Trap

Even without the module, the trap is well-defined. Here is the invariant and the test structure you must anchor the refactor to.

### Invariant

> Unknown metadata fields whose values are falsy (`0`, `False`, `""`, `[]`, `{}`) must survive round-trip through any cleanup, merge, or normalization path unchanged.

Naive refactors fail here because `if value:` silently drops falsy values.

### Correct guard (before writing any cleanup helper)

```python
# Wrong — drops 0, False, "", [], {}
cleaned = {k: v for k, v in metadata.items() if v}

# Correct — only drops explicit None
cleaned = {k: v for k, v in metadata.items() if v is not None}
```

### Test cases to prove unchanged behavior

```python
import pytest

FALSY_CASES = [
    ("zero",        {"count": 0}),
    ("false_flag",  {"enabled": False}),
    ("empty_str",   {"label": ""}),
    ("empty_list",  {"tags": []}),
    ("empty_dict",  {"extra": {}}),
]

@pytest.mark.parametrize("name,meta", FALSY_CASES)
def test_falsy_metadata_preserved(name, meta):
    result = your_public_function(meta)          # replace with actual call
    for key, expected in meta.items():
        assert key in result, f"{name}: key '{key}' was dropped"
        assert result[key] == expected, f"{name}: value changed"

def test_none_is_still_excluded():
    result = your_public_function({"ghost": None})
    assert "ghost" not in result
```

---

## Next Step

Paste the module contents and I will produce:
1. Minimal patch plan (which duplication to collapse and how)
2. The refactored module
3. Full test file covering happy path + the falsy-metadata invariants above
