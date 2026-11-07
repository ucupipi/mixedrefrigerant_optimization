"""operator-website/backend/tests/test_adversarial_m2_extended.py
Extended Adversarial Fuzzing and Stress Harness for Milestone 2.
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2.

Empirical verification of:
1. Extreme loop inventories (microscopic 1.0 kg, small 10.0 kg, huge 1e8 kg, float limits).
2. Extreme duration parameters (sub-threshold, upper limits, zero/negative, NaN, Inf).
3. Corrupted nested types (nested dicts, lists, complex, strings, boolean components).
4. Edge-case compositions (zero actual concentration, zero target, near 100% single component).
5. Degenerate and singular stream purity matrix fallback.
6. Strict NOT EVALUATED contract returning None (null) and NEVER false zeros (0.0).
7. JSON serialization verification confirming null flows in output JSON payload.
8. Alternate C1 DCS tag switching (H4FIC005 vs H4FIC009).
9. API Endpoint fuzzing across /api/v1/makeup-advisory and /api/makeup-advisory.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
import unittest
from typing import Any, Dict

import numpy as np
from fastapi.testclient import TestClient

_CURRENT_FILE = Path(__file__).resolve()
_BACKEND_DIR = _CURRENT_FILE.parents[1]
_ROOT = _BACKEND_DIR.parents[1]
for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.makeup_calculator import (
    DEFAULT_STREAM_PURITY_MATRIX,
    ESTIMATED_MCR_LOOP_INVENTORY_KG,
    MW_COMPONENTS,
    NORMAL_MOLAR_VOLUME_NM3_PER_KMOL,
    SCFD_PER_NM3_H,
    TAG_MAKEUP_CONTROLLERS,
    calculate_makeup_recommendations,
    validate_makeup_inputs,
)
from api.schemas import MakeupAdvisoryRequest, MakeupAdvisoryResponse
from main import app


class TestExtendedAdversarialFuzzing(unittest.TestCase):
    """Extended adversarial stress harness for makeup calculator."""

    def setUp(self):
        self.valid_act = {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C3": 6.28, "C2H4": 1.03}
        self.valid_tgt = {"N2": 3.80, "C1": 45.00, "C2": 44.00, "C3": 6.20, "C2H4": 1.00}
        self.client = TestClient(app)

    def _assert_strict_not_evaluated(self, res: Dict[str, Any], context: str):
        self.assertEqual(res["status"], "NOT EVALUATED", f"{context}: status must be NOT EVALUATED")
        self.assertIsNone(res["total_makeup_flow_nm3_h"], f"{context}: total nm3/h must be None")
        self.assertIsNone(res["total_makeup_flow_kg_h"], f"{context}: total kg/h must be None")
        self.assertIsNone(res["total_makeup_flow_t_h"], f"{context}: total t/h must be None")
        self.assertIsNone(res["total_makeup_flow_scfd"], f"{context}: total scfd must be None")
        self.assertIsNone(res["initial_moles_kmol"], f"{context}: initial_moles must be None")
        self.assertIsNone(res["final_moles_kmol"], f"{context}: final_moles must be None")
        self.assertIsNone(res["expansion_ratio"], f"{context}: expansion_ratio must be None")
        for item in res["items"]:
            self.assertEqual(item["action"], "TIDAK DAPAT DIEVALUASI")
            self.assertIsNone(item["recommended_flow_nm3_h"])
            self.assertIsNone(item["recommended_flow_kg_h"])
            self.assertIsNone(item["recommended_flow_t_h"])
            self.assertIsNone(item["recommended_flow_scfd"])
            self.assertIsNone(item["needed_kmol"])
            self.assertIsNone(item["needed_kg"])

    # 1. Corrupted nested types in components
    def test_corrupted_nested_dictionary(self):
        """Nested dictionary inside a component value must trigger NOT EVALUATED without unhandled exception."""
        corrupted = dict(self.valid_act)
        corrupted["N2"] = {"nested": 12.3}
        res = calculate_makeup_recommendations(corrupted, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "nested dict in N2")

    def test_corrupted_nested_list(self):
        """List inside component value must trigger NOT EVALUATED."""
        corrupted = dict(self.valid_act)
        corrupted["C1"] = [44.37, 45.0]
        res = calculate_makeup_recommendations(corrupted, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "list in C1")

    def test_corrupted_boolean_in_components(self):
        """Boolean True/False (which is a subclass of int in Python) must trigger NOT EVALUATED."""
        corrupted_act = dict(self.valid_act)
        corrupted_act["C2"] = True
        res = calculate_makeup_recommendations(corrupted_act, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "boolean True in actual C2")

        corrupted_tgt = dict(self.valid_tgt)
        corrupted_tgt["C3"] = False
        res2 = calculate_makeup_recommendations(self.valid_act, corrupted_tgt)
        self._assert_strict_not_evaluated(res2, "boolean False in target C3")

    def test_corrupted_complex_number(self):
        """Complex number in component value must trigger NOT EVALUATED without crashing."""
        corrupted = dict(self.valid_act)
        corrupted["N2"] = 3.5 + 2j
        res = calculate_makeup_recommendations(corrupted, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "complex number in N2")

    def test_corrupted_none_in_component_value(self):
        """None value inside component dict must trigger NOT EVALUATED."""
        corrupted = dict(self.valid_act)
        corrupted["C1"] = None
        res = calculate_makeup_recommendations(corrupted, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "None in C1")

    def test_corrupted_unicode_string(self):
        """Unicode characters in component values must trigger NOT EVALUATED."""
        corrupted = dict(self.valid_act)
        corrupted["N2"] = "\u4e09\u70b9\u4e94"  # Chinese characters
        res = calculate_makeup_recommendations(corrupted, self.valid_tgt)
        self._assert_strict_not_evaluated(res, "unicode string in N2")

    # 2. Extreme loop inventories
    def test_extreme_astronomical_inventory(self):
        """Astronomical loop inventory (1e8 kg = 100,000 tons) must evaluate without overflow or crash."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, inventory_kg=1e8, transition_hours=2.0
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["total_makeup_flow_kg_h"], 0.0)
        self.assertFalse(math.isnan(res["total_makeup_flow_kg_h"]))
        self.assertFalse(math.isinf(res["total_makeup_flow_kg_h"]))

    def test_extreme_microscopic_inventory(self):
        """Microscopic loop inventory (1.0 kg) calculates without crash and yields non-negative rates."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, inventory_kg=1.0, transition_hours=2.0
        )
        self.assertEqual(res["status"], "EVALUATED")
        # In small inventory, scfd captures small volumetric rates accurately
        self.assertGreater(res["total_makeup_flow_scfd"], 0.0)
        # Rates are non-negative
        self.assertGreaterEqual(res["total_makeup_flow_kg_h"], 0.0)
        self.assertGreaterEqual(res["total_makeup_flow_nm3_h"], 0.0)

    def test_extreme_small_scale_inventory(self):
        """Small pilot inventory (10.0 kg) must evaluate with positive rates across all units."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, inventory_kg=10.0, transition_hours=2.0
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["total_makeup_flow_kg_h"], 0.0)
        self.assertGreater(res["total_makeup_flow_scfd"], 0.0)

    def test_inventory_overflow_float(self):
        """Near overflow float (1e308) in inventory_kg must either evaluate or return NOT EVALUATED without unhandled exception."""
        try:
            res = calculate_makeup_recommendations(
                self.valid_act, self.valid_tgt, inventory_kg=1e308
            )
            self.assertIn(res["status"], ["EVALUATED", "NOT EVALUATED"])
        except Exception as e:
            self.fail(f"Unhandled exception with huge inventory: {e}")

    # 3. Extreme durations
    def test_clamped_short_duration(self):
        """Sub-threshold duration (0.1 h) passed directly is clamped to 0.5 h and evaluated safely."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, transition_hours=0.1
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertEqual(res["transition_hours"], 0.5)

    def test_extreme_long_duration(self):
        """Long duration (1000.0 hours) evaluates cleanly with small hourly rates."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, transition_hours=1000.0
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["total_makeup_flow_nm3_h"], 0.0)
        self.assertLess(res["total_makeup_flow_nm3_h"], 10.0)

    # 4. Zero actual concentration / Zero target concentration
    def test_zero_actual_concentration_for_deficit_component(self):
        """Actual concentration of N2 is 0.00 mol%, target is 5.0 mol%.
        Should evaluate cleanly with N2 injection and closed-loop molar balance."""
        act_zero_n2 = {"N2": 0.0, "C1": 47.0, "C2": 45.0, "C3": 7.0, "C2H4": 1.0}
        tgt = {"N2": 5.0, "C1": 44.5, "C2": 43.0, "C3": 6.5, "C2H4": 1.0}
        res = calculate_makeup_recommendations(act_zero_n2, tgt)
        self.assertEqual(res["status"], "EVALUATED")
        n2_item = next(it for it in res["items"] if it["component"] == "N2")
        self.assertEqual(n2_item["action"], "INJEKSI")
        self.assertGreater(n2_item["recommended_flow_nm3_h"], 0.0)

    def test_zero_target_concentration_for_excess_component(self):
        """Target concentration of N2 is 0.0 mol% (unrealistic in plant, but adversarial).
        Should evaluate without division by zero or NaN."""
        act = {"N2": 3.0, "C1": 46.0, "C2": 44.0, "C3": 6.0, "C2H4": 1.0}
        tgt = {"N2": 0.0, "C1": 47.5, "C2": 45.5, "C3": 6.0, "C2H4": 1.0}
        res = calculate_makeup_recommendations(act, tgt)
        self.assertEqual(res["status"], "EVALUATED")
        n2_item = next(it for it in res["items"] if it["component"] == "N2")
        # N2 cannot be injected; it is held on standby / stop
        self.assertEqual(n2_item["action"], "TAHAN / STOP")
        self.assertEqual(n2_item["recommended_flow_nm3_h"], 0.0)

    # 5. Singular / degenerate stream purity matrix fallback
    def test_singular_purity_matrix_fallback(self):
        """If a singular purity matrix is passed, calculator must fall back to identity matrix without crashing."""
        singular_matrix = {
            "N2": {"N2": 1.0, "C1": 0.0, "C2": 0.0, "C2H4": 0.0, "C3": 0.0},
            "C1": {"N2": 1.0, "C1": 0.0, "C2": 0.0, "C2H4": 0.0, "C3": 0.0},  # identical column -> singular
            "C2": {"N2": 0.0, "C1": 0.0, "C2": 1.0, "C2H4": 0.0, "C3": 0.0},
            "C3": {"N2": 0.0, "C1": 0.0, "C2": 0.0, "C2H4": 0.0, "C3": 1.0},
            "C2H4": {"N2": 0.0, "C1": 0.0, "C2": 0.0, "C2H4": 1.0, "C3": 0.0},
        }
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, purity_matrix=singular_matrix
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["total_makeup_flow_nm3_h"], 0.0)

    # 6. Extreme near 100% single component
    def test_extreme_near_100_percent_single_component(self):
        """Actual is 96% C1, target has N2 deficiency."""
        act = {"N2": 0.1, "C1": 96.0, "C2": 2.0, "C3": 1.5, "C2H4": 0.4}
        tgt = {"N2": 4.0, "C1": 91.0, "C2": 3.0, "C3": 1.6, "C2H4": 0.4}
        res = calculate_makeup_recommendations(act, tgt)
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["expansion_ratio"], 1.0)
        self.assertGreater(res["total_makeup_flow_nm3_h"], 0.0)

    # 7. Alternate C1 DCS Tag (H4FIC005 vs H4FIC009)
    def test_alternate_c1_dcs_tag(self):
        """Verify that selecting c1_tag='H4FIC009' correctly routes the controller tag."""
        res = calculate_makeup_recommendations(
            self.valid_act, self.valid_tgt, c1_tag="H4FIC009"
        )
        self.assertEqual(res["status"], "EVALUATED")
        c1_item = next(it for it in res["items"] if it["component"] == "C1")
        self.assertEqual(c1_item["tag_dcs"], "H4FIC009")

    # 8. Strict JSON serialization null checks (Zero false zeros in wire protocol)
    def test_strict_json_null_serialization_wire_contract(self):
        """Verify that in the JSON wire payload, unevaluated flows are explicitly null (NOT 0.0)."""
        res = calculate_makeup_recommendations(None, None)
        response_model = MakeupAdvisoryResponse(**res)
        json_str = response_model.model_dump_json()
        parsed = json.loads(json_str)

        self.assertEqual(parsed["status"], "NOT EVALUATED")
        self.assertIsNone(parsed["total_makeup_flow_nm3_h"])
        self.assertIsNone(parsed["total_makeup_flow_kg_h"])
        self.assertIsNone(parsed["total_makeup_flow_t_h"])
        self.assertIsNone(parsed["total_makeup_flow_scfd"])

        for rec in parsed["recommendations"]:
            self.assertEqual(rec["action"], "TIDAK DAPAT DIEVALUASI")
            self.assertIsNone(rec["recommended_flow_nm3_h"])
            self.assertIsNone(rec["recommended_flow_kg_h"])
            self.assertIsNone(rec["recommended_flow_t_h"])
            self.assertIsNone(rec["recommended_flow_scfd"])
            self.assertIsNone(rec["needed_kmol"])
            self.assertIsNone(rec["needed_kg"])

    # 9. Additional API Fuzzing
    def test_api_fuzzing_nested_corrupted_payload(self):
        """API receiving nested dictionary in component returns 422 Unprocessable Content."""
        payload = {
            "actual_comp": {"N2": {"nested": "corrupt"}, "C1": 44.0, "C2": 45.0, "C3": 7.0, "C2H4": 1.0},
            "target_comp": self.valid_tgt,
        }
        resp = self.client.post("/api/v1/makeup-advisory", json=payload)
        self.assertEqual(resp.status_code, 422)

    def test_api_fuzzing_infinite_inventory(self):
        """API receiving infinity in inventory returns 422 or 200 with NOT EVALUATED."""
        payload = {
            "actual_comp": self.valid_act,
            "target_comp": self.valid_tgt,
            "inventory_kg": "Infinity",
        }
        resp = self.client.post("/api/v1/makeup-advisory", json=payload)
        self.assertIn(resp.status_code, [422, 200])
        if resp.status_code == 200:
            self.assertEqual(resp.json()["status"], "NOT EVALUATED")

    def test_api_fuzzing_nan_transition_hours(self):
        """API receiving NaN transition hours returns 422 or 200 with NOT EVALUATED."""
        payload = {
            "actual_comp": self.valid_act,
            "target_comp": self.valid_tgt,
            "transition_hours": "NaN",
        }
        resp = self.client.post("/api/v1/makeup-advisory", json=payload)
        self.assertIn(resp.status_code, [422, 200])
        if resp.status_code == 200:
            self.assertEqual(resp.json()["status"], "NOT EVALUATED")

    def test_api_fuzzing_unexpected_extra_keys(self):
        """API receiving unknown extra keys ignores them or handles gracefully."""
        payload = {
            "actual_comp": self.valid_act,
            "target_comp": self.valid_tgt,
            "unknown_bogus_key_123": "unexpected_value",
            "another_extra_field": 999.9,
        }
        resp = self.client.post("/api/v1/makeup-advisory", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "EVALUATED")


if __name__ == "__main__":
    unittest.main()
