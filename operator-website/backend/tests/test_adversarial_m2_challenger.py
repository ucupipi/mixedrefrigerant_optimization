"""operator-website/backend/tests/test_adversarial_m2_challenger.py
Milestone 2 Adversarial Empirical Stress Suite & Metamorphic Oracle
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Authored by challenger_m2 (Role: critic, specialist)
Adversarial stress-testing of:
  - operator-website/backend/core/makeup_calculator.py
  - operator-website/backend/api/schemas.py
  - operator-website/backend/api/routes.py

Challenge Dimensions:
  1. Edge-Case Targets:
     - Target identical to actual: zero make-up additions, actions in (STABIL / SEIMBANG, TAHAN / STOP), no INJEKSI.
     - Sub-threshold deltas (delta_pct <= 0.02%): no injection triggered.
  2. Extreme Make-Up Conditions:
     - Large N2 deficiency (e.g. actual N2 = 0.5%, target N2 = 8.0%).
     - Large C3 deficiency (e.g. actual C3 = 1.0%, target C3 = 10.0%).
     - Multi-component deficiency with non-negative flows and closed-loop molar conservation.
     - Inverted extreme distributions.
  3. Degenerate Inputs & Strict NOT EVALUATED Contract:
     - Empty dicts, None values, zero/negative/NaN/inf inventory and transition hours.
     - Negative mole fractions and unphysical sums.
     - Strict return of status = "NOT EVALUATED" and None (null) for all flow fields (NO false zeros 0.0).
  4. API Endpoint /api/v1/makeup-advisory & Malformed Payloads:
     - Valid inputs return 200 with complete schema.
     - Empty inputs return 200 with NOT EVALUATED status.
     - Malformed payloads (type mismatch, range violations ge=0.5, le=24, gt=0) return clean 422 Unprocessable Entity.
  5. Read-Only Advisory Guarantees & Safety:
     - All instructions prefixed with [ADVISORY].
     - Zero industrial control write commands or automated actuation.
  6. Metamorphic Dual Unit Invariants:
     - Strict physical conversion between mass (kg/h, t/h) and volumetric (Nm3/h, scfd) rates.
     - Metamorphic conservation across duration and inventory scaling.

Compliance: AGENTS.md (Pasal 1-13), ORIGINAL_REQUEST.md (§R3, §R4).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
import unittest
from typing import Any, Dict

import numpy as np
from fastapi.testclient import TestClient

# Resolve paths
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
from api.schemas import (
    MakeupAdvisoryRequest,
    MakeupAdvisoryResponse,
    MakeupComponentRecommendation,
)
from main import app


class TestAdversarialEdgeCaseTargets(unittest.TestCase):
    """Dimension 1: Edge-case targets (identical target to actual, sub-threshold deltas)."""

    def setUp(self):
        self.actual_comp = {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C3": 6.28, "C2H4": 1.03}

    def test_identical_target_yields_zero_makeup_additions(self):
        """When target is identical to actual, all additions must be zero and no component is injected."""
        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=dict(self.actual_comp),
            transition_hours=2.0,
            inventory_kg=24000.0,
            use_stream_purity=True,
        )

        self.assertEqual(res["status"], "EVALUATED")
        self.assertAlmostEqual(res["expansion_ratio"], 1.0, places=4)
        self.assertEqual(res["total_makeup_flow_nm3_h"], 0.0)
        self.assertEqual(res["total_makeup_flow_kg_h"], 0.0)
        self.assertEqual(res["total_makeup_flow_t_h"], 0.0)
        self.assertEqual(res["total_makeup_flow_scfd"], 0.0)

        for item in res["items"]:
            # Action must be STABIL / SEIMBANG or TAHAN / STOP, never INJEKSI
            self.assertIn(item["action"], ["STABIL / SEIMBANG", "TAHAN / STOP"])
            self.assertNotEqual(item["action"], "INJEKSI")
            self.assertEqual(item["needed_kmol"], 0.0)
            self.assertEqual(item["needed_kg"], 0.0)
            self.assertEqual(item["recommended_flow_nm3_h"], 0.0)
            self.assertEqual(item["recommended_flow_kg_h"], 0.0)
            self.assertEqual(item["recommended_flow_t_h"], 0.0)
            self.assertEqual(item["recommended_flow_scfd"], 0.0)

    def test_sub_threshold_positive_delta_does_not_trigger_injection(self):
        """A tiny delta (+0.01 mol%) is within noise/threshold (<= 0.02%) and must not trigger injection."""
        target_comp = dict(self.actual_comp)
        target_comp["N2"] += 0.01  # delta = +0.01%
        target_comp["C1"] -= 0.01  # compensate

        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=target_comp,
            transition_hours=2.0,
            inventory_kg=24000.0,
        )

        self.assertEqual(res["status"], "EVALUATED")
        n2_item = next(it for it in res["items"] if it["component"] == "N2")
        self.assertNotEqual(n2_item["action"], "INJEKSI")
        self.assertEqual(n2_item["recommended_flow_nm3_h"], 0.0)
        self.assertEqual(n2_item["recommended_flow_kg_h"], 0.0)

    def test_all_components_in_excess_or_balanced(self):
        """When all components are slightly in excess or balanced, no injection occurs."""
        target_comp = {k: v - 0.1 for k, v in self.actual_comp.items()}
        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=target_comp,
            transition_hours=2.0,
        )
        self.assertEqual(res["status"], "EVALUATED")
        for item in res["items"]:
            self.assertNotEqual(item["action"], "INJEKSI")
            self.assertEqual(item["recommended_flow_nm3_h"], 0.0)


class TestAdversarialExtremeMakeup(unittest.TestCase):
    """Dimension 2: Extreme make-up scenarios (large deficiencies, non-negativity, conservation)."""

    def setUp(self):
        self.inv_kg = 24000.0
        self.t_hours = 2.0

    def test_extreme_n2_deficiency_conservation_and_non_negativity(self):
        """Test massive N2 deficiency (actual N2 = 0.5%, target N2 = 8.0%).

        Verifies non-negative flow across all controllers, active N2 injection,
        dilution of C1/C2/C3/C2H4, and strict conservation.
        """
        actual = {"N2": 0.50, "C1": 47.00, "C2": 45.00, "C3": 7.00, "C2H4": 0.50}
        target = {"N2": 8.00, "C1": 43.50, "C2": 42.00, "C3": 6.00, "C2H4": 0.50}

        for use_purity in [False, True]:
            with self.subTest(use_purity=use_purity):
                res = calculate_makeup_recommendations(
                    actual_molpct=actual,
                    target_molpct=target,
                    transition_hours=self.t_hours,
                    inventory_kg=self.inv_kg,
                    use_stream_purity=use_purity,
                )

                self.assertEqual(res["status"], "EVALUATED")
                self.assertGreater(res["expansion_ratio"], 1.05)
                self.assertGreater(res["total_makeup_flow_nm3_h"], 0.0)
                self.assertGreater(res["total_makeup_flow_kg_h"], 0.0)

                items = {it["component"]: it for it in res["items"]}

                # N2 MUST be injected
                self.assertEqual(items["N2"]["action"], "INJEKSI")
                self.assertGreater(items["N2"]["recommended_flow_nm3_h"], 0.0)
                self.assertGreater(items["N2"]["recommended_flow_kg_h"], 0.0)
                self.assertGreater(items["N2"]["recommended_flow_t_h"], 0.0)
                self.assertGreater(items["N2"]["recommended_flow_scfd"], 0.0)

                # All flows MUST be non-negative
                for comp, item in items.items():
                    self.assertGreaterEqual(
                        item["recommended_flow_nm3_h"], 0.0,
                        msg=f"Negative flow detected for component {comp}",
                    )
                    self.assertGreaterEqual(
                        item["recommended_flow_kg_h"], 0.0,
                        msg=f"Negative flow detected for component {comp}",
                    )

                # Initial and final moles check: n_final = n0 * expansion_ratio
                n0 = res["initial_moles_kmol"]
                n_final = res["final_moles_kmol"]
                self.assertAlmostEqual(n_final, n0 * res["expansion_ratio"], delta=0.05)

    def test_extreme_c3_deficiency_conservation_and_non_negativity(self):
        """Test massive C3 deficiency (actual C3 = 1.0%, target C3 = 10.0%).

        Verifies non-negative flow, C3 injection, and holding of other streams.
        """
        actual = {"N2": 3.50, "C1": 47.00, "C2": 47.50, "C3": 1.00, "C2H4": 1.00}
        target = {"N2": 3.00, "C1": 43.00, "C2": 43.00, "C3": 10.00, "C2H4": 1.00}

        for use_purity in [False, True]:
            with self.subTest(use_purity=use_purity):
                res = calculate_makeup_recommendations(
                    actual_molpct=actual,
                    target_molpct=target,
                    transition_hours=self.t_hours,
                    inventory_kg=self.inv_kg,
                    use_stream_purity=use_purity,
                )

                self.assertEqual(res["status"], "EVALUATED")
                items = {it["component"]: it for it in res["items"]}

                # C3 MUST be injected
                self.assertEqual(items["C3"]["action"], "INJEKSI")
                self.assertGreater(items["C3"]["recommended_flow_nm3_h"], 0.0)
                self.assertGreater(items["C3"]["recommended_flow_kg_h"], 0.0)

                # Limiting component N2 is held while other injections dilute it
                self.assertIn("TAHAN", items["N2"]["action"])
                self.assertEqual(items["N2"]["recommended_flow_nm3_h"], 0.0)

                # Non-negativity across all components
                for comp, item in items.items():
                    self.assertGreaterEqual(item["recommended_flow_nm3_h"], 0.0)
                    self.assertGreaterEqual(item["recommended_flow_kg_h"], 0.0)

    def test_multi_component_deficiency_coupling(self):
        """Test simultaneous deficiency in N2 and C3 with excess in C1 and C2."""
        actual = {"N2": 1.00, "C1": 50.00, "C2": 46.50, "C3": 2.00, "C2H4": 0.50}
        target = {"N2": 4.50, "C1": 43.00, "C2": 43.50, "C3": 8.50, "C2H4": 0.50}

        res = calculate_makeup_recommendations(
            actual_molpct=actual,
            target_molpct=target,
            transition_hours=self.t_hours,
            inventory_kg=self.inv_kg,
            use_stream_purity=True,
        )

        self.assertEqual(res["status"], "EVALUATED")
        items = {it["component"]: it for it in res["items"]}

        self.assertEqual(items["N2"]["action"], "INJEKSI")
        self.assertGreater(items["N2"]["recommended_flow_nm3_h"], 0.0)

        self.assertEqual(items["C3"]["action"], "INJEKSI")
        self.assertGreater(items["C3"]["recommended_flow_nm3_h"], 0.0)

        # Limiting component C1 is held while other injections dilute it
        self.assertIn("TAHAN", items["C1"]["action"])
        self.assertEqual(items["C1"]["recommended_flow_nm3_h"], 0.0)

    def test_extreme_expansion_ratio_triggers_purging_warning(self):
        """When required expansion ratio > 1.25 (+25%), an explicit operational purging warning must be added."""
        actual = {"N2": 1.00, "C1": 40.00, "C2": 55.00, "C3": 3.00, "C2H4": 1.00}
        target = {"N2": 4.00, "C1": 50.00, "C2": 38.00, "C3": 7.00, "C2H4": 1.00}

        res = calculate_makeup_recommendations(actual, target)
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["expansion_ratio"], 1.25)

        # Operational notes must warn operator about loop inventory / purging
        has_warning = any("purge" in note.lower() or "purging" in note.lower() or "loop inventory" in note.lower() for note in res["operational_notes"])
        self.assertTrue(has_warning, "Operational notes must warn operator when expansion exceeds 25%")


class TestAdversarialDegenerateInputs(unittest.TestCase):
    """Dimension 3: Degenerate inputs, strict NOT EVALUATED boundary contract, zero false zeros."""

    def setUp(self):
        self.valid_comp = {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C3": 6.28, "C2H4": 1.03}

    def _assert_strict_not_evaluated(self, res: Dict[str, Any], context: str):
        """Helper to verify strict NOT EVALUATED contract and absence of false zeros."""
        self.assertEqual(res["status"], "NOT EVALUATED", msg=f"Failed for {context}: status must be NOT EVALUATED")
        self.assertIsNone(res["total_makeup_flow_nm3_h"], msg=f"Failed for {context}: total nm3/h must be None")
        self.assertIsNone(res["total_makeup_flow_kg_h"], msg=f"Failed for {context}: total kg/h must be None")
        self.assertIsNone(res["total_makeup_flow_t_h"], msg=f"Failed for {context}: total t/h must be None")
        self.assertIsNone(res["total_makeup_flow_scfd"], msg=f"Failed for {context}: total scfd must be None")
        self.assertIsNone(res["initial_moles_kmol"], msg=f"Failed for {context}: initial_moles must be None")
        self.assertIsNone(res["final_moles_kmol"], msg=f"Failed for {context}: final_moles must be None")
        self.assertIsNone(res["expansion_ratio"], msg=f"Failed for {context}: expansion_ratio must be None")

        self.assertIn("items", res)
        self.assertEqual(len(res["items"]), 4)

        for item in res["items"]:
            comp = item["component"]
            self.assertEqual(
                item["action"], "TIDAK DAPAT DIEVALUASI",
                msg=f"Failed for {context}, comp {comp}: action must be TIDAK DAPAT DIEVALUASI",
            )
            # Flow fields MUST BE strictly None, NOT 0.0!
            self.assertIsNone(item["recommended_flow_nm3_h"], msg=f"Failed for {context}, comp {comp}: nm3/h is not None")
            self.assertIsNone(item["recommended_flow_kg_h"], msg=f"Failed for {context}, comp {comp}: kg/h is not None")
            self.assertIsNone(item["recommended_flow_t_h"], msg=f"Failed for {context}, comp {comp}: t/h is not None")
            self.assertIsNone(item["recommended_flow_scfd"], msg=f"Failed for {context}, comp {comp}: scfd is not None")
            self.assertIsNone(item["needed_kmol"], msg=f"Failed for {context}, comp {comp}: needed_kmol is not None")
            self.assertIsNone(item["needed_kg"], msg=f"Failed for {context}, comp {comp}: needed_kg is not None")

    def test_none_inputs(self):
        """None actual or target composition must trigger NOT EVALUATED."""
        res1 = calculate_makeup_recommendations(None, self.valid_comp)
        self._assert_strict_not_evaluated(res1, "actual_molpct=None")

        res2 = calculate_makeup_recommendations(self.valid_comp, None)
        self._assert_strict_not_evaluated(res2, "target_molpct=None")

        res3 = calculate_makeup_recommendations(None, None)
        self._assert_strict_not_evaluated(res3, "both None")

    def test_empty_dictionaries(self):
        """Empty dictionaries must trigger NOT EVALUATED."""
        res1 = calculate_makeup_recommendations({}, self.valid_comp)
        self._assert_strict_not_evaluated(res1, "actual_molpct={}")

        res2 = calculate_makeup_recommendations(self.valid_comp, {})
        self._assert_strict_not_evaluated(res2, "target_molpct={}")

        res3 = calculate_makeup_recommendations({}, {})
        self._assert_strict_not_evaluated(res3, "both {}")

    def test_zero_and_negative_inventory(self):
        """Zero, negative, NaN, and inf inventory must trigger NOT EVALUATED."""
        for bad_inv in [0.0, -1.0, -24000.0, float("nan"), float("inf"), float("-inf")]:
            with self.subTest(bad_inv=bad_inv):
                res = calculate_makeup_recommendations(
                    self.valid_comp, self.valid_comp, inventory_kg=bad_inv
                )
                self._assert_strict_not_evaluated(res, f"inventory_kg={bad_inv}")

    def test_zero_and_negative_transition_hours(self):
        """Zero, negative, NaN, and inf transition hours must trigger NOT EVALUATED."""
        for bad_t in [0.0, -0.5, -5.0, float("nan"), float("inf"), float("-inf")]:
            with self.subTest(bad_t=bad_t):
                res = calculate_makeup_recommendations(
                    self.valid_comp, self.valid_comp, transition_hours=bad_t
                )
                self._assert_strict_not_evaluated(res, f"transition_hours={bad_t}")

    def test_negative_mole_fractions(self):
        """Negative component mole fractions must trigger NOT EVALUATED."""
        bad_act = dict(self.valid_comp)
        bad_act["N2"] = -0.5
        res = calculate_makeup_recommendations(bad_act, self.valid_comp)
        self._assert_strict_not_evaluated(res, "negative N2 in actual")

        bad_tgt = dict(self.valid_comp)
        bad_tgt["C3"] = -1.0
        res2 = calculate_makeup_recommendations(self.valid_comp, bad_tgt)
        self._assert_strict_not_evaluated(res2, "negative C3 in target")

    def test_unphysical_composition_sums(self):
        """Mole fraction sums that are unphysical (<= 10% or > 150%) must trigger NOT EVALUATED."""
        tiny_comp = {"N2": 1.0, "C1": 2.0, "C2": 1.0, "C3": 0.5}  # sum = 4.5%
        res1 = calculate_makeup_recommendations(tiny_comp, self.valid_comp)
        self._assert_strict_not_evaluated(res1, "sum <= 10%")

        huge_comp = {"N2": 30.0, "C1": 80.0, "C2": 80.0, "C3": 20.0}  # sum = 210%
        res2 = calculate_makeup_recommendations(self.valid_comp, huge_comp)
        self._assert_strict_not_evaluated(res2, "sum > 150%")

    def test_nan_component_values_must_return_not_evaluated(self):
        """NaN values in actual or target mole fractions must strictly return NOT EVALUATED."""
        nan_act = dict(self.valid_comp, N2=float("nan"))
        res1 = calculate_makeup_recommendations(nan_act, self.valid_comp)
        self._assert_strict_not_evaluated(res1, "N2 is NaN in actual")

        nan_tgt = dict(self.valid_comp, C1=float("nan"))
        res2 = calculate_makeup_recommendations(self.valid_comp, nan_tgt)
        self._assert_strict_not_evaluated(res2, "C1 is NaN in target")

    def test_missing_core_components_must_return_not_evaluated(self):
        """Missing core components (e.g. C2 or C3 omitted) must strictly return NOT EVALUATED."""
        incomplete_act = {"N2": 5.0, "C1": 95.0}  # C2 and C3 missing
        res = calculate_makeup_recommendations(incomplete_act, self.valid_comp)
        self._assert_strict_not_evaluated(res, "C2 and C3 missing from actual")

    def test_negative_or_nan_c2h4_must_return_not_evaluated(self):
        """Negative or NaN C2H4 values must strictly return NOT EVALUATED."""
        neg_c2h4 = dict(self.valid_comp, C2H4=-5.0)
        res1 = calculate_makeup_recommendations(self.valid_comp, neg_c2h4)
        self._assert_strict_not_evaluated(res1, "negative C2H4 in target")

        nan_c2h4 = dict(self.valid_comp, C2H4=float("nan"))
        res2 = calculate_makeup_recommendations(self.valid_comp, nan_c2h4)
        self._assert_strict_not_evaluated(res2, "NaN C2H4 in target")

    def test_non_numeric_component_values_must_not_crash(self):
        """Non-numeric string or None in component values must return NOT EVALUATED without crashing."""
        str_comp = dict(self.valid_comp, N2="corrupted_sensor")
        res = calculate_makeup_recommendations(str_comp, self.valid_comp)
        self._assert_strict_not_evaluated(res, "string value in component dict")


class TestAdversarialAPIEndpointsAndMalformedPayloads(unittest.TestCase):
    """Dimension 4: Dedicated API /api/v1/makeup-advisory, 422 validations, read-only guarantees."""

    def setUp(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "actual_comp": {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C3": 6.28, "C2H4": 1.03},
            "target_comp": {"N2": 3.80, "C1": 45.00, "C2": 44.00, "C3": 6.20, "C2H4": 1.00},
            "transition_hours": 2.0,
            "inventory_kg": 24000.0,
            "use_stream_purity": True,
            "c1_tag": "H4FIC005",
        }

    def test_api_success_v1_and_alias(self):
        """Verify 200 OK on both /api/v1/makeup-advisory and /api/makeup-advisory."""
        for endpoint in ["/api/v1/makeup-advisory", "/api/makeup-advisory"]:
            with self.subTest(endpoint=endpoint):
                resp = self.client.post(endpoint, json=self.valid_payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertEqual(data["status"], "EVALUATED")
                self.assertGreater(data["total_makeup_flow_nm3_h"], 0.0)
                self.assertEqual(len(data["recommendations"]), 4)

    def test_api_empty_payload_returns_clean_not_evaluated_200(self):
        """Posting an empty JSON object returns 200 with status 'NOT EVALUATED' and null flows."""
        resp = self.client.post("/api/v1/makeup-advisory", json={})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "NOT EVALUATED")
        self.assertIsNone(data["total_makeup_flow_nm3_h"])
        for rec in data["recommendations"]:
            self.assertEqual(rec["action"], "TIDAK DAPAT DIEVALUASI")
            self.assertIsNone(rec["recommended_flow_nm3_h"])

    def test_api_malformed_transition_hours_returns_422(self):
        """Transition hours violations (ge=0.5, le=24.0, non-numeric) must return 422."""
        # 1. Less than 0.5 h
        p1 = dict(self.valid_payload, transition_hours=0.2)
        resp1 = self.client.post("/api/v1/makeup-advisory", json=p1)
        self.assertEqual(resp1.status_code, 422, "transition_hours < 0.5 must return 422")

        # 2. Greater than 24.0 h
        p2 = dict(self.valid_payload, transition_hours=30.0)
        resp2 = self.client.post("/api/v1/makeup-advisory", json=p2)
        self.assertEqual(resp2.status_code, 422, "transition_hours > 24 must return 422")

        # 3. String instead of float
        p3 = dict(self.valid_payload, transition_hours="fast_transition")
        resp3 = self.client.post("/api/v1/makeup-advisory", json=p3)
        self.assertEqual(resp3.status_code, 422, "String transition_hours must return 422")

    def test_api_malformed_inventory_returns_422(self):
        """Inventory violations (gt=0.0, non-numeric) must return 422."""
        # 1. Zero inventory
        p1 = dict(self.valid_payload, inventory_kg=0.0)
        resp1 = self.client.post("/api/v1/makeup-advisory", json=p1)
        self.assertEqual(resp1.status_code, 422, "inventory_kg = 0.0 must return 422")

        # 2. Negative inventory
        p2 = dict(self.valid_payload, inventory_kg=-500.0)
        resp2 = self.client.post("/api/v1/makeup-advisory", json=p2)
        self.assertEqual(resp2.status_code, 422, "inventory_kg < 0 must return 422")

        # 3. Non-numeric
        p3 = dict(self.valid_payload, inventory_kg="heavy")
        resp3 = self.client.post("/api/v1/makeup-advisory", json=p3)
        self.assertEqual(resp3.status_code, 422, "String inventory_kg must return 422")

    def test_api_malformed_composition_types_returns_422(self):
        """Actual or target composition passed as string/list instead of dict must return 422."""
        p1 = dict(self.valid_payload, actual_comp="N2=3,C1=44")
        resp1 = self.client.post("/api/v1/makeup-advisory", json=p1)
        self.assertEqual(resp1.status_code, 422)

        p2 = dict(self.valid_payload, target_comp=[3.8, 45.0, 44.0, 6.2])
        resp2 = self.client.post("/api/v1/makeup-advisory", json=p2)
        self.assertEqual(resp2.status_code, 422)

    def test_api_malformed_boolean_use_stream_purity_returns_422(self):
        """use_stream_purity with invalid string value returns 422."""
        p = dict(self.valid_payload, use_stream_purity="not_a_boolean")
        resp = self.client.post("/api/v1/makeup-advisory", json=p)
        self.assertEqual(resp.status_code, 422)


class TestAdversarialReadOnlyAdvisoryAndSafety(unittest.TestCase):
    """Dimension 5: Read-only decision support guarantees (zero valve write commands)."""

    def test_operator_instructions_always_prefixed_advisory(self):
        """All instructions in evaluated and unevaluated responses must start with '[ADVISORY]'."""
        # 1. Evaluated response
        res_eval = calculate_makeup_recommendations(
            actual_molpct={"N2": 3.0, "C1": 44.0, "C2": 45.0, "C3": 7.0, "C2H4": 1.0},
            target_molpct={"N2": 3.5, "C1": 45.5, "C2": 44.0, "C3": 6.2, "C2H4": 0.8},
        )
        for item in res_eval["items"]:
            self.assertTrue(
                item["instruction"].startswith("[ADVISORY]"),
                f"Instruction '{item['instruction']}' must start with '[ADVISORY]'",
            )

        # 2. Unevaluated response
        res_uneval = calculate_makeup_recommendations(None, None)
        for item in res_uneval["items"]:
            self.assertTrue(
                item["instruction"].startswith("[ADVISORY]"),
                f"Unevaluated instruction '{item['instruction']}' must start with '[ADVISORY]'",
            )

    def test_source_code_inspection_for_write_commands(self):
        """Verify core/makeup_calculator.py contains zero write capabilities to DCS/SIS/PLC."""
        calc_path = _BACKEND_DIR / "core" / "makeup_calculator.py"
        with open(calc_path, "r", encoding="utf-8") as f:
            code = f.read()

        prohibited_tokens = [
            "modbus",
            "opcua",
            "pymodbus",
            "snap7",
            "write_tag",
            "set_tag",
            "send_setpoint",
            "write_register",
            "valve.open",
            "valve.close",
        ]
        for token in prohibited_tokens:
            self.assertNotIn(
                token, code.lower(),
                msg=f"Prohibited write token '{token}' found in core/makeup_calculator.py!",
            )


class TestAdversarialMetamorphicDualUnitsAndInvariants(unittest.TestCase):
    """Dimension 6: Dual mass and volumetric units, and metamorphic conservation relations."""

    def setUp(self):
        self.actual = {"N2": 3.00, "C1": 43.50, "C2": 45.00, "C3": 7.50, "C2H4": 1.00}
        self.target = {"N2": 3.60, "C1": 45.50, "C2": 44.00, "C3": 6.10, "C2H4": 0.80}

    def test_dual_unit_physical_consistency_across_all_positive_components(self):
        """Verify strict equivalence: V_nm3 = m_kg * 22.414 / MW, and scfd = Nm3/h * 24 * 37.3263."""
        res = calculate_makeup_recommendations(self.actual, self.target, transition_hours=2.0)
        self.assertEqual(res["status"], "EVALUATED")

        for item in res["items"]:
            if item["recommended_flow_kg_h"] > 0:
                comp = item["component"]
                mw = item.get("stream_mw", MW_COMPONENTS[comp])
                expected_nm3_h = item["recommended_flow_kg_h"] * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL / mw
                self.assertAlmostEqual(
                    item["recommended_flow_nm3_h"], expected_nm3_h, delta=0.5,
                    msg=f"Volumetric Nm3/h inconsistent with kg/h for {comp}",
                )

                # t/h = kg/h / 1000.0
                self.assertAlmostEqual(
                    item["recommended_flow_t_h"], item["recommended_flow_kg_h"] / 1000.0, places=4,
                )

                # scfd = Nm3/h * 24 * 37.3263
                expected_scfd = item["recommended_flow_nm3_h"] * SCFD_PER_NM3_H
                self.assertAlmostEqual(
                    item["recommended_flow_scfd"], expected_scfd, delta=50.0,
                    msg=f"scfd rate inconsistent with Nm3/h for {comp}",
                )

    def test_metamorphic_time_duration_inverse_proportionality(self):
        """Metamorphic property: Total moles injected = Rate(t) * t = Constant."""
        res_1h = calculate_makeup_recommendations(self.actual, self.target, transition_hours=1.0)
        res_2h = calculate_makeup_recommendations(self.actual, self.target, transition_hours=2.0)
        res_4h = calculate_makeup_recommendations(self.actual, self.target, transition_hours=4.0)

        tot_moles_1h = res_1h["total_makeup_flow_nm3_h"] * 1.0
        tot_moles_2h = res_2h["total_makeup_flow_nm3_h"] * 2.0
        tot_moles_4h = res_4h["total_makeup_flow_nm3_h"] * 4.0

        self.assertAlmostEqual(tot_moles_1h, tot_moles_2h, delta=1.0)
        self.assertAlmostEqual(tot_moles_2h, tot_moles_4h, delta=1.0)

    def test_metamorphic_inventory_mass_proportionality(self):
        """Metamorphic property: Rate(2 * M) = 2 * Rate(M)."""
        res_base = calculate_makeup_recommendations(self.actual, self.target, inventory_kg=24000.0)
        res_double = calculate_makeup_recommendations(self.actual, self.target, inventory_kg=48000.0)
        res_half = calculate_makeup_recommendations(self.actual, self.target, inventory_kg=12000.0)

        self.assertAlmostEqual(
            res_double["total_makeup_flow_kg_h"], 2.0 * res_base["total_makeup_flow_kg_h"], delta=0.5
        )
        self.assertAlmostEqual(
            res_half["total_makeup_flow_kg_h"], 0.5 * res_base["total_makeup_flow_kg_h"], delta=0.5
        )


if __name__ == "__main__":
    unittest.main()
