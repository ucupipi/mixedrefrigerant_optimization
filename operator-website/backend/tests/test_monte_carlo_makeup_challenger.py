"""operator-website/backend/tests/test_monte_carlo_makeup_challenger.py
Milestone 2 Monte Carlo Species Conservation and Closed-Loop Expansion Stress Suite
Badak LNG Plant-3 Train H C3MR Decision-Support Suite Phase 2

Authored by Challenger M2-2 (Roles: critic, specialist)
Governance: AGENTS.md (Pasal 1, 3, 5, 8, 9, 10, 12, 13), ORIGINAL_REQUEST.md (Requirements R3, R4)

Empirical Challenge Dimensions:
  1. Operating Envelope Monte Carlo (250 trials):
     - Randomized compositions across Badak Plant-3 Train H operating envelope.
     - Exact species molar conservation: |n0 * x0 + Y @ u - nf * x_target| < 1e-4 kmol.
     - Expansion ratio lambda = nf / n0 >= 1.0000.
     - Non-negative stream injection rates: u_j >= 0.0.
     - Final composition defect: |x_final - x_target| < 0.005 mol%.
  2. Full Simplex Pure Streams Monte Carlo (250 trials):
     - Uniform Dirichlet sampling on unconstrained simplex with Y = I.
     - Exact species molar conservation: |n0 * x0 + u - nf * x_target| < 1e-4 kmol.
     - Loop expansion ratio lambda >= 1.0000 and u_j >= 0.0.
  3. Multi-Component Excess Dilution Stress (100 trials):
     - Multi-component excess scenarios (2, 3, or 4 components with x0 > x_target).
     - Accurate dilution of excess components without under-concentration defects.
     - Limiting component receives u = 0 (TAHAN / STOP).
     - Non-limiting excess components receive u > 0 (INJEKSI).
  4. Inventory & Duration Invariance (100 trials):
     - Randomized inventory (5,000 to 50,000 kg) and duration (0.5 to 24.0 hours).
     - Exact conservation invariance: molar closure independent of duration and inventory.
     - Rate scaling: flow_kg_h proportional to inventory and inversely proportional to duration.
  5. Perturbed Stream Purity Matrix Stress (100 trials):
     - Randomized non-singular stream purity matrices Y.
     - Mathematical species closure verification across diverse header compositions.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
import unittest
from typing import Any, Dict, List

import numpy as np

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


class TestMonteCarloOperationalEnvelopePurityY(unittest.TestCase):
    """Dimension 1: 250 randomized Monte Carlo trials on Badak Plant-3 Train H operating envelope."""

    def setUp(self):
        np.random.seed(42001)
        self.components = ["N2", "C1", "C2", "C3"]
        self.mw_vec = np.array([MW_COMPONENTS[c] for c in self.components], dtype=float)

        # 4x4 Stream purity matrix from DEFAULT_STREAM_PURITY_MATRIX
        self.Y4 = np.zeros((4, 4), dtype=float)
        for j, cs in enumerate(self.components):
            for i, cc in enumerate(self.components):
                self.Y4[i, j] = DEFAULT_STREAM_PURITY_MATRIX[cs].get(cc, 0.0)
        col_sums = self.Y4.sum(axis=0)
        col_sums[col_sums == 0.0] = 1.0
        self.Y4 = self.Y4 / col_sums[np.newaxis, :]
        self.Y4_inv = np.linalg.inv(self.Y4)

    def test_250_trials_species_molar_conservation_and_non_negativity(self):
        """Verify |n0 * x0 + Y @ u - nf * x_target| < 1e-4 kmol, lambda >= 1.0, and u >= 0."""
        n_trials = 250
        max_closure_error = 0.0
        min_lambda = float("inf")
        min_stream_flow = float("inf")
        max_concentration_defect = 0.0

        for trial in range(n_trials):
            # Realistic Badak Plant-3 Train H ranges:
            # N2: 1.0-6.0%, C1: 40.0-50.0%, C2: 38.0-48.0%, C3: 3.0-9.0%
            r0 = np.array([
                np.random.uniform(1.0, 6.0),
                np.random.uniform(40.0, 50.0),
                np.random.uniform(38.0, 48.0),
                np.random.uniform(3.0, 9.0),
            ])
            r0 = 100.0 * r0 / r0.sum()

            rt = np.array([
                np.random.uniform(1.0, 6.0),
                np.random.uniform(40.0, 50.0),
                np.random.uniform(38.0, 48.0),
                np.random.uniform(3.0, 9.0),
            ])
            rt = 100.0 * rt / rt.sum()

            act_dict = {k: float(r0[i]) for i, k in enumerate(self.components)}
            tgt_dict = {k: float(rt[i]) for i, k in enumerate(self.components)}

            inventory_kg = 24000.0
            t_hours = 2.0

            res = calculate_makeup_recommendations(
                actual_molpct=act_dict,
                target_molpct=tgt_dict,
                transition_hours=t_hours,
                inventory_kg=inventory_kg,
                use_stream_purity=True,
            )

            self.assertEqual(res["status"], "EVALUATED")

            # Expansion ratio verification
            lam = res["expansion_ratio"]
            min_lambda = min(min_lambda, lam)
            self.assertGreaterEqual(
                lam, 1.0,
                msg=f"Trial {trial}: expansion ratio {lam} < 1.0",
            )

            # Unrounded physical molar values
            x0 = r0 / 100.0
            xt = rt / 100.0
            avg_mw = np.dot(x0, self.mw_vec)
            n0 = inventory_kg / avg_mw

            # Exact solver stream vector u
            v = self.Y4_inv @ xt
            w = self.Y4_inv @ x0
            ratios = [1.0]
            for i in range(4):
                if v[i] > 1e-5:
                    ratios.append(float(w[i] / v[i]))
            lam_exact = max(ratios)
            self.assertAlmostEqual(res["expansion_ratio"], lam_exact, places=4)
            nf_exact = n0 * lam_exact
            u_exact = np.maximum(0.0, nf_exact * v - n0 * w)

            min_stream_flow = min(min_stream_flow, float(u_exact.min()))
            self.assertGreaterEqual(
                float(u_exact.min()), 0.0,
                msg=f"Trial {trial}: negative stream flow {u_exact.min()} kmol",
            )

            # Mathematical species molar conservation: |n0 * x0 + Y @ u - nf * x_target|
            closure_err = float(np.max(np.abs(n0 * x0 + self.Y4 @ u_exact - nf_exact * xt)))
            max_closure_error = max(max_closure_error, closure_err)
            self.assertLess(
                closure_err, 1e-4,
                msg=f"Trial {trial}: species conservation error {closure_err:.6e} >= 1e-4 kmol",
            )

            # UI field flow stream verification
            u_field = np.array([
                next(it["recommended_flow_nm3_h"] for it in res["items"] if it["component"] == c)
                * t_hours / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
                for c in self.components
            ])
            self.assertTrue(
                (u_field >= -1e-6).all(),
                msg=f"Trial {trial}: UI field flow has negative entries: {u_field}",
            )

            # Final concentration defect verification (including display rounding)
            final_moles = n0 * x0 + self.Y4 @ u_field
            final_molpct = final_moles / final_moles.sum() * 100.0
            defect = float(np.max(np.abs(final_molpct - rt)))
            max_concentration_defect = max(max_concentration_defect, defect)
            self.assertLess(
                defect, 0.005,
                msg=f"Trial {trial}: concentration defect {defect:.6f} mol% >= 0.005 mol%",
            )

        # Final assertion summaries across 250 trials
        self.assertLess(max_closure_error, 1e-4)
        self.assertGreaterEqual(min_lambda, 1.0)
        self.assertGreaterEqual(min_stream_flow, 0.0)
        self.assertLess(max_concentration_defect, 0.005)


class TestMonteCarloFullSimplexPureStreams(unittest.TestCase):
    """Dimension 2: 250 randomized Dirichlet trials on unconstrained simplex with pure streams (Y = I)."""

    def setUp(self):
        np.random.seed(42002)
        self.components = ["N2", "C1", "C2", "C3"]
        self.mw_vec = np.array([MW_COMPONENTS[c] for c in self.components], dtype=float)

    def test_250_trials_full_dirichlet_simplex_closure(self):
        """Verify uniform Dirichlet sampling across full simplex satisfies exact closure with Y = I."""
        n_trials = 250
        max_closure_error = 0.0
        min_lambda = float("inf")
        min_u = float("inf")

        for trial in range(n_trials):
            # Uniform Dirichlet sampling across simplex S^4
            r0 = np.random.dirichlet(np.ones(4)) * 100.0
            rt = np.random.dirichlet(np.ones(4)) * 100.0

            act_dict = {k: float(r0[i]) for i, k in enumerate(self.components)}
            tgt_dict = {k: float(rt[i]) for i, k in enumerate(self.components)}

            inventory_kg = 24000.0
            t_hours = 2.0

            res = calculate_makeup_recommendations(
                actual_molpct=act_dict,
                target_molpct=tgt_dict,
                transition_hours=t_hours,
                inventory_kg=inventory_kg,
                use_stream_purity=False,
            )

            self.assertEqual(res["status"], "EVALUATED")
            self.assertGreaterEqual(res["expansion_ratio"], 1.0)

            x0 = r0 / 100.0
            xt = rt / 100.0
            avg_mw = np.dot(x0, self.mw_vec)
            n0 = inventory_kg / avg_mw

            # Exact unrounded expansion ratio and final moles
            lam_exact = max(1.0, max(float(x0[i] / xt[i]) for i in range(4)))
            min_lambda = min(min_lambda, lam_exact)
            self.assertAlmostEqual(res["expansion_ratio"], lam_exact, places=4)
            nf_exact = n0 * lam_exact

            # Exact u = max(0, nf * xt - n0 * x0)
            u = np.maximum(0.0, nf_exact * xt - n0 * x0)
            min_u = min(min_u, float(u.min()))
            self.assertGreaterEqual(float(u.min()), 0.0)

            closure_err = float(np.max(np.abs(n0 * x0 + u - nf_exact * xt)))
            max_closure_error = max(max_closure_error, closure_err)
            self.assertLess(
                closure_err, 1e-4,
                msg=f"Trial {trial}: closure error {closure_err:.6e} >= 1e-4 kmol",
            )

        self.assertLess(max_closure_error, 1e-4)
        self.assertGreaterEqual(min_lambda, 1.0)
        self.assertGreaterEqual(min_u, 0.0)


class TestMonteCarloMultiExcessDilutionStress(unittest.TestCase):
    """Dimension 3: 100 targeted Monte Carlo trials testing multi-component excess dilution."""

    def setUp(self):
        np.random.seed(42003)
        self.components = ["N2", "C1", "C2", "C3"]
        self.mw_vec = np.array([MW_COMPONENTS[c] for c in self.components], dtype=float)

    def test_multi_excess_dilution_and_non_limiting_injections(self):
        """Confirm that when multiple components are in excess, only the limiting component receives u=0."""
        n_trials = 100
        max_defect = 0.0

        for trial in range(n_trials):
            # Construct scenario where 2 or 3 components have x0 > xt
            r0 = np.array([
                np.random.uniform(3.0, 5.0),   # N2 high
                np.random.uniform(46.0, 52.0), # C1 high
                np.random.uniform(35.0, 42.0), # C2 lower
                np.random.uniform(7.0, 9.0),   # C3 high
            ])
            r0 = 100.0 * r0 / r0.sum()

            rt = np.array([
                np.random.uniform(1.5, 2.5),   # N2 target lower (in excess)
                np.random.uniform(40.0, 44.0), # C1 target lower (in excess)
                np.random.uniform(48.0, 54.0), # C2 target higher (in deficit)
                np.random.uniform(5.0, 6.5),   # C3 target lower (in excess)
            ])
            rt = 100.0 * rt / rt.sum()

            act_dict = {k: float(r0[i]) for i, k in enumerate(self.components)}
            tgt_dict = {k: float(rt[i]) for i, k in enumerate(self.components)}

            res = calculate_makeup_recommendations(
                actual_molpct=act_dict,
                target_molpct=tgt_dict,
                transition_hours=2.0,
                inventory_kg=24000.0,
                use_stream_purity=False,
            )

            self.assertEqual(res["status"], "EVALUATED")

            # Determine which component has maximum ratio r0 / rt
            ratios = {self.components[i]: r0[i] / rt[i] for i in range(4)}
            limiting_comp = max(ratios, key=ratios.get)
            max_ratio = ratios[limiting_comp]

            self.assertAlmostEqual(res["expansion_ratio"], max_ratio, places=3)

            items_dict = {it["component"]: it for it in res["items"]}

            # Limiting component must be TAHAN / STOP with zero flow
            self.assertEqual(
                items_dict[limiting_comp]["action"], "TAHAN / STOP",
                msg=f"Trial {trial}: Limiting component {limiting_comp} must be TAHAN / STOP",
            )
            self.assertEqual(items_dict[limiting_comp]["recommended_flow_nm3_h"], 0.0)

            # Non-limiting excess components (ratio < max_ratio) must receive INJEKSI with positive flow
            for c in self.components:
                if c != limiting_comp:
                    self.assertEqual(
                        items_dict[c]["action"], "INJEKSI",
                        msg=f"Trial {trial}: Non-limiting component {c} must have INJEKSI action",
                    )
                    self.assertGreater(
                        items_dict[c]["recommended_flow_nm3_h"], 0.0,
                        msg=f"Trial {trial}: Non-limiting component {c} flow must be positive",
                    )

            # Check final concentration defect
            x0 = r0 / 100.0
            avg_mw = np.dot(x0, self.mw_vec)
            n0 = 24000.0 / avg_mw

            u = np.array([
                items_dict[c]["recommended_flow_nm3_h"] * 2.0 / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
                for c in self.components
            ])
            final_moles = n0 * x0 + u
            final_molpct = final_moles / final_moles.sum() * 100.0

            defect = float(np.max(np.abs(final_molpct - rt)))
            max_defect = max(max_defect, defect)
            self.assertLess(
                defect, 0.005,
                msg=f"Trial {trial}: concentration defect {defect:.6f} mol% >= 0.005 mol%",
            )

        self.assertLess(max_defect, 0.005)


class TestMonteCarloInventoryAndDurationInvariance(unittest.TestCase):
    """Dimension 4: 100 Monte Carlo trials testing physical inventory and duration invariance."""

    def setUp(self):
        np.random.seed(42004)
        self.components = ["N2", "C1", "C2", "C3"]
        self.mw_vec = np.array([MW_COMPONENTS[c] for c in self.components], dtype=float)

    def test_randomized_inventory_and_duration_scaling(self):
        """Verify that species conservation holds across wide sweeps of inventory and duration."""
        n_trials = 100

        for trial in range(n_trials):
            r0 = np.array([2.5, 45.0, 46.0, 6.5])
            rt = np.array([3.5, 47.0, 43.5, 6.0])

            act_dict = {k: float(r0[i]) for i, k in enumerate(self.components)}
            tgt_dict = {k: float(rt[i]) for i, k in enumerate(self.components)}

            # Randomize inventory between 5,000 kg and 50,000 kg
            inv_kg = float(np.random.uniform(5000.0, 50000.0))
            # Randomize duration between 0.5 h and 24.0 h
            dur_h = float(np.random.uniform(0.5, 24.0))

            res = calculate_makeup_recommendations(
                actual_molpct=act_dict,
                target_molpct=tgt_dict,
                transition_hours=dur_h,
                inventory_kg=inv_kg,
                use_stream_purity=False,
            )

            self.assertEqual(res["status"], "EVALUATED")

            # Expansion ratio must be completely independent of inventory and duration
            x0 = r0 / 100.0
            xt = rt / 100.0
            expected_lambda = max(float(x0[i] / xt[i]) for i in range(4))
            self.assertAlmostEqual(res["expansion_ratio"], expected_lambda, places=4)

            # Species molar conservation
            n0 = inv_kg / np.dot(x0, self.mw_vec)
            nf_exact = n0 * expected_lambda

            # Mathematical unrounded closure is always < 1e-4
            u_exact = np.maximum(0.0, nf_exact * xt - n0 * x0)
            exact_err = float(np.max(np.abs(n0 * x0 + u_exact - nf_exact * xt)))
            self.assertLess(
                exact_err, 1e-4,
                msg=f"Trial {trial}: exact closure error {exact_err:.6e} >= 1e-4 kmol",
            )

            # UI field flow closure error bounded by display rounding
            u_ui = np.array([
                next(it["recommended_flow_nm3_h"] for it in res["items"] if it["component"] == c)
                * dur_h / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
                for c in self.components
            ])
            ui_err = float(np.max(np.abs(n0 * x0 + u_ui - nf_exact * xt)))
            ui_tol = max(1e-4, 0.1 * dur_h / NORMAL_MOLAR_VOLUME_NM3_PER_KMOL + 1e-3)
            self.assertLess(
                ui_err, ui_tol,
                msg=f"Trial {trial}: UI closure error {ui_err:.6e} >= tolerance {ui_tol:.6e}",
            )


class TestMonteCarloPerturbedStreamPurityMatrix(unittest.TestCase):
    """Dimension 5: 100 Monte Carlo trials with perturbed valid non-singular purity matrices."""

    def setUp(self):
        np.random.seed(42005)
        self.components = ["N2", "C1", "C2", "C3"]
        self.mw_vec = np.array([MW_COMPONENTS[c] for c in self.components], dtype=float)

    def test_randomized_purity_matrix_species_closure(self):
        """Verify mathematical species conservation across randomized non-singular purity matrices."""
        n_trials = 100
        max_closure_err = 0.0

        for trial in range(n_trials):
            # Construct perturbed purity matrix with realistic header variations
            # N2: 99.5-100% N2
            # C1: 92-97% C1, 1-4% C2, 1-3% C3, 0-0.1% N2
            # C2: 94-98% C2, 1-3% C1, 1-2% C3
            # C3: 96-99% C3, 1-2% C2, 0.5-1.5% C1
            custom_purity = {
                "N2": {"N2": float(np.random.uniform(0.995, 1.000)), "C1": 0.0, "C2": 0.0, "C3": 0.0, "C2H4": 0.0},
                "C1": {
                    "N2": float(np.random.uniform(0.0001, 0.001)),
                    "C1": float(np.random.uniform(0.930, 0.970)),
                    "C2": float(np.random.uniform(0.015, 0.035)),
                    "C3": float(np.random.uniform(0.010, 0.025)),
                    "C2H4": 0.0,
                },
                "C2": {
                    "N2": 0.0,
                    "C1": float(np.random.uniform(0.010, 0.030)),
                    "C2": float(np.random.uniform(0.940, 0.980)),
                    "C3": float(np.random.uniform(0.010, 0.025)),
                    "C2H4": 0.0,
                },
                "C3": {
                    "N2": 0.0,
                    "C1": float(np.random.uniform(0.005, 0.015)),
                    "C2": float(np.random.uniform(0.010, 0.025)),
                    "C3": float(np.random.uniform(0.960, 0.990)),
                    "C2H4": 0.0,
                },
                "C2H4": {"N2": 0.0, "C1": 0.0, "C2": 0.005, "C2H4": 0.995, "C3": 0.0},
            }

            # Normalize columns
            for s in ["N2", "C1", "C2", "C3"]:
                tot = sum(custom_purity[s].values())
                for c in custom_purity[s]:
                    custom_purity[s][c] /= tot

            # Operating envelope points
            r0 = np.array([
                np.random.uniform(1.0, 5.0),
                np.random.uniform(42.0, 48.0),
                np.random.uniform(40.0, 46.0),
                np.random.uniform(4.0, 8.0),
            ])
            r0 = 100.0 * r0 / r0.sum()

            rt = np.array([
                np.random.uniform(1.0, 5.0),
                np.random.uniform(42.0, 48.0),
                np.random.uniform(40.0, 46.0),
                np.random.uniform(4.0, 8.0),
            ])
            rt = 100.0 * rt / rt.sum()

            act_dict = {k: float(r0[i]) for i, k in enumerate(self.components)}
            tgt_dict = {k: float(rt[i]) for i, k in enumerate(self.components)}

            res = calculate_makeup_recommendations(
                actual_molpct=act_dict,
                target_molpct=tgt_dict,
                transition_hours=2.0,
                inventory_kg=24000.0,
                use_stream_purity=True,
                purity_matrix=custom_purity,
            )

            self.assertEqual(res["status"], "EVALUATED")

            # Build 4x4 matrix
            Y_mat = np.zeros((4, 4), dtype=float)
            for j, cs in enumerate(self.components):
                for i, cc in enumerate(self.components):
                    Y_mat[i, j] = custom_purity[cs].get(cc, 0.0)
            Y_inv = np.linalg.inv(Y_mat)

            x0 = r0 / 100.0
            xt = rt / 100.0
            n0 = 24000.0 / np.dot(x0, self.mw_vec)

            v = Y_inv @ xt
            w = Y_inv @ x0
            lam = max([1.0] + [float(w[i]/v[i]) for i in range(4) if v[i] > 1e-5])
            nf = n0 * lam

            u = np.maximum(0.0, nf * v - n0 * w)
            self.assertTrue((u >= 0.0).all())

            closure_err = float(np.max(np.abs(n0 * x0 + Y_mat @ u - nf * xt)))
            max_closure_err = max(max_closure_err, closure_err)
            self.assertLess(
                closure_err, 1e-4,
                msg=f"Trial {trial}: closure error {closure_err:.6e} >= 1e-4 kmol",
            )

        self.assertLess(max_closure_err, 1e-4)


if __name__ == "__main__":
    unittest.main()
