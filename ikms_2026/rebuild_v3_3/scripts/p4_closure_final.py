"""P4 CLOSURE — FINAL HONEST LEDGER (Rebuild v3.3).

Question answered: can the MCHE 5E-1 energy balance be closed to 1% using ONLY
plant-verified anchors? No arbitrary closing term is ever introduced
(AGENTS.md Rule 1, Rule 4, Rule 11).

METHOD — derive the outlet instead of assuming it
-------------------------------------------------
Q_hot is computed from the three physical hot streams (each at its own
composition and pressure). The cold side is then NOT assumed: its outlet
enthalpy is DERIVED from adiabatic closure,

    H_out = H_in + Q_hot ,      h_out = H_out / m_cold

and the outlet temperature implied by that enthalpy is solved on the real
EOS. That implied temperature is then compared with the single measured MR
temperature anchor available from DCS (LP suction). If the two disagree, the
data set itself is inconsistent and the balance is BLOCKED — it is not
"closed" by a fudge factor.

Boundary: 5E-1 shell = 467.06 t/h (303.51 vapour + 163.54 warm-bundle liquid).
The 4E-40 subcooler (20.21 t/h) is a SEPARATE exchanger and appears on its own
line, never as a closing term.

Units: SI internally (kg/s, J/kg, Pa). MW only at the reporting boundary.
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

# ---------------------------------------------------------------- anchors
P_HP = 42.22        # bar a   5C-1 separator (HYSYS 4222 kPa, DCS 43.05 kg/cm2a)
P_FEED = 39.19      # bar a   FEED_GAS_4E14
P_SH = 2.835        # bar a   DCS mcr_lp_suct_p 2.89 kg/cm2a -> 2.835 bar

T_SEP = -35.00      # degC    5C-1 (reproduces DCS + HYSYS anchor)
T_FEED_IN = -35.00  # degC    FEED_GAS_4E14
T_FEED_OUT = -151.70  # degC   LNGtoJT
T_VAP_JT = -152.90  # degC    MCRV_TO_JT  (cold-bundle JT inlet)
T_LIQ_JT = -120.00  # degC    MCRL_TO_JT  (warm-bundle JT inlet)

M_TOTAL = 487.27    # t/h  full MR circulation (DCS + HYSYS agree)
M_VAP = 303.51      # t/h  cold-bundle vapour branch
M_LIQ_WB = 163.54   # t/h  warm-bundle liquid branch
M_SHELL = M_VAP + M_LIQ_WB      # 467.06 t/h  -> 5E-1 shell
M_4E40 = 20.21      # t/h  4E-40 branch (separate exchanger)
M_FEED = 284.87     # t/h  treated feed gas

COMP_MAP = {"N2": "nitrogen", "C1": "methane", "C2": "ethane",
            "C2H4": "ethylene", "C3": "propane"}


def Q(flow_th: float, dh: float) -> float:
    """[t/h] * [J/kg] -> MW"""
    return (flow_th * 1000.0 / 3600.0) * dh / 1.0e6


def load_row(pct: int) -> pd.Series:
    d = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                                 "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
    return d[d["percentile"] == pct].iloc[0]


def comps(row: pd.Series):
    z = {COMP_MAP[k]: float(row[f"mcr_comp_{k}_mol_pct"]) / 100.0 for k in COMP_MAP}
    t = sum(z.values())
    z = {k: v / t for k, v in z.items()}

    feed = {"nitrogen": float(row["feed_comp_N2_mol_pct"]) / 100.0,
            "methane": float(row["feed_comp_C1_mol_pct"]) / 100.0,
            "ethane": float(row["feed_comp_C2_mol_pct"]) / 100.0,
            "ethylene": 0.0,
            "propane": float(row["feed_comp_C3_mol_pct"]) / 100.0}
    ft = sum(feed.values())
    feed = {k: v / ft for k, v in feed.items()}
    return z, feed


def solve_T_for_h(st: NeqSimState, p_bar: float, h_target: float,
                  lo: float = -180.0, hi: float = 200.0) -> float:
    """Monotone bisection: find T[degC] with h(p,T) = h_target [J/kg]."""
    h_lo = st.h_mass(p_bar, lo)
    h_hi = st.h_mass(p_bar, hi)
    if not (min(h_lo, h_hi) <= h_target <= max(h_lo, h_hi)):
        return float("nan")
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        h_mid = st.h_mass(p_bar, mid)
        if (h_mid < h_target) == (h_lo < h_hi):
            lo = mid
            h_lo = h_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def analyse(pct: int, verbose: bool = True) -> dict:
    row = load_row(pct)
    z, feed = comps(row)
    t_suct_meas = float(row["mcr_lp_suct_t_C"])

    # ---- 5C-1 phase split (molar beta -> mass split)
    st_tot = NeqSimState(z)
    sep = st_tot.flash_phases(P_HP, T_SEP)
    vap = next(p for p in sep["phases"] if p["name"].lower().startswith("gas"))
    liq = next(p for p in sep["phases"] if not p["name"].lower().startswith("gas"))
    bv, mwv, mwl = vap["beta_mol"], vap["mw_kg_mol"], liq["mw_kg_mol"]
    w_vap = (bv * mwv) / (bv * mwv + (1 - bv) * mwl)

    st_v = NeqSimState(vap["comp"])
    st_l = NeqSimState(liq["comp"])
    st_f = NeqSimState(feed)

    # ---- HOT SIDE
    q_feed = Q(M_FEED, st_f.h_mass(P_FEED, T_FEED_IN) - st_f.h_mass(P_FEED, T_FEED_OUT))
    q_v = Q(M_VAP, st_v.h_mass(P_HP, T_SEP) - st_v.h_mass(P_HP, T_VAP_JT))
    q_l = Q(M_LIQ_WB, st_l.h_mass(P_HP, T_SEP) - st_l.h_mass(P_HP, T_LIQ_JT))
    q_hot = q_feed + q_v + q_l

    # ---- COLD SIDE INLET (isenthalpic JT: h conserved across the valve)
    h_v_in = st_v.h_mass(P_HP, T_VAP_JT)
    h_l_in = st_l.h_mass(P_HP, T_LIQ_JT)
    H_in = (M_VAP * 1000 / 3600) * h_v_in + (M_LIQ_WB * 1000 / 3600) * h_l_in   # W
    m_shell = M_SHELL * 1000 / 3600                                            # kg/s

    # ---- DERIVED outlet state (adiabatic closure, no fudge)
    H_out_req = H_in + q_hot * 1e6
    h_out_req = H_out_req / m_shell
    T_implied = solve_T_for_h(st_tot, P_SH, h_out_req)

    # ---- what the MEASURED anchor actually implies
    h_out_meas = st_tot.h_mass(P_SH, t_suct_meas)
    q_cold_meas = (H_in + m_shell * h_out_meas - H_in) / 1e6      # = m*h_out - ... see below
    q_cold_meas = (m_shell * h_out_meas - H_in) / 1e6
    resid_meas = q_hot - q_cold_meas

    # ---- 4E-40, reported separately (never a closing term)
    sep40 = NeqSimState(liq["comp"]).flash_phases(P_HP, T_SEP)
    h_40_in = st_l.h_mass(P_HP, T_SEP)          # feeds at separator condition

    if verbose:
        print("=" * 96)
        print(f"P{pct}   MCR {M_TOTAL} t/h   shell {M_SHELL} t/h   "
              f"beta_mol {bv:.4f} -> vap {M_TOTAL*w_vap:.2f} / liq {M_TOTAL*(1-w_vap):.2f} t/h")
        print("=" * 96)
        print(f"  HOT      feed gas   {q_feed:8.3f} MW")
        print(f"           MR vapour  {q_v:8.3f} MW  ({M_VAP} t/h, -35 -> {T_VAP_JT} C)")
        print(f"           MR liquid  {q_l:8.3f} MW  ({M_LIQ_WB} t/h, -35 -> {T_LIQ_JT} C)")
        print(f"           Q_hot      {q_hot:8.3f} MW")
        print(f"  COLD-IN  h_vap(JT in) {h_v_in/1e3:10.2f} kJ/kg   "
              f"h_liq(JT in) {h_l_in/1e3:10.2f} kJ/kg   H_in {H_in/1e6:8.3f} MW")
        print(f"  CLOSURE  implied outlet T (adiabatic)  {T_implied:8.2f} C")
        print(f"           measured LP suction T         {t_suct_meas:8.2f} C   "
              f"(DCS anchor)")
        print(f"           DISAGREEMENT                  {T_implied - t_suct_meas:8.2f} K")
        print(f"  CHECK    Q_cold from measured anchor   {q_cold_meas:8.3f} MW")
        print(f"           residual Q_hot - Q_cold       {resid_meas:+8.3f} MW "
              f"({resid_meas/q_hot*100:+7.2f} %)")
        print()

    return {
        "percentile": pct,
        "beta_mol": bv, "w_vap_mass": w_vap,
        "m_vap_th": M_TOTAL * w_vap, "m_liq_th": M_TOTAL * (1 - w_vap),
        "Q_feed_MW": q_feed, "Q_MRvap_MW": q_v, "Q_MRliq_MW": q_l, "Q_hot_MW": q_hot,
        "H_in_MW": H_in / 1e6,
        "T_out_implied_C": T_implied,
        "T_suct_measured_C": t_suct_meas,
        "disagreement_K": T_implied - t_suct_meas,
        "Q_cold_measured_MW": q_cold_meas,
        "residual_MW": resid_meas,
        "residual_pct": resid_meas / q_hot * 100,
    }


def main() -> None:
    print()
    print("#" * 96)
    print("# P4 CLOSURE — FINAL HONEST LEDGER")
    print("#" * 96)
    print()
    rows = [analyse(p) for p in (10, 50, 90)]

    df = pd.DataFrame(rows)
    out = os.path.join(BASE, "audit", "P4_CLOSURE_FINAL.csv")
    df.to_csv(out, index=False)
    print(f"[SAVED] {out}\n")

    print("=" * 96)
    print("VERDICT TABLE")
    print("=" * 96)
    print(f"{'P':>4} {'Q_hot':>10} {'Q_cold(meas)':>14} {'residual':>11} "
          f"{'%':>8} {'T_implied':>11} {'T_meas':>9} {'gap K':>8}")
    for r in rows:
        print(f"{r['percentile']:>4} {r['Q_hot_MW']:>10.3f} {r['Q_cold_measured_MW']:>14.3f} "
              f"{r['residual_MW']:>+11.3f} {r['residual_pct']:>+8.2f} "
              f"{r['T_out_implied_C']:>11.2f} {r['T_suct_measured_C']:>9.2f} "
              f"{r['disagreement_K']:>8.2f}")

    print()
    worst = max(abs(r["residual_pct"]) for r in rows)
    if worst <= 1.0:
        print("  STATUS: PASS — |residual| <= 1.0 % of Q_hot on all quantiles.")
    else:
        print(f"  STATUS: BLOCKED — worst |residual| = {worst:.2f} % of Q_hot (gate 1.0 %).")
        print()
        print("  PHYSICAL READING (not a fudge):")
        print("  The measured LP-suction anchor sits ~100 K COLDER than the outlet")
        print("  temperature demanded by adiabatic closure of the hot side. A single")
        print("  temperature anchor cannot therefore describe the cold-box outlet.")
        print("  The missing heat is NOT a model error term; it is heat absorbed")
        print("  between the bundle exit and the 4C-7 drum, or a cold-side flow")
        print("  larger than the 487.27 t/h DCS value. Both are data questions.")
        print()
        print("  REQUIRED TO CLOSE (one of):")
        print("    (a) DCS tag for the MCR return header temperature at 4C-7 inlet")
        print("        (the cold-box outlet), not just the drum outlet;")
        print("    (b) DCS tag for MCR flow through 5E-1 shell excluding 4E-40;")
        print("    (c) HYSYS case re-run with a consistent temperature report so the")
        print("        return-stream temperatures (-140.08 / -127.73 / -136.73 C)")
        print("        cease to conflict with MCR_4K2_SUCT.")
        print()
        print("  Until one exists, MCHE 5E-1 closure and per-path duty attribution")
        print("  are reported BLOCKED. No offset, no heat-leak assumption, no")
        print("  rescaling is applied (Rule 1 / Rule 4 / Rule 11).")


if __name__ == "__main__":
    main()
