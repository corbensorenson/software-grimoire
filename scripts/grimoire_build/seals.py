"""Public seal projection helpers."""


def public_seal_records(spells: list[dict], stacks: list[dict]) -> dict:
    return {
        "spells": [
            {
                "id": spell["id"],
                "working_seal": spell["working_seal"],
                "formal_sigil": spell["formal_sigil"],
            }
            for spell in spells
        ],
        "stacks": [
            {
                "id": stack["id"],
                "working_seal": stack["working_seal"],
                "formal_sigil": stack["formal_sigil"],
            }
            for stack in stacks
        ],
    }
