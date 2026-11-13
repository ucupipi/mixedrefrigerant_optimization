"""P4 — ENERGY RESIDUAL DECOMPOSITION ON THE VERIFIED TWO-ZONE TOPOLOGY.

Residual convention (defined BEFORE evaluation, per the execution order):

    R_Q  = Q_hot - Q_cold          [kW, signed]
    eps  = R_Q / Q_hot * 100       [%]     reference duty = Q_hot (the cooling that must be delivered)

Sign: R_Q > 0 means the hot side releases more than the cold side absorbs.
All duties in kW. All enthalpies mass-specific [J/kg] from NeqSim PR-EOS at the stream's own
(P, composition). No term is added to close the balance; each candidate correction is applied
ONE AT A TIME and its effect on R_Q is measured.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE, "ikms_2026", "rebuild_v3_3", "scripts"))

from mche_engine_v33 import NeqSimState, COMP_ORDER  # noqa: E402

OUT = os.path.join(BASE, "audit")
OUTDIR = os.path.join(BASE, "outputs", "P4_RESIDUAL_INVESTIGATION")
os.makedirs(OUTDIR, exist_ok=True)

dcs = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                               "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
hy = pd.read_csv(os.path.join(OUT, "P4_hysys_stream_table_raw.csv"))

# ---------------------------------------------------------------- HYSYS anchors
def h(name, field="mass_flow_t_h"):
    r = hy[hy.stream == name]
    return float(r.iloc[0][field]) if len(r) and pd.notna(r.iloc[0][field]) else np.nan


M_FEED = h("FEED_GAS_4E14")          # 284.87 t/h treated feed gas into the cold box
M_MCR = h("MCR_5C1_FEED")            # 487.27 t/h total MR circulation
M_VAP = h("MCR_5C1_VAP")             # 303.51 -> cold bundle
M_LIQ_WB = h("MCR_LIQ_5E1")          # 163.54 -> warm bundle
M_LIQ_4E40 = h("MCR_LIQ_4E40")       # 20.21  -> 4E-40 subcooler

# HYSYS boundary temperatures (connectivity reliable; T field usable at these anchors only)
T_FEED_IN = -35.0        # FEED_GAS_4E14
T_FEED_MID = -52.93      # FEED_GAS_TO_WB  (warm/cold bundle split)
T_FEED_CB = -124.0       # FEED_GAS_TO_CB
T_LNG_JT = -151.7        # LNGtoJT
T_SEP = -35.0            # 5C-1
P_HP = 4222.0 / 100.0    # kPa -> bar  = 42.22
P_LP = 307.34 / 100.0    # warm-bundle return header, bar
P_FEED = 3919.0 / 100.0  # FEED_GAS_4E14, bar

# ---------------------------------------------------------------- one point
def evaluate_point(q, verbose=False):
    r = dcs[dcs["percentile"] == q].iloc[0]
    z = np.array([r["mcr_comp_N2_mol_pct"], r["mcr_comp_C1_mol_pct"], r["mcr_comp_C2_mol_pct"],
                  r["mcr_comp_C2H4_mol_pct"], r["mcr_comp_C3_mol_pct"]]) / 100.0
    z = np.clip(z, 0, None)
    z = z / z.sum()

    st = NeqSimState(dict(zip(COMP_ORDER, z)))
    sep = st.flash_phases(P_HP, T_SEP)
    vap = next((p for p in sep["phases"] if p["name"].lower().startswith("gas")), None)
    liq = next((p for p in sep["phases"] if not p["name"].lower().startswith("gas")), None)
    bv = vap["beta_mol"]
    mw_v, mw_l = vap["mw_kg_mol"], liq["mw_kg_mol"]
    w_v = (bv * mw_v) / (bv * mw_v + (1 - bv) * mw_l)
    m_vap = M_MCR * w_v / 3.6          # t/h -> kg/s
    m_liq = M_MCR * (1 - w_v) / 3.6
    m_feed = M_FEED / 3.6

    # split of liquid between warm bundle and 4E-40, from HYSYS (fixed ratio)
    frac_wb = M_LIQ_WB / M_MCR
    m_liq_wb = M_MCR * frac_wb / 3.6
    frac_4e40 = M_LIQ_4E40 / M_MCR
    m_4e40 = M_MCR * frac_4e40 / 3.6

    # --- HOT: feed gas -35 -> -151.7 ; HP MR -35 -> -125 (cold), -35 -> -120 (warm)
    st_feed = NeqSimState({"nitrogen": float(r["feed_comp_N2_mol_pct"]) / 100,
                           "methane": float(r["feed_comp_C1_mol_pct"]) / 100,
                           "ethane": float(r["feed_comp_C2_mol_pct"]) / 100,
                           "propane": float(r["feed_comp_C3_mol_pct"]) / 100})
    q_feed = m_feed * (st_feed.h_mass(P_FEED, T_FEED_IN) - st_feed.h_mass(P_FEED, T_LNG_JT)) / 1000.0

    st_v = NeqSimState(vap["comp"])
    q_vap_hot = m_vap * (st_v.h_mass(P_HP, T_SEP) - st_v.h_mass(P_HP, -125.0)) / 1000.0
    st_l = NeqSimState(liq["comp"])
    q_liq_hot = m_liq * (st_l.h_mass(P_HP, T_SEP) - st_l.h_mass(P_HP, -120.0)) / 1000.0

    q_hot = q_feed + q_vap_hot + q_liq_hot

    # --- COLD: returns measured at the warm-bundle header (P_LP, DCS t_suct)
    t_suct = float(r["mcr_lp_suct_t_C"])
    st_c = NeqSimState(dict(zip(COMP_ORDER, z)))
    h_out = st_c.h_mass(P_LP, t_suct)

    # cold inlet enthalpy options (JT isenthalpic)
    h_in_liq_Tend = st_l.h_mass(P_HP, -120.0)      # liquid subcooled then JT
    h_in_vap_Tend = st_v.h_mass(P_HP, -125.0)
    h_in_total_Tend = st.h_mass(P_HP, -125.0)

    q_cold_T1 = M_MCR / 3.6 * (h_out - h_in_liq_Tend) / 1000.0      # full MCR, liquid ref (previous T1)
    q_cold_mix = (m_vap * (h_out - h_in_vap_Tend) + m_liq_wb * (h_out - h_in_liq_Tend)) / 1000.0

    R1 = q_hot - q_cold_T1
    R2 = q_hot - q_cold_mix

    if verbose:
        print("  separator beta=%.4f  m_vap=%.1f t/h  m_liq=%.1f t/h" % (bv, m_vap * 3.6, m_liq * 3.6))
        print("  HOT : feed %.2f + MRvap %.2f + MRliq %.2f = %.2f MW" %
              (q_feed / 1e3, q_vap_hot / 1e3, q_liq_hot / 1e3, q_hot / 1e3))
        print("  COLD(T1 full-MCR)  = %.2f MW | COLD(phase-split) = %.2f MW" %
              (q_cold_T1 / 1e3, q_cold_mix / 1e3))
        print("  R1 = %+.2f MW (%+.2f%%)   R2 = %+.2f MW (%+.2f%%)" %
              (R1 / 1e3, R1 / q_hot * 100, R2 / 1e3, R2 / q_hot * 100))

    return {
        "percentile": int(q), "Q_hot_kW": q_hot, "Q_cold_T1_kW": q_cold_T1,
        "Q_cold_phasesplit_kW": q_cold_mix, "R1_kW": R1, "R1_pct": R1 / q_hot * 100,
        "R2_kW": R2, "R2_pct": R2 / q_hot * 100,
        "beta": bv, "m_vap_t_h": m_vap * 3.6, "m_liq_t_h": m_liq * 3.6,
        "q_feed_MW": q_feed / 1e3, "q_vap_hot_MW": q_vap_hot / 1e3, "q_liq_hot_MW": q_liq_hot / 1e3,
    }

print("=" * 96)
print("P4 RESIDUAL DECOMPOSITION ON VERIFIED TWO-ZONE TOPOLOGY")
print("=" * 96)
for q in (10, 50, 90):
    print("\n--- P%d ---" % q)
    evaluate_point(q, verbose=True)

rows = [evaluate_point(q) for q in (10, 50, 90)]
dec = pd.DataFrame(rows)
dec.to_csv(os.path.join(OUT, "P4_RESIDUAL_DECOMPOSITION.csv"), index=False)
print("\nwritten: audit/P4_RESIDUAL_DECOMPOSITION.csv")
