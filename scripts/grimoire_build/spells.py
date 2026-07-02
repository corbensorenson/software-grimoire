"""Spell generation helper contracts."""


def spell_slug(spell: dict) -> str:
    return spell["id"].split(".")[1]
