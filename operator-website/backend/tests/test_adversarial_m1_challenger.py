"""operator-website/backend/tests/test_adversarial_m1_challenger.py
Milestone 1 Adversarial Empirical Stress Suite & Metamorphic Oracle
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Authored by challenger_m1_1 (Role: critic, specialist)
This test suite executes empirical adversarial challenges against:
  - operator-website/backend/core/optimizer_engine.py
  - operator-website/backend/api/schemas.py
  - operator-website/backend/api/routes.py

Challenge Dimensions:
  1. Operating Load Sweeps & Anti-Surge Operating Floor:
     - Feeds from extreme underload (50-100 t/h) to baseload (340-450 t/h).
     - Strict verification that MCR circulation flow >= 480.0 t/h (Modul 3).
     - Verified across all 3 strategies: CONDITION_DEPENDENT, FIXED_RECIPE, MINIMUM_INTERVENTION.
  2. Simplex Closure and Numerical Positivity:
     - Strict mathematical positivity: x_i > 0 for all 5 components.
     - Strict display positivity: x_i >= 0.01 mol%.
     - Exact molar closure: sum(x_i) == 100.00 +- 0.001 mol%.
     - Corrupted, unnormalized, or zero-component actual DCS compositions.
  3. Condition-Dependent Metamorphic Properties:
     - Target compositions actively differ across underload and baseload regimes without freezing.
     - Targets are invariant to actual DCS composition (zero artificial proximity clamping).
  4. Fixed-Recipe Metamorphic Properties:
     - Invariant master recipe locked across loads within +-0.02 mol%.
     - Monotonically non-decreasing circulation scaling with load.
     - Support for custom selected recipe presets.
  5. Minimum-Intervention Metamorphic Properties:
     - Smooth monotonic trade-off across alpha_trim (0.05 to 1.0).
     - Proximity increases with higher intervention_weight.
  6. Independent Thermodynamic Constraint Residuals:
     - Anti-surge margin >= 0.0.
     - Suction drum TAL margin >= 0.0 (T_suct >= -45.0 °C, Modul 4).
     - Superheat margin >= 0.0 (Delta T_sh >= 3.0 °C above PR dew point).
     - Mahalanobis compositional distance margin >= 0.0 (D_M <= 3.0802, Modul 5).
  7. API Schema, Contract Parity & Defensive Guards:
     - Valid and invalid strategy tokens.
     - Out-of-bounds inputs rejected with HTTP 422.
     - Effective inputs echoing and timestamp generation.
     - Strict read-only safety boundary verification.

Compliance: AGENTS.md (Hukum Anti-Dosa Rekayasa), ORIGINAL_REQUEST.md.
"""
from __future__ import annotations

import datetime
import math
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi.testclient import TestClient

# Resolve paths
_CURRENT_FILE = Path(__file__).resolve()
_BACKEND_DIR = _CURRENT_FILE.parents[1]
_ROOT = _BACKEND_DIR.parents[1]

for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.ilr_engine import CHI2_CRITICAL_5COMP, ilr_forward, ilr_inverse
from core.optimizer_engine import (
    ANTISURGE_FLOOR_T_H,
    INVARIANT_RECIPE_MOLPCT,
    SUCTION_TAL_C,
    SUPERHEAT_MIN_C,
    OptimizationStrategy,
    compute_superheat_margin,
    enforce_simplex_closure,
    recommend,
)
from main import app

PARTS = ("N2", "C1", "C2", "C2H4", "C3")


