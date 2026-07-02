I couldn’t modify the file because this session is read-only. The patch was rejected by the sandbox. The cleanup needed is small: remove the truthiness filter and make normalization explicit.

```diff
*** Begin Patch
*** Update File: examples/evaluations/fixtures/safe-refactoring/normalize_user.py
@@
+_KNOWN_FIELDS = frozenset(("email", "display_name"))
+
+
+def _normalize_email(value):
+    if value is None:
+        return None
+    return str(value).strip().lower()
+
+
+def _normalize_display_name(value):
+    if value is None:
+        return None
+    return str(value).strip()
+
+
 def normalize_user(raw):
     if not isinstance(raw, dict):
         raise TypeError("raw must be a dict")

-    result = {
-        "email": None,
-        "display_name": None,
-        "extra": {},
+    return {
+        "email": _normalize_email(raw.get("email")),
+        "display_name": _normalize_display_name(raw.get("display_name")),
+        "extra": {
+            key: value
+            for key, value in raw.items()
+            if key not in _KNOWN_FIELDS
+        },
     }
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
*** End Patch
```

Verification note: `python -m pytest examples/evaluations/fixtures/safe-refactoring/check_normalize_user.py` could not start because the sandbox has no writable temp directory. A direct Python check against the current file returned `{}` for falsy unknown fields, confirming the existing failure.
