"""
PRIORITY 2 — RECONSTRUCT TRUE ENERGY BASELINE
Separate: header steam, individual turbine steam, bypass, condensate, calculated power.
Reconstruct shaft power from compressor OEM curves (model-derived).
Do NOT use steam/4.040 as power measurement.
"""
import os, json, csv
import pandas as pd
import numpy as np
import CoolProp.CoolProp as CP

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "02_energy_baseline")
os.makedirs(OUT_DIR, exist_ok=True)

DATA_DIR = os.path.join(BASE_DIR, "ikms_2026", "data")
df_base = pd.read_csv(os.path.join(DATA_DIR, "reconciliation",
                                    "baseline_hysys_vs_dcs_validation_p1_p100.csv"))

# =============================================================================
# STEP 1: RECONSTRUCT STEAM BUDGET WITH PHYSICAL STREAM SEPARATION
# =============================================================================
steam_budget = []

for _, row in df_base.iterrows():
    q = int(row["percentile"])
    total_header = float(row["total_driver_steam_t_h"])
    
    # Individual turbine steam — may be NaN for P62-P100
    c3_steam = row.get("c3_turb_steam_t_h", np.nan)
    lp_steam = row.get("mcr_lp_turb_steam_t_h", np.nan)
    hp_steam = row.get("mcr_hp_turb_steam_t_h", np.nan)
    
    # Predicted turbine flows (regression-derived)
    pred_c3 = row.get("pred_c3_turb_steam_t_h", np.nan)
    pred_lp = row.get("pred_mcr_lp_turb_steam_t_h", np.nan)
    pred_hp = row.get("pred_mcr_hp_turb_steam_t_h", np.nan)
    pred_sum = row.get("pred_sum_turbines_t_h", np.nan)
    
    # Sum of measured individual turbines
    if pd.notna(c3_steam) and pd.notna(lp_steam) and pd.notna(hp_steam):
        meas_sum = c3_steam + lp_steam + hp_steam
        meas_available = True
    else:
        meas_sum = np.nan
        meas_available = False
    
    # Bypass & balancing steam = header minus turbine consumption
    if meas_available:
        bypass_steam = total_header - meas_sum
    elif pd.notna(pred_sum):
        bypass_steam = total_header - pred_sum
    else:
        bypass_steam = np.nan
    
    steam_budget.append({
        "percentile": q,
        "operating_hours_yr": float(row["operating_hours_yr"]),
        "total_header_steam_t_h": round(total_header, 2),
        "c3_turb_steam_measured_t_h": round(c3_steam, 2) if pd.notna(c3_steam) else None,
        "mcr_lp_turb_steam_measured_t_h": round(lp_steam, 2) if pd.notna(lp_steam) else None,
        "mcr_hp_turb_steam_measured_t_h": round(hp_steam, 2) if pd.notna(hp_steam) else None,
        "measured_sum_turbines_t_h": round(meas_sum, 2) if pd.notna(meas_sum) else None,
        "individual_turbine_data_available": meas_available,
        "pred_c3_turb_steam_t_h": round(pred_c3, 2) if pd.notna(pred_c3) else None,
        "pred_mcr_lp_turb_steam_t_h": round(pred_lp, 2) if pd.notna(pred_lp) else None,
        "pred_mcr_hp_turb_steam_t_h": round(pred_hp, 2) if pd.notna(pred_hp) else None,
        "pred_sum_turbines_t_h": round(pred_sum, 2) if pd.notna(pred_sum) else None,
        "bypass_balancing_steam_t_h": round(bypass_steam, 2) if pd.notna(bypass_steam) else None,
        "legacy_power_steam_div_4040_MW": round(total_header / 4.040, 2),
        "legacy_power_classification": "CIRCULAR SYNTHETIC (NOT INDEPENDENT MEASUREMENT)",
    })

df_steam = pd.DataFrame(steam_budget)
df_steam.to_csv(os.path.join(OUT_DIR, "steam_budget_decomposition.csv"), index=False)

