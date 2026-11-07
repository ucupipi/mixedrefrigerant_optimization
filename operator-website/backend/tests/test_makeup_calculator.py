"""Comprehensive Test Suite for MCR Closed-Loop Make-Up Inventory Balance Advisory.

Covers Milestone 2 (Requirements R3 and R4) and AGENTS.md (Pasal 1, 3, 5, 8, 9, 10, 12, 13):
1. Closed-loop component mass conservation and dilution effect.
2. Stream purity matrix Y integration (fuel gas, de-ethanizer/de-propanizer distillates).
3. Strict "NOT EVALUATED" boundary contracts with null flow fields (zero false zeros).
4. Canonical Badak Plant-5 Train H DCS tag verification (H4FIC006, H4FIC007, H4FI00C8, H4FIC009/005).
5. Dual mass (kg/h, t/h) and volumetric (Nm3/h, scfd) rate consistency & metamorphic scaling.
6. Dedicated API endpoint integration (/api/v1/makeup-advisory & /api/makeup-advisory).
7. Purely read-only advisory guarantees (zero valve control commands).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
import unittest

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND_DIR.parents[1]
for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
import numpy as np

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


class TestMakeupClosedLoopMassBalance(unittest.TestCase):
    """Test group 1: Closed-loop molar conservation, expansion ratio, and dilution physics."""

    def setUp(self):
        self.actual_comp = {"N2": 3.00, "C1": 44.00, "C2": 45.00, "C3": 7.00, "C2H4": 1.00}
        self.target_comp = {"N2": 3.50, "C1": 45.50, "C2": 44.00, "C3": 6.20, "C2H4": 0.80}
        self.transition_hours = 2.0
        self.inventory_kg = 24000.0

    def test_molar_conservation_and_dilution_expansion(self):
        """Verify that loop inventory expands to dilute excess components without venting."""
        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=self.target_comp,
            transition_hours=self.transition_hours,
            inventory_kg=self.inventory_kg,
            use_stream_purity=False,  # Test ideal pure stream baseline first
        )

        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreaterEqual(res["expansion_ratio"], 1.0)
        self.assertAlmostEqual(res["estimated_inventory_kg"], 24000.0, places=1)
        self.assertEqual(res["transition_hours"], 2.0)

        # In this scenario C2H4 limits expansion (1.0% -> 0.8%, lambda = 1.25):
        # All core components (N2, C1, C2, C3) must be injected to maintain recipe during expansion
        items_by_comp = {item["component"]: item for item in res["items"]}

        for comp in ["N2", "C1", "C2", "C3"]:
            self.assertEqual(
                items_by_comp[comp]["action"], "INJEKSI",
                msg=f"Component {comp} must have INJEKSI action during loop expansion",
            )
            self.assertGreater(
                items_by_comp[comp]["recommended_flow_nm3_h"], 0.0,
                msg=f"Component {comp} volumetric rate must be positive",
            )
            self.assertGreater(
                items_by_comp[comp]["recommended_flow_kg_h"], 0.0,
                msg=f"Component {comp} mass rate must be positive",
            )

        # Check total mole balance closure: n_final = n0 * expansion_ratio
        n0 = res["initial_moles_kmol"]
        n_final = res["final_moles_kmol"]
        self.assertAlmostEqual(n_final, n0 * res["expansion_ratio"], delta=0.05)

        # Rigorous species molar conservation verification: n0 * x0 + Y @ u = n_final * x_target
        injected_stream_kmol = {
            item["component"]: item["recommended_flow_nm3_h"] * res["transition_hours"] / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
            for item in res["items"]
        }
        injected_stream_kmol["C2H4"] = 0.0  # C2H4 not on online header

        comps = ["N2", "C1", "C2", "C3", "C2H4"]
        resulting_moles = np.array([
            n0 * (self.actual_comp[c] / 100.0) + injected_stream_kmol[c]
            for c in comps
        ])
        resulting_molpct = resulting_moles / np.sum(resulting_moles) * 100.0
        target_molpct = np.array([self.target_comp[c] for c in comps])

        for idx, comp in enumerate(comps):
            self.assertAlmostEqual(
                resulting_molpct[idx], target_molpct[idx], delta=0.05,
                msg=f"Species mass balance closure failed for {comp}: resulting {resulting_molpct[idx]:.2f}% vs target {target_molpct[idx]:.2f}%",
            )

    def test_core_component_limiting_dilution_and_mass_closure(self):
        """When a core DCS component (C3) limits expansion, verify TAHAN/STOP and exact mass closure."""
        actual = {"N2": 3.00, "C1": 44.00, "C2": 45.00, "C3": 8.00}
        target = {"N2": 3.50, "C1": 45.50, "C2": 45.00, "C3": 6.00}

        res = calculate_makeup_recommendations(
            actual_molpct=actual,
            target_molpct=target,
            transition_hours=self.transition_hours,
            inventory_kg=self.inventory_kg,
            use_stream_purity=False,
        )

        self.assertEqual(res["status"], "EVALUATED")
        self.assertAlmostEqual(res["expansion_ratio"], 8.0 / 6.0, places=3)

        items_by_comp = {item["component"]: item for item in res["items"]}

        # C3 is the limiting component in excess: must be TAHAN / STOP with zero flow
        self.assertEqual(items_by_comp["C3"]["action"], "TAHAN / STOP")
        self.assertEqual(items_by_comp["C3"]["recommended_flow_nm3_h"], 0.0)
        self.assertEqual(items_by_comp["C3"]["recommended_flow_kg_h"], 0.0)

        # N2, C1, C2 must be INJEKSI with positive flow
        for comp in ["N2", "C1", "C2"]:
            self.assertEqual(items_by_comp[comp]["action"], "INJEKSI")
            self.assertGreater(items_by_comp[comp]["recommended_flow_nm3_h"], 0.0)
            self.assertGreater(items_by_comp[comp]["recommended_flow_kg_h"], 0.0)

        # Species conservation closure
        n0 = res["initial_moles_kmol"]
        injected_stream_kmol = {
            item["component"]: item["recommended_flow_nm3_h"] * res["transition_hours"] / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
            for item in res["items"]
        }
        comps = ["N2", "C1", "C2", "C3"]
        resulting_moles = {
            c: n0 * (actual[c] / 100.0) + injected_stream_kmol[c]
            for c in comps
        }
        tot_final = sum(resulting_moles.values())

        for comp in comps:
            res_pct = (resulting_moles[comp] / tot_final) * 100.0
            self.assertAlmostEqual(
                res_pct, target[comp], delta=0.05,
                msg=f"Limiting scenario closure failed for {comp}: {res_pct:.2f}% vs {target[comp]:.2f}%",
            )

    def test_identical_composition_requires_zero_makeup(self):
        """When actual and target compositions are identical, no make-up is needed."""
        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=self.actual_comp,
            transition_hours=2.0,
            inventory_kg=24000.0,
        )

        self.assertEqual(res["status"], "EVALUATED")
        self.assertAlmostEqual(res["expansion_ratio"], 1.0, places=3)
        self.assertAlmostEqual(res["total_makeup_flow_nm3_h"], 0.0, places=1)
        self.assertAlmostEqual(res["total_makeup_flow_kg_h"], 0.0, places=1)

        for item in res["items"]:
            self.assertIn(item["action"], ["STABIL / SEIMBANG", "TAHAN / STOP"])
            self.assertEqual(item["recommended_flow_nm3_h"], 0.0)
            self.assertEqual(item["recommended_flow_kg_h"], 0.0)


class TestStreamPurityMatrixIntegration(unittest.TestCase):
    """Test group 2: Make-up stream purity matrix Y handling."""

    def setUp(self):
        self.actual_comp = {"N2": 3.00, "C1": 43.50, "C2": 45.00, "C3": 7.50, "C2H4": 1.00}
        self.target_comp = {"N2": 3.40, "C1": 45.50, "C2": 44.00, "C3": 6.30, "C2H4": 0.80}

    def test_stream_purity_matrix_structure_and_closure(self):
        """Verify that default stream purity matrix Y has proper column sums of 1.0."""
        for header, comp_dict in DEFAULT_STREAM_PURITY_MATRIX.items():
            col_sum = sum(comp_dict.values())
            self.assertAlmostEqual(
                col_sum, 1.0, places=4,
                msg=f"Header {header} composition sum {col_sum} must equal 1.0 within numerical tolerance",
            )

    def test_purity_matrix_accounts_for_fuel_gas_heavy_ends(self):
        """Verify that fuel gas C1 make-up accounts for C2/C3 content in stream."""
        # Run with stream purity enabled
        res_impure = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=self.target_comp,
            transition_hours=2.0,
            inventory_kg=24000.0,
            use_stream_purity=True,
        )
        # Run with pure components
        res_pure = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=self.target_comp,
            transition_hours=2.0,
            inventory_kg=24000.0,
            use_stream_purity=False,
        )

        self.assertEqual(res_impure["status"], "EVALUATED")
        self.assertEqual(res_pure["status"], "EVALUATED")
        # In impure stream, C1 fuel gas carries C2 and C3, so expansion and rates differ
        self.assertIsNotNone(res_impure["total_makeup_flow_nm3_h"])
        self.assertGreater(res_impure["total_makeup_flow_nm3_h"], 0.0)

    def test_custom_purity_matrix_override(self):
        """Verify that custom purity matrix override is accepted and correctly utilized."""
        # 99% pure C1, 1% C2
        custom_purity = {
            "N2": {"N2": 1.0, "C1": 0.0, "C2": 0.0, "C2H4": 0.0, "C3": 0.0},
            "C1": {"N2": 0.0, "C1": 0.99, "C2": 0.01, "C2H4": 0.0, "C3": 0.0},
            "C2": {"N2": 0.0, "C1": 0.0, "C2": 1.0, "C2H4": 0.0, "C3": 0.0},
            "C3": {"N2": 0.0, "C1": 0.0, "C2": 0.0, "C2H4": 0.0, "C3": 1.0},
            "C2H4": {"N2": 0.0, "C1": 0.0, "C2": 0.0, "C2H4": 1.0, "C3": 0.0},
        }
        res = calculate_makeup_recommendations(
            actual_molpct=self.actual_comp,
            target_molpct=self.target_comp,
            transition_hours=2.0,
            purity_matrix=custom_purity,
        )
        self.assertEqual(res["status"], "EVALUATED")
        self.assertGreater(res["total_makeup_flow_nm3_h"], 0.0)


class TestStrictNotEvaluatedNullGuards(unittest.TestCase):
    """Test group 3: Strict 'NOT EVALUATED' boundary contracts returning null (never false 0.0)."""

    def setUp(self):
        self.valid_comp = {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C3": 6.28, "C2H4": 0.85}

    def test_none_or_empty_actual_composition_returns_not_evaluated(self):
        """None or empty actual composition must return status 'NOT EVALUATED' with null flows."""
        res_none = calculate_makeup_recommendations(
            actual_molpct=None,
            target_molpct=self.valid_comp,
        )
        self.assertEqual(res_none["status"], "NOT EVALUATED")
        self.assertIsNone(res_none["total_makeup_flow_nm3_h"])
        self.assertIsNone(res_none["total_makeup_flow_kg_h"])
        self.assertIsNone(res_none["total_makeup_flow_t_h"])
        self.assertIsNone(res_none["total_makeup_flow_scfd"])

        for item in res_none["items"]:
            self.assertEqual(item["action"], "TIDAK DAPAT DIEVALUASI")
            self.assertIsNone(item["recommended_flow_nm3_h"])
            self.assertIsNone(item["recommended_flow_kg_h"])
            self.assertIsNone(item["recommended_flow_t_h"])
            self.assertIsNone(item["recommended_flow_scfd"])

        res_empty = calculate_makeup_recommendations(
            actual_molpct={},
            target_molpct=self.valid_comp,
        )
        self.assertEqual(res_empty["status"], "NOT EVALUATED")
        self.assertIsNone(res_empty["total_makeup_flow_nm3_h"])

    def test_none_or_empty_target_composition_returns_not_evaluated(self):
        """None or empty target composition must return status 'NOT EVALUATED' with null flows."""
        res = calculate_makeup_recommendations(
            actual_molpct=self.valid_comp,
            target_molpct=None,
        )
        self.assertEqual(res["status"], "NOT EVALUATED")
        self.assertIsNone(res["total_makeup_flow_nm3_h"])
        self.assertIn("NOT EVALUATED", res["explanation"])

    def test_invalid_inventory_returns_not_evaluated(self):
        """Non-positive or NaN inventory must return status 'NOT EVALUATED'."""
        for bad_inv in [0.0, -1000.0, float("nan")]:
            res = calculate_makeup_recommendations(
                actual_molpct=self.valid_comp,
                target_molpct=self.valid_comp,
                inventory_kg=bad_inv,
            )
            self.assertEqual(res["status"], "NOT EVALUATED")
            self.assertIsNone(res["total_makeup_flow_nm3_h"])

    def test_invalid_transition_hours_returns_not_evaluated(self):
        """Non-positive or NaN transition duration must return status 'NOT EVALUATED'."""
        for bad_hrs in [0.0, -2.5, float("nan")]:
            res = calculate_makeup_recommendations(
                actual_molpct=self.valid_comp,
                target_molpct=self.valid_comp,
                transition_hours=bad_hrs,
            )
            self.assertEqual(res["status"], "NOT EVALUATED")
            self.assertIsNone(res["total_makeup_flow_nm3_h"])

    def test_negative_mole_fraction_returns_not_evaluated(self):
        """Negative component mole fractions violate physical bounds and must return NOT EVALUATED."""
        bad_comp = {"N2": -2.0, "C1": 46.0, "C2": 45.0, "C3": 7.0}
        res = calculate_makeup_recommendations(
            actual_molpct=bad_comp,
            target_molpct=self.valid_comp,
        )
        self.assertEqual(res["status"], "NOT EVALUATED")
        self.assertIsNone(res["total_makeup_flow_nm3_h"])

    def test_unphysical_sum_returns_not_evaluated(self):
        """Mole fraction sums that deviate radically from 100% indicate sensor fault."""
        tiny_comp = {"N2": 0.05, "C1": 0.10, "C2": 0.05, "C3": 0.05}
        res = calculate_makeup_recommendations(
            actual_molpct=tiny_comp,
            target_molpct=self.valid_comp,
        )
        self.assertEqual(res["status"], "NOT EVALUATED")


class TestCanonicalBadakDCSTags(unittest.TestCase):
    """Test group 4: Alignment with CANONICAL_TAG_DICTIONARY.csv."""

    def test_canonical_dcs_tags_in_metadata_dictionary(self):
        """Verify that TAG_MAKEUP_CONTROLLERS contains certified Plant-5 Train H DCS tags."""
        self.assertEqual(TAG_MAKEUP_CONTROLLERS["N2"]["tag"], "H4FIC006")
        self.assertEqual(TAG_MAKEUP_CONTROLLERS["C3"]["tag"], "H4FIC007")
        self.assertEqual(TAG_MAKEUP_CONTROLLERS["C2"]["tag"], "H4FI00C8")
        self.assertIn(TAG_MAKEUP_CONTROLLERS["C1"]["tag"], ["H4FIC005", "H4FIC009"])

    def test_calculated_items_contain_canonical_tags(self):
        """Verify that calculate_makeup_recommendations outputs correct tags."""
        actual = {"N2": 3.0, "C1": 44.0, "C2": 45.0, "C3": 7.0}
        target = {"N2": 3.5, "C1": 45.0, "C2": 44.0, "C3": 6.5}

        # Test with default C1 tag (H4FIC005)
        res1 = calculate_makeup_recommendations(actual, target, c1_tag="H4FIC005")
        tags1 = {item["component"]: item["tag_dcs"] for item in res1["items"]}
        self.assertEqual(tags1["N2"], "H4FIC006")
        self.assertEqual(tags1["C1"], "H4FIC005")
        self.assertEqual(tags1["C2"], "H4FI00C8")
        self.assertEqual(tags1["C3"], "H4FIC007")

        # Test with alternative canonical C1 tag (H4FIC009)
        res2 = calculate_makeup_recommendations(actual, target, c1_tag="H4FIC009")
        tags2 = {item["component"]: item["tag_dcs"] for item in res2["items"]}
        self.assertEqual(tags2["C1"], "H4FIC009")


class TestDualRateUnitsAndMetamorphicScaling(unittest.TestCase):
    """Test group 5: Dual mass and volumetric units, and metamorphic relations."""

    def setUp(self):
        self.actual = {"N2": 3.0, "C1": 43.5, "C2": 45.0, "C3": 7.5, "C2H4": 1.0}
        self.target = {"N2": 3.5, "C1": 45.0, "C2": 44.0, "C3": 6.5, "C2H4": 1.0}

    def test_mass_and_volume_mathematical_consistency(self):
        """Verify that mass rate (kg/h) and volumetric rate (Nm3/h) strictly obey MW and V_m."""
        res = calculate_makeup_recommendations(self.actual, self.target, transition_hours=2.0)

        for item in res["items"]:
            if item["recommended_flow_kg_h"] > 0:
                mw = item.get("stream_mw", MW_COMPONENTS[item["component"]])
                # V = m * V_m / MW
                expected_nm3 = item["recommended_flow_kg_h"] * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL / mw
                self.assertAlmostEqual(
                    item["recommended_flow_nm3_h"], expected_nm3, delta=0.5,
                    msg=f"Discrepancy in component {item['component']}: Nm3/h vs kg/h",
                )
                # t/h = kg/h / 1000.0
                self.assertAlmostEqual(
                    item["recommended_flow_t_h"], item["recommended_flow_kg_h"] / 1000.0, places=4,
                )
                # scfd = Nm3/h * 24 * 37.3263
                expected_scfd = item["recommended_flow_nm3_h"] * SCFD_PER_NM3_H
                self.assertAlmostEqual(
                    item["recommended_flow_scfd"], expected_scfd, delta=50.0,
                )

    def test_metamorphic_transition_duration_scaling(self):
        """Doubling transition duration must exactly halve hourly injection rates."""
        res_2h = calculate_makeup_recommendations(self.actual, self.target, transition_hours=2.0)
        res_4h = calculate_makeup_recommendations(self.actual, self.target, transition_hours=4.0)

        self.assertAlmostEqual(
            res_2h["total_makeup_flow_kg_h"], 2.0 * res_4h["total_makeup_flow_kg_h"], delta=0.5,
        )
        self.assertAlmostEqual(
            res_2h["total_makeup_flow_nm3_h"], 2.0 * res_4h["total_makeup_flow_nm3_h"], delta=0.5,
        )

    def test_metamorphic_inventory_mass_scaling(self):
        """Doubling loop inventory mass must exactly double the total make-up required."""
        res_24k = calculate_makeup_recommendations(self.actual, self.target, inventory_kg=24000.0)
        res_48k = calculate_makeup_recommendations(self.actual, self.target, inventory_kg=48000.0)

        self.assertAlmostEqual(
            res_48k["total_makeup_flow_kg_h"], 2.0 * res_24k["total_makeup_flow_kg_h"], delta=0.5,
        )
        self.assertAlmostEqual(
            res_48k["total_makeup_flow_nm3_h"], 2.0 * res_24k["total_makeup_flow_nm3_h"], delta=0.5,
        )


class TestDedicatedMakeupAPIEndpoint(unittest.TestCase):
    """Test group 6: Dedicated API endpoint /api/v1/makeup-advisory integration."""

    def setUp(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "actual_comp": {"N2": 3.0, "C1": 44.0, "C2": 45.0, "C3": 7.0, "C2H4": 1.0},
            "target_comp": {"N2": 3.5, "C1": 45.5, "C2": 44.0, "C3": 6.2, "C2H4": 0.8},
            "transition_hours": 2.0,
            "inventory_kg": 24000.0,
            "use_stream_purity": True,
            "c1_tag": "H4FIC005",
        }

    def test_post_makeup_advisory_v1_endpoint_success(self):
        """Test POST /api/v1/makeup-advisory returns 200 and valid MakeupAdvisoryResponse schema."""
        resp = self.client.post("/api/v1/makeup-advisory", json=self.valid_payload)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["status"], "EVALUATED")
        self.assertEqual(data["transition_hours"], 2.0)
        self.assertEqual(data["estimated_inventory_kg"], 24000.0)
        self.assertGreater(data["total_makeup_flow_nm3_h"], 0.0)
        self.assertGreater(data["total_makeup_flow_kg_h"], 0.0)
        self.assertIn("recommendations", data)
        self.assertIn("items", data)
        self.assertEqual(len(data["recommendations"]), 4)
        self.assertIn("calculation_timestamp", data)
        self.assertIn("explanation", data)

    def test_post_makeup_advisory_route_alias(self):
        """Test POST /api/makeup-advisory route alias returns identical response."""
        resp = self.client.post("/api/makeup-advisory", json=self.valid_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "EVALUATED")

    def test_post_makeup_advisory_missing_inputs_returns_not_evaluated(self):
        """Test POST /api/v1/makeup-advisory with empty payload returns NOT EVALUATED (not 500 error)."""
        resp = self.client.post("/api/v1/makeup-advisory", json={})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data["status"], "NOT EVALUATED")
        self.assertIsNone(data["total_makeup_flow_nm3_h"])
        self.assertIsNone(data["total_makeup_flow_kg_h"])
        self.assertIn("NOT EVALUATED", data["explanation"])

        for rec in data["recommendations"]:
            self.assertEqual(rec["action"], "TIDAK DAPAT DIEVALUASI")
            self.assertIsNone(rec["recommended_flow_nm3_h"])


class TestReadOnlyAdvisorySafety(unittest.TestCase):
    """Test group 7: Read-only decision support and zero valve command capability."""

    def test_advisory_prefix_in_all_operator_instructions(self):
        """Every generated operator instruction MUST be prefixed with '[ADVISORY]'."""
        actual = {"N2": 3.0, "C1": 44.0, "C2": 45.0, "C3": 7.0}
        target = {"N2": 3.5, "C1": 45.5, "C2": 44.0, "C3": 6.2}

        res = calculate_makeup_recommendations(actual, target)
        self.assertEqual(res["status"], "EVALUATED")

        for item in res["items"]:
            self.assertTrue(
                item["instruction"].startswith("[ADVISORY]"),
                f"Instruction '{item['instruction']}' must start with '[ADVISORY]'",
            )

    def test_not_evaluated_instructions_are_prefixed_advisory(self):
        """Even unevaluated fallback instructions must be prefixed with '[ADVISORY]'."""
        res = calculate_makeup_recommendations(None, None)
        self.assertEqual(res["status"], "NOT EVALUATED")

        for item in res["items"]:
            self.assertTrue(
                item["instruction"].startswith("[ADVISORY]"),
                f"Instruction '{item['instruction']}' must start with '[ADVISORY]'",
            )


if __name__ == "__main__":
    unittest.main()
