"""Proportional Engineering Metric Suite for Power (MW) and Composition (mol%).

Enforces AGENTS.md Pasal 2 and Pasal 13:
- Power & Exergy MAE and RMSE reported strictly in MW (< 1.0 MW).
- Normalized / Relative MAE (NMAE) reported in % (< 1.0%).
- Out-of-sample coefficient of determination R² >= 0.60.
- Composition error reported in mol% with simplex closure sum = 100.0 mol%.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List
import numpy as np


def compute_bootstrap_ci_mw(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_boot: int = 500,
    ci: float = 0.95,
    random_state: int = 42,
) -> Dict[str, float]:
    """Compute paired non-parametric bootstrap confidence intervals in MW and NMAE %."""
    y_t = np.asarray(y_true, dtype=float).ravel()
    y_p = np.asarray(y_pred, dtype=float).ravel()
    if y_t.size != y_p.size or y_t.size == 0:
        raise ValueError("y_true and y_pred must be non-empty arrays of identical length")

    if float(np.median(y_t)) > 1000.0:
        y_t = y_t / 1000.0
    if float(np.median(y_p)) > 1000.0:
        y_p = y_p / 1000.0

    rng = np.random.default_rng(random_state)
    n = y_t.size
    abs_err = np.abs(y_t - y_p)
    sq_err = (y_t - y_p) ** 2
    mean_true = float(np.mean(y_t))

    idx = rng.integers(0, n, size=(int(n_boot), n))
    boot_mae = np.mean(abs_err[idx], axis=1)
    boot_rmse = np.sqrt(np.mean(sq_err[idx], axis=1))
    boot_nmae = (boot_mae / mean_true) * 100.0 if abs(mean_true) > 1e-12 else np.zeros_like(boot_mae)

    alpha = (1.0 - float(ci)) / 2.0
    lo_q = 100.0 * alpha
    hi_q = 100.0 * (1.0 - alpha)

    return {
        "mae_ci_lower_mw": float(np.percentile(boot_mae, lo_q)),
        "mae_ci_upper_mw": float(np.percentile(boot_mae, hi_q)),
        "rmse_ci_lower_mw": float(np.percentile(boot_rmse, lo_q)),
        "rmse_ci_upper_mw": float(np.percentile(boot_rmse, hi_q)),
        "nmae_ci_lower_pct": float(np.percentile(boot_nmae, lo_q)),
        "nmae_ci_upper_pct": float(np.percentile(boot_nmae, hi_q)),
    }


def evaluate_blocked_timeseries_cv(
    X: np.ndarray,
    y: np.ndarray,
    model_builder: Callable[[], Any],
    n_splits: int = 3,
    purge_buffer: int = 2,
) -> Dict[str, Any]:
    """Evaluate expanding-window blocked time-series cross-validation with purge buffer."""
    X_arr = np.asarray(X, dtype=float)
    y_arr = np.asarray(y, dtype=float).ravel()
    n = len(y_arr)
    if n < (n_splits + 1) * 10:
        raise ValueError(f"Insufficient samples ({n}) for {n_splits}-fold blocked CV")

    fold_size = n // (n_splits + 1)
    fold_metrics: List[Dict[str, float]] = []

    for k in range(1, n_splits + 1):
        train_end = k * fold_size
        val_start = min(n, train_end + int(purge_buffer))
        val_end = min(n, (k + 1) * fold_size)
        if val_end - val_start < 4:
            continue
        model = model_builder()
        model.fit(X_arr[:train_end], y_arr[:train_end])
        preds = model.predict(X_arr[val_start:val_end])
        m = evaluate_power_metrics(y_arr[val_start:val_end], preds)
        fold_metrics.append(m)

    return {
        "n_splits": len(fold_metrics),
        "mean_mae_mw": float(np.mean([m["mae_mw"] for m in fold_metrics])),
        "mean_rmse_mw": float(np.mean([m["rmse_mw"] for m in fold_metrics])),
        "mean_nmae_pct": float(np.mean([m["nmae_pct"] for m in fold_metrics])),
        "mean_r2": float(np.mean([m["r2"] for m in fold_metrics])),
        "folds": fold_metrics,
    }


def evaluate_power_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate proportional engineering metrics in MW (MAE, RMSE, NMAE %, R²)."""
    y_t = np.asarray(y_true, dtype=float).ravel()
    y_p = np.asarray(y_pred, dtype=float).ravel()
    if y_t.size != y_p.size or y_t.size == 0:
        raise ValueError("y_true and y_pred must be non-empty arrays of identical length")

    # Scale guard: convert raw kW (> 1000) to MW
    if float(np.median(y_t)) > 1000.0:
        y_t = y_t / 1000.0
    if float(np.median(y_p)) > 1000.0:
        y_p = y_p / 1000.0

    mae_mw = float(np.mean(np.abs(y_t - y_p)))
    rmse_mw = float(np.sqrt(np.mean((y_t - y_p) ** 2)))
    mean_true = float(np.mean(y_t))
    nmae_pct = float((mae_mw / mean_true) * 100.0) if abs(mean_true) > 1e-12 else 0.0

    ss_res = float(np.sum((y_t - y_p) ** 2))
    ss_tot = float(np.sum((y_t - mean_true) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 0.0

    return {
        "mae_mw": mae_mw,
        "rmse_mw": rmse_mw,
        "nmae_pct": nmae_pct,
        "r2": r2,
    }


def evaluate_composition_metrics(comp_true: np.ndarray, comp_pred: np.ndarray) -> Dict[str, float]:
    """Evaluate 5-component composition prediction error in mol% and verify closure."""
    c_t = np.atleast_2d(np.asarray(comp_true, dtype=float))
    c_p = np.atleast_2d(np.asarray(comp_pred, dtype=float))
    if c_t.shape != c_p.shape:
        raise ValueError(f"Composition shapes must match: {c_t.shape} vs {c_p.shape}")

    # Convert mole fractions [0, 1] to mol% [0, 100] if needed
    scale_t = 100.0 if float(np.median(c_t.sum(axis=-1))) <= 1.5 else 1.0
    scale_p = 100.0 if float(np.median(c_p.sum(axis=-1))) <= 1.5 else 1.0
    t_pct = c_t * scale_t
    p_pct = c_p * scale_p

    abs_err_pct = np.abs(t_pct - p_pct)
    closure_dev_pct = float(np.max(np.abs(p_pct.sum(axis=-1) - 100.0)))

    return {
        "mae_mol_pct": float(np.mean(abs_err_pct)),
        "max_component_err_mol_pct": float(np.max(abs_err_pct)),
        "max_closure_deviation_mol_pct": closure_dev_pct,
    }


def verify_model_qualification(
    metrics: Dict[str, float],
    max_mae_mw: float = 1.0,
    max_nmae_pct: float = 1.0,
    min_r2: float = 0.60,
) -> bool:
    """Verify whether evaluated power metrics satisfy AGENTS.md Pasal 2 & 13 gates."""
    return (
        float(metrics.get("mae_mw", 999.0)) < float(max_mae_mw)
        and float(metrics.get("nmae_pct", 999.0)) < float(max_nmae_pct)
        and float(metrics.get("r2", -1.0)) >= float(min_r2)
    )

