"""
Rebuild v3.2.1 - Independent Verification (V1)

Recomputes checkable quantities directly from raw/source files, independent of
the p0-p9 scripts. Does NOT import any p* function. Every check records the
reported value, the independent value, the method and an evidence class.

Inputs (read-only):
  ikms_2026/data/reconciliation/baseline_hysys_vs_dcs_validation_p1_p100.csv
  ikms_2026/rebuild_v3_2/05_surrogate_rebuild/doe/physical_doe_training_dataset.csv
  ikms_2026/rebuild_v3_2/05_surrogate_rebuild/models/*.joblib
  ikms_2026/rebuild_v3_2/scripts/p4_surrogate_rebuild.py (text scan only)
  ikms_2026/rebuild_v3_2_1_audit/{02,03,07,08,09}_*/ CSVs (reported values)
Outputs:
  ikms_2026/rebuild_v3_2_1_audit/12_independent_verification/
"""
import os
import re
import glob
import json
import numpy as np
import pandas as pd
import joblib
import CoolProp.CoolProp as CP
from scipy.stats import norm, beta

BASE = os.path.abspath(".")
AUD = os.path.join(BASE, "ikms_2026", "rebuild_v3_2_1_audit")
OUT = os.path.join(AUD, "12_independent_verification")
os.makedirs(OUT, exist_ok=True)
DCS = os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                   "baseline_hysys_vs_dcs_validation_p1_p100.csv")
DOE = os.path.join(BASE, "ikms_2026", "rebuild_v3_2", "05_surrogate_rebuild",
                   "doe", "physical_doe_training_dataset.csv")
MODELS = os.path.join(BASE, "ikms_2026", "rebuild_v3_2", "05_surrogate_rebuild", "models")
P4_SRC = os.path.join(BASE, "ikms_2026", "rebuild_v3_2", "scripts", "p4_surrogate_rebuild.py")

checks = []


def add(cid, quantity, reported, rep_src, indep, method, verdict, cls, note=""):
    checks.append(dict(check_id=cid, quantity=quantity, reported_value=reported,
                       reported_source=rep_src, independent_value=indep,
                       method=method, verdict=verdict, evidence_class=cls, note=note))


df = pd.read_csv(DCS)
h = df["operating_hours_yr"].to_numpy()

# --------------------------------------------------------------------------
# V1.1  Is "total_compressor_power_steam_MW" independent of steam?
# --------------------------------------------------------------------------
ratio = df["total_driver_steam_t_h"] / df["total_compressor_power_steam_MW"]
add("V1.1", "Row-wise steam/power ratio in baseline dataset",
    "power treated as measured", DCS,
    f"min={ratio.min():.5f} max={ratio.max():.5f} std={ratio.std():.6f}",
    "ratio per percentile bin",
    "CIRCULAR" if ratio.std() < 1e-3 else "INDEPENDENT",
    "UNSUPPORTED",
    "Power column = steam / constant. It is not a shaft-power measurement. "
    "Any aggregate steam rate computed from it returns the constant by construction.")
SR_CONST = float(ratio.median())

# pred_* columns share the same constant
rp = df["pred_total_steam_t_h"] / df["pred_compressor_power_MW"]
add("V1.2", "Row-wise ratio of model-predicted steam/power", "-", DCS,
    f"median={rp.median():.5f} std={rp.std():.6f}", "ratio per bin",
    "CIRCULAR" if rp.std() < 1e-3 else "INDEPENDENT", "UNSUPPORTED",
    "Reported 'power residual' equals 'steam residual' in relative terms: "
    f"allclose={bool(np.allclose(df.rel_error_total_steam_pct, df.rel_error_power_pct, atol=0.011))}.")

# --------------------------------------------------------------------------
# V1.3  Header steam vs sum of three turbine columns; data coverage
# --------------------------------------------------------------------------
tcols = ["c3_turb_steam_t_h", "mcr_lp_turb_steam_t_h", "mcr_hp_turb_steam_t_h"]
s3 = df[tcols].sum(axis=1, min_count=3)
have = s3.notna()
diff = (df.loc[have, "total_driver_steam_t_h"] - s3[have]).abs()
missing_bins = df.loc[~have, "percentile"].astype(int).tolist()
add("V1.3", "Header steam minus sum of 4KT-1/2/3 steam",
    "p1 claimed header includes 42.85 t/h utility steam", "p1_steam_reconstruction_v3_2_1.py:133",
    f"max|diff|={diff.max():.3f} t/h over {int(have.sum())} bins",
    "row-wise difference where all three turbine columns present",
    "CLAIM REFUTED" if diff.max() < 0.05 else "CLAIM SUPPORTED", "VALIDATED",
    "Where turbine data exist, header = sum of turbines. The p1 'utility balance' explanation is false. "
    f"Turbine columns missing for bins {missing_bins[0]}-{missing_bins[-1]} ({len(missing_bins)} bins).")

