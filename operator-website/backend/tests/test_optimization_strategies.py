"""operator-website/backend/tests/test_optimization_strategies.py
Milestone 1 Automated Verification Suite: Multi-Strategy C3MR Optimization Engine
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Test Coverage per Milestone 1 Specification & Requirements R2, R4, R5:
  1. Strategy CONDITION_DEPENDENT:
     - Actively responds to feed variations (150 t/h vs 280 t/h).
     - Proves targets are NOT frozen or clamped to actual DCS composition.
     - Proves circulation flow scales actively with load.
  2. Strategy FIXED_RECIPE:
     - Maintains certified invariant master recipe ([3.77% N2, 42.21% C1, 43.67% C2, 1.53% C2H4, 8.82% C3])
       across operating envelope (150 t/h, 200 t/h, 280 t/h).
     - Circulation flow scales with load while adhering to anti-surge floor (480.0 t/h).
  3. Strategy MINIMUM_INTERVENTION:
     - Demonstrates smooth trade-off between energy optimization and proximity to current DCS state.
     - Proves distance to actual composition decreases as transition penalty increases (or alpha_trim decreases).
  4. Simplex Closure & Positivity:
     - Strict positivity: x_i > 0 for all components across all strategies and feed rates.
     - Molar conservation: sum(x_i) == 100.00 +- 0.01 mol% across all transformations.
  5. Constraint Residuals Verification:
     - Independent margin recalculation and non-negativity:
       * antisurge_margin_t_h >= 0.0 (MCR >= 480.0 t/h)
       * suction_tal_margin_c >= 0.0 (T_suct >= -45.0 °C)
       * superheat_margin_c >= 0.0 (Delta T_superheat >= 3.0 °C)
       * mahalanobis_margin >= 0.0 (D_M <= 3.0802, chi²(4, 0.95))
  6. API Endpoint /api/v1/optimize Integration:
     - Strategy dispatch handling (CONDITION_DEPENDENT, FIXED_RECIPE, MINIMUM_INTERVENTION).
     - Backward compatibility when strategy is omitted.
     - Verification of response schema fields (effective_inputs, calculation_timestamp, constraint_residuals, explanation).
     - Request validation and rejection of out-of-range or invalid inputs (HTTP 422).
     - Read-only safety verification: zero DCS write endpoints or control side effects.

Governance: AGENTS.md (Pasals 1-13), ORIGINAL_REQUEST.md (Requirements R2, R4, R5).
"""
from __future__ import annotations

import datetime
import math
import os
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi.testclient import TestClient

# ── Ensure Backend and Root are in sys.path ───────────────────────────
_CURRENT_FILE = Path(__file__).resolve()
if "operator-website" in _CURRENT_FILE.parts:
    _BACKEND_DIR = _CURRENT_FILE.parents[1]
    _ROOT = _BACKEND_DIR.parents[1]
else:
    _ROOT = _CURRENT_FILE.parents[3]
    _BACKEND_DIR = _ROOT / "operator-website" / "backend"

for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.ilr_engine import CHI2_CRITICAL_5COMP, ilr_forward
from core.optimizer_engine import (
    ANTISURGE_FLOOR_T_H,
    SUCTION_TAL_C,
    SUPERHEAT_MIN_C,
    recommend,
)
from main import app

try:
    from api.schemas import OptimizationStrategy
except ImportError:
    # Graceful fallback before schema implementation
    class OptimizationStrategy:  # type: ignore
        CONDITION_DEPENDENT = "CONDITION_DEPENDENT"
        FIXED_RECIPE = "FIXED_RECIPE"
        MINIMUM_INTERVENTION = "MINIMUM_INTERVENTION"


