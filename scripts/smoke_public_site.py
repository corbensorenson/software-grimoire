#!/usr/bin/env python3
"""Smoke-check local render artifacts and optionally the public GitHub Pages site."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_REQUIRED = [
    "index.html",
    "reference/evidence-browser.html",
    "reference/calibration.html",
    "reference/hardness-v4.html",
    "reference/ward-science.html",
    "reference/canon-review-queue.html",
    "reference/methods-structure-reviewability-warding.html",
    "reference/logical-conclusion-status.html",
    "reference/package-index-release.html",
    "examples/evaluations/index.html",
    "examples/jailbreak-resilience/index.html",
]
RESOURCE_REQUIRED = [
    "data/evidence_taxonomy.json",
    "data/evidence_index.json",
    "data/logical_conclusion_status.json",
    "data/canon_review_queue.json",
    "examples/canon/canon-audit-decision-template.json",
    "examples/evaluations/model-execution-results.json",
    "examples/evaluations/hardness-v4/results.json",
    "examples/evaluations/hardness-v4/model-surface-results.json",
    "examples/evaluations/hardness-v4/manual-import-template.json",
    "examples/adoption/package-index-release-plan.json",
    "examples/adoption/package-index-smoke-template.json",
    "examples/jailbreak-resilience/ab-results.json",
    "examples/jailbreak-resilience/ward-science-results.json",
    "exports/library-manifest.json",
    "exports/checksums.sha256",
]


def report_path(value: str) -> Path:
    path = Path(value).expanduser()
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("Report path must stay inside this repository; use tmp/... for scratch reports.") from exc
    return resolved


def display_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def fetch(url: str, timeout: int = 20) -> tuple[bool, int | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read(1024).decode("utf-8", errors="replace")
            return 200 <= response.status < 400, response.status, body
    except urllib.error.HTTPError as exc:
        return False, exc.code, exc.reason
    except Exception as exc:
        return False, None, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", default="_site")
    parser.add_argument("--live-url", default="")
    parser.add_argument("--write-report", default="examples/release-gate/public-smoke-check.json")
    args = parser.parse_args()

    site = ROOT / args.site_dir
    checks = []
    for rel in LOCAL_REQUIRED:
        path = site / rel
        checks.append({"kind": "local_html", "target": rel, "passed": path.exists() and path.stat().st_size > 0})
    for rel in RESOURCE_REQUIRED:
        path = site / rel
        checks.append({"kind": "local_resource", "target": rel, "passed": path.exists() and path.stat().st_size > 0})
    if args.live_url:
        for rel in ["", "reference/evidence-browser.html", "exports/library-manifest.json"]:
            url = args.live_url.rstrip("/") + "/" + rel
            ok, status, sample = fetch(url)
            checks.append({"kind": "live_url", "target": url, "passed": ok, "status": status, "sample": sample[:200]})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "site_dir": args.site_dir,
        "live_url": args.live_url,
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
    }
    try:
        out = report_path(args.write_report)
    except ValueError as exc:
        parser.error(str(exc))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {display_path(out)}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