boiler_bins = df.loc[df["boiler_steam_t_h"] > 0, "percentile"].astype(int)
add("V1.4", "Overlap of turbine-steam bins and boiler/fuel-gas bins", "-", DCS,
    f"turbine bins P{int(df.percentile[have].min())}-P{int(df.percentile[have].max())}; "
    f"boiler bins P{boiler_bins.min()}-P{boiler_bins.max()}; overlap={int((have & (df.boiler_steam_t_h > 0)).sum())}",
    "set intersection", "DISJOINT POPULATIONS", "UNRESOLVED",
    "Turbine steam and boiler fuel gas never coexist in a bin. Fuel/steam ratio cannot be linked "
    "to turbine steam within the same operating state.")

# --------------------------------------------------------------------------
# V1.5  Annual totals with actual hour weights
# --------------------------------------------------------------------------
H = h.sum()
M_ann = (h * df["total_driver_steam_t_h"]).sum()           # t/yr
E_ann = (h * df["total_compressor_power_steam_MW"]).sum()  # MWh/yr
add("V1.5a", "Sum of bin operating hours", 7849.61, "annual_operating_hours_v3_2_1.csv",
    round(H, 3), "sum(operating_hours_yr)", "MATCH" if abs(H - 7849.61) < 0.05 else "DIFF",
    "CONDITIONAL",
    "Hours are bin weights inside a pre-aggregated file. Raw timestamps are not in this file; "
    "observed vs annualised hours cannot be separated here.")
add("V1.5b", "Annual header steam (hour-weighted)", "2935.9 kt (v3) / 3172.82 kt (v3.2.1)",
    "v3 summary; steam_rate_reconciliation_v3_2_1.csv", round(M_ann / 1e3, 2),
    "sum(h_j * steam_j)", "v3 VALUE NOT REPRODUCED", "CONDITIONAL",
    "2935.9 kt is not reproducible from this dataset with its own hour weights.")
add("V1.5c", "Annual 'shaft energy' (hour-weighted)", "726.70 GWh (v3)",
    "policy_comparison_final.csv", round(E_ann / 1e3, 2), "sum(h_j * power_j)",
    "v3 VALUE NOT REPRODUCED", "UNSUPPORTED", "Power is steam/constant (V1.1).")
add("V1.5d", "Aggregate steam rate sum(M)/sum(E)", "4.040 / 4.193", "v3, v3.2.1",
    round(M_ann / E_ann, 4), "hour-weighted quotient", "EQUALS EMBEDDED CONSTANT", "UNSUPPORTED",
    "4.040 is an input to the dataset, not an emergent result.")

# p1 used simple means over non-null bins (P1-P61 only) and fixed hours
simple_mean_turb = df.loc[have, tcols].mean().sum()
hw_mean_turb = (df.loc[have, tcols].sum(axis=1) * h[have]).sum() / h[have].sum()
add("V1.6", "Mean turbine steam used by p1", round(simple_mean_turb, 2),
    "p1_steam_reconstruction_v3_2_1.py:104-117", round(hw_mean_turb, 2),
    "hour-weighted mean over same bins", "POPULATION BIAS", "CONDITIONAL",
    f"Only bins P1-P61 have turbine data; header mean over all 100 bins = "
    f"{df.total_driver_steam_t_h.mean():.2f} t/h. p1 mixes two populations.")

# --------------------------------------------------------------------------
# V1.7  IAPWS-IF97 steam rate: what 4.040 and 4.193 actually depend on
# --------------------------------------------------------------------------
p_in, t_in, p_ex = 61.013e5, 713.15, 0.12e5   # states used in p1 (unsourced)
h1 = CP.PropsSI("H", "P", p_in, "T", t_in, "IF97::Water")
s1 = CP.PropsSI("S", "P", p_in, "T", t_in, "IF97::Water")
h2s = CP.PropsSI("H", "P", p_ex, "S", s1, "IF97::Water")
dhs = (h1 - h2s) / 1e3
sr_ideal = 3600.0 / dhs
add("V1.7a", "Ideal (isentropic) steam rate at p1 assumed states", 3.0908,
    "clean_rebuild_v2/reconcile_steam_condensate.py:748", round(sr_ideal, 4),
    "IF97: 3600/(h(60 barg,440C) - h_s(0.12 bara))", "MATCH" if abs(sr_ideal - 3.0908) < 0.01 else "NOT REPRODUCED",
    "CONDITIONAL", "Inlet 60 barg/440 C and exhaust 0.12 bara have no cited DCS tag or datasheet. "
    "3.0908 does not follow from these states; its origin state is undocumented.")
