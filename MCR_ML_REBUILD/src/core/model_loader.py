"""Model loader module for Operator Decision-Support Website.

Safely locates, resolves dependencies, and caches the C3MR Power Surrogate model.
Governance: AGENTS.md (Pasal 1, 2, 5), Read-only decision-support mode.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional
import joblib
import joblib.numpy_pickle

# Scikit-learn Cython loss compatibility shim across Python/sklearn versions (e.g. Python 3.14/sklearn 1.9)
if "_loss" not in sys.modules:
    try:
        import sklearn._loss._loss as _loss_submod
        sys.modules["_loss"] = _loss_submod
    except Exception:
        try:
            import sklearn._loss as _loss_mod
            sys.modules["_loss"] = _loss_mod
        except Exception:
            pass

# Unpickling compatibility hook for HistGradientBoosting Cython loss across Python/sklearn versions
_orig_joblib_find_class = joblib.numpy_pickle.NumpyUnpickler.find_class

def _patch_unpickler_find_class(self, module: str, name: str) -> Any:
    if module == "_loss" or module.endswith("._loss"):
        for mod_name in ["sklearn._loss._loss", "sklearn._loss", "sklearn._loss.loss"]:
            try:
                mod = __import__(mod_name, fromlist=[name])
                if hasattr(mod, name):
                    return getattr(mod, name)
            except Exception:
                continue
    return _orig_joblib_find_class(self, module, name)

joblib.numpy_pickle.NumpyUnpickler.find_class = _patch_unpickler_find_class

_CACHED_MODEL: Optional[Any] = None
_MODEL_PATH_LOADED: Optional[Path] = None


def get_rebuild_root() -> Path:
    """Resolve path to MCR_ML_REBUILD root directory."""
    current_file = Path(__file__).resolve()
    # Check standalone deployment locations in backend directory
    backend_dir = current_file.parent.parent
    if (backend_dir / "src").exists():
        return backend_dir
    if (backend_dir / "MCR_ML_REBUILD" / "src").exists():
        return backend_dir / "MCR_ML_REBUILD"

    # Check parent project root
    for candidate_parent in [current_file.parents[3], current_file.parents[2], current_file.parents[1]]:
        target = candidate_parent / "MCR_ML_REBUILD"
        if target.exists() and (target / "src").exists():
            return target
    # Fallback to relative path from cwd
    cwd_candidate = Path("MCR_ML_REBUILD").resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    raise FileNotFoundError("MCR_ML_REBUILD directory not found for model resolution.")


def ensure_rebuild_in_path() -> Path:
    """Ensure MCR_ML_REBUILD is present in sys.path so joblib can unpickle surrogate classes."""
    rebuild_root = get_rebuild_root()
    rebuild_str = str(rebuild_root)
    if rebuild_str not in sys.path:
        sys.path.insert(0, rebuild_str)

    # Scikit-learn Cython loss compatibility shim across Python/sklearn versions (e.g. Python 3.14/sklearn 1.9)
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

    return rebuild_root


def get_model_path() -> Path:
    """Find the serialized surrogate model artifact."""
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent

    # Standalone deployment fallback (models stored directly in backend/models)
    standalone_model = backend_dir / "models" / "c3mr_power_surrogate_real.joblib"
    if standalone_model.exists():
        return standalone_model

    rebuild_root = get_rebuild_root()
    models_dir = rebuild_root / "models"
    
    # Priority 1: Real-data qualified surrogate
    real_model = models_dir / "c3mr_power_surrogate_real.joblib"
    if real_model.exists():
        return real_model
        
    # Priority 2: Standard surrogate artifact
    std_model = models_dir / "c3mr_power_surrogate.joblib"
    if std_model.exists():
        return std_model
        
    raise FileNotFoundError(f"Surrogate model artifact not found in {models_dir}")


def load_surrogate_model(force_reload: bool = False) -> Any:
    """Load and cache the trained surrogate model singleton."""
    global _CACHED_MODEL, _MODEL_PATH_LOADED
    if _CACHED_MODEL is not None and not force_reload:
        return _CACHED_MODEL

    ensure_rebuild_in_path()
    model_path = get_model_path()
    model = joblib.load(model_path)
    _CACHED_MODEL = model
    _MODEL_PATH_LOADED = model_path
    return _CACHED_MODEL


def get_model_info() -> dict:
    """Return metadata about the loaded surrogate model."""
    ensure_rebuild_in_path()
    model = load_surrogate_model()
    model_path = _MODEL_PATH_LOADED or get_model_path()
    
    from src.models.surrogates import REAL_DATA_SURROGATE_FEATURES, REAL_DATA_MONOTONIC_CST
    
    return {
        "model_file": model_path.name,
        "model_type": type(model).__name__,
        "n_features": len(REAL_DATA_SURROGATE_FEATURES),
        "features": list(REAL_DATA_SURROGATE_FEATURES),
        "monotonic_constraints": list(REAL_DATA_MONOTONIC_CST),
        "target": "total_shaft_power_mw",
        "unit": "MW",
        "governance": "AGENTS.md Pasal 2, 10, 13 (Proportional MW, Leakage Firewall)",
    }

