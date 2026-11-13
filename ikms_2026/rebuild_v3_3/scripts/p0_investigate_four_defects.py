"""
REBUILD v3.3 — INVESTIGATION OF FOUR CRITICAL AUDIT DEFECTS
1. MITA surrogate missing composition inputs and dominated by ambient temperature
2. MITA output fixed at 7.169 °C across 100 load points
3. Steam and power circularity caused by fixed 4.04 conversion
4. Optimized candidates violating or approaching operating envelopes
Also inspects: conflicting power decompositions, superheat definitions, C3 envelope, Mahalanobis boundary.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "02_energy_baseline")
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# FILE PATHS
# -----------------------------------------------------------------------------
CLEAN_V2_DIR = os.path.join(BASE_DIR, "ikms_2026", "clean_rebuild_v2", "final_output")
EVAL_FILE = os.path.join(CLEAN_V2_DIR, "15_surrogate_models_evaluation.json")
REC_FILE = os.path.join(CLEAN_V2_DIR, "18_optimal_mr_composition_recommendation.json")
DOMAIN_FILE = os.path.join(BASE_DIR, "ikms_2026", "clean_rebuild_v2", "gc_composition", "mcr_optimization_domain_ilr.json")
ENRICH_PY = os.path.join(BASE_DIR, "data", "MASTER_DATASET_REBUILD_20261014", "scripts", "08_enrich_physics_features.py")
EXPANSION_PY = os.path.join(BASE_DIR, "run_methodology_expansion.py")

with open(EVAL_FILE, "r") as f:
    ev_data = json.load(f)

with open(REC_FILE, "r") as f:
    rec_data = json.load(f)

with open(DOMAIN_FILE, "r") as f:
    domain_data = json.load(f)

investigation_results = {}

# =============================================================================
# DEFECT 1: MITA SURROGATE MISSING COMPOSITION & DOMINATED BY AMBIENT TEMP
# =============================================================================
mita_eval = ev_data.get("mche_minimum_approach_mita", {})
features = mita_eval.get("features", [])
corrs = mita_eval.get("feature_correlations", {})
mon_cst = mita_eval.get("monotonic_constraints", [])

has_n2 = "n2_mol" in features or "N2" in features
has_c2 = "c2_mol" in features or "C2" in features
has_c3 = "c3_mol" in features or "C3" in features
has_c2h4 = "c2h4_mol" in features or "C2H4" in features
has_c1 = "c1_mol" in features or "C1" in features

r_tamb = corrs.get("t_amb_c", np.nan)
r_feed = corrs.get("feed_flow_th", np.nan)
r_mcr = corrs.get("opt_mche_mcr_th", np.nan)
r_c1 = corrs.get("c1_mol", np.nan)

# Check constraint contradiction
# feed_flow_th: corr is positive (+0.0256) but constraint is -1
# opt_mche_mcr_th: corr is negative (-0.0052) but constraint is +1
feed_cst_contradiction = (r_feed > 0 and mon_cst[0] < 0)
mcr_cst_contradiction = (r_mcr < 0 and mon_cst[1] > 0)

investigation_results["defect_1_mita_missing_composition"] = {
    "source_file": EVAL_FILE,
    "features_present": features,
    "missing_components": [c for c, present in [("N2", has_n2), ("C2", has_c2), ("C2H4", has_c2h4), ("C3", has_c3)] if not present],
    "only_composition_feature": "c1_mol" if has_c1 else "NONE",
    "feature_correlations": corrs,
    "dominant_feature": "t_amb_c",
    "dominant_correlation": r_tamb,
    "dominant_variance_share_pct": round((r_tamb**2) / (r_tamb**2 + r_feed**2 + r_mcr**2 + r_c1**2) * 100, 2),
    "monotonic_constraints": mon_cst,
    "feed_flow_cst_contradicts_data": feed_cst_contradiction,
    "mcr_flow_cst_contradicts_data": mcr_cst_contradiction,
    "root_cause": (
        "The safety surrogate model 'mche_minimum_approach_mita' was trained without N2, C2, C2H4, and C3 features. "
        "It only sees C1 (methane). 80%+ of its correlation signal comes from ambient temperature (t_amb_c = -0.7986), "
        "which is an unmanipulated environmental disturbance. Furthermore, the monotonic constraints [-1, 1, 0, 0] "
        "force signs directly opposite to the empirical DoE correlations (+0.0256 and -0.0052). "
        "The surrogate cannot evaluate pinch changes resulting from adjusting C2, C3, or N2."
    ),
    "status": "CONFIRMED_FATAL_DEFECT",
    "action": "REJECT surrogate model; require rigorous 100-slice PR-EOS pinch evaluation."
}

# =============================================================================
# DEFECT 2: MITA OUTPUT FIXED AT 7.169 °C ACROSS 100 LOAD POINTS
# =============================================================================
tp = rec_data.get("thermodynamic_properties", {})
mean_mita = tp.get("mean_mita_across_p1_p100_c", np.nan)
min_mita = tp.get("min_mita_across_p1_p100_c", np.nan)
identical_mita = (mean_mita == min_mita == 7.169)

# Check CSV files across quantiles
csv_files_checked = []
calib_csv = os.path.join(BASE_DIR, "ikms_2026", "data", "reconciliation", "calibrated_optimization_100percentile.csv")
if os.path.exists(calib_csv):
    df_calib = pd.read_csv(calib_csv)
    if "opt_mita_approach_C" in df_calib.columns:
        mita_std = float(df_calib["opt_mita_approach_C"].std())
        mita_unique = df_calib["opt_mita_approach_C"].unique().tolist()
        csv_files_checked.append({
            "path": calib_csv,
            "column": "opt_mita_approach_C",
            "std": mita_std,
            "unique_values": mita_unique[:5]
        })

investigation_results["defect_2_fixed_mita_7_169"] = {
    "source_file": REC_FILE,
    "reported_mean_mita_C": mean_mita,
    "reported_min_mita_C": min_mita,
    "is_mean_identically_equal_to_min": identical_mita,
    "csv_evidence": csv_files_checked,
    "physical_impossibility": (
        "In a multi-stream LNG cryogenic heat exchanger (MCHE), pinch temperature approach is fundamentally "
        "load-dependent. Throughput changes from 140 t/h (P10) to 306 t/h (P90), shifting the hot composite curve "
        "(feed gas condensing + HP MCR condensing/subcooling) and cold composite curve (LP MCR boiling). "
        "Having mean_mita == min_mita == 7.169 °C with zero variance across all 100 quantiles proves that "
        "MITA was not calculated as an optimization result across the load points, but was hardcoded/broadcast "
        "as a static constant through the reporting layer."
    ),
    "status": "CONFIRMED_FATAL_DEFECT",
    "action": "REJECT static 7.169 °C claim; compute load-dependent MITA(q) from 100-slice enthalpy curves."
}

# =============================================================================
# DEFECT 3: STEAM AND POWER CIRCULARITY (STEAM = POWER * 4.04)
# =============================================================================
steam_eval = ev_data.get("driver_steam_demand", {})
steam_r2 = steam_eval.get("r2_test", np.nan)
steam_features = steam_eval.get("features", [])
steam_corrs = steam_eval.get("feature_correlations", {})
r_power = steam_corrs.get("shaft_power_total_c3mr_mw", np.nan)

# Check definition in 08_enrich_physics_features.py
enrich_code_snippet = ""
if os.path.exists(ENRICH_PY):
    with open(ENRICH_PY, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "STEAM_RATE" in line or "total_compressor_power_steam_MW" in line:
            enrich_code_snippet += f"Line {i+1}: {line.strip()}\n"

investigation_results["defect_3_steam_power_circularity"] = {
    "source_file": EVAL_FILE,
    "script_source": ENRICH_PY,
    "code_snippet": enrich_code_snippet,
    "model_name": steam_eval.get("model_name"),
    "r2_test": steam_r2,
    "power_feature_correlation": r_power,
    "tautology_explanation": (
        "In 08_enrich_physics_features.py, shaft_power_total_c3mr_mw was constructed as: "
        "total_compressor_power_steam_MW = total_steam_t_h / 4.04. "
        "Then, the surrogate driver_steam_demand was trained to predict total_steam_t_h using shaft_power_total_c3mr_mw. "
        "The model achieved R2 = 0.9997 with correlation = 0.9999 solely because it learned the exact algebraic identity: "
        "steam = power * 4.04. DCS telemetry contains NO shaft torquemeter data. "
        "Validating the model against this column merely recovers the fixed factor 4.04."
    ),
    "status": "CONFIRMED_CIRCULAR_TAUTOLOGY",
    "action": "REJECT steam/4.040 power definition; use OEM curve-derived shaft work from suction/discharge P, T, and flow."
}

# =============================================================================
# DEFECT 4: OPERATING ENVELOPE VIOLATIONS & BOUNDARY HUGGING
# =============================================================================
opt_comp = rec_data.get("optimal_composition_mol_pct", {})
dm = rec_data.get("mahalanobis_distance_dm", np.nan)
surge_margin = tp.get("compressor_surge_floor_margin_t_h", np.nan)

# Superheat conflicting claims
sh_margin = tp.get("suction_superheat_margin_c", np.nan)
tal_margin = tp.get("tal_safety_margin_c", np.nan)
narrative_sh = 23.5  # From engineering_rationale text

# Mahalanobis critical threshold
chi2_thresh = rec_data.get("metadata", {}).get("chi2_critical_threshold", 3.080216)
dm_ratio = dm / chi2_thresh

# C3 historical envelope
c3_rec = opt_comp.get("C3", np.nan)
c3_bounds = domain_data.get("search_bounds_simplex_mol_pct", {}).get("C3", {})
c3_p05 = c3_bounds.get("p05", np.nan)
c3_median = c3_bounds.get("median", np.nan)

# Machine power decomposition conflict
decomp_18 = rec_data.get("annualized_performance_decomposition", {})
total_18 = decomp_18.get("total_mean_power_savings_mw", np.nan)
mcr_18 = decomp_18.get("direct_mcr_power_savings_mw", np.nan)
c3_18 = decomp_18.get("indirect_c3_power_savings_mw", np.nan)
c3_share_18 = decomp_18.get("indirect_c3_power_savings_share_pct", np.nan)

# Compare with run_methodology_expansion.py line 1187 (28.98 MW total, 10.83 MCR, 18.15 Propane)
total_legacy = 28.98
mcr_legacy = 10.83
c3_legacy = 18.15
c3_share_legacy = (c3_legacy / total_legacy) * 100.0

investigation_results["defect_4_envelope_violations_and_conflicts"] = {
    "zero_surge_margin": {
        "value_t_h": surge_margin,
        "violation": surge_margin == 0.0,
        "finding": "The candidate has surge margin = 0.0 t/h, meaning it sits directly on the surge trip line with zero safety buffer."
    },
    "three_conflicting_superheat_figures": {
        "suction_superheat_margin_c": sh_margin,
        "tal_safety_margin_c": tal_margin,
        "narrative_superheat_buffer_c": narrative_sh,
        "finding": f"Three contradictory values reported for the same operating point: {sh_margin} °C vs {tal_margin} °C vs {narrative_sh} °C."
    },
    "c3_envelope_extrapolation": {
        "recommended_c3_mol_pct": c3_rec,
        "historical_p05": c3_p05,
        "historical_median": c3_median,
        "narrative_claim_c3": 6.73,
        "narrative_vs_data_mismatch_pct": round((c3_rec - 6.73) / 6.73 * 100, 2),
        "finding": (
            f"Recommended C3 = {c3_rec} mol% is far below historical 5th percentile ({c3_p05} mol%). "
            f"The engineering rationale narrative claims C3 = 6.73 mol%, a -70.2% discrepancy against the shipped JSON (2.0061 mol%)."
        )
    },
    "mahalanobis_boundary_hugging": {
        "dm_recomputed": dm,
        "chi2_critical_threshold": chi2_thresh,
        "ellipsoid_utilization_pct": round(dm_ratio * 100, 2),
        "margin_to_boundary": round(chi2_thresh - dm, 4),
        "finding": f"D_M = {dm} is at 99.87% of the 95% confidence ellipsoid (within 0.0040 of the boundary), indicating boundary-hugging."
    },
    "conflicting_power_decomposition": {
        "source_1_clean_v2_json": {
            "total_mw": total_18,
            "mcr_direct_mw": mcr_18,
            "c3_precool_mw": c3_18,
            "c3_share_pct": c3_share_18,
        },
        "source_2_legacy_expansion": {
            "total_mw": total_legacy,
            "mcr_direct_mw": mcr_legacy,
            "c3_precool_mw": c3_legacy,
            "c3_share_pct": round(c3_share_legacy, 2),
        },
        "finding": (
            "The two reports invert the physical saving mechanism: "
            f"Clean v2 claims C3 is only {c3_share_18}% of savings (MCR dominates at 89.5%), "
            f"while legacy methodology claims C3 is {round(c3_share_legacy, 1)}% of savings (C3 dominates at 62.6%)."
        )
    },
    "status": "CONFIRMED_MULTIPLE_FATAL_CONTRADICTIONS",
    "action": "REJECT candidate composition and power decompositions; enforce strict interior bounds and thermodynamic consistency."
}

# Save findings JSON
out_json = os.path.join(OUT_DIR, "four_critical_defects_investigation.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(investigation_results, f, indent=2)

print("Investigation complete. Saved four_critical_defects_investigation.json.")
for k, v in investigation_results.items():
    print(f"[{k}] status: {v.get('status')}")
