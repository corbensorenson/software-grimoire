"""Stack generation helper contracts."""


def stack_slug(stack: dict) -> str:
    return stack["id"].split(".")[1]
