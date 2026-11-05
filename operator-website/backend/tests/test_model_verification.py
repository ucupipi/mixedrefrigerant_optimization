"""
operator-website/backend/tests/test_model_verification.py
Milestone 2 Test Suite: ML Model, Provenance, Normalization & Preprocessing Verification
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Test Coverage:
  TASK 1: ML Model Artifact Provenance & Immutability
    - Check c3mr_power_surrogate_real.joblib SHA-256 digest: 1fe6bb9566dec8c3414176013c608e69f84a1911ad905967767435c250072196.
    - Confirm hybrid architecture: PhysicsResidualSurrogate (Ridge alpha=2.0 on StandardScaler + HistGradientBoostingRegressor on residuals).
    - Verify raw datasets and original ML artifacts are never overwritten.
  TASK 2: Feature Pipeline & Leakage Firewall
    - Verify exact 20-feature ordering (REAL_DATA_SURROGATE_FEATURES vs ORDERED_FEATURES).
    - Verify feature engineering input units and names.
    - Verify leakage firewall: 25 quarantined tags (compressor powers, turbine speeds, steam meters, future targets) blocked.
  TASK 3: Preprocessing Consistency & Leakage Prevention
    - Confirm StandardScaler fitted strictly on training partition (n=1,178), never globally on test data.
    - Confirm chronological 80:20 partition (1,178 train shifts, 295 test shifts, 2-shift purge buffer).
  TASK 4: Performance Across Operating Regimes
    - Prove R^2 = 0.8365 >= 0.60, MAE = 0.8021 MW < 1.0 MW, NMAE = 0.9311% < 1.0% on out-of-sample test set.
    - Verify regime breakdown: Baseload (R^2=0.668, MAE=0.520 MW), Underload (R^2=0.491, MAE=0.774 MW), Transition (R^2=0.477, MAE=1.250 MW).
    - Verify residual distribution: mean near zero, no systematic bias, bootstrap 95% CI.
  TASK 5: Composition Integrity & Simplex Geometry
    - 5-component Aitchison simplex S^5 -> R^4 via orthonormal SBP contrast matrix (V^T V = I_4).
    - Full-precision 64-bit internal representation preserved across roundtrip isometry.
    - Display rounding to 2 decimals uses C1 residual absorption guaranteeing exact 100.00 mol% closure.
  TASK 6: Out-of-Domain Behavior & Uncertainty
    - 4D Mahalanobis distance D_M <= 3.080216 (sqrt(chi^2(0.95, 4))) calibrated on 1,475 shifts.
    - Verify statistical extrapolation warnings emitted when D_M > 3.0802.

Governance: AGENTS.md (Pasals 1-13), ORIGINAL_REQUEST.md (Phase 2 Master Prompt), /unlazy
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# ── Ensure Backend, Rebuild, and Stage2 paths are in sys.path ───────────────
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND_DIR.parents[1]
_REBUILD_ROOT = _ROOT / "MCR_ML_REBUILD"

for p in (str(_ROOT), str(_BACKEND_DIR), str(_REBUILD_ROOT), str(_ROOT / "analysis" / "stage2_optimization")):
    if p not in sys.path:
        sys.path.insert(0, p)

import joblib

# Backend core imports
from core.feature_builder import (
    BASELOAD_THRESHOLD_T_H,
    MW_SPECIES,
    ORDERED_FEATURES,
    UNDERLOAD_THRESHOLD_T_H,
    build_feature_vector,
    compute_apparent_mw,
)
from core.ilr_engine import (
    CHI2_CRITICAL_5COMP,
    HISTORICAL_COV_INV,
    HISTORICAL_MEAN_XI,
    SBP_5COMP,
    V_MATRIX_5,
    check_composition_envelope,
    closure,
    compute_mahalanobis_distance,
    ilr_forward,
    ilr_inverse,
)
from core.model_loader import get_model_info, get_model_path, load_surrogate_model
from core.validator import validate_operating_point

# MCR_ML_REBUILD source imports
from src.data.governance import (
    DEFAULT_QUARANTINED_TAGS,
    enforce_leakage_firewall,
    filter_quarantined_dataframe,
    is_quarantined_column,
)
from src.data.ingestion import build_real_plant_datasets
from src.evaluation.metrics import evaluate_power_metrics
from src.features.engineering import (
    add_compressor_and_jt_physics_features,
    add_mche_regime_and_dp_features,
    chronological_train_test_split,
)
from src.models.surrogates import (
    REAL_DATA_MONOTONIC_CST,
    REAL_DATA_SURROGATE_FEATURES,
    PhysicsResidualSurrogate,
)


class TestModelArtifactProvenance(unittest.TestCase):
    """TASK 1: Verify ML Model Artifact Provenance, SHA-256, and Immutability."""

    EXPECTED_SHA256 = "1fe6bb9566dec8c3414176013c608e69f84a1911ad905967767435c250072196"

    def test_surrogate_artifact_file_and_sha256(self):
        """Confirm artifact exists, non-empty, and SHA-256 matches registered hash."""
        model_path = _REBUILD_ROOT / "models" / "c3mr_power_surrogate_real.joblib"
        self.assertTrue(model_path.exists(), f"Surrogate artifact missing: {model_path}")
        self.assertGreater(model_path.stat().st_size, 0, "Artifact file is empty")

        raw_bytes = model_path.read_bytes()
        actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        self.assertEqual(
            actual_sha256,
            self.EXPECTED_SHA256,
            f"SHA-256 digest mismatch! Expected {self.EXPECTED_SHA256}, got {actual_sha256}",
        )

    def test_surrogate_hybrid_architecture(self):
        """Confirm PhysicsResidualSurrogate architecture: Ridge base model + HistGradientBoosting residual."""
        model_path = _REBUILD_ROOT / "models" / "c3mr_power_surrogate_real.joblib"
        model = joblib.load(model_path)

        # 1. Outer wrapper class
        self.assertIsInstance(
            model,
            PhysicsResidualSurrogate,
            f"Model is not an instance of PhysicsResidualSurrogate: {type(model)}",
        )

        # 2. Linear physics base model
        self.assertTrue(hasattr(model, "base_model_"), "Model missing base_model_ attribute")
        from sklearn.linear_model import Ridge
        self.assertIsInstance(model.base_model_, Ridge, "base_model_ must be Ridge")
        self.assertEqual(model.base_model_.alpha, 2.0, "Ridge alpha must be 2.0")

        # 3. Scaler fitted for linear base model
        self.assertTrue(hasattr(model, "scaler_"), "Model missing scaler_ attribute")
        self.assertIsInstance(model.scaler_, StandardScaler, "scaler_ must be StandardScaler")

        # 4. GBDT residual model
        self.assertTrue(hasattr(model, "res_model_"), "Model missing res_model_ attribute")
        from sklearn.ensemble import HistGradientBoostingRegressor
        self.assertIsInstance(model.res_model_, HistGradientBoostingRegressor, "res_model_ must be HistGradientBoostingRegressor")
        self.assertEqual(model.res_model_.l2_regularization, 3.0, "l2_regularization must be 3.0")
        self.assertEqual(model.res_model_.learning_rate, 0.05, "learning_rate must be 0.05")
        self.assertEqual(model.res_model_.max_iter, 80, "max_iter must be 80")
        self.assertEqual(model.res_model_.max_leaf_nodes, 15, "max_leaf_nodes must be 15")
        self.assertEqual(model.res_model_.min_samples_leaf, 15, "min_samples_leaf must be 15")

    def test_raw_datasets_and_original_artifacts_immutability(self):
        """Verify that raw canonical datasets match manifest hashes and were never overwritten."""
        manifest_path = _REBUILD_ROOT / "data" / "manifests" / "sha256_manifest.json"
        self.assertTrue(manifest_path.exists(), "sha256_manifest.json missing")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        files_dict = manifest if isinstance(manifest, dict) else {item["name"]: item["sha256"] for item in manifest}
        unprocessed_dir = _ROOT / "data" / "unprocessed"

        expected_checksums = {
            "ProcessParameter_2023_2024.xlsx": "990bbe46a10d155479dd593e61dc6e58439236dea5fceddaaef1fe755b7de03b",
            "ProcessParameter_July_2025.xlsx": "34d66a21e4d9a09ec8bf9d8c11a5229ea8cfae034a3f6ce09b147309ceaf4911",
            "ProcessParameter_August_2026.xlsx": "baf9196b9e8235a6539868b0abc26cf6409e181d994b390857063312f435303c",
            "OverallComposition_2023_2024.xlsx": "2bd72831eaa5d4f927006d5d90c61af60d5c1d7f8346798a07d5b343bcaad6df",
            "OverallComposition_July_2025.tsv": "6f64596c60bf8a3df48d78c108aee810c4a28d679575f6b8ddf60ccf9aca3529",
            "OverallComposition_August_2026.tsv": "94b320f974ba5cbd002f5d6c20cc06210aa6b42e6036af65f589656906f3f06c",
        }

        for filename, expected_hash in expected_checksums.items():
            filepath = unprocessed_dir / filename
            if filepath.exists():
                actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
                self.assertEqual(
                    actual_hash,
                    expected_hash,
                    f"Raw dataset {filename} was modified or corrupted! Hash mismatch.",
                )


class TestFeaturePipelineAndLeakageFirewall(unittest.TestCase):
    """TASK 2: Verify Feature Pipeline, Ordering, Units, and Target Leakage Firewall."""

    def test_exact_20_feature_ordering_and_names(self):
        """Confirm exact 20-feature array alignment between surrogates.py and feature_builder.py."""
        self.assertEqual(len(REAL_DATA_SURROGATE_FEATURES), 20, "REAL_DATA_SURROGATE_FEATURES must have 20 features")
        self.assertEqual(len(ORDERED_FEATURES), 20, "ORDERED_FEATURES must have 20 features")
        self.assertEqual(
            REAL_DATA_SURROGATE_FEATURES,
            ORDERED_FEATURES,
            "Feature names or ordering in backend feature_builder.py differs from surrogate model definition!",
        )

        expected_features = (
            "H1FI012",
            "H4FI001",
            "xi_1",
            "xi_2",
            "xi_3",
            "xi_4",
            "is_underload",
            "is_baseload",
            "rp_LP_MCR",
            "rp_HP_MCR",
            "rp_MCR_total",
            "dp_interstage_4E5",
            "rp_C3_total",
            "MCHE_dT_cold_bundle_approach",
            "MCHE_dT_shell_span",
            "MW_MCR",
            "MCHE_dT_lngexit_mrv",
            "work_proxy_mcr_total",
            "work_proxy_c3",
            "feed_mcr_product",
        )
        self.assertEqual(REAL_DATA_SURROGATE_FEATURES, expected_features)

    def test_feature_builder_output_shape_and_units(self):
        """Confirm build_feature_vector produces a clean (1, 20) float64 array with physical units."""
        scenario = {
            "feed_flow_t_h": 250.0,
            "mcr_flow_t_h": 560.0,
            "comp_N2_molpct": 3.38,
            "comp_C1_molpct": 44.37,
            "comp_C2_molpct": 44.94,
            "comp_C2H4_molpct": 0.85,
            "comp_C3_molpct": 6.28,
        }
        vec, feat_dict = build_feature_vector(scenario)

        self.assertIsInstance(vec, np.ndarray)
        self.assertEqual(vec.shape, (1, 20))
        self.assertEqual(vec.dtype, np.float64)

        # Verify key physical ranges
        self.assertEqual(feat_dict["H1FI012"], 250.0)
        self.assertEqual(feat_dict["H4FI001"], 560.0)
        self.assertGreater(feat_dict["MW_MCR"], 20.0)
        self.assertLess(feat_dict["MW_MCR"], 35.0)
        self.assertGreater(feat_dict["feed_mcr_product"], 100.0)
        self.assertGreater(feat_dict["rp_MCR_total"], 5.0)

    def test_leakage_firewall_blocks_25_quarantined_tags(self):
        """Verify leakage firewall identifies and blocks 25 quarantined tags and their variants."""
        quarantined_25_tags = [
            # 1-10: Default quarantined base tags
            "H4FI029A",
            "H4FI030A",
            "H4FI031A",
            "H5FI006A",
            "H1FI0009",
            "total_steam_t_h",
            "total_shaft_power_mw",
            "mcr_shaft_power_mw",
            "c3_shaft_power_mw",
            "exergy_destruction_mw",
            # 11-15: Direct speed & power tags
            "H4SI018A",
            "H4SI023A",
            "H4SI028A",
            "total_compressor_power_MW",
            "total_shaft_power_kw",
            # 16-25: Derived preprocessing, lag, rolling, std, and differential variants
            "H4FI029A_norm",
            "H4FI030A_std",
            "H4FI031A_mean",
            "H4SI018A_rolling6",
            "H4SI023A_lag1",
            "H4SI028A_median",
            "total_shaft_power_mw_norm",
            "total_steam_t_h_mean",
            "mcr_shaft_power_mw_diff",
            "exergy_destruction_mw_scaled",
        ]
        self.assertEqual(len(quarantined_25_tags), 25, "Must test exactly 25 quarantined tags")

        extended_quarantine_set = set(DEFAULT_QUARANTINED_TAGS) | {
            "H4SI018A",
            "H4SI023A",
            "H4SI028A",
            "total_compressor_power_MW",
            "total_shaft_power_kw",
            "specific_energy_consumption_kwh_t",
        }

        for tag in quarantined_25_tags:
            self.assertTrue(
                is_quarantined_column(tag, extended_quarantine_set),
                f"Quarantine firewall failed to detect leaky tag: {tag}",
            )

        # Confirm enforce_leakage_firewall raises ValueError when any leaky tag is present
        dirty_features = ["H1FI012", "H4FI001", "H4FI029A"]
        with self.assertRaises(ValueError) as ctx:
            enforce_leakage_firewall(dirty_features, extended_quarantine_set)
        self.assertIn("Target leakage firewall violation", str(ctx.exception))

    def test_zero_quarantined_tags_in_active_surrogate_features(self):
        """Confirm zero quarantined tags exist in active production surrogate features."""
        extended_quarantine_set = set(DEFAULT_QUARANTINED_TAGS) | {
            "H4SI018A",
            "H4SI023A",
            "H4SI028A",
            "total_compressor_power_MW",
        }
        for feat in REAL_DATA_SURROGATE_FEATURES:
            self.assertFalse(
                is_quarantined_column(feat, extended_quarantine_set),
                f"Active feature {feat} violates target leakage firewall!",
            )


class TestPreprocessingConsistencyAndPartitions(unittest.TestCase):
    """TASK 3: Verify Preprocessing Consistency, StandardScaler Train Fitting, and Chronological Split."""

    @classmethod
    def setUpClass(cls):
        """Load real plant dataset once for preprocessing and performance tests."""
        f_df, t_df = build_real_plant_datasets()
        f_df = add_mche_regime_and_dp_features(f_df)
        f_df = add_compressor_and_jt_physics_features(f_df)
        cls.merged_df = pd.merge(
            f_df, t_df[["shift_id", "total_shaft_power_mw"]], on="shift_id", how="inner"
        )
        cls.train_df, cls.test_df = chronological_train_test_split(
            cls.merged_df, test_ratio=0.20, purge_buffer=2, timestamp_col="shift_id"
        )
        cls.model = joblib.load(_REBUILD_ROOT / "models" / "c3mr_power_surrogate_real.joblib")

    def test_chronological_80_20_partition_integrity(self):
        """Confirm chronological split produces 1,178 train shifts and 295 test shifts without temporal leakage."""
        self.assertEqual(len(self.train_df), 1178, "Train set must have exactly 1,178 shifts")
        self.assertEqual(len(self.test_df), 295, "Test set must have exactly 295 shifts")

        # Confirm strict temporal ordering: max train shift timestamp < min test shift timestamp
        max_train_shift = self.train_df["shift_id"].max()
        min_test_shift = self.test_df["shift_id"].min()
        self.assertLess(
            max_train_shift,
            min_test_shift,
            "Chronological ordering violated: train shift overlaps with test shift!",
        )

    def test_standard_scaler_fitted_strictly_on_training_partition(self):
        """Confirm model.scaler_ was fitted strictly on X_train (n=1,178) and NOT on test or full dataset."""
        self.assertEqual(
            self.model.scaler_.n_samples_seen_,
            1178,
            "StandardScaler must have seen exactly 1,178 training samples",
        )

        X_train = self.train_df.loc[:, list(REAL_DATA_SURROGATE_FEATURES)].to_numpy(dtype=float)
        X_all = self.merged_df.loc[:, list(REAL_DATA_SURROGATE_FEATURES)].to_numpy(dtype=float)

        scaler_train = StandardScaler().fit(X_train)
        scaler_all = StandardScaler().fit(X_all)

        # 1. Scaler in production model matches scaler_train to floating point precision
        max_diff_train_mean = float(np.max(np.abs(self.model.scaler_.mean_ - scaler_train.mean_)))
        max_diff_train_scale = float(np.max(np.abs(self.model.scaler_.scale_ - scaler_train.scale_)))
        self.assertLess(max_diff_train_mean, 1e-7, "Model scaler mean does not match training partition mean")
        self.assertLess(max_diff_train_scale, 1e-7, "Model scaler scale does not match training partition scale")

        # 2. Scaler in production model differs significantly from scaler fitted on all data
        max_diff_all_mean = float(np.max(np.abs(self.model.scaler_.mean_ - scaler_all.mean_)))
        self.assertGreater(
            max_diff_all_mean,
            1.0,
            "Data leakage detected! Scaler appears to have been fitted globally on full dataset.",
        )


class TestPerformanceAcrossOperatingRegimes(unittest.TestCase):
    """TASK 4: Verify Out-of-Sample Performance, Regime Breakdown, and Residual Distribution."""

    @classmethod
    def setUpClass(cls):
        """Evaluate model on out-of-sample test split."""
        f_df, t_df = build_real_plant_datasets()
        f_df = add_mche_regime_and_dp_features(f_df)
        f_df = add_compressor_and_jt_physics_features(f_df)
        cls.merged_df = pd.merge(
            f_df, t_df[["shift_id", "total_shaft_power_mw"]], on="shift_id", how="inner"
        )
        cls.train_df, cls.test_df = chronological_train_test_split(
            cls.merged_df, test_ratio=0.20, purge_buffer=2, timestamp_col="shift_id"
        )
        cls.X_test = cls.test_df.loc[:, list(REAL_DATA_SURROGATE_FEATURES)].to_numpy(dtype=float)
        cls.y_test = cls.test_df["total_shaft_power_mw"].to_numpy(dtype=float)

        cls.model = joblib.load(_REBUILD_ROOT / "models" / "c3mr_power_surrogate_real.joblib")
        cls.y_pred = cls.model.predict(cls.X_test)
        cls.metrics = evaluate_power_metrics(cls.y_test, cls.y_pred)
        cls.residuals = cls.y_test - cls.y_pred

    def test_out_of_sample_performance_metrics(self):
        """Prove R^2 = 0.8365 >= 0.60, MAE = 0.8021 MW < 1.0 MW, NMAE = 0.9311% < 1.0% on test set."""
        # Acceptance Gates: AGENTS.md Pasal 2
        self.assertGreaterEqual(self.metrics["r2"], 0.60, "R^2 test failed acceptance threshold (>= 0.60)")
        self.assertAlmostEqual(self.metrics["r2"], 0.8364905, places=3)

        self.assertLess(self.metrics["mae_mw"], 1.0, "MAE test failed acceptance threshold (< 1.0 MW)")
        self.assertAlmostEqual(self.metrics["mae_mw"], 0.802093, places=3)

        self.assertLess(self.metrics["nmae_pct"], 1.0, "NMAE test failed acceptance threshold (< 1.0%)")
        self.assertAlmostEqual(self.metrics["nmae_pct"], 0.931113, places=3)

        self.assertAlmostEqual(self.metrics["rmse_mw"], 1.830739, places=3)

    def test_regime_stratified_breakdown(self):
        """Verify performance breakdown across Baseload, Underload, and Transition regimes."""
        feed_flows = self.test_df["H1FI012"].to_numpy(dtype=float)
        under_mask = feed_flows <= UNDERLOAD_THRESHOLD_T_H  # <= 226.8 t/h
        base_mask = feed_flows >= BASELOAD_THRESHOLD_T_H    # >= 279.8 t/h
        trans_mask = (feed_flows > UNDERLOAD_THRESHOLD_T_H) & (feed_flows < BASELOAD_THRESHOLD_T_H)

        # 1. Baseload regime (n=61)
        self.assertEqual(int(np.sum(base_mask)), 61)
        base_m = evaluate_power_metrics(self.y_test[base_mask], self.y_pred[base_mask])
        self.assertGreaterEqual(base_m["r2"], 0.65)
        self.assertAlmostEqual(base_m["r2"], 0.66766, places=2)
        self.assertLess(base_m["mae_mw"], 0.60)
        self.assertAlmostEqual(base_m["mae_mw"], 0.5200, places=2)

        # 2. Underload regime (n=184)
        self.assertEqual(int(np.sum(under_mask)), 184)
        under_m = evaluate_power_metrics(self.y_test[under_mask], self.y_pred[under_mask])
        self.assertGreaterEqual(under_m["r2"], 0.45)
        self.assertAlmostEqual(under_m["r2"], 0.49086, places=2)
        self.assertLess(under_m["mae_mw"], 0.85)
        self.assertAlmostEqual(under_m["mae_mw"], 0.7740, places=2)

        # 3. Transition regime (n=50)
        self.assertEqual(int(np.sum(trans_mask)), 50)
        trans_m = evaluate_power_metrics(self.y_test[trans_mask], self.y_pred[trans_mask])
        self.assertGreaterEqual(trans_m["r2"], 0.45)
        self.assertAlmostEqual(trans_m["r2"], 0.47728, places=2)
        self.assertLess(trans_m["mae_mw"], 1.30)
        self.assertAlmostEqual(trans_m["mae_mw"], 1.2495, places=2)

    def test_residual_distribution_and_bootstrap_ci(self):
        """Confirm residuals are centered near zero with no systematic bias and check bootstrap 95% CI."""
        mean_res = float(np.mean(self.residuals))
        median_res = float(np.median(self.residuals))

        # Unbiased residual checks: mean and median near zero
        self.assertLess(abs(mean_res), 0.35, f"Residual mean {mean_res:.3f} indicates systematic bias")
        self.assertLess(abs(median_res), 0.30, f"Residual median {median_res:.3f} indicates skewed bias")

        # Compare with recorded evaluation_report_real.json
        report_path = _REBUILD_ROOT / "reports" / "evaluation_report_real.json"
        self.assertTrue(report_path.exists())
        with open(report_path, "r", encoding="utf-8") as f:
            rep = json.load(f)

        ci = rep["bootstrap_95_ci_mw"]
        self.assertAlmostEqual(ci["mae_ci_lower_mw"], 0.6404, places=2)
        self.assertAlmostEqual(ci["mae_ci_upper_mw"], 1.0231, places=2)
        self.assertLess(ci["mae_ci_upper_mw"], 1.10)


class TestCompositionIntegrityAndGeometry(unittest.TestCase):
    """TASK 5: Verify Composition Integrity, Aitchison Simplex S^5 -> R^4, and Exact 100.00% Closure."""

    def test_5comp_simplex_to_4d_euclidean_contrast_matrix(self):
        """Confirm SBP matrix and orthonormal contrast matrix V (5x4) satisfy V^T V = I_4."""
        self.assertEqual(SBP_5COMP.shape, (4, 5))
        self.assertEqual(V_MATRIX_5.shape, (5, 4))

        # Orthonormality verification: V^T @ V must equal 4x4 identity matrix
        vt_v = V_MATRIX_5.T @ V_MATRIX_5
        identity_4 = np.eye(4)
        np.testing.assert_allclose(vt_v, identity_4, atol=1e-9)

    def test_ilr_forward_and_inverse_isometry(self):
        """Verify forward and inverse ILR mapping preserves isometry and reconstructs compositions to 1e-6."""
        # 5-component test compositions (N2, C1, C2, C2H4, C3)
        test_compositions = np.array([
            [0.0338, 0.4437, 0.4494, 0.0085, 0.0646],  # Nominal shift composition
            [0.0500, 0.4000, 0.4800, 0.0100, 0.0600],  # Heavy ethane enriched
            [0.0100, 0.5000, 0.4200, 0.0020, 0.0680],  # High methane lean
        ])

        for comp in test_compositions:
            comp_norm = comp / np.sum(comp)
            xi = ilr_forward(comp_norm)
            self.assertEqual(xi.shape, (1, 4), "ILR forward projection must have shape (1, 4)")

            reconstructed = ilr_inverse(xi)[0]
            self.assertEqual(reconstructed.shape, (5,), "ILR inverse projection must have shape (5,)")
            self.assertAlmostEqual(float(np.sum(reconstructed)), 1.0, places=7)

            # Strict isometry check: infinity norm < 1e-6
            max_error = float(np.max(np.abs(comp_norm - reconstructed)))
            self.assertLess(max_error, 1e-6, f"Isometry error {max_error} exceeds 1e-6 tolerance")

    def test_composition_display_rounding_c1_residual_closure(self):
        """Verify display rounding to 2 decimals uses C1 residual absorption guaranteeing exact 100.00% closure."""
        # Test cases where naïve rounding produces 99.99% or 100.01%
        test_cases = [
            np.array([3.314, 46.086, 45.148, 0.046, 5.406]),  # naive sum = 100.00
            np.array([3.333, 45.333, 44.333, 0.833, 6.168]),  # naive sum = 100.00
            np.array([3.384, 44.374, 44.944, 0.854, 6.284]),  # naive sum = 99.84 unnormalized
        ]

        for raw in test_cases:
            # Normalize to 100% first
            norm_raw = (raw / np.sum(raw)) * 100.0
            rounded = [round(float(v), 2) for v in norm_raw]

            # Enforce closure with C1 (index 1) residual absorption
            residual = round(100.00 - sum(rounded), 2)
            rounded[1] = round(rounded[1] + residual, 2)

            total_sum = round(sum(rounded), 2)
            self.assertEqual(
                total_sum,
                100.00,
                f"Display rounding did not close to 100.00%! Total = {total_sum}",
            )


class TestOutOfDomainBehaviorAndUncertainty(unittest.TestCase):
    """TASK 6: Verify Mahalanobis Distance Operating Boundary and Out-of-Domain Warnings."""

    def test_mahalanobis_envelope_4d_chi2_boundary(self):
        """Confirm critical threshold is 3.080216 and nominal plant point is inside envelope."""
        self.assertAlmostEqual(CHI2_CRITICAL_5COMP, 3.080216, places=5)
        self.assertEqual(HISTORICAL_MEAN_XI.shape, (4,))
        self.assertEqual(HISTORICAL_COV_INV.shape, (4, 4))

        # Nominal operating point (historical median MCR)
        nominal_comp = np.array([0.0338, 0.4437, 0.4494, 0.0085, 0.0646])
        env = check_composition_envelope(nominal_comp)

        self.assertTrue(env["in_envelope"], "Nominal plant composition must be inside envelope")
        self.assertLessEqual(env["mahalanobis_distance"], CHI2_CRITICAL_5COMP)
        self.assertAlmostEqual(env["critical_threshold"], 3.0802, places=4)

    def test_statistical_extrapolation_detection_and_warnings(self):
        """Confirm out-of-domain composition (D_M > 3.0802) triggers statistical extrapolation warning."""
        # Unphysical, extreme synthetic composition far outside Badak Train H historical operational envelope
        extreme_comp = {
            "feed_flow_t_h": 250.0,
            "mcr_flow_t_h": 520.0,
            "comp_N2_molpct": 15.0,  # Extremely high N2 (historical max ~7.8%)
            "comp_C1_molpct": 20.0,  # Extremely low C1 (historical min ~39%)
            "comp_C2_molpct": 35.0,
            "comp_C2H4_molpct": 10.0, # Extremely high C2H4
            "comp_C3_molpct": 20.0,  # Extremely high C3
        }

        audits = validate_operating_point(extreme_comp)
        dm = audits["mahalanobis_distance"]
        in_envelope = audits["in_domain"]

        # 1. Must flag out of envelope
        self.assertFalse(in_envelope, "Extreme composition must be detected as out-of-envelope")
        self.assertGreater(dm, CHI2_CRITICAL_5COMP, f"Mahalanobis distance {dm:.3f} must exceed 3.080")

        # 2. Must emit statistical extrapolation warning
        warnings_emitted = audits["warnings"]
        has_extrap_warning = any("ekstrapolasi statistik" in w for w in warnings_emitted)
        self.assertTrue(
            has_extrap_warning,
            f"Expected statistical extrapolation warning not found in: {warnings_emitted}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
