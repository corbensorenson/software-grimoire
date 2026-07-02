def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    result = {
        "email": None,
        "display_name": None,
        "extra": {},
    }

    if "email" in raw and raw["email"] is not None:
        result["email"] = str(raw["email"]).strip().lower()

    if "display_name" in raw and raw["display_name"] is not None:
        result["display_name"] = str(raw["display_name"]).strip()

    for key, value in raw.items():
        if key not in ("email", "display_name"):
            result["extra"][key] = value

    return result
