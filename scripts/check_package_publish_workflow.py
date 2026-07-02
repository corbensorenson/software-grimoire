#!/usr/bin/env python3
"""Validate the manual package-index publish workflow contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
ROOT = SOURCE_ROOT if (SOURCE_ROOT / "pyproject.toml").exists() else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "publish-package.yml"
PLAN = ROOT / "examples" / "adoption" / "package-index-release-plan.json"
CONFIRMATION = "publish software-grimoire"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def require_text(errors: list[str], text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(errors, f"publish workflow missing {label}: {needle}")


def check_no_secret_upload_path(errors: list[str], text: str) -> None:
    forbidden = [
        r"PYPI_TOKEN",
        r"TEST_PYPI_TOKEN",
        r"pypi_password",
        r"password:\s*\$\{\{\s*secrets\.",
        r"username:\s*__token__",
        r"twine\s+upload",
    ]
    for pattern in forbidden:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(errors, f"publish workflow must use trusted publishing, not secret/token upload path: {pattern}")


def check_manual_only(errors: list[str], text: str) -> None:
    require_text(errors, text, "workflow_dispatch:", "manual dispatch trigger")
    trigger_block = text.split("permissions:", 1)[0]
    for forbidden in ["pull_request:", "push:", "release:", "schedule:"]:
        if forbidden in trigger_block:
            fail(errors, f"publish workflow must stay manual-only; found trigger {forbidden}")


def check_workflow(errors: list[str]) -> None:
    if not WORKFLOW.exists():
        fail(errors, f"missing publish workflow: {WORKFLOW.relative_to(ROOT)}")
        return
    text = WORKFLOW.read_text(encoding="utf-8")
    check_manual_only(errors, text)
    check_no_secret_upload_path(errors, text)
    for needle, label in [
        ("pypa/gh-action-pypi-publish@release/v1", "PyPA trusted publishing action"),
        ("id-token: write", "OIDC id-token permission"),
        ("environment: testpypi", "TestPyPI protected environment"),
        ("environment: pypi", "PyPI protected environment"),
        ("repository-url: https://test.pypi.org/legacy/", "TestPyPI repository URL"),
        ("python scripts/bootstrap_project.py", "bootstrap preflight"),
        ("python scripts/validate_data.py", "data validation preflight"),
        ("python scripts/check_package_publish_workflow.py", "self-validation preflight"),
        ("python -m pytest", "test preflight"),
        ("python scripts/check_package.py", "local package smoke preflight"),
        ("python scripts/check_package_index.py --index", "public-index smoke contract"),
        ("python -m build", "distribution build"),
        ("python -m twine check dist/*", "distribution metadata check"),
        ("actions/upload-artifact@v4", "distribution/report artifacts"),
        ("actions/download-artifact@v4", "distribution download"),
        (CONFIRMATION, "manual confirmation phrase"),
    ]:
        require_text(errors, text, needle, label)


def check_plan(errors: list[str]) -> None:
    if not PLAN.exists():
        fail(errors, f"missing package-index release plan: {PLAN.relative_to(ROOT)}")
        return
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    trusted = plan.get("trusted_publishing_workflow", {})
    if trusted.get("path") != ".github/workflows/publish-package.yml":
        fail(errors, "release plan must point to .github/workflows/publish-package.yml")
    if trusted.get("trigger") != "workflow_dispatch":
        fail(errors, "release plan must keep package publishing workflow_dispatch-only")
    if trusted.get("authentication") != "PyPI Trusted Publishing via GitHub OIDC":
        fail(errors, "release plan must require PyPI Trusted Publishing via GitHub OIDC")
    if "id-token: write" not in trusted.get("required_permissions", []):
        fail(errors, "release plan must record id-token: write as required permission")
    if set(trusted.get("environments", [])) != {"testpypi", "pypi"}:
        fail(errors, "release plan must record testpypi and pypi environments")
    if trusted.get("manual_confirmation") != CONFIRMATION:
        fail(errors, "release plan manual confirmation phrase must match workflow")
    for upload_key in ["testpypi_upload", "pypi_upload"]:
        upload = plan.get(upload_key, {})
        if upload.get("human_required") is not True:
            fail(errors, f"{upload_key} must require a human maintainer")
        if ".github/workflows/publish-package.yml" not in upload.get("command", ""):
            fail(errors, f"{upload_key} command must dispatch the package publish workflow")
        if "scripts/check_package_index.py" not in upload.get("post_upload_check", ""):
            fail(errors, f"{upload_key} must keep the public-index smoke checker")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    errors: list[str] = []
    check_workflow(errors)
    check_plan(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Package publish workflow contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
