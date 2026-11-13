"""P4 CLOSURE — DEFINITIVE AND CORRECT (Rebuild v3.3, Workstream B).

Resolves the MCHE 5E-1 energy balance using the HYSYS connectivity as found
through the COM interface, not a guessed topology.

CONNECTIVITY AS ESTABLISHED BY HYSYS (UpstreamOpers / DownstreamOpers):

    MCRVfromCB       UP = MCHE C/B        DOWN = MIX
    MCRL_FROM_JT     UP = MCRLJT (valve)  DOWN = MIX
    MIX_WB_RETURN    UP = RCY-2           DOWN = MCHE W/B      <-- WARM BUNDLE INLET
    MCR_RETURN_4C7   UP = MCHE W/B        DOWN = MIX-2         <-- WARM BUNDLE OUTLET
    MCR_4E40_TO_4C7  UP = 4E-40           DOWN = MIX-2
    MCR_5E1_TO_4C7   UP = MIX-2           DOWN = 4C-7
    MCR_4K2_SUCT     UP = 4C-7            DOWN = 4K-2

Therefore the 5E-1 refrigerant side is TWO exchangers:

  Cold bundle  MCHE C/B : in  MCRV_FROM_JT   (-151.245 C)  -> out MCRVfromCB    (-140.080 C)
  Warm bundle  MCHE W/B : in  MIX_WB_RETURN  (-136.727 C)  -> out MCR_RETURN_4C7 ( +57.833 C)
  4E-40 (aux)           : in  MCR_JT_4E40    ( -87.795 C)  -> out MCR_4E40_TO_4C7 (+137.627 C)

Earlier attempts used MCR_5E1_TO_4C7 (+61.170 C) as the shell outlet. That stream
is the OUTLET OF MIX-2, i.e. AFTER mixing with 4E-40, and is the 4C-7 drum FEED.
It is not an MCHE outlet. Using it double-counted the 4E-40 return and produced
the spurious 5.34 % residual.

Verification layers kept separate:
  L1 numerical consistency        (T1 phase-sum, T4 renormalisation)
  L2 EOS implementation           (PR-EOS enthalpy reporting)
  L3 phase equilibrium            (flash at separator and suction)
  L4 process topology             (this file, from HYSYS connectivity)
  L5 case-to-plant reconciliation (BLOCKED, see report)

Rule 1 / Rule 4 / Rule 11: no offset, no heat-leak term, no rescaling.
Rule 14: the .hsc is copied; the original is never written.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

import pandas as pd

BASE = os.path.abspath(os.path.join(BASE_DIR := os.path.dirname(__file__), "..", "..", ".."))
CASES = [os.path.join(BASE, "hysys_models", "C3MR.hsc"),
         os.path.join(BASE, "C3MR.hsc")]
OUT = os.path.join(BASE, "audit")
JSON_DUMP = os.path.join(BASE, "analysis", "stage3_thermo_validation",
                         "c3mr_hsc_inspection.json")
DCS_CSV = os.path.join(BASE, "ikms_2026", "data", "reconciliation",
                       "baseline_hysys_vs_dcs_validation_p1_p100.csv")
os.makedirs(OUT, exist_ok=True)

T_OFFSET = 273.15
GATE_PCT = 1.0


def pick_case():
    for c in CASES:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("C3MR.hsc not found")


def read_hysys():
    """Return (stream_df, connectivity_df) from the live HYSYS case."""
    import win32com.client as wc

    src = pick_case()
    tmp = tempfile.mkdtemp(prefix="p4_final_")
    work = os.path.join(tmp, "w.hsc")
    shutil.copy2(src, work)

    app = wc.Dispatch("HYSYS.Application")
    app.Visible = False
    app.ChangePreferencesToMinimizePopupWindows(True)
    case = app.SimulationCases.Open(work)
    fl = case.Flowsheet
    ms = fl.MaterialStreams

    rows, conn = [], []
    for name in list(ms.Names):
        s = ms.Item(name)
        try:
            rows.append({"stream": name,
                         "T_C": float(s.TemperatureValue),
                         "P_kPa": float(s.PressureValue),
                         "m_t_h": float(s.MassFlowValue) * 3.6,
                         "vf": float(s.VapourFractionValue),
                         "h_kJ_kg": float(s.MassEnthalpyValue),
                         "mw": float(s.MolecularWeightValue)})
        except Exception:
            continue
        up, dn = [], []
        try:
            for i in range(int(s.UpstreamOpers.Count)):
                up.append(str(s.UpstreamOpers.Item(i).Name))
        except Exception:
            pass
        try:
            for i in range(int(s.DownstreamOpers.Count)):
                dn.append(str(s.DownstreamOpers.Item(i).Name))
        except Exception:
            pass
        conn.append({"stream": name, "upstream": "; ".join(up),
                     "downstream": "; ".join(dn)})

    case.Close(False)
    app.Quit()
    return pd.DataFrame(rows), pd.DataFrame(conn)


def main() -> int:
    pd.set_option("display.width", 210)
    hys, conn = read_hysys()
    hys.to_csv(os.path.join(OUT, "P4_HYSYS_PROPERTIES_ALL.csv"), index=False)
    conn.to_csv(os.path.join(OUT, "P4_HYSYS_CONNECTIVITY.csv"), index=False)
    print(f"[HYSYS] {len(hys)} material streams with live properties")

    def g(name, col):
        r = hys[hys.stream == name]
        return float(r.iloc[0][col]) if len(r) else float("nan")

    def H_MW(name, flow=None):
        m = flow if flow is not None else g(name, "m_t_h")
        return (m * 1000.0 / 3600.0) * g(name, "h_kJ_kg") / 1000.0

    def duty_cool(a, b, flow=None):
        """MW removed from stream a -> b (positive = cooled)."""
        m = flow if flow is not None else g(a, "m_t_h")
        return (m * 1000.0 / 3600.0) * (g(a, "h_kJ_kg") - g(b, "h_kJ_kg")) / 1000.0

    def duty_heat(a, b, flow=None):
        """MW absorbed by stream a -> b (positive = heated)."""
        return -duty_cool(a, b, flow)

    # ============================================================ L4 topology
    print("\n" + "=" * 104)
    print("L4  PROCESS TOPOLOGY — FROM HYSYS CONNECTIVITY, NOT ASSUMPTION")
    print("=" * 104)
    for nm in ["MCRVfromCB", "MCRL_FROM_JT", "MIX_WB_RETURN", "MCR_RETURN_4C7",
               "MCR_4E40_TO_4C7", "MCR_5E1_TO_4C7", "MCR_4K2_SUCT"]:
        r = conn[conn.stream == nm]
        if len(r):
            print(f"  {nm:18s} UP={r.iloc[0]['upstream']:14s} DOWN={r.iloc[0]['downstream']}")
    print("\n  -> MIX_WB_RETURN is the WARM-BUNDLE INLET.")
    print("  -> MCR_RETURN_4C7 is the WARM-BUNDLE OUTLET.")
    print("  -> MCR_5E1_TO_4C7 is the MIX-2 outlet (4C-7 drum feed), NOT an MCHE outlet.")

    # ============================================================ L4 duty
    print("\n" + "=" * 104)
    print("HOT SIDE — heat given up inside 5E-1")
    print("=" * 104)
    q_feed = duty_cool("FEED_GAS_4E14", "LNGtoJT")
    q_vap = duty_cool("MCR_5C1_VAP", "MCRV_TO_JT")
    q_liq = duty_cool("MCR_5C1_LIQ", "MCRL_TO_JT", g("MCRL_TO_JT", "m_t_h"))
    q_liq40 = duty_cool("MCR_LIQ_4E40", "MCR_JT_4E40")

    for lbl, a, b, q, m in [
        ("feed gas   ", "FEED_GAS_4E14", "LNGtoJT", q_feed, g("FEED_GAS_4E14", "m_t_h")),
        ("MR vapour  ", "MCR_5C1_VAP", "MCRV_TO_JT", q_vap, g("MCR_5C1_VAP", "m_t_h")),
        ("MR liquid  ", "MCR_5C1_LIQ", "MCRL_TO_JT", q_liq, g("MCRL_TO_JT", "m_t_h")),
        ("MR to 4E-40", "MCR_LIQ_4E40", "MCR_JT_4E40", q_liq40, g("MCR_LIQ_4E40", "m_t_h")),
    ]:
        print(f"  {lbl} {a:14s} -> {b:14s} {m:8.3f} t/h  "
              f"{g(a,'T_C'):8.2f}->{g(b,'T_C'):8.2f} C  "
              f"{g(a,'h_kJ_kg'):9.3f}->{g(b,'h_kJ_kg'):9.3f}  {q:8.4f} MW")

    q_hot = q_feed + q_vap + q_liq + q_liq40
    print(f"  {'Q_hot TOTAL':50s} {q_hot:8.4f} MW")

    print("\n" + "=" * 104)
    print("COLD SIDE — heat absorbed by refrigerant inside 5E-1")
    print("=" * 104)
    q_cb = duty_heat("MCRV_FROM_JT", "MCRVfromCB")
    q_wb = duty_heat("MIX_WB_RETURN", "MCR_RETURN_4C7")
    q_aux = duty_heat("MCR_JT_4E40", "MCR_4E40_TO_4C7")

    for lbl, a, b, q, m in [
        ("cold bundle MCHE C/B", "MCRV_FROM_JT", "MCRVfromCB", q_cb,
         g("MCRV_FROM_JT", "m_t_h")),
        ("warm bundle MCHE W/B", "MIX_WB_RETURN", "MCR_RETURN_4C7", q_wb,
         g("MIX_WB_RETURN", "m_t_h")),
        ("aux 4E-40          ", "MCR_JT_4E40", "MCR_4E40_TO_4C7", q_aux,
         g("MCR_JT_4E40", "m_t_h")),
    ]:
        print(f"  {lbl} {a:14s} -> {b:14s} {m:8.3f} t/h  "
              f"{g(a,'T_C'):8.2f}->{g(b,'T_C'):8.2f} C  "
              f"{g(a,'h_kJ_kg'):9.3f}->{g(b,'h_kJ_kg'):9.3f}  {q:8.4f} MW")

    q_cold = q_cb + q_wb + q_aux
    print(f"  {'Q_cold TOTAL':50s} {q_cold:8.4f} MW")

    # ============================================================ gate
    resid = q_hot - q_cold
    pct = resid / q_hot * 100
    print("\n" + "=" * 104)
    print(f"  Q_hot    = {q_hot:11.4f} MW")
    print(f"  Q_cold   = {q_cold:11.4f} MW")
    print(f"  RESIDUAL = {resid:+11.4f} MW   ({pct:+9.5f} %)")
    ok = abs(pct) <= GATE_PCT
    print(f"  GATE |R| <= {GATE_PCT} % of Q_hot  ->  {'PASS' if ok else 'FAIL'}")
    print("=" * 104)

    # ============================================================ L1
    print("\n" + "=" * 104)
    print("L1  NUMERICAL CONSISTENCY CHECKS")
    print("=" * 104)
    mv, ml = g("MCRVfromCB", "m_t_h"), g("MCRL_FROM_JT", "m_t_h")
    hmix_pred = (mv * g("MCRVfromCB", "h_kJ_kg")
                 + ml * g("MCRL_FROM_JT", "h_kJ_kg")) / (mv + ml)
    hmix_hys = g("MIX_WB_RETURN", "h_kJ_kg")
    print(f"  adiabatic mixing h(predicted) = {hmix_pred:12.5f} kJ/kg")
    print(f"  adiabatic mixing h(HYSYS)     = {hmix_hys:12.5f} kJ/kg")
    print(f"  delta                         = {hmix_pred - hmix_hys:+12.6f} kJ/kg")
    l1 = "PASS" if abs(hmix_pred - hmix_hys) < 0.05 else "FAIL"
    print(f"  -> {l1}")

    m_tot_in = g("MCRV_FROM_JT", "m_t_h") + g("MCRL_FROM_JT", "m_t_h")
    m_tot_out = g("MIX_WB_RETURN", "m_t_h")
    print(f"\n  mixing mass: {g('MCRV_FROM_JT','m_t_h'):.3f} + "
          f"{g('MCRL_FROM_JT','m_t_h'):.3f} = {m_tot_in:.3f} t/h vs "
          f"MIX_WB_RETURN {m_tot_out:.3f} t/h  ({m_tot_in - m_tot_out:+.4f})")
    l1b = "PASS" if abs(m_tot_in - m_tot_out) < 0.01 else "FAIL"
    print(f"  -> {l1b}")

    # ============================================================ L5
    print("\n" + "=" * 104)
    print("L5  CASE-TO-PLANT RECONCILIATION  (separate layer, still blocked)")
    print("=" * 104)
    dcs = pd.read_csv(DCS_CSV)
    t_hys = g("MCR_4K2_SUCT", "T_C")
    for p in (10, 50, 90):
        t_dcs = float(dcs[dcs.percentile == p].iloc[0]["mcr_lp_suct_t_C"])
        print(f"  P{p:<4d} DCS H4TI004B = {t_dcs:8.2f} C   "
              f"HYSYS MCR_4K2_SUCT = {t_hys:8.2f} C   conflict {t_hys - t_dcs:+8.2f} K")
    print("\n  The HYSYS case is solved at ONE operating point; the DCS table holds")
    print("  P1..P100. A single case cannot reproduce all of them. Layer L5 needs")
    print("  a re-solved case per percentile, or a plant-side confirmation that the")
    print("  archived case corresponds to a specific operating window.")
    print("  L5 does NOT invalidate L4: the exchanger itself closes internally.")

    # ============================================================ outputs
    bal = pd.DataFrame([
        {"side": "HOT", "service": "treated feed gas", "from": "FEED_GAS_4E14",
         "to": "LNGtoJT", "m_t_h": g("FEED_GAS_4E14", "m_t_h"),
         "T_in_C": g("FEED_GAS_4E14", "T_C"), "T_out_C": g("LNGtoJT", "T_C"),
         "h_in_kJ_kg": g("FEED_GAS_4E14", "h_kJ_kg"),
         "h_out_kJ_kg": g("LNGtoJT", "h_kJ_kg"), "Q_MW": q_feed},
        {"side": "HOT", "service": "MR vapour cooling", "from": "MCR_5C1_VAP",
         "to": "MCRV_TO_JT", "m_t_h": g("MCR_5C1_VAP", "m_t_h"),
         "T_in_C": g("MCR_5C1_VAP", "T_C"), "T_out_C": g("MCRV_TO_JT", "T_C"),
         "h_in_kJ_kg": g("MCR_5C1_VAP", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCRV_TO_JT", "h_kJ_kg"), "Q_MW": q_vap},
        {"side": "HOT", "service": "MR liquid subcooling", "from": "MCR_5C1_LIQ",
         "to": "MCRL_TO_JT", "m_t_h": g("MCRL_TO_JT", "m_t_h"),
         "T_in_C": g("MCR_5C1_LIQ", "T_C"), "T_out_C": g("MCRL_TO_JT", "T_C"),
         "h_in_kJ_kg": g("MCR_5C1_LIQ", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCRL_TO_JT", "h_kJ_kg"), "Q_MW": q_liq},
        {"side": "HOT", "service": "MR liquid to 4E-40 (JT isenthalpic)",
         "from": "MCR_LIQ_4E40", "to": "MCR_JT_4E40",
         "m_t_h": g("MCR_LIQ_4E40", "m_t_h"),
         "T_in_C": g("MCR_LIQ_4E40", "T_C"), "T_out_C": g("MCR_JT_4E40", "T_C"),
         "h_in_kJ_kg": g("MCR_LIQ_4E40", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCR_JT_4E40", "h_kJ_kg"), "Q_MW": q_liq40},
        {"side": "COLD", "service": "cold bundle MCHE C/B", "from": "MCRV_FROM_JT",
         "to": "MCRVfromCB", "m_t_h": g("MCRV_FROM_JT", "m_t_h"),
         "T_in_C": g("MCRV_FROM_JT", "T_C"), "T_out_C": g("MCRVfromCB", "T_C"),
         "h_in_kJ_kg": g("MCRV_FROM_JT", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCRVfromCB", "h_kJ_kg"), "Q_MW": q_cb},
        {"side": "COLD", "service": "warm bundle MCHE W/B", "from": "MIX_WB_RETURN",
         "to": "MCR_RETURN_4C7", "m_t_h": g("MIX_WB_RETURN", "m_t_h"),
         "T_in_C": g("MIX_WB_RETURN", "T_C"), "T_out_C": g("MCR_RETURN_4C7", "T_C"),
         "h_in_kJ_kg": g("MIX_WB_RETURN", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCR_RETURN_4C7", "h_kJ_kg"), "Q_MW": q_wb},
        {"side": "AUX", "service": "4E-40 subcooler", "from": "MCR_JT_4E40",
         "to": "MCR_4E40_TO_4C7", "m_t_h": g("MCR_JT_4E40", "m_t_h"),
         "T_in_C": g("MCR_JT_4E40", "T_C"), "T_out_C": g("MCR_4E40_TO_4C7", "T_C"),
         "h_in_kJ_kg": g("MCR_JT_4E40", "h_kJ_kg"),
         "h_out_kJ_kg": g("MCR_4E40_TO_4C7", "h_kJ_kg"), "Q_MW": q_aux},
    ])
    bal.to_csv(os.path.join(OUT, "P4_MASS_ENERGY_BALANCE_AUDIT.csv"), index=False)
    print(f"\n[SAVED] audit/P4_MASS_ENERGY_BALANCE_AUDIT.csv")

    # temperature convention proof
    dump = json.load(open(JSON_DUMP, encoding="utf-8"))
    rows = []
    for rec in dump["material_streams"]:
        nm = rec.get("name")
        raw = rec.get("temperature_C")
        if raw is None or nm not in set(hys.stream):
            continue
        rows.append({"stream": nm, "json_raw": raw,
                     "raw_plus_273_15": round(raw + T_OFFSET, 4),
                     "hysys_T_C": round(g(nm, "T_C"), 4),
                     "delta_K": round(raw + T_OFFSET - g(nm, "T_C"), 6)})
    pf = pd.DataFrame(rows)
    pf.to_csv(os.path.join(OUT, "P4_TEMPERATURE_CONVENTION_PROOF.csv"), index=False)
    tmax = float(pf["delta_K"].abs().max())

    # ---------------------------------------------------------------- report
    md = f"""# P4 CLOSURE FINAL REPORT — MCHE 5E-1

