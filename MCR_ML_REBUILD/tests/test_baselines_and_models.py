"""Unit tests for Baseline Models, Monotonic Surrogates, and Proportional MW Metrics."""
from __future__ import annotations

from pathlib import Path
import numpy as np

from src.evaluation.metrics import (
    evaluate_composition_metrics,
    evaluate_power_metrics,
    verify_model_qualification,
)
from src.models.baselines import train_and_evaluate_baselines
from src.models.surrogates import (
    build_monotonic_surrogate,
    load_surrogate_model,
    save_surrogate_model,
)


def test_proportional_mw_metrics_and_kw_guard():
    y_true_kw = np.array([105000.0, 108000.0, 99000.0, 112000.0])
    y_pred_kw = np.array([105200.0, 107800.0, 99100.0, 111800.0])
    m = evaluate_power_metrics(y_true_kw, y_pred_kw)
    assert m["mae_mw"] < 1.0
    assert m["nmae_pct"] < 1.0
    assert m["r2"] > 0.99
    assert verify_model_qualification(m) is True


def test_composition_mol_pct_metrics():
    c_t = np.array([[0.02, 0.45, 0.45, 0.01, 0.07]])
    c_p = np.array([[0.021, 0.449, 0.450, 0.010, 0.070]])
    m = evaluate_composition_metrics(c_t, c_p)
    assert m["mae_mol_pct"] < 0.2
    assert m["max_closure_deviation_mol_pct"] < 1e-6


def test_baselines_vs_monotonic_surrogate(tmp_path: Path):
    rng = np.random.default_rng(42)
    t = np.linspace(0, 6 * np.pi, 160)
    x1 = 600.0 + 220.0 * np.sin(t)
    x2 = 29.0 + 3.0 * np.cos(t)
    X = np.column_stack([x1, x2])
    y = 0.08 * x1 + 0.5 * x2 + 2.0 * np.sin(x1 / 100.0) + rng.normal(0.0, 0.15, 160)

    X_train, X_test = X[:128], X[128:]
    y_train, y_test = y[:128], y[128:]

    base_res = train_and_evaluate_baselines(X_train, y_train, X_test, y_test)
    model = build_monotonic_surrogate(monotonic_cst=[1, 1], random_state=42)
    model.fit(X_train, y_train)
    surr_res = evaluate_power_metrics(y_test, model.predict(X_test))

    assert surr_res["mae_mw"] < base_res["dummy_mean"]["mae_mw"]
    assert surr_res["r2"] > 0.90

    saved = save_surrogate_model(model, tmp_path / "m.joblib")
    loaded = load_surrogate_model(saved)
    np.testing.assert_allclose(model.predict(X_test), loaded.predict(X_test))

