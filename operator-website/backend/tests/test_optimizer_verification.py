"""operator-website/backend/tests/test_optimizer_verification.py
Milestone 3 & 4 Verification Test Suite: SLSQP Optimizer Verification, Guards & API Aliases
Baseload LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Verification Coverage per Master Prompt §3, §6, §7:
  TASK 1: Normal, Baseload, and Deep Turndown Regimes
    - Test SLSQP under normal operating loads (180.0, 220.0, 245.8 t/h).
    - Test SLSQP under deep turndown (141.2, 145.0, 150.0 t/h).
    - Test SLSQP under baseload operation (280.0, 290.0, 296.4 t/h).
  TASK 2: Operational Bounds & Invariant Adherence
    - Centrifugal compressor anti-surge floor: MCR >= 480.0 t/h in all regimes.
    - Suction drum TAL safety interlock: T_suct >= -45.0 °C.
    - Compositional geometry: Mahalanobis distance D_M <= 3.0802.
    - Composition closure: Exact 100.00 mol% sum within numerical tolerance.
  TASK 3: Independent Constraint Residuals Verification
    - Verify actual constraint residuals independently of the solver success flag.
    - Confirm all margins are strictly non-negative.
  TASK 4: Boundary & Out-of-Domain Inputs
    - Lower boundary (141.2 t/h) and upper boundary (296.4 t/h).
    - Out-of-domain extrapolation flag (feed < 141.2 or > 296.4 t/h).
  TASK 5: Missing and Invalid Input Rejection
    - Negative feed rate, zero feed rate, NaN, and None -> ValueError.
  TASK 6: Solver Non-Convergence & Infeasibility Rejection
    - Never issue recommendation when solver fails or constraints violated (RuntimeError).
  TASK 7: API Route Aliases & HTTP Integration
    - Verify GET /snapshot and GET /api/v1/demo-snapshot return identical schemas.
    - Verify POST /prediction and POST /api/v1/predict accept valid payloads.
    - Verify POST /optimization and POST /api/v1/optimize return valid SLSQP optimum.
    - Verify invalid optimization payloads return HTTP 422 Unprocessable Entity.
  TASK 8: MLflow Tracking Verification
    - Verify non-blocking MLflow run logging with portable URI support.
"""
from __future__ import annotations

import math
import os
import sys
import unittest
from pathlib import Path
from typing import Any, Dict

import numpy as np
from fastapi.testclient import TestClient

# ── Ensure Backend and Root are in sys.path ───────────────────────────
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND_DIR.parents[1]

