#!/usr/bin/env python3
"""Install generated Software Grimoire prompt/rule assets locally."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_PREFIXES = {
    "prompts": ["prompts/"],
    "markdown": ["exports/markdown/spells/", "exports/markdown/stacks/"],
    "codex": ["exports/codex/"],
    "cursor": ["exports/cursor/rules/"],
    "stacks": ["exports/markdown/stacks/", "prompts/stacks/"],
    "all": ["prompts/", "exports/markdown/", "exports/codex/", "exports/cursor/rules/"],
}


def load_manifest() -> dict:
    path = ROOT / "exports" / "library-manifest.json"
    if not path.exists():
        raise SystemExit("Missing exports/library-manifest.json; run `python3 scripts/bootstrap_project.py` first.")
    return json.loads(path.read_text(encoding="utf-8"))


def selected_assets(manifest: dict, target: str) -> list[dict]:
    prefixes = TARGET_PREFIXES[target]
    assets = [
        item for item in manifest.get("assets", [])
        if any(item["path"].startswith(prefix) for prefix in prefixes)
    ]
    return sorted(assets, key=lambda item: item["path"])


def install_assets(target: str, dest: Path, write: bool, force: bool) -> int:
    manifest = load_manifest()
    assets = selected_assets(manifest, target)
    if not assets:
        print(f"No assets matched target {target!r}", file=sys.stderr)
        return 1
    for item in assets:
        source = ROOT / item["path"]
        relative = Path(item["path"])
        destination = dest / relative
        if not source.exists():
            print(f"Missing source asset: {item['path']}", file=sys.stderr)
            return 1
        if destination.exists() and not force and write:
            print(f"Refusing to overwrite without --force: {destination}", file=sys.stderr)
            return 1
        action = "install" if write else "dry-run"
        print(f"{action}: {item['path']} -> {destination}")
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                backup = destination.with_suffix(destination.suffix + ".bak")
                shutil.copy2(destination, backup)
            shutil.copy2(source, destination)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install generated Software Grimoire assets")
    parser.add_argument("--target", choices=sorted(TARGET_PREFIXES), default="all")
    parser.add_argument("--dest", required=True, help="destination directory")
    parser.add_argument("--write", action="store_true", help="actually copy files; default is dry-run")
    parser.add_argument("--force", action="store_true", help="overwrite existing files, keeping a .bak copy")
    args = parser.parse_args(argv)
    return install_assets(args.target, Path(args.dest).expanduser(), args.write, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
