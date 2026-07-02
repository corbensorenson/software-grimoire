**Invariants**

`normalize_user(raw)` stays one-argument and returns `{"email", "display_name", "extra"}`. Non-dict input still raises `TypeError`. Email/display fields keep the same stripping/coercion rules. Unknown fields are copied unchanged into `extra`, including `0`, `False`, and `""`.

**Patch Plan**

1. Add one private helper for normalized text fields.
2. Replace duplicated email/display logic with the helper.
3. Change `extra` construction to filter only known public fields, not falsy values.
4. Keep/add edge tests in `check_normalize_user.py`.

**Proposed Refactor**

```diff
+PUBLIC_FIELDS = ("email", "display_name")
+
+
+def _normalize_text_field(raw, key, *, lowercase=False):
+    if key not in raw:
+        return None
+
+    value = raw.get(key)
+    if value is None:
+        return None
+
+    normalized = str(value).strip()
+    return normalized.lower() if lowercase else normalized
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
+        "email": _normalize_text_field(raw, "email", lowercase=True),
+        "display_name": _normalize_text_field(raw, "display_name"),
+        "extra": {
+            key: value
+            for key, value in raw.items()
+            if key not in PUBLIC_FIELDS
+        },
+    }
```

**Tests**

```python
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

**Before/After Edge Cases**

- `{"quota": 0, "enabled": False, "note": ""}`: before returns `extra == {}`; after returns all three values.
- `None`: before/after raises `TypeError`.
- `{"email": " USER@Example.COM ", "display_name": "  Ada  "}`: before/after returns normalized public fields.

I could not run the full pytest check here because pytest cannot create a temporary file in this read-only sandbox. A direct import confirmed the current module returns `{}` for the falsy-extra edge case.
