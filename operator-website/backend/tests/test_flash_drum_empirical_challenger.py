"""
operator-website/backend/tests/test_flash_drum_empirical_challenger.py
Empirical Challenger Test Harness: Rigorous PR-EOS 5C-1 Flash Drum Thermodynamics
Baseload LNG Plant-3 Train H OTS & C3MR Optimization Suite

Independent Empirical Stress Test Harness verifying:
  1. Feed Rate Sweep (50.0 to 300.0 t/h) & Exact Mass Conservation (|w_L + w_V - 1| < 1e-6)
  2. Nominal 150.0 t/h Feed Liquid Rundown Target (141.80 +- 0.5 t/h)
  3. MCHE Outlet Temperature Variations (-150°C to -155°C) Monotonic Vapor Fraction
  4. Flash Drum Pressure Variations (0.20 to 0.40 kg/cm²G) Monotonic Physical Response
  5. Equilibrium Bubble Point (-157.7°C to -158.0°C) Matching DCS H5TI0041 (-158.135°C)
  6. Component Molar & Mass Conservation Across All 7 Species
  7. Physical Edge Cases (Zero Feed, Negative Feed Rejection, Extreme Scaling)
  8. Compositional Disturbance Sensitivity (N2 volatility enrichment)

Compliance: AGENTS.md (Pasals 1, 3, 5, 8), ORIGINAL_REQUEST.md (§R3, §Acceptance Criteria)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
import numpy as np

# Ensure backend root and src directory are on sys.path
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND_DIR.parents[1]

for p in (str(_ROOT), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from thermo.flash_drum_vle import (
    BASELINE_FEED_COMP_MOL,
    COMPONENT_NAMES,
    MW,
    calculate_flash_drum_5c1,
    pr_bubble_point_temperature,
    pr_pt_flash,
    _normalize_comp,
    KGCM2G_TO_BARA,
)


class TestFlashDrumEmpiricalChallenger(unittest.TestCase):
    """Adversarial and empirical validation suite for PR-EOS 5C-1 Flash Drum engine."""

    # =========================================================================
    # Test 1: Feed Rate Sweep & Mass Conservation
    # =========================================================================
    def test_feed_rate_sweep_mass_conservation(self):
        """Verify mass conservation across feed rates 50.0 to 300.0 t/h.
        Tolerance: exact thermodynamic mass fraction closure |w_L + w_V - 1.0| < 1e-6,
        and stream mass flow balance |(lng_liquid + efg_gas) - feed| <= 0.01 t/h.
        """
        feed_rates = np.linspace(50.0, 300.0, 251)  # step 1.0 t/h
        max_yield_diff = 0.0
        max_flow_diff = 0.0

        for f in feed_rates:
            res = calculate_flash_drum_5c1(float(f))

            # 1. Exact thermodynamic mass fraction closure
            w_L = res.mass_liquid_yield
            w_V = (res.vapor_fraction_mol * res.mw_vapor) / res.mw_feed
            yield_diff = abs(w_L + w_V - 1.0)
            if yield_diff > max_yield_diff:
                max_yield_diff = yield_diff

            self.assertLess(
                yield_diff,
                1e-6,
                f"Thermodynamic mass yield non-closure at feed={f:.1f} t/h: w_L={w_L}, w_V={w_V}, diff={yield_diff}",
            )

            # 2. Flow balance closure (rounded streams within 0.01 t/h precision)
            flow_diff = abs((res.lng_liquid_flow_t_h + res.efg_gas_flow_t_h) - res.feed_flow_t_h)
            if flow_diff > max_flow_diff:
                max_flow_diff = flow_diff

            self.assertLessEqual(
                flow_diff,
                0.01,
                f"Stream flow non-balance at feed={f:.1f} t/h: diff={flow_diff}",
            )

        # Assert worst-case across 251 points meets strict limits
        self.assertLess(max_yield_diff, 1e-6)
        self.assertLessEqual(max_flow_diff, 0.01)

    # =========================================================================
    # Test 2: Nominal Feed Rate Liquid Rundown Parity (150.0 t/h -> 141.80 +- 0.5 t/h)
    # =========================================================================
    def test_nominal_feed_rate_liquid_rundown_141_80(self):
        """Verify that at nominal 150.0 t/h feed, liquid rundown evaluates to 141.80 +- 0.5 t/h.
        Target: 141.80 t/h. Observed: 141.79 t/h (error = 0.01 t/h, delta = 0.007%).
        """
        feed = 150.00
        res = calculate_flash_drum_5c1(feed)

        self.assertAlmostEqual(
            res.lng_liquid_flow_t_h,
            141.80,
            delta=0.50,
            msg=f"Liquid rundown {res.lng_liquid_flow_t_h} t/h deviates from 141.80 t/h target by > 0.5 t/h",
        )
        # Verify specific empirical value observed
        self.assertAlmostEqual(res.lng_liquid_flow_t_h, 141.79, delta=0.02)
        self.assertAlmostEqual(res.efg_gas_flow_t_h, 8.21, delta=0.02)
        self.assertAlmostEqual(res.mass_liquid_yield, 0.945285, places=5)
        self.assertAlmostEqual(res.vapor_fraction_mol, 0.058736, places=5)

    # =========================================================================
    # Test 3: MCHE Outlet Temperature Sensitivity & Monotonicity (-150°C to -155°C)
    # =========================================================================
    def test_mche_outlet_temperature_variations_monotonic_vapor(self):
        """Verify MCHE outlet temperature variations (-150.0°C to -155.0°C):
        Higher temperatures must yield strictly higher vapor fractions and lower liquid yields.
        """
        temperatures = [-150.0, -151.0, -152.0, -152.5, -153.0, -154.0, -155.0]
        results = [calculate_flash_drum_5c1(150.0, t_mche_out_c=t) for t in temperatures]

        prev_vf = None
        prev_yield = None

        for t, res in zip(temperatures, results):
            vf = res.vapor_fraction_mol
            ly = res.mass_liquid_yield

            # Physical ranges
            self.assertGreater(vf, 0.03, f"Vapor fraction at {t}°C unexpectedly low: {vf}")
            self.assertLess(vf, 0.10, f"Vapor fraction at {t}°C unexpectedly high: {vf}")
            self.assertGreater(ly, 0.90, f"Liquid yield at {t}°C unexpectedly low: {ly}")
            self.assertLess(ly, 0.98, f"Liquid yield at {t}°C unexpectedly high: {ly}")

            if prev_vf is not None:
                # As T decreases, vapor fraction MUST strictly decrease
                self.assertLess(
                    vf,
                    prev_vf,
                    f"Non-monotonic vapor fraction at T={t}°C: current {vf} >= prev {prev_vf}",
                )
                # As T decreases, liquid yield MUST strictly increase
                self.assertGreater(
                    ly,
                    prev_yield,
                    f"Non-monotonic liquid yield at T={t}°C: current {ly} <= prev {prev_yield}",
                )

            prev_vf = vf
            prev_yield = ly

    # =========================================================================
    # Test 4: Flash Drum Pressure Variations & Physical Response (0.20 to 0.40 kg/cm²G)
    # =========================================================================
    def test_flash_drum_pressure_variations_monotonic_response(self):
        """Verify flash drum pressure variations (0.20 to 0.40 kg/cm²G):
        Higher vessel pressure suppresses vaporization (lower vapor fraction, higher liquid flow)
        and raises the bubble point temperature monotonically.
        """
        pressures = [0.20, 0.25, 0.30, 0.35, 0.40]
        results = [calculate_flash_drum_5c1(150.0, p_flash_kgcm2g=p) for p in pressures]

        prev_t_bubble = None
        prev_vf = None
        prev_liquid_flow = None

        for p, res in zip(pressures, results):
            t_bub = res.t_bubble_c
            vf = res.vapor_fraction_mol
            l_flow = res.lng_liquid_flow_t_h

            if prev_t_bubble is not None:
                # Bubble point must increase monotonically with pressure
                self.assertGreater(
                    t_bub,
                    prev_t_bubble,
                    f"Bubble point must rise with pressure: p={p}, t_bub={t_bub} <= prev {prev_t_bubble}",
                )
                # Vapor fraction must decrease monotonically with pressure
                self.assertLess(
                    vf,
                    prev_vf,
                    f"Vapor fraction must fall with pressure: p={p}, vf={vf} >= prev {prev_vf}",
                )
                # Liquid flow must increase monotonically with pressure
                self.assertGreater(
                    l_flow,
                    prev_liquid_flow,
                    f"Liquid rundown flow must rise with pressure: p={p}, flow={l_flow} <= prev {prev_liquid_flow}",
                )

            prev_t_bubble = t_bub
            prev_vf = vf
            prev_liquid_flow = l_flow

    # =========================================================================
    # Test 5: Equilibrium Bubble Point Matches DCS Sensor H5TI0041
    # =========================================================================
    def test_equilibrium_bubble_point_dcs_sensor_match(self):
        """Verify equilibrium bubble point evaluates to -157.7°C to -158.0°C
        matching DCS sensor H5TI0041 (-158.135°C).
        """
        res = calculate_flash_drum_5c1(150.0, p_flash_kgcm2g=0.30)
        dcs_sensor_h5ti0041 = -158.135  # °C from Plant-3 DCS

        self.assertGreaterEqual(
            res.t_bubble_c,
            -158.00,
            f"Bubble point {res.t_bubble_c}°C must be >= -158.00°C",
        )
        self.assertLessEqual(
            res.t_bubble_c,
            -157.70,
            f"Bubble point {res.t_bubble_c}°C must be <= -157.70°C",
        )

        # Difference to plant DCS sensor must be within 0.5°C
        sensor_diff = abs(res.t_bubble_c - dcs_sensor_h5ti0041)
        self.assertLess(
            sensor_diff,
            0.50,
            f"Bubble point deviation from DCS H5TI0041 ({dcs_sensor_h5ti0041}°C) exceeds 0.5°C: diff={sensor_diff:.3f}°C",
        )
        # Flash temperature should also be in the cryogenic boiling regime
        self.assertAlmostEqual(res.t_flash_c, -157.76, delta=0.20)

    # =========================================================================
    # Test 6: Component-Wise Molar and Mass Partition Closure
    # =========================================================================
    def test_component_wise_molar_and_mass_closure(self):
        """Verify species-by-species conservation:
        1. sum(x_i) = 1.0, sum(y_i) = 1.0 (phase simplex closure)
        2. z_i = (1 - beta) * x_i + beta * y_i (species molar balance)
        3. Species mass conservation across vessel
        4. Physical enrichment: light ends (N2, C1) partition preferentially to vapor;
           heavy ends (C2, C3, iC4, nC4, iC5) partition to liquid.
        """
        res = calculate_flash_drum_5c1(150.0)
        z = _normalize_comp()
        beta = res.vapor_fraction_mol

        xl = np.array([res.liquid_comp_mol[k] / 100.0 for k in COMPONENT_NAMES])
        yv = np.array([res.vapor_comp_mol[k] / 100.0 for k in COMPONENT_NAMES])

        # 1. Simplex closure of individual phases
        self.assertAlmostEqual(float(xl.sum()), 1.0, places=6)
        self.assertAlmostEqual(float(yv.sum()), 1.0, places=6)

        # 2. Species molar conservation
        z_reconstructed = (1.0 - beta) * xl + beta * yv
        molar_residuals = np.abs(z - z_reconstructed)
        self.assertLess(
            float(np.max(molar_residuals)),
            1e-6,
            f"Species molar balance violation: max residual={np.max(molar_residuals):.2e}",
        )

        # 3. Species mass flow conservation
        f_mol = 150.0 * 1e6 / res.mw_feed
        l_mol = f_mol * (1.0 - beta)
        v_mol = f_mol * beta
        m_in = f_mol * z * MW / 1e6  # t/h
        m_out = (l_mol * xl * MW + v_mol * yv * MW) / 1e6  # t/h
        mass_residuals = np.abs(m_in - m_out)
        self.assertLess(
            float(np.max(mass_residuals)),
            1e-5,
            f"Species mass flow balance violation: max residual={np.max(mass_residuals):.2e} t/h",
        )

        # 4. K-values & physical equilibrium partitioning
        k_values = yv / np.maximum(xl, 1e-12)
        # N2 (index 0) has the highest volatility
        self.assertGreater(k_values[0], k_values[1], "N2 volatility K_N2 must exceed K_C1")
        # C1 (index 1) is volatile (K > 1.0)
        self.assertGreater(k_values[1], 1.0, "Methane K_C1 must exceed 1.0 in flash gas")
        # C2, C3, C4, C5 are heavy ends (K < 1.0)
        for i in range(2, 7):
            self.assertLess(
                k_values[i],
                0.1,
                f"Heavy component {COMPONENT_NAMES[i]} K-value must be < 0.1, got {k_values[i]}",
            )

    # =========================================================================
    # Test 7: Adversarial Boundaries & Edge Cases
    # =========================================================================
    def test_adversarial_boundaries_and_edge_cases(self):
        """Stress-test edge cases:
        - Zero feed rate (feed = 0.0 t/h) -> returns 0.0 liquid and vapor flows
        - Negative feed rate (feed < 0.0) -> cleanly raises ValueError
        - Huge feed rate (feed = 10,000.0 t/h) -> linear scaling with exact yields
        """
        # Zero feed
        r0 = calculate_flash_drum_5c1(0.0)
        self.assertEqual(r0.feed_flow_t_h, 0.0)
        self.assertEqual(r0.lng_liquid_flow_t_h, 0.0)
        self.assertEqual(r0.efg_gas_flow_t_h, 0.0)

        # Negative feed
        with self.assertRaises(ValueError):
            calculate_flash_drum_5c1(-50.0)

        # Scalability
        r_large = calculate_flash_drum_5c1(10000.0)
        self.assertAlmostEqual(r_large.lng_liquid_flow_t_h, 10000.0 * r_large.mass_liquid_yield, places=2)
        self.assertAlmostEqual(
            r_large.lng_liquid_flow_t_h + r_large.efg_gas_flow_t_h,
            10000.0,
            places=2,
        )

    # =========================================================================
    # Test 8: Disturbance Composition Sensitivity
    # =========================================================================
    def test_disturbance_composition_sensitivity(self):
        """Verify sensitivity to feed composition variations:
        Increasing light inert fraction (N2 = 1.0 mol%) must increase vapor fraction
        due to N2 high relative volatility.
        """
        r_base = calculate_flash_drum_5c1(150.0)

        # Perturbed feed with 1.0 mol% N2
        comp_perturbed = dict(BASELINE_FEED_COMP_MOL)
        comp_perturbed["N2"] = 1.00
        comp_perturbed["C1"] = BASELINE_FEED_COMP_MOL["C1"] - (1.00 - BASELINE_FEED_COMP_MOL["N2"])

        r_pert = calculate_flash_drum_5c1(150.0, feed_comp_mol=comp_perturbed)

        self.assertGreater(
            r_pert.vapor_fraction_mol,
            r_base.vapor_fraction_mol,
            f"Vapor fraction should increase with elevated N2: {r_pert.vapor_fraction_mol} <= {r_base.vapor_fraction_mol}",
        )
        self.assertLess(
            r_pert.mass_liquid_yield,
            r_base.mass_liquid_yield,
            f"Liquid yield should decrease with elevated N2: {r_pert.mass_liquid_yield} >= {r_base.mass_liquid_yield}",
        )


if __name__ == "__main__":
    unittest.main()
