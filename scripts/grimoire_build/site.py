"""Quarto site generation contracts."""

QUARTO_RESOURCE_PATTERNS = [
    ".nojekyll",
    "data/*.json",
    "prompts/**",
    "exports/**",
    "assets/diagrams/generated/**",
    "examples/evaluations/manual-import-template.json",
    "examples/evaluations/results.json",
    "examples/evaluations/fixtures/**",
    "examples/evaluations/runs/**",
    "examples/adoption/**",
    "examples/jailbreak-resilience/fixtures/**",
    "examples/jailbreak-resilience/results.json",
    "examples/jailbreak-resilience/harness-results.json",
    "examples/jailbreak-resilience/runs/**",
    "examples/release-gate/**",
]


def quarto_resources_block(indent: str = "    - ") -> str:
    return "\n".join(f"{indent}{item}" for item in QUARTO_RESOURCE_PATTERNS)
