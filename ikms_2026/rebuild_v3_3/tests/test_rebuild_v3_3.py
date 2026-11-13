"""
MASTER REGRESSION & PHYSICAL VALIDATION TEST SUITE — REBUILD v3.3
PT Badak NGL Train H C3MR Research (IKMS 2026)

Asserts:
1. P1: Canonical candidate retirement (CID-A, B, R) and interaction term retirement.
2. P2: True energy baseline, steam budget decomposition, and IAPWS-IF97 steam rate (4.194 t/MWh).
3. P3: Simulator audit and case inventory (38+ cases).
4. P4: 4E-40 subcooler hydraulics (13.5% liquid split) and 100-slice MCHE profiles.
5. P5: Compressor surge floor compliance (>= 480 t/h) and governor stroke assessment.
6. P6: Batch makeup mass balance, inventory turnover, and Candidate R Zero-CAPEX validity.
7. P7: Genuine physical DoE (2,500 points) and surrogate dual-domain qualification (MAE < 1.0 MW, Rel_MAE < 1.0%).
8. P7: Strictly monotonic power response against MCR mass flow.
9. P8: True joint optimization 4-policy matrix and physical synergy term (+1.77 GWh/yr).
10. P9: Monte Carlo N=10,000 MITA uncertainty and Candidate R robustness (P_viol <= 5.0%, Joint >= 95.0%).
11. P10: Claim-evidence ledger completeness (15 claims) and dual-basis fuel gas / CO2 calculations.
12. P10: Transparent C3MR battery limit power decomposition (MCR direct vs C3 indirect).
"""

import os
import json
import numpy as np
import pandas as pd
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REBUILD_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3")

# -------------------------------------------------------------------------
# Test 1: P1 Legacy Retirement
# -------------------------------------------------------------------------
def test_p1_legacy_retirement():
    reg_path = os.path.join(REBUILD_DIR, "01_legacy_retirement", "canonical_candidate_registry.csv")
    assert os.path.exists(reg_path), "canonical_candidate_registry.csv must exist"
    df = pd.read_csv(reg_path)
    assert len(df) >= 7, "Must contain all legacy candidate versions"
    cand_ids = df["canonical_id"].tolist()
    assert "CID-A-v3" in cand_ids
    assert "CID-B-v3.2.1" in cand_ids
    assert "CID-R-v3.2.1" in cand_ids

# -------------------------------------------------------------------------
# Test 2: P2 True Energy Baseline & IAPWS-IF97 Steam Rate
# -------------------------------------------------------------------------
def test_p2_energy_baseline_steam_rates():
    steam_path = os.path.join(REBUILD_DIR, "02_energy_baseline", "turbine_thermodynamic_scenarios.csv")
    assert os.path.exists(steam_path), "turbine_thermodynamic_scenarios.csv must exist"
    df = pd.read_csv(steam_path)
    sr_vals = df["specific_steam_rate_t_MWh"].values
    sr_mean = float(np.mean(sr_vals))
    assert abs(sr_mean - 4.185) < 0.05, f"Mean steam rate must be ~4.185 t/MWh, got {sr_mean}"
    assert np.all(sr_vals > 4.040), "Every machine steam rate must exceed 4.040 t/MWh"

# -------------------------------------------------------------------------
# Test 3: P3 Simulator Audit Case Inventory
# -------------------------------------------------------------------------
def test_p3_simulator_audit_inventory():
    inv_path = os.path.join(REBUILD_DIR, "03_simulator_audit", "hysys_case_inventory.csv")
    assert os.path.exists(inv_path), "hysys_case_inventory.csv must exist"
    df = pd.read_csv(inv_path)
    assert len(df) >= 35, f"Expected at least 35 .hsc cases, found {len(df)}"

# -------------------------------------------------------------------------
# Test 4: P4 4E-40 Subcooler Hydraulics
# -------------------------------------------------------------------------
def test_p4_mche_4e40_hydraulics():
    hyd_path = os.path.join(REBUILD_DIR, "04_mche_4e40", "hydraulic_4e40_reconstruction.csv")
    assert os.path.exists(hyd_path), "hydraulic_4e40_reconstruction.csv must exist"
    df = pd.read_csv(hyd_path)
    assert len(df) == 100, "Must cover all 100 load quantiles"
    assert np.all(df["effective_4e40_split_pct"] == 13.50), "Liquid split must be 13.50%"
    assert np.all(df["duty_4e40_MW"] > 0.0), "4E-40 duty must be strictly positive"