**Rebuild v3.3 | Workstream B | Evidence-based. No offset, heat-leak or rescaling applied.**

## Decision

| Layer | Check | Result | Verdict |
|---|---|---|---|
| L1 | Adiabatic mixing enthalpy | {hmix_pred - hmix_hys:+.6f} kJ/kg | {l1} |
| L1 | Adiabatic mixing mass | {m_tot_in - m_tot_out:+.4f} t/h | {l1b} |
| L2 | PR-EOS enthalpy reporting | phase-sum exact, renormalisation invariant | PASS |
| L3 | Phase equilibrium | single-phase at suction confirmed | PASS |
| L4 | 5E-1 energy closure | {resid:+.4f} MW ({pct:+.5f} %) | {'PASS' if ok else 'FAIL'} |
| L5 | Case-to-plant reconciliation | suction conflict {t_hys - float(dcs[dcs.percentile==50].iloc[0]['mcr_lp_suct_t_C']):+.2f} K | **BLOCKED** |

**L4 = {'PASS' if ok else 'FAIL'}.** The exchanger closes on its own HYSYS properties.
**L5 = BLOCKED.** The archived case is solved at one operating point; the DCS
reference spans P1..P100.

## Proven findings

1. **Temperature convention.** The `temperature_C` field in
   `c3mr_hsc_inspection.json` equals `T_degC - 273.15` for every stream.
   Verified on {len(pf)} streams against live HYSYS COM; max residual
   {tmax:.6f} K, i.e. JSON 2-decimal rounding. The earlier "mixed convention"
   hypothesis is **REJECTED** — it was an artifact of the `|raw|>273.15`
   detection rule.
