"""Data Governance and Target Leakage Firewall Module.

Enforces strict separation between input feature matrix X and quarantined target-reconstructing
tags (steam turbine meters, product flow, direct duties).
Governance: AGENTS.md (Pasal 2), ORIGINAL_REQUEST.md (§R3, F6).
"""
from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Set, Tuple
import numpy as np
import pandas as pd


DEFAULT_QUARANTINED_TAGS: Tuple[str, ...] = (
    "H4FI029A",              # 4KT-2 MCR LP compressor turbine steam (t/h)
    "H4FI030A",              # 4KT-3 MCR HP compressor turbine steam (t/h)
    "H4FI031A",              # 4KT-1 Propane compressor turbine steam (t/h)
    "H5FI006A",              # LNG product flow rate (target reconstructor)
    "H1FI0009",              # Raw feed gas flow (collinear baseline target)
    "total_steam_t_h",       # Aggregate driver steam
    "total_shaft_power_mw",  # Target C3MR total shaft power
    "mcr_shaft_power_mw",    # Target MCR shaft power
    "c3_shaft_power_mw",     # Target C3 shaft power
    "exergy_destruction_mw", # Target total exergy destruction
)

_VARIANT_SUFFIX_RE = re.compile(
    r"(_norm|_scaled|_std|_min|_max|_mean|_median|_lag\d+|_rolling\d+|_diff)$",
    re.IGNORECASE,
)


def strip_feature_suffix(column_name: str) -> str:
    """Strip common preprocessing/lag/rolling suffixes to expose the base tag name."""
    base = str(column_name).strip()
    while True:
        new_base = _VARIANT_SUFFIX_RE.sub("", base)
        if new_base == base:
            break
        base = new_base
    return base


def is_quarantined_column(
    column_name: str,
    quarantined_tags: Iterable[str] = DEFAULT_QUARANTINED_TAGS,
) -> bool:
    """Case-insensitive check whether a column or its derived variant belongs to quarantined tags."""
    q_lower: Set[str] = {str(t).strip().lower() for t in quarantined_tags}
    col_lower = str(column_name).strip().lower()
    base_lower = strip_feature_suffix(col_lower)
    return col_lower in q_lower or base_lower in q_lower


def enforce_leakage_firewall(
    feature_columns: Sequence[str],
    quarantined_tags: Iterable[str] = DEFAULT_QUARANTINED_TAGS,
) -> List[str]:
    """Validate feature column names against target leakage firewall.

    Raises ValueError if any quarantined tag or its derived variant is present.
    """
    offending = [col for col in feature_columns if is_quarantined_column(col, quarantined_tags)]
    if offending:
        raise ValueError(f"Target leakage firewall violation: {offending}")
    return list(feature_columns)


def filter_quarantined_dataframe(
    df: pd.DataFrame,
    quarantined_tags: Iterable[str] = DEFAULT_QUARANTINED_TAGS,
) -> pd.DataFrame:
    """Return a copy of DataFrame with all quarantined tags and variants removed."""
    keep_cols = [c for c in df.columns if not is_quarantined_column(str(c), quarantined_tags)]
    return df.loc[:, keep_cols].copy()


def check_collinear_identity_leakage(
    X: pd.DataFrame,
    y: np.ndarray,
    max_abs_corr: float = 0.9995,
) -> List[str]:
    """Detect features that trivially reconstruct the target via algebraic identity (|r| > max_abs_corr)."""
    y_arr = np.asarray(y, dtype=float).ravel()
    if y_arr.size < 3 or np.std(y_arr) < 1e-12:
        return []
    suspects: List[str] = []
    for col in X.select_dtypes(include=[np.number]).columns:
        vals = X[col].to_numpy(dtype=float)
        mask = np.isfinite(vals) & np.isfinite(y_arr)
        if mask.sum() >= 3 and np.std(vals[mask]) > 1e-12:
            r = float(np.corrcoef(vals[mask], y_arr[mask])[0, 1])
            if abs(r) >= max_abs_corr:
                suspects.append(str(col))
    return suspects

