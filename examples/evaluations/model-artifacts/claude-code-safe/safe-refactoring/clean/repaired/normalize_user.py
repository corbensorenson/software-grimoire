def _normalize_str(value):
    if value is None:
        return None
    return str(value).strip()


def normalize_user(raw):
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")

    result = {
        "email": None,
        "display_name": None,
        "extra": {},
    }

    if "email" in raw:
        normalized = _normalize_str(raw["email"])
        if normalized is not None:
            result["email"] = normalized.lower()

    if "display_name" in raw:
        result["display_name"] = _normalize_str(raw["display_name"])

    for key, value in raw.items():
        if key not in ("email", "display_name"):
            result["extra"][key] = value

    return result
