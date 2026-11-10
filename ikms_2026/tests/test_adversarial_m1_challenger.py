"""
Adversarial Stress Test Suite for Milestone 1 (M1) Deliverables
Badak LNG Plant-3 Train H C3MR Liquefaction Optimization (IKMS 2026)

Challenger: challenger_m1_1 (critic, specialist)
Governance: AGENTS.md (Pasal 1 s.d. Pasal 13) | Zero Fake Regression | Zero Magic Numbers

Scope of Challenges:
1. Edge cases, boundary violations, zero/negative inputs, cryogenic limits (-45 C TAL),
   and extreme ambient temperatures in decoupled_balances.py.
2. Suction node mass balance and kickback valve (4UV-53) modulation across deep turndown,
   zero flow, and anti-surge flow floor (480.0 t/h).
3. Metamorphic stress testing of surrogate models in surrogate_models.joblib:
   - Physical monotonicity across all directional constraints (monotonic_cst).
   - Non-negativity, finite bounds, zero NaN/Inf under extreme operational sweeps.
   - Non-crossing quantile predictions (lower <= median <= upper).
   - MITA pinch approach non-crossover (MITA > 0.0 C).
4. Subprocess execution and metric integrity of validate_ml_surrogates.py.
"""

import sys
import subprocess
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import joblib

