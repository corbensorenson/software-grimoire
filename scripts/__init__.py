"""Import helpers for script modules used by tests.

Most files in this directory are executable scripts. Adding the directory to
``sys.path`` lets package imports such as ``scripts.run_evaluations`` resolve
the sibling ``grimoire_build`` package the same way direct script execution
does.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