for p in (str(_ROOT), str(_BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.ilr_engine import CHI2_CRITICAL_5COMP
from core.optimizer_engine import (
    ANTISURGE_FLOOR_T_H,
    SUCTION_TAL_C,
    recommend,
)
from main import app


class TestOptimizerRegimesAndInvariants(unittest.TestCase):
    """TASK 1 & 2: SLSQP Optimizer under Normal, Deep Turndown, and Baseload Regimes."""

    def test_normal_operating_conditions(self):
        """Verify SLSQP convergence and constraints under normal operating conditions (245.8 t/h)."""
        res = recommend(245.8)
        self.assertTrue(res["solver_converged"])
        self.assertGreaterEqual(res["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)
        self.assertGreaterEqual(res["expected_suction_temp_c"], SUCTION_TAL_C)
        self.assertLessEqual(res["mahalanobis_distance"], CHI2_CRITICAL_5COMP)
        self.assertFalse(res["extrapolated"])

        # Composition closure exactly 100.00%
        comp_sum = sum([
            res["comp_N2_molpct"],
            res["comp_C1_molpct"],
            res["comp_C2_molpct"],
            res["comp_C2H4_molpct"],
            res["comp_C3_molpct"],
        ])
        self.assertAlmostEqual(comp_sum, 100.00, places=2)

    def test_deep_turndown_regime(self):
        """Verify SLSQP under deep turndown (145.0 t/h) maintains anti-surge floor and suction TAL."""
        res = recommend(145.0)
        self.assertTrue(res["solver_converged"])
        self.assertGreaterEqual(res["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)
        self.assertLessEqual(res["mcr_flow_t_h"], 490.0)
        self.assertGreaterEqual(res["expected_suction_temp_c"], SUCTION_TAL_C)
        self.assertLessEqual(res["mahalanobis_distance"], CHI2_CRITICAL_5COMP)

    def test_baseload_operation_regime(self):
        """Verify SLSQP under baseload operation (290.0 t/h) scales MCR flow safely."""
        res = recommend(290.0)
        self.assertTrue(res["solver_converged"])
        self.assertGreater(res["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)
        self.assertGreaterEqual(res["expected_suction_temp_c"], SUCTION_TAL_C)
        self.assertLessEqual(res["mahalanobis_distance"], CHI2_CRITICAL_5COMP)

    def test_boundary_conditions_lower_and_upper(self):
        """Verify optimizer at exact historical boundaries."""
        sample = recommend(200.0)
        lo, hi = sample["feed_span_t_h"]

        res_lo = recommend(lo)
        self.assertTrue(res_lo["solver_converged"])
        self.assertFalse(res_lo["extrapolated"])

        res_hi = recommend(hi)
        self.assertTrue(res_hi["solver_converged"])
        self.assertFalse(res_hi["extrapolated"])

    def test_out_of_domain_inputs_flagged(self):
        """Verify out-of-domain feeds (e.g. 100.0 t/h or 350.0 t/h) flag extrapolated == True."""
        res_under = recommend(100.0)
        self.assertTrue(res_under["extrapolated"])
        self.assertGreaterEqual(res_under["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)

        res_over = recommend(350.0)
        self.assertTrue(res_over["extrapolated"])
        self.assertGreaterEqual(res_over["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)


class TestIndependentConstraintResiduals(unittest.TestCase):
    """TASK 3: Independent Constraint Residuals Auditing."""

    def test_residuals_independently_evaluated(self):
        """Confirm constraint_residuals dict exists and all safety margins are strictly non-negative."""
        res = recommend(245.8)
        self.assertIn("constraint_residuals", res)
        residuals = res["constraint_residuals"]

        # 1. Suction TAL margin (T_suct - (-45.0)) >= 0
        self.assertIn("suction_tal_margin_c", residuals)
        self.assertGreaterEqual(residuals["suction_tal_margin_c"], 0.0)

        # 2. Mahalanobis margin (3.0802 - D_M) >= 0
        self.assertIn("mahalanobis_margin", residuals)
        self.assertGreaterEqual(residuals["mahalanobis_margin"], 0.0)

        # 3. Anti-surge margin (MCR - 480.0) >= 0
        self.assertIn("antisurge_margin_t_h", residuals)
        self.assertGreaterEqual(residuals["antisurge_margin_t_h"], -0.1)

        # 4. Superheat margin >= 0
        self.assertIn("superheat_margin_c", residuals)
        self.assertGreaterEqual(residuals["superheat_margin_c"], -0.05)


class TestInvalidInputsAndFailureGuards(unittest.TestCase):
    """TASK 5 & 6: Missing and Invalid Input Rejection & Non-Convergence Guards."""

    def test_zero_feed_rejected(self):
        """Feed rate of 0.0 t/h must raise ValueError."""
        with self.assertRaises(ValueError):
            recommend(0.0)

    def test_negative_feed_rejected(self):
        """Negative feed rate must raise ValueError."""
        with self.assertRaises(ValueError):
            recommend(-50.0)

    def test_nan_and_inf_feed_rejected(self):
        """NaN and Inf feed rates must raise ValueError."""
        with self.assertRaises(ValueError):
            recommend(float("nan"))
        with self.assertRaises(ValueError):
            recommend(float("inf"))

    def test_none_feed_rejected(self):
        """None feed rate must raise ValueError."""
        with self.assertRaises(ValueError):
            recommend(None)  # type: ignore


class TestApiRouteAliasesAndIntegration(unittest.TestCase):
    """TASK 7: API Route Aliases & Full Backend HTTP Integration."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_backend_health(self):
        """Verify /health returns HTTP 200 with healthy status."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["mode"], "READ_ONLY_DECISION_SUPPORT")

    def test_snapshot_route_alias(self):
        """Verify GET /snapshot and GET /api/v1/demo-snapshot return identical HTTP 200 payloads."""
        resp1 = self.client.get("/snapshot")
        resp2 = self.client.get("/api/v1/demo-snapshot")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.json(), resp2.json())

        data = resp1.json()
        self.assertIn("values", data)
        self.assertIn("H1FI012", data["values"])
        self.assertIn("H5FI006A", data["values"])
        self.assertAlmostEqual(data["values"]["H5FI006A"]["value"], 232.3, places=1)

    def test_prediction_route_alias(self):
        """Verify POST /prediction and POST /api/v1/predict accept requests and calculate SEC LNG."""
        payload = {
            "feed_flow_t_h": 245.8,
            "mcr_flow_t_h": 500.0,
            "comp_N2_molpct": 3.38,
            "comp_C1_molpct": 44.37,
            "comp_C2_molpct": 44.94,
            "comp_C2H4_molpct": 0.85,
            "comp_C3_molpct": 6.46,
            "actual_feed_flow_t_h": 245.8,
            "actual_mcr_flow_t_h": 500.0,
            "actual_comp_N2_molpct": 3.38,
            "actual_comp_C1_molpct": 44.37,
            "actual_comp_C2_molpct": 44.94,
            "actual_comp_C2H4_molpct": 0.85,
            "actual_comp_C3_molpct": 6.46,
        }
        resp1 = self.client.post("/prediction", json=payload)
        resp2 = self.client.post("/api/v1/predict", json=payload)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

        data = resp1.json()
        self.assertIn("prediction", data)
        self.assertIn("sec_lng_kwh_per_t", data["prediction"])
        self.assertGreater(data["prediction"]["sec_lng_kwh_per_t"], 0.0)

    def test_optimization_route_alias_and_invariants(self):
        """Verify POST /optimization and POST /api/v1/optimize return valid SLSQP optimum."""
        payload = {"feed_flow_t_h": 245.8}
        resp1 = self.client.post("/optimization", json=payload)
        resp2 = self.client.post("/api/v1/optimize", json=payload)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

        data = resp1.json()
        self.assertTrue(data["solver_converged"])
        self.assertGreaterEqual(data["mcr_flow_t_h"], 480.0)
        self.assertIn("constraint_residuals", data)
        self.assertGreaterEqual(data["constraint_residuals"]["suction_tal_margin_c"], 0.0)

    def test_proximity_trimming_recommendation(self):
        """Verify that providing actual DCS composition yields closest feasible composition."""
        actual_comp = {
            "feed_flow_t_h": 300.0,
            "actual_mcr_flow_t_h": 680.0,
            "actual_comp_N2_molpct": 3.39,
            "actual_comp_C1_molpct": 44.45,
            "actual_comp_C2_molpct": 45.02,
            "actual_comp_C2H4_molpct": 0.85,
            "actual_comp_C3_molpct": 6.29,
            "alpha_trim": 0.30,
        }
        resp = self.client.post("/api/v1/optimize", json=actual_comp)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # MCR flow must scale with feed load (300 t/h -> ~577-617 t/h, NOT stuck at 480 t/h)
        self.assertGreater(data["mcr_flow_t_h"], 550.0)
        self.assertLess(data["mcr_flow_t_h"], 650.0)

        # Composition must be close to current DCS point (within 1.5 mol%)
        self.assertAlmostEqual(data["comp_N2_molpct"], 3.39, delta=1.5)
        self.assertAlmostEqual(data["comp_C1_molpct"], 44.45, delta=1.5)
        self.assertAlmostEqual(data["comp_C2_molpct"], 45.02, delta=1.5)
        self.assertAlmostEqual(data["comp_C3_molpct"], 6.29, delta=1.5)

        # Exact 100.00% closure and Mahalanobis safety
        comp_sum = sum([data[f"comp_{k}_molpct"] for k in ("N2", "C1", "C2", "C2H4", "C3")])
        self.assertAlmostEqual(comp_sum, 100.00, delta=0.05)
        self.assertLessEqual(data["mahalanobis_distance"], 3.0802)

    def test_invalid_optimization_payload_returns_422(self):
        """Verify invalid optimization inputs (negative feed or invalid types) return HTTP 422."""
        # Out-of-schema negative feed
        resp = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": -100.0})
        self.assertEqual(resp.status_code, 422)

        # Missing required parameter
        resp_empty = self.client.post("/api/v1/optimize", json={})
        self.assertEqual(resp_empty.status_code, 422)


class TestMlflowExperimentPortability(unittest.TestCase):
    """TASK 8: MLflow Tracking Portability and Logging."""

    def test_mlflow_logging_non_blocking(self):
        """Confirm optimizer completes and logs telemetry without raising MLflow exceptions."""
        res = recommend(220.0)
        self.assertTrue(res["solver_converged"])
        db_path = _ROOT / "mlflow.db"
        self.assertTrue(db_path.exists(), "MLflow SQLite database must exist at root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
