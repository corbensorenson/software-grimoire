```py path=feature_flags.py
def is_feature_enabled(user, flag_name):
    if flag_name == "standard_dashboard":
        return True
    if flag_name == "beta_dashboard":
        return bool(getattr(user, "is_staff", False))
    return False
```

```json path=change_manifest.json
{
  "changed": ["feature_flags.py"],
  "preserved_out_of_scope": ["billing.py"]
}
```
