"""CLI subpackage for MCR_ML_REBUILD.

Governance: AGENTS.md, ORIGINAL_REQUEST.md (§R2).
Exposes build_parser and main entry points for module-level importation.
"""
from __future__ import annotations

import sys
from pathlib import Path

_package_root = Path(__file__).resolve().parent.parent.parent
if str(_package_root) not in sys.path:
    sys.path.insert(0, str(_package_root))

from src.cli.commands import build_parser, main

__all__ = ["build_parser", "main"]
