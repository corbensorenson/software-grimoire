**Invariants**

- Public function names, parameter order, return types, and exception classes do not change.
- Unknown metadata keys are preserved verbatim.
- Unknown falsy metadata values are preserved: `0`, `False`, `""`, `[]`, `{}`.
- Refactor must distinguish “missing” from “present but falsy”; no `if value` filtering.
- Existing mutation behavior must remain unchanged.

**Missing**

The actual module and test file are not supplied, so I cannot produce a literal safe patch without inventing facts. I need the module path/source and current tests.

**Minimal Patch Plan**

1. Add characterization tests for metadata edge cases before refactoring.
2. Extract duplicated metadata handling into one private helper.
3. Replace duplicated call sites with the helper without changing public APIs.
4. Run old tests plus new edge-case tests against before/after behavior.

**Proposed Refactor**

Use an explicit sentinel and copy unknown metadata without truthiness checks:

```python
_MISSING = object()

def _copy_unknown_metadata(metadata):
    if metadata is None:
        return {}

    copied = {}
    for key, value in metadata.items():
        copied[key] = value
    return copied


def _put_if_present(target, key, value=_MISSING):
    if value is not _MISSING:
        target[key] = value
```

The important part is avoiding patterns like:

```python
if value:
    metadata[key] = value
```

or:

```python
{key: value for key, value in metadata.items() if value}
```

Both change behavior by dropping valid falsy values.

**Tests Proving Unchanged Behavior**

Before refactor, add tests that lock current behavior:

```python
def test_unknown_falsy_metadata_values_are_preserved():
    metadata = {
        "zero": 0,
        "false": False,
        "empty_string": "",
        "empty_list": [],
        "empty_dict": {},
    }

    result = public_function(..., metadata=metadata)

    assert result["metadata"]["zero"] == 0
    assert result["metadata"]["false"] is False
    assert result["metadata"]["empty_string"] == ""
    assert result["metadata"]["empty_list"] == []
    assert result["metadata"]["empty_dict"] == {}
```

Also cover absence separately:

```python
def test_missing_metadata_still_uses_existing_default_behavior():
    result = public_function(..., metadata=None)

    assert result["metadata"] == {}
```

After refactor, run the same tests unchanged. That proves the refactor removed duplication without collapsing “present but falsy” into “missing.”
