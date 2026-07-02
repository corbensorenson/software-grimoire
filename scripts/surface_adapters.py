#!/usr/bin/env python3
"""Shared model/tool surface adapters for Software Grimoire benches."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_BIN = Path("/Applications/Codex.app/Contents/Resources/codex")


def command_version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True, timeout=20)
    except Exception:
        return "unknown"
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else "unknown"


def codex_available() -> bool:
    return CODEX_BIN.exists()


def claude_available() -> bool:
    return shutil.which("claude") is not None


def surface_catalog() -> dict[str, dict]:
    return {
        "codex-cli-default": {
            "surface_id": "codex-cli-default",
            "kind": "codex",
            "label": "Codex CLI default model",
            "ownership": "project-owned",
            "execution": "local read-only CLI",
            "requires_credentials": False,
            "redaction_policy": "Public fixtures only; no secrets intentionally supplied.",
            "tool_name": "Codex CLI",
            "tool_version": command_version([str(CODEX_BIN), "--version"]) if codex_available() else "unavailable",
            "model_name": "default",
            "evidence_class": "project_owned_model_run",
            "available": codex_available(),
            "timeout_seconds": 240,
        },
        "claude-code-safe": {
            "surface_id": "claude-code-safe",
            "kind": "claude-code",
            "label": "Claude Code CLI with tools disabled",
            "ownership": "project-owned",
            "execution": "local CLI, print mode, tools disabled",
            "requires_credentials": True,
            "redaction_policy": "Public fixtures only; outputs are redacted for fixture canaries and forbidden operational strings before publication.",
            "tool_name": "Claude Code",
            "tool_version": command_version(["claude", "--version"]) if claude_available() else "unavailable",
            "model_name": "default",
            "evidence_class": "project_owned_model_run",
            "available": claude_available(),
            "timeout_seconds": 240,
        },
        "manual-reviewer-import": {
            "surface_id": "manual-reviewer-import",
            "kind": "manual-import",
            "label": "Reviewer supplied model/tool transcript",
            "ownership": "reviewer-supplied",
            "execution": "manual import",
            "requires_credentials": False,
            "redaction_policy": "Reviewer must declare redactions and provenance.",
            "tool_name": "manual",
            "tool_version": "n/a",
            "model_name": "declared-by-reviewer",
            "evidence_class": "reviewer_supplied_model_run",
            "available": True,
            "timeout_seconds": 0,
        },
    }


def runnable_surfaces(available_only: bool = True) -> dict[str, dict]:
    surfaces = {surface_id: item for surface_id, item in surface_catalog().items() if item["kind"] != "manual-import"}
    if available_only:
        surfaces = {surface_id: item for surface_id, item in surfaces.items() if item["available"]}
    return surfaces


def surface_for_result(surface_id: str) -> dict:
    surface = surface_catalog()[surface_id]
    return {
        "kind": surface["kind"],
        "label": surface["label"],
        "ownership": surface["ownership"],
        "execution": surface["execution"],
        "requires_credentials": surface["requires_credentials"],
        "redaction_policy": surface["redaction_policy"],
        "tool_name": surface["tool_name"],
        "tool_version": surface["tool_version"],
        "model_name": surface["model_name"],
        "evidence_class": surface["evidence_class"],
    }


def run_codex(prompt: str, timeout: int = 240) -> str:
    if not codex_available():
        raise RuntimeError("Codex CLI is not available")
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [
                str(CODEX_BIN),
                "exec",
                "--ephemeral",
                "--ignore-rules",
                "-s",
                "read-only",
                "-o",
                str(out_path),
                prompt,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
        return out_path.read_text(encoding="utf-8").strip()
    finally:
        out_path.unlink(missing_ok=True)


def run_claude(prompt: str, timeout: int = 240) -> str:
    if not claude_available():
        raise RuntimeError("Claude Code CLI is not available")
    result = subprocess.run(
        [
            "claude",
            "-p",
            "--tools",
            "",
            "--no-session-persistence",
            "--permission-mode",
            "dontAsk",
            "--max-budget-usd",
            "0.25",
            prompt,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def run_surface(surface_id: str, prompt: str) -> str:
    surface = surface_catalog()[surface_id]
    if surface["kind"] == "codex":
        return run_codex(prompt, surface["timeout_seconds"])
    if surface["kind"] == "claude-code":
        return run_claude(prompt, surface["timeout_seconds"])
    raise ValueError(f"Surface {surface_id!r} is not runnable")


def enrich_run_metadata(surface_id: str) -> dict:
    surface = surface_catalog()[surface_id]
    return {
        "surface": surface_id,
        "surface_id": surface_id,
        "surface_kind": surface["kind"],
        "surface_label": surface["label"],
        "tool_name": surface["tool_name"],
        "tool_version": surface["tool_version"],
        "model_name": surface["model_name"],
        "provenance": surface["ownership"],
        "evidence_class": surface["evidence_class"],
        "redaction_policy": surface["redaction_policy"],
    }