class TestConditionDependentStrategy(unittest.TestCase):
    """Test Suite 1: Strategy CONDITION_DEPENDENT active response and non-freezing."""

    def test_active_response_to_feed_rate_variations(self):
        """Verify that CONDITION_DEPENDENT actively shifts targets between underload (150 t/h) and baseload (280 t/h)."""
        res_150 = recommend(150.0, strategy="CONDITION_DEPENDENT")
        res_280 = recommend(280.0, strategy="CONDITION_DEPENDENT")

        # 1. Both optimizations must succeed
        self.assertTrue(res_150["solver_converged"], "Optimizer must converge at 150.0 t/h")
        self.assertTrue(res_280["solver_converged"], "Optimizer must converge at 280.0 t/h")

        # 2. Circulation flow scales actively with load
        self.assertGreaterEqual(
            res_150["mcr_flow_t_h"],
            ANTISURGE_FLOOR_T_H,
            "150 t/h MCR flow must respect anti-surge floor",
        )
        self.assertGreater(
            res_280["mcr_flow_t_h"],
            res_150["mcr_flow_t_h"],
            "280 t/h MCR flow must be strictly greater than 150 t/h flow",
        )
        self.assertGreaterEqual(
            res_280["mcr_flow_t_h"],
            530.0,
            "280 t/h baseload MCR flow must scale above 530 t/h",
        )

        # 3. Composition targets are NOT frozen across loads
        c3_diff = abs(res_280["comp_C3_molpct"] - res_150["comp_C3_molpct"])
        c1_diff = abs(res_280["comp_C1_molpct"] - res_150["comp_C1_molpct"])
        total_comp_diff = sum(
            abs(res_280[f"comp_{k}_molpct"] - res_150[f"comp_{k}_molpct"])
            for k in ("N2", "C1", "C2", "C2H4", "C3")
        )

        self.assertGreater(
            c3_diff,
            1.0,
            f"C3 target must actively shift with load (delta={c3_diff:.2f} mol% <= 1.0)",
        )
        self.assertGreater(
            c1_diff,
            1.0,
            f"C1 target must actively shift with load (delta={c1_diff:.2f} mol% <= 1.0)",
        )
        self.assertGreater(
            total_comp_diff,
            2.5,
            f"Total absolute composition movement must be significant (sum={total_comp_diff:.2f} mol% <= 2.5)",
        )

    def test_targets_not_clamped_to_actual_dcs_composition(self):
        """Verify that in CONDITION_DEPENDENT mode, targets are NOT artificially contracted to actual DCS values."""
        actual_comp = {
            "N2": 3.39,
            "C1": 44.45,
            "C2": 45.02,
            "C2H4": 0.85,
            "C3": 6.29,
        }
        # At 150 t/h underload, thermodynamic optimum requires lower C3 (~3.7-4.2%)
        res_150 = recommend(
            150.0,
            actual_comp=actual_comp,
            strategy="CONDITION_DEPENDENT",
        )

        self.assertTrue(res_150["solver_converged"])
        # In CONDITION_DEPENDENT mode, C3 must not be pulled back to actual 6.29%
        c3_delta = abs(res_150["comp_C3_molpct"] - actual_comp["C3"])
        self.assertGreater(
            c3_delta,
            1.0,
            f"In CONDITION_DEPENDENT mode, C3 must not be clamped to actual composition (delta={c3_delta:.2f} mol%)",
        )


