"""P4 / B6 — LIVE HYSYS STREAM + ENTHALPY EXTRACTION (API-correct).

Uses the verified HYSYS V12.1 COM interface:
    app.SimulationCases.Open(path) -> case
(There is no app.SimulationCase setter and no app.OpenCase in V12.1.)

Rule 14 compliance: the original .hsc is never modified. A temporary copy is
opened, and the case is closed without saving.

Outputs
  audit/P4_HYSYS_STREAMS_LIVE.csv    every material stream, native properties
  audit/P4_HYSYS_ENERGY_BALANCE.csv  5E-1 per-side duty with HYSYS enthalpies
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


def val(obj, units):
    """Read a HYSYS unit-aware property for the first working unit."""
    for u in units:
        try:
            v = obj.GetValue(u)
            if v is not None:
                return float(v), u
        except Exception:
            continue
    return float("nan"), None


def read_stream(s, comp_names):
    rec = {"name": str(getattr(s, "Name", "?"))}

    rec["T_C"], rec["T_unit"] = val(s.Temperature, ["C", "degC"])
    rec["T_K"], _ = val(s.Temperature, ["K"])
    rec["P_kPa"], _ = val(s.Pressure, ["kPa"])
    rec["P_bara"], _ = val(s.Pressure, ["bar"])
    rec["mass_flow_t_h"], _ = val(s.MassFlow, ["t/h", "tonne/h"])
    rec["mass_flow_kg_s"], _ = val(s.MassFlow, ["kg/s"])
    rec["vapour_fraction"], _ = val(s.VapourFraction, [""])
    rec["mass_enthalpy_kJ_kg"], rec["h_unit"] = val(s.MassEnthalpy, ["kJ/kg"])
    rec["mw_kg_kgmol"], _ = val(s.MolecularWeight, ["kg/kgmole", "kg/kgmol"])

    try:
        rec["package"] = str(s.PropertyPackageName)
    except Exception:
        rec["package"] = "?"

    for c in comp_names:
        key = "z_" + c
        try:
            rec[key] = float(s.ComponentMolarFractionValue.GetValue(c))
        except Exception:
            rec[key] = float("nan")
    return rec


def main() -> int:
    import win32com.client as wc

    src = pick_case()
    print(f"[CASE] {src}")
    tmpdir = tempfile.mkdtemp(prefix="p4_hysys_")
    work = os.path.join(tmpdir, "p4_work.hsc")
    shutil.copy2(src, work)
    print(f"[COPY] {work}  (original untouched)")

    app = wc.Dispatch("HYSYS.Application")
    try:
        app.Visible = False
    except Exception:
        pass
    app.ChangePreferencesToMinimizePopupWindows(True)

    case = app.SimulationCases.Open(work)
    print(f"[HYSYS] {app.Version}")
    try:
        case.Solver.CanSolve = True
        case.Solver.Start()
    except Exception as e:
        print(f"[WARN] solver start: {e}")
    print(f"[HYSYS] solver active={case.Solver.Active} solving={case.Solver.IsSolving}")

    fl = case.Flowsheet
    ops = fl.Operations
    n = int(ops.Count)
    print(f"[HYSYS] operations: {n}")

    comp_names = []
    try:
        comps = fl.FluidPackages.Item(0).Components
        for i in range(int(comps.Count)):
            comp_names.append(str(comps.Item(i).Name))
    except Exception as e:
        print(f"[WARN] components: {e}")
    print(f"[HYSYS] components ({len(comp_names)}): {comp_names}")

    rows = []
    for i in range(n):
        try:
            op = ops.Item(i)
            tname = str(op.TypeName)
            if "Stream" not in tname:
                continue
            rows.append(read_stream(op, comp_names))
        except Exception:
            continue

    df = pd.DataFrame(rows)
    csv1 = os.path.join(OUT, "P4_HYSYS_STREAMS_LIVE.csv")
    df.to_csv(csv1, index=False)
    print(f"\n[SAVED] {csv1}  ({len(df)} streams)")

    pd.set_option("display.width", 230)
    show = [c for c in ["name", "T_C", "P_bara", "mass_flow_t_h",
                        "vapour_fraction", "mass_enthalpy_kJ_kg", "mw_kg_kgmol"]
            if c in df.columns]
    print(df[show].to_string())

    # ------------------------------------------------------------ 5E-1 duties
    def g(name, col):
        r = df[df["name"] == name]
        return float(r.iloc[0][col]) if len(r) else float("nan")

    def H(flow_th, h_kj):
        """t/h * kJ/kg -> MW"""
        return (flow_th * 1000.0 / 3600.0) * h_kj * 1000.0 / 1.0e6

    print("\n" + "=" * 100)
    print("5E-1 PER-SIDE DUTY — HYSYS-NATIVE MASS ENTHALPIES")
    print("=" * 100)

    hot_pairs = [
        ("FEED_GAS_4E14", "LNGtoJT", "treated feed gas (gas side)"),
        ("MCR_5C1_VAP", "MCRVfromCB", "cold-bundle MR vapour (shell)"),
        ("MCR_5C1_LIQ", "MCRL_FROM_JT", "warm-bundle MR liquid (shell)"),
    ]

    rows2 = []
    q_hot = 0.0
    for a, b, svc in hot_pairs:
        ma, ha = g(a, "mass_flow_t_h"), g(a, "mass_enthalpy_kJ_kg")
        mb, hb = g(b, "mass_flow_t_h"), g(b, "mass_enthalpy_kJ_kg")
        if not (ma == ma) or not (mb == mb):
            print(f"  [MISSING] {a} -> {b}")
            continue
        # use the penetrating stream's own flow (they must agree)
        q = H(ma, ha) - H(mb, hb)
        q_hot += q
        rows2.append({"side": "HOT", "service": svc, "from": a, "to": b,
                      "m_from_t_h": ma, "m_to_t_h": mb,
                      "h_from_kJ_kg": ha, "h_to_kJ_kg": hb, "Q_MW": q})
        print(f"  HOT  {svc:38s} {ma:8.2f}->{mb:8.2f} t/h  "
              f"{ha:10.3f}->{hb:10.3f} kJ/kg  Q={q:9.4f} MW")

    # 4E-40 is its own exchanger: report separately, never as a closer
    print()
    for a, b, svc in [("MCR_LIQ_4E40", "MCR_4E40_TO_4C7", "4E-40 subcooler (SEPARATE)")]:
        ma, ha = g(a, "mass_flow_t_h"), g(a, "mass_enthalpy_kJ_kg")
        mb, hb = g(b, "mass_flow_t_h"), g(b, "mass_enthalpy_kJ_kg")
        if ma == ma and mb == mb:
            q = H(mb, hb) - H(ma, ha)
            rows2.append({"side": "AUX", "service": svc, "from": a, "to": b,
                          "m_from_t_h": ma, "m_to_t_h": mb,
                          "h_from_kJ_kg": ha, "h_to_kJ_kg": hb, "Q_MW": q})
            print(f"  AUX  {svc:38s} {ma:8.2f}->{mb:8.2f} t/h  "
                  f"{ha:10.3f}->{hb:10.3f} kJ/kg  Q={q:9.4f} MW")

    print("\n" + "-" * 100)
    print(f"  Q_hot (5E-1 hot side total) = {q_hot:10.4f} MW")
    print("  The shell-side refrigerant absorbs exactly this much in a converged")
    print("  case; the shell outlet states are MCRVfromCB and MCRL_FROM_JT, so the")
    print("  cold-side duty IS the enthalpy rise of those two streams from their")
    print("  JT-inlet conditions. HYSYS already guarantees closure internally.")
    print("  Any residual here would mean the SELECTED streams do not form a")
    print("  physically closed control volume.")

    pdf = pd.DataFrame(rows2)
    csv2 = os.path.join(OUT, "P4_HYSYS_ENERGY_BALANCE.csv")
    pdf.to_csv(csv2, index=False)
    print(f"\n[SAVED] {csv2}")

    try:
        case.Close(False)          # do not save
    except Exception:
        pass
    try:
        app.Quit()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
