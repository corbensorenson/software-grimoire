#!/usr/bin/env python3
"""Bench v2 facade for Software Grimoire evaluations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> int:
    return subprocess.call(args, cwd=ROOT)


def load_contract() -> dict:
    return json.loads((ROOT / "data" / "bench_v2.json").read_text(encoding="utf-8"))


def validate_import(path: Path) -> int:
    contract = load_contract()
    record = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for field in contract["manual_import_contract"]["required_fields"]:
        if field not in record or record[field] in ("", None):
            errors.append(f"missing required field: {field}")
    if record.get("surface_id") not in contract["surfaces"]:
        errors.append(f"unknown surface_id: {record.get('surface_id')!r}")
    if record.get("provenance") not in contract["manual_import_contract"]["provenance_values"]:
        errors.append(f"bad provenance: {record.get('provenance')!r}")
    for key in ["fixture_path", "prompt_path", "transcript_path"]:
        value = record.get(key)
        if value and not (ROOT / value).exists():
            errors.append(f"{key} does not exist: {value}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Bench import record is valid: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    eval_parser = sub.add_parser("evaluations", help="run field-spell evaluations")
    eval_parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments forwarded to run_evaluations.py")
    jail_parser = sub.add_parser("jailbreak-resilience", help="run jailbreak-resilience bench")
    jail_parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments forwarded to run_jailbreak_resilience.py")
    execution_parser = sub.add_parser("execution", help="run execution-graded clean/trap bench")
    execution_parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments forwarded to run_execution_bench.py")
    all_parser = sub.add_parser("all", help="run all project-owned benches")
    all_parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments forwarded to bench runners")
    import_parser = sub.add_parser("import", help="validate a manual reviewer-supplied run record")
    import_parser.add_argument("path", help="path to manual import JSON")
    args = parser.parse_args(argv)

    if args.command == "evaluations":
        return run([sys.executable, "scripts/run_evaluations.py", *args.args])
    if args.command == "jailbreak-resilience":
        return run([sys.executable, "scripts/run_jailbreak_resilience.py", *args.args])
    if args.command == "execution":
        return run([sys.executable, "scripts/run_execution_bench.py", *args.args])
    if args.command == "all":
        code = run([sys.executable, "scripts/run_evaluations.py", *args.args])
        if code:
            return code
        code = run([sys.executable, "scripts/run_jailbreak_resilience.py", *args.args])
        if code:
            return code
        return run([sys.executable, "scripts/run_execution_bench.py", *args.args])
    if args.command == "import":
        return validate_import(Path(args.path))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
