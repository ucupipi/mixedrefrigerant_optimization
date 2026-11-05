"""Root ASGI entrypoint for Badak LNG Train H C3MR Decision-Support Workspace.

Allows running `uvicorn main:app` directly from the repository root directory.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Add backend and src package to sys.path
_ROOT = Path(__file__).resolve().parent
_BACKEND_DIR = _ROOT / "operator-website" / "backend"
_SRC_DIR = _BACKEND_DIR / "src"

for _d in [_BACKEND_DIR, _SRC_DIR]:
    _d_str = str(_d)
    if _d_str not in sys.path:
        sys.path.insert(0, _d_str)

# Scikit-learn Cython loss compatibility shim across Python/sklearn versions
if "_loss" not in sys.modules:
    try:
        import sklearn._loss._loss as _sklearn_subloss
        sys.modules["_loss"] = _sklearn_subloss
    except (ImportError, AttributeError):
        try:
            import sklearn._loss as _sklearn_loss
            sys.modules["_loss"] = _sklearn_loss
        except (ImportError, AttributeError):
            pass

# Load the actual backend main.py
_spec = importlib.util.spec_from_file_location("backend_main", _BACKEND_DIR / "main.py")
_backend_module = importlib.util.module_from_spec(_spec)
sys.modules["backend_main"] = _backend_module
_spec.loader.exec_module(_backend_module)

app = _backend_module.app
