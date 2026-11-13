"""
Comprehensive Test & Regression Suite for Rebuild v3.2.1 Independent Forensic Qualification
Verifies all 10 Gates (Gate 0 through Gate 9) and thermodynamic/hydraulic invariants.
"""

import os
import pandas as pd
import numpy as np
import pytest

BASE_DIR = os.path.abspath(".")
AUDIT_ROOT = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_2_1_audit")

# Gate 0 Tests: Source Forensics
def test_gate_0_registers_exist():
    p0_dir = os.path.join(AUDIT_ROOT, "01_source_forensics")
    assert os.path.exists(os.path.join(p0_dir, "hardcoded_constants_register.csv"))
    assert os.path.exists(os.path.join(p0_dir, "formula_forensic_register.csv"))
    assert os.path.exists(os.path.join(p0_dir, "target_provenance_register.csv"))
    assert os.path.exists(os.path.join(p0_dir, "candidate_dependency_register.csv"))
    assert os.path.exists(os.path.join(p0_dir, "source_dependency_map.md"))
    assert os.path.exists(os.path.join(p0_dir, "v3_2_1_source_audit.md"))

# Gate 1 Tests: Steam & Condensate Balance
def test_gate_1_steam_rates_and_boundary():
    p1_dir = os.path.join(AUDIT_ROOT, "02_steam_balance")
    df_turb = pd.read_csv(os.path.join(p1_dir, "turbine_steam_balance_v3_2_1.csv"))
    df_rec = pd.read_csv(os.path.join(p1_dir, "steam_rate_reconciliation_v3_2_1.csv"))
    df_sav = pd.read_csv(os.path.join(p1_dir, "steam_saving_reconstruction.csv"))
    df_hrs = pd.read_csv(os.path.join(p1_dir, "annual_operating_hours_v3_2_1.csv"))
    
    # Verify individual machine rates
    sr_4kt1 = float(df_turb.loc[df_turb['turbine_tag'] == '4KT-1', 'design_steam_rate_t_MWh'].values[0])
    sr_4kt2 = float(df_turb.loc[df_turb['turbine_tag'] == '4KT-2', 'design_steam_rate_t_MWh'].values[0])
    sr_4kt3 = float(df_turb.loc[df_turb['turbine_tag'] == '4KT-3', 'design_steam_rate_t_MWh'].values[0])
    
    assert abs(sr_4kt1 - 4.262) < 0.01
    assert abs(sr_4kt2 - 4.183) < 0.01
    assert abs(sr_4kt3 - 4.107) < 0.01
    
    # Verify weighted steam rate
    weighted_sr = float(df_rec.loc[df_rec['metric'] == 'Specific Motive Steam Rate (t/MWh)', 'rebuild_v3_2_1_value'].values[0])
    assert abs(weighted_sr - 4.193) < 0.01
    
    # Verify H4FI031A physical boundary description
    h4fi031a_boundary = df_turb.loc[df_turb['turbine_tag'] == '4KT-1', 'tag_physical_boundary'].values[0]
    assert "Condensate Extraction Pump Discharge" in h4fi031a_boundary
    
    # Verify annual hours
    avail_hrs = float(df_hrs.loc[df_hrs['parameter'] == 'Annual Operating Stream Hours', 'value'].values[0])
    assert abs(avail_hrs - 7849.61) < 0.1

# Gate 2 Tests: MCHE Uncertainty & Robustness
def test_gate_2_mche_uncertainty_and_candidates():
    p2_dir = os.path.join(AUDIT_ROOT, "03_mche_uncertainty")
    df_unc = pd.read_csv(os.path.join(p2_dir, "mche_uncertainty_reconstruction.csv"))
    df_cand = pd.read_csv(os.path.join(p2_dir, "mita_candidate_comparison.csv"))
    df_4e40 = pd.read_csv(os.path.join(p2_dir, "4e40_independent_balance.csv"))
    
    # Verify combined uncertainty
    u_c = float(df_unc.loc[df_unc['component'] == 'Combined Standard Uncertainty', 'value_deg_C'].values[0])
    assert abs(u_c - 0.622) < 0.005
    
    # Verify Candidate A rejection
    p_viol_a = float(df_cand.loc[df_cand['candidate_id'] == 'Candidate A', 'prob_pinch_violation_pct'].values[0])
    assert p_viol_a > 40.0 # 44.1%
    assert "REJECTED" in df_cand.loc[df_cand['candidate_id'] == 'Candidate A', 'engineering_feasibility'].values[0]
    
    # Verify Candidate R robust compliance
    p_viol_r = float(df_cand.loc[df_cand['candidate_id'] == 'Candidate R', 'prob_pinch_violation_pct'].values[0])
    p5_r = float(df_cand.loc[df_cand['candidate_id'] == 'Candidate R', 'p5_one_sided_lower_C'].values[0])
    assert p_viol_r <= 5.0 # 4.57%
    assert p5_r >= 1.500   # 1.527 C >= 1.500 C
    
    # Verify 4E-40 duty
    mean_duty_4e40 = df_4e40["subcooler_4E40_duty_MW"].mean()
    assert 0.40 <= mean_duty_4e40 <= 0.60