# Quantify coverage
n_meas = df_steam["individual_turbine_data_available"].sum()
print(f"Individual turbine steam available: {n_meas}/100 quantiles ({n_meas}%)")

# =============================================================================
# STEP 2: IAPWS-IF97 TURBINE THERMODYNAMIC SCENARIOS
# Verify inlet state per turbine — check if they share identical conditions
# =============================================================================
# Train H HP steam header documented conditions
# Source: Badak LNG Plant specifications and P&ID instrument list
steam_scenarios = []

# Scenario A: Common header (60 barg, 440 C) — assumed identical for all turbines
p_in_bar = 61.013  # 60 barg + 1.01325 bara = 61.013 bara
t_in_K = 713.15     # 440 C

# Exhaust: surface condenser
p_ex_bar = 0.12      # 0.12 bara

h_in = CP.PropsSI('H', 'P', p_in_bar * 1e5, 'T', t_in_K, 'IF97::Water') / 1e3  # kJ/kg
s_in = CP.PropsSI('S', 'P', p_in_bar * 1e5, 'T', t_in_K, 'IF97::Water') / 1e3  # kJ/(kg·K)
h_ex_s = CP.PropsSI('H', 'P', p_ex_bar * 1e5, 'S', s_in * 1e3, 'IF97::Water') / 1e3  # kJ/kg
delta_h_s = h_in - h_ex_s  # isentropic enthalpy drop

# Machine-specific scenarios
turbine_configs = [
    {"tag": "4KT-1", "service": "C3 Propane Compressor Driver",
     "assumed_eta_s": 0.752, "assumed_eta_m": 0.985,
     "inlet_note": "Common HP header (60 barg, 440°C) — ASSUMED IDENTICAL, NOT INDEPENDENTLY VERIFIED",
     "exhaust_note": "Surface condenser 0.12 bara — ASSUMED"},
    {"tag": "4KT-2", "service": "MCR LP Compressor Driver",
     "assumed_eta_s": 0.766, "assumed_eta_m": 0.985,
     "inlet_note": "Common HP header (60 barg, 440°C) — ASSUMED IDENTICAL, NOT INDEPENDENTLY VERIFIED",
     "exhaust_note": "Surface condenser 0.12 bara — ASSUMED"},
    {"tag": "4KT-3", "service": "MCR HP Compressor Driver",
     "assumed_eta_s": 0.780, "assumed_eta_m": 0.985,
     "inlet_note": "Common HP header (60 barg, 440°C) — ASSUMED IDENTICAL, NOT INDEPENDENTLY VERIFIED",
     "exhaust_note": "Surface condenser 0.12 bara — ASSUMED"},
]

for tc in turbine_configs:
    eta_overall = tc["assumed_eta_s"] * tc["assumed_eta_m"]
    actual_dh = delta_h_s * tc["assumed_eta_s"]
    sr = 3600.0 / (delta_h_s * eta_overall)
    steam_scenarios.append({
        "turbine_tag": tc["tag"],
        "service": tc["service"],
        "inlet_pressure_bara": p_in_bar,
        "inlet_temperature_C": 440.0,
        "inlet_enthalpy_kJ_kg": round(h_in, 2),
        "inlet_entropy_kJ_kgK": round(s_in, 4),
        "exhaust_pressure_bara": p_ex_bar,
        "isentropic_exhaust_enthalpy_kJ_kg": round(h_ex_s, 2),
        "isentropic_delta_h_kJ_kg": round(delta_h_s, 2),
        "assumed_isentropic_efficiency": tc["assumed_eta_s"],
        "assumed_mechanical_efficiency": tc["assumed_eta_m"],
        "actual_delta_h_kJ_kg": round(actual_dh, 2),
        "specific_steam_rate_t_MWh": round(sr, 3),
        "inlet_state_verification": tc["inlet_note"],
        "exhaust_state_verification": tc["exhaust_note"],
        "efficiency_source": "ENGINEERING ESTIMATE (NOT OEM TEST REPORT)",
        "classification": "CONDITIONAL THERMODYNAMIC SCENARIO",
    })