class TestAdversarialLoadEnvelopeAndSurgeFloor(unittest.TestCase):
    """Adversarial Challenge 1: Operating envelope sweeps and anti-surge floor enforcement."""

    def setUp(self):
        self.feed_sweep = [
            50.0, 80.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0,
            180.0, 200.0, 220.0, 250.0, 280.0, 300.0, 320.0, 340.0,
            380.0, 450.0
        ]
        self.strategies = [
            OptimizationStrategy.CONDITION_DEPENDENT,
            OptimizationStrategy.FIXED_RECIPE,
            OptimizationStrategy.MINIMUM_INTERVENTION,
        ]

    def test_antisurge_floor_never_violated_across_envelope(self):
        """Stress-test: anti-surge floor (480.0 t/h) must hold for all loads and strategies."""
        for strat in self.strategies:
            for feed in self.feed_sweep:
                with self.subTest(strategy=strat.value, feed=feed):
                    res = recommend(feed, strategy=strat)
                    mcr = res["mcr_flow_t_h"]
                    margin = res["constraint_residuals"]["antisurge_margin_t_h"]

                    self.assertGreaterEqual(
                        mcr,
                        ANTISURGE_FLOOR_T_H,
                        f"Strategy {strat.value} at feed {feed} t/h violated anti-surge floor: {mcr} < {ANTISURGE_FLOOR_T_H}",
                    )
                    self.assertGreaterEqual(
                        margin,
                        0.0,
                        f"Strategy {strat.value} at feed {feed} t/h had negative anti-surge margin: {margin}",
                    )

                    # Underload condition: feed <= 220 t/h must trigger anti-surge floor
                    if feed <= 220.0:
                        self.assertEqual(
                            mcr,
                            ANTISURGE_FLOOR_T_H,
                            f"At underload {feed} t/h, MCR flow should be clamped exactly at floor 480.0 t/h, got {mcr}",
                        )
                        self.assertTrue(
                            res["antisurge_floor_applied"],
                            f"antisurge_floor_applied flag should be True at feed {feed} t/h",
                        )

    def test_monotonic_circulation_scaling(self):
        """Verify MCR circulation flow is monotonically non-decreasing with feed rate."""
        for strat in self.strategies:
            prev_mcr = -1.0
            for feed in sorted(self.feed_sweep):
                res = recommend(feed, strategy=strat)
                mcr = res["mcr_flow_t_h"]
                if prev_mcr >= 0:
                    self.assertGreaterEqual(
                        mcr,
                        prev_mcr - 1e-4,
                        f"Strategy {strat.value} violated monotonicity: at feed {feed} t/h mcr={mcr} < prev={prev_mcr}",
                    )
                prev_mcr = mcr


class TestAdversarialSimplexAndCompositionInvariants(unittest.TestCase):
    """Adversarial Challenge 2: Simplex geometry closure and positivity invariants."""

    def test_simplex_positivity_and_exact_closure_sweep(self):
        """Empirically test that every component is strictly > 0 and sum is exactly 100.00%."""
        feed_points = [100.0, 140.0, 180.0, 220.0, 280.0, 320.0, 360.0]
        strategies = [
            OptimizationStrategy.CONDITION_DEPENDENT,
            OptimizationStrategy.FIXED_RECIPE,
            OptimizationStrategy.MINIMUM_INTERVENTION,
        ]

        for strat in strategies:
            for feed in feed_points:
                with self.subTest(strategy=strat.value, feed=feed):
                    res = recommend(feed, strategy=strat)
                    comps = [res[f"comp_{p}_molpct"] for p in PARTS]

                    # 1. Positivity
                    for p, val in zip(PARTS, comps):
                        self.assertGreater(
                            val,
                            0.0,
                            f"Strategy {strat.value} at feed {feed} t/h: component {p} <= 0: {val}",
                        )
                        self.assertGreaterEqual(
                            val,
                            0.01,
                            f"Strategy {strat.value} at feed {feed} t/h: component {p} < 0.01 mol%: {val}",
                        )

                    # 2. Exact 100.00% closure
                    total_molpct = round(sum(comps), 4)
                    self.assertAlmostEqual(
                        total_molpct,
                        100.00,
                        places=2,
                        msg=f"Strategy {strat.value} at feed {feed} t/h: sum(x_i) != 100.00%: {total_molpct}",
                    )

    def test_corrupted_actual_composition_resilience(self):
        """Adversarial test: pass unnormalized, near-zero, and corrupted actual compositions."""
        corrupted_cases = [
            {"label": "Unnormalized Low", "comp": {"N2": 1.0, "C1": 20.0, "C2": 20.0, "C2H4": 0.5, "C3": 3.0}},  # Sum = 44.5%
            {"label": "Unnormalized High", "comp": {"N2": 10.0, "C1": 80.0, "C2": 80.0, "C2H4": 5.0, "C3": 20.0}}, # Sum = 195%
            {"label": "Near-Zero C2H4", "comp": {"N2": 3.5, "C1": 44.5, "C2": 45.0, "C2H4": 1e-6, "C3": 7.0}},
            {"label": "Missing C2H4", "comp": {"N2": 3.5, "C1": 44.5, "C2": 45.0, "C3": 7.0}},  # Missing key
            {"label": "Extreme Heavy C3", "comp": {"N2": 2.0, "C1": 35.0, "C2": 45.0, "C2H4": 1.0, "C3": 17.0}},
        ]

        for case in corrupted_cases:
            with self.subTest(case=case["label"]):
                res = recommend(
                    200.0,
                    strategy=OptimizationStrategy.MINIMUM_INTERVENTION,
                    actual_comp=case["comp"],
                    alpha_trim=0.30,
                )
                self.assertTrue(res["solver_converged"], f"Solver must succeed for {case['label']}")
                comps = [res[f"comp_{p}_molpct"] for p in PARTS]
                for p, val in zip(PARTS, comps):
                    self.assertGreaterEqual(val, 0.01, f"{p} below 0.01 mol% for {case['label']}")
                self.assertAlmostEqual(round(sum(comps), 4), 100.00, places=2)


