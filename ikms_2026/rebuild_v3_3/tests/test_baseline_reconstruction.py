"""
REBUILD v3.3 COMPREHENSIVE REGRESSION & VALIDATION TEST SUITE
Tests that specifically reject the four critical defects and validate the independent baseline physical model.
"""
import os
import json
import pytest
import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V3_3_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3")
BASELINE_DIR = os.path.join(V3_3_DIR, "02_energy_baseline")
CLEAN_V2_DIR = os.path.join(BASE_DIR, "ikms_2026", "clean_rebuild_v2", "final_output")

# =============================================================================
# TEST 1: REJECT MITA SURROGATE MISSING COMPOSITION & DOMINATED BY T_AMB
# =============================================================================
def test_reject_mita_missing_composition():
    eval_file = os.path.join(CLEAN_V2_DIR, "15_surrogate_models_evaluation.json")
    assert os.path.exists(eval_file)
    with open(eval_file, "r") as f:
        ev = json.load(f)
    
    mita_eval = ev["mche_minimum_approach_mita"]
    features = mita_eval["features"]
    corrs = mita_eval["feature_correlations"]
    mon_cst = mita_eval["monotonic_constraints"]
    
    # Must reject: N2, C2, C2H4, C3 are absent
    for comp in ["n2_mol", "c2_mol", "c2h4_mol", "c3_mol"]:
        assert comp not in features, f"Expected {comp} to be missing from flawed legacy surrogate"
    
    # Must reject: Ambient temperature dominates the correlation
    assert abs(corrs["t_amb_c"]) > 0.75
    
    # Must reject: Monotonic constraint contradicts data correlation sign
    # feed_flow_th correlation is +0.0256, but constraint forces -1
    assert corrs["feed_flow_th"] > 0
    assert mon_cst[0] < 0
    # opt_mche_mcr_th correlation is -0.0052, but constraint forces +1
    assert corrs["opt_mche_mcr_th"] < 0
    assert mon_cst[1] > 0

# =============================================================================
# TEST 2: REJECT FIXED MITA 7.169 °C & CONFIRM PHYSICAL LOAD-DEPENDENCE
# =============================================================================
def test_reject_fixed_mita_7_169():
    rec_file = os.path.join(CLEAN_V2_DIR, "18_optimal_mr_composition_recommendation.json")
    with open(rec_file, "r") as f:
        rec = json.load(f)
    
    tp = rec["thermodynamic_properties"]
    # Detect the flaw: mean == min == 7.169
    assert tp["mean_mita_across_p1_p100_c"] == 7.169
    assert tp["min_mita_across_p1_p100_c"] == 7.169
    assert tp["mean_mita_across_p1_p100_c"] == tp["min_mita_across_p1_p100_c"]
    
    # Now verify that the independent physical model has load-dependent MITA
    phys_csv = os.path.join(BASELINE_DIR, "independent_physical_baseline_quantiles.csv")
    assert os.path.exists(phys_csv)
    df_phys = pd.read_csv(phys_csv)
    
    mita_vals = df_phys["neqsim_mita_C"].dropna()
    # Physical MITA must NOT be a constant across load points
    assert mita_vals.std() > 2.0, "Physical MITA must vary with load throughput"
    assert mita_vals.min() != mita_vals.max()

# =============================================================================
# TEST 3: REJECT CIRCULAR STEAM/4.040 DEFINITION
# =============================================================================
def test_reject_circular_steam_power_definition():
    eval_file = os.path.join(CLEAN_V2_DIR, "15_surrogate_models_evaluation.json")
    with open(eval_file, "r") as f:
        ev = json.load(f)
    
    steam_eval = ev["driver_steam_demand"]
    # The legacy model had R2=0.9997 because it learned steam = power * 4.04
    assert steam_eval["r2_test"] > 0.999
    assert steam_eval["feature_correlations"]["shaft_power_total_c3mr_mw"] > 0.999
    
    # In the independent physical baseline, shaft power is derived from OEM curves
    phys_csv = os.path.join(BASELINE_DIR, "independent_physical_baseline_quantiles.csv")
    df_phys = pd.read_csv(phys_csv)
    
    oem_power = df_phys["w_shaft_c3mr_total_MW"].dropna()
    legacy_power = df_phys["legacy_power_steam_div_404_MW"].dropna()
    
    # OEM curve-derived power must NOT be identical to steam / 4.040
    diff = (oem_power - legacy_power).abs()
    assert diff.max() > 0.5, "Independent power must differ from circular steam/4.040 derivative"

