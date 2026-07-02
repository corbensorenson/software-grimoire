from normalize_user import normalize_user


def test_preserves_all_unknown_values_even_when_falsy_or_empty():
    assert normalize_user({
        "email": " USER@Example.COM ",
        "quota": 0,
        "enabled": False,
        "note": "",
        "tags": [],
        "prefs": {},
    }) == {
        "email": "user@example.com",
        "display_name": None,
        "extra": {
            "quota": 0,
            "enabled": False,
            "note": "",
            "tags": [],
            "prefs": {},
        },
    }
