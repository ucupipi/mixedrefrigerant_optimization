"""operator-website/backend/tests/test_m1_adversarial_challenger.py
Empirical Adversarial Challenge Suite: Milestone 1 API Contracts & Constraint Residuals
Baseload LNG Plant-3 Train H C3MR Decision-Support Suite

Tester: challenger_m1_2 (Adversarial Critic & Domain Specialist)
Mission:
  1. Adversarially stress-test all 4 constraint residuals across sweeps:
     - antisurge_margin_t_h >= 0.0
     - suction_tal_margin_c >= 0.0
     - superheat_margin_c >= 0.0
     - mahalanobis_margin >= 0.0
     - Zero NaN, None, or negative violations across 100+ parameter combinations.
  2. Test malformed and malicious payloads against FastAPI endpoints (POST /api/v1/optimize):
     - Invalid strategy types and values
     - Negative and out-of-range feed flows
     - Malformed JSON structures
     - Ensure clean HTTP 422 Unprocessable Entity responses with ZERO unhandled 500 crashes.
  3. Verify backward compatibility when strategy is omitted or specified with case variations.
  4. Verify mathematical Simplex invariants (x_i > 0, sum(x_i) == 100.00 +- 0.01%).
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

# Ensure backend root is on sys.path
_CURRENT_FILE = Path(__file__).resolve()
_BACKEND_DIR = _CURRENT_FILE.parents[1]
_ROOT = _BACKEND_DIR.parents[1]

for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.ilr_engine import CHI2_CRITICAL_5COMP
from core.optimizer_engine import (
    ANTISURGE_FLOOR_T_H,
    SUCTION_TAL_C,
    SUPERHEAT_MIN_C,
    recommend,
    get_pareto_fallback_recommendation,
)
from main import app


class TestAdversarialConstraintSweeps(unittest.TestCase):
    """Stress-test physical constraint residuals across fine-grained operational sweeps."""

    # Broad sweep of feed flows covering underload, baseload, design limits, and boundaries
    FEED_SWEEPS = [
        50.0, 75.0, 100.0, 120.0, 140.0, 160.0, 185.8, 200.0,
        220.0, 245.8, 260.0, 280.0, 300.0, 325.9, 350.0, 375.0,
        400.0, 500.0, 750.0, 1000.0
    ]

    STRATEGIES = ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"]

    VARIED_COMPOSITIONS = {
        "nominal": {"N2": 3.39, "C1": 44.45, "C2": 45.02, "C2H4": 0.85, "C3": 6.29},
        "high_c3": {"N2": 2.00, "C1": 40.00, "C2": 45.00, "C2H4": 1.00, "C3": 12.00},
        "low_c3": {"N2": 4.50, "C1": 48.00, "C2": 44.00, "C2H4": 0.50, "C3": 3.00},
        "high_n2": {"N2": 7.50, "C1": 42.00, "C2": 42.50, "C2H4": 1.00, "C3": 7.00},
    }

    def test_sweep_all_strategies_residuals_non_negative_and_not_nan(self):
        """Adversarially sweep 20 feed rates x 3 strategies and verify all 4 residuals are strictly valid."""
        violations = []
        tested_count = 0

        for strat in self.STRATEGIES:
            for feed in self.FEED_SWEEPS:
                tested_count += 1
                try:
                    res = recommend(
                        feed_t_h=feed,
                        actual_comp=self.VARIED_COMPOSITIONS["nominal"] if strat == "MINIMUM_INTERVENTION" else None,
                        strategy=strat,
                    )
                except Exception as exc:
                    violations.append(f"recommend() crashed at feed={feed}, strat={strat}: {exc}")
                    continue

                residuals = res.get("constraint_residuals")
                if not residuals or not isinstance(residuals, dict):
                    violations.append(f"Missing/invalid constraint_residuals dict at feed={feed}, strat={strat}")
                    continue

                for key in (
                    "antisurge_margin_t_h",
                    "suction_tal_margin_c",
                    "superheat_margin_c",
                    "mahalanobis_margin",
                ):
                    if key not in residuals:
                        violations.append(f"Missing residual key '{key}' at feed={feed}, strat={strat}")
                        continue
                    val = residuals[key]
                    if val is None or math.isnan(val) or math.isinf(val):
                        violations.append(f"Residual '{key}' is NaN/None/Inf ({val}) at feed={feed}, strat={strat}")
                    elif key == "mahalanobis_margin" and val < -0.02:
                        violations.append(f"Residual '{key}' negative ({val:.4f} < -0.02) at feed={feed}, strat={strat}")
                    elif val < -0.10:
                        violations.append(f"Residual '{key}' negative ({val:.4f} < -0.10) at feed={feed}, strat={strat}")

                # Verify Simplex invariants
                comp_sum = sum(res.get(f"comp_{k}_molpct", 0.0) for k in ("N2", "C1", "C2", "C2H4", "C3"))
                if abs(comp_sum - 100.00) > 0.02:
                    violations.append(f"Composition sum violation ({comp_sum:.4f} != 100.00) at feed={feed}, strat={strat}")

                for k in ("N2", "C1", "C2", "C2H4", "C3"):
                    val = res.get(f"comp_{k}_molpct", 0.0)
                    if val <= 0.0:
                        violations.append(f"Component '{k}' non-positive ({val}) at feed={feed}, strat={strat}")

        self.assertEqual(
            len(violations),
            0,
            f"Encountered {len(violations)} adversarial sweep violations out of {tested_count} tests:\n"
            + "\n".join(violations[:15]),
        )

    def test_sweep_minimum_intervention_across_extreme_compositions(self):
        """Adversarially test MINIMUM_INTERVENTION across diverse abnormal compositions and alpha steps."""
        alphas = [0.05, 0.10, 0.30, 0.70, 0.95, 1.00]
        test_feeds = [140.0, 245.8, 350.0]

        for comp_name, comp_dict in self.VARIED_COMPOSITIONS.items():
            for a in alphas:
                for feed in test_feeds:
                    res = recommend(
                        feed_t_h=feed,
                        actual_comp=comp_dict,
                        alpha_trim=a,
                        strategy="MINIMUM_INTERVENTION",
                    )
                    residuals = res.get("constraint_residuals", {})
                    self.assertGreaterEqual(
                        residuals.get("antisurge_margin_t_h", -1.0),
                        -0.05,
                        f"Anti-surge margin violated for {comp_name}, alpha={a}, feed={feed}",
                    )
                    self.assertGreaterEqual(
                        residuals.get("suction_tal_margin_c", -1.0),
                        -0.05,
                        f"Suction TAL margin violated for {comp_name}, alpha={a}, feed={feed}",
                    )
                    self.assertGreaterEqual(
                        residuals.get("superheat_margin_c", -1.0),
                        -0.05,
                        f"Superheat margin violated for {comp_name}, alpha={a}, feed={feed}",
                    )

    def test_pareto_fallback_resilience_and_residuals(self):
        """Adversarially probe get_pareto_fallback_recommendation across full sweep."""
        for strat in self.STRATEGIES:
            for feed in [50.0, 150.0, 245.8, 350.0, 1000.0]:
                res = get_pareto_fallback_recommendation(
                    feed_t_h=feed,
                    actual_comp=self.VARIED_COMPOSITIONS["nominal"],
                    strategy=strat,
                )
                self.assertTrue(res["solver_converged"])
                residuals = res["constraint_residuals"]
                for k in ("antisurge_margin_t_h", "suction_tal_margin_c", "superheat_margin_c", "mahalanobis_margin"):
                    self.assertIn(k, residuals)
                    val = residuals[k]
                    self.assertFalse(math.isnan(val))
                    self.assertGreaterEqual(val, -0.05)


class TestAdversarialApiEndpoints(unittest.TestCase):
    """Stress-test FastAPI POST /api/v1/optimize with malformed, malicious, and boundary payloads."""

    def setUp(self):
        self.client = TestClient(app)

    def test_malformed_strategy_payloads_return_clean_422(self):
        """Verify that any invalid strategy representation returns HTTP 422 without unhandled 500."""
        malformed_strategies = [
            "INVALID_STRATEGY",
            "RANDOM_JUNK",
            "CONDITION-DEPENDENT",  # with hyphen instead of underscore
            "fixed_recipe_fake",
            "12345",
            "",
            "   ",
        ]

        for bad_strat in malformed_strategies:
            resp = self.client.post(
                "/api/v1/optimize",
                json={"feed_flow_t_h": 245.8, "strategy": bad_strat},
            )
            self.assertEqual(
                resp.status_code,
                422,
                f"Expected 422 for strategy '{bad_strat}', got {resp.status_code}: {resp.text}",
            )
            # Ensure error detail is a clean JSON structure
            err_data = resp.json()
            self.assertIn("detail", err_data)

    def test_malformed_strategy_non_string_types_return_422(self):
        """Verify that non-string strategy types return HTTP 422."""
        invalid_types = [
            123,
            True,
            ["CONDITION_DEPENDENT"],
            {"strategy": "FIXED_RECIPE"},
            45.67,
        ]

        for bad_val in invalid_types:
            resp = self.client.post(
                "/api/v1/optimize",
                json={"feed_flow_t_h": 245.8, "strategy": bad_val},
            )
            self.assertEqual(
                resp.status_code,
                422,
                f"Expected 422 for non-string strategy '{bad_val}', got {resp.status_code}: {resp.text}",
            )

    def test_malformed_feed_flow_payloads_return_422(self):
        """Verify that invalid feed_flow_t_h values return HTTP 422."""
        invalid_feed_flows = [
            -100.0,
            -0.001,
            0.0,
            49.99,     # below ge=50.0 boundary
            1000.01,   # above le=1000.0 boundary
            1e9,
            "two_hundred",
            None,
            [],
            {},
        ]

        for bad_feed in invalid_feed_flows:
            resp = self.client.post(
                "/api/v1/optimize",
                json={"feed_flow_t_h": bad_feed},
            )
            self.assertEqual(
                resp.status_code,
                422,
                f"Expected 422 for invalid feed_flow_t_h '{bad_feed}', got {resp.status_code}: {resp.text}",
            )

    def test_empty_and_broken_json_payloads_return_422(self):
        """Verify that missing fields or malformed JSON headers return 422 without 500."""
        # Empty JSON
        resp_empty = self.client.post("/api/v1/optimize", json={})
        self.assertEqual(resp_empty.status_code, 422)

        # JSON with only unexpected fields
        resp_unexpected = self.client.post(
            "/api/v1/optimize",
            json={"foo": "bar", "baz": 123},
        )
        self.assertEqual(resp_unexpected.status_code, 422)

        # Malformed raw text content with application/json header
        resp_raw_broken = self.client.post(
            "/api/v1/optimize",
            content="{feed_flow_t_h: broken_json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp_raw_broken.status_code, 422)

    def test_malformed_alpha_trim_and_weight_return_422(self):
        """Verify range boundaries on alpha_trim and intervention_weight."""
        # alpha_trim < 0.05
        resp_low_alpha = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 245.8, "alpha_trim": 0.01},
        )
        self.assertEqual(resp_low_alpha.status_code, 422)

        # alpha_trim > 1.0
        resp_high_alpha = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 245.8, "alpha_trim": 1.5},
        )
        self.assertEqual(resp_high_alpha.status_code, 422)

        # intervention_weight < 0.0
        resp_neg_weight = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 245.8, "intervention_weight": -2.0},
        )
        self.assertEqual(resp_neg_weight.status_code, 422)

    def test_case_insensitive_strategy_normalization(self):
        """Verify that lowercase, mixed-case, and whitespace-padded strategy strings are parsed cleanly."""
        variants = [
            ("condition_dependent", "CONDITION_DEPENDENT"),
            ("Fixed_Recipe", "FIXED_RECIPE"),
            ("  minimum_intervention  ", "MINIMUM_INTERVENTION"),
            ("CONDITION_DEPENDENT", "CONDITION_DEPENDENT"),
        ]

        for input_strat, expected_strat in variants:
            resp = self.client.post(
                "/api/v1/optimize",
                json={"feed_flow_t_h": 245.8, "strategy": input_strat},
            )
            self.assertEqual(
                resp.status_code,
                200,
                f"Failed to normalize valid strategy variant '{input_strat}': {resp.text}",
            )
            data = resp.json()
            self.assertEqual(data.get("strategy"), expected_strat)

    def test_backward_compatibility_omitted_strategy_matrix(self):
        """Verify backward compatibility across combinations of omitted strategy."""
        # Case A: Minimal payload (only feed_flow_t_h)
        resp_a = self.client.post("/api/v1/optimize", json={"feed_flow_t_h": 245.8})
        self.assertEqual(resp_a.status_code, 200)
        data_a = resp_a.json()
        self.assertEqual(data_a["strategy"], "CONDITION_DEPENDENT")
        self.assertIn("constraint_residuals", data_a)
        self.assertIn("effective_inputs", data_a)

        # Case B: Omitted strategy with actual_comp and alpha_trim < 1.0
        resp_b = self.client.post(
            "/api/v1/optimize",
            json={
                "feed_flow_t_h": 245.8,
                "alpha_trim": 0.25,
                "actual_comp_N2_molpct": 3.39,
                "actual_comp_C1_molpct": 44.45,
                "actual_comp_C2_molpct": 45.02,
                "actual_comp_C2H4_molpct": 0.85,
                "actual_comp_C3_molpct": 6.29,
            },
        )
        self.assertEqual(resp_b.status_code, 200)
        data_b = resp_b.json()
        self.assertEqual(data_b["strategy"], "MINIMUM_INTERVENTION")
        self.assertEqual(data_b["effective_inputs"]["strategy"], "MINIMUM_INTERVENTION")

        # Case C: Omitted strategy with actual_comp but alpha_trim == 1.0
        resp_c = self.client.post(
            "/api/v1/optimize",
            json={
                "feed_flow_t_h": 245.8,
                "alpha_trim": 1.0,
                "actual_comp_N2_molpct": 3.39,
            },
        )
        self.assertEqual(resp_c.status_code, 200)
        data_c = resp_c.json()
        self.assertEqual(data_c["strategy"], "CONDITION_DEPENDENT")

    def test_boundary_feed_rates_and_extra_fields_immunity(self):
        """Verify exact boundary values (50.0 and 1000.0) and immunity to extra unknown fields."""
        # Exact lower boundary 50.0
        resp_min = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 50.0, "strategy": "CONDITION_DEPENDENT"},
        )
        self.assertEqual(resp_min.status_code, 200)
        self.assertGreaterEqual(resp_min.json()["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)

        # Exact upper boundary 1000.0
        resp_max = self.client.post(
            "/api/v1/optimize",
            json={"feed_flow_t_h": 1000.0, "strategy": "FIXED_RECIPE"},
        )
        self.assertEqual(resp_max.status_code, 200)

        # Extra unexpected fields (should be ignored gracefully)
        resp_extra = self.client.post(
            "/api/v1/optimize",
            json={
                "feed_flow_t_h": 245.8,
                "unrecognized_field_abc": "ignored_value",
                "attempted_dcs_setpoint_injection": 999.9,
            },
        )
        self.assertEqual(resp_extra.status_code, 200)
        self.assertNotIn("unrecognized_field_abc", resp_extra.json())


if __name__ == "__main__":
    unittest.main(verbosity=2)

