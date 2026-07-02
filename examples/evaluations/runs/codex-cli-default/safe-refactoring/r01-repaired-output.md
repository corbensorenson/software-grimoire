**Invariants**

`normalize_user(raw)` keeps its public name, one-argument signature, dict return type, keys `email`, `display_name`, `extra`, and still raises `TypeError` for non-dicts. Email is stripped/lowercased, display name is stripped, and unknown fields are copied into `extra` without truthiness filtering.

I could not apply the patch because the workspace is read-only, but this is the minimal diff:

```diff
+def _normalize_text_field(raw, key, transform=None):
+    if key not in raw:
+        return None
+    value = raw.get(key)
+    if value is None:
+        return None
+    value = str(value).strip()
+    return transform(value) if transform is not None else value
+
+
 def normalize_user(raw):
     if not isinstance(raw, dict):
         raise TypeError("raw must be a dict")

-    result = {
-        "email": None,
-        "display_name": None,
-        "extra": {},
-    }
-
-    if "email" in raw:
-        email = raw.get("email")
-        if email is not None:
-            result["email"] = str(email).strip().lower()
-
-    if "display_name" in raw:
-        display_name = raw.get("display_name")
-        if display_name is not None:
-            result["display_name"] = str(display_name).strip()
-
-    for key, value in raw.items():
-        if key in ("email", "display_name"):
-            continue
-        if value:
-            result["extra"][key] = value
-
-    return result
+    return {
+        "email": _normalize_text_field(raw, "email", str.lower),
+        "display_name": _normalize_text_field(raw, "display_name"),
+        "extra": {
+            key: value
+            for key, value in raw.items()
+            if key not in ("email", "display_name")
+        },
+    }
```

**Patch Plan**

1. Add one private helper for duplicated text-field normalization.
2. Replace the email/display-name blocks with helper calls.
3. Replace the unknown-field loop with a key-filtered dict comprehension so falsy unknown values are preserved.
4. Keep tests in `check_normalize_user.py`; add one edge test if desired:

```python
def test_public_none_values_do_not_stringify():
    assert normalize_user({"email": None, "display_name": None}) == {
        "email": None,
        "display_name": None,
        "extra": {},
    }
```

**Before/After Edge Cases**

Current fixture result: `test_preserves_unknown_falsy_values` fails because `0`, `False`, and `""` are dropped from `extra`.

Proposed refactor result, verified in-memory:

```python
normalize_user({"quota": 0, "enabled": False, "note": ""})["extra"]
# {"quota": 0, "enabled": False, "note": ""}
```

Invalid input behavior remains:

```python
with pytest.raises(TypeError):
    normalize_user(None)
```

Verification note: the exact pytest command could not run normally because this sandbox has no writable temp directory. Running pytest with capture/cache disabled collected tests and showed the current falsy-value failure.