class TestFixedRecipeStrategy(unittest.TestCase):
    """Test Suite 2: Strategy FIXED_RECIPE across varying loads."""

    CERTIFIED_MASTER_RECIPE = {
        "N2": 3.77,
        "C1": 42.21,  # 42.21 or 42.22 after C1 residual absorption
        "C2": 43.67,
        "C2H4": 1.53,
        "C3": 8.82,
    }

    def test_fixed_recipe_composition_invariance(self):
        """Verify composition remains constant at certified master recipe across 150, 200, and 280 t/h."""
        loads = [150.0, 200.0, 280.0]
        results = [recommend(f, strategy="FIXED_RECIPE") for f in loads]

        for idx, res in enumerate(results):
            feed = loads[idx]
            self.assertTrue(res["solver_converged"], f"Solver must converge at {feed} t/h")
            self.assertAlmostEqual(res["comp_N2_molpct"], 3.77, delta=0.05)
            self.assertIn(res["comp_C1_molpct"], (42.21, 42.22))
            self.assertAlmostEqual(res["comp_C2_molpct"], 43.67, delta=0.05)
            self.assertAlmostEqual(res["comp_C2H4_molpct"], 1.53, delta=0.05)
            self.assertAlmostEqual(res["comp_C3_molpct"], 8.82, delta=0.05)

        # Invariance across loads: delta between 150 t/h and 280 t/h must be negligible
        res_150, res_280 = results[0], results[2]
        for k in ("N2", "C1", "C2", "C2H4", "C3"):
            diff = abs(res_150[f"comp_{k}_molpct"] - res_280[f"comp_{k}_molpct"])
            self.assertLess(
                diff,
                0.02,
                f"Component {k} must remain invariant between loads in FIXED_RECIPE (diff={diff:.3f})",
            )

    def test_fixed_recipe_circulation_flow_scaling(self):
        """Verify that while composition is fixed, circulation flow scales with feed rate."""
        res_150 = recommend(150.0, strategy="FIXED_RECIPE")
        res_200 = recommend(200.0, strategy="FIXED_RECIPE")
        res_280 = recommend(280.0, strategy="FIXED_RECIPE")

        # 150 t/h respects anti-surge floor
        self.assertGreaterEqual(res_150["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)
        # Monotonic scaling with load
        self.assertLessEqual(res_150["mcr_flow_t_h"], res_200["mcr_flow_t_h"])
        self.assertLess(res_200["mcr_flow_t_h"], res_280["mcr_flow_t_h"])
        self.assertGreaterEqual(res_280["mcr_flow_t_h"], 530.0)


class TestMinimumInterventionStrategy(unittest.TestCase):
    """Test Suite 3: Strategy MINIMUM_INTERVENTION trade-off and transition tuning."""

    ACTUAL_DCS_COMP = {
        "N2": 3.39,
        "C1": 44.45,
        "C2": 45.02,
        "C2H4": 0.85,
        "C3": 6.29,
    }

    def test_minimum_intervention_closer_to_actual_than_unconstrained(self):
        """Verify that MINIMUM_INTERVENTION results in a composition strictly closer to actual DCS state."""
        feed = 245.8
        res_cond = recommend(feed, strategy="CONDITION_DEPENDENT")
        res_min = recommend(
            feed,
            actual_comp=self.ACTUAL_DCS_COMP,
            strategy="MINIMUM_INTERVENTION",
        )

        dist_cond = sum(
            abs(res_cond[f"comp_{k}_molpct"] - self.ACTUAL_DCS_COMP[k])
            for k in ("N2", "C1", "C2", "C2H4", "C3")
        )
        dist_min = sum(
            abs(res_min[f"comp_{k}_molpct"] - self.ACTUAL_DCS_COMP[k])
            for k in ("N2", "C1", "C2", "C2H4", "C3")
        )

        self.assertLess(
            dist_min,
            dist_cond,
            f"MINIMUM_INTERVENTION distance ({dist_min:.2f}) must be smaller than CONDITION_DEPENDENT ({dist_cond:.2f})",
        )

    def test_smooth_transition_tuning_progression(self):
        """Verify that varying alpha_trim provides a smooth, monotonic progression in distance to actual DCS."""
        feed = 245.8
        alphas = [0.10, 0.30, 0.70]
        distances = []

        for a in alphas:
            res = recommend(
                feed,
                actual_comp=self.ACTUAL_DCS_COMP,
                alpha_trim=a,
                strategy="MINIMUM_INTERVENTION",
            )
            d = sum(
                abs(res[f"comp_{k}_molpct"] - self.ACTUAL_DCS_COMP[k])
                for k in ("N2", "C1", "C2", "C2H4", "C3")
            )
            distances.append(d)

        # Monotonic increase: smaller alpha_trim -> closer to actual DCS
        self.assertLess(
            distances[0],
            distances[1],
            f"Distance at alpha=0.10 ({distances[0]:.2f}) must be less than alpha=0.30 ({distances[1]:.2f})",
        )
        self.assertLess(
            distances[1],
            distances[2],
            f"Distance at alpha=0.30 ({distances[1]:.2f}) must be less than alpha=0.70 ({distances[2]:.2f})",
        )


class TestSimplexClosureAndPositivity(unittest.TestCase):
    """Test Suite 4: Aitchison Simplex closure and strict positivity across all strategies and loads."""

    FEED_RATES = [141.2, 150.0, 180.0, 200.0, 245.8, 280.0, 296.4]
    STRATEGIES = ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"]
    SAMPLE_ACTUAL_COMP = {
        "N2": 3.39,
        "C1": 44.45,
        "C2": 45.02,
        "C2H4": 0.85,
        "C3": 6.29,
    }

    def test_simplex_positivity_and_exact_closure(self):
        """Verify x_i > 0 and sum(x_i) == 100.00 +- 0.01% for all strategies across full operating envelope."""
        for strategy in self.STRATEGIES:
            for feed in self.FEED_RATES:
                res = recommend(
                    feed_t_h=feed,
                    actual_comp=self.SAMPLE_ACTUAL_COMP if strategy == "MINIMUM_INTERVENTION" else None,
                    strategy=strategy,
                )

                # 1. Positivity
                for k in ("N2", "C1", "C2", "C2H4", "C3"):
                    val = res[f"comp_{k}_molpct"]
                    self.assertGreater(
                        val,
                        0.0,
                        f"Component {k} must be strictly positive at feed={feed}, strategy={strategy} (got {val})",
                    )

                # 2. Closure to 100.00%
                comp_sum = sum(res[f"comp_{k}_molpct"] for k in ("N2", "C1", "C2", "C2H4", "C3"))
                self.assertAlmostEqual(
                    comp_sum,
                    100.00,
                    places=2,
                    msg=f"Composition must sum to 100.00 +- 0.01% at feed={feed}, strategy={strategy} (got {comp_sum:.4f})",
                )

                # 3. Mahalanobis operating envelope adherence
                self.assertLessEqual(
                    res["mahalanobis_distance"],
                    CHI2_CRITICAL_5COMP,
                    f"Mahalanobis distance D_M must remain <= 3.0802 at feed={feed}, strategy={strategy}",
                )


class TestConstraintResidualsVerification(unittest.TestCase):
    """Test Suite 5: Independent recalculation and non-negativity of physical constraint residuals."""

    TEST_LOADS = [145.0, 220.0, 290.0]
    STRATEGIES = ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"]

    def test_constraint_residuals_presence_and_non_negativity(self):
        """Verify constraint_residuals dictionary contains all 4 required margins and each is >= 0.0."""
        for strategy in self.STRATEGIES:
            for feed in self.TEST_LOADS:
                res = recommend(feed_t_h=feed, strategy=strategy)

                self.assertIn(
                    "constraint_residuals",
                    res,
                    f"constraint_residuals must be present for strategy={strategy}, feed={feed}",
                )
                residuals = res["constraint_residuals"]
                self.assertIsInstance(residuals, dict)

                # Required keys
                for key in (
                    "antisurge_margin_t_h",
                    "suction_tal_margin_c",
                    "superheat_margin_c",
                    "mahalanobis_margin",
                ):
                    self.assertIn(key, residuals, f"Missing key '{key}' in constraint_residuals")

                # Non-negativity with numerical epsilon
                self.assertGreaterEqual(
                    residuals["antisurge_margin_t_h"],
                    -0.05,
                    f"antisurge_margin_t_h violated at feed={feed}, strategy={strategy}",
                )
                self.assertGreaterEqual(
                    residuals["suction_tal_margin_c"],
                    -0.05,
                    f"suction_tal_margin_c violated at feed={feed}, strategy={strategy}",
                )
                self.assertGreaterEqual(
                    residuals["superheat_margin_c"],
                    -0.05,
                    f"superheat_margin_c violated at feed={feed}, strategy={strategy}",
                )
                self.assertGreaterEqual(
                    residuals["mahalanobis_margin"],
                    -0.01,
                    f"mahalanobis_margin violated at feed={feed}, strategy={strategy}",
                )

    def test_independent_residual_recalculation_consistency(self):
        """Verify that reported margins match independent direct physical recalculation."""
        res = recommend(245.8, strategy="CONDITION_DEPENDENT")
        residuals = res["constraint_residuals"]

        # 1. Anti-surge floor margin: MCR - 480.0
        expected_surge_margin = res["mcr_flow_t_h"] - ANTISURGE_FLOOR_T_H
        self.assertAlmostEqual(
            residuals["antisurge_margin_t_h"],
            expected_surge_margin,
            places=1,
            msg="antisurge_margin_t_h must equal mcr_flow_t_h - 480.0",
        )

        # 2. Suction TAL margin: T_suct - (-45.0)
        expected_tal_margin = res["expected_suction_temp_c"] - SUCTION_TAL_C
        self.assertAlmostEqual(
            residuals["suction_tal_margin_c"],
            expected_tal_margin,
            places=1,
            msg="suction_tal_margin_c must equal expected_suction_temp_c - (-45.0)",
        )

        # 3. Mahalanobis margin: 3.0802 - D_M
        expected_mahalanobis_margin = CHI2_CRITICAL_5COMP - res["mahalanobis_distance"]
        self.assertAlmostEqual(
            residuals["mahalanobis_margin"],
            expected_mahalanobis_margin,
            places=3,
            msg="mahalanobis_margin must equal 3.0802 - mahalanobis_distance",
        )


class TestOptimizeApiIntegration(unittest.TestCase):
    """Test Suite 6: API Integration tests for /api/v1/optimize and /optimization endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_api_strategy_dispatch_and_response_schema(self):
        """Verify that /api/v1/optimize correctly handles all 3 strategies and returns complete schema fields."""
        strategies = ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"]

        for strat in strategies:
            payload = {
                "feed_flow_t_h": 245.8,
                "strategy": strat,
                "actual_comp_N2_molpct": 3.39,
                "actual_comp_C1_molpct": 44.45,
                "actual_comp_C2_molpct": 45.02,
                "actual_comp_C2H4_molpct": 0.85,
                "actual_comp_C3_molpct": 6.29,
                "alpha_trim": 0.30,
            }

            resp = self.client.post("/api/v1/optimize", json=payload)
            self.assertEqual(
                resp.status_code,
                200,
                f"/api/v1/optimize failed for strategy {strat}: {resp.text}",
            )
            data = resp.json()

            # Verify strategy echo
            self.assertEqual(data.get("strategy"), strat)

            # Verify effective_inputs echo
            self.assertIn("effective_inputs", data)
            self.assertEqual(data["effective_inputs"].get("feed_flow_t_h"), 245.8)
            self.assertEqual(data["effective_inputs"].get("strategy"), strat)

            # Verify calculation_timestamp (valid ISO 8601 string)
            self.assertIn("calculation_timestamp", data)
            ts_str = data["calculation_timestamp"]
            parsed_dt = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            self.assertIsNotNone(parsed_dt)

            # Verify constraint_residuals
            self.assertIn("constraint_residuals", data)
            for k in ("antisurge_margin_t_h", "suction_tal_margin_c", "superheat_margin_c", "mahalanobis_margin"):
                self.assertIn(k, data["constraint_residuals"])
                self.assertGreaterEqual(data["constraint_residuals"][k], -0.05)

            # Verify explanation string
            self.assertIn("explanation", data)
            self.assertTrue(len(data["explanation"]) > 10, "Explanation must be a descriptive non-empty string")

    def test_api_backward_compatibility_omitted_strategy(self):
        """Verify that omitting strategy in request body defaults gracefully without error."""
        resp = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": 245.8})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["solver_converged"])
        self.assertIn(data.get("strategy"), ("CONDITION_DEPENDENT", None, "Live SLSQP Solver"))

    def test_api_route_alias_parity(self):
        """Verify POST /optimization behaves identically to POST /api/v1/optimize."""
        payload = {"feed_flow_t_h": 220.0, "strategy": "FIXED_RECIPE"}
        resp_v1 = self.client.post("/api/v1/optimize", json=payload)
        resp_alias = self.client.post("/optimization", json=payload)

        self.assertEqual(resp_v1.status_code, 200)
        self.assertEqual(resp_alias.status_code, 200)

        data_v1 = resp_v1.json()
        data_alias = resp_alias.json()
        self.assertEqual(data_v1["mcr_flow_t_h"], data_alias["mcr_flow_t_h"])
        self.assertEqual(data_v1["comp_N2_molpct"], data_alias["comp_N2_molpct"])
        self.assertEqual(data_v1["comp_C3_molpct"], data_alias["comp_C3_molpct"])

    def test_api_request_validation_rejections(self):
        """Verify HTTP 422 Unprocessable Entity for invalid or out-of-range payloads."""
        # 1. Negative feed rate
        resp_neg = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": -50.0})
        self.assertEqual(resp_neg.status_code, 422)

        # 2. Zero feed rate
        resp_zero = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": 0.0})
        self.assertEqual(resp_zero.status_code, 422)

        # 3. Missing feed rate
        resp_empty = self.client.post("/api/v1/optimize", json={})
        self.assertEqual(resp_empty.status_code, 422)

        # 4. Out-of-range feed rate
        resp_huge = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": 5000.0})
        self.assertEqual(resp_huge.status_code, 422)

        # 5. Invalid strategy string
        resp_bad_strat = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 245.8, "strategy": "NON_EXISTENT_STRATEGY"},
        )
        self.assertEqual(resp_bad_strat.status_code, 422)

    def test_read_only_safety_boundaries(self):
        """Verify that zero write or control endpoints exist on the FastAPI application router."""
        disallowed_prefixes = ["/setpoint", "/dcs", "/sis", "/plc", "/write", "/control"]
        for route in app.routes:
            path = getattr(route, "path", "").lower()
            methods = getattr(route, "methods", set())
            for prefix in disallowed_prefixes:
                self.assertFalse(
                    path.startswith(prefix),
                    f"Read-only boundary violated: found dangerous endpoint '{path}'",
                )
            # No PUT or DELETE endpoints should exist in an advisory decision-support system
            self.assertNotIn("PUT", methods, f"PUT method not permitted on advisory endpoint '{path}'")
            self.assertNotIn("DELETE", methods, f"DELETE method not permitted on advisory endpoint '{path}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
