#!/usr/bin/env python3
"""Smoke-test an installed package from a public package index."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
ROOT = SOURCE_ROOT if (SOURCE_ROOT / "pyproject.toml").exists() else Path.cwd()
SCRATCH_DIR = ROOT / "tmp"
PYPROJECT = ROOT / "pyproject.toml"
INDEXES = {
    "pypi": {
        "index_url": "https://pypi.org/simple/",
        "extra_index_url": "",
        "package_url": "https://pypi.org/project/software-grimoire/",
    },
    "testpypi": {
        "index_url": "https://test.pypi.org/simple/",
        "extra_index_url": "https://pypi.org/simple/",
        "package_url": "https://test.pypi.org/project/software-grimoire/",
    },
}


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-subprocess-", dir=SCRATCH_DIR) as raw_tmp:
        env = os.environ.copy()
        scratch = str(Path(raw_tmp).resolve())
        env.update({"TMPDIR": scratch, "TEMP": scratch, "TMP": scratch})
        return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True, env=env)


def read_project_metadata() -> tuple[str, str]:
    if PYPROJECT.exists():
        text = PYPROJECT.read_text(encoding="utf-8")
        name = re.search(r'(?m)^name = "([^"]+)"', text)
        version = re.search(r'(?m)^version = "([^"]+)"', text)
        if not name or not version:
            raise ValueError("Could not read project name/version from pyproject.toml")
        return name.group(1), version.group(1)
    try:
        return "software-grimoire", metadata.version("software-grimoire")
    except metadata.PackageNotFoundError:
        return "software-grimoire", "3.0.0"


def report_path(value: str) -> Path:
    raw = Path(value)
    full = raw if raw.is_absolute() else ROOT / raw
    resolved = full.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Report path must stay inside this repository: {value}") from exc
    return resolved


def display_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def install_command(python: Path, index: str, package: str, version: str) -> list[str]:
    config = INDEXES[index]
    command = [
        str(python),
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--index-url",
        config["index_url"],
    ]
    if config["extra_index_url"]:
        command.extend(["--extra-index-url", config["extra_index_url"]])
    command.append(f"{package}=={version}")
    return command


def step(name: str, passed: bool, completed: subprocess.CompletedProcess[str] | None = None, remediation: str = "", command: list[str] | None = None) -> dict:
    record = {
        "name": name,
        "passed": passed,
        "stdout": (completed.stdout[-4000:] if completed else ""),
        "stderr": (completed.stderr[-4000:] if completed else ""),
    }
    if remediation:
        record["remediation"] = remediation
    if command:
        record["command"] = " ".join(command)
    return record


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {display_path(path)}")


def main() -> int:
    default_package, default_version = read_project_metadata()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", choices=sorted(INDEXES), default="pypi")
    parser.add_argument("--package", default=default_package)
    parser.add_argument("--version", default=default_version)
    parser.add_argument("--uploader", default="", help="named human maintainer who performed the upload")
    parser.add_argument("--package-url", default="", help="public package URL recorded after upload")
    parser.add_argument("--dry-run", action="store_true", help="record the command contract without installing from an index")
    parser.add_argument("--write-report", default="tmp/package-index-smoke.json")
    args = parser.parse_args()

    out = report_path(args.write_report)
    config = INDEXES[args.index]
    report = {
        "schema_version": "4.0.0-package-index-smoke",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "dry_run" if args.dry_run else "failed",
        "policy": "This report proves package-index availability only when it installs the named version from TestPyPI or PyPI after a named human upload.",
        "index": args.index,
        "index_url": config["index_url"],
        "extra_index_url": config["extra_index_url"],
        "package": args.package,
        "version": args.version,
        "human_upload": {
            "required": True,
            "uploader": args.uploader,
            "uploaded_at": "",
            "package_url": args.package_url or config["package_url"],
        },
        "steps": [],
        "passed": False,
    }

    if args.dry_run:
        command = install_command(Path("python"), args.index, args.package, args.version)
        report["steps"].append(
            step(
                "construct package-index install command",
                True,
                command=command,
                remediation="Run without --dry-run only after a named human upload exists.",
            )
        )
        report["steps"].append(
            step(
                "package-index install",
                False,
                remediation="Skipped by --dry-run; this does not prove public package-index availability.",
            )
        )
        write_report(out, report)
        return 0

    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-package-index-", dir=SCRATCH_DIR) as raw_tmp:
        venv = Path(raw_tmp) / "venv"
        created = run([sys.executable, "-m", "venv", str(venv)])
        report["steps"].append(step("create venv", created.returncode == 0, created))
        code = created.returncode
        if code == 0:
            python = venv / "bin" / "python"
            installed = run(install_command(python, args.index, args.package, args.version))
            report["steps"].append(
                step(
                    "install from package index",
                    installed.returncode == 0,
                    installed,
                    remediation="Confirm the named human upload completed and the requested version exists on the selected index.",
                )
            )
            code = installed.returncode
        if code == 0:
            for command in [
                [str(venv / "bin" / "grimoire"), "--help"],
                [str(venv / "bin" / "grimoire-check-package-index"), "--help"],
                [str(venv / "bin" / "grimoire-create-adoption-report"), "--help"],
                [str(venv / "bin" / "grimoire-check-adoption-intake"), "--help"],
                [str(venv / "bin" / "grimoire-check-hardness-intake"), "--help"],
                [str(venv / "bin" / "grimoire-check-canon-decision"), "--help"],
                [str(venv / "bin" / "grimoire-check-package-publish-workflow"), "--help"],
                [str(venv / "bin" / "grimoire-install-assets"), "--help"],
                [str(venv / "bin" / "grimoire-import-hardness-run"), "--help"],
            ]:
                checked = run(command)
                report["steps"].append(step(" ".join(Path(part).name if idx == 0 else part for idx, part in enumerate(command)), checked.returncode == 0, checked))
                code = checked.returncode
                if code:
                    break

    report["passed"] = all(item["passed"] for item in report["steps"])
    report["status"] = "passed" if report["passed"] else "failed"
    write_report(out, report)
    return 0 if report["passed"] else code or 1


if __name__ == "__main__":
    raise SystemExit(main())