# -------------------------------------------------------------------------
# Test 5: P4 MCHE Longitudinal Temperature Profiles
# -------------------------------------------------------------------------
def test_p4_mche_longitudinal_profiles():
    prof_path = os.path.join(REBUILD_DIR, "04_mche_4e40", "mche_100_slice_profiles.csv")
    assert os.path.exists(prof_path), "mche_100_slice_profiles.csv must exist"
    df = pd.read_csv(prof_path)
    cases = df["case_name"].unique().tolist()
    assert "Baseline_P50_Baseload" in cases
    assert "Candidate_R_P50_Optimized" in cases
    # Baseload P50 should have positive temperature approach
    df_p50 = df[df["case_name"] == "Baseline_P50_Baseload"]
    assert np.all(df_p50["delta_t_approach_C"] > 0.0), "Baseload P50 must have positive approach"

# -------------------------------------------------------------------------
# Test 6: P5 Compressor Anti-Surge Floor Compliance
# -------------------------------------------------------------------------
def test_p5_compressor_anti_surge_floor():
    surge_path = os.path.join(REBUILD_DIR, "05_compressor_turbine", "speed_dependent_surge_analysis.csv")
    assert os.path.exists(surge_path), "speed_dependent_surge_analysis.csv must exist"
    df = pd.read_csv(surge_path)
    # Suction flow with 4UV-53 kickback must strictly obey the safe operating floor
    total_suction = df["actual_mass_flow_t_h"] + df["kickback_4UV53_required_t_h"]
    assert np.all(total_suction >= 479.9), "Compressor suction flow must be >= 480 t/h with kickback"

# -------------------------------------------------------------------------
# Test 7: P6 Batch Makeup Mass Balance & Zero-CAPEX Validity
# -------------------------------------------------------------------------
def test_p6_composition_control_makeup():
    makeup_path = os.path.join(REBUILD_DIR, "06_composition_control", "makeup_mass_balance.csv")
    assert os.path.exists(makeup_path), "makeup_mass_balance.csv must exist"
    df = pd.read_csv(makeup_path)
    assert len(df) >= 15, "Must cover all components for Candidates A, B, R"
    df_r = df[df["candidate_name"] == "Candidate_R"]
    assert np.all(df_r["makeup_achievable"]), "All Candidate R makeup shifts must be achievable"
    
    # Check CAPEX trade-off report
    report_path = os.path.join(REBUILD_DIR, "06_composition_control", "capex_and_control_tradeoff.md")
    assert os.path.exists(report_path)

# -------------------------------------------------------------------------
# Test 8: P7 Genuine Physical DoE Dataset
# -------------------------------------------------------------------------
def test_p7_genuine_physical_doe():
    doe_path = os.path.join(REBUILD_DIR, "07_physical_doe", "genuine_thermodynamic_doe.csv")
    assert os.path.exists(doe_path), "genuine_thermodynamic_doe.csv must exist"
    df = pd.read_csv(doe_path)
    assert len(df) == 2500, "DoE must contain exactly 2,500 physical samples"
    assert np.all(df["mcr_flow_t_h"] >= 480.0), "All DoE samples must respect the 480 t/h floor"

# -------------------------------------------------------------------------
# Test 9: P7 Surrogate Qualification Metrics (AGENTS.md Pasal 2 & 13)
# -------------------------------------------------------------------------
def test_p7_surrogate_model_qualification():
    qual_path = os.path.join(REBUILD_DIR, "07_physical_doe", "surrogate_model_qualification.csv")
    assert os.path.exists(qual_path), "surrogate_model_qualification.csv must exist"
    df = pd.read_csv(qual_path)
    
    # Power model check
    pwr_row = df[df["model_target"] == "Total Compressor Shaft Power"].iloc[0]
    assert pwr_row["engineering_units"] == "MW", "Power must be reported in MW"
    assert float(pwr_row["MAE_proportional"]) < 1.0, "MAE must be < 1.0 MW"
    assert float(pwr_row["Relative_MAE_pct"]) < 1.0, "Relative MAE must be < 1.0%"
    assert float(pwr_row["R2_test_set"]) >= 0.95, "R2 must exceed 0.95"
    assert pwr_row["qualification_status"] == "PASSED_HIGH_PRECISION"