df_turb = pd.DataFrame(steam_scenarios)
df_turb.to_csv(os.path.join(OUT_DIR, "turbine_thermodynamic_scenarios.csv"), index=False)

# =============================================================================
# STEP 3: MODEL-DERIVED COMPRESSOR SHAFT POWER FROM OEM CURVES
# Use digitized compressor curves to calculate shaft power independently
# =============================================================================
comp_power_records = []

# Load digitized OEM data for each compressor
for comp_tag in ["4K1", "4K2", "4K3"]:
    curve_file = os.path.join(DATA_DIR, "digitized", f"compressor_curves_{comp_tag}.csv")
    if not os.path.exists(curve_file):
        comp_power_records.append({
            "compressor_tag": comp_tag.replace("K", "K-"),
            "oem_curves_available": False,
            "n_curve_points": 0,
        })
        continue
    
    df_curve = pd.read_csv(curve_file)
    n_points = len(df_curve)
    speed_range = df_curve["speed_pct"].unique()
    curve_types = df_curve["curve_type"].unique()
    
    comp_power_records.append({
        "compressor_tag": comp_tag.replace("K", "K-"),
        "oem_curves_available": True,
        "n_curve_points": n_points,
        "speed_pct_range": f"{min(speed_range):.0f}-{max(speed_range):.0f}%",
        "available_curve_types": ", ".join(sorted(curve_types)),
        "source_file": f"ikms_2026/data/digitized/compressor_curves_{comp_tag}.csv",
    })

# Load mapped operating points
opm_file = os.path.join(DATA_DIR, "processed", "compressor_mapped_operating_points.csv")
df_opm = pd.read_csv(opm_file)

# Build quantile-level model-derived shaft power
quantile_power = []
for q_label in df_opm["load_quantile"].unique():
    try:
        q_num = int(q_label.replace("P", "").split("_")[0])
    except Exception:
        continue
    df_q = df_opm[df_opm["load_quantile"] == q_label]
    
    # Find baseline operating mode
    df_bl = df_q[df_q["operating_mode"] == "Baseline"]
    
    if len(df_bl) == 0:
        continue
    
    total_shaft_kw = df_bl["shaft_power_kw"].sum()
    total_shaft_mw = total_shaft_kw / 1000.0
    
    # Get per-machine breakdown
    machine_powers = {}
    for _, mrow in df_bl.iterrows():
        tag = mrow["casing_tag"]
        machine_powers[tag] = {
            "shaft_power_kw": round(float(mrow["shaft_power_kw"]), 1),
            "shaft_power_mw": round(float(mrow["shaft_power_mw"]), 3),
            "polytropic_efficiency": round(float(mrow["polytropic_efficiency"]), 4),
            "speed_rpm": float(mrow["speed_rpm"]),
            "mass_flow_t_h": round(float(mrow["mass_flow_t_h"]), 1),
            "pressure_ratio": round(float(mrow["pressure_ratio"]), 4),
            "surge_margin_pct": round(float(mrow["surge_margin_pct"]), 2),
            "is_surge_safe": bool(mrow["is_surge_safe"]),
        }
    
    # Compare to legacy steam/4.040
    row_base = df_base[df_base["percentile"] == q_num]
    legacy_power = float(row_base["total_compressor_power_steam_MW"].values[0]) if len(row_base) > 0 else np.nan
    
    quantile_power.append({
        "percentile": q_num,
        "model_derived_total_shaft_MW": round(total_shaft_mw, 3),
        "legacy_steam_div_4040_MW": round(legacy_power, 3) if pd.notna(legacy_power) else None,
        "difference_MW": round(total_shaft_mw - legacy_power, 3) if pd.notna(legacy_power) else None,
        "relative_diff_pct": round((total_shaft_mw - legacy_power) / legacy_power * 100, 2) if pd.notna(legacy_power) and legacy_power > 0 else None,
        "power_classification": "MODEL-DERIVED (OEM CURVE INTERPOLATION)",
        "n_machines_in_sum": len(machine_powers),
        "machines": machine_powers,
    })

