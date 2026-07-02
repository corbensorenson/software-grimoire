def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    result = {
        "email": None,
        "display_name": None,
        "extra": {},
    }

    if "email" in raw:
        email = raw.get("email")
        if email is not None:
            result["email"] = str(email).strip().lower()

    if "display_name" in raw:
        display_name = raw.get("display_name")
        if display_name is not None:
            result["display_name"] = str(display_name).strip()

    for key, value in raw.items():
        if key in ("email", "display_name"):
            continue
        if value:
            result["extra"][key] = value

    return result