# Gate 3 Tests: Rotating Equipment & Anti-Surge
def test_gate_3_rotating_equipment():
    p3_dir = os.path.join(AUDIT_ROOT, "04_rotating_equipment")
    df_anti = pd.read_csv(os.path.join(p3_dir, "p10_flow_boundary_reconciliation.csv"))
    df_gov = pd.read_csv(os.path.join(p3_dir, "p90_governor_verification.csv"))
    
    # P10 flow reconciliation
    p10_row = df_anti[df_anti["percentile"] == 10].iloc[0]
    tot_suct_p10 = float(p10_row["total_compressor_suction_flow_t_h"])
    kick_p10 = float(p10_row["kickback_4UV53_flow_t_h"])
    assert tot_suct_p10 >= 480.0
    assert abs(kick_p10 - 148.3) < 0.5
    
    # P90 governor stroke saturation vs aerodynamic choke
    gov_hkt3 = float(df_gov.loc[df_gov['component'].str.contains('4HKT-3'), 'governor_valve_stroke_p90_pct'].values[0])
    choke_margin = float(df_gov.loc[df_gov['component'].str.contains('4HKT-3'), 'choke_headroom_margin_pct'].values[0])
    assert abs(gov_hkt3 - 94.5) < 0.5
    assert choke_margin > 30.0 # > 33%

# Gate 4 Tests: Control Feasibility (APC vs Passive)
def test_gate_4_control_feasibility():
    p4_dir = os.path.join(AUDIT_ROOT, "05_control_apc")
    df_comp = pd.read_csv(os.path.join(p4_dir, "B_vs_R_control_feasibility.csv"))
    assert os.path.exists(os.path.join(p4_dir, "candidate_B_APC_requirements.md"))
    assert os.path.exists(os.path.join(p4_dir, "candidate_R_passive_assessment.md"))
    assert os.path.exists(os.path.join(p4_dir, "B_vs_R_engineering_tradeoff.md"))
    
    cand_b_status = df_comp.loc[df_comp['evaluation_dimension'] == 'Closed-Loop Dynamic Qualification Status', 'candidate_B_active_apc'].values[0]
    assert "CONCEPTUAL STEADY-STATE ONLY" in cand_b_status

# Gate 5 Tests: Surrogate Qualification
def test_gate_5_surrogate_qualification():
    p5_dir = os.path.join(AUDIT_ROOT, "06_surrogate_qualification")
    df_feat = pd.read_csv(os.path.join(p5_dir, "surrogate_feature_provenance.csv"))
    df_split = pd.read_csv(os.path.join(p5_dir, "surrogate_split_audit.csv"))
    df_mono = pd.read_csv(os.path.join(p5_dir, "surrogate_monotonicity_audit.csv"))
    
    # Check monotonic constraints verified
    assert np.all(df_mono["verified_strictly_monotonic"] == True)
    
    # Check holdout validation metrics from the training pipeline
    # Source: surrogate_holdout_validation_metrics.csv from rebuild_v3_2
    holdout_path = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_2",
                                "05_surrogate_rebuild", "validation",
                                "surrogate_holdout_validation_metrics.csv")
    df_holdout = pd.read_csv(holdout_path)
    
    # All surrogates must have R2_test >= 0.60 (AGENTS.md Pasal 2) — actual all > 0.98
    assert np.all(df_holdout["r2_test"] >= 0.60)
    
    # Total shaft power surrogate relative MAE < 1.0% (AGENTS.md Pasal 2)
    total_power_row = df_holdout[df_holdout["target_name"] == "power_total_shaft_MW"]
    assert float(total_power_row["relative_mae_pct"].values[0]) < 1.0

# Gate 6 Tests: Joint Optimization & Synergy
def test_gate_6_joint_optimization_and_synergy():
    p6_dir = os.path.join(AUDIT_ROOT, "07_joint_optimization")
    df_cand = pd.read_csv(os.path.join(p6_dir, "candidate_comparison_final.csv"))
    df_pol = pd.read_csv(os.path.join(p6_dir, "policy_comparison_final.csv"))
    df_sens = pd.read_csv(os.path.join(p6_dir, "component_sensitivity_final.csv"))
    
    # Synergy term
    delta_int = float(df_pol.loc[df_pol['policy_id'] == 'Policy 4 (F1C1)', 'interaction_contribution_GWh'].values[0])
    assert abs(delta_int - 1.77) < 0.05
    
    # Sensitivity records count (5 components x 4 perturbations = 20)
    assert len(df_sens) == 20