# Resolve project paths
IKMS_ROOT = Path(r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026")
WORKSPACE_ROOT = Path(r"D:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK")

SCRIPTS_DIR = IKMS_ROOT / "scripts"
MODELS_BUNDLE_PATH = WORKSPACE_ROOT / "MR_OPTIMIZATION_REBUILD" / "models" / "surrogate_models.joblib"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import decoupled_balances as db


# ==============================================================================
# SUITE 1: DECOUPLED PHYSICAL BALANCES - EDGE CASES & OPERATIONAL LIMITS
# ==============================================================================

class TestDecoupledBalancesEdgeCases:
    """Adversarial stress testing of deterministic algebraic physical balances."""

    def test_sec_normal_and_boundary_conditions(self):
        """Verify SEC calculation on normal and boundary conditions."""
        # Baseline P90
        sec_p90 = db.calculate_sec(108055.14, 308.30)
        assert sec_p90 == pytest.approx(350.487, rel=1e-3)

        # Turndown P10
        sec_p10 = db.calculate_sec(73855.10, 141.22)
        assert sec_p10 == pytest.approx(522.979, rel=1e-3)

        # Zero power with production
        assert db.calculate_sec(0.0, 100.0) == 0.0

    def test_sec_zero_and_negative_exceptions(self):
        """Verify SEC raises ValueError on zero or negative denominator/numerator."""
        # Zero LNG production (must reject division by zero)
        with pytest.raises(ValueError, match="LNG production mass flow must be positive"):
            db.calculate_sec(50000.0, 0.0)

        # Negative LNG production
        with pytest.raises(ValueError, match="LNG production mass flow must be positive"):
            db.calculate_sec(50000.0, -10.0)

        # Negative shaft power
        with pytest.raises(ValueError, match="Total compressor shaft power cannot be negative"):
            db.calculate_sec(-1000.0, 100.0)

    def test_sec_extreme_orders_of_magnitude(self):
        """Stress test SEC across extreme numerical orders of magnitude."""
        # Micro-production
        sec_micro = db.calculate_sec(100.0, 1e-6)
        assert sec_micro == pytest.approx(1e8)
        assert np.isfinite(sec_micro)

        # Mega-production
        sec_mega = db.calculate_sec(1e9, 1e6)
        assert sec_mega == pytest.approx(1000.0)
        assert np.isfinite(sec_mega)

    def test_boiler_fuel_gas_stoichiometry_and_linearity(self):
        """Verify ASME PTC 4.1 / Ramadan (2025) fuel gas factor and linearity."""
        # Standard benchmark factor (97.674 derived from enthalpy/LHV, rounded as 97.70)
        assert db.SPECIFIC_FUEL_GAS_NM3_PER_T_STEAM == pytest.approx(97.70, abs=0.05)

        # Zero steam consumption
        assert db.calculate_boiler_fuel_gas(0.0) == 0.0

        # Exact linear scaling
        v1 = db.calculate_boiler_fuel_gas(100.0)
        v2 = db.calculate_boiler_fuel_gas(200.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-6)

        # Negative steam must raise ValueError
        with pytest.raises(ValueError, match="Driver steam consumption cannot be negative"):
            db.calculate_boiler_fuel_gas(-5.0)

    def test_fuel_gas_energy_mmbtu(self):
        """Verify fuel gas heat input factor and error handling."""
        assert db.calculate_fuel_gas_energy_mmbtu(0.0) == 0.0
        assert db.calculate_fuel_gas_energy_mmbtu(100.0) == pytest.approx(351.88, rel=1e-4)

        with pytest.raises(ValueError, match="Driver steam consumption cannot be negative"):
            db.calculate_fuel_gas_energy_mmbtu(-1.0)

    def test_scope1_co2_emissions_stoichiometry(self):
        """Verify IPCC 2006 stationary combustion CO2 emissions calculation."""
        # Zero fuel gas -> zero emissions
        assert db.calculate_scope1_co2(0.0) == 0.0

        # Negative fuel gas must raise ValueError
        with pytest.raises(ValueError, match="Fuel gas consumption cannot be negative"):
            db.calculate_scope1_co2(-100.0)

        # Exact stoichiometric formula check:
        # m_CO2 = V_FG * LHV (0.03310 GJ/Nm3) * EF (56.10 kg/GJ) / 1000
        v_test = 47269.11  # P90 baseline fuel gas
        expected_co2 = v_test * 0.03310 * 56.10 / 1000.0
        actual_co2 = db.calculate_scope1_co2(v_test)
        assert actual_co2 == pytest.approx(expected_co2, rel=1e-5)
        assert actual_co2 == pytest.approx(87.77, abs=0.05)

    def test_suction_node_balance_above_floor(self):
        """Verify suction node balance when MCHE circulation exceeds floor (> 480 t/h)."""
        res = db.calculate_compressor_suction_balance(mche_circulation_t_h=550.0, reheat_4tv510_t_h=0.0)
        assert res["mche_circulation_t_h"] == 550.0
        assert res["kickback_4uv53_t_h"] == 0.0  # Valve fully closed
        assert res["compressor_suction_t_h"] == 550.0
        assert res["surge_margin_percent"] == pytest.approx((550.0 - 480.0) / 480.0 * 100.0)
        assert res["is_surge_safe"] is True

    def test_suction_node_balance_exact_floor(self):
        """Verify suction node balance exactly at anti-surge boundary (480.0 t/h)."""
        res = db.calculate_compressor_suction_balance(mche_circulation_t_h=480.0, reheat_4tv510_t_h=0.0)
        assert res["kickback_4uv53_t_h"] == 0.0
        assert res["compressor_suction_t_h"] == 480.0
        assert res["surge_margin_percent"] == pytest.approx(0.0, abs=1e-6)
        assert res["is_surge_safe"] is True

    def test_suction_node_balance_deep_turndown_modulation(self):
        """Verify kickback valve 4UV-53 modulates open when MCHE flow < 480 t/h."""
        # P10 optimal MCHE flow: 373.55 t/h
        res_p10 = db.calculate_compressor_suction_balance(mche_circulation_t_h=373.55, reheat_4tv510_t_h=0.0)
        assert res_p10["kickback_4uv53_t_h"] == pytest.approx(106.45, abs=0.01)
        assert res_p10["compressor_suction_t_h"] == pytest.approx(480.0, abs=0.01)
        assert res_p10["surge_margin_percent"] == pytest.approx(0.0, abs=1e-4)
        assert res_p10["is_surge_safe"] is True

        # With 4TV-510 reheat valve active (123.55 t/h)
        res_p10_reheat = db.calculate_compressor_suction_balance(mche_circulation_t_h=373.55, reheat_4tv510_t_h=123.55)
        assert res_p10_reheat["kickback_4uv53_t_h"] == pytest.approx(106.45, abs=0.01)
        assert res_p10_reheat["compressor_suction_t_h"] == pytest.approx(603.55, abs=0.01)
        assert res_p10_reheat["surge_margin_percent"] == pytest.approx(25.74, abs=0.05)
        assert res_p10_reheat["is_surge_safe"] is True

    def test_suction_node_balance_complete_zero_flow(self):
        """Verify full recycle behavior when MCHE circulation is zero (standby/recirculation)."""
        res_zero = db.calculate_compressor_suction_balance(mche_circulation_t_h=0.0, reheat_4tv510_t_h=0.0)
        assert res_zero["kickback_4uv53_t_h"] == 480.0
        assert res_zero["compressor_suction_t_h"] == 480.0
        assert res_zero["is_surge_safe"] is True

    def test_suction_node_balance_negative_flow_rejection(self):
        """Verify negative MCHE circulation raises ValueError."""
        with pytest.raises(ValueError, match="MCHE circulation flow cannot be negative"):
            db.calculate_compressor_suction_balance(mche_circulation_t_h=-50.0)

    def test_suction_node_piecewise_continuity(self):
        """Verify C0 continuity of compressor suction flow across the 480 t/h boundary."""
        eps = 1e-4
        left = db.calculate_compressor_suction_balance(480.0 - eps)
        right = db.calculate_compressor_suction_balance(480.0 + eps)
        assert abs(left["compressor_suction_t_h"] - right["compressor_suction_t_h"]) < 2 * eps

    def test_compressor_exergy_destruction_bounds(self):
        """Verify Gouy-Stodola exergy destruction calculation and efficiency bounds."""
        # 100% isentropic (ideal reversible) -> zero exergy destruction
        assert db.calculate_compressor_exergy_destruction(50000.0, 1.0) == 0.0

        # Normal efficiency 80%
        ed = db.calculate_compressor_exergy_destruction(10000.0, 0.80)
        assert ed == pytest.approx(2000.0)

        # Zero power -> zero destruction
        assert db.calculate_compressor_exergy_destruction(0.0, 0.85) == 0.0

        # Negative power must raise ValueError
        with pytest.raises(ValueError, match="Shaft power cannot be negative"):
            db.calculate_compressor_exergy_destruction(-1000.0, 0.85)

        # Invalid efficiency values must raise ValueError
        with pytest.raises(ValueError, match="Isentropic efficiency must be in"):
            db.calculate_compressor_exergy_destruction(10000.0, 0.0)
        with pytest.raises(ValueError, match="Isentropic efficiency must be in"):
            db.calculate_compressor_exergy_destruction(10000.0, 1.1)
        with pytest.raises(ValueError, match="Isentropic efficiency must be in"):
            db.calculate_compressor_exergy_destruction(10000.0, -0.5)

    def test_gas_density_cryogenic_suction_tal_limit(self):
        """Verify real gas density at cryogenic suction TAL limit (-45.0 C)."""
        # Suction Drum 4C-7 conditions: 3.5 kg/cm2A, -45.0 C, baseline MCR (MW = 28.530 kg/kmol)
        density, vol_flow = db.calculate_gas_density_and_volumetric_flow(
            mass_flow_t_h=480.0,
            pressure_kgcm2a=3.5,
            temperature_c=-45.0,
            molecular_weight=db.MW_MCR_BASELINE,
            z_factor=0.95
        )
        # Expected density ~ 5.43 kg/m3
        assert 5.0 < density < 6.0
        # Expected volumetric flow ~ 88,000 m3/h
        assert 80000.0 < vol_flow < 95000.0
        assert np.isfinite(density)
        assert np.isfinite(vol_flow)

    def test_gas_density_extreme_ambient_temperatures(self):
        """Verify gas density behavior across extreme tropical ambient temperatures."""
        temps = [0.0, 15.0, 25.0, 35.0, 45.0, 55.0]
        densities = []
        for t in temps:
            rho, _ = db.calculate_gas_density_and_volumetric_flow(
                mass_flow_t_h=100.0,
                pressure_kgcm2a=1.033,  # 1 atm
                temperature_c=t,
                molecular_weight=db.MW_FEED_GAS,
                z_factor=1.0
            )
            densities.append(rho)

        # Density must strictly decrease as temperature increases (d(rho)/dT < 0)
        diffs = np.diff(densities)
        assert np.all(diffs < 0.0), f"Densities not strictly decreasing with temperature: {densities}"

    def test_gas_density_invalid_physical_parameters(self):
        """Verify gas density function rejects unphysical pressures and absolute temperatures."""
        # Absolute zero (-273.15 C -> 0 K)
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, 3.5, -273.15, 28.53, 0.95)

        # Below absolute zero
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, 3.5, -300.0, 28.53, 0.95)

        # Zero or negative absolute pressure
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, 0.0, 25.0, 28.53, 0.95)
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, -1.0, 25.0, 28.53, 0.95)

        # Zero or negative compressibility factor Z
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, 3.5, 25.0, 28.53, 0.0)
        with pytest.raises(ValueError, match="Pressure, absolute temperature, and Z factor must be positive"):
            db.calculate_gas_density_and_volumetric_flow(100.0, 3.5, 25.0, 28.53, -0.5)

    def test_annualized_benefits_calculation(self):
        """Verify annual hours-weighted benefit calculations."""
        q_p90 = db.OperatingQuantile(
            name="P90_Baseload",
            hours_per_year=2000.0,
            lng_production_t_h=308.30,
            shaft_power_baseline_kw=108055.14,
            shaft_power_optimized_kw=79083.37,
            steam_baseline_t_h=483.95,
            steam_optimized_t_h=452.30
        )
        q_p10 = db.OperatingQuantile(
            name="P10_Turndown",
            hours_per_year=1000.0,
            lng_production_t_h=141.22,
            shaft_power_baseline_kw=73855.10,
            shaft_power_optimized_kw=47999.30,
            steam_baseline_t_h=354.20,
            steam_optimized_t_h=346.50
        )
        res = db.calculate_annualized_benefits([q_p90, q_p10])
        assert res["total_operating_hours"] == 3000.0
        assert res["annual_energy_saved_mwh"] > 0.0
        assert res["annual_driver_steam_saved_t"] > 0.0
        assert res["annual_fuel_gas_saved_nm3"] > 0.0
        assert res["annual_co2_abated_t"] > 0.0
        assert res["annual_cost_savings_usd"] > 0.0


