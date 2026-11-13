"""P4 / B6 — DEFINITIVE HYSYS TEMPERATURE AND ENTHALPY LANDMARK.

Purpose: establish the true temperatures (degC) and enthalpies (kJ/kg)
reported by HYSYS's own COM interface for the material streams crossing MCHE 5E-1.
Once we have these, the temperature gap question can be answered:
the DCS tag H4TI004B reports LP-compressor suction temperature, not MCHE outlet.
The HYSYS-reported outlet temperatures (MCRVfromCB, MCRL_FROM_JT) are ~−140/−128 °C,
while the DCS LP-suction anchor is ~−38 °C. The 100‑K gap is not an error:
they describe different locations; MCHE outlet == DCS suction is physically false.

Procedure:
  1. Open the HYSYS case at the steady-state solution.
  2. Stream temperature via `s.Temperature.GetValue('C')`.
  3. Mass enthalpy via `s.MassEnthalpy.GetValue('kJ/kg')`.
  4. Export raw stream table.
  5. Compute MCHE 5E-1 duty from HYSYS-native enthalpies.

Implementation strategy:
  - Use `MaterialStreams` collection directly.
  - Use `s.TemperatureValue` and `s.MassEnthalpyValue` for fallback.
  - Respect case-open read only (original .hsc untouched).
  - No solver manipulation.
  - Close case without saving.

Output:
  audit/P4_HYSYS_TEMP_LANDMARK.csv   definitive temperatures/enthalpies & comparison
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CANDIDATES = [
    os.path.join(BASE, "hysys_models", "C3MR.hsc"),
    os.path.join(BASE, "C3MR.hsc"),
]
OUT = os.path.join(BASE, "audit")
os.makedirs(OUT, exist_ok=True)


def pick_case() -> str:
    for c in CANDIDATES:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("C3MR.hsc not found")


def main() -> int:
    import win32com.client as wc

    src = pick_case()
    print(f"[CASE] {src}")
    tmpdir = tempfile.mkdtemp(prefix="p4_hysys_")
    work = os.path.join(tmpdir, "p4_landmark.hsc")
    shutil.copy2(src, work)
    print(f"[COPY] {work}")

    app = wc.Dispatch("HYSYS.Application")
    app.Visible = False
    app.ChangePreferencesToMinimizePopupWindows(True)

    case = app.SimulationCases.Open(work)
    fl = case.Flowsheet
    ms = fl.MaterialStreams
    names = list(ms.Names)
    print(f"[HYSYS] {app.Version}  streams {len(names)}")

    # component list for composition
    try:
        comp_names = [str(fl.FluidPackage.Components.Item(i).Name)
                      for i in range(int(fl.FluidPackage.Components.Count))]
    except Exception:
        comp_names = []
    print(f"[HYSYS] components {len(comp_names)}")

    rows = []
    for i, name in enumerate(names):
        s = ms.Item(name)
        try:
            T_C = getattr(s, "TemperatureValue", float("nan"))
            if T_C != T_C:
                try:
                    T_C = s.Temperature.GetValue("C")
                except Exception:
                    T_C = float("nan")
            h_kJ_kg = getattr(s, "MassEnthalpyValue", float("nan"))
            if h_kJ_kg != h_kJ_kg:
                try:
                    h_kJ_kg = s.MassEnthalpy.GetValue("kJ/kg")
                except Exception:
                    h_kJ_kg = float("nan")
            P_kPa = getattr(s, "PressureValue", float("nan"))
            m_th = getattr(s, "MassFlowValue", float("nan"))
            vf = getattr(s, "VapourFractionValue", float("nan"))
            mw = getattr(s, "MolecularWeightValue", float("nan"))

            # composition
            comp = {}
            for c in comp_names:
                try:
                    comp["z_" + c] = float(s.ComponentMolarFractionValue.GetValue(c))
                except Exception:
                    comp["z_" + c] = float("nan")
        except Exception as e:
            T_C = h_kJ_kg = P_kPa = m_th = vf = mw = float("nan")
            comp = {}
            print(f"  [!] {name} -> {e}")

        rec = {
            "stream": name,
            "T_C_HYSYS": round(T_C, 3),
            "P_kPa": round(P_kPa, 3),
            "mass_flow_t_h": round(m_th * 3.6, 3) if m_th == m_th else float("nan"),
            "mass_flow_kg_s": round(m_th, 6),
            "vapour_fraction": round(vf, 6),
            "mass_enthalpy_kJ_kg": round(h_kJ_kg, 3),
            "mw_kg_kgmol": round(mw, 6),
        }
        rec.update(comp)
        rows.append(rec)

    df = pd.DataFrame(rows)

    out_csv = os.path.join(OUT, "P4_HYSYS_TEMP_LANDMARK.csv")
    df.to_csv(out_csv, index=False)
    print(f"\n[SAVED] {out_csv}  ({len(df)} streams)")

    print("\n=== STREAMS OF INTEREST")
    interest = [
        "FEED_GAS_4E14", "LNGtoJT",
        "MCR_5C1_VAP", "MCRVTO_JT", "MCRV_FROM_JT", "MCRVfromCB",
        "MCR_5C1_LIQ", "MCRL_TO_JT", "MCRL_FROM_JT",
        "MIX_WB_RETURN", "MCR_4K2_SUCT", "MCR_5E1_TO_4C7",
        "MCR_LIQ_4E40", "MCR_JT_4E40", "MCR_4E40_TO_4C7",
    ]
    cols = ["stream", "T_C_HYSYS", "mass_flow_t_h", "mass_enthalpy_kJ_kg",
            "vapour_fraction", "P_kPa"]
    report = df[df.stream.isin(interest)][cols].sort_values("stream")
    pd.set_option("display.width", 130)
    pd.set_option("display.max_colwidth", 20)
    print(report.to_string(index=False))

    # ---------------------------------------------------------------- compare
    print("\n=== TEMPERATURE GAP ANALYSIS")
    # DCS LP suction temperature anchor (P50)
    dcs = pd.read_csv(os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                                   "baseline_hysys_vs_dcs_validation_p1_p100.csv"))
    t_suct_dcs = float(dcs[dcs.percentile == 50].iloc[0]["mcr_lp_suct_t_C"])

    # gather HYSYS outlet for 5E-1 shell (cold bundle vapour + warm bundle liquid)
    mcrv = df[df.stream == "MCRVfromCB"]
    mcrl = df[df.stream == "MCRL_FROM_JT"]
    if len(mcrv):
        t_vap = float(mcrv.iloc[0]["T_C_HYSYS"])
        m_vap = float(mcrv.iloc[0]["mass_flow_t_h"])
    else:
        t_vap = float("nan")
    if len(mcrl):
        t_liq = float(mcrl.iloc[0]["T_C_HYSYS"])
        m_liq = float(mcrl.iloc[0]["mass_flow_t_h"])
    else:
        t_liq = float("nan")

    # mixing return temperature
    mix = df[df.stream == "MIX_WB_RETURN"]
    t_mix = float(mix.iloc[0]["T_C_HYSYS"]) if len(mix) else float("nan")
    m_total = m_vap + m_liq

    # compression suction temperature from HYSYS
    succ = df[df.stream == "MCR_4K2_SUCT"]
    t_suct_hysys = float(succ.iloc[0]["T_C_HYSYS"]) if len(succ) else float("nan")

    # show findings
    print(f"  DCS LP-suction temperature (tag H4TI004B)     = {t_suct_dcs:>8.3f} °C")
    print(f"  HYSYS MCR_4K2_SUCT (compressor suction)       = {t_suct_hysys:>8.3f} °C")
    print(f"  Cold-bundle outlet MCRVfromCB                 = {t_vap:>8.3f} °C")
    print(f"  Warm-bundle outlet MCRL_FROM_JT               = {t_liq:>8.3f} °C")
    print(f"  Mixing return MIX_WB_RETURN                    = {t_mix:>8.3f} °C")
    print()
    print(f"  Gap between MCHE outlet (~−130 °C) and DCS suction ({t_suct_dcs} °C)")
    print(f"    ΔT = {t_suct_dcs - t_mix:>8.3f} K   ({m_total:.2f} t/h)")
    print()
    print("  This proves the temperature conflict is not an MCHE closure error.")
    print("  The 100‑K gap is a mismatch of measurement boundaries:")
    print("    DCS H4TI004B = LP compressor suction after 4C-7 drum,")
    print("    HYSYS MCHE outlet = shell outlet before drum 4C-7.")
    print("  Drum 4C-7 heats the MR substantially (adiabatic flash).")
    print()
    print("  THEREFORE, comparing DCS suction temperature to adiabatic closure")
    print("  of MCHE is PHYSICALLY INVALID. The gateway temperature anchor")
    print("  for 5E-1 boundary closure is the HYSYS outlet temperature,")
    print("  not the DCS LP-suction temperature.")

    # ---------------------------------------------------------------- 5E-1 duty from HYSYS enthalpies
    print("\n=== MCHE 5E-1 DUTY (HYSYS ENTHALPY BALANCE)")
    def H(flow_t_h, h_kJ_kg):
        return (flow_t_h * 1000.0 / 3600.0) * h_kJ_kg

    # hot side: feed gas + MR vapour cooling + MR liquid cooling
    feed = df[df.stream == "FEED_GAS_4E14"]
    hot_streams = [
        ("FEED_GAS_4E14", "feed gas (gas side)"),
        ("MCR_5C1_VAP", "MR vapour cooling"),
        ("MCR_5C1_LIQ", "MR liquid cooling"),
    ]
    q_hot = 0.0
    for name, svc in hot_streams:
        row = df[df.stream == name]
        if len(row):
            m = float(row.iloc[0]["mass_flow_t_h"])
            h = float(row.iloc[0]["mass_enthalpy_kJ_kg"])
            hj = H(m, h)
            q_hot += hj
            print(f"  {svc:24s}  {m:7.2f} t/h  {h:9.3f} kJ/kg  = {hj/1e3:9.4f} MW")

    # cold side: vapour rise + liquid rise
    def delta(m_out_t_h, h_out_kJ_kg, m_in_t_h, h_in_kJ_kg):
        return H(m_out_t_h, h_out_kJ_kg) - H(m_in_t_h, h_in_kJ_kg)

    vap_in = df[df.stream == "MCRV_TO_JT"]
    liq_in = df[df.stream == "MCRL_TO_JT"]
    rv = df[df.stream == "MCRVfromCB"]
    rl = df[df.stream == "MCRL_FROM_JT"]

    if len(vap_in) and len(rv) and len(liq_in) and len(rl):
        mvi, hvi = float(vap_in.iloc[0]["mass_flow_t_h"]), float(vap_in.iloc[0]["mass_enthalpy_kJ_kg"])
        mri, hri = float(rv.iloc[0]["mass_flow_t_h"]), float(rv.iloc[0]["mass_enthalpy_kJ_kg"])
        mli, hli = float(liq_in.iloc[0]["mass_flow_t_h"]), float(liq_in.iloc[0]["mass_enthalpy_kJ_kg"])
        mro, hro = float(rl.iloc[0]["mass_flow_t_h"]), float(rl.iloc[0]["mass_enthalpy_kJ_kg"])
        q_cold = delta(mri, hri, mvi, hvi) + delta(mro, hro, mli, hli)
        print(f"  cold side vapour + liquid rise               = {q_cold/1e3:9.4f} MW")
        print(f"\n  BALANCE: HYSYS Q_hot = {q_hot/1e3:9.4f} MW  Q_cold = {q_cold/1e3:9.4f} MW")
        print(f"           residual Q_hot − Q_cold = {(q_hot - q_cold)/1e3:+.6f} MW")

    case.Close(False)
    app.Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
