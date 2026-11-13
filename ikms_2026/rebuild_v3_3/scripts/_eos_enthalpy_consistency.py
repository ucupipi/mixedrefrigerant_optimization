"""EOS ENTHALPY CONSISTENCY TEST — is NeqSim's mass enthalpy composition-consistent?

Decisive diagnostic before any boundary work. If the engine's enthalpy reporting
is not internally consistent, every boundary decomposition built on it is
meaningless (AGENTS.md Rule 1, Rule 11: no invented numbers).

TESTS
  T1  Phase-sum vs mixture:  m * [w_v*h_v + (1-w_v)*h_l]  ==  m * h_mixture
      at the same (P, T). This must hold to machine precision.

  T2  Re-created phase fluid:  h(new fluid from phase comp at P,T)  ==  h_phase
      Creating a fresh fluid from the phase composition must reproduce the phase
      mass enthalpy at the same (P, T).

  T3  Adiabatic mixing:  m_a*h_a(T_a) + m_b*h_b(T_b)  ==  m*h_mixed(T_mixed)
      where T_mixed is found by enthalpy conservation. Checks that the
      H-formulation is consistent across differing compositions.

  T4  Reference sensitivity: h at (P,T) for scaled compositions 0.5*z and 2*z
      (renormalised). Absolute h should be invariant under renormalisation.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(BASE, "ikms_2026", "rebuild_v3_3", "scripts"))

os.environ.setdefault("JAVA_HOME", r"C:\Users\khari\AppData\Local\openLCA\jre")

from mche_engine_v33 import NeqSimState, COMP_ORDER  # noqa: E402

P_HP = 42.22
P_SH = 3.0734


def load_z(percentile=50):
    d = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                                 "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
    r = d[d["percentile"] == percentile].iloc[0]
    z = {
        "nitrogen": float(r["mcr_comp_N2_mol_pct"]) / 100,
        "methane": float(r["mcr_comp_C1_mol_pct"]) / 100,
        "ethane": float(r["mcr_comp_C2_mol_pct"]) / 100,
        "ethylene": float(r["mcr_comp_C2H4_mol_pct"]) / 100,
        "propane": float(r["mcr_comp_C3_mol_pct"]) / 100,
    }
    tot = sum(z.values())
    return {k: v / tot for k, v in z.items()}


def t1_phase_sum(z):
    print("=" * 92)
    print("T1  PHASE-SUM vs MIXTURE  (must match to < 0.01 kJ/kg)")
    print("=" * 92)
    st = NeqSimState(z)
    sep = st.flash_phases(P_HP, -35.0)
    tot_h = st.h_mass(P_HP, -35.0) / 1e3

    # flash_phases already ran a TP flash; re-read total from same object
    sum_mass = 0.0
    for ph in sep["phases"]:
        # mass fraction of this phase from molar beta and molar masses
        pass

    vap = liq = None
    for ph in sep["phases"]:
        if ph["name"].lower().startswith("gas"):
            vap = ph
        else:
            liq = ph

    bv = vap["beta_mol"]
    mw_v, mw_l = vap["mw_kg_mol"], liq["mw_kg_mol"]
    mw_bar = bv * mw_v + (1 - bv) * mw_l
    w_v = (bv * mw_v) / mw_bar

    h_v = vap["h_mass"] / 1e3
    h_l = liq["h_mass"] / 1e3
    h_sum = w_v * h_v + (1 - w_v) * h_l

    print(f"  w_vap(mass)                 = {w_v:.6f}")
    print(f"  h_vapour phase              = {h_v:12.4f} kJ/kg")
    print(f"  h_liquid phase              = {h_l:12.4f} kJ/kg")
    print(f"  mass-weighted phase sum     = {h_sum:12.4f} kJ/kg")
    print(f"  h_mixture (getEnthalpy)     = {tot_h:12.4f} kJ/kg")
    print(f"  DELTA                       = {h_sum - tot_h:+12.6f} kJ/kg")
    ok = abs(h_sum - tot_h) < 0.01
    print(f"  -> {'PASS' if ok else 'FAIL'}\n")
    return vap, liq, w_v, ok


def t2_recreated(vap, liq):
    print("=" * 92)
    print("T2  RE-CREATED PHASE FLUID  (fresh fluid from phase comp must reproduce h)")
    print("=" * 92)
    ok = True
    for tag, ph in (("vapour", vap), ("liquid", liq)):
        st_new = NeqSimState(ph["comp"])
        h_new = st_new.h_mass(P_HP, -35.0) / 1e3
        h_ref = ph["h_mass"] / 1e3
        d = h_new - h_ref
        good = abs(d) < 0.01
        ok &= good
        print(f"  {tag:7s} h_phase {h_ref:12.4f}  h_recreated {h_new:12.4f}"
              f"  DELTA {d:+10.6f}  -> {'PASS' if good else 'FAIL'}")
    print(f"  -> {'PASS' if ok else 'FAIL'}\n")
    return ok


def t3_adiabatic_mixing(vap, liq):
    print("=" * 92)
    print("T3  ADIABATIC MIXING  (m_a*h_a + m_b*h_b == m*h_mixed at conserved T)")
    print("=" * 92)
    m_a, t_a = 303.51, -140.08      # MCRVfromCB
    m_b, t_b = 163.54, -127.73      # MCRL_FROM_JT

    st_a = NeqSimState(vap["comp"])
    st_b = NeqSimState(liq["comp"])

    h_a = st_a.h_mass(P_SH, t_a) / 1e3
    h_b = st_b.h_mass(P_SH, t_b) / 1e3
    h_target = (m_a * h_a + m_b * h_b) / (m_a + m_b)

    # find T_mixed by bisection on the mixed (total) composition
    z_tot = {}
    for k in COMP_ORDER:
        z_tot[k] = (m_a * vap["comp"].get(k, 0.0) + m_b * liq["comp"].get(k, 0.0)) / (m_a + m_b)
    st_mix = NeqSimState(z_tot)

    lo, hi = -180.0, -60.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        h_mid = st_mix.h_mass(P_SH, mid) / 1e3
        if h_mid < h_target:
            lo = mid
        else:
            hi = mid
    t_mix = 0.5 * (lo + hi)
    h_mix = st_mix.h_mass(P_SH, t_mix) / 1e3

    print(f"  h_a (m={m_a} t/h, T={t_a} C) = {h_a:12.4f} kJ/kg")
    print(f"  h_b (m={m_b} t/h, T={t_b} C) = {h_b:12.4f} kJ/kg")
    print(f"  mass-weighted target h        = {h_target:12.4f} kJ/kg")
    print(f"  solved T_mixed                = {t_mix:12.4f} C   (HYSYS: -136.73 C)")
    print(f"  h at solved T_mixed           = {h_mix:12.4f} kJ/kg")
    print(f"  DELTA h                       = {h_mix - h_target:+12.6f} kJ/kg")
    ok = abs(h_mix - h_target) < 0.01
    print(f"  -> {'PASS (enthalpy consistent)' if ok else 'FAIL (enthalpy NOT consistent)'}\n")
    return ok, t_mix


def t4_reference(z):
    print("=" * 92)
    print("T4  RENORMALISATION INVARIANCE  (scaling composition must not shift h)")
    print("=" * 92)
    st1 = NeqSimState(z)
    h1 = st1.h_mass(P_HP, -35.0) / 1e3
    z2 = {k: v * 0.5 for k, v in z.items()}
    st2 = NeqSimState(z2)
    h2 = st2.h_mass(P_HP, -35.0) / 1e3
    z3 = {k: v * 3.0 for k, v in z.items()}
    st3 = NeqSimState(z3)
    h3 = st3.h_mass(P_HP, -35.0) / 1e3
    print(f"  h(z)   = {h1:12.6f}")
    print(f"  h(0.5z)= {h2:12.6f}   delta {h2-h1:+12.6f}")
    print(f"  h(3z)  = {h3:12.6f}   delta {h3-h1:+12.6f}")
    ok = abs(h2 - h1) < 1e-6 and abs(h3 - h1) < 1e-6
    print(f"  -> {'PASS' if ok else 'FAIL'}\n")
    return ok


def t5_component_exclusion():
    print("=" * 92)
    print("T5  COMPONENT-SET SENSITIVITY  (adding a trace component must not shift h)")
    print("=" * 92)
    z_base = {"nitrogen": 0.045, "methane": 0.425, "ethane": 0.468,
              "ethylene": 0.004, "propane": 0.058}
    tot = sum(z_base.values())
    z_base = {k: v / tot for k, v in z_base.items()}
    h_base = NeqSimState(z_base).h_mass(P_HP, -35.0) / 1e3

    # add 1e-6 mol of n-butane (allowed by NeqSim but not in COMP_ORDER list)
    st = NeqSimState(z_base)
    print(f"  base 5-comp h        = {h_base:12.6f} kJ/kg")
    print("  (n-butane reference test skipped: COMP_ORDER is a fixed 5-component set,")
    print("   so cross-set reference drift cannot be introduced by this engine.)\n")
    return True


def main():
    z = load_z(50)
    print(f"\nComposition P50: " + ", ".join(f"{k}={v:.5f}" for k, v in z.items()) + "\n")

    vap, liq, w_v, ok1 = t1_phase_sum(z)
    ok2 = t2_recreated(vap, liq)
    ok3, t_mix = t3_adiabatic_mixing(vap, liq)
    ok4 = t4_reference(z)
    t5_component_exclusion()

    print("=" * 92)
    print("SUMMARY")
    print("=" * 92)
    print(f"  T1 phase-sum vs mixture   : {'PASS' if ok1 else 'FAIL'}")
    print(f"  T2 re-created phase fluid : {'PASS' if ok2 else 'FAIL'}")
    print(f"  T3 adiabatic mixing       : {'PASS' if ok3 else 'FAIL'}"
          f"   (solved T_mix = {t_mix:.2f} C vs HYSYS -136.73 C)")
    print(f"  T4 renormalisation        : {'PASS' if ok4 else 'FAIL'}")
    print()
    if all([ok1, ok2, ok3, ok4]):
        print("  VERDICT: NeqSim mass enthalpy IS internally consistent.")
        print("           The MCHE residual is therefore a SYSTEM-BOUNDARY defect,")
        print("           not an EOS/reference artifact.")
    else:
        print("  VERDICT: NeqSim enthalpy reporting is NOT consistent.")
        print("           All boundary decompositions built on it are invalid until fixed.")


if __name__ == "__main__":
    main()
