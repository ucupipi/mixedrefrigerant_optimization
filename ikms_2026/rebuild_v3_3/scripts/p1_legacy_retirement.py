"""
PRIORITY 1 — RETIRE INVALID LEGACY OPTIMIZATION CLAIMS
Create canonical candidate registry with immutable IDs.
Mark all scaled-factor claims as UNSUPPORTED.
"""
import os, json, hashlib, csv
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "01_legacy_retirement")
os.makedirs(OUT_DIR, exist_ok=True)

# =============================================================================
# 1. BUILD CANONICAL CANDIDATE REGISTRY
# Each distinct composition gets a unique immutable ID (CID-XXXX)
# =============================================================================
candidates = [
    # Candidate A — single version across all rebuilds
    {
        "canonical_id": "CID-A-v3",
        "label": "Candidate A",
        "source_rebuild": "rebuild_v3",
        "source_file": "ikms_2026/rebuild_v3/scripts/p5_joint_optimization.py",
        "N2_mol_pct": 3.77,
        "C1_mol_pct": 42.22,
        "C2_mol_pct": 43.67,
        "C2H4_mol_pct": 1.53,
        "C3_mol_pct": 8.82,
        "sum_mol_pct": None,
        "DM_mahalanobis": 2.98,
        "claimed_savings_GWh_yr": 20.06,
        "savings_derivation": "100-quantile schedule (Candidate A only solved)",
        "scaling_factor": 1.000,
        "scaled_from": "SELF",
        "mita_nominal_C": 1.530,
        "prob_pinch_violation_pct": 44.1,
        "retirement_status": "UNSUPPORTED — REJECTED (44.1% MITA VIOLATION RISK)",
    },
    # Candidate B v3.1
    {
        "canonical_id": "CID-B-v3.1",
        "label": "Candidate B (v3.1)",
        "source_rebuild": "rebuild_v3_1_audit",
        "source_file": "ikms_2026/rebuild_v3_1_audit/03_mche_robustness/mita_candidate_comparison.csv",
        "N2_mol_pct": 3.65,
        "C1_mol_pct": 42.10,
        "C2_mol_pct": 46.85,
        "C2H4_mol_pct": 0.25,
        "C3_mol_pct": 7.15,
        "sum_mol_pct": None,
        "DM_mahalanobis": 1.821,
        "claimed_savings_GWh_yr": 16.85,
        "savings_derivation": "Scaled from Candidate A (sf=0.840)",
        "scaling_factor": 0.840,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": 1.845,
        "prob_pinch_violation_pct": 28.9,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE",
    },
    # Candidate B v3.2
    {
        "canonical_id": "CID-B-v3.2",
        "label": "Candidate B (v3.2)",
        "source_rebuild": "rebuild_v3_2",
        "source_file": "ikms_2026/rebuild_v3_2/04_mche_robustness/mita_candidate_comparison.csv",
        "N2_mol_pct": 4.15,
        "C1_mol_pct": 42.10,
        "C2_mol_pct": 46.20,
        "C2H4_mol_pct": 0.40,
        "C3_mol_pct": 7.15,
        "sum_mol_pct": None,
        "DM_mahalanobis": 1.820,
        "claimed_savings_GWh_yr": 16.85,
        "savings_derivation": "Scaled from Candidate A (sf=0.840)",
        "scaling_factor": 0.840,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": None,
        "prob_pinch_violation_pct": None,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE",
    },
    # Candidate B v3.2.1
    {
        "canonical_id": "CID-B-v3.2.1",
        "label": "Candidate B (v3.2.1)",
        "source_rebuild": "rebuild_v3_2_1_audit",
        "source_file": "ikms_2026/rebuild_v3_2_1_audit/07_joint_optimization/candidate_comparison_final.csv",
        "N2_mol_pct": 4.10,
        "C1_mol_pct": 41.20,
        "C2_mol_pct": 47.30,
        "C2H4_mol_pct": 0.25,
        "C3_mol_pct": 7.15,
        "sum_mol_pct": None,
        "DM_mahalanobis": 2.410,
        "claimed_savings_GWh_yr": 16.85,
        "savings_derivation": "Scaled from Candidate A (sf=0.840)",
        "scaling_factor": 0.840,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": None,
        "prob_pinch_violation_pct": None,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE",
    },
    # Candidate C
    {
        "canonical_id": "CID-C-v3",
        "label": "Candidate C",
        "source_rebuild": "rebuild_v3",
        "source_file": "ikms_2026/rebuild_v3_2_1_audit/scripts/p6_joint_optimization_v3_2_1.py (Line 110)",
        "N2_mol_pct": None,
        "C1_mol_pct": None,
        "C2_mol_pct": None,
        "C2H4_mol_pct": None,
        "C3_mol_pct": None,
        "sum_mol_pct": None,
        "DM_mahalanobis": None,
        "claimed_savings_GWh_yr": 13.40,
        "savings_derivation": "Scaled from Candidate A (sf=0.668)",
        "scaling_factor": 0.668,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": None,
        "prob_pinch_violation_pct": None,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE (NO COMPOSITION RECORDED)",
    },
    # Candidate D (baseline, zero savings)
    {
        "canonical_id": "CID-D-v3",
        "label": "Candidate D (Baseline)",
        "source_rebuild": "rebuild_v3",
        "source_file": "ikms_2026/rebuild_v3_2_1_audit/scripts/p6_joint_optimization_v3_2_1.py (Line 111)",
        "N2_mol_pct": None,
        "C1_mol_pct": None,
        "C2_mol_pct": None,
        "C2H4_mol_pct": None,
        "C3_mol_pct": None,
        "sum_mol_pct": None,
        "DM_mahalanobis": None,
        "claimed_savings_GWh_yr": 0.00,
        "savings_derivation": "Scaled from Candidate A (sf=0.000)",
        "scaling_factor": 0.000,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": None,
        "prob_pinch_violation_pct": None,
        "retirement_status": "SUPERSEDED — BASELINE REFERENCE",
    },
    # Candidate R v3.2 (sf=0.558)
    {
        "canonical_id": "CID-R-v3.2",
        "label": "Candidate R (v3.2)",
        "source_rebuild": "rebuild_v3_2",
        "source_file": "ikms_2026/rebuild_v3_2/scripts/p5_joint_optimization.py (Line 94)",
        "N2_mol_pct": 3.77,
        "C1_mol_pct": 42.22,
        "C2_mol_pct": 46.80,
        "C2H4_mol_pct": 1.36,
        "C3_mol_pct": 5.85,
        "sum_mol_pct": None,
        "DM_mahalanobis": 1.89,
        "claimed_savings_GWh_yr": 11.20,
        "savings_derivation": "Scaled from Candidate A (sf=0.558)",
        "scaling_factor": 0.558,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": 2.550,
        "prob_pinch_violation_pct": 4.57,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE",
    },
    # Candidate R v3.2.1 (sf=0.694)
    {
        "canonical_id": "CID-R-v3.2.1",
        "label": "Candidate R (v3.2.1)",
        "source_rebuild": "rebuild_v3_2_1_audit",
        "source_file": "ikms_2026/rebuild_v3_2_1_audit/scripts/p6_joint_optimization_v3_2_1.py (Line 101)",
        "N2_mol_pct": 3.77,
        "C1_mol_pct": 42.22,
        "C2_mol_pct": 46.80,
        "C2H4_mol_pct": 1.36,
        "C3_mol_pct": 5.85,
        "sum_mol_pct": None,
        "DM_mahalanobis": 1.89,
        "claimed_savings_GWh_yr": 13.92,
        "savings_derivation": "Scaled from Candidate A (sf=0.694)",
        "scaling_factor": 0.694,
        "scaled_from": "CID-A-v3",
        "mita_nominal_C": 2.550,
        "prob_pinch_violation_pct": 4.57,
        "retirement_status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE",
    },
]

