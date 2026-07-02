I couldn’t modify the file because this session’s filesystem is read-only, and pytest also couldn’t start because there is no writable temp directory available.

Apply this patch to [normalize_user.py](/Users/corbensorenson/Documents/software%20grimoire/examples/evaluations/fixtures/safe-refactoring/normalize_user.py):

```diff
 def normalize_user(raw):
     if not isinstance(raw, dict):
         raise TypeError("raw must be a dict")

-    result = {
+    normalized = {
         "email": None,
         "display_name": None,
-        "extra": {},
+        "extra": {
+            key: value
+            for key, value in raw.items()
+            if key not in {"email", "display_name"}
+        },
     }

-    if "email" in raw:
-        email = raw.get("email")
-        if email is not None:
-            result["email"] = str(email).strip().lower()
+    email = raw.get("email")
+    if email is not None:
+        normalized["email"] = str(email).strip().lower()

-    if "display_name" in raw:
-        display_name = raw.get("display_name")
-        if display_name is not None:
-            result["display_name"] = str(display_name).strip()
+    display_name = raw.get("display_name")
+    if display_name is not None:
+        normalized["display_name"] = str(display_name).strip()

-    for key, value in raw.items():
-        if key in ("email", "display_name"):
-            continue
-        if value:
-            result["extra"][key] = value
-
-    return result
+    return normalized
```

This keeps the public API and return keys intact, strips/lowercases email, strips `display_name`, preserves all unknown fields including `0`, `False`, and `""`, and still raises `TypeError` for non-dict input.