# Gate 7 Tests: Accounting & Energy Closure
def test_gate_7_accounting_exact_closure():
    p7_dir = os.path.join(AUDIT_ROOT, "08_accounting")
    df_decomp = pd.read_csv(os.path.join(p7_dir, "energy_saving_final.csv"))
    df_fg = pd.read_csv(os.path.join(p7_dir, "fuel_gas_reconciliation_final.csv"))
    df_co2 = pd.read_csv(os.path.join(p7_dir, "co2_reconciliation_final.csv"))
    df_econ = pd.read_csv(os.path.join(p7_dir, "economic_scenarios_final.csv"))
    
    # Exact unclipped closure
    max_closure_err = df_decomp["closure_error_GWh"].abs().max()
    assert max_closure_err < 1e-5
    
    # Dual SFC
    sfc_asme = float(df_fg["sfc_asme_Nm3_t"].iloc[0])
    sfc_field = float(df_fg["sfc_field_Nm3_t"].iloc[0])
    assert abs(sfc_asme - 97.70) < 0.01
    assert abs(sfc_field - 79.76) < 0.01

# Gate 8 Tests: Robustness & Decisions
def test_gate_8_robustness_and_decisions():
    p8_dir = os.path.join(AUDIT_ROOT, "09_robustness")
    df_joint = pd.read_csv(os.path.join(p8_dir, "joint_constraint_feasibility.csv"))
    df_accept = pd.read_csv(os.path.join(p8_dir, "candidate_acceptance_matrix.csv"))
    
    # Candidate R accepted as primary recommendation
    status_r = df_accept.loc[df_accept['candidate_id'] == 'Candidate R', 'qualification_status'].values[0]
    assert "ROBUSTLY QUALIFIED & RECOMMENDED" in status_r
    
    # Candidate A rejected
    status_a = df_accept.loc[df_accept['candidate_id'] == 'Candidate A', 'qualification_status'].values[0]
    assert "REJECTED" in status_a

# Gate 9 Tests: Field Testability & Claim Evidence
def test_gate_9_field_testability_and_ledger():
    p9_dir = os.path.join(AUDIT_ROOT, "10_field_testability")
    p9_ledger = os.path.join(AUDIT_ROOT, "11_manuscript_ledger")
    p9_rep = os.path.join(AUDIT_ROOT, "reports")
    
    assert os.path.exists(os.path.join(p9_dir, "draft_plant_trial_proposal.md"))
    assert os.path.exists(os.path.join(p9_ledger, "claim_evidence_ledger_final.csv"))
    assert os.path.exists(os.path.join(p9_ledger, "claim_evidence_ledger_final.md"))
    assert os.path.exists(os.path.join(p9_ledger, "manuscript_claim_audit.md"))
    assert os.path.exists(os.path.join(p9_rep, "REBUILD_V3_2_1_EXECUTIVE_SUMMARY.md"))
    assert os.path.exists(os.path.join(p9_rep, "REBUILD_V3_2_1_FINAL_FORENSIC_AUDIT.md"))
    assert os.path.exists(os.path.join(p9_rep, "REBUILD_V3_2_1_GATE_DECISIONS.md"))
    assert os.path.exists(os.path.join(p9_rep, "REBUILD_V3_2_1_CHANGE_LOG.md"))
    
    df_ledger = pd.read_csv(os.path.join(p9_ledger, "claim_evidence_ledger_final.csv"))
    assert len(df_ledger) >= 15
    assert set(df_ledger["evidence_classification"].unique()).issubset({
        "VALIDATED", "CONDITIONAL", "ESTIMATED", "UNSUPPORTED", "SUPERSEDED", "UNRESOLVED"
    })

