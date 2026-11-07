"""Test fixtures and reference implementations for MCR_ML_REBUILD.

Governance: AGENTS.md, ORIGINAL_REQUEST.md (§R2, §R5).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Set
import pytest


@pytest.fixture(scope="session")
def rebuild_root() -> Path:
    """Root directory of MCR_ML_REBUILD package."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def default_config_path(rebuild_root: Path) -> Path:
    """Path to configs/default.yaml."""
    return rebuild_root / "configs" / "default.yaml"