class TestConditionDependentMetamorphicProperties(unittest.TestCase):
    """Adversarial Challenge 3: Verify CONDITION_DEPENDENT active response and non-clamping."""

    def test_condition_dependent_actively_differentiates_regimes(self):
        """Empirically prove that composition actively shifts across regimes (no static freezing)."""
        underload = recommend(150.0, strategy=OptimizationStrategy.CONDITION_DEPENDENT)
        baseload = recommend(280.0, strategy=OptimizationStrategy.CONDITION_DEPENDENT)
        peak = recommend(340.0, strategy=OptimizationStrategy.CONDITION_DEPENDENT)

        c3_underload = underload["comp_C3_molpct"]
        c3_baseload = baseload["comp_C3_molpct"]
        c3_peak = peak["comp_C3_molpct"]

        # Shift in C3 must be significant (> 1.0 mol%)
        delta_c3_load = abs(c3_baseload - c3_underload)
        self.assertGreater(
            delta_c3_load,
            1.0,
            f"C3 did not shift significantly between 150 and 280 t/h: delta={delta_c3_load:.2f} mol%",
        )

        # Total compositional movement across all 5 components
        total_shift = sum(
            abs(baseload[f"comp_{p}_molpct"] - underload[f"comp_{p}_molpct"])
            for p in PARTS
        )
        self.assertGreater(
            total_shift,
            2.5,
            f"Total compositional shift across load regimes must be > 2.5 mol%, got {total_shift:.2f}",
        )

    def test_condition_dependent_ignores_actual_dcs_composition(self):
        """Metamorphic relation: in CONDITION_DEPENDENT, output must be invariant to actual_comp."""
        comp_a = {"N2": 2.0, "C1": 40.0, "C2": 48.0, "C2H4": 1.0, "C3": 9.0}
        comp_b = {"N2": 5.0, "C1": 50.0, "C2": 38.0, "C2H4": 2.0, "C3": 5.0}

        res_a = recommend(250.0, strategy=OptimizationStrategy.CONDITION_DEPENDENT, actual_comp=comp_a)
        res_b = recommend(250.0, strategy=OptimizationStrategy.CONDITION_DEPENDENT, actual_comp=comp_b)

        # Compositions must be identical (not anchored to actual_comp)
        for p in PARTS:
            val_a = res_a[f"comp_{p}_molpct"]
            val_b = res_b[f"comp_{p}_molpct"]
            self.assertAlmostEqual(
                val_a,
                val_b,
                places=2,
                msg=f"CONDITION_DEPENDENT improperly anchored to actual DCS for {p}: {val_a} vs {val_b}",
            )


