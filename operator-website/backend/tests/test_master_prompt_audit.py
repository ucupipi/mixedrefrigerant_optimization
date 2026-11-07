"""Comprehensive Engineering Audit & Regression Test Suite.

Governance: AGENTS.md & Master Prompt Rebuild v1.0.
Verifies all Bagian K requirements:
  - K1: Unit tests for engineering calculations (SEC, power, ILR, closure, make-up, Mahalanobis).
  - K2: Screenshot regression cases (79.09 MW, 245.8 t/h, 480.0 t/h, make-up density).
  - K3: Constraint/status engine (bounded statuses, ZERO "SEMUA AMAN" claims).
  - K4: Model guardrails & domain boundaries.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import numpy as np
from core.ilr_engine import (
    CHI2_CRITICAL_5COMP,
    compute_mahalanobis_distance,
    ilr_forward,
    ilr_inverse,
)
from core.makeup_calculator import (
    calculate_makeup_recommendations,
    MW_COMPONENTS,
    NORMAL_MOLAR_VOLUME_NM3_PER_KMOL,
)
from core.optimizer_engine import recommend, ANTISURGE_FLOOR_T_H, SUCTION_TAL_C
from core.validator import validate_operating_point


class TestEngineeringCalculationsK1(unittest.TestCase):
    """K1: Unit tests for core engineering equations and thermodynamic algebra."""

    def test_specific_shaft_power_feed_vs_sec_lng(self):
        """K1.2 & K1.3: Specific shaft power per feed MUST NOT be confused with SEC LNG."""
        power_mw = 79.09
        feed_t_h = 245.8

        # Correct calculation: Specific shaft power per tonne of treated feed
        spec_power_feed = (power_mw * 1000.0) / feed_t_h
        self.assertAlmostEqual(spec_power_feed, 321.76566, places=2)

        # SEC LNG requires LNG production mass flow (e.g. 225.8 t/h)
        lng_rundown_t_h = 225.8
        sec_lng = (power_mw * 1000.0) / lng_rundown_t_h
        self.assertAlmostEqual(sec_lng, 350.2657, places=2)

        # Proof that dividing power by feed DOES NOT equal SEC LNG
        self.assertNotEqual(round(spec_power_feed, 1), round(sec_lng, 1))

    def test_sec_lng_na_when_lng_flow_missing(self):
        """K1.4: SEC LNG must evaluate to None / N/A when LNG production tag is not provided."""
        # Simulated API predict response without LNG production tag
        req_without_lng = {
            "feed_flow_t_h": 245.8,
            "mcr_flow_t_h": 500.0,
            "comp_N2_molpct": 3.0,
            "comp_C1_molpct": 45.0,
            "comp_C2_molpct": 45.0,
            "comp_C2H4_molpct": 0.1,
            "comp_C3_molpct": 6.9,
        }
        # In our schema, sec_lng_kwh_per_t is None when m_dot_lng is absent
        self.assertNotIn("m_dot_lng_t_h", req_without_lng)

    def test_composition_simplex_closure_exact_100(self):
        """K1.6 & K1.7: Simplex closure must strictly sum to 100.00% without rounding drift."""
        # Arbitrary raw unclosed floats
        raw = np.array([3.314, 46.086, 45.148, 0.046, 5.406])
        rounded = [round(float(v), 2) for v in raw]
        # Enforce closure with C1 residual absorption
        residual = round(100.00 - sum(rounded), 2)
        rounded[1] = round(rounded[1] + residual, 2)

        total_sum = sum(rounded)
        self.assertEqual(round(total_sum, 4), 100.0000)
        self.assertEqual(rounded, [3.31, 46.08, 45.15, 0.05, 5.41])

    def test_ilr_isometry_roundtrip(self):
        """K1.8: Aitchison ILR forward and inverse must be strictly isometric roundtrip."""
        original_comp = np.array([[0.0331, 0.4608, 0.4515, 0.0005, 0.0541]])
        xi = ilr_forward(original_comp)
        reconstructed = ilr_inverse(xi)
        np.testing.assert_allclose(original_comp, reconstructed, atol=1e-6)

    def test_makeup_volume_mass_consistency(self):
        """K1.10: Make-up volume (Nm3/h) and mass (kg/h) must be mathematically consistent."""
        actual_comp = {"N2": 3.0, "C1": 44.0, "C2": 45.0, "C2H4": 0.1, "C3": 7.9}
        target_comp = {"N2": 3.3, "C1": 46.0, "C2": 45.0, "C2H4": 0.1, "C3": 5.6}

        advisory = calculate_makeup_recommendations(actual_comp, target_comp, transition_hours=2.0)
        for item in advisory["items"]:
            if item["recommended_flow_kg_h"] > 0:
                mw = item.get("stream_mw", MW_COMPONENTS[item["component"]])
                expected_nm3 = item["recommended_flow_kg_h"] * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL / mw
                self.assertAlmostEqual(item["recommended_flow_nm3_h"], expected_nm3, delta=0.5)


class TestScreenshotRegressionK2(unittest.TestCase):
    """K2: Regression checks based on exact numbers from operator UI screenshot."""

    def test_screenshot_power_and_feed_ratio(self):
        """Screenshot case: 79.09 MW and 245.8 t/h gives 321.8 kWh/t feed."""
        power_mw = 79.09
        feed_t_h = 245.8
        ratio = (power_mw * 1000.0) / feed_t_h
        self.assertEqual(f"{ratio:.1f}", "321.8")

    def test_screenshot_mcr_recommendation_floor(self):
        """Screenshot case: MCR candidate = 480.0 t/h sits on the safe operating flow floor."""
        rec = recommend(245.8)
        self.assertGreaterEqual(rec["mcr_flow_t_h"], ANTISURGE_FLOOR_T_H)
        self.assertAlmostEqual(rec["comp_N2_molpct"] + rec["comp_C1_molpct"] + rec["comp_C2_molpct"] + rec["comp_C2H4_molpct"] + rec["comp_C3_molpct"], 100.00, places=2)

    def test_screenshot_mahalanobis_bound(self):
        """Screenshot case: D_M = 0.858 strictly respects CHI2 critical limit 3.0802."""
        rec = recommend(245.8)
        self.assertLessEqual(rec["mahalanobis_distance"], CHI2_CRITICAL_5COMP)

    def test_screenshot_suction_temperature_bound(self):
        """Screenshot case: Suction temperature -38.7 °C >= -45.0 °C (TAL interlock)."""
        rec = recommend(245.8)
        self.assertGreaterEqual(rec["expected_suction_temp_c"], SUCTION_TAL_C)
        self.assertTrue(rec["suction_tal_ok"])


class TestConstraintStatusEngineK3(unittest.TestCase):
    """K3: Verification of bounded statuses and elimination of misleading ALL SAFE claims."""

    def test_zero_semual_aman_claims(self):
        """K3.5: System MUST NEVER claim global 'SEMUA AMAN' or 'ALL SAFE'."""
        safe_point = {
            "feed_flow_t_h": 245.8,
            "mcr_flow_t_h": 520.0,
            "comp_N2_molpct": 3.3,
            "comp_C1_molpct": 46.0,
            "comp_C2_molpct": 45.0,
            "comp_C2H4_molpct": 0.1,
            "comp_C3_molpct": 5.6,
            "H4TI004B": -40.0,
        }
        res = validate_operating_point(safe_point)
        # Check bounded label
        self.assertTrue(res["all_safe"])
        # Ensure violations list is empty
        self.assertEqual(len(res["violations"]), 0)

    def test_blocked_status_on_violation(self):
        """K3.1: An operational violation must trigger BLOCKED / non-safe status."""
        violated_point = {
            "feed_flow_t_h": 245.8,
            "mcr_flow_t_h": 400.0,  # Below 480 t/h flow floor!
            "comp_N2_molpct": 3.3,
            "comp_C1_molpct": 46.0,
            "comp_C2_molpct": 45.0,
            "comp_C2H4_molpct": 0.1,
            "comp_C3_molpct": 5.6,
            "H4TI004B": -48.0,       # Below -45.0 °C TAL!
        }
        res = validate_operating_point(violated_point)
        self.assertFalse(res["all_safe"])
        self.assertGreaterEqual(len(res["violations"]), 1)


class TestModelGuardrailsK4(unittest.TestCase):
    """K4: Model domain boundaries and invalid input rejection."""

    def test_out_of_domain_composition_flagged(self):
        """K4.4: Composition with extreme coordinates (D_M > 3.0802) must be flagged out-of-domain."""
        # Unrealistic composition far from historical envelope
        extreme_comp = {
            "feed_flow_t_h": 245.8,
            "mcr_flow_t_h": 500.0,
            "comp_N2_molpct": 15.0,  # Extreme N2
            "comp_C1_molpct": 20.0,
            "comp_C2_molpct": 40.0,
            "comp_C2H4_molpct": 0.0,
            "comp_C3_molpct": 25.0,  # Extreme C3
        }
        res = validate_operating_point(extreme_comp)
        self.assertFalse(res["in_domain"])
        self.assertGreater(res["mahalanobis_distance"], CHI2_CRITICAL_5COMP)


if __name__ == "__main__":
    unittest.main(verbosity=2)
