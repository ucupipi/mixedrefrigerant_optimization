"""Command Line Interface entry point for MCR_ML_REBUILD.

Governance: AGENTS.md, ORIGINAL_REQUEST.md (§R2).
Provides subcommands: audit, verify, ingest, preprocess, train, evaluate, predict, infer.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Ensure package root is in sys.path when invoked directly as a script
_package_root = Path(__file__).resolve().parent.parent
if str(_package_root) not in sys.path:
    sys.path.insert(0, str(_package_root))

from src.cli.commands import (
    build_parser,
    handle_audit,
    handle_evaluate,
    handle_infer,
    handle_ingest,
    handle_predict,
    handle_preprocess,
    handle_train,
    handle_verify,
    main as _commands_main,
)

__all__ = [
    "build_parser",
    "handle_audit",
    "handle_evaluate",
    "handle_infer",
    "handle_ingest",
    "handle_predict",
    "handle_preprocess",
    "handle_train",
    "handle_verify",
    "main",
]


def main(argv: Optional[List[str]] = None) -> int:
    """Parse command line arguments using standard library argparse and dispatch to handlers.

    Supported subcommands: audit, verify, ingest, preprocess, train, evaluate, predict, infer.
    """
    return _commands_main(argv)


if __name__ == "__main__":
    sys.exit(main())
