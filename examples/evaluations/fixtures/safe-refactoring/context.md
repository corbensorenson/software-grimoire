The fixture is a Python module at `examples/evaluations/fixtures/safe-refactoring/normalize_user.py`.

Ground truth:

- Public function `normalize_user(raw)` must keep its name, one-argument signature, return type, and return keys.
- Email values are stripped and lowercased.
- `display_name` is stripped when present.
- Unknown fields must be preserved in `extra`.
- Falsy-but-valid values such as `0`, `False`, and empty strings in unknown fields must not be dropped.
- Invalid input still raises `TypeError`.

Use `python -m pytest examples/evaluations/fixtures/safe-refactoring/check_normalize_user.py` as the executable fixture check.
