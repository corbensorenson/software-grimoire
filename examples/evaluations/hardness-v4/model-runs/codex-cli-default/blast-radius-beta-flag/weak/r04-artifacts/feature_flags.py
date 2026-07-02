def is_feature_enabled(user, flag_name):
    if flag_name == "standard_dashboard":
        return True
    if flag_name == "beta_dashboard":
        if user is None:
            return False
        if isinstance(user, dict):
            return bool(user.get("is_staff", False))
        return bool(getattr(user, "is_staff", False))
    return False
