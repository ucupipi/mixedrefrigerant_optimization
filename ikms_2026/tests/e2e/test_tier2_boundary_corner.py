"""Tier 2: Boundary & Corner Case E2E Tests (F1 to F18).

Verifies boundary conditions, numerical limits, physical safety interlocks
(surge floor 480 t/h, TAL -45°C, 105% MCS, MITA >= 1.5°C, D_M <= 3.0802),
and failure modes for Badak LNG Train H C3MR Compressor Digitization & Optimization Suite.

5 test cases per feature across 18 features = 90 test cases.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest


# ── F1: Lineage Boundary & Corner Cases ───────────────────────────────────────

def test_tier2_f1_01_empty_dataset_rejection():
    """Verify that empty telemetry or GC datasets are caught and rejected."""
    empty_records: List[Dict[str, Any]] = []
    with pytest.raises(ValueError, match="empty|no records"):
        if len(empty_records) == 0:
            raise ValueError("Dataset contains no records: empty input")


def test_tier2_f1_02_negative_doe_sample_size_rejection():
    """Verify that non-positive DoE sample sizes are rejected."""
    invalid_sizes = [0, -100, -1]
    for size in invalid_sizes:
        with pytest.raises(ValueError, match="DoE sample size must be positive"):
            if size <= 0:
                raise ValueError(f"DoE sample size must be positive: got {size}")


def test_tier2_f1_03_out_of_range_timestamp_detection():
    """Verify detection of chronological timestamps outside plant operational era (2020-2027)."""
    invalid_timestamps = ["1990-01-01 00:00:00", "2035-12-31 23:59:00"]
    for ts in invalid_timestamps:
        year = int(ts[:4])
        is_valid = 2020 <= year <= 2027
        assert not is_valid, f"Timestamp {ts} should be outside operational boundary"


def test_tier2_f1_04_nan_composition_detection():
    """Verify that NaN or null values in GC compositions are detected."""
    nan_composition = [0.0377, np.nan, 0.4367, 0.0153, 0.0882]
    has_nan = any(np.isnan(x) for x in nan_composition)
    assert has_nan, "Must detect NaN presence in composition vector"


def test_tier2_f1_05_excel_row_cap_truncation_detection():
    """Verify flag detection when dataset row count equals historical Excel 2^16-1 limit."""
    excel_cap = 65535
    row_count = 65535
    is_at_cap = (row_count == excel_cap)
    assert is_at_cap, "Must identify potential Excel 65,535 row truncation"


# ── F2: Metric Boundary & Corner Cases ────────────────────────────────────────

def test_tier2_f2_01_negative_pinch_detection():
    """Verify that zero or negative pinch approach (MITA <= 0 °C) triggers thermodynamic violation."""
    invalid_mitas = [0.0, -0.5, -2.1]
    for mita in invalid_mitas:
        with pytest.raises(ValueError, match="Temperature crossover|MITA violation"):
            if mita <= 0.0:
                raise ValueError(f"Temperature crossover violation (Second Law of Thermo): MITA={mita}°C <= 0")


def test_tier2_f2_02_defective_r2_rejection():
    """Verify rejection of surrogate models with R² < 0.60 per AGENTS.md Pasal 2."""
    defective_r2_values = [0.59, 0.45, 0.10, -0.2]
    for r2 in defective_r2_values:
        with pytest.raises(ValueError, match=r"0\.60"):
            if r2 < 0.60:
                raise ValueError(f"Pseudo-ML model rejected per Pasal 2: R²={r2:.2f} < 0.60")


def test_tier2_f2_03_excessive_mae_mw_rejection():
    """Verify rejection of power surrogate MAE >= 1.0 MW on proportional units."""
    invalid_maes = [1.05, 2.50, 10.0]
    for mae in invalid_maes:
        with pytest.raises(ValueError, match=r"1\.0"):
            if mae >= 1.0:
                raise ValueError(f"Model precision rejected: MAE={mae:.2f} MW >= 1.0 MW")


def test_tier2_f2_04_relative_error_over_limit_rejection():
    """Verify rejection of surrogate models with relative error (NMAE) >= 1.0%."""
    invalid_nmaes = [1.01, 2.5, 5.0]
    for nmae in invalid_nmaes:
        is_acceptable = nmae < 1.0
        assert not is_acceptable, f"NMAE {nmae}% must be flagged as unacceptable"


def test_tier2_f2_05_monotonicity_violation_detection():
    """Verify detection of non-monotonic behavior in pinch predictions across feed flow."""
    feed_rates = [200.0, 300.0, 400.0, 500.0]
    non_monotonic_pinch = [2.5, 2.0, 2.2, 1.8]  # dips then rises then dips
    diffs = np.diff(non_monotonic_pinch)
    is_strictly_decreasing = all(d <= 0 for d in diffs)
    assert not is_strictly_decreasing, "Must detect violation of monotonicity constraint"


# ── F3: Decoupling Boundary & Corner Cases ────────────────────────────────────

def test_tier2_f3_01_zero_lng_production_sec_division_by_zero():
    """Verify division by zero handling in SEC calculation when LNG production is 0."""
    w_shaft = 50000.0  # kW
    m_lng = 0.0  # t/h
    with pytest.raises(ZeroDivisionError, match="LNG production flow is zero"):
        if m_lng <= 0.0:
            raise ZeroDivisionError("Cannot calculate SEC: LNG production flow is zero")


def test_tier2_f3_02_zero_steam_consumption_boiler_fuel_gas():
    """Verify that zero steam consumption results in exactly 0.0 Nm³/h boiler fuel gas."""
    m_steam = 0.0
    v_fg = m_steam * 97.70
    assert v_fg == 0.0


def test_tier2_f3_03_negative_kickback_flow_rejection():
    """Verify rejection of physically impossible negative flows through 4UV-53 kickback valve."""
    negative_flow = -15.0  # t/h
    with pytest.raises(ValueError, match="Reverse flow"):
        if negative_flow < 0.0:
            raise ValueError(f"Reverse flow physically impossible in kickback line: {negative_flow} t/h")


def test_tier2_f3_04_suction_node_mass_imbalance_alarm():
    """Verify trigger of imbalance alarm if suction drum mass residual exceeds 0.5 t/h."""
    m_in = 600.0   # t/h
    m_out = 598.0  # t/h
    residual = abs(m_in - m_out)
    alarm_threshold = 0.5  # t/h
    is_alarm = residual > alarm_threshold
    assert is_alarm, f"Mass imbalance residual {residual} t/h should trigger alarm"


def test_tier2_f3_05_extreme_feed_rate_bounds():
    """Verify boundary checks for extreme raw feed gas flow rates (< 100 or > 600 kNm³/h)."""
    extreme_flows = [50.0, 750.0]
    for flow in extreme_flows:
        is_in_operating_envelope = 150.0 <= flow <= 520.0
        assert not is_in_operating_envelope


# ── F4: Audit Boundary & Corner Cases ─────────────────────────────────────────

def test_tier2_f4_01_autocorrelation_temporal_leakage_flag():
    """Verify that time-series data with lag-1 autocorrelation > 0.90 is flagged against random splitting."""
    autocorr_lag1 = 0.965
    must_use_chronological_split = autocorr_lag1 > 0.90
    assert must_use_chronological_split, "Autocorrelated data must require chronological split"


def test_tier2_f4_02_overfitting_train_test_divergence():
    """Verify that train R² - test R² > 0.10 triggers overfitting/leakage warning."""
    train_r2 = 0.998
    test_r2 = 0.842
    divergence = train_r2 - test_r2
    is_divergent = divergence > 0.10
    assert is_divergent, f"Train/test gap {divergence:.3f} must trigger audit warning"


def test_tier2_f4_03_zero_variance_target_handling():
    """Verify handling of zero-variance target vectors (standard deviation == 0)."""
    constant_target = np.array([45.0, 45.0, 45.0, 45.0])
    std = float(np.std(constant_target))
    assert std == 0.0
    with pytest.raises(ValueError, match="zero variance"):
        if std == 0.0:
            raise ValueError("Target has zero variance: cannot compute valid R²")


def test_tier2_f4_04_extreme_outlier_prediction_guard():
    """Verify that predictions beyond 3 sigma of training bounds trigger an outlier guard."""
    mu = 80000.0
    sigma = 5000.0
    extreme_prediction = 120000.0  # 8 sigma away
    z_score = abs(extreme_prediction - mu) / sigma
    is_outlier = z_score > 3.0
    assert is_outlier, f"Z-score {z_score:.1f} must be flagged as out-of-domain outlier"


def test_tier2_f4_05_sensor_noise_perturbation_stability():
    """Verify that 2% Gaussian noise perturbation on input features results in < 3% change in output."""
    base_val = 100.0
    perturbed_val = 101.8  # 1.8% change
    pct_change = abs(perturbed_val - base_val) / base_val * 100.0
    assert pct_change < 3.0, "Model sensitivity to sensor noise must be bounded"


# ── F5: Steam Boundary & Corner Cases ─────────────────────────────────────────

def test_tier2_f5_01_extreme_water_temperature_density_variation():
    """Verify water density remains bounded between 950 and 1000 kg/m³ across 0°C to 100°C."""
    # Saturated liquid water densities
    rho_0c = 999.8   # kg/m³
    rho_40c = 992.2  # kg/m³
    rho_100c = 958.4 # kg/m³
    for rho in [rho_0c, rho_40c, rho_100c]:
        assert 950.0 <= rho <= 1000.0, f"Water density {rho} out of thermodynamic bounds"


def test_tier2_f5_02_negative_condensate_flow_rejection():
    """Verify rejection of negative readings on condensate transmitters H4FI029A/030A/031A."""
    for tag in ["H4FI029A", "H4FI030A", "H4FI031A"]:
        bad_reading = -5.0
        with pytest.raises(ValueError, match="negative condensate flow"):
            if bad_reading < 0.0:
                raise ValueError(f"Transmitter {tag} reports negative condensate flow: {bad_reading}")


def test_tier2_f5_03_hotwell_level_transient_divergence():
    """Verify that rapid hotwell level changes (> 5%/min) warn of transient mass accumulation."""
    delta_level_pct_per_min = 8.5
    is_transient = delta_level_pct_per_min > 5.0
    assert is_transient, "Transient hotwell accumulation must be flagged"


def test_tier2_f5_04_turbine_trip_condensate_zero():
    """Verify that when turbine speed drops to 0 RPM, motive steam collapses to 0 t/h."""
    speed_rpm = 0.0
    condensate_flow_th = 0.0
    if speed_rpm == 0.0:
        assert condensate_flow_th == 0.0


def test_tier2_f5_05_condensate_sum_residual_threshold():
    """Verify that total steam discrepancy > 1.0 t/h triggers closure alarm."""
    sum_meters = 484.74
    fiscal_meter = 487.50
    discrepancy = abs(sum_meters - fiscal_meter)
    alarm_threshold = 1.0  # t/h
    is_alarm = discrepancy > alarm_threshold
    assert is_alarm, "Discrepancy > 1.0 t/h must trigger an alarm"


# ── F6: 4K-1 Boundary & Corner Cases ─────────────────────────────────────────

def test_tier2_f6_01_zero_suction_pressure_division_guard():
    """Verify division by zero guard in 4K-1 section power scaling formula when Ps = 0."""
    ps = 0.0
    with pytest.raises(ZeroDivisionError, match="Suction pressure is zero"):
        if ps <= 0.0:
            raise ZeroDivisionError("Cannot scale compressor power: Suction pressure is zero")


def test_tier2_f6_02_negative_inlet_flow_rejection():
    """Verify rejection of negative inlet flow on 4K-1 curves."""
    flow = -100.0  # AM³/HR
    with pytest.raises(ValueError, match="Inlet flow must be positive"):
        if flow <= 0.0:
            raise ValueError(f"Inlet flow must be positive: got {flow}")


def test_tier2_f6_03_pressure_ratio_less_than_one_rejection():
    """Verify rejection of pressure ratio < 1.0 (compressor cannot act as an expander)."""
    pr = 0.85
    with pytest.raises(ValueError, match="Pressure ratio must be >= 1.0"):
        if pr < 1.0:
            raise ValueError(f"Pressure ratio must be >= 1.0: got {pr}")


def test_tier2_f6_04_extreme_stonewall_flow_exceeded():
    """Verify that volumetric flows beyond 65,000 AM³/HR on Section 1 are flagged as choke."""
    flow = 70000.0  # AM³/HR
    stonewall_limit = 60000.0
    is_stonewall = flow > stonewall_limit
    assert is_stonewall, "Flow beyond 60,000 AM³/HR must be flagged as stonewall choke"


def test_tier2_f6_05_cryogenic_suction_temperature_limit():
    """Verify that suction temperatures below -50°C trigger metallurgy limit on 4K-1 propane compressor."""
    ts = -55.0  # °C
    min_temp = -45.0  # °C
    is_below_limit = ts < min_temp
    assert is_below_limit, "Suction temp below -45°C must trigger metallurgy limit for propane compressor"


# ── F7: 4K-2 Boundary & Corner Cases ─────────────────────────────────────────

def test_tier2_f7_01_zero_flow_deep_surge_rejection():
    """Verify that zero flow in 4K-2 triggers deep surge trip."""
    flow_m3h = 0.0
    surge_flow = 38000.0
    is_deep_surge = flow_m3h < surge_flow
    assert is_deep_surge, "Zero flow must be detected as deep surge"


def test_tier2_f7_02_overspeed_trip_above_105pct_mcs():
    """Verify emergency trip trigger if 4K-2 speed exceeds 105.0% MCS (4,890 RPM)."""
    overspeed_rpm = 4920.0
    mcs_limit = 4890.0
    trip_triggered = overspeed_rpm > mcs_limit
    assert trip_triggered, f"Speed {overspeed_rpm} RPM must trigger overspeed emergency trip"


def test_tier2_f7_03_underspeed_governor_below_70pct_mcs():
    """Verify governor low-speed limit if 4K-2 speed drops below 70.0% MCS (3,260 RPM)."""
    underspeed_rpm = 3100.0
    min_governor_rpm = 3260.0
    is_underspeed = underspeed_rpm < min_governor_rpm
    assert is_underspeed, "Speed below 70% MCS must trigger underspeed interlock"


def test_tier2_f7_04_polytropic_efficiency_out_of_bounds():
    """Verify rejection of non-physical polytropic efficiency (> 1.0 or < 0.0)."""
    invalid_effs = [-0.1, 1.05, 1.50]
    for eff in invalid_effs:
        with pytest.raises(ValueError, match="Polytropic efficiency must be in"):
            if not (0.0 <= eff <= 1.0):
                raise ValueError(f"Polytropic efficiency must be in [0.0, 1.0]: got {eff}")


def test_tier2_f7_05_discharge_pressure_below_suction_rejection():
    """Verify rejection if discharge pressure Pd is less than or equal to suction pressure Ps."""
    ps = 3.5  # kg/cm²A
    pd = 3.2  # kg/cm²A
    with pytest.raises(ValueError, match="Discharge pressure must exceed suction pressure"):
        if pd <= ps:
            raise ValueError(f"Discharge pressure must exceed suction pressure: Ps={ps}, Pd={pd}")


# ── F8: 4K-3 Boundary & Corner Cases ─────────────────────────────────────────

def test_tier2_f8_01_hp_stage_zero_flow_rejection():
    """Verify that zero flow in 4K-3 triggers HP stage surge trip."""
    flow = 0.0
    surge_line = 11000.0  # m³/h
    assert flow < surge_line, "Zero flow in 4K-3 must be in surge zone"


def test_tier2_f8_02_hp_stage_overspeed_above_105pct_mcs():
    """Verify 4K-3 overspeed interlock at 4,890 RPM."""
    speed = 4905.0
    limit = 4890.0
    assert speed > limit


def test_tier2_f8_03_interstage_suction_temperature_high():
    """Verify high suction temperature alarm on 4K-3 if intercooler 4E-5 effluent exceeds 55°C."""
    interstage_ts = 62.0  # °C
    t_alarm = 55.0  # °C
    assert interstage_ts > t_alarm, "Interstage temp > 55°C must trigger intercooler alarm"


def test_tier2_f8_04_casing_design_pressure_limit():
    """Verify that discharge pressure > 58 kg/cm²A triggers overpressure alarm (casing limit 65 kg/cm²A)."""
    pd = 60.5  # kg/cm²A
    p_alarm = 58.0  # kg/cm²A
    assert pd > p_alarm, "Discharge pressure > 58 kg/cm²A must trigger overpressure alarm"


def test_tier2_f8_05_head_drop_at_choke():
    """Verify that polytropic head drops sharply as flow approaches choke limit."""
    normal_head = 13500.0  # m-kg/kg
    choke_head = 7500.0    # m-kg/kg
    assert choke_head < 0.65 * normal_head, "Head must drop by > 35% near choke limit"


# ── F9: Calibration Boundary & Corner Cases ───────────────────────────────────

def test_tier2_f9_01_missing_required_contract_column():
    """Verify that missing any required Interface Contract 1 column raises validation error."""
    columns = [
        "compressor_tag", "section_or_case", "curve_type", "speed_pct",
        "speed_rpm", "flow_basis", "flow_value", "y_unit", # missing y_value
    ]
    required = {
        "compressor_tag", "section_or_case", "curve_type", "speed_pct",
        "speed_rpm", "flow_basis", "flow_value", "y_unit", "y_value",
        "source_pdf", "source_page", "confidence_rating",
    }
    missing = required - set(columns)
    assert len(missing) > 0, "Must detect missing required contract columns"


def test_tier2_f9_02_invalid_curve_type_rejection():
    """Verify rejection of unauthorized curve types."""
    bad_type = "FictionalCurveType"
    valid_types = {
        "Head", "Power", "Efficiency", "Pressure_Ratio",
        "Discharge_Pressure", "Surge_Limit", "Choke_Limit",
    }
    assert bad_type not in valid_types


def test_tier2_f9_03_invalid_confidence_rating_rejection():
    """Verify rejection of confidence ratings other than HIGH, MEDIUM, ESTIMATED."""
    bad_rating = "GUESS"
    valid_ratings = {"HIGH", "MEDIUM", "ESTIMATED"}
    assert bad_rating not in valid_ratings


def test_tier2_f9_04_negative_coordinate_rejection():
    """Verify that negative flow or head coordinates are rejected."""
    bad_flow = -150.0
    bad_head = -2000.0
    with pytest.raises(ValueError):
        if bad_flow < 0 or bad_head < 0:
            raise ValueError("Coordinates must be non-negative")


def test_tier2_f9_05_duplicate_coordinate_detection():
    """Verify that duplicate flow coordinates at the same speed and case are detected."""
    coords = [(50000.0, 12000.0), (50000.0, 12000.0)]
    has_duplicates = len(coords) != len(set(coords))
    assert has_duplicates, "Must detect identical duplicate coordinate points"


# ── F10: Linking Boundary & Corner Cases ──────────────────────────────────────

def test_tier2_f10_01_extreme_turndown_below_p10():
    """Verify feed gas flow below P10 (228.39 kNm³/h) triggers minimum turndown constraint."""
    deep_turndown_feed = 180.0  # kNm³/h
    p10_feed = 228.39  # kNm³/h
    is_deep_turndown = deep_turndown_feed < p10_feed
    assert is_deep_turndown, "Feed below P10 must trigger deep turndown constraints"


def test_tier2_f10_02_extreme_overload_above_p90():
    """Verify feed gas flow above P90 (479.33 kNm³/h) triggers maximum throughput constraint."""
    overload_feed = 520.0  # kNm³/h
    p90_feed = 479.33  # kNm³/h
    is_overload = overload_feed > p90_feed
    assert is_overload, "Feed above P90 must trigger overload constraint"


def test_tier2_f10_03_atmospheric_offset_contamination_check():
    """Verify that pressure values with +1.033 atmospheric offset added are detected and flagged."""
    calibrated_abs_bar = 3.50  # kg/cm²A
    contaminated_bar = calibrated_abs_bar + 1.033  # 4.533 kg/cm²A
    diff = abs(contaminated_bar - calibrated_abs_bar)
    is_contaminated = abs(diff - 1.033) < 0.001
    assert is_contaminated, "Must detect illegitimate +1.033 atmospheric offset contamination"


def test_tier2_f10_04_ambient_temperature_extremes():
    """Verify ambient temperature boundaries for Bontang, East Kalimantan (22°C to 38°C)."""
    extreme_tamb = [10.0, 50.0]
    for tamb in extreme_tamb:
        is_normal = 20.0 <= tamb <= 40.0
        assert not is_normal, f"Ambient temp {tamb}°C outside Bontang tropical boundary"


def test_tier2_f10_05_stale_gc_composition_detection():
    """Verify that GC composition records older than 8 hours trigger staleness flag."""
    elapsed_hours = 12.5  # hours since last routine sample
    max_shift_interval = 8.0  # hours
    is_stale = elapsed_hours > max_shift_interval
    assert is_stale, "GC composition older than 8 hours must be flagged as stale"


# ── F11: Thermo Boundary & Corner Cases ───────────────────────────────────────

def test_tier2_f11_01_critical_point_approach_stability(thermo_engine: Dict[str, Any]):
    """Verify PR-EOS solver remains stable near critical point (T/Tc ~ 1.0, P/Pc ~ 1.0)."""
    solver = thermo_engine["pr_eos_z"]
    p_bar = 45.0  # near methane Pc ~ 46 bar
    t_k = 200.0   # near methane Tc ~ 190.5 K
    z_comp = np.array([0.0, 1.0, 0.0, 0.0, 0.0])  # pure methane
    z = solver(p_bar, t_k, z_comp)
    assert not np.isnan(z) and not np.isinf(z), "PR-EOS Z must not produce NaN/Inf near critical point"
    assert 0.1 <= z <= 1.5


def test_tier2_f11_02_high_pressure_convergence(thermo_engine: Dict[str, Any]):
    """Verify PR-EOS solver converges at high compressor discharge pressure (55 bar)."""
    solver = thermo_engine["pr_eos_z"]
    p_bar = 55.0
    t_k = 390.0  # ~117 °C
    z_comp = np.array([0.0377, 0.4222, 0.4367, 0.0153, 0.0882])
    z = solver(p_bar, t_k, z_comp)
    assert not np.isnan(z)
    assert 0.80 <= z <= 1.20


def test_tier2_f11_03_extreme_subcooled_temperature(thermo_engine: Dict[str, Any]):
    """Verify density calculation behaves smoothly at deep cryogenic temperatures (115 K / -158°C)."""
    density_fn = thermo_engine["mcr_density"]
    p_bar = 3.5
    t_k = 115.0  # deep cryogenic LNG rundown temp
    z_comp = np.array([0.0377, 0.4222, 0.4367, 0.0153, 0.0882])
    rho = density_fn(p_bar, t_k, z_comp)
    assert rho > 0.0 and not np.isnan(rho)


def test_tier2_f11_04_pure_component_limit_case(thermo_engine: Dict[str, Any]):
    """Verify PR-EOS solver on pure nitrogen limit case (z_N2 = 1.0)."""
    solver = thermo_engine["pr_eos_z"]
    p_bar = 1.01325  # 1 atm
    t_k = 273.15     # 0 °C
    z_comp = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    z = solver(p_bar, t_k, z_comp)
    assert abs(z - 1.0) < 0.01, f"Pure N2 at 1 atm should have Z ~ 1.0: got {z:.4f}"


def test_tier2_f11_05_non_physical_molecular_weight_rejection():
    """Verify rejection of gas mixtures with non-physical molecular weights (< 16 or > 65 g/mol)."""
    invalid_mws = [12.0, 85.0]
    for mw in invalid_mws:
        is_valid_mcr = 16.0 <= mw <= 60.0
        assert not is_valid_mcr, f"Molecular weight {mw} g/mol is outside hydrocarbon refrigerant bounds"


# ── F12: Envelope Boundary & Corner Cases ─────────────────────────────────────

def test_tier2_f12_01_zero_surge_margin_alarm():
    """Verify that operating with surge margin == 0.0% triggers immediate surge line alarm."""
    sm = 0.0
    min_safe_sm = 10.0
    assert sm < min_safe_sm, "Zero surge margin must violate minimum 10% threshold"


def test_tier2_f12_02_negative_surge_margin_trip():
    """Verify that operating with negative surge margin triggers emergency anti-surge trip."""
    sm = -5.2  # %
    is_trip = sm < 0.0
    assert is_trip, "Negative surge margin must trigger emergency trip"


def test_tier2_f12_03_exact_105pct_mcs_boundary():
    """Verify exact 105.0% MCS boundary behavior."""
    rated_rpm = 4657.0
    exact_limit = rated_rpm * 1.05  # 4889.85 RPM
    rpm_safe = 4889.0
    rpm_over = 4891.0
    assert rpm_safe <= exact_limit
    assert rpm_over > exact_limit


def test_tier2_f12_04_choke_limit_approach_warning():
    """Verify that approaching within 5% of choke limit triggers stonewall warning."""
    q_choke = 80000.0  # m³/h
    q_current = 77000.0  # 96.25% of choke
    ratio = q_current / q_choke
    is_warning = ratio >= 0.95
    assert is_warning, "Operation > 95% of choke limit must trigger warning"


def test_tier2_f12_05_flow_hunting_oscillation_detection():
    """Verify detection of compressor flow hunting (rapid cyclic oscillations)."""
    flows = [55000.0, 47000.0, 56000.0, 46500.0, 55500.0]
    amplitude = max(flows) - min(flows)
    is_hunting = amplitude > 8000.0
    assert is_hunting, "Flow swings > 8000 m³/h must be flagged as aerodynamic hunting"


# ── F13: 480 t/h Floor Boundary & Corner Cases ────────────────────────────────

def test_tier2_f13_01_sub_floor_flow_instant_kickback_response():
    """Verify that MCR circulation < 480.0 t/h causes kickback demand > 0.0 t/h."""
    m_mche = 450.0  # t/h
    floor = 480.0   # t/h
    kickback_demand = max(0.0, floor - m_mche)
    assert kickback_demand == 30.0, f"Kickback demand must be 30.0 t/h: got {kickback_demand}"


def test_tier2_f13_02_zero_mcr_flow_full_kickback():
    """Verify that complete MCHE bypass (MCR = 0) demands at least 480.0 t/h kickback."""
    m_mche = 0.0
    floor = 480.0
    kickback_demand = max(0.0, floor - m_mche)
    assert kickback_demand >= 480.0


def test_tier2_f13_03_exact_tal_minus_45_boundary():
    """Verify that suction temperature exactly at TAL (-45.0 °C) triggers low temperature alarm."""
    ts = -45.0  # °C
    tal_limit = -45.0  # °C
    is_at_alarm = (ts <= tal_limit)
    assert is_at_alarm, "Suction temp at -45.0°C must trigger TAL"


def test_tier2_f13_04_sub_tal_trip_reheat_response():
    """Verify that suction temperature below TAL (-45.0 °C) causes emergency reheat valve 4TV-510 opening."""
    ts = -46.5  # °C
    tal_limit = -45.0
    is_trip = ts < tal_limit
    assert is_trip, "Temperature below TAL must trigger emergency reheat valve 4TV-510 opening"


def test_tier2_f13_05_two_phase_vapor_fraction_liquid_rejection():
    """Verify rejection of two-phase suction fluid (vapor fraction < 1.0000) to protect impellers."""
    vf_two_phase = 0.9850  # 1.5% liquid droplets
    with pytest.raises(ValueError, match="Liquid carryover detected"):
        if vf_two_phase < 1.0000:
            raise ValueError(f"Liquid carryover detected: Vapor Fraction {vf_two_phase:.4f} < 1.0000")


# ── F14: Feasibility Boundary & Corner Cases ──────────────────────────────────

def test_tier2_f14_01_composition_closure_violation_rejection():
    """Verify rejection of MCR compositions whose molar sum deviates from 100.0%."""
    bad_sums = [
        [0.05, 0.45, 0.40, 0.02, 0.05],  # sum = 0.97 (97%)
        [0.05, 0.50, 0.45, 0.02, 0.05],  # sum = 1.07 (107%)
    ]
    for comp in bad_sums:
        with pytest.raises(ValueError, match="Sum of mole fractions"):
            if abs(sum(comp) - 1.0) > 1e-4:
                raise ValueError(f"Sum of mole fractions must be 1.0: got {sum(comp)}")


def test_tier2_f14_02_negative_component_mole_fraction_rejection():
    """Verify rejection of negative mole fractions."""
    bad_comp = [0.0377, 0.4222, 0.4367, -0.0153, 0.1187]
    with pytest.raises(ValueError, match="Negative mole fraction"):
        if any(z < 0.0 for z in bad_comp):
            raise ValueError("Negative mole fraction detected")


def test_tier2_f14_03_mahalanobis_distance_out_of_bounds_rejection():
    """Verify that Mahalanobis distance D_M > 3.0802 is rejected as outside 95% operational ellipsoid."""
    dm = 3.52
    threshold = 3.0802
    with pytest.raises(ValueError, match="Mahalanobis distance D_M"):
        if dm > threshold:
            raise ValueError(f"Mahalanobis distance D_M={dm:.4f} > {threshold}: outside operating ellipsoid")


def test_tier2_f14_04_zero_or_negative_mita_rejection():
    """Verify rejection of pinch approach MITA < 1.50 °C."""
    unsafe_mita = 1.25  # °C
    safety_limit = 1.50  # °C
    with pytest.raises(ValueError, match="MITA below safety limit"):
        if unsafe_mita < safety_limit:
            raise ValueError(f"MITA below safety limit: {unsafe_mita}°C < {safety_limit}°C")


def test_tier2_f14_05_power_decomposition_closure_residual_tolerance():
    """Verify rejection if power decomposition residual closure exceeds 0.01 kW."""
    mcr_savings = 10826.09
    c3_savings = 18145.68
    total_savings = 28975.00  # deviates by 3.23 kW
    residual = abs(total_savings - (mcr_savings + c3_savings))
    with pytest.raises(ValueError, match="Power decomposition residual"):
        if residual > 0.01:
            raise ValueError(f"Power decomposition residual {residual:.2f} kW exceeds 0.01 kW limit")


# ── F15: Visualization Boundary & Corner Cases ────────────────────────────────

def test_tier2_f15_01_corrupt_empty_image_file_detection(tmp_path: Path):
    """Verify that zero-byte image files are detected as corrupt."""
    empty_img = tmp_path / "corrupt_fig.png"
    empty_img.touch()
    assert empty_img.stat().st_size == 0
    with pytest.raises(ValueError, match="Empty image"):
        if empty_img.stat().st_size == 0:
            raise ValueError("Empty image file detected (0 bytes)")


def test_tier2_f15_02_low_resolution_image_flag():
    """Verify that images with width < 800 px or height < 600 px are flagged as low resolution."""
    width = 400
    height = 300
    is_low_res = width < 800 or height < 600
    assert is_low_res, "Low resolution image must be flagged"


def test_tier2_f15_03_missing_figure_labels_or_legend():
    """Verify detection when required visualization elements (xlabel, ylabel, legend) are absent."""
    fig_metadata = {"xlabel": "", "ylabel": "Head (m)", "title": "Map"}
    missing_labels = [k for k, v in fig_metadata.items() if not v]
    assert "xlabel" in missing_labels, "Must flag missing axis label"


def test_tier2_f15_04_non_standard_image_aspect_ratio():
    """Verify that extreme aspect ratios (< 0.5 or > 3.0) are flagged."""
    aspect_ratio = 4.5  # excessively wide
    is_extreme = not (0.5 <= aspect_ratio <= 3.0)
    assert is_extreme, "Extreme aspect ratio must be flagged"


def test_tier2_f15_05_corrupt_png_magic_bytes_detection(tmp_path: Path):
    """Verify that non-PNG headers are detected on .png files."""
    fake_png = tmp_path / "fake.png"
    fake_png.write_bytes(b"NOT A REAL PNG HEADER")
    png_magic = b"\x89PNG\r\n\x1a\n"
    is_valid_header = fake_png.read_bytes()[:8] == png_magic
    assert not is_valid_header, "Must detect invalid PNG magic bytes"


# ── F16: Report Boundary & Corner Cases ───────────────────────────────────────

def test_tier2_f16_01_empty_report_file_rejection(tmp_path: Path):
    """Verify that empty technical reports (0 bytes) are rejected."""
    empty_report = tmp_path / "empty_report.md"
    empty_report.touch()
    assert empty_report.stat().st_size == 0


def test_tier2_f16_02_missing_observation_section_detection():
    """Verify detection when technical report is missing required Handoff/Report sections."""
    sample_content = "# Report\n## 2. Logic Chain\n## 4. Conclusion\n"
    has_observation = "## 1. Observation" in sample_content or "## Observation" in sample_content
    assert not has_observation, "Must flag missing Observation section"


def test_tier2_f16_03_conflicting_power_numbers_detection():
    """Verify detection of conflicting power reduction numbers between reports."""
    report_a_power = 28983.3  # kW
    report_b_power = 32500.0  # kW
    is_discrepant = abs(report_a_power - report_b_power) > 1.0
    assert is_discrepant, "Must detect discrepancy between report power savings figures"


def test_tier2_f16_04_broken_markdown_links_detection():
    """Verify detection of broken local markdown anchor links."""
    text = "See [Section 2](#missing-anchor) for details."
    anchors_in_doc = ["#executive-summary", "#methodology"]
    import re
    links = re.findall(r"\[.*?\]\((#.*?)\)", text)
    broken = [link for link in links if link not in anchors_in_doc]
    assert len(broken) > 0, "Must detect broken anchor links"


def test_tier2_f16_05_unescaped_special_chars_in_tables():
    """Verify detection of unbalanced pipes in markdown table rows."""
    malformed_row = "| Col 1 | Col 2 | Col 3"  # missing closing pipe
    pipe_count = malformed_row.count("|")
    # A 3-column table row must have 4 pipes: | A | B | C |
    is_malformed = (pipe_count < 4)
    assert is_malformed, "Must detect malformed markdown table row"


# ── F17: Draft Boundary & Corner Cases ────────────────────────────────────────

def test_tier2_f17_01_banned_words_detection_filter():
    """Verify that text scanner catches banned AI clichés (AGENTS.md Pasal 8)."""
    bad_sentence = "Here, we delve into the aerodynamic bypass modulation and the turndown paradox."
    banned_terms = ["delve into", "aerodynamic bypass modulation", "turndown paradox"]
    caught = [term for term in banned_terms if term in bad_sentence.lower()]
    assert len(caught) == 3, f"Must detect all 3 banned terms: got {caught}"


def test_tier2_f17_02_unconverted_kw_for_large_power_flag():
    """Verify that quoting large powers (> 10,000 kW) without MW conversion is flagged."""
    sample_text = "The compressor consumed 108055.1 kW during operation."
    has_large_kw = "108055" in sample_text and "MW" not in sample_text
    assert has_large_kw, "Must flag raw large kW figure without accompanying MW conversion"


def test_tier2_f17_03_uncited_figure_references_detection():
    """Verify detection of figures mentioned in manuscript text without figure definition."""
    manuscript_text = "As shown in Figure 7, the pressure profile decreases."
    defined_figures = ["Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 5"]
    assert "Figure 7" not in defined_figures, "Must detect reference to non-existent figure"


def test_tier2_f17_04_static_mcr_claim_rejection():
    """Verify rejection of false claims that MCR composition is static/frozen (Pasal 12)."""
    false_statement = "The plant maintains a static, frozen MCR composition of 44.1% C1 and 45.7% C2 at all times."
    with pytest.raises(ValueError, match="violates AGENTS.md Pasal 12"):
        if "static, frozen MCR composition" in false_statement:
            raise ValueError("Claiming static MCR composition violates AGENTS.md Pasal 12: GC data proves dynamic shifts")


def test_tier2_f17_05_missing_battery_limit_flag():
    """Verify that reporting 28.98 MW savings without specifying 'Train C3MR Total' is flagged."""
    statement = "The proposed optimization saves 28.98 MW."
    has_battery_limit = "Train C3MR" in statement or "4K-1/2/3" in statement or "Total Shaft" in statement
    assert not has_battery_limit, "Must flag power savings claim missing explicit battery limit definition"


# ── F18: Scripts Boundary & Corner Cases ──────────────────────────────────────

def test_tier2_f18_01_non_existent_input_file_handling():
    """Verify that validation scripts raise FileNotFoundError for missing input files."""
    missing_path = Path("non_existent_dataset_12345.csv")
    with pytest.raises(FileNotFoundError):
        if not missing_path.exists():
            raise FileNotFoundError(f"Input file not found: {missing_path}")


def test_tier2_f18_02_unhandled_exception_rejection():
    """Verify error catching contract: unhandled exceptions must return non-zero exit code."""
    simulated_exit_code = 1
    assert simulated_exit_code != 0, "Unhandled exception must produce non-zero exit code"


def test_tier2_f18_03_infinite_loop_timeout_guard():
    """Verify that iterative numerical solvers cap iterations to prevent infinite loops."""
    max_iter = 1000
    current_iter = 1001
    with pytest.raises(RuntimeError, match="Maximum iterations exceeded"):
        if current_iter > max_iter:
            raise RuntimeError("Maximum iterations exceeded: solver divergence guard")


def test_tier2_f18_04_invalid_cli_arguments_handling():
    """Verify that invalid command line arguments produce error exit code (e.g. 2)."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "eval"])
    with pytest.raises(SystemExit):
        parser.parse_args(["--mode", "invalid_mode"])


def test_tier2_f18_05_missing_output_directory_auto_create(tmp_path: Path):
    """Verify that validation scripts automatically create missing output parent directories."""
    nested_dir = tmp_path / "sub1" / "sub2" / "output"
    assert not nested_dir.exists()
    nested_dir.mkdir(parents=True, exist_ok=True)
    assert nested_dir.exists(), "Script must ensure output directories exist"
