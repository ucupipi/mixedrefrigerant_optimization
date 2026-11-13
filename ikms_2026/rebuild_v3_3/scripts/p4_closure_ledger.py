"""P4 CLOSURE LEDGER — strict SI, per-stream enthalpy accounting.

Purpose: find WHERE the energy residual physically lives, without adding any
arbitrary closing term (AGENTS.md Rule 1, Rule 4, Rule 11).

Units: SI internally (kg/s, J/kg, Pa, K). MW only at print boundary.
Enthalpy source: NeqSim Peng-Robinson TP flash via NeqSimState.h_mass() -> J/kg.

Physical topology used (from verified HYSYS V12.1 connectivity, mass balance
closed to 0.000% on every node):

  5C-1 HP sep @ 42.22 bara, -35 C, 487.27 t/h, vf 0.685 mol
     |-- VAPOUR 303.51 t/h --> cold bundle --> MCRVtoCB (-125 C)
     |                                    --> MCRV_TO_JT (-152.90 C)
     |                                    ==JT==> MCRV_FROM_JT (-151.24 C)
     |                                    --> MCRVfromCB (-140.08 C) ----+
     |-- LIQUID 183.76 t/h                                             |
          |-- 163.54 t/h --> MCRL_TO_JT (-120 C)                       |
          |              ==JT==> MCRL_FROM_JT (-127.73 C) --> mix ----+
          |--  20.21 t/h --> 4E-40 subcooler (SEPARATE boundary)       |
                                                                      |
                              MIX_WB_RETURN 467.06 t/h @ -136.73 C <---+
                                      --> 4C-7 LP suction drum
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE, "ikms_2026", "rebuild_v3_3", "scripts"))

os.environ.setdefault("JAVA_HOME", r"C:\Users\khari\AppData\Local\openLCA\jre")

from mche_engine_v33 import NeqSimState, COMP_ORDER, FEED_COMP  # noqa: E402

# ------------------------------------------------------------------ constants
T_SEP_C = -35.0          # 5C-1 separator temperature (HYSYS + DCS anchor)
P_HP_BARA = 42.22        # 5C-1 pressure, 4222 kPa
P_SHELL_BARA = 3.0734    # warm-bundle return header, 307.34 kPa
P_FEED_BARA = 39.19      # FEED_GAS_4E14, 3919 kPa

T_VAP_TO_JT = -152.90    # MCRV_TO_JT
T_VAP_FROM_JT = -151.24  # MCRV_FROM_JT
T_VAP_CB_OUT = -140.08   # MCRVfromCB  (vapour leaves cold bundle)
T_LIQ_TO_JT = -120.00    # MCRL_TO_JT
T_LIQ_FROM_JT = -127.73  # MCRL_FROM_JT (liquid leaves warm bundle)
T_MIX_RETURN = -136.73   # MIX_WB_RETURN
T_FEED_IN = -35.00       # FEED_GAS_4E14
T_FEED_OUT = -151.70     # LNGtoJT

M_TOTAL = 487.27         # t/h
M_VAP = 303.51           # t/h
M_LIQ_WB = 163.54        # t/h  (warm bundle liquid)
M_LIQ_4E40 = 20.21       # t/h  (separate exchanger)
M_FEED = 284.87          # t/h


def mw(*args):
    """Convert mass flow [t/h] * enthalpy diff [J/kg] -> MW."""
    flow_th, dh = args
    return (flow_th * 1000.0 / 3600.0) * dh / 1.0e6


def load_dcs_row(percentile: int) -> pd.Series:
    d = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                                 "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
    return d[d["percentile"] == percentile].iloc[0]


def mcr_composition(row: pd.Series) -> tuple[dict, dict]:
    """Return (normalised total composition, feed composition) from the DCS row."""
    z = {
        "nitrogen": float(row["mcr_comp_N2_mol_pct"]) / 100.0,
        "methane": float(row["mcr_comp_C1_mol_pct"]) / 100.0,
        "ethane": float(row["mcr_comp_C2_mol_pct"]) / 100.0,
        "ethylene": float(row["mcr_comp_C2H4_mol_pct"]) / 100.0,
        "propane": float(row["mcr_comp_C3_mol_pct"]) / 100.0,
    }
    tot = sum(z.values())
    z = {k: v / tot for k, v in z.items()}

    feed = {
        "nitrogen": float(row["feed_comp_N2_mol_pct"]) / 100.0,
        "methane": float(row["feed_comp_C1_mol_pct"]) / 100.0,
        "ethane": float(row["feed_comp_C2_mol_pct"]) / 100.0,
        "propane": float(row["feed_comp_C3_mol_pct"]) / 100.0,
    }
    feed["ethylene"] = 0.0
    ftot = sum(feed.values())
    feed = {k: v / ftot for k, v in feed.items()}
    return z, feed


def build_basis(z: dict, label: str) -> dict:
    """Flash 5C-1 and derive the mass-basis phase split from molar beta."""
    st = NeqSimState(z)
    sep = st.flash_phases(P_HP_BARA, T_SEP_C)
    vap = liq = None
    for ph in sep["phases"]:
        if ph["name"].lower().startswith("gas"):
            vap = ph
        else:
            liq = ph
    if vap is None or liq is None:
        raise RuntimeError(f"{label}: single-phase at 5C-1, cannot split")

    bv = float(vap["beta_mol"])
    mw_v, mw_l = float(vap["mw_kg_mol"]), float(liq["mw_kg_mol"])
    mw_bar = bv * mw_v + (1.0 - bv) * mw_l
    w_vap = (bv * mw_v) / mw_bar
    return {
        "beta_mol": bv,
        "w_vap_mass": w_vap,
        "m_vap_th": M_TOTAL * w_vap,
        "m_liq_th": M_TOTAL * (1.0 - w_vap),
        "z_vap": vap["comp"],
        "z_liq": liq["comp"],
        "mw_vap": mw_v,
        "mw_liq": mw_l,
    }


def ledger(percentile: int, verbose: bool = True) -> dict:
    row = load_dcs_row(percentile)
    z, feed = mcr_composition(row)
    b = build_basis(z, f"P{percentile}")

    if verbose:
        print("=" * 92)
        print(f"P{percentile}  |  MCR {M_TOTAL} t/h  feed {M_FEED} t/h"
              f"  |  beta_mol {b['beta_mol']:.4f}  -> vap {b['m_vap_th']:.2f}"
              f" t/h, liq {b['m_liq_th']:.2f} t/h")
        print("=" * 92)

    # ------------------------------------------------ HOT SIDE (heat released)
    # Feed gas cools -35 -> -151.7 at its own pressure and its own composition
    st_f = NeqSimState(feed)
    dh_feed = st_f.h_mass(P_FEED_BARA, T_FEED_IN) - st_f.h_mass(P_FEED_BARA, T_FEED_OUT)
    q_feed = mw(M_FEED, dh_feed)

    # MR vapour cools -35 -> -152.90 at 42.22 bara (its own phase composition)
    st_v = NeqSimState(b["z_vap"])
    dh_v = st_v.h_mass(P_HP_BARA, T_SEP_C) - st_v.h_mass(P_HP_BARA, T_VAP_TO_JT)
    q_v = mw(b["m_vap_th"], dh_v)

    # MR liquid (warm bundle portion) cools -35 -> -120 at 42.22 bara
    st_l = NeqSimState(b["z_liq"])
    dh_l = st_l.h_mass(P_HP_BARA, T_SEP_C) - st_l.h_mass(P_HP_BARA, T_LIQ_TO_JT)
    q_l = mw(M_LIQ_WB, dh_l)

    q_hot = q_feed + q_v + q_l

    # ------------------------------------------------ COLD SIDE (heat absorbed)
    # Vapour path: isenthalpic JT from 42.22 bara / -152.90 C to 3.073 bara.
    # JT conserves enthalpy, so shell inlet enthalpy == enthalpy at JT inlet.
    h_vap_shell_in = st_v.h_mass(P_HP_BARA, T_VAP_TO_JT)
    h_vap_shell_out = st_v.h_mass(P_SHELL_BARA, T_VAP_CB_OUT)
    q_c_v = mw(M_VAP, h_vap_shell_out - h_vap_shell_in)

    # Liquid path: JT from 42.22 bara / -120 C -> 3.073 bara / -127.73 C.
    h_liq_shell_in = st_l.h_mass(P_HP_BARA, T_LIQ_TO_JT)
    h_liq_shell_out = st_l.h_mass(P_SHELL_BARA, T_LIQ_FROM_JT)
    q_c_l = mw(M_LIQ_WB, h_liq_shell_out - h_liq_shell_in)

    q_cold = q_c_v + q_c_l

    closure = q_hot - q_cold
    closure_pct = 100.0 * closure / q_hot

    out = {
        "percentile": percentile,
        "beta_mol": b["beta_mol"],
        "m_vap_th": b["m_vap_th"],
        "m_liq_th": b["m_liq_th"],
        "Q_feed_MW": q_feed,
        "Q_MRvap_hot_MW": q_v,
        "Q_MRliq_hot_MW": q_l,
        "Q_hot_MW": q_hot,
        "Q_MRvap_cold_MW": q_c_v,
        "Q_MRliq_cold_MW": q_c_l,
        "Q_cold_MW": q_cold,
        "closure_MW": closure,
        "closure_pct": closure_pct,
        "dh_feed_kJ_kg": dh_feed / 1e3,
        "dh_vap_hot_kJ_kg": dh_v / 1e3,
        "dh_liq_hot_kJ_kg": dh_l / 1e3,
        "dh_vap_cold_kJ_kg": (h_vap_shell_out - h_vap_shell_in) / 1e3,
        "dh_liq_cold_kJ_kg": (h_liq_shell_out - h_liq_shell_in) / 1e3,
    }

    if verbose:
        print(f"  HOT   feed  {q_feed:8.3f} MW  (dh {dh_feed/1e3:8.2f} kJ/kg)")
        print(f"        MRvap {q_v:8.3f} MW  (dh {dh_v/1e3:8.2f} kJ/kg)  @ {b['m_vap_th']:.2f} t/h")
        print(f"        MRliq {q_l:8.3f} MW  (dh {dh_l/1e3:8.2f} kJ/kg)  @ {M_LIQ_WB:.2f} t/h")
        print(f"        TOTAL {q_hot:8.3f} MW")
        print(f"  COLD  MRvap {q_c_v:8.3f} MW  (dh {(h_vap_shell_out-h_vap_shell_in)/1e3:8.2f} kJ/kg)")
        print(f"        MRliq {q_c_l:8.3f} MW  (dh {(h_liq_shell_out-h_liq_shell_in)/1e3:8.2f} kJ/kg)")
        print(f"        TOTAL {q_cold:8.3f} MW")
        print(f"  CLOSURE  {closure:+8.3f} MW   ({closure_pct:+7.3f} %)")
        print()

    return out


def jt_isenthalpy_check(percentile: int = 50) -> None:
    """Verify that the JT assumption holds in PR-EOS: h(42.22,-152.9) == h(3.073,-151.24)?"""
    row = load_dcs_row(percentile)
    z, _ = mcr_composition(row)
    b = build_basis(z, "JT")
    st_v = NeqSimState(b["z_vap"])
    st_l = NeqSimState(b["z_liq"])

    print("-" * 92)
    print("JT ISENTHALPIC CHECK (PR-EOS) — deviation tells us if JT is really h-conserving")
    print("-" * 92)
    hs = [
        ("vapour", st_v, P_HP_BARA, T_VAP_TO_JT, P_SHELL_BARA, T_VAP_FROM_JT),
        ("liquid", st_l, P_HP_BARA, T_LIQ_TO_JT, P_SHELL_BARA, T_LIQ_FROM_JT),
    ]
    for name, st, p1, t1, p2, t2 in hs:
        h1 = st.h_mass(p1, t1)
        h2 = st.h_mass(p2, t2)
        print(f"  {name:8s} h({p1:.2f} bar,{t1:+7.2f} C) = {h1/1e3:11.3f} kJ/kg")
        print(f"  {name:8s} h({p2:.4f} bar,{t2:+7.2f} C) = {h2/1e3:11.3f} kJ/kg"
              f"   dH = {(h2-h1)/1e3:+9.3f} kJ/kg  ({(h2-h1)/abs(h1)*100:+6.3f} %)")

    # mixing check: 303.51 * h(MCRVfromCB) + 163.54 * h(MCRL_FROM_JT) = 467.06 * h(MIX)?
    st_mix = NeqSimState(b["z_vap"])  # placeholder; mixing needs total comp
    print()
    print("  NOTE: mixing-return check needs the TOTAL MR composition on the mixed")
    print("        stream; the vapour/liquid compositions differ. Computed separately")
    print("        below with the total composition.")
    st_tot = NeqSimState(z)
    h_mix_model = st_tot.h_mass(P_SHELL_BARA, T_MIX_RETURN)
    num = M_VAP * st_v.h_mass(P_SHELL_BARA, T_VAP_CB_OUT) + M_LIQ_WB * st_l.h_mass(P_SHELL_BARA, T_LIQ_FROM_JT)
    h_mix_from_streams = num / (M_VAP + M_LIQ_WB)
    print(f"  h(MIX_WB_RETURN, total comp, {T_MIX_RETURN} C) = {h_mix_model/1e3:11.3f} kJ/kg")
    print(f"  h(mass-weighted from the two returns)          = {h_mix_from_streams/1e3:11.3f} kJ/kg")
    print(f"  difference = {(h_mix_model-h_mix_from_streams)/1e3:+9.3f} kJ/kg"
          f"  ({(h_mix_model-h_mix_from_streams)/abs(h_mix_from_streams)*100:+6.3f} %)")
    print()


def main() -> None:
    rows = [ledger(p) for p in (10, 50, 90)]
    jt_isenthalpy_check(50)

    df = pd.DataFrame(rows)
    out = os.path.join(BASE, "audit", "P4_CLOSURE_LEDGER.csv")
    df.to_csv(out, index=False)
    print(f"[SAVED] {out}")

    print()
    print("=" * 92)
    print("GATE CHECK — |closure_pct| <= 1.0 % of Q_hot (AGENTS.md Rule 5 / Rule 11)")
    print("=" * 92)
    all_pass = True
    for r in rows:
        ok = abs(r["closure_pct"]) <= 1.0
        all_pass &= ok
        print(f"  P{r['percentile']:>3d}  {r['closure_MW']:+8.3f} MW   "
              f"{r['closure_pct']:+7.3f} %   -> {'PASS' if ok else 'FAIL'}")
    print(f"\n  OVERALL: {'PASS' if all_pass else 'FAIL — residual must be attributed physically'}")


if __name__ == "__main__":
    main()