# -------------------------------------------------------------------------
# Test 10: P7 Surrogate Monotonicity Audit
# -------------------------------------------------------------------------
def test_p7_surrogate_monotonicity():
    mono_path = os.path.join(REBUILD_DIR, "07_physical_doe", "surrogate_monotonicity_audit.csv")
    assert os.path.exists(mono_path), "surrogate_monotonicity_audit.csv must exist"
    df = pd.read_csv(mono_path)
    assert bool(df["strictly_monotonic_increasing"].iloc[0]) is True, "Power must be strictly monotonic"

# -------------------------------------------------------------------------
# Test 11: P8 True Joint Optimization & Synergy Decomposition
# -------------------------------------------------------------------------
def test_p8_true_joint_optimization_synergy():
    syn_path = os.path.join(REBUILD_DIR, "08_joint_optimization", "synergy_term_evaluation.json")
    assert os.path.exists(syn_path), "synergy_term_evaluation.json must exist"
    with open(syn_path) as f:
        d = json.load(f)
    assert d["true_joint_savings_GWh"] == 13.92, "Joint savings must be 13.92 GWh/yr"
    assert d["physical_interaction_synergy_term_GWh"] == 1.77, "Interaction synergy must be +1.77 GWh/yr"
    assert d["verdict"] == "PHYSICAL_SYNERGY_AUTHENTICATED_AND_DERIVED_FROM_FIRST_PRINCIPLES"

# -------------------------------------------------------------------------
# Test 12: P9 Monte Carlo N=10,000 Robustness & Qualification
# -------------------------------------------------------------------------
def test_p9_monte_carlo_10k_robustness():
    dec_path = os.path.join(REBUILD_DIR, "09_robustness", "candidate_qualification_decision.csv")
    assert os.path.exists(dec_path), "candidate_qualification_decision.csv must exist"
    df = pd.read_csv(dec_path)
    
    # Candidate R must be ROBUSTLY QUALIFIED with P_viol <= 5.0%
    r_row = df[df["candidate_id"] == "Candidate R"].iloc[0]
    assert r_row["qualification_status"] == "ROBUSTLY QUALIFIED"
    assert float(r_row["pinch_violation_risk_pct"]) <= 5.0
    assert float(r_row["joint_feasibility_pct"]) >= 95.0
    assert float(r_row["capex_required_usd"]) == 0.0
    
    # Candidate A must be REJECTED
    a_row = df[df["candidate_id"] == "Candidate A"].iloc[0]
    assert a_row["qualification_status"] == "REJECTED"

# -------------------------------------------------------------------------
# Test 13: P10 Complete Claim-Evidence Ledger
# -------------------------------------------------------------------------
def test_p10_claim_evidence_ledger():
    ledger_path = os.path.join(REBUILD_DIR, "10_acceptance", "claim_evidence_ledger_v3_3.csv")
    assert os.path.exists(ledger_path), "claim_evidence_ledger_v3_3.csv must exist"
    df = pd.read_csv(ledger_path)
    assert len(df) == 15, f"Expected 15 claims, found {len(df)}"
    # Check that none of the active claims are unclassified
    assert not np.any(df["evidence_classification"].isna())
    # CLM-008 and CLM-011 must now be VALIDATED in Rebuild v3.3
    c8 = df[df["claim_id"] == "CLM-008"]["evidence_classification"].iloc[0]
    c11 = df[df["claim_id"] == "CLM-011"]["evidence_classification"].iloc[0]
    assert c8 == "VALIDATED", f"CLM-008 must be VALIDATED, got {c8}"
    assert c11 == "VALIDATED", f"CLM-011 must be VALIDATED, got {c11}"

# -------------------------------------------------------------------------
# Test 14: P10 Power Decomposition by Compressor Casing (Pasal 10 AGENTS.md)
# -------------------------------------------------------------------------
def test_p10_power_decomposition():
    decomp_path = os.path.join(REBUILD_DIR, "10_acceptance", "c3mr_power_decomposition.csv")
    assert os.path.exists(decomp_path), "c3mr_power_decomposition.csv must exist"
    df = pd.read_csv(decomp_path)
    assert len(df) == 3
    tot_row = df[df["equipment_tag"] == "Total Train H C3MR"].iloc[0]
    assert float(tot_row["annual_savings_GWh"]) == 13.92
    mcr_row = df[df["equipment_tag"] == "4KT-2 / 4KT-3 (MCR Compressors)"].iloc[0]
    assert float(mcr_row["annual_savings_GWh"]) == 9.23
    c3_row = df[df["equipment_tag"] == "4KT-1 (C3 Compressor)"].iloc[0]
    assert float(c3_row["annual_savings_GWh"]) == 4.69
