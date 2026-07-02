#!/usr/bin/env python3
"""Small CLI wrapper for common Software Grimoire maintenance tasks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

from bootstrap_project import seal_for


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> int:
    return subprocess.call(args, cwd=ROOT)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema_for_record(record: dict) -> Path:
    ident = record.get("id", "")
    if ident.startswith("spell."):
        return ROOT / "schemas" / "spell.schema.json"
    if ident.startswith("stack."):
        return ROOT / "schemas" / "stack.schema.json"
    raise ValueError(f"Cannot infer schema from id: {ident!r}")


def validate_file(path: Path) -> int:
    data = load_json(path)
    records = data if isinstance(data, list) else [data]
    errors: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{path}:{index}: expected object")
            continue
        schema = load_json(schema_for_record(record))
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{path}:{index}.{location}: {error.message}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validation passed: {path}")
    return 0


def seal_file(path: Path) -> int:
    record = load_json(path)
    if not isinstance(record, dict):
        print("seal expects one spell or stack JSON object", file=sys.stderr)
        return 1
    ident = record.get("id", "")
    kind = ident.split(".", 1)[0]
    if kind not in {"spell", "stack"}:
        print(f"cannot infer seal kind from id: {ident!r}", file=sys.stderr)
        return 1
    sealed = seal_for(kind, record)
    print(json.dumps(sealed, indent=2, ensure_ascii=False))
    return 0


def spell_skeleton() -> dict:
    return {
        "id": "spell.local-example.v1",
        "title": "Spell of Local Example",
        "version": 1,
        "cast_level": "full",
        "status": "draft",
        "use_when": "Use when this local task recurs and needs a stable prompt contract.",
        "role": "Act as a senior software engineer.",
        "objective": "State the exact change or analysis needed.",
        "context": "Name the artifact, system boundary, inputs, and constraints that matter.",
        "constraints": "State what must not change and what tools or dependencies are allowed.",
        "procedure": "Describe the smallest useful sequence of work.",
        "output_contract": "State the exact shape of the answer or patch.",
        "verification": "State the tests, checks, queries, or review evidence required.",
        "failure_behavior": "State what to do if the task is underspecified or unsafe.",
        "runes": [1172, 1152, 1445],
        "source": "local",
        "human_title": "Spell of Local Example",
    }


def write_new_spell(path: Path | None) -> int:
    record = spell_skeleton()
    record.update(seal_for("spell", record))
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        print(text, end="")
    return 0


def export_assets(target: str) -> int:
    targets = {
        "markdown": ROOT / "exports" / "markdown",
        "codex": ROOT / "exports" / "codex",
        "cursor": ROOT / "exports" / "cursor" / "rules",
        "claude-code": ROOT / "exports" / "claude-code" / "skills",
        "all": ROOT / "exports",
    }
    base = targets[target]
    if not base.exists():
        print(f"Missing generated exports for target {target!r}; run `grimoire generate` first.", file=sys.stderr)
        return 1
    files = sorted(path for path in base.rglob("*") if path.is_file())
    if not files:
        print(f"No export files found for target {target!r}", file=sys.stderr)
        return 1
    for path in files:
        print(path.relative_to(ROOT))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="grimoire", description="Software Grimoire maintenance CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate", help="regenerate Quarto pages and structured data")
    validate_parser = sub.add_parser("validate", help="validate repository data or one spell/stack JSON file")
    validate_parser.add_argument("path", nargs="?", help="optional spell or stack JSON path")
    seal_parser = sub.add_parser("seal", help="compute a working seal for one spell or stack JSON file")
    seal_parser.add_argument("path", help="spell or stack JSON path")
    new_parser = sub.add_parser("new", help="create a local scaffold")
    new_sub = new_parser.add_subparsers(dest="kind", required=True)
    new_spell = new_sub.add_parser("spell", help="create a spell JSON skeleton")
    new_spell.add_argument("path", nargs="?", help="optional output path")
    export_parser = sub.add_parser("export", help="list generated installable exports")
    export_parser.add_argument("--target", choices=["all", "markdown", "codex", "cursor", "claude-code"], default="all")
    bench_parser = sub.add_parser("bench", help="bench utilities")
    bench_sub = bench_parser.add_subparsers(dest="bench_command", required=True)
    bench_import = bench_sub.add_parser("import", help="validate a manual benchmark import record")
    bench_import.add_argument("path", help="manual import JSON path")
    bench_execution = bench_sub.add_parser("execution", help="run execution-graded trap bench")
    bench_execution.add_argument("args", nargs=argparse.REMAINDER, help="arguments forwarded to run_execution_bench.py")
    sub.add_parser("seals", help="regenerate seal summary data")
    sub.add_parser("render", help="render the Quarto site")
    sub.add_parser("test", help="run repository tests")
    sub.add_parser("all", help="generate, validate, render, and test")
    args = parser.parse_args(argv)

    if args.command == "generate":
        return run([sys.executable, "scripts/bootstrap_project.py"])
    if args.command == "validate":
        if args.path:
            return validate_file(Path(args.path))
        return run([sys.executable, "scripts/validate_data.py"])
    if args.command == "seal":
        return seal_file(Path(args.path))
    if args.command == "new":
        if args.kind == "spell":
            return write_new_spell(Path(args.path) if args.path else None)
        return 2
    if args.command == "export":
        return export_assets(args.target)
    if args.command == "bench":
        if args.bench_command == "import":
            return run([sys.executable, "scripts/run_bench.py", "import", args.path])
        if args.bench_command == "execution":
            return run([sys.executable, "scripts/run_bench.py", "execution", *args.args])
        return 2
    if args.command == "seals":
        return run([sys.executable, "scripts/generate_seals.py"])
    if args.command == "render":
        return run(["quarto", "render"])
    if args.command == "test":
        return run([sys.executable, "-m", "pytest"])
    if args.command == "all":
        for command in [
            [sys.executable, "scripts/bootstrap_project.py"],
            [sys.executable, "scripts/validate_data.py"],
            [sys.executable, "scripts/run_execution_bench.py"],
            ["quarto", "render"],
            [sys.executable, "-m", "pytest"],
        ]:
            code = run(command)
            if code:
                return code
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