# ==============================================================================
# SUITE 2: SURROGATE MODELS - MONOTONICITY, BOUNDS & NON-NEGATIVITY
# ==============================================================================

@pytest.fixture(scope="module")
def model_bundle():
    """Load the certified surrogate models bundle."""
    assert MODELS_BUNDLE_PATH.exists(), f"Model bundle missing at {MODELS_BUNDLE_PATH}"
    return joblib.load(MODELS_BUNDLE_PATH)


class TestMLSurrogatesAdversarial:
    """Metamorphic and stress testing of trained surrogate ML models."""

    def test_mche_flow_monotonicity_and_bounds(self, model_bundle):
        """Verify mche_flow surrogate is monotonically non-decreasing with feed and ambient temp."""
        model = model_bundle["models"]["mche_flow"]

        # 1. Sweep feed flow from deep underload (50 t/h) to baseload (400 t/h)
        feeds = np.linspace(50.0, 400.0, 50)
        df_feed = pd.DataFrame({
            "feed_flow_th": feeds,
            "c1_mol": 42.22,
            "c2_mol": 43.67,
            "t_amb_c": 30.0
        })
        preds_feed = model.predict(df_feed)

        # Non-negativity
        assert np.all(preds_feed > 0.0), "MCHE flow predictions must be strictly positive"

        # Monotonicity with feed_flow_th (constraint = +1)
        diff_feed = np.diff(preds_feed)
        assert np.all(diff_feed >= -1e-9), f"MCHE flow not monotonic with feed: min diff {diff_feed.min()}"

        # 2. Sweep ambient temperature (20 C to 40 C)
        t_ambs = np.linspace(20.0, 40.0, 30)
        df_tamb = pd.DataFrame({
            "feed_flow_th": 250.0,
            "c1_mol": 42.22,
            "c2_mol": 43.67,
            "t_amb_c": t_ambs
        })
        preds_tamb = model.predict(df_tamb)
        diff_tamb = np.diff(preds_tamb)
        assert np.all(diff_tamb >= -1e-9), f"MCHE flow not monotonic with t_amb: min diff {diff_tamb.min()}"

    def test_mita_pinch_approach_monotonicity_and_no_crossover(self, model_bundle):
        """Verify MITA pinch approach is strictly positive (no crossover) and respects physical monotonicity."""
        model = model_bundle["models"]["mita"]

        # 1. Sweep feed flow: Higher feed narrows pinch (cst = -1, non-increasing)
        feeds = np.linspace(100.0, 400.0, 50)
        df_f = pd.DataFrame({
            "feed_flow_th": feeds,
            "opt_mche_mcr_th": 550.0,
            "c1_mol": 42.22,
            "t_amb_c": 30.0
        })
        preds_f = model.predict(df_f)

        # Safety floor: MITA must never cross over (MITA > 0.0 C)
        assert np.all(preds_f > 1.50), f"MITA violated 1.50 C floor: min {preds_f.min()}"
        diff_f = np.diff(preds_f)
        assert np.all(diff_f <= 1e-9), f"MITA not non-increasing with feed: max diff {diff_f.max()}"

        # 2. Sweep MCR flow: Higher MCR widens pinch (cst = +1, non-decreasing)
        mcrs = np.linspace(350.0, 750.0, 50)
        df_m = pd.DataFrame({
            "feed_flow_th": 250.0,
            "opt_mche_mcr_th": mcrs,
            "c1_mol": 42.22,
            "t_amb_c": 30.0
        })
        preds_m = model.predict(df_m)
        assert np.all(preds_m > 1.50), f"MITA violated 1.50 C floor: min {preds_m.min()}"
        diff_m = np.diff(preds_m)
        assert np.all(diff_m >= -1e-9), f"MITA not non-decreasing with MCR flow: min diff {diff_m.min()}"

    def test_mita_quantile_intervals_non_crossing(self, model_bundle):
        """Verify quantile uncertainty regressors do not cross: mita_lower <= mita <= mita_upper."""
        m_med = model_bundle["models"]["mita"]
        m_low = model_bundle["models"]["mita_lower"]
        m_upp = model_bundle["models"]["mita_upper"]

        df = pd.DataFrame({
            "feed_flow_th": [141.22, 220.0, 308.30, 330.0],
            "opt_mche_mcr_th": [373.55, 480.0, 580.0, 620.0],
            "c1_mol": [42.22, 42.22, 42.22, 42.22],
            "t_amb_c": [28.0, 30.0, 32.0, 35.0]
        })
        low = m_low.predict(df)
        med = m_med.predict(df)
        upp = m_upp.predict(df)

        assert np.all(low <= med + 1e-6), f"Lower quantile crosses median: low={low}, med={med}"
        assert np.all(med <= upp + 1e-6), f"Median crosses upper quantile: med={med}, upp={upp}"

    def test_power_surrogate_monotonicity_and_bounds(self, model_bundle):
        """Verify PR-EOS compressor power is monotonically increasing with throughput and ambient temp."""
        model = model_bundle["models"]["power"]

        # Sweep throughput across operating range
        throughputs = np.linspace(480.0, 750.0, 50)
        df = pd.DataFrame({
            "feed_flow_th": 250.0,
            "opt_mche_mcr_th": 500.0,
            "opt_comp_throughput_th": throughputs,
            "suction_temp_c": -35.0,
            "t_amb_c": 30.0
        })
        preds = model.predict(df)
        assert np.all(preds > 20000.0), f"Shaft power unrealistically low: min {preds.min()}"
        diff = np.diff(preds)
        assert np.all(diff >= -1e-9), f"Shaft power not monotonic with throughput: min diff {diff.min()}"

    def test_plant_power_surrogate_monotonicity(self, model_bundle):
        """Verify DCS plant power surrogate is monotonically non-decreasing with all load variables."""
        model = model_bundle["models"]["plant_power"]

        feeds = np.linspace(100.0, 350.0, 50)
        df = pd.DataFrame({
            "feed_flow_th": feeds,
            "opt_mche_mcr_th": feeds * 1.8,
            "opt_comp_throughput_th": np.maximum(480.0, feeds * 1.8),
            "suction_temp_c": -35.0,
            "t_amb_c": 30.0
        })
        preds = model.predict(df)
        assert np.all(preds > 40000.0), f"Plant power unrealistically low: min {preds.min()}"
        diff = np.diff(preds)
        assert np.all(diff >= -1e-9), f"Plant power not monotonic with load: min diff {diff.min()}"

    def test_steam_surrogate_monotonicity_and_positive_bounds(self, model_bundle):
        """Verify total driver steam surrogate is monotonically increasing with shaft power and feed."""
        model = model_bundle["models"]["steam"]

        powers = np.linspace(50000.0, 115000.0, 50)
        feeds = np.linspace(140.0, 340.0, 50)
        df = pd.DataFrame({
            "plant_total_shaft_kw": powers,
            "feed_flow_th": feeds,
            "t_amb_c": 30.0
        })
        preds = model.predict(df)
        assert np.all(preds > 200.0), f"Driver steam flow unrealistically low: min {preds.min()}"
        diff = np.diff(preds)
        assert np.all(diff >= -1e-9), f"Driver steam not monotonic: min diff {diff.min()}"

    def test_suction_temp_surrogate_safety_envelope(self, model_bundle):
        """Verify suction temperature surrogate remains safely above TAL (-45.0 C) across normal operations."""
        model = model_bundle["models"]["suction_temp"]

        # Grid across operational feeds and MCR flows
        feeds = [141.22, 220.0, 308.30]
        mcrs = [373.55, 480.0, 600.0]
        records = []
        for f in feeds:
            for m in mcrs:
                kb = max(0.0, 480.0 - m)
                records.append({
                    "feed_flow_th": f,
                    "opt_mche_mcr_th": m,
                    "anti_surge_kickback_th": kb,
                    "t_amb_c": 30.0
                })
        df = pd.DataFrame(records)
        preds = model.predict(df)

        # Must never trigger TAL (-45.0 C)
        assert np.all(preds > -45.0), f"Suction temp surrogate breached TAL (-45 C): {preds}"
        # Realistic cryogenic range: -43.0 C to -20.0 C
        assert np.all(preds < -15.0), f"Suction temp surrogate unphysically warm: {preds}"


# ==============================================================================
# SUITE 3: VALIDATION ENGINE AND SSOT CONSISTENCY CHECKS
# ==============================================================================

class TestValidationEngineAndSSOT:
    """Execution and verification of the official validation script."""

    def test_validate_ml_surrogates_subprocess_execution(self):
        """Execute validate_ml_surrogates.py independently and assert return code 0."""
        script_path = IKMS_ROOT / "scripts" / "validate_ml_surrogates.py"
        assert script_path.exists(), f"validate_ml_surrogates.py missing at {script_path}"

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(IKMS_ROOT)
        )
        assert result.returncode == 0, f"Script failed with code {result.returncode}:\n{result.stderr}"
        assert "VERIFICATION RECEIPT: ALL CHECKS PASSED [STATUS: SUCCESS - EXIT 0]" in result.stdout
        assert "Total Unlabelled 1-Minute DCS Telemetry Records (2023-2026): 720,734" in result.stdout
        assert "Authenticated Steady-State Training Records (Filtered): 67,916" in result.stdout
        assert "Tag: H4FI030A" in result.stdout
        assert "4G-5" in result.stdout
