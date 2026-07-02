#!/usr/bin/env python3
"""Validate the manual trusted-publishing workflow."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-package.yml"


def test_package_publish_workflow_static_contract() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert "id-token: write" in text
    assert "environment: testpypi" in text
    assert "environment: pypi" in text
    assert "repository-url: https://test.pypi.org/legacy/" in text
    assert "python scripts/check_package_index.py --index" in text
    assert "python scripts/check_package_publish_workflow.py" in text
    assert "publish software-grimoire" in text
    assert "PYPI_TOKEN" not in text
    assert "twine upload" not in text


def test_package_publish_workflow_checker_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/check_package_publish_workflow.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Package publish workflow contract is valid" in completed.stdout


def test_package_release_plan_points_to_trusted_publishing_workflow() -> None:
    plan = json.loads((ROOT / "examples" / "adoption" / "package-index-release-plan.json").read_text(encoding="utf-8"))
    trusted = plan["trusted_publishing_workflow"]
    assert trusted["path"] == ".github/workflows/publish-package.yml"
    assert trusted["trigger"] == "workflow_dispatch"
    assert trusted["authentication"] == "PyPI Trusted Publishing via GitHub OIDC"
    assert "id-token: write" in trusted["required_permissions"]
    assert set(trusted["environments"]) == {"testpypi", "pypi"}
    assert trusted["manual_confirmation"] == "publish software-grimoire"
