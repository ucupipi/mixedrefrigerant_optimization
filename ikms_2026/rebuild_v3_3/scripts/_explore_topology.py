"""Empirical topology exploration for the MCHE 5E-1 cold side.

The DCS does not give us the PFD, so we do NOT invent a topology. Instead we test the
candidate topologies against the ONE thing the plant does tell us: the MCR returning to
compressor 4K-2 has a measured mass flow, pressure and temperature
(compressor_mapped_operating_points.csv). Whichever topology reproduces the measured
duty closure is the one consistent with the plant; the rest are rejected.
"""
import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE, "ikms_2026", "rebuild_v3_3", "scripts"))

from mche_engine_v33 import MCHEEngine, COMP_ORDER, NeqSimState  # noqa: E402

df = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                              "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
opm = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "processed",
                               "compressor_mapped_operating_points.csv"))

for q in [10, 50, 90]:
    lab = "P%d" % q
    r = df[df["percentile"] == q].iloc[0]
    z = np.array([r["mcr_comp_N2_mol_pct"], r["mcr_comp_C1_mol_pct"], r["mcr_comp_C2_mol_pct"],
                  r["mcr_comp_C2H4_mol_pct"], r["mcr_comp_C3_mol_pct"]]) / 100.0

    mcr_rec = float(r["mcr_mass_flow_t_h"])
    mcr_comp_flow = float(opm[(opm.load_quantile == lab) & (opm.compressor_tag == "4K-2")
                              & (opm.operating_mode == "Baseline")]["mass_flow_t_h"].iloc[0])
    p_sh = float(opm[(opm.load_quantile == lab) & (opm.compressor_tag == "4K-2")
                     & (opm.operating_mode == "Baseline")]["suction_pressure_bar_a"].iloc[0])
    t_sh = float(opm[(opm.load_quantile == lab) & (opm.compressor_tag == "4K-2")
                     & (opm.operating_mode == "Baseline")]["suction_temperature_c"].iloc[0])

    print("=" * 100)
    print("%s  mcr_reconciliation=%.1f t/h | compressor 4K-2 draws %.1f t/h at %.3f bar, %.2f C"
          % (lab, mcr_rec, mcr_comp_flow, p_sh, t_sh))
    print("=" * 100)

    p_hp = float(r["mcr_hp_disch_p_kgcm2a"]) * 0.980665
    t_sep = float(r["mcr_mche_vap_in_temp_C"])
    t_end = -151.0
    m_ng = float(r["feed_gas_flow_t_h"]) * 1000.0 / 3600.0

    # separator flash -> phase split
    st = NeqSimState(dict(zip(COMP_ORDER, z)))
    sep = st.flash_phases(p_hp, t_sep)
    vap = liq = None
    for ph in sep["phases"]:
        if ph["name"].lower().startswith("gas"):
            vap = ph
        else:
            liq = ph
    bv, mw_v, mw_l = vap["beta_mol"], vap["mw_kg_mol"], liq["mw_kg_mol"]
    w_v = (bv * mw_v) / (bv * mw_v + (1 - bv) * mw_l)
    m_vap = mcr_rec * w_v * 1000 / 3600
    m_liq = mcr_rec * (1 - w_v) * 1000 / 3600
    print("  separator: beta=%.4f  vapour=%.1f t/h  liquid=%.1f t/h"
          % (bv, m_vap * 3.6, m_liq * 3.6))

    # ---- HOT duty (same for every topology) --------------------------------
    eng = MCHEEngine()
    ng = {"nitrogen": 0.0006, "methane": 0.9105, "ethane": 0.0230, "propane": 0.0160}
    st_ng = NeqSimState(ng)
    q_feed = m_ng * (st_ng.h_mass(40.0, t_sep) - st_ng.h_mass(40.0, t_end)) / 1000.0
    st_v = NeqSimState(vap["comp"])
    q_vap = m_vap * (st_v.h_mass(p_hp, t_sep) - st_v.h_mass(p_hp, t_end)) / 1000.0
    st_l = NeqSimState(liq["comp"])
    q_liq = m_liq * (st_l.h_mass(p_hp, t_sep) - st_l.h_mass(p_hp, t_end)) / 1000.0
    q_hot = q_feed + q_vap + q_liq
    print("  HOT: feed %.1f + MRvap %.1f + MRliq %.1f = %.1f MW" % (q_feed/1000, q_vap/1000, q_liq/1000, q_hot/1000))

    # ---- cold-side candidate topologies -------------------------------------
    h_out_full = st.h_mass(p_sh, t_sh) if abs(t_sh - float(r["mcr_lp_suct_t_C"])) < 30 else None

    cands = []
    # T1: cold = full MCR recombined, JT from 5C-1 liquid enthalpy at t_end
    for (label, comp, keys, m_cold, h_in) in [
        ("T1 full-MCR, h_in = h_liquid(T_end@p_hp)",
         dict(zip(COMP_ORDER, z)), COMP_ORDER, mcr_comp_flow * 1000 / 3600,
         st_l.h_mass(p_hp, t_end)),
        ("T2 full-MCR, h_in = h_MR(T_end@p_hp)",
         dict(zip(COMP_ORDER, z)), COMP_ORDER, mcr_comp_flow * 1000 / 3600,
         st.h_mass(p_hp, t_end)),
        ("T3 liquid-only, h_in = h_liq(T_end@p_hp)",
         liq["comp"], COMP_ORDER, m_liq, st_l.h_mass(p_hp, t_end)),
        ("T4 full-MCR, h_in = h_MR(t_sep@p_hp) [JT from separator]",
         dict(zip(COMP_ORDER, z)), COMP_ORDER, mcr_comp_flow * 1000 / 3600,
         st.h_mass(p_hp, t_sep)),
    ]:
        st_c = NeqSimState(comp)
        h_out = st_c.h_mass(p_sh, t_sh)
        q_cold = m_cold * (h_out - h_in) / 1000.0
        err = q_hot - q_cold
        cands.append((label, q_cold / 1000, err / 1000, 100 * err / q_hot))

    print("  COLD candidates (measured shell outlet %.2f C @ %.3f bar):" % (t_sh, p_sh))
    for lab, qc, e, ep in cands:
        flag = "  <== CLOSES (<5%%)" if abs(ep) < 5 else ""
        print("    %-52s Q_cold=%7.2f MW  err=%+7.2f MW (%+6.2f%%)%s" % (lab, qc, e, ep, flag))
    print()