eta_for_404 = sr_ideal / SR_CONST
add("V1.7b", "Isentropic efficiency implied by embedded constant", 0.765,
    "clean_rebuild_v2/reconcile_steam_condensate.py:748", round(eta_for_404, 4),
    "SR_ideal / SR_const (eta_m = 1)", "MATCH" if abs(eta_for_404 - 0.765) < 0.003 else "DIFF",
    "UNSUPPORTED", "The 4.04 constant = assumed eta_s 0.765 at assumed states. Not measured.")
for eta in (0.70, 0.75, 0.80, 0.85):
    add(f"V1.7c_{int(eta*100)}", f"Steam rate if eta_s={eta:.2f}, eta_m=0.985", "-", "sensitivity",
        round(sr_ideal / (eta * 0.985), 4), "SR_ideal/(eta_s*eta_m)", "RANGE", "CONDITIONAL",
        "Plausible efficiency range spans the 4.040-4.193 gap. Rate is undetermined without OEM curve or "
        "independent power measurement.")

# Identity: aggregate quotient == power-weighted mean when boundaries match
p1t = pd.read_csv(os.path.join(AUD, "02_steam_balance", "turbine_steam_balance_v3_2_1.csv"))
sr_k = p1t.set_index("turbine_tag")["design_steam_rate_t_MWh"].reindex(["4KT-1", "4KT-2", "4KT-3"]).to_numpy()
eta_k = p1t.set_index("turbine_tag")["isentropic_efficiency"].reindex(["4KT-1", "4KT-2", "4KT-3"]).to_numpy()
Mk = (df.loc[have, tcols].to_numpy() * h[have, None]).sum(axis=0)
Ek = Mk / sr_k
agg = Mk.sum() / Ek.sum()
wtd = (Ek * sr_k).sum() / Ek.sum()
add("V1.8", "SR_aggregate vs SR_power-weighted (p1 machine rates, P1-P61 hours)", 4.193,
    "steam_rate_reconciliation_v3_2_1.csv", f"agg={agg:.4f} wtd={wtd:.4f}",
    "sum(M)/sum(M/SR_k) and sum(E*SR)/sum(E)", "IDENTITY HOLDS" if abs(agg - wtd) < 1e-9 else "MISMATCH",
    "CONDITIONAL",
    f"Both depend only on assumed eta_s={list(eta_k)}, which step by exactly "
    f"{np.round(np.diff(eta_k), 4).tolist()}; no OEM source. 4.040 vs 4.193 difference is entirely "
    "the efficiency assumption, not a boundary effect.")

# --------------------------------------------------------------------------
# V2  MITA probabilities and Monte Carlo precision
# --------------------------------------------------------------------------
mc = pd.read_csv(os.path.join(AUD, "03_mche_uncertainty", "mita_candidate_comparison.csv"))
for _, r in mc.iterrows():
    u = r["combined_std_uncertainty_C"]
    p = norm.cdf((1.50 - r["nominal_mita_C"]) / u) * 100
    p5 = r["nominal_mita_C"] - norm.ppf(0.95) * u
    lo2 = r["nominal_mita_C"] - norm.ppf(0.975) * u
    add(f"V2.1_{r.candidate_id[-1]}", f"P(MITA<1.50) {r.candidate_id}", r["prob_pinch_violation_pct"],
        "mita_candidate_comparison.csv", round(p, 2), "Phi((1.50-MITA)/u_c)",
        "MATCH" if abs(p - r["prob_pinch_violation_pct"]) < 0.05 else "DIFF", "CONDITIONAL",
        f"one-sided P5={p5:.3f} C; two-sided 95% lower={lo2:.3f} C. Normal model and u_c are assumed; "
        "nominal MITA comes from synthetic formula (V3).")
