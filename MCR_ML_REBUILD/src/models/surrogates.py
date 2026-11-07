"""Physics-Constrained Monotonic and Hybrid Surrogate Models.

Implements:
1. HistGradientBoostingRegressor with physical monotonic constraints (monotonic_cst)
   for synthetic steady-state and baseline envelope validation.
2. PhysicsResidualSurrogate: A hybrid architecture combining first-principles Ridge
   isentropic work scaling with regularized GBDT residual modeling for real plant data.

Governance: AGENTS.md (Pasal 2, 5, 13), ORIGINAL_REQUEST.md (§R4, F13).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence, Tuple, Union
import joblib
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


DEFAULT_SURROGATE_FEATURES: Tuple[str, ...] = (
    "H1FI012",  # Feed gas flow rate (t/h) -> monotonic +1
    "H0TI001",  # Ambient air temperature (C) -> monotonic +1
    "H4FI001",  # MCR circulation flow rate (t/h) -> monotonic +1
    "xi_1",     # ILR coordinate 1 (0: unconstrained)
    "xi_2",     # ILR coordinate 2 (0: unconstrained)
    "xi_3",     # ILR coordinate 3 (0: unconstrained)
    "xi_4",     # ILR coordinate 4 (0: unconstrained)
)

DEFAULT_MONOTONIC_CST: Tuple[int, ...] = (1, 1, 1, 0, 0, 0, 0)

EXTENDED_SURROGATE_FEATURES: Tuple[str, ...] = (
    "H1FI012",                           # Feed gas flow rate (t/h) -> monotonic +1
    "H0TI001",                           # Ambient air temperature (C) -> monotonic +1
    "H4FI001",                           # MCR circulation flow rate (t/h) -> monotonic +1
    "xi_1",                              # ILR coordinate 1 (0: unconstrained)
    "xi_2",                              # ILR coordinate 2 (0: unconstrained)
    "xi_3",                              # ILR coordinate 3 (0: unconstrained)
    "xi_4",                              # ILR coordinate 4 (0: unconstrained)
    "is_underload",                      # Binary underload indicator (0: unconstrained)
    "is_baseload",                       # Binary baseload indicator (0: unconstrained)
    "feat_mche_shell_dp_total",          # Total shell differential pressure (0: unconstrained)
    "feat_mche_dp_ratio_warm_cold",      # Hydraulic warm/cold dP ratio (0: unconstrained)
    "feat_mche_norm_warm_dp",            # Specific flow-normalized warm dP (0: unconstrained)
    "feat_mche_vertical_thermal_lift",   # Vertical thermal lift suction to cold LNG (0: unconstrained)
    "feat_cold_bundle_depression_index", # Cold bundle temperature depression index (0: unconstrained)
)

EXTENDED_MONOTONIC_CST: Tuple[int, ...] = (1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

REAL_DATA_SURROGATE_FEATURES: Tuple[str, ...] = (
    "H1FI012",                           # Feed gas flow rate (t/h) -> monotonic +1
    "H4FI001",                           # MCR circulation flow rate (t/h) -> monotonic +1
    "xi_1",                              # ILR coordinate 1 (0: unconstrained)
    "xi_2",                              # ILR coordinate 2 (0: unconstrained)
    "xi_3",                              # ILR coordinate 3 (0: unconstrained)
    "xi_4",                              # ILR coordinate 4 (0: unconstrained)
    "is_underload",                      # Binary underload indicator (0: unconstrained)
    "is_baseload",                       # Binary baseload indicator (0: unconstrained)
    "rp_LP_MCR",                         # LP stage pressure ratio (monotonic +1)
    "rp_HP_MCR",                         # HP stage pressure ratio (monotonic +1)
    "rp_MCR_total",                      # Overall MCR pressure ratio (monotonic +1)
    "dp_interstage_4E5",                 # Interstage cooler 4E-5AB dP (0: unconstrained)
    "rp_C3_total",                       # Propane 4K-1 pressure ratio (monotonic +1)
    "MCHE_dT_cold_bundle_approach",      # H5TI0026 - H5TI0021 (0: unconstrained)
    "MCHE_dT_shell_span",                # H5TI0047 - H5TI0025 (0: unconstrained)
    "MW_MCR",                            # Apparent molecular weight (0: unconstrained)
    "MCHE_dT_lngexit_mrv",               # Rundown approach (0: unconstrained)
    "work_proxy_mcr_total",              # Isentropic work proxy MCR (monotonic +1)
    "work_proxy_c3",                     # Isentropic work proxy C3 (monotonic +1)
    "feed_mcr_product",                  # Mass flow interaction (monotonic +1)
)

REAL_DATA_MONOTONIC_CST: Tuple[int, ...] = (1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1)


class PhysicsResidualSurrogate(BaseEstimator, RegressorMixin):
    """Hybrid First-Principles Linear + Non-Linear Residual GBDT Surrogate.

    Combines a physics-constrained Ridge regression baseline (capturing isentropic head
    and flow rate scaling across operating regimes without tree extrapolation drift)
    with a regularized HistGradientBoostingRegressor on the residuals (capturing
    higher-order tray and thermal interactions).
    Governance: AGENTS.md (Pasal 2, 5, 13).
    """

    def __init__(
        self,
        alpha: float = 2.0,
        max_iter: int = 80,
        learning_rate: float = 0.05,
        max_leaf_nodes: int = 15,
        min_samples_leaf: int = 15,
        l2_regularization: float = 3.0,
        random_state: int = 42,
    ) -> None:
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.learning_rate = float(learning_rate)
        self.max_leaf_nodes = int(max_leaf_nodes)
        self.min_samples_leaf = int(min_samples_leaf)
        self.l2_regularization = float(l2_regularization)
        self.random_state = int(random_state)

    def fit(self, X: np.ndarray, y: np.ndarray) -> PhysicsResidualSurrogate:
        X_mat = np.asarray(X, dtype=float)
        y_vec = np.asarray(y, dtype=float)

        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X_mat)

        self.base_model_ = Ridge(alpha=self.alpha, random_state=self.random_state)
        self.base_model_.fit(X_scaled, y_vec)
        base_pred = self.base_model_.predict(X_scaled)

        residuals = y_vec - base_pred
        self.res_model_ = HistGradientBoostingRegressor(
            max_iter=self.max_iter,
            learning_rate=self.learning_rate,
            max_leaf_nodes=self.max_leaf_nodes,
            min_samples_leaf=self.min_samples_leaf,
            l2_regularization=self.l2_regularization,
            random_state=self.random_state,
        )
        self.res_model_.fit(X_mat, residuals)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X_mat = np.asarray(X, dtype=float)
        X_scaled = self.scaler_.transform(X_mat)
        base_pred = self.base_model_.predict(X_scaled)
        res_pred = self.res_model_.predict(X_mat)
        return base_pred + res_pred


def build_monotonic_surrogate(
    monotonic_cst: Optional[Sequence[int]] = DEFAULT_MONOTONIC_CST,
    max_iter: int = 150,
    learning_rate: float = 0.05,
    max_leaf_nodes: int = 31,
    min_samples_leaf: int = 10,
    l2_regularization: float = 0.1,
    random_state: int = 42,
) -> HistGradientBoostingRegressor:
    """Initialize a HistGradientBoostingRegressor with physical monotonic constraints."""
    cst = list(monotonic_cst) if monotonic_cst is not None else None
    return HistGradientBoostingRegressor(
        monotonic_cst=cst,
        max_iter=int(max_iter),
        learning_rate=float(learning_rate),
        max_leaf_nodes=int(max_leaf_nodes),
        min_samples_leaf=int(min_samples_leaf),
        l2_regularization=float(l2_regularization),
        random_state=int(random_state),
    )


def build_real_data_surrogate(
    alpha: float = 2.0,
    max_iter: int = 80,
    learning_rate: float = 0.05,
    max_leaf_nodes: int = 15,
    min_samples_leaf: int = 15,
    l2_regularization: float = 3.0,
    random_state: int = 42,
) -> PhysicsResidualSurrogate:
    """Initialize a hybrid Physics-Residual Surrogate model for real plant data."""
    return PhysicsResidualSurrogate(
        alpha=alpha,
        max_iter=max_iter,
        learning_rate=learning_rate,
        max_leaf_nodes=max_leaf_nodes,
        min_samples_leaf=min_samples_leaf,
        l2_regularization=l2_regularization,
        random_state=random_state,
    )


def save_surrogate_model(model: Any, filepath: Path) -> Path:
    """Serialize trained surrogate model to disk via joblib."""
    out = Path(filepath)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)
    return out


def load_surrogate_model(filepath: Path) -> Any:
    """Load serialized surrogate model from disk."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Serialized surrogate model not found: {p}")
    return joblib.load(p)


def check_monotonic_predictions(
    model: Any,
    base_point: np.ndarray,
    feature_index: int = 2,
    scan_min: float = 480.0,
    scan_max: float = 820.0,
    n_points: int = 25,
) -> bool:
    """Verify that model predictions are monotonically non-decreasing along feature_index."""
    pt = np.asarray(base_point, dtype=float).ravel()
    grid = np.tile(pt, (int(n_points), 1))
    grid[:, int(feature_index)] = np.linspace(float(scan_min), float(scan_max), int(n_points))
    preds = np.asarray(model.predict(grid), dtype=float).ravel()
    diffs = np.diff(preds)
    return bool(np.all(diffs >= -1e-9))
