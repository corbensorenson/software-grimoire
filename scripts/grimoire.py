#!/usr/bin/env python3
"""Small CLI wrapper for common Software Grimoire maintenance tasks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> int:
    return subprocess.call(args, cwd=ROOT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="grimoire", description="Software Grimoire maintenance CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate", help="regenerate Quarto pages and structured data")
    sub.add_parser("validate", help="validate structured data")
    sub.add_parser("seals", help="regenerate seal summary data")
    sub.add_parser("render", help="render the Quarto site")
    sub.add_parser("all", help="generate, validate, and render")
    args = parser.parse_args(argv)

    if args.command == "generate":
        return run([sys.executable, "scripts/bootstrap_project.py"])
    if args.command == "validate":
        return run([sys.executable, "scripts/validate_data.py"])
    if args.command == "seals":
        return run([sys.executable, "scripts/generate_seals.py"])
    if args.command == "render":
        return run(["quarto", "render"])
    if args.command == "all":
        for command in [
            [sys.executable, "scripts/bootstrap_project.py"],
            [sys.executable, "scripts/validate_data.py"],
            ["quarto", "render"],
        ]:
            code = run(command)
            if code:
                return code
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