# Save as flat CSV (without nested machines dict)
flat_power = []
for qp in quantile_power:
    flat_power.append({
        "percentile": qp["percentile"],
        "model_derived_total_shaft_MW": qp["model_derived_total_shaft_MW"],
        "legacy_steam_div_4040_MW": qp["legacy_steam_div_4040_MW"],
        "difference_MW": qp["difference_MW"],
        "relative_diff_pct": qp["relative_diff_pct"],
        "power_classification": qp["power_classification"],
        "n_machines_in_sum": qp["n_machines_in_sum"],
    })

df_power = pd.DataFrame(flat_power)
df_power.to_csv(os.path.join(OUT_DIR, "model_derived_shaft_power.csv"), index=False)

# Save detailed JSON with machine breakdown
with open(os.path.join(OUT_DIR, "model_derived_shaft_power_detail.json"), "w") as fp:
    json.dump(quantile_power, fp, indent=2)

# =============================================================================
# STEP 4: ANNUAL STEAM RECONCILIATION
# =============================================================================
h_yr = df_base["operating_hours_yr"].values
total_header_steam = df_base["total_driver_steam_t_h"].values

# Method 1: Full header integration
annual_header_kt = float(np.sum(h_yr * total_header_steam) / 1000.0)

# Method 2: Predicted 3-turbine sum
pred_sum = df_base["pred_sum_turbines_t_h"].values
annual_pred_3turb_kt = float(np.nansum(h_yr * pred_sum) / 1000.0)

# Method 3: Measured 3-turbine sum (where available)
meas_c3 = df_base["c3_turb_steam_t_h"].values
meas_lp = df_base["mcr_lp_turb_steam_t_h"].values
meas_hp = df_base["mcr_hp_turb_steam_t_h"].values
meas_sum_vals = np.where(
    np.isnan(meas_c3) | np.isnan(meas_lp) | np.isnan(meas_hp),
    np.nan,
    meas_c3 + meas_lp + meas_hp
)
mask_valid = ~np.isnan(meas_sum_vals)
annual_meas_3turb_partial_kt = float(np.sum(h_yr[mask_valid] * meas_sum_vals[mask_valid]) / 1000.0)
hours_covered_meas = float(np.sum(h_yr[mask_valid]))

# Bypass/balancing steam
bypass_per_q = np.where(mask_valid, total_header_steam - meas_sum_vals, np.nan)
mean_bypass_where_available = float(np.nanmean(bypass_per_q))

steam_recon = {
    "method_1_full_header_integration": {
        "annual_steam_kt_yr": round(annual_header_kt, 2),
        "mean_flow_t_h": round(float(np.mean(total_header_steam)), 2),
        "source": "total_driver_steam_t_h (plant header meter)",
        "coverage": "100 quantiles, 7849.61 operating hours",
        "classification": "PRIMARY PHYSICAL MEASUREMENT",
    },
    "method_2_predicted_3_turbine_sum": {
        "annual_steam_kt_yr": round(annual_pred_3turb_kt, 2),
        "mean_flow_t_h": round(float(np.nanmean(pred_sum)), 2),
        "source": "pred_sum_turbines_t_h (regression model)",
        "coverage": "100 quantiles",
        "classification": "MODEL-DERIVED (REGRESSION PREDICTION)",
    },
    "method_3_measured_individual_turbines": {
        "annual_steam_partial_kt_yr": round(annual_meas_3turb_partial_kt, 2),
        "n_quantiles_with_data": int(mask_valid.sum()),
        "hours_covered": round(hours_covered_meas, 1),
        "source": "c3_turb_steam + mcr_lp_turb_steam + mcr_hp_turb_steam",
        "classification": "DIRECT MEASUREMENT (PARTIAL COVERAGE)",
    },
    "bypass_balancing_steam": {
        "mean_where_measured_t_h": round(mean_bypass_where_available, 2),
        "note": "Difference between header meter and sum of 3 turbines where individual data available",
        "classification": "DERIVED RESIDUAL",
    },
    "legacy_value_2935_9_kt": {
        "source": "rebuild_v3 (374.02 t/h × 7849.61 h)",
        "classification": "SUPERSEDED — USES PREDICTED 3-TURBINE MEAN ONLY",
    },
    "reconciliation_delta_kt": round(annual_header_kt - annual_pred_3turb_kt, 2),
    "reconciliation_delta_pct": round((annual_header_kt - annual_pred_3turb_kt) / annual_pred_3turb_kt * 100, 2),
}

