I can’t complete the cleanup from the provided context alone: the actual Python module or file path is missing.

The key invariant for any refactor is clear: unknown metadata values must be preserved even when falsy, including `0`, `False`, `""`, `[]`, and `{}`. A cleanup must avoid truthiness filters like:

```python
if value:
    metadata[key] = value
```

Use explicit absence checks only when intended, for example:

```python
if value is not None:
    metadata[key] = value
```

or preserve all unknown metadata values unchanged.
