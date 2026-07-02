#!/usr/bin/env python3
"""Regenerate seal summary data."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    spells = json.loads((ROOT / "data" / "spells.json").read_text(encoding="utf-8"))
    stacks = json.loads((ROOT / "data" / "stacks.json").read_text(encoding="utf-8"))
    seals = {
        "spells": [{"id": item["id"], "working_seal": item["working_seal"], "formal_sigil": item["formal_sigil"]} for item in spells],
        "stacks": [{"id": item["id"], "working_seal": item["working_seal"], "formal_sigil": item["formal_sigil"]} for item in stacks],
    }
    (ROOT / "data" / "seals.json").write_text(json.dumps(seals, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(seals['spells'])} spell seals and {len(seals['stacks'])} stack seals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

