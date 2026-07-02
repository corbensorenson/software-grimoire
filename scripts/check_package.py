#!/usr/bin/env python3
"""Build and install the public package in a temporary virtual environment."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_DIR = ROOT / "tmp"


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", default="examples/adoption/package-check.json")
    args = parser.parse_args()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
        "passed": False,
    }
    build_module = run([sys.executable, "-c", "import build; print(build.__version__)"])
    if build_module.returncode != 0:
        report["steps"].append(
            {
                "name": "build dependency",
                "passed": False,
                "stdout": build_module.stdout.strip(),
                "stderr": build_module.stderr.strip(),
                "remediation": "Install with `python -m pip install build` before running this check locally.",
            }
        )
        out = ROOT / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"ERROR: missing Python build module; wrote {out.relative_to(ROOT)}", file=sys.stderr)
        return 1

    shutil.rmtree(ROOT / "dist", ignore_errors=True)
    build = run([sys.executable, "-m", "build"])
    report["steps"].append({"name": "build wheel and sdist", "passed": build.returncode == 0, "stdout": build.stdout[-4000:], "stderr": build.stderr[-4000:]})
    if build.returncode != 0:
        out = ROOT / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return build.returncode

    wheels = sorted((ROOT / "dist").glob("*.whl"))
    if not wheels:
        report["steps"].append({"name": "wheel exists", "passed": False, "stdout": "", "stderr": "no wheel in dist"})
        out = ROOT / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 1

    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="grimoire-package-check-", dir=SCRATCH_DIR) as raw_tmp:
        venv = Path(raw_tmp) / "venv"
        created = run([sys.executable, "-m", "venv", str(venv)])
        report["steps"].append({"name": "create venv", "passed": created.returncode == 0, "stdout": created.stdout, "stderr": created.stderr})
        if created.returncode != 0:
            code = created.returncode
        else:
            python = venv / "bin" / "python"
            installed = run([str(python), "-m", "pip", "install", str(wheels[-1])])
            report["steps"].append({"name": "install wheel", "passed": installed.returncode == 0, "stdout": installed.stdout[-4000:], "stderr": installed.stderr[-4000:]})
            code = installed.returncode
            for command in [
                [str(python), "-m", "pip", "show", "software-grimoire"],
                [str(venv / "bin" / "grimoire"), "--help"],
                [str(venv / "bin" / "grimoire-create-adoption-report"), "--help"],
                [str(venv / "bin" / "grimoire-check-adoption-intake"), "--help"],
                [str(venv / "bin" / "grimoire-install-assets"), "--help"],
                [str(venv / "bin" / "grimoire-run-bench"), "--help"],
                [str(venv / "bin" / "grimoire-run-hardness-bench"), "--help"],
                [str(venv / "bin" / "grimoire-import-hardness-run"), "--help"],
                [str(venv / "bin" / "grimoire-check-package-index"), "--help"],
                [str(venv / "bin" / "grimoire-check-canon-decision"), "--help"],
            ]:
                if code:
                    break
                checked = run(command)
                report["steps"].append({"name": " ".join(Path(part).name if idx == 0 else part for idx, part in enumerate(command)), "passed": checked.returncode == 0, "stdout": checked.stdout[-4000:], "stderr": checked.stderr[-4000:]})
                code = checked.returncode

    report["passed"] = all(step["passed"] for step in report["steps"])
    out = ROOT / args.write_report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0 if report["passed"] else code or 1


if __name__ == "__main__":
    raise SystemExit(main())