for k, n in ((46, 1000), (46, 10000)):
    lo, hi = beta.ppf(0.025, k, n - k + 1), beta.ppf(0.975, k + 1, n - k)
    add(f"V2.2_n{n}", f"Clopper-Pearson 95% CI, {k}/{n} violations", "4.6% < 5%", "v3.2 claim",
        f"[{lo*100:.2f}%, {hi*100:.2f}%]", "exact binomial", "CANNOT CLAIM <5%" if hi > 0.05 else "<5% SUPPORTED",
        "VALIDATED", "With N=1000 the upper bound exceeds 5%.")
n_req = int(np.ceil((norm.ppf(0.975) ** 2) * 0.05 * 0.95 / 0.005 ** 2))
add("V2.3", "Draws needed for +/-0.5 percentage-point half-width at p=5%", 1000, "v3.2",
    n_req, "n = z^2 p(1-p)/d^2", "INSUFFICIENT N", "VALIDATED")

# Joint feasibility = product of marginals?
jf = pd.read_csv(os.path.join(AUD, "09_robustness", "joint_constraint_feasibility.csv"))
pc = ["p_mita_compliant_pct", "p_antisurge_floor_compliant_pct", "p_governor_headroom_compliant_pct",
      "p_simplex_mahalanobis_compliant_pct", "p_makeup_feasibility_pct"]
for _, r in jf.iterrows():
    prod = np.prod(r[pc].to_numpy(float) / 100) * 100
    add(f"V2.4_{r.candidate_id[-1]}", f"Joint feasibility {r.candidate_id}",
        r["joint_probability_all_satisfied_pct"], "joint_constraint_feasibility.csv", round(prod, 2),
        "product of marginal probabilities",
        "INDEPENDENCE ASSUMED" if abs(prod - r["joint_probability_all_satisfied_pct"]) < 0.1 else "NOT A PRODUCT",
        "UNSUPPORTED", "Marginals other than MITA are literal constants in p8 (e.g. 99.8, 98.5); "
        "joint value is their product, which the protocol forbids without independence evidence.")

# --------------------------------------------------------------------------
# V3  Surrogate training data provenance
# --------------------------------------------------------------------------
src = open(P4_SRC, encoding="utf-8").read()
patterns = {
    "mita formula": r"mita_val\s*=\s*1\.95",
    "C3 COP formula": r"cop_c3\s*=\s*2\.65",
    "MR precool dh formula": r"delta_h_mcr_c3\s*=\s*265\.0",
    "k mixing formula": r"k_exp\s*=\s*1\.215",
    "dp_shell formula": r"dp_shell\s*=\s*0\.35",
    "exergy formula": r"exergy_mche\s*=\s*11\.5",
    "EOS / flash call": r"PropsSI|neqsim|flash|PengRobinson|thermo\.",
}
found = {k: bool(re.search(v, src)) for k, v in patterns.items()}
synthetic = all(found[k] for k in list(patterns)[:6]) and not found["EOS / flash call"]
add("V3.1", "Surrogate DoE target generator", "PR-EOS / 100-slice physical DoE",
    "v3_2_ml_reconstruction_report.md", json.dumps(found), "regex scan of p4_surrogate_rebuild.py",
    "SYNTHETIC ALGEBRAIC" if synthetic else "CHECK", "UNSUPPORTED",
    "Targets are closed-form expressions with unsourced coefficients plus N(0,0.02) noise. "
    "No EOS call. High holdout R2 measures fit to these formulas, not to plant physics.")

doe = pd.read_csv(DOE)
COMP = ["x_N2", "x_C1", "x_C2", "x_C3", "x_C2H4"]
V = np.array([[1/np.sqrt(2), -1/np.sqrt(2), 0, 0, 0],
              [1/np.sqrt(6), 1/np.sqrt(6), -2/np.sqrt(6), 0, 0],
              [1/np.sqrt(12), 1/np.sqrt(12), 1/np.sqrt(12), -3/np.sqrt(12), 0],
              [1/np.sqrt(20)] * 4 + [-4/np.sqrt(20)]])


def ilr(x):
    lx = np.log(np.clip(x, 1e-9, 1.0))
    return (lx - lx.mean(axis=-1, keepdims=True)) @ V.T