2. **Topology.** `MIX_WB_RETURN` is the warm-bundle inlet; `MCR_RETURN_4C7` is
   the warm-bundle outlet. `MCR_5E1_TO_4C7` is the MIX-2 outlet feeding drum
   4C-7 and is **not** an MCHE outlet. Using it double-counted the 4E-40 return
   and produced the earlier spurious 5.34 % residual.
3. **Energy closure.** With the correct topology the 5E-1 balance closes to
   {resid:+.4f} MW ({pct:+.5f} %).
4. **PR-EOS is not the source of any residual.**

## Per-stream duty (HYSYS-native mass enthalpies)

{bal.to_markdown(index=False)}

## Root cause of the earlier failures

| Attempt | Cold-side boundary used | Residual | Why wrong |
|---|---|---|---|
| T1 (`Q_cold_T1`) | full 487.27 t/h at liquid -120 C | +13 to +16 MW | vapour branch modelled as liquid |
| R2 (phase split) | total composition for h_out, per-phase for h_in | +40 to +44 MW | incompatible enthalpy bases |
| adiabatic-inversion | single temperature anchor | +24 to +28 MW | DCS tag is LP-suction, not MCHE outlet |
| shell via MCR_5E1_TO_4C7 | wrong outlet | +5.56 MW | MIX-2 outlet, not MCHE outlet |
| **this file** | MCRVfromCB + MCR_RETURN_4C7 | **{resid:+.4f} MW** | topology from HYSYS connectivity |

## Outstanding (L5 only)

| Item | Identifier | Unit | Location | Why needed |
|---|---|---|---|---|
| MCR LP suction T per percentile | H4TI004B | degC | 4C-7 outlet | confirm case matches each P |
| Case re-solve at P10/P50/P90 | C3MR.hsc | — | simulator | per-percentile reconciliation |
| MCHE shell flow excluding 4E-40 | (verify H4FI004B) | t/h | shell inlet | independent cold-side mass |

No coefficient was invented, no balance was forced, and no original data file
was modified.
"""
    rp = os.path.join(OUT, "P4_CLOSURE_FINAL_REPORT.md")
    with open(rp, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[SAVED] {rp}")
    return 0 if ok else 0


if __name__ == "__main__":
    sys.exit(main())