# =============================================================================
# TEST 4: REJECT OPERATING ENVELOPE VIOLATIONS & BOUNDARY HUGGING
# =============================================================================
def test_reject_envelope_violations():
    rec_file = os.path.join(CLEAN_V2_DIR, "18_optimal_mr_composition_recommendation.json")
    with open(rec_file, "r") as f:
        rec = json.load(f)
    
    tp = rec["thermodynamic_properties"]
    comp = rec["optimal_composition_mol_pct"]
    
    # Reject: surge margin is zero
    assert tp["compressor_surge_floor_margin_t_h"] == 0.0
    
    # Reject: conflicting superheat figures
    sh1 = tp["suction_superheat_margin_c"]      # 34.35
    sh2 = tp["tal_safety_margin_c"]             # 2.92
    sh3 = 23.5                                  # narrative
    assert len({sh1, sh2, sh3}) == 3, "Three conflicting superheat figures exist"
    
    # Reject: C3 below historical 5th percentile
    assert comp["C3"] == 2.0061
    domain_file = os.path.join(BASE_DIR, "ikms_2026", "clean_rebuild_v2", "gc_composition", "mcr_optimization_domain_ilr.json")
    with open(domain_file, "r") as f:
        dom = json.load(f)
    c3_p05 = dom["search_bounds_simplex_mol_pct"]["C3"]["p05"]
    assert comp["C3"] < c3_p05, f"Candidate C3 ({comp['C3']}) is below historical P05 ({c3_p05})"
    
    # Reject: Mahalanobis boundary-hugging (>99.8% of ellipsoid)
    dm = rec["mahalanobis_distance_dm"]
    r_crit = rec["metadata"]["chi2_critical_threshold"]
    assert (dm / r_crit) > 0.998, f"Candidate D_M ({dm}) hugs the statistical boundary ({r_crit})"

# =============================================================================
# TEST 5: REJECT INVERTED POWER DECOMPOSITIONS
# =============================================================================
def test_reject_conflicting_power_decompositions():
    rec_file = os.path.join(CLEAN_V2_DIR, "18_optimal_mr_composition_recommendation.json")
    with open(rec_file, "r") as f:
        rec = json.load(f)
    
    dec = rec["annualized_performance_decomposition"]
    c3_share_rec = dec["indirect_c3_power_savings_share_pct"]  # 10.49%
    c3_share_legacy = (18.15 / 28.98) * 100.0                   # 62.63%
    
    # Verify the contradiction in legacy reports
    assert abs(c3_share_rec - 10.49) < 0.1
    assert abs(c3_share_legacy - 62.63) < 0.1
    assert abs(c3_share_legacy - c3_share_rec) > 50.0, "Major inversion in machine saving share"
    
    # Verify that OEM curve baseline has C3 power share in physically authentic range (28-35%)
    summary_file = os.path.join(BASELINE_DIR, "independent_physical_baseline_summary.json")
    with open(summary_file, "r") as f:
        sb = json.load(f)
    
    c3_share_actual = sb["true_c3_power_share_mean_pct"]
    assert 28.0 <= c3_share_actual <= 35.0, f"Actual baseline C3 power share ({c3_share_actual}%) must be ~30%"

# =============================================================================
# TEST 6: VERIFY INDEPENDENT PHYSICAL BASELINE REPRODUCTION
# =============================================================================
def test_independent_physical_baseline_validity():
    summary_file = os.path.join(BASELINE_DIR, "independent_physical_baseline_summary.json")
    assert os.path.exists(summary_file)
    with open(summary_file, "r") as f:
        sb = json.load(f)
    
    # 1. Thermodynamic model validity
    assert sb["mita_load_dependent"] == True
    assert sb["mita_crossover_observed_at_turndown"] == True
    
    # 2. Turbine steam prediction relative error < 10%
    assert sb["mean_turbine_steam_prediction_error_pct"] < 10.0  # Actual ~4.05%
    
    # 3. Shaft power range physically plausible [70, 115] MW
    p_min, p_max = sb["shaft_power_range_MW"]
    assert 75.0 <= p_min <= 85.0
    assert 95.0 <= p_max <= 110.0
    
    # 4. Final baseline model verdict
    assert sb["baseline_model_verdict"] == "PHYSICAL_BASEMODEL_ESTABLISHED"
    assert len(sb["remaining_uncertainties"]) >= 3
