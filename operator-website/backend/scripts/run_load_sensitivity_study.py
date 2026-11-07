"""operator-website/backend/scripts/run_load_sensitivity_study.py
Badak LNG Plant-5 Train H (Liquefaction) - C3MR Load Sensitivity Study
Milestone 4: Comprehensive Operating Envelope Sweep (140.0 to 340.0 t/h)

This script performs systematic multi-scenario simulation sweeps across the
operating envelope of Train H, comparing:
  - Baseline DCS Operation (historical quantile anchor)
  - Strategy A: FIXED_RECIPE (certified invariant master recipe)
  - Strategy B: CONDITION_DEPENDENT (dynamic 5D composition & circulation)
  - Strategy C: MINIMUM_INTERVENTION (energy gain vs transition cost)

Outputs:
  - operator-website/backend/data/load_sensitivity_study.csv
  - Formatted console ledger with thermodynamic margin verification

Safety & Governance:
  - Badak LNG Plant-5 Train H (Liquefaction). Advisory decision support only.
  - Zero DCS write operations.
  - 100% first-principles thermodynamics: PR-EOS, anti-surge floor 480 t/h,
    suction TAL -45.0 deg C, Mahalanobis distance <= 3.0802.
  - Zero em-dashes and en-dashes per repository guidelines.
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# ── Ensure Backend and Root are in sys.path ───────────────────────────
_CURRENT_FILE = Path(__file__).resolve()
_SCRIPTS_DIR = _CURRENT_FILE.parent
_BACKEND_DIR = _SCRIPTS_DIR.parent
_ROOT_DIR = _BACKEND_DIR.parent.parent

for p in (str(_ROOT_DIR), str(_BACKEND_DIR), str(_BACKEND_DIR / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.optimizer_engine import recommend, ANTISURGE_FLOOR_T_H, SUCTION_TAL_C
from core.makeup_calculator import calculate_makeup_recommendations
from api.routes import predict_scenario
from api.schemas import PredictRequest


def run_load_sensitivity_sweep() -> List[Dict[str, Any]]:
    feed_steps = [140.0, 160.0, 180.0, 200.0, 220.0, 240.0, 245.8, 260.0, 280.0, 300.0, 320.0, 340.0]
    strategies = ["FIXED_RECIPE", "CONDITION_DEPENDENT", "MINIMUM_INTERVENTION"]

    # Baseline DCS composition at Train H
    base_actual_dcs = {
        "comp_N2_molpct": 3.39,
        "comp_C1_molpct": 44.45,
        "comp_C2_molpct": 45.02,
        "comp_C2H4_molpct": 0.85,
        "comp_C3_molpct": 6.29,
        "mcr_flow_t_h": 562.3,
    }

    records: List[Dict[str, Any]] = []

    print("=" * 115)
    print("BADAK LNG PLANT-5 TRAIN H : LOAD SENSITIVITY SWEEP (140.0 - 340.0 t/h)")
    print("Zero DCS Write Advisory : Comparing Strategies A, B, and C against DCS Baseline")
    print("=" * 115)

    for feed in feed_steps:
        # Scale baseline DCS MCR circulation with feed (subject to minimum anti-surge floor 480 t/h)
        # Ratio around 2.28 t/h MCR per t/h feed at baseline
        scaled_dcs_mcr = max(ANTISURGE_FLOOR_T_H, feed * (562.3 / 245.8))
        actual_dcs = dict(base_actual_dcs)
        actual_dcs["mcr_flow_t_h"] = round(scaled_dcs_mcr, 1)

        # Baseline Prediction
        base_req = PredictRequest(
            feed_flow_t_h=feed,
            mcr_flow_t_h=scaled_dcs_mcr,
            comp_N2_molpct=actual_dcs["comp_N2_molpct"],
            comp_C1_molpct=actual_dcs["comp_C1_molpct"],
            comp_C2_molpct=actual_dcs["comp_C2_molpct"],
            comp_C2H4_molpct=actual_dcs["comp_C2H4_molpct"],
            comp_C3_molpct=actual_dcs["comp_C3_molpct"],
            actual_feed_flow_t_h=feed,
            actual_mcr_flow_t_h=scaled_dcs_mcr,
            actual_comp_N2_molpct=actual_dcs["comp_N2_molpct"],
            actual_comp_C1_molpct=actual_dcs["comp_C1_molpct"],
            actual_comp_C2_molpct=actual_dcs["comp_C2_molpct"],
            actual_comp_C2H4_molpct=actual_dcs["comp_C2H4_molpct"],
            actual_comp_C3_molpct=actual_dcs["comp_C3_molpct"],
            transition_hours=2.0,
        )
        base_res = predict_scenario(base_req)
        base_power_mw = base_res.prediction.total_shaft_power_mw
        base_sec = base_res.prediction.sec_lng_kwh_per_t or base_res.prediction.sec_kwh_per_t

        actual_comp_map = {
            "N2": actual_dcs["comp_N2_molpct"],
            "C1": actual_dcs["comp_C1_molpct"],
            "C2": actual_dcs["comp_C2_molpct"],
            "C2H4": actual_dcs["comp_C2H4_molpct"],
            "C3": actual_dcs["comp_C3_molpct"],
        }

        for strat in strategies:
            # 1. Run optimizer
            opt = recommend(
                feed_t_h=feed,
                actual_comp=actual_comp_map,
                actual_mcr_flow_t_h=scaled_dcs_mcr,
                alpha_trim=0.30,
                strategy=strat,
            )

            # 2. Run predictor for optimal target
            opt_req = PredictRequest(
                feed_flow_t_h=feed,
                mcr_flow_t_h=opt["mcr_flow_t_h"],
                comp_N2_molpct=opt["comp_N2_molpct"],
                comp_C1_molpct=opt["comp_C1_molpct"],
                comp_C2_molpct=opt["comp_C2_molpct"],
                comp_C2H4_molpct=opt["comp_C2H4_molpct"],
                comp_C3_molpct=opt["comp_C3_molpct"],
                actual_feed_flow_t_h=feed,
                actual_mcr_flow_t_h=scaled_dcs_mcr,
                actual_comp_N2_molpct=actual_dcs["comp_N2_molpct"],
                actual_comp_C1_molpct=actual_dcs["comp_C1_molpct"],
                actual_comp_C2_molpct=actual_dcs["comp_C2_molpct"],
                actual_comp_C2H4_molpct=actual_dcs["comp_C2H4_molpct"],
                actual_comp_C3_molpct=actual_dcs["comp_C3_molpct"],
                transition_hours=2.0,
            )
            opt_pred = predict_scenario(opt_req)

            opt_power_mw = opt_pred.prediction.total_shaft_power_mw
            opt_sec = opt_pred.prediction.sec_lng_kwh_per_t or opt_pred.prediction.sec_kwh_per_t
            delta_power_mw = opt_pred.prediction.delta_power_mw
            delta_power_pct = opt_pred.prediction.delta_power_pct
            delta_sec = opt_pred.prediction.delta_sec_kwh_per_t or (opt_sec - base_sec)

            # 3. Calculate make-up requirement
            actual_comp_map = {
                "N2": actual_dcs["comp_N2_molpct"],
                "C1": actual_dcs["comp_C1_molpct"],
                "C2": actual_dcs["comp_C2_molpct"],
                "C2H4": actual_dcs["comp_C2H4_molpct"],
                "C3": actual_dcs["comp_C3_molpct"],
            }
            target_comp_map = {
                "N2": opt["comp_N2_molpct"],
                "C1": opt["comp_C1_molpct"],
                "C2": opt["comp_C2_molpct"],
                "C2H4": opt["comp_C2H4_molpct"],
                "C3": opt["comp_C3_molpct"],
            }
            makeup = calculate_makeup_recommendations(
                actual_molpct=actual_comp_map,
                target_molpct=target_comp_map,
                inventory_kg=24000.0,
                transition_hours=2.0,
            )

            residuals = opt.get("constraint_residuals", {})
            suct_margin = residuals.get("suction_tal_margin_c", opt["expected_suction_temp_c"] - SUCTION_TAL_C)
            surge_margin = residuals.get("antisurge_margin_t_h", opt["mcr_flow_t_h"] - ANTISURGE_FLOOR_T_H)

            record = {
                "feed_flow_t_h": feed,
                "strategy": strat,
                "mcr_flow_t_h": opt["mcr_flow_t_h"],
                "comp_N2_molpct": opt["comp_N2_molpct"],
                "comp_C1_molpct": opt["comp_C1_molpct"],
                "comp_C2_molpct": opt["comp_C2_molpct"],
                "comp_C2H4_molpct": opt["comp_C2H4_molpct"],
                "comp_C3_molpct": opt["comp_C3_molpct"],
                "total_shaft_power_mw": opt_power_mw,
                "baseline_power_mw": base_power_mw,
                "delta_power_mw": delta_power_mw,
                "delta_power_pct": delta_power_pct,
                "sec_lng_kwh_per_t": opt_sec,
                "baseline_sec_lng_kwh_per_t": base_sec,
                "delta_sec_kwh_per_t": delta_sec,
                "expected_suction_temp_c": opt["expected_suction_temp_c"],
                "suction_tal_margin_c": suct_margin,
                "antisurge_margin_t_h": surge_margin,
                "mahalanobis_distance": opt["mahalanobis_distance"],
                "makeup_total_flow_nm3_h": makeup["total_makeup_flow_nm3_h"],
                "makeup_total_flow_kg_h": makeup["total_makeup_flow_kg_h"],
                "makeup_status": makeup["status"],
                "solver_converged": opt.get("solver_converged", True),
                "capacity_warning": opt_pred.prediction.capacity_warning or "None",
            }
            records.append(record)

    # 4. Print summary table
    print(f"{'Feed':>6} | {'Strategy':<22} | {'MCR':>6} | {'N2/C1/C2/C3':<20} | {'Power':>7} | {'dPower':>7} | {'SEC':>6} | {'dSEC':>6} | {'Tsuct':>6} | {'Surge':>6} | {'Makeup Nm3/h':>12}")
    print("-" * 115)
    for r in records:
        comp_str = f"{r['comp_N2_molpct']:.1f}/{r['comp_C1_molpct']:.1f}/{r['comp_C2_molpct']:.1f}/{r['comp_C3_molpct']:.1f}"
        print(f"{r['feed_flow_t_h']:6.1f} | {r['strategy']:<22} | {r['mcr_flow_t_h']:6.1f} | {comp_str:<20} | {r['total_shaft_power_mw']:7.2f} | {r['delta_power_mw']:7.2f} | {r['sec_lng_kwh_per_t']:6.1f} | {r['delta_sec_kwh_per_t']:6.1f} | {r['expected_suction_temp_c']:6.1f} | {r['antisurge_margin_t_h']:6.1f} | {r['makeup_total_flow_nm3_h']:12.1f}")

    # 5. Export CSV
    out_dir = _BACKEND_DIR / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "load_sensitivity_study.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print("\n" + "=" * 115)
    print(f"Sweep completed successfully. {len(records)} scenario evaluations exported to:")
    print(f"  {out_csv}")
    print("=" * 115)
    return records


if __name__ == "__main__":
    run_load_sensitivity_sweep()
