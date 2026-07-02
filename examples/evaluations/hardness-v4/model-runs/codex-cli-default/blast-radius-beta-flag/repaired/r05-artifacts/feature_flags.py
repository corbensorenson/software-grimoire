def is_feature_enabled(user, flag_name):
    if flag_name == "standard_dashboard":
        return True
    if flag_name == "beta_dashboard":
        return bool(getattr(user, "is_staff", False))
    return False
