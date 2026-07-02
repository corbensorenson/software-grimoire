#!/usr/bin/env python3
"""Validate public package-index smoke tooling."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_package_index.py"


def remove_scratch(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass


def test_package_index_smoke_dry_run_records_no_public_proof() -> None:
    scratch = ROOT / "tmp" / "tests" / "package-index-smoke"
    remove_scratch(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    report = scratch / "dry-run.json"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--index",
                "pypi",
                "--dry-run",
                "--write-report",
                str(report.relative_to(ROOT)),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["status"] == "dry_run"
        assert data["passed"] is False
        assert data["human_upload"]["required"] is True
        assert "software-grimoire==3.0.0" in data["steps"][0]["command"]
        assert any(step["name"] == "package-index install" and step["passed"] is False for step in data["steps"])
    finally:
        remove_scratch(scratch)


def test_package_index_report_path_must_stay_inside_repo() -> None:
    from scripts import check_package_index

    external = ROOT.parent / "package-index-smoke.json"
    with pytest.raises(ValueError, match="inside this repository"):
        check_package_index.report_path(str(external))
    assert check_package_index.report_path("tmp/package-index-smoke.json") == ROOT / "tmp" / "package-index-smoke.json"


def test_package_index_install_command_uses_selected_index() -> None:
    from scripts.check_package_index import install_command

    pypi = install_command(Path("python"), "pypi", "software-grimoire", "3.0.0")
    testpypi = install_command(Path("python"), "testpypi", "software-grimoire", "3.0.0")
    assert "https://pypi.org/simple/" in pypi
    assert "--extra-index-url" not in pypi
    assert "https://test.pypi.org/simple/" in testpypi
    assert "https://pypi.org/simple/" in testpypi


def test_package_index_release_plan_uses_manual_trusted_publishing_workflow() -> None:
    plan = json.loads((ROOT / "examples" / "adoption" / "package-index-release-plan.json").read_text(encoding="utf-8"))
    trusted = plan["trusted_publishing_workflow"]
    assert trusted["path"] == ".github/workflows/publish-package.yml"
    assert trusted["trigger"] == "workflow_dispatch"
    assert trusted["authentication"] == "PyPI Trusted Publishing via GitHub OIDC"
    assert any("check_package_publish_workflow.py" in item for item in plan["preflight_checks"])
    assert ".github/workflows/publish-package.yml" in plan["testpypi_upload"]["command"]
    assert ".github/workflows/publish-package.yml" in plan["pypi_upload"]["command"]