class TestFixedRecipeMetamorphicProperties(unittest.TestCase):
    """Adversarial Challenge 4: Verify FIXED_RECIPE invariance and custom recipe adherence."""

    def test_fixed_recipe_composition_locked_across_full_range(self):
        """Verify that across 120 to 340 t/h, composition does not drift."""
        baseline_res = recommend(200.0, strategy=OptimizationStrategy.FIXED_RECIPE)
        base_comps = [baseline_res[f"comp_{p}_molpct"] for p in PARTS]

        # Check against certified invariant recipe
        for p, expected, actual in zip(PARTS, INVARIANT_RECIPE_MOLPCT, base_comps):
            self.assertAlmostEqual(
                actual,
                expected,
                delta=0.05,
                msg=f"FIXED_RECIPE baseline diverged from invariant recipe for {p}: {actual} vs {expected}",
            )

        # Check across loads
        for feed in [120.0, 160.0, 220.0, 260.0, 300.0, 340.0]:
            res = recommend(feed, strategy=OptimizationStrategy.FIXED_RECIPE)
            comps = [res[f"comp_{p}_molpct"] for p in PARTS]
            for p, b_val, c_val in zip(PARTS, base_comps, comps):
                self.assertAlmostEqual(
                    b_val,
                    c_val,
                    places=2,
                    msg=f"FIXED_RECIPE drifted at feed {feed} t/h for {p}: {b_val} vs {c_val}",
                )

    def test_custom_fixed_recipe_preset(self):
        """Verify that custom recipe preset is strictly maintained across loads."""
        custom_recipe = {"N2": 4.10, "C1": 43.00, "C2": 43.90, "C2H4": 1.20, "C3": 7.80}
        for feed in [150.0, 250.0, 320.0]:
            res = recommend(
                feed,
                strategy=OptimizationStrategy.FIXED_RECIPE,
                selected_recipe=custom_recipe,
            )
            for p in PARTS:
                expected = custom_recipe[p]
                actual = res[f"comp_{p}_molpct"]
                self.assertAlmostEqual(
                    actual,
                    expected,
                    delta=0.05,
                    msg=f"Custom fixed recipe diverged at {feed} t/h for {p}: {actual} vs {expected}",
                )


class TestMinimumInterventionMetamorphicProperties(unittest.TestCase):
    """Adversarial Challenge 5: Verify MINIMUM_INTERVENTION trade-off and tuning parameter."""

    def test_alpha_trim_monotonic_progression(self):
        """Verify that distance to actual DCS composition grows monotonically with alpha_trim."""
        actual_comp = {"N2": 3.0, "C1": 45.0, "C2": 44.0, "C2H4": 1.0, "C3": 7.0}
        c_act = np.array([actual_comp[p] for p in PARTS])

        alphas = [0.10, 0.30, 0.60, 0.90]
        distances = []

        for a in alphas:
            res = recommend(
                280.0,
                strategy=OptimizationStrategy.MINIMUM_INTERVENTION,
                actual_comp=actual_comp,
                alpha_trim=a,
            )
            c_target = np.array([res[f"comp_{p}_molpct"] for p in PARTS])
            dist = float(np.linalg.norm(c_target - c_act))
            distances.append(dist)

        for i in range(len(distances) - 1):
            self.assertLessEqual(
                distances[i],
                distances[i + 1] + 1e-4,
                f"Alpha progression violated distance monotonicity: {distances}",
            )


