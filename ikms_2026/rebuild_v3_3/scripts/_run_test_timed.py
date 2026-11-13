import os, sys, time, numpy as np, pandas as pd
BASE = r"d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK"
sys.path.insert(0, os.path.join(BASE, "ikms_2026", "rebuild_v3_3", "scripts"))
from mche_engine_v33 import MCHEEngine
df = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation", "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
eng = MCHEEngine()
for q in range(1, 101, 5):
    t0 = time.time()
    rr = df[df["percentile"] == q].iloc[0]
    cc = np.array([rr["mcr_comp_N2_mol_pct"], rr["mcr_comp_C1_mol_pct"], rr["mcr_comp_C2_mol_pct"], rr["mcr_comp_C2H4_mol_pct"], rr["mcr_comp_C3_mol_pct"]]) / 100.0
    o = eng.evaluate(
        mcr_flow_th=float(rr["mcr_mass_flow_t_h"]), mcr_comp=cc,
        feed_flow_th=float(rr["feed_gas_flow_t_h"]),
        t_suct_c=float(rr["mcr_lp_suct_t_C"]),
        p_shell_bara=float(rr["mcr_lp_suct_p_kgcm2a"]) * 0.980665,
        p_hp_bara=float(rr["mcr_hp_suct_p_kgcm2a"]) * 0.980665)
    print(f"q={q:2d}: MITA={o['mita_C']} feasible={o['feasible']} in {time.time()-t0:.2f}s", flush=True)
