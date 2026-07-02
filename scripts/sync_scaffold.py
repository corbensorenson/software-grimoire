#!/usr/bin/env python3
"""Regenerate Quarto scaffold and generated pages."""

try:
    from bootstrap_project import main
except ModuleNotFoundError:
    from scripts.bootstrap_project import main

if __name__ == "__main__":
    main()
