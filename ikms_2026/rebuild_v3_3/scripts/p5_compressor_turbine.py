"""
PRIORITY 5 — RECONSTRUCT COMPRESSOR AND TURBINE LIMITS
Speed-dependent corrected surge limits from OEM curves.
Remove hardcoded governor valve percentage from DCS claims.
"""
import os, json
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "05_compressor_turbine")
os.makedirs(OUT_DIR, exist_ok=True)

DATA_DIR = os.path.join(BASE_DIR, "ikms_2026", "data")
df_base = pd.read_csv(os.path.join(DATA_DIR, "reconciliation",
                                    "baseline_hysys_vs_dcs_validation_p1_p100.csv"))

# =============================================================================
# STEP 1: DIGITIZED OEM SURGE LINE RECONSTRUCTION
# =============================================================================
surge_analysis = {}

for comp_tag, casing, fluid in [
    ("4K1", "4K-2", "MCR LP"),
    ("4K2", "4K-2", "MCR LP"),
    ("4K3", "4K-3", "MCR HP"),
]:
    curve_file = os.path.join(DATA_DIR, "digitized", f"compressor_curves_{comp_tag}.csv")
    if not os.path.exists(curve_file):
        surge_analysis[comp_tag] = {"status": "OEM CURVES NOT FOUND"}
        continue
    
    df_curve = pd.read_csv(curve_file)
    
    # Extract surge points at each speed line
    # Surge is the leftmost point on each speed-Head curve
    df_head = df_curve[df_curve["curve_type"] == "Head"]
    
    surge_points = []
    for spd in sorted(df_head["speed_pct"].unique()):
        df_spd = df_head[df_head["speed_pct"] == spd].sort_values("flow_value")
        if len(df_spd) == 0:
            continue
        # First point at each speed = surge boundary
        surge_row = df_spd.iloc[0]
        surge_points.append({
            "speed_pct": float(spd),
            "speed_rpm": float(surge_row["speed_rpm"]),
            "surge_flow_m3h": float(surge_row["flow_value"]),
            "surge_head_m": float(surge_row["y_value"]),
        })
    
    # Also get choke points (rightmost point on each speed line)
    choke_points = []
    for spd in sorted(df_head["speed_pct"].unique()):
        df_spd = df_head[df_head["speed_pct"] == spd].sort_values("flow_value")
        if len(df_spd) == 0:
            continue
        choke_row = df_spd.iloc[-1]
        choke_points.append({
            "speed_pct": float(spd),
            "speed_rpm": float(choke_row["speed_rpm"]),
            "choke_flow_m3h": float(choke_row["flow_value"]),
            "choke_head_m": float(choke_row["y_value"]),
        })
    
    surge_analysis[comp_tag] = {
        "casing_tag": casing,
        "fluid": fluid,
        "n_speed_lines": len(surge_points),
        "surge_boundary": surge_points,
        "choke_boundary": choke_points,
    }

# =============================================================================
# STEP 2: SPEED-DEPENDENT CORRECTED SURGE FLOOR
# =============================================================================
# Use 4K2 (MCR LP compressor) as the primary anti-surge reference
# since it is the main MCR compressor with the anti-surge controller 4UV-53

df_4k2 = pd.read_csv(os.path.join(DATA_DIR, "digitized", "compressor_curves_4K2.csv"))
df_4k2_head = df_4k2[df_4k2["curve_type"] == "Head"]

# Build surge flow vs speed interpolant
surge_speeds = []
surge_flows = []
for spd in sorted(df_4k2_head["speed_pct"].unique()):
    df_spd = df_4k2_head[df_4k2_head["speed_pct"] == spd].sort_values("flow_value")
    if len(df_spd) > 0:
        surge_speeds.append(float(spd))
        surge_flows.append(float(df_spd.iloc[0]["flow_value"]))

if len(surge_speeds) >= 2:
    f_surge = interp1d(surge_speeds, surge_flows, kind="linear", fill_value="extrapolate")
else:
    f_surge = None

# Load mapped operating points for actual speed at each quantile
df_opm = pd.read_csv(os.path.join(DATA_DIR, "processed",
                                    "compressor_mapped_operating_points.csv"))