# Fill sum_mol_pct
for c in candidates:
    comp_fields = ["N2_mol_pct", "C1_mol_pct", "C2_mol_pct", "C2H4_mol_pct", "C3_mol_pct"]
    vals = [c[f] for f in comp_fields if c[f] is not None]
    c["sum_mol_pct"] = round(sum(vals), 4) if len(vals) == 5 else None

df_reg = pd.DataFrame(candidates)
df_reg.to_csv(os.path.join(OUT_DIR, "canonical_candidate_registry.csv"), index=False)

# =============================================================================
# 2. BUILD LEGACY CLAIMS RETIREMENT LEDGER
# =============================================================================
retired_claims = [
    {"claim_id": "LC-01", "claim": "Candidate A saves 20.06 GWh/year",
     "canonical_ref": "CID-A-v3", "status": "UNSUPPORTED — REJECTED (44.1% MITA RISK)"},
    {"claim_id": "LC-02", "claim": "Candidate B saves 16.85 GWh/year",
     "canonical_ref": "CID-B-v3.1 / CID-B-v3.2 / CID-B-v3.2.1",
     "status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE"},
    {"claim_id": "LC-03", "claim": "Candidate C saves 13.40 GWh/year",
     "canonical_ref": "CID-C-v3", "status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE"},
    {"claim_id": "LC-04", "claim": "Candidate R saves 11.20 GWh/year",
     "canonical_ref": "CID-R-v3.2", "status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE"},
    {"claim_id": "LC-05", "claim": "Candidate R saves 13.92 GWh/year",
     "canonical_ref": "CID-R-v3.2.1", "status": "UNSUPPORTED — SCALED FROM LEGACY CANDIDATE"},
    {"claim_id": "LC-06", "claim": "Composition-flow interaction contributes 1.77 GWh/year",
     "canonical_ref": "ALL", "status": "UNSUPPORTED — HARDCODED SYNERGY CONSTANT"},
    {"claim_id": "LC-07", "claim": "Surrogate R2 > 0.98 validates physical accuracy",
     "canonical_ref": "ALL", "status": "UNSUPPORTED — SYNTHETIC ALGEBRAIC DoE TARGETS"},
    {"claim_id": "LC-08", "claim": "Baseline power is independently measured",
     "canonical_ref": "ALL", "status": "UNSUPPORTED — CIRCULAR (STEAM / 4.040)"},
    {"claim_id": "LC-09", "claim": "Steam rate is 4.040 t/MWh",
     "canonical_ref": "ALL", "status": "SUPERSEDED — REPLACED BY IAPWS-IF97 MACHINE RATES"},
    {"claim_id": "LC-10", "claim": "Zero-CAPEX applies to all candidates",
     "canonical_ref": "CID-B-*", "status": "UNSUPPORTED — CANDIDATE B REQUIRES APC (USD 250k-400k)"},
]

df_retired = pd.DataFrame(retired_claims)
df_retired.to_csv(os.path.join(OUT_DIR, "legacy_claims_retirement.csv"), index=False)

# =============================================================================
# 3. INTERACTION TERM RETIREMENT
# =============================================================================
interaction_retirement = {
    "claim": "Composition-flow interaction = 1.77 GWh/year",
    "source_location": "ikms_2026/rebuild_v3_2_1_audit/scripts/p6_joint_optimization_v3_2_1.py",
    "code_evidence": "delta_int = 1.77  # hardcoded constant",
    "derivation": "This value was a hardcoded literal, not derived from comparing four optimization policies through the physical model.",
    "status": "UNSUPPORTED — HARDCODED SYNERGY CONSTANT",
    "v3_3_action": "Must be recalculated from genuine four-policy comparison (baseline, composition-only, flow-only, joint) using physical simulator if available."
}

with open(os.path.join(OUT_DIR, "interaction_term_retirement.json"), "w") as fp:
    json.dump(interaction_retirement, fp, indent=2)

print(f"P1 complete: {len(candidates)} canonical candidates registered, {len(retired_claims)} legacy claims retired.")