with open(os.path.join(OUT_DIR, "annual_steam_reconciliation.json"), "w") as fp:
    json.dump(steam_recon, fp, indent=2)

# =============================================================================
# STEP 5: POWER-WEIGHTED STEAM RATE CALCULATION
# =============================================================================
sr_records = []
for tc in steam_scenarios:
    sr_records.append({
        "turbine_tag": tc["turbine_tag"],
        "specific_steam_rate_t_MWh": tc["specific_steam_rate_t_MWh"],
        "classification": tc["classification"],
    })

# Weighted average using P1-P61 mean flows (where individual data available)
mask_p1_p61 = (df_base["percentile"] <= 61) & pd.notna(df_base["c3_turb_steam_t_h"])
if mask_p1_p61.sum() > 0:
    m_c3_mean = df_base.loc[mask_p1_p61, "c3_turb_steam_t_h"].mean()
    m_lp_mean = df_base.loc[mask_p1_p61, "mcr_lp_turb_steam_t_h"].mean()
    m_hp_mean = df_base.loc[mask_p1_p61, "mcr_hp_turb_steam_t_h"].mean()
    
    sr_4kt1 = steam_scenarios[0]["specific_steam_rate_t_MWh"]
    sr_4kt2 = steam_scenarios[1]["specific_steam_rate_t_MWh"]
    sr_4kt3 = steam_scenarios[2]["specific_steam_rate_t_MWh"]
    
    p_c3 = m_c3_mean / sr_4kt1
    p_lp = m_lp_mean / sr_4kt2
    p_hp = m_hp_mean / sr_4kt3
    
    wtd_sr = (m_c3_mean + m_lp_mean + m_hp_mean) / (p_c3 + p_lp + p_hp)
else:
    wtd_sr = np.nan

steam_rate_summary = {
    "legacy_circular_rate_t_MWh": 4.040,
    "legacy_classification": "CIRCULAR (2935.9 kt / 726.7 GWh, where GWh = kt / 4.040)",
    "iapws_machine_weighted_rate_t_MWh": round(wtd_sr, 3),
    "iapws_classification": "CONDITIONAL THERMODYNAMIC SCENARIO (ASSUMED EFFICIENCIES)",
    "iapws_ideal_isentropic_rate_t_MWh": round(3600.0 / delta_h_s, 3),
    "machines": sr_records,
    "recommendation": "Use machine-specific rates with stated uncertainty on isentropic efficiency assumptions."
}

with open(os.path.join(OUT_DIR, "steam_rate_reconciliation.json"), "w") as fp:
    json.dump(steam_rate_summary, fp, indent=2)

print(f"P2 complete:")
print(f"  Steam budget: {len(steam_budget)} quantiles decomposed")
print(f"  Turbine scenarios: {len(steam_scenarios)} machines")
print(f"  Model-derived power: {len(quantile_power)} quantiles")
print(f"  Annual steam (header): {annual_header_kt:.2f} kt/yr")
print(f"  Annual steam (pred 3-turb): {annual_pred_3turb_kt:.2f} kt/yr")
print(f"  Delta: {annual_header_kt - annual_pred_3turb_kt:.2f} kt/yr ({(annual_header_kt - annual_pred_3turb_kt)/annual_pred_3turb_kt*100:.2f}%)")
print(f"  Weighted steam rate (IAPWS): {wtd_sr:.3f} t/MWh")
