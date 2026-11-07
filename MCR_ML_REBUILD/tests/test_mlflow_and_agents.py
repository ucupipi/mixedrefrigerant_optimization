"""Unit and Integration Tests for MLflow Tracking, Bootstrap CI, A-Evolve, and 3-Agent Crew."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from src.agents.crew import C3MRAdvisoryCrew
from src.agents.evolver import SurrogateEvolver
from src.cli.commands import main
from src.data.ingestion import build_clean_shift_datasets
from src.evaluation.metrics import compute_bootstrap_ci_mw, evaluate_blocked_timeseries_cv
from src.features.engineering import chronological_train_test_split
from src.models.mlflow_tracker import MLflowExperimentTracker
from src.models.surrogates import DEFAULT_SURROGATE_FEATURES, build_monotonic_surrogate


def test_paired_bootstrap_ci_and_blocked_cv() -> None:
    """Verify paired bootstrap 95% CI in MW and blocked time-series CV."""
    features_df, targets_df = build_clean_shift_datasets(n_shifts=120, random_state=42)
    X = features_df.loc[:, list(DEFAULT_SURROGATE_FEATURES)].to_numpy(dtype=float)
    y = targets_df["total_shaft_power_mw"].to_numpy(dtype=float)

    cv_res = evaluate_blocked_timeseries_cv(
        X,
        y,
        model_builder=lambda: build_monotonic_surrogate(random_state=42),
        n_splits=3,
        purge_buffer=2,
    )
    assert cv_res["n_splits"] == 3
    assert cv_res["mean_mae_mw"] < 1.0
    assert cv_res["mean_r2"] >= 0.60

    model = build_monotonic_surrogate(random_state=42)
    model.fit(X[:90], y[:90])
    preds = model.predict(X[92:])
    ci = compute_bootstrap_ci_mw(y[92:], preds, n_boot=300, ci=0.95, random_state=42)
    assert 0.0 <= ci["mae_ci_lower_mw"] <= ci["mae_ci_upper_mw"] < 1.0
    assert 0.0 <= ci["nmae_ci_lower_pct"] <= ci["nmae_ci_upper_pct"] < 1.0


def test_mlflow_experiment_tracker(tmp_path: Path) -> None:
    """Verify MLflowExperimentTracker creates run summary and registers Production stage."""
    tracker = MLflowExperimentTracker(tracking_dir=tmp_path / "mlruns", experiment_name="test_exp")
    dummy_model_path = tmp_path / "model.joblib"
    dummy_model_path.write_bytes(b"serialized-surrogate-bytes")

    run_info = tracker.log_training_run(
        run_name="unit_test_run",
        params={"learning_rate": 0.05, "max_iter": 200},
        metrics={"mae_mw": 0.25, "rmse_mw": 0.31, "nmae_pct": 0.29, "r2": 0.995},
        bootstrap_ci={
            "mae_ci_lower_mw": 0.20,
            "mae_ci_upper_mw": 0.30,
            "rmse_ci_lower_mw": 0.25,
            "rmse_ci_upper_mw": 0.36,
            "nmae_ci_lower_pct": 0.23,
            "nmae_ci_upper_pct": 0.35,
        },
        blocked_cv={
            "n_splits": 3,
            "mean_mae_mw": 0.28,
            "mean_rmse_mw": 0.34,
            "mean_nmae_pct": 0.33,
            "mean_r2": 0.992,
        },
        model_artifact_path=dummy_model_path,
        tags={"suite": "pytest"},
    )
    assert run_info["model_registry"]["stage"] == "Production"
    assert len(run_info["model_registry"]["sha256"]) == 64
    summary_file = tmp_path / "mlruns" / "test_exp" / run_info["run_id"] / "run_summary.json"
    assert summary_file.exists()


def test_surrogate_evolver_gates_and_rollback(tmp_path: Path) -> None:
    """Verify A-Evolve Solve -> Observe -> Evolve -> Gate -> Reload loop and automatic rollback."""
    features_df, targets_df = build_clean_shift_datasets(n_shifts=240, random_state=42)
    merged = features_df.merge(targets_df[["shift_id", "total_shaft_power_mw"]], on="shift_id")
    train_df, test_df = chronological_train_test_split(merged, test_ratio=0.20, purge_buffer=2, timestamp_col="shift_id")

    X_train = train_df.loc[:, list(DEFAULT_SURROGATE_FEATURES)].to_numpy(dtype=float)
    y_train = train_df["total_shaft_power_mw"].to_numpy(dtype=float)
    X_test = test_df.loc[:, list(DEFAULT_SURROGATE_FEATURES)].to_numpy(dtype=float)
    y_test = test_df["total_shaft_power_mw"].to_numpy(dtype=float)

    evolver = SurrogateEvolver(X_train, y_train, X_test, y_test, random_state=42)
    out_json = tmp_path / "evolution_history.json"
    res = evolver.run_evolution(generations=5, feed_flow_t_h=550.0, ambient_temp_c=29.5, output_report_path=out_json)

    assert out_json.exists()
    assert res["gates_verified"] is True
    assert res["rollback_tested"] is True
    assert res["rollbacks_triggered"] >= 1
    best = res["best_candidate"]
    assert best["mita_c"] >= 1.50
    assert best["suction_temp_c"] >= -45.0
    assert best["mcr_flow_t_h"] >= 480.0
    assert best["mahalanobis_d"] <= 3.080216
    assert abs(sum(best["comp_mol_frac"]) - 1.0) < 1e-9


def test_c3mr_advisory_crew_pasal_9_and_10(tmp_path: Path) -> None:
    """Verify 3-agent sequential crew enforces Pasal 9 boundary roles and Pasal 10 MW decomposition."""
    crew = C3MRAdvisoryCrew()
    out_file = tmp_path / "crew_advisory_report.json"
    report = crew.kickoff(feed_flow_t_h=550.0, ambient_temp_c=29.5, output_report_path=out_file)

    assert out_file.exists()
    assert report["governance_audit"]["leakage_firewall_passed"] is True
    safety = report["safety_verification"]
    assert safety["all_interlocks_passed"] is True
    assert safety["boundary_enablers"]["4UV-53_role"] == "safety_boundary_constraint_only"
    assert safety["boundary_enablers"]["4TV-510_role"] == "safety_boundary_constraint_only"

    opt = report["optimization_recommendation"]
    p = opt["power_decomposition_mw"]
    assert p["unit"] == "MW"
    assert abs(p["delta_total_c3mr_mw"] - (p["delta_mcr_direct_mw"] + p["delta_c3_precooling_mw"])) < 1e-6
    assert abs(opt["primary_decision_variables"]["comp_sum_mol_pct"] - 100.0) < 1e-4


def test_cli_phase2_subcommands() -> None:
    """Verify CLI subcommands mlflow-run, evolve, crew, and verify return exit code 0."""
    assert main(["mlflow-run"]) == 0
    assert main(["evolve", "--generations", "3"]) == 0
    assert main(["crew", "--feed-flow", "550.0", "--ambient-temp", "29.5"]) == 0
    assert main(["verify", "--gate", "all"]) == 0