# Independent Forensic Verification Checks (Phase V1)
def test_independent_forensic_verification():
    v1_dir = os.path.join(AUDIT_ROOT, "12_independent_verification")
    assert os.path.exists(os.path.join(v1_dir, "independent_checks.csv"))
    assert os.path.exists(os.path.join(v1_dir, "independent_checks_summary.json"))
    
    df_checks = pd.read_csv(os.path.join(v1_dir, "independent_checks.csv")).set_index("check_id")
    assert len(df_checks) >= 25
    
    # Check that circular baseline power definition was detected
    assert df_checks.loc["V1.1", "verdict"] == "CIRCULAR"
    assert df_checks.loc["V1.1", "evidence_class"] == "UNSUPPORTED"
    
    # Check that synthetic surrogate generator was detected
    assert df_checks.loc["V3.1", "verdict"] == "SYNTHETIC ALGEBRAIC"
    assert df_checks.loc["V3.1", "evidence_class"] == "UNSUPPORTED"
    
    # Check that hardcoded synergy term was detected
    assert df_checks.loc["V4.1", "verdict"] == "HARDCODED"
    assert df_checks.loc["V4.1", "evidence_class"] == "UNSUPPORTED"
    
    # Check that H4FI031A tag boundary was validated
    assert df_checks.loc["V1.3", "verdict"] == "CLAIM REFUTED" # p1 claim of 42.85 t/h utility balance refuted

# Ten Critical Forensic Blockers Resolution (Phase V2)
def test_ten_forensic_blockers_resolved():
    import json
    v2_dir = os.path.join(AUDIT_ROOT, "13_blocker_resolution")
    json_path = os.path.join(v2_dir, "forensic_blocker_resolution.json")
    md_path = os.path.join(v2_dir, "TEN_FORENSIC_BLOCKERS_RESOLVED.md")
    
    assert os.path.exists(json_path)
    assert os.path.exists(md_path)
    
    with open(json_path, "r", encoding="utf-8") as fp:
        b = json.load(fp)
    
    # 1. Candidate R Savings Discrepancy
    q1 = b["Q1_Candidate_R_Discrepancy"]
    assert q1["scaling_factor_v3_2"] == 0.558
    assert q1["scaling_factor_v3_2_1"] == 0.694
    assert abs(q1["calculated_savings_v3_2_GWh"] - 11.20) < 0.05
    assert abs(q1["calculated_savings_v3_2_1_GWh"] - 13.92) < 0.05
    
    # 2. Candidate B Three Inconsistent Compositions
    q2 = b["Q2_Candidate_B_Compositions"]
    assert q2["rebuild_v3_1"]["DM"] == 1.821
    assert q2["rebuild_v3_2"]["DM"] == 1.82
    assert q2["rebuild_v3_2_1"]["DM"] == 2.41
    
    # 3. Candidate Scaling Origin
    q3 = b["Q3_Candidate_Scaling_Origin"]
    assert q3["scaling_table"]["Candidate B"]["sf"] == 0.840
    assert q3["scaling_table"]["Candidate R"]["sf"] == 0.694
    
    # 4. Baseline Power Circularity (Steam / 4.040)
    q4 = b["Q4_Baseline_Power_Circularity"]
    assert q4["std_ratio"] < 0.001
    assert abs(q4["min_ratio"] - 4.040) < 0.01
    
    # 5. Annual Steam Discrepancy
    q5 = b["Q5_Annual_Steam_Discrepancy"]
    assert abs(q5["reconstructed_annual_steam_kt"] - 3172.83) < 0.1
    assert abs(q5["legacy_v3_annual_steam_kt"] - 2935.90) < 0.1
    
    # 6. Steam Rate Contradiction
    q6 = b["Q6_Steam_Rate_Contradiction"]
    assert abs(q6["direct_division_2935_over_726"] - 4.040) < 0.01
    assert abs(q6["power_weighted_average_rate"] - 4.194) < 0.01
    
    # 7. Candidate R Statistical Power
    q7 = b["Q7_Candidate_R_Statistical_Power"]
    assert abs(q7["analytical_normal_cdf_risk_pct"] - 4.57) < 0.05
    assert q7["clopper_pearson_95_ci_pct"][1] > 5.0 # Upper bound crosses 5%
    assert q7["sample_size_required_for_sub_5_pct_proof"] > 7000
    
    # 8. DoE Target Provenance
    q8 = b["Q8_DoE_Target_Provenance"]
    assert q8["pattern_audit"]["k_exp formula"] == True
    assert q8["pattern_audit"]["mita synthetic formula"] == True
    assert q8["pattern_audit"]["hysys COM call"] == False
    
    # 9. 4E-40 Routing, Makeup, Zero-CAPEX
    q9 = b["Q9_Subcooler_Makeup_ZeroCAPEX"]
    assert "ZERO-CAPEX VALID FOR CANDIDATE R ONLY" in q9["verdict"]
    
    # 10. Compressor Flow Floor & Governor Limits
    q10 = b["Q10_Compressor_and_Governor_Limits"]
    assert q10["compressor_anti_surge_floor"]["status"] == "VALIDATED VIA OEM MAP"
    assert q10["turbine_governor_stroke"]["status"] == "HARDCODED ESTIMATE (NO TELEMETRY TAG)"



