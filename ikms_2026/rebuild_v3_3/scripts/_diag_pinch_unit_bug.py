"""Diagnose whether the reported MTA crossover is real physics or the unit bug
at neqsim_engine.py:201-203, where min_pinch (degC) is compared against
-shortfall_mw (MW)."""
import os
import sys

import numpy as np
import pandas as pd

os.environ["JAVA_HOME"] = r"C:\Users\khari\AppData\Local\openLCA\jre"
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(os.path.join(BASE, "MR_OPTIMIZATION_REBUILD", "src"))

from thermodynamics.neqsim_engine import evaluate_mche_pinch_5comp  # noqa: E402

df = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                              "baseline_hysys_vs_dcs_validation_p1_p100.csv"))

print("%-5s %8s %8s %8s | %9s %9s %9s | %9s" % (
    "Q", "mcr_t_h", "feed_t_h", "t_suct", "duty_MW", "min_pinch", "cold_appr", "np.min_raw"))
print("-" * 90)

rows = []
for q in [1, 5, 10, 25, 50, 75, 90]:
    r = df[df["percentile"] == q].iloc[0]
    comp = [r["mcr_comp_N2_mol_pct"] / 100.0, r["mcr_comp_C1_mol_pct"] / 100.0,
            r["mcr_comp_C2_mol_pct"] / 100.0, r["mcr_comp_C2H4_mol_pct"] / 100.0,
            r["mcr_comp_C3_mol_pct"] / 100.0]
    res = evaluate_mche_pinch_5comp(
        mcr_flow_th=float(r["mcr_mass_flow_t_h"]),
        mcr_comp=comp,
        feed_flow_th=float(r["feed_gas_flow_t_h"]),
        t_suct_c=float(r["mcr_lp_suct_t_C"]),
        p_shell_bara=float(r["mcr_lp_suct_p_kgcm2a"]) * 0.980665,
        n_slices=50,
    )
    # Reconstruct the RAW temperature-only minimum (before the MW penalty)
    t_h = np.array(res["t_hot_profile"])
    t_c = np.array(res["t_cold_profile"])
    dt = t_h - t_c
    raw_min = float(np.min(dt))
    penalty = float(res["min_pinch"]) - raw_min

    print("%-5d %8.1f %8.1f %8.1f | %9.2f %9.3f %9.3f | %9.3f  penalty=%+.3f" % (
        q, r["mcr_mass_flow_t_h"], r["feed_gas_flow_t_h"], r["mcr_lp_suct_t_C"],
        res["total_duty_mw"], res["min_pinch"], res["cold_approach"], raw_min, penalty))

    rows.append({"percentile": q, "reported_min_pinch": res["min_pinch"],
                 "raw_temperature_min_C": raw_min, "penalty_delta": penalty,
                 "duty_MW": res["total_duty_mw"]})

df_out = pd.DataFrame(rows)
print()
print("=== INTERPRETATION ===")
n_penalised = int((df_out["penalty_delta"].abs() > 1e-9).sum())
print("quantiles where reported min_pinch != raw temperature minimum:", n_penalised, "/", len(df_out))
if n_penalised:
    print("-> the MW-vs-degC penalty at neqsim_engine.py:201-203 IS FIRING.")
    print("-> reported 'crossover' values are NOT temperatures; they are -shortfall_mw.")
print()
print("raw temperature minima (true pinch, degC):")
print(df_out[["percentile", "raw_temperature_min_C"]].to_string(index=False))
