#!/usr/bin/env python3
"""Audit rendered internal links in the Quarto site."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import pytest


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
HREF_RE = re.compile(r"""href=["']([^"']+)["']""")
ID_RE = re.compile(r"""\s(?:id|name)=["']([^"']+)["']""")
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}


def rendered_html_files() -> list[Path]:
    if not (SITE / "index.html").exists():
        pytest.skip("_site is missing; run `quarto render` before link audit")
    return sorted(SITE.rglob("*.html"))


def anchors_by_file(files: list[Path]) -> dict[Path, set[str]]:
    anchors: dict[Path, set[str]] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        anchors[path.resolve()] = {unquote(match) for match in ID_RE.findall(text)}
    return anchors


def is_external_or_special(href: str) -> bool:
    parsed = urlparse(href)
    return bool(parsed.scheme in SKIP_SCHEMES or parsed.netloc)


def test_rendered_internal_links_resolve() -> None:
    files = rendered_html_files()
    anchors = anchors_by_file(files)
    failures: list[str] = []

    for html_path in files:
        text = html_path.read_text(encoding="utf-8")
        for href in HREF_RE.findall(text):
            href = href.strip()
            if not href or is_external_or_special(href):
                continue

            parsed = urlparse(href)
            fragment = unquote(parsed.fragment)
            path_part = unquote(parsed.path)

            if not path_part:
                if fragment and fragment not in anchors[html_path.resolve()]:
                    failures.append(f"{html_path.relative_to(SITE)} -> #{fragment}")
                continue

            target = (html_path.parent / path_part).resolve()
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                failures.append(f"{html_path.relative_to(SITE)} -> {href} escapes _site")
                continue

            if not target.exists():
                failures.append(f"{html_path.relative_to(SITE)} -> {href} missing target")
                continue

            if target.suffix == ".html" and fragment and fragment not in anchors.get(target, set()):
                failures.append(f"{html_path.relative_to(SITE)} -> {href} missing anchor")

    assert not failures, "\n".join(failures[:50])
