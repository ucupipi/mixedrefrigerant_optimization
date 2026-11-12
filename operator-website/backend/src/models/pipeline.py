"""End-to-End Training, Validation, and Evaluation Pipeline for MCR_ML_REBUILD.

Executes chronological train/test partitioning, leakage firewall enforcement, baseline
comparison, monotonic and hybrid surrogate training, and engineering metric reporting in MW.
Supports both synthetic steady-state data and real plant shift records (1,475 shifts).
Governance: AGENTS.md (Pasal 2, 10, 13), ORIGINAL_REQUEST.md (§R4, §R5).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import numpy as np
import pandas as pd

from src.data.governance import DEFAULT_QUARANTINED_TAGS, enforce_leakage_firewall
from src.data.ingestion import build_real_plant_datasets, save_processed_datasets
from src.evaluation.metrics import (
    compute_bootstrap_ci_mw,
    evaluate_blocked_timeseries_cv,
    evaluate_power_metrics,
    verify_model_qualification,
)
from src.features.engineering import (
    add_compressor_and_jt_physics_features,
    add_mche_regime_and_dp_features,
    chronological_train_test_split,
)
from src.models.baselines import train_and_evaluate_baselines
from src.models.mlflow_tracker import MLflowExperimentTracker
from src.models.surrogates import (
    DEFAULT_MONOTONIC_CST,
    DEFAULT_SURROGATE_FEATURES,
    EXTENDED_MONOTONIC_CST,
    EXTENDED_SURROGATE_FEATURES,
    REAL_DATA_MONOTONIC_CST,
    REAL_DATA_SURROGATE_FEATURES,
    build_monotonic_surrogate,
    build_real_data_surrogate,
    save_surrogate_model,
)


def run_training_pipeline(
    processed_dir: Path,
    models_dir: Path,
    reports_dir: Path,
    feature_cols: Optional[Sequence[str]] = None,
    monotonic_cst: Optional[Sequence[int]] = None,
    target_col: str = "total_shaft_power_mw",
    test_ratio: float = 0.20,
    random_state: int = 42,
    use_extended_features: bool = False,
    data_source: str = "synthetic",
    force_rebuild: bool = False,
) -> Dict[str, Any]:
    """Execute end-to-end training and evaluation pipeline on unleakaged shift datasets."""
    proc_path = Path(processed_dir)
    feat_file = proc_path / "features_unleakaged.parquet"
    target_file = proc_path / "target_energy.parquet"

    if data_source == "real":
        # Always build directly from master_shift_level.parquet for real plant data
        features_df, targets_df = build_real_plant_datasets()
        features_df = add_mche_regime_and_dp_features(features_df)
        features_df = add_compressor_and_jt_physics_features(features_df)
        if feature_cols is None:
            feature_cols = REAL_DATA_SURROGATE_FEATURES
        if monotonic_cst is None:
            monotonic_cst = REAL_DATA_MONOTONIC_CST
    else:
        if force_rebuild or not feat_file.exists() or not target_file.exists():
            save_processed_datasets(proc_path, n_shifts=240, random_state=random_state, data_source="synthetic")

        features_df = pd.read_parquet(feat_file)
        targets_df = pd.read_parquet(target_file)

        if use_extended_features:
            features_df = add_mche_regime_and_dp_features(features_df)
            if feature_cols is None:
                feature_cols = EXTENDED_SURROGATE_FEATURES
            if monotonic_cst is None:
                monotonic_cst = EXTENDED_MONOTONIC_CST
        else:
            if feature_cols is None:
                feature_cols = DEFAULT_SURROGATE_FEATURES
            if monotonic_cst is None:
                monotonic_cst = DEFAULT_MONOTONIC_CST

        missing_feats = [c for c in feature_cols if c not in features_df.columns]
        if missing_feats:
            features_df = add_mche_regime_and_dp_features(features_df)

    # Strict leakage firewall verification
    enforce_leakage_firewall(list(features_df.columns), DEFAULT_QUARANTINED_TAGS)
    enforce_leakage_firewall(list(feature_cols), DEFAULT_QUARANTINED_TAGS)

    merged = pd.merge(features_df, targets_df[["shift_id", target_col]], on="shift_id", how="inner")
    train_df, test_df = chronological_train_test_split(
        merged, test_ratio=test_ratio, purge_buffer=2, timestamp_col="shift_id"
    )

    X_train = train_df.loc[:, list(feature_cols)].to_numpy(dtype=float)
    y_train = train_df[target_col].to_numpy(dtype=float)
    X_test = test_df.loc[:, list(feature_cols)].to_numpy(dtype=float)
    y_test = test_df[target_col].to_numpy(dtype=float)

    baseline_results = train_and_evaluate_baselines(
        X_train, y_train, X_test, y_test, alpha=1.0, random_state=random_state
    )

    if data_source == "real":
        surrogate = build_real_data_surrogate(
            alpha=2.0,
            max_iter=80,
            learning_rate=0.05,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=3.0,
            random_state=random_state,
        )
        model_builder = lambda: build_real_data_surrogate(
            alpha=2.0,
            max_iter=80,
            learning_rate=0.05,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=3.0,
            random_state=random_state,
        )
        run_name = "physics_residual_surrogate_real_data_80_20"
    else:
        surrogate = build_monotonic_surrogate(
            monotonic_cst=monotonic_cst,
            max_iter=200,
            learning_rate=0.05,
            random_state=random_state,
        )
        model_builder = lambda: build_monotonic_surrogate(
            monotonic_cst=monotonic_cst,
            max_iter=200,
            learning_rate=0.05,
            random_state=random_state,
        )
        run_name = "monotonic_hgb_chronological_80_20"

    surrogate.fit(X_train, y_train)
    y_pred_test = surrogate.predict(X_test)
    surrogate_metrics = evaluate_power_metrics(y_test, y_pred_test)
    bootstrap_ci = compute_bootstrap_ci_mw(y_test, y_pred_test, n_boot=500, ci=0.95, random_state=random_state)
    blocked_cv = evaluate_blocked_timeseries_cv(
        X_train,
        y_train,
        model_builder=model_builder,
        n_splits=3,
        purge_buffer=2,
    )
    qualified = verify_model_qualification(surrogate_metrics)

    # Regime-stratified evaluation on out-of-sample test split
    regime_stratified_metrics: Dict[str, Any] = {}
    test_feed_col = "H1FI012" if "H1FI012" in test_df.columns else None
    if test_feed_col:
        test_flows = test_df[test_feed_col].to_numpy(dtype=float)
        under_mask = test_flows <= 226.8
        base_mask = test_flows >= 279.8
        trans_mask = (test_flows > 226.8) & (test_flows < 279.8)

        if np.sum(under_mask) >= 2:
            regime_stratified_metrics["underload"] = {
                "n_samples": int(np.sum(under_mask)),
                "metrics": evaluate_power_metrics(y_test[under_mask], y_pred_test[under_mask]),
            }
        if np.sum(base_mask) >= 2:
            regime_stratified_metrics["baseload"] = {
                "n_samples": int(np.sum(base_mask)),
                "metrics": evaluate_power_metrics(y_test[base_mask], y_pred_test[base_mask]),
            }
        if np.sum(trans_mask) >= 2:
            regime_stratified_metrics["transition"] = {
                "n_samples": int(np.sum(trans_mask)),
                "metrics": evaluate_power_metrics(y_test[trans_mask], y_pred_test[trans_mask]),
            }

    models_out = Path(models_dir)
    primary_model_name = "c3mr_power_surrogate_real.joblib" if data_source == "real" else "c3mr_power_surrogate.joblib"
    model_artifact_path = save_surrogate_model(surrogate, models_out / primary_model_name)
    if data_source == "real":
        save_surrogate_model(surrogate, models_out / "c3mr_power_surrogate.joblib")

    reports_out = Path(reports_dir)
    reports_out.mkdir(parents=True, exist_ok=True)

    tracker = MLflowExperimentTracker(tracking_dir=reports_out / "mlruns")
    mlflow_run = tracker.log_training_run(
        run_name=run_name,
        params={
            "data_source": data_source,
            "target_column": target_col,
            "test_ratio": test_ratio,
            "purge_buffer": 2,
            "random_state": random_state,
            "n_train": int(len(train_df)),
            "n_test": int(len(test_df)),
            "n_features": len(feature_cols),
            "extended_features": use_extended_features or (data_source == "real"),
        },
        metrics=surrogate_metrics,
        bootstrap_ci=bootstrap_ci,
        blocked_cv=blocked_cv,
        model_artifact_path=model_artifact_path,
        tags={
            "plant": "Baseload_LNG_Train_H",
            "unit": "MW",
            "data_source": data_source,
            "governance": "AGENTS_MD_PASAL_2_13",
        },
    )

    report_payload: Dict[str, Any] = {
        "data_source": data_source,
        "target_column": target_col,
        "unit": "MW",
        "n_train": int(len(train_df)),
        "n_test": int(len(test_df)),
        "features": list(feature_cols),
        "monotonic_constraints": list(monotonic_cst),
        "baselines": baseline_results,
        "surrogate_test_metrics": surrogate_metrics,
        "regime_stratified_metrics": regime_stratified_metrics,
        "bootstrap_95_ci_mw": bootstrap_ci,
        "blocked_cv_metrics": blocked_cv,
        "mlflow_run_id": mlflow_run["run_id"],
        "qualified": bool(qualified),
        "model_artifact": str(model_artifact_path.name),
    }

    primary_report = "evaluation_report_real.json" if data_source == "real" else "evaluation_report.json"
    with open(reports_out / primary_report, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)
    if data_source == "real":
        with open(reports_out / "evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)

    return report_payload