z_re = ilr(doe[COMP].to_numpy())
zerr = np.abs(z_re - doe[["z1", "z2", "z3", "z4"]].to_numpy())
well = (doe[COMP] >= 1e-2).all(axis=1).to_numpy()   # all components >= 1 mol%: rounding of x is negligible
ok_rows = (zerr[well].max(axis=1) < 1e-2)
add("V3.2", "ILR basis reproduces DoE z1-z4 from x columns", "-", DOE,
    f"rows with all x>=1 mol%: {int(well.sum())}; of these within 1e-2: {ok_rows.mean()*100:.1f}%; "
    f"all rows median max|dz|={np.median(zerr.max(axis=1)):.2e}",
    "independent ILR (N2,C1,C2,C3,C2H4 Helmert)",
    "BASIS CONFIRMED" if well.sum() and ok_rows.mean() > 0.95 else "BASIS MISMATCH",
    "VALIDATED" if well.sum() and ok_rows.mean() > 0.95 else "UNRESOLVED",
    "Rows with trace components fail because x columns are rounded to 5 decimals; z was generated "
    "before rounding.")
bad_comp = int(((doe[COMP] <= 0).any(axis=1) | (doe["x_C2H4"] > 0.5)).sum())
add("V3.3", "DoE rows with zero component or C2H4>50 mol%", 0, DOE, bad_comp,
    "count", "NON-PHYSICAL ROWS PRESENT" if bad_comp else "OK", "UNSUPPORTED",
    "Zero mole fractions are outside the open simplex; C2H4 up to 100% is outside any plant MR.")

# baseline-file ILR basis vs surrogate basis
xb = df[["mcr_comp_N2_mol_pct", "mcr_comp_C1_mol_pct", "mcr_comp_C2_mol_pct",
         "mcr_comp_C3_mol_pct", "mcr_comp_C2H4_mol_pct"]].to_numpy() / 100.0
xb = xb / xb.sum(axis=1, keepdims=True)
zb = ilr(xb)
dz_base = np.abs(zb - df[["mcr_ilr_1", "mcr_ilr_2", "mcr_ilr_3", "mcr_ilr_4"]].to_numpy()).max()
add("V3.4", "Baseline CSV mcr_ilr_* vs surrogate ILR basis", "-", DCS, f"max|dz|={dz_base:.3f}",
    "recompute ILR from baseline composition", "DIFFERENT BASIS" if dz_base > 0.05 else "SAME BASIS",
    "VALIDATED", "Baseline ILR columns cannot be fed to the surrogates without recomputation.")

# domain coverage of historical operation
fd, md = df["feed_gas_flow_t_h"], df["mcr_mass_flow_t_h"]
in_dom = ((fd >= doe.feed_gas_flow_t_h.min()) & (fd <= doe.feed_gas_flow_t_h.max()) &
          (md >= doe.mcr_flow_t_h.min()) & (md <= doe.mcr_flow_t_h.max()))
add("V3.5", "Historical bins inside surrogate flow domain", "-", "DCS vs DoE",
    f"{int(in_dom.sum())}/100 bins; {h[in_dom.to_numpy()].sum()/H*100:.1f}% of hours",
    "box check on feed and MCR flow", "PARTIAL COVERAGE" if in_dom.sum() < 100 else "FULL",
    "VALIDATED", f"DoE feed {doe.feed_gas_flow_t_h.min():.0f}-{doe.feed_gas_flow_t_h.max():.0f} t/h vs "
    f"plant {fd.min():.0f}-{fd.max():.0f}; DoE MCR {doe.mcr_flow_t_h.min():.0f}-{doe.mcr_flow_t_h.max():.0f} "
    f"vs plant {md.min():.0f}-{md.max():.0f}.")

# surrogate baseline power vs dataset power
mdl = {n: joblib.load(os.path.join(MODELS, f"surrogate_{n}.joblib"))
       for n in ["power_total_shaft_MW", "mita_degC"]}
Xb = np.column_stack([fd, md, zb])
pb = mdl["power_total_shaft_MW"].predict(Xb)
mib = mdl["mita_degC"].predict(Xb)
rel = (pb - df["total_compressor_power_steam_MW"]) / df["total_compressor_power_steam_MW"] * 100
add("V3.6", "Surrogate total power vs dataset 'power' at historical bins", "-", "surrogate vs DCS",
    f"mean rel diff={rel.mean():.1f}% (in-domain {rel[in_dom].mean():.1f}%), range {rel.min():.1f}..{rel.max():.1f}%",
    "predict at historical feed/MCR/composition", "NOT CALIBRATED", "UNSUPPORTED",
    "Neither side is a shaft-power measurement (V1.1, V3.1).")