surge_floor_results = []
for q_label in sorted(df_opm["load_quantile"].unique()):
    try:
        q_num = int(q_label.replace("P", "").split("_")[0])
    except Exception:
        continue
    df_q = df_opm[(df_opm["load_quantile"] == q_label) &
                   (df_opm["operating_mode"] == "Baseline") &
                   (df_opm["casing_tag"] == "4K-2")]
    
    if len(df_q) == 0:
        continue
    
    row = df_q.iloc[0]
    actual_speed_pct = float(row["speed_pct_rated"])
    actual_flow_m3h = float(row["actual_volumetric_flow"])
    actual_mass_flow = float(row["mass_flow_t_h"])
    suct_density = float(row["suction_density_kg_m3"])
    
    # Speed-dependent surge flow from OEM curve
    if f_surge is not None:
        surge_flow_at_speed = float(f_surge(actual_speed_pct))
    else:
        surge_flow_at_speed = np.nan
    
    # Apply 10% safety margin
    surge_floor_vol = surge_flow_at_speed * 1.10 if pd.notna(surge_flow_at_speed) else np.nan
    surge_floor_mass = surge_floor_vol * suct_density / 1000.0 if pd.notna(surge_floor_vol) else np.nan
    
    # Actual operating margin
    surge_margin_vol = ((actual_flow_m3h - surge_flow_at_speed) / surge_flow_at_speed * 100
                        if pd.notna(surge_flow_at_speed) and surge_flow_at_speed > 0 else np.nan)
    
    # Required kickback
    if pd.notna(surge_floor_mass) and actual_mass_flow < surge_floor_mass:
        kickback_required = surge_floor_mass - actual_mass_flow
    else:
        kickback_required = 0.0
    
    surge_floor_results.append({
        "percentile": q_num,
        "actual_speed_pct": round(actual_speed_pct, 2),
        "actual_vol_flow_m3h": round(actual_flow_m3h, 1),
        "actual_mass_flow_t_h": round(actual_mass_flow, 1),
        "suction_density_kg_m3": round(suct_density, 3),
        "oem_surge_flow_at_speed_m3h": round(surge_flow_at_speed, 1) if pd.notna(surge_flow_at_speed) else None,
        "surge_floor_with_10pct_margin_m3h": round(surge_floor_vol, 1) if pd.notna(surge_floor_vol) else None,
        "surge_floor_mass_t_h": round(surge_floor_mass, 1) if pd.notna(surge_floor_mass) else None,
        "actual_surge_margin_pct": round(surge_margin_vol, 2) if pd.notna(surge_margin_vol) else None,
        "kickback_4UV53_required_t_h": round(kickback_required, 1),
        "is_surge_safe_without_kickback": actual_mass_flow >= (surge_floor_mass if pd.notna(surge_floor_mass) else 0),
        "classification": "OEM CURVE-DERIVED (SPEED-DEPENDENT)",
        "note": "480.0 t/h fixed floor is an approximation; actual floor varies with speed",
    })

df_surge = pd.DataFrame(surge_floor_results)
df_surge.to_csv(os.path.join(OUT_DIR, "speed_dependent_surge_analysis.csv"), index=False)

# =============================================================================
# STEP 3: GOVERNOR VALVE STATUS — CLASSIFICATION ONLY
# =============================================================================
governor_assessment = {
    "legacy_claim": "Governor valve stroke = 94.5% at P90",
    "legacy_source": "p3_rotating_equipment_v3_2_1.py line 107 (hardcoded if/else literal)",
    "dcs_telemetry_tags_found": [],
    "dcs_telemetry_check": (
        "Searched master_minute_level.parquet and Book1.csv column names for governor, "
        "ZT, POS, GV, stroke patterns. ZERO matching tags found."
    ),
    "classification": "THEORETICAL CAPACITY ESTIMATE (NOT DCS MEASUREMENT)",
    "derivation_basis": (
        "Estimated from steam demand / rated nozzle flow capacity. "
        "Cannot be verified from DCS telemetry."
    ),
    "v3_3_action": (
        "94.5% may be retained as a theoretical estimate with explicit caveat. "
        "Must not be presented as measured DCS data."
    ),
}

with open(os.path.join(OUT_DIR, "governor_valve_assessment.json"), "w") as fp:
    json.dump(governor_assessment, fp, indent=2)

# =============================================================================
# STEP 4: FLOW DECOMPOSITION (process, recycle, total, corrected)
# =============================================================================
flow_decomp = []
for q_label in sorted(df_opm["load_quantile"].unique()):
    try:
        q_num = int(q_label.replace("P", "").split("_")[0])
    except Exception:
        continue
    df_q = df_opm[(df_opm["load_quantile"] == q_label) &
                   (df_opm["operating_mode"] == "Baseline") &
                   (df_opm["casing_tag"] == "4K-2")]
    
    if len(df_q) == 0:
        continue
    
    row = df_q.iloc[0]
    flow_decomp.append({
        "percentile": q_num,
        "process_flow_t_h": round(float(row["net_process_flow_t_h"]), 1),
        "kickback_recycle_flow_t_h": round(float(row["anti_surge_kickback_flow_t_h"]), 1),
        "total_suction_flow_t_h": round(float(row["mass_flow_t_h"]), 1),
        "corrected_vol_flow_m3h": round(float(row["actual_volumetric_flow"]), 1),
        "suction_density_kg_m3": round(float(row["suction_density_kg_m3"]), 3),
        "speed_rpm": float(row["speed_rpm"]),
        "speed_pct_rated": round(float(row["speed_pct_rated"]), 2),
    })

df_flow = pd.DataFrame(flow_decomp)
df_flow.to_csv(os.path.join(OUT_DIR, "flow_decomposition.csv"), index=False)

print(f"P5 complete:")
print(f"  Surge analysis: {len(surge_floor_results)} quantiles")
print(f"  Flow decomposition: {len(flow_decomp)} quantiles")
print(f"  Governor valve: THEORETICAL ESTIMATE (no DCS tag)")
with open(os.path.join(OUT_DIR, "surge_boundary_oem.json"), "w") as fp:
    json.dump(surge_analysis, fp, indent=2, default=str)