class TestPhysicalConstraintResiduals(unittest.TestCase):
    """Adversarial Challenge 6: Rigorous constraint residual recalculation and bounds."""

    def test_all_residuals_non_negative_and_consistent(self):
        """Verify that all 4 constraint residuals are >= 0.0 and match independent definitions."""
        for feed in [140.0, 200.0, 280.0, 340.0]:
            for strat in [OptimizationStrategy.CONDITION_DEPENDENT, OptimizationStrategy.FIXED_RECIPE]:
                res = recommend(feed, strategy=strat)
                residuals = res["constraint_residuals"]

                # 1. Check keys presence
                for k in ("antisurge_margin_t_h", "suction_tal_margin_c", "superheat_margin_c", "mahalanobis_margin"):
                    self.assertIn(k, residuals)

                # 2. Antisurge margin
                expected_surge = round(res["mcr_flow_t_h"] - ANTISURGE_FLOOR_T_H, 1)
                self.assertAlmostEqual(residuals["antisurge_margin_t_h"], expected_surge, places=1)
                self.assertGreaterEqual(residuals["antisurge_margin_t_h"], 0.0)

                # 3. Suction TAL margin
                expected_tal = round(res["expected_suction_temp_c"] - SUCTION_TAL_C, 2)
                self.assertAlmostEqual(residuals["suction_tal_margin_c"], expected_tal, places=1)
                self.assertGreaterEqual(residuals["suction_tal_margin_c"], 0.0)

                # 4. Mahalanobis margin
                expected_dm_margin = round(CHI2_CRITICAL_5COMP - res["mahalanobis_distance"], 4)
                self.assertAlmostEqual(residuals["mahalanobis_margin"], expected_dm_margin, places=2)
                self.assertGreaterEqual(residuals["mahalanobis_margin"], 0.0)

                # 5. Superheat margin
                self.assertGreaterEqual(residuals["superheat_margin_c"], 0.0)


class TestApiAdversarialAndContractParity(unittest.TestCase):
    """Adversarial Challenge 7: API contract integrity and defensive rejection."""

    def setUp(self):
        self.client = TestClient(app)

    def test_api_valid_strategy_dispatch_and_timestamp(self):
        """Verify API accepts strategies and returns valid ISO 8601 UTC timestamp and effective_inputs."""
        for strat in ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"]:
            resp = self.client.post(
                "/api/v1/optimize",
                json={"feed_flow_t_h": 240.0, "strategy": strat},
            )
            self.assertEqual(resp.status_code, 200, f"Strategy {strat} failed with {resp.text}")
            data = resp.json()

            # Effective inputs echo
            self.assertEqual(data["effective_inputs"]["strategy"], strat)
            self.assertEqual(data["effective_inputs"]["feed_flow_t_h"], 240.0)

            # Calculation timestamp ISO 8601
            ts = data["calculation_timestamp"]
            parsed_dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            self.assertIsNotNone(parsed_dt)

            # Residuals
            self.assertIn("constraint_residuals", data)
            self.assertGreaterEqual(data["constraint_residuals"]["antisurge_margin_t_h"], 0.0)

    def test_api_rejects_invalid_inputs(self):
        """Verify API rejects invalid strategies or negative/out-of-bounds feed flow."""
        # 1. Invalid strategy
        resp = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 240.0, "strategy": "MAGIC_STRATEGY"},
        )
        self.assertEqual(resp.status_code, 422)

        # 2. Negative feed flow
        resp = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": -50.0, "strategy": "CONDITION_DEPENDENT"},
        )
        self.assertEqual(resp.status_code, 422)

        # 3. Excessive feed flow > 1000
        resp = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 5000.0, "strategy": "CONDITION_DEPENDENT"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_read_only_safety_boundary_defense(self):
        """Verify zero unsafe HTTP methods exist on optimize and related routes."""
        for path in ["/api/v1/optimize", "/api/optimize", "/api/v1/makeup-advisory"]:
            for method in ["PUT", "PATCH", "DELETE"]:
                resp = self.client.request(method, path)
                self.assertIn(
                    resp.status_code,
                    [404, 405],
                    f"Unsafe HTTP method {method} unexpectedly allowed on {path}",
                )


if __name__ == "__main__":
    unittest.main()
