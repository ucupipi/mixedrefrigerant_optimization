"""Baseline Reference Models (Dummy Mean Regressor & Ridge Linear Benchmark).

Establishes simple, interpretable baseline performance before fitting non-linear surrogates.
Governance: AGENTS.md (Bab II §3), ORIGINAL_REQUEST.md (§R4, F12).
"""
from __future__ import annotations

from typing import Dict
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.evaluation.metrics import evaluate_power_metrics


def build_dummy_baseline(strategy: str = "mean") -> DummyRegressor:
    """Create a DummyRegressor baseline predicting training set mean/median."""
    return DummyRegressor(strategy=strategy)


def build_ridge_baseline(alpha: float = 1.0, random_state: int = 42) -> Pipeline:
    """Create a standardized Ridge linear regression benchmark pipeline."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=float(alpha), random_state=int(random_state))),
    ])


def train_and_evaluate_baselines(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    alpha: float = 1.0,
    random_state: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Fit Dummy and Ridge baselines on train split and evaluate on test split in MW."""
    dummy = build_dummy_baseline("mean")
    dummy.fit(X_train, y_train)
    dummy_preds = dummy.predict(X_test)

    ridge = build_ridge_baseline(alpha=alpha, random_state=random_state)
    ridge.fit(X_train, y_train)
    ridge_preds = ridge.predict(X_test)

    return {
        "dummy_mean": evaluate_power_metrics(y_test, dummy_preds),
        "ridge_linear": evaluate_power_metrics(y_test, ridge_preds),
    }