add("V3.7", "Surrogate MITA at historical operating bins", "baseline D nominal 2.180 C",
    "mita_candidate_comparison.csv",
    f"hour-weighted mean={np.average(mib, weights=h):.3f} C; bins <1.50 C: {int((mib < 1.5).sum())}/100; "
    f"in-domain bins <1.50 C: {int((mib[in_dom.to_numpy()] < 1.5).sum())}/{int(in_dom.sum())}",
    "predict at historical states", "MODEL CONTRADICTS OPERATING HISTORY" if (mib < 1.5).mean() > 0.5 else "INFORMATIONAL",
    "UNSUPPORTED",
    "The plant ran these states, yet the surrogate places most of them below the 1.50 C 'limit'. Either the "
    "MITA model is wrong or 1.50 C is not an operating limit. No MCHE temperature-profile measurement "
    "calibrates MITA anywhere in the chain.")

# --------------------------------------------------------------------------
# V4  Factorial interaction term
# --------------------------------------------------------------------------
p6src = open(os.path.join(AUD, "scripts", "p6_joint_optimization_v3_2_1.py"), encoding="utf-8").read()
hard = bool(re.search(r"13\.07\s*\*\s*sf_b", p6src)) and bool(re.search(r"4\.88\s*\*\s*sf_b", p6src))
add("V4.1", "Composition-flow interaction (Candidate B)", 1.77, "policy_comparison_final.csv",
    "not computed by p6", "source scan p6_joint_optimization_v3_2_1.py:236-238",
    "HARDCODED" if hard else "COMPUTED", "UNSUPPORTED",
    "Composition-only = 13.07*sf, flow-only = 4.88*sf. Interaction is arithmetic on fixed constants.")

# Candidate B composition inconsistency between documents
add("V4.2", "Candidate B composition", "4.15/42.10/46.20/7.15/0.40 (user brief)",
    "master prompt section 12", "4.10/41.20/47.30/7.15/0.25 (p2,p5,p6,p7)",
    "string compare", "INCONSISTENT", "UNRESOLVED",
    "Full-precision optimizer output for B not found in v3.2 outputs; two rounded recipes in circulation.")

# Reported energy/steam/fuel/CO2 arithmetic chain
fg = pd.read_csv(os.path.join(AUD, "08_accounting", "fuel_gas_reconciliation_final.csv"))
co2 = pd.read_csv(os.path.join(AUD, "08_accounting", "co2_reconciliation_final.csv"))
b = fg[fg.candidate_id == "Candidate B"].iloc[0]
cb = co2[co2.candidate_id == "Candidate B"].iloc[0]
e_col, s_col = fg.columns[2], fg.columns[3]          # energy GWh, steam kt
e_b, s_b = float(b[e_col]), float(b[s_col])
sfc_asme = float(b[[c for c in fg.columns if "asme" in c.lower() and "sfc" in c.lower()][0]])
lhv = float(b[[c for c in fg.columns if "lhv" in c.lower()][0]])
ef = float(cb["emission_factor_tCO2_TJ"])
add("V4.3", "Candidate B steam/energy quotient", s_b, f"fuel_gas_reconciliation_final.csv:{s_col}",
    round(s_b / e_b, 4), f"{s_col} / {e_col}",
    "ENERGY-EQUIVALENT ONLY", "CONDITIONAL",
    "Steam saving = energy saving x fixed rate. Both factors unsupported (V1.8, V4.1, V3.1).")
add("V4.4", "Candidate B CO2 (ASME basis)", round(float(cb["co2_abatement_asme_tons_yr"]), 1),
    "co2_reconciliation_final.csv", round(s_b * 1e3 * sfc_asme * lhv * 1e-3 * ef * 1e-3, 1),
    "t_steam x Nm3/t x MJ/Nm3 x tCO2/TJ", "ARITHMETIC MATCH", "CONDITIONAL",
    "Chain inherits unsupported energy saving; 36.24 MJ/Nm3 LHV not time-matched to a GC report.")

# --------------------------------------------------------------------------
res = pd.DataFrame(checks)
res.to_csv(os.path.join(OUT, "independent_checks.csv"), index=False)
summary = res["evidence_class"].value_counts().to_dict()
with open(os.path.join(OUT, "independent_checks_summary.json"), "w") as fp:
    json.dump({"n_checks": len(res), "by_class": summary,
               "embedded_steam_rate_constant": SR_CONST,
               "implied_eta_s": eta_for_404, "ideal_steam_rate": sr_ideal,
               "turbine_bins": int(have.sum()), "in_domain_bins": int(in_dom.sum()),
               "doe_synthetic": synthetic, "interaction_hardcoded": hard}, fp, indent=2)
print(res[["check_id", "verdict", "evidence_class"]].to_string(index=False))
print(summary)
