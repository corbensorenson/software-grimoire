import pytest

from normalize_user import normalize_user


def test_normalizes_public_fields():
    assert normalize_user({"email": " USER@Example.COM ", "display_name": "  Ada  "}) == {
        "email": "user@example.com",
        "display_name": "Ada",
        "extra": {},
    }


def test_preserves_unknown_falsy_values():
    assert normalize_user({"quota": 0, "enabled": False, "note": ""})["extra"] == {
        "quota": 0,
        "enabled": False,
        "note": "",
    }


def test_rejects_non_dict_input():
    with pytest.raises(TypeError):
        normalize_user(None)
