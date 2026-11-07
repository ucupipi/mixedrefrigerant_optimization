"""Automated Verification Suite for MCHE Differential Pressure, Cold Bundle Limits & Regimes.

Verifies:
1. Raw/legacy dataset read-only immutability.
2. Physical plausibility and range bounds for dP and temperature tags.
3. Operating regime partitioning logic (underload <= 226.8 t/h, baseload >= 279.8 t/h).
4. Feature engineering calculations and absence of NaN/Inf.
5. Sensor discontinuity quarantine for H5TI0020.
6. MCHE operational boundary checks (PDAH, PDAHH, TAL, TALL, MITA).
7. Extended surrogate model qualification on out-of-sample test splits (R² >= 0.60, MAE < 1.0 MW, NMAE < 1.0%).

Governance: AGENTS.md (Pasals 1-13), ORIGINAL_REQUEST.md (§R1, §R2, §R3).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List
import numpy as np
import pandas as pd
import pytest
import yaml

from src.config import Config, load_config
from src.data.ingestion import (
    build_clean_shift_datasets,
    build_real_plant_datasets,
    handle_h5ti0020_sensor_discontinuity,
    ingest_master_shift_data,
)
from src.features.engineering import (
    add_compressor_and_jt_physics_features,
    add_mche_dp_features,
    add_mche_regime_and_dp_features,
    add_mche_thermal_features,
    add_regime_indicators,
    chronological_train_test_split,
    verify_mche_operational_boundaries,
)
from src.models.pipeline import run_training_pipeline
from src.models.surrogates import (
    DEFAULT_SURROGATE_FEATURES,
    EXTENDED_MONOTONIC_CST,
    EXTENDED_SURROGATE_FEATURES,
    REAL_DATA_MONOTONIC_CST,
    REAL_DATA_SURROGATE_FEATURES,
    PhysicsResidualSurrogate,
    build_monotonic_surrogate,
    build_real_data_surrogate,
    check_monotonic_predictions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_raw_and_legacy_data_immutability():
    """Verify that raw datasets and legacy directories remain strictly read-only and uncorrupted."""
    manifest_path = PROJECT_ROOT / "data" / "manifests" / "sha256_manifest.json"
    assert manifest_path.exists(), "Cryptographic manifest must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    file_entries = manifest.get("files", [])
    if isinstance(file_entries, dict):
        file_entries = [
            {"file_name": k, **v} if isinstance(v, dict) else {"file_name": k, "sha256": v}
            for k, v in file_entries.items()
        ]

    assert len(file_entries) >= 6, "At least 6 canonical raw files must be registered in manifest"

    raw_dir = PROJECT_ROOT / "data" / "raw"
    checked_files = 0
    for entry in file_entries:
        fname = entry.get("file_name") or entry.get("file")
        expected_hash = entry.get("sha256")
        target_file = raw_dir / fname
        if target_file.exists():
            h = hashlib.sha256()
            with open(target_file, "rb") as rf:
                while chunk := rf.read(65536):
                    h.update(chunk)
            computed_hash = h.hexdigest()
            assert computed_hash == expected_hash, f"Hash mismatch for {fname}: raw file was modified!"
            checked_files += 1

    # Also verify that master_shift_level.parquet exists and is intact
    master_path = PROJECT_ROOT / "data" / "processed" / "master_shift_level.parquet"
    assert master_path.exists(), "master_shift_level.parquet must exist in processed/"


def test_config_mche_limits_integrity():
    """Verify default.yaml contains canonical regime thresholds and MCHE safety limits."""
    cfg_file = PROJECT_ROOT / "configs" / "default.yaml"
    assert cfg_file.exists(), "default.yaml must exist"

    with open(cfg_file, "r", encoding="utf-8") as f:
        raw_cfg = yaml.safe_load(f)

    # Regimes
    assert "regimes" in raw_cfg, "regimes section must be in default.yaml"
    assert raw_cfg["regimes"]["underload_threshold_t_h"] == 226.8
    assert raw_cfg["regimes"]["baseload_threshold_t_h"] == 279.8

    # MCHE dP limits
    assert "mche_dp_limits" in raw_cfg, "mche_dp_limits section must be in default.yaml"
    assert raw_cfg["mche_dp_limits"]["warm_bundle_alarm_kg_cm2"] == 0.42
    assert raw_cfg["mche_dp_limits"]["warm_bundle_trip_kg_cm2"] == 0.54
    assert raw_cfg["mche_dp_limits"]["cold_bundle_normal_max_kg_cm2"] == 0.17

    # Thermal limits
    assert "thermal_limits" in raw_cfg, "thermal_limits section must be in default.yaml"
    assert raw_cfg["thermal_limits"]["suction_temp_tal_c"] == -45.0
    assert raw_cfg["thermal_limits"]["suction_temp_tall_c"] == -51.0
    assert raw_cfg["thermal_limits"]["rundown_temp_min_c"] == -152.0


def test_regime_indicators_exact_partitioning():
    """Test exact threshold logic for regime indicators across the flow domain."""
    flows = np.array([
        50.0, 100.0, 180.0, 226.79, 226.8,   # Underload: <= 226.8
        226.81, 240.0, 260.0, 279.79,         # Transition: (226.8, 279.8)
        279.8, 280.0, 310.0, 350.0            # Baseload: >= 279.8
    ])
    test_df = pd.DataFrame({"H1FI012": flows})
    res_df = add_regime_indicators(test_df, flow_col="H1FI012", underload_threshold=226.8, baseload_threshold=279.8)

    assert "is_underload" in res_df.columns
    assert "is_baseload" in res_df.columns
    assert "is_transition" in res_df.columns

    u = res_df["is_underload"].to_numpy()
    b = res_df["is_baseload"].to_numpy()
    t = res_df["is_transition"].to_numpy()

    # Exact threshold partition checks
    np.testing.assert_array_equal(u[:5], [1, 1, 1, 1, 1], err_msg="Underload points must be 1")
    np.testing.assert_array_equal(u[5:], [0] * (len(flows) - 5), err_msg="Non-underload points must be 0")

    np.testing.assert_array_equal(b[9:], [1, 1, 1, 1], err_msg="Baseload points must be 1")
    np.testing.assert_array_equal(b[:9], [0] * 9, err_msg="Non-baseload points must be 0")

    np.testing.assert_array_equal(t[5:9], [1, 1, 1, 1], err_msg="Transition points must be 1")
    np.testing.assert_array_equal(t[:5], [0] * 5)
    np.testing.assert_array_equal(t[9:], [0] * 4)

    # Mutual exclusivity and complete partition
    np.testing.assert_array_equal(u + b + t, np.ones(len(flows)), err_msg="Partition must sum to 1 everywhere")
    np.testing.assert_array_equal(u * b, np.zeros(len(flows)), err_msg="Underload and baseload must be mutually exclusive")


def test_mche_feature_calculations_and_zero_nan():
    """Verify feature calculation formulas and absence of NaN / Inf."""
    features_df, _ = build_clean_shift_datasets(n_shifts=50, random_state=42)
    enriched = add_mche_regime_and_dp_features(features_df)

    expected_cols = [
        "is_underload",
        "is_baseload",
        "is_transition",
        "feat_mche_dp_ratio_warm_cold",
        "feat_mche_shell_dp_total",
        "feat_mche_norm_warm_dp",
        "feat_mche_vertical_thermal_lift",
        "feat_cold_bundle_depression_index",
    ]
    for col in expected_cols:
        assert col in enriched.columns, f"Column {col} missing from enriched DataFrame"
        vals = enriched[col].to_numpy()
        assert not np.any(np.isnan(vals)), f"Column {col} contains NaN values"
        assert not np.any(np.isinf(vals)), f"Column {col} contains Inf values"

    # Verify physical sanity
    assert np.all(enriched["feat_mche_dp_ratio_warm_cold"] > 0.5), "Warm/cold dP ratio must be positive"
    assert np.all(enriched["feat_mche_dp_ratio_warm_cold"] < 15.0), "Warm/cold dP ratio must be physically bounded"
    assert np.all(enriched["feat_mche_shell_dp_total"] > 0.05), "Total shell dP must be positive"
    assert np.all(enriched["feat_mche_vertical_thermal_lift"] > 80.0), "Vertical thermal lift must be > 80 C"
    assert np.all(enriched["feat_cold_bundle_depression_index"] > 10.0), "Cold bundle depression index must be > 10 C"


def test_h5ti0020_sensor_discontinuity_quarantine():
    """Test handling of the 2025 vs 2026 sensor discontinuity on H5TI0020."""
    df_test = pd.DataFrame({
        "pp_H5TI0020_mean": [-43.0, -42.5, -44.0, -135.0, -140.0, -138.5],
        "pp_H4TI004B_mean": [-40.0, -40.5, -41.0, -41.2, -41.5, -41.8],
    })
    cleaned = handle_h5ti0020_sensor_discontinuity(df_test, threshold_c=-100.0)

    assert "pp_H5TI0020_quarantined" in cleaned.columns
    assert "pp_H5TI0020_imputed" in cleaned.columns

    q = cleaned["pp_H5TI0020_quarantined"].to_numpy()
    np.testing.assert_array_equal(q, [False, False, False, True, True, True])

    imp = cleaned["pp_H5TI0020_imputed"].to_numpy()
    assert np.all(imp >= -50.0), "Imputed values must not contain cryogenic flare temperatures (< -100 C)"


def test_mche_operational_boundary_verification():
    """Test verification helper against Badak LNG operational thresholds."""
    # Normal point
    normal_obs = {
        "pp_H5PDI003_mean": 0.35,
        "pp_H5PDI004_mean": 0.10,
        "pp_H4TI004B_mean": -41.0,
        "pp_H5TI0029_mean": -149.0,
    }
    ok, violations = verify_mche_operational_boundaries(normal_obs)
    assert ok is True
    assert len(violations) == 0

    # High warm bundle dP alarm (PDAH 0.42 kg/cm2)
    alarm_obs = dict(normal_obs, pp_H5PDI003_mean=0.45)
    ok, violations = verify_mche_operational_boundaries(alarm_obs)
    assert ok is False
    assert any("PDAH" in v for v in violations)

    # Emergency warm bundle dP trip (5PDAHH-25 0.54 kg/cm2)
    trip_obs = dict(normal_obs, pp_H5PDI003_mean=0.55)
    ok, violations = verify_mche_operational_boundaries(trip_obs)
    assert ok is False
    assert any("5PDAHH-25" in v for v in violations)

    # Suction TAL violation (-45.0 C)
    tal_obs = dict(normal_obs, pp_H4TI004B_mean=-46.5)
    ok, violations = verify_mche_operational_boundaries(tal_obs)
    assert ok is False
    assert any("TAL" in v for v in violations)

    # Suction TALL trip (-51.0 C)
    tall_obs = dict(normal_obs, pp_H4TI004B_mean=-52.0)
    ok, violations = verify_mche_operational_boundaries(tall_obs)
    assert ok is False
    assert any("TALL" in v for v in violations)


def test_master_shift_data_ingestion():
    """Test ingestion of real master_shift_level.parquet without modifying raw data."""
    master_path = PROJECT_ROOT / "data" / "processed" / "master_shift_level.parquet"
    if not master_path.exists():
        pytest.skip("master_shift_level.parquet not found")

    features_df, targets_df = ingest_master_shift_data(master_path, min_operating_flow_t_h=10.0)

    assert len(features_df) > 500, "Should ingest at least 500 active shifts"
    assert "H1FI012" in features_df.columns
    assert "H4FI001" in features_df.columns
    assert "pp_H5PDI003_mean" in features_df.columns
    assert "pp_H5PDI004_mean" in features_df.columns
    assert "pp_H5TI0025_mean" in features_df.columns
    assert "pp_H5TI0029_mean" in features_df.columns
    assert "pp_H4TI004B_mean" in features_df.columns
    assert "shift_id" in targets_df.columns
    assert "total_shaft_power_mw" in targets_df.columns


def test_extended_surrogate_model_qualification():
    """Verify surrogate training with extended features, monotonic constraints, and MW metrics."""
    proc_dir = PROJECT_ROOT / "data" / "processed"
    models_dir = PROJECT_ROOT / "models"
    reports_dir = PROJECT_ROOT / "reports"

    report = run_training_pipeline(
        processed_dir=proc_dir,
        models_dir=models_dir,
        reports_dir=reports_dir,
        use_extended_features=True,
        random_state=42,
    )

    metrics = report["surrogate_test_metrics"]
    assert metrics["r2"] >= 0.60, f"Surrogate R² {metrics['r2']} < 0.60"
    assert metrics["mae_mw"] < 1.0, f"Surrogate MAE {metrics['mae_mw']} MW >= 1.0 MW"
    assert metrics["nmae_pct"] < 1.0, f"Surrogate NMAE {metrics['nmae_pct']}% >= 1.0%"
    assert report["unit"] == "MW", "Engineering unit must be proportional MW"

    # Verify regime-stratified metrics are present
    assert "regime_stratified_metrics" in report, "Must include regime_stratified_metrics"
    assert len(report["regime_stratified_metrics"]) > 0, "At least one regime must have stratified metrics"

    # Verify physical monotonicity
    trained_model = build_monotonic_surrogate(
        monotonic_cst=EXTENDED_MONOTONIC_CST,
        max_iter=100,
        random_state=42,
    )
    # Fit on synthetic data to test monotonicity
    features_df, targets_df = build_clean_shift_datasets(n_shifts=120, random_state=42)
    enriched = add_mche_regime_and_dp_features(features_df)
    X = enriched[list(EXTENDED_SURROGATE_FEATURES)].to_numpy(dtype=float)
    y = targets_df["total_shaft_power_mw"].to_numpy(dtype=float)
    trained_model.fit(X, y)

    base_pt = X[0].copy()
    # Feature 0: Feed flow rate -> monotonic non-decreasing
    assert check_monotonic_predictions(trained_model, base_pt, feature_index=0, scan_min=320.0, scan_max=850.0)
    # Feature 2: MCR flow rate -> monotonic non-decreasing
    assert check_monotonic_predictions(trained_model, base_pt, feature_index=2, scan_min=480.0, scan_max=820.0)


def test_empirical_regime_envelopes_and_advisory_crew_dp_bounds():
    """Verify data-driven regime envelopes, CrewAI underload vs baseload policies, and HYSYS dP deck."""
    from src.agents.crew import C3MRAdvisoryCrew
    from src.features.engineering import classify_operating_regime, fit_empirical_regime_envelopes
    from src.thermo.hysys_parity import build_hysys_stream_deck

    assert classify_operating_regime(195.0) == "underload"
    assert classify_operating_regime(254.0) == "transition"
    assert classify_operating_regime(295.0) == "baseload"

    env = fit_empirical_regime_envelopes()
    assert "hydraulic_power_law" in env
    assert 1.30 < env["hydraulic_power_law"]["warm_bundle_beta"] < 1.70
    assert 1.40 < env["hydraulic_power_law"]["cold_bundle_beta"] < 1.80
    assert env["regimes"]["underload"]["q1_n2_cap_frac"] < env["regimes"]["underload"]["q4_worst_comp_frac"][0]

    crew = C3MRAdvisoryCrew()
    rep_under = crew.kickoff(feed_flow_t_h=200.0, ambient_temp_c=29.0)
    assert rep_under["safety_verification"]["operating_regime"] == "underload"
    assert rep_under["safety_verification"]["mche_hydraulic_verification"]["chinese_hat_distributor_safe"] is True
    assert rep_under["safety_verification"]["cold_bundle_thermal_verification"]["n2_cold_bundle_overcooling_prevented"] is True
    assert "Underload regime" in rep_under["optimization_recommendation"]["regime_optimization_strategy"]

    rep_base = crew.kickoff(feed_flow_t_h=300.0, ambient_temp_c=29.5)
    assert rep_base["safety_verification"]["operating_regime"] == "baseload"
    assert rep_base["safety_verification"]["mche_hydraulic_verification"]["chinese_hat_distributor_safe"] is True
    assert "Baseload regime" in rep_base["optimization_recommendation"]["regime_optimization_strategy"]

    deck = build_hysys_stream_deck()
    assert len(deck) == 18
    for row in deck:
        assert "mche_dp_warm_kgcm2" in row
        assert 0.05 < row["mche_dp_warm_kgcm2"] < 0.42
        assert "mche_dp_ratio_warm_cold" in row


def test_corrected_compressor_and_jt_physics_features():
    """Verify corrected 4K-2/4K-3 tag mapping, native KGC2A ratios, JT cooling, MW_MCR, and BOOK-4/5 boundaries."""
    df_sample = pd.DataFrame(
        {
            "H4PI014B": [3.235],
            "H4PI015A": [13.697],
            "H4PI016B": [13.417],
            "H4PI017B": [43.881],
            "H4PIC002": [1.045],
            "H4PI006B": [14.164],
            "H4TI004B": [-38.75],
            "H4TI007B": [57.43],
            "H4TI006B": [33.12],
            "H4TI008B": [125.08],
            "H5TI0031": [-122.49],
            "H5TI0032": [-127.85],
            "H5TI0030": [-150.39],
            "H5TI0029": [-152.84],
            "H4FI001A": [212.5],
            "H4FI002B": [66.2],
            "H4FI003B": [50.8],
            "comp_N2": [3.38],
            "comp_C1": [44.37],
            "comp_C2": [44.94],
            "comp_C2H4": [0.85],
            "comp_C3": [6.28],
            "comp_iC4": [0.12],
            "comp_nC4": [0.06],
        }
    )

    out = add_compressor_and_jt_physics_features(df_sample)

    # 1. Native KGC2A pressure ratios without double +1.03323 offset and with corrected H4PI015A (4K-2 DISCH) / H4PI016B (4K-3 SUCT)
    assert np.isclose(out["rp_LP_MCR"].iloc[0], 13.697 / 3.235, rtol=1e-5)
    assert np.isclose(out["rp_HP_MCR"].iloc[0], 43.881 / 13.417, rtol=1e-5)
    assert np.isclose(out["rp_MCR_total"].iloc[0], 43.881 / 3.235, rtol=1e-5)
    assert np.isclose(out["dp_interstage_4E5"].iloc[0], 13.697 - 13.417, atol=1e-5)
    assert np.isclose(out["rp_C3_total"].iloc[0], 14.164 / 1.045, rtol=1e-5)

    # 2. Corrected 4K-2 DISCH (H4TI007B) and 4K-3 SUCT (H4TI006B) temperature deltas
    assert np.isclose(out["comp_dT_discharge_4K2"].iloc[0], 57.43 - (-38.75), atol=1e-5)
    assert np.isclose(out["comp_dT_discharge_4K3"].iloc[0], 125.08 - 33.12, atol=1e-5)
    assert np.isclose(out["dT_intercooler_4E5"].iloc[0], 57.43 - 33.12, atol=1e-5)

    # 3. JT expansion cooling across 5FV-2 and 5PV-15
    assert np.isclose(out["MCR_dT_JT_5FV2"].iloc[0], -122.49 - (-127.85), atol=1e-5)
    assert np.isclose(out["MCR_dT_JT_PV15"].iloc[0], -150.39 - (-152.84), atol=1e-5)

    # 4. Apparent molecular weight MW_MCR [g/mol] and BOOK-4 4K-1 anti-surge margins
    assert 24.0 < float(out["MW_MCR"].iloc[0]) < 25.5
    assert np.isclose(out["c3_antisurge_margin_stg1"].iloc[0], 212.5 - 155.0, atol=1e-5)
    assert np.isclose(out["c3_antisurge_margin_stg2"].iloc[0], 66.2 - 55.0, atol=1e-5)
    assert np.isclose(out["c3_antisurge_margin_stg3"].iloc[0], 50.8 - 38.0, atol=1e-5)

    # 5. Optional BOOK-4 / BOOK-5 boundary checks
    ok_book, viol_book = verify_mche_operational_boundaries(
        {
            "pp_H5PDI003_mean": 0.30,
            "pp_H5PDI004_mean": 0.09,
            "pp_H4TI004B_mean": -40.0,
            "pp_H5TI0029_mean": -149.0,
            "H4PIC002": 1.010,   # Violates >= 1.033 kg/cm2A vacuum limit (BOOK-4 p. 149)
            "H4TI0296": 41.2,    # Violates <= 39.0 C desuperheater limit (BOOK-4 p. 72)
            "H4PI017B": 55.5,    # Violates <= 54.0 kg/cm2A Train E-H PAH (BOOK-5 p. 80)
            "H4TI007B": 162.0,   # Violates < 160.0 C 4K-2 TAH (BOOK-5 p. 103)
        }
    )
    assert ok_book is False
    assert len(viol_book) == 4


def test_real_data_surrogate_qualification():
    """Verify that training on real plant data (1,475 shifts) satisfies AGENTS.md Pasal 2 & 13 qualification gates."""
    proc_dir = PROJECT_ROOT / "data" / "processed"
    models_dir = PROJECT_ROOT / "models"
    reports_dir = PROJECT_ROOT / "reports"

    report = run_training_pipeline(
        processed_dir=proc_dir,
        models_dir=models_dir,
        reports_dir=reports_dir,
        data_source="real",
        random_state=42,
    )

    metrics = report["surrogate_test_metrics"]
    assert metrics["r2"] >= 0.60, f"Real data surrogate R² {metrics['r2']} < 0.60"
    assert metrics["mae_mw"] < 1.0, f"Real data surrogate MAE {metrics['mae_mw']} MW >= 1.0 MW"
    assert metrics["nmae_pct"] < 1.0, f"Real data surrogate NMAE {metrics['nmae_pct']}% >= 1.0%"
    assert report["unit"] == "MW", "Engineering unit must be proportional MW"
    assert report["qualified"] is True, "Real data surrogate must pass qualification gate"


def test_regime_stratified_real_data():
    """Verify real data surrogate performance across operating regimes (underload, baseload, transition)."""
    reports_file = PROJECT_ROOT / "reports" / "evaluation_report.json"
    assert reports_file.exists(), "evaluation_report.json must exist"

    with open(reports_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    regimes = report.get("regime_stratified_metrics", {})
    assert "underload" in regimes, "Must contain underload regime metrics"
    assert "baseload" in regimes, "Must contain baseload regime metrics"

    # Baseload regime should have strong accuracy (R² >= 0.60, MAE < 1.0 MW)
    base_m = regimes["baseload"]["metrics"]
    assert base_m["mae_mw"] < 1.0, f"Baseload MAE {base_m['mae_mw']} MW >= 1.0 MW"
    assert base_m["r2"] >= 0.60, f"Baseload R² {base_m['r2']} < 0.60"

    # Underload regime is turndown, MAE must still be physically bounded < 1.5 MW
    under_m = regimes["underload"]["metrics"]
    assert under_m["mae_mw"] < 1.5, f"Underload MAE {under_m['mae_mw']} MW >= 1.5 MW"



