"""Standalone Empirical Verification & Challenger Test Harness for Milestone 2.

Exercises computeClientPrediction (TypeScript) against backend routes and optimizer engine (Python).
Zero em-dash (U+2014) and zero en-dash (U+2013) strict rule applied.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Setup sys.path
backend_dir = Path(__file__).resolve().parents[1]
root_dir = backend_dir.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from fastapi.testclient import TestClient
from main import app
from core.ilr_engine import (
    CHI2_CRITICAL_5COMP,
    compute_mahalanobis_distance,
    ilr_forward,
)
from core.optimizer_engine import get_pareto_fallback_recommendation

client = TestClient(app)

print("=" * 70)
print("EMPIRICAL CHALLENGER: MILESTONE 2 VERIFICATION HARNESS")
print("=" * 70)

frontend_root = backend_dir.parent / "frontend"
if not frontend_root.exists():
    frontend_root = root_dir / "operator-website" / "frontend"

def run_ts_prediction(scenario: Dict[str, Any], actual_dcs: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute computeClientPrediction in pure TypeScript using npx tsx."""
    payload = json.dumps(scenario)
    actual_payload = json.dumps(actual_dcs) if actual_dcs else "undefined"
    ts_file = frontend_root / "src" / "utils" / "physicsEngine.ts"
    ts_file_posix = ts_file.as_posix()
    
    js_code = f"""
    import {{ computeClientPrediction }} from '{ts_file_posix}';
    const sc = {payload};
    const act = {actual_payload};
    const res = computeClientPrediction(sc, act);
    console.log(JSON.stringify(res));
    """
    
    proc = subprocess.run(
        ["cmd", "/c", "npx", "tsx", "-e", js_code],
        capture_output=True,
        text=True,
        cwd=str(frontend_root),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"TS execution failed: {proc.stderr}")
    return json.loads(proc.stdout)

def run_ts_recommendation(feed_flow: float, actual_dcs: Dict[str, Any] = None, alpha: float = 0.30) -> Dict[str, Any]:
    """Execute computeFrontendRecommendation in pure TypeScript using npx tsx."""
    act_payload = json.dumps(actual_dcs) if actual_dcs else "undefined"
    api_file = frontend_root / "src" / "api.ts"
    api_file_posix = api_file.as_posix()
    
    js_code = f"""
    import {{ computeFrontendRecommendation }} from '{api_file_posix}';
    const res = computeFrontendRecommendation({feed_flow}, {act_payload}, {alpha});
    console.log(JSON.stringify(res));
    """
    
    proc = subprocess.run(
        ["cmd", "/c", "npx", "tsx", "-e", js_code],
        capture_output=True,
        text=True,
        cwd=str(frontend_root),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"TS recommendation failed: {proc.stderr}")
    return json.loads(proc.stdout)

results_summary = {
    "task1_scenarios_tested": 0,
    "task2_power_matches_under_0_5_pct": 0,
    "task2_power_fails_over_0_5_pct": 0,
    "task2_dm_matches": 0,
    "task2_dm_fails": 0,
    "task2_interlocks_tested": 0,
    "task2_interlocks_passed": 0,
    "task2_power_decomposition_passed": 0,
    "task2_power_decomposition_failed": 0,
}

print("\n--- TEST 1: Power Parity Across Operating Regimes ---")
test_cases = [
    {"name": "Turndown 120 t/h", "feed_flow_t_h": 120.0, "mcr_flow_t_h": 480.0},
    {"name": "Baseline 150 t/h", "feed_flow_t_h": 150.0, "mcr_flow_t_h": 560.0},
    {"name": "Anchor 245.8 t/h", "feed_flow_t_h": 245.8, "mcr_flow_t_h": 505.3},
    {"name": "Baseload 303.8 t/h", "feed_flow_t_h": 303.8, "mcr_flow_t_h": 620.0},
    {"name": "Overload 380 t/h", "feed_flow_t_h": 380.0, "mcr_flow_t_h": 680.0},
]

for tc in test_cases:
    results_summary["task1_scenarios_tested"] += 1
    # Backend
    py_resp = client.post("/api/v1/predict", json=tc).json()
    py_power = py_resp["prediction"]["total_shaft_power_mw"]
    py_c3 = py_resp["prediction"]["power_c3_mw"]
    py_mcr = py_resp["prediction"]["power_mcr_mw"]
    
    # Frontend
    ts_resp = run_ts_prediction(tc)
    ts_power = ts_resp["prediction"]["total_shaft_power_mw"]
    ts_c3 = ts_resp["prediction"]["power_c3_mw"]
    ts_mcr = ts_resp["prediction"]["power_mcr_mw"]
    
    delta_mw = abs(ts_power - py_power)
    delta_pct = (delta_mw / py_power) * 100.0
    
    within_tol = delta_pct <= 0.50
    if within_tol:
        results_summary["task2_power_matches_under_0_5_pct"] += 1
        status = "PASS (< 0.5%)"
    else:
        results_summary["task2_power_fails_over_0_5_pct"] += 1
        status = "FAIL (> 0.5%)"
        
    print(f"Scenario: {tc['name']:<18} | Py: {py_power:6.2f} MW | TS: {ts_power:6.2f} MW | Diff: {delta_mw:5.2f} MW ({delta_pct:5.2f}%) | {status}")
    
    # Verify decomposition sum
    decomp_sum = ts_c3 + ts_mcr
    decomp_ok = abs(decomp_sum - ts_power) <= 0.02
    if decomp_ok:
        results_summary["task2_power_decomposition_passed"] += 1
    else:
        results_summary["task2_power_decomposition_failed"] += 1

print("\n--- TEST 2: Mahalanobis Distance D_M Parity ---")
comp_cases = [
    {"name": "Baseline GC", "comp": [3.38, 44.37, 44.94, 0.85, 6.28]},
    {"name": "High N2 (5.0%)", "comp": [5.00, 43.50, 44.50, 0.50, 6.50]},
    {"name": "Low C3 (3.7%)", "comp": [3.03, 47.49, 45.78, 0.00, 3.70]},
    {"name": "Shifted Heavy", "comp": [2.26, 42.35, 48.95, 0.01, 6.42]},
    {"name": "Out of Envelope", "comp": [10.0, 30.0, 40.0, 5.0, 15.0]},
]

for cc in comp_cases:
    comp = cc["comp"]
    c_arr = [c / sum(comp) for c in comp]
    py_xi = ilr_forward(c_arr)[0]
    py_dm = float(compute_mahalanobis_distance(py_xi))
    
    sc = {
        "feed_flow_t_h": 250.0,
        "mcr_flow_t_h": 560.0,
        "comp_N2_molpct": comp[0],
        "comp_C1_molpct": comp[1],
        "comp_C2_molpct": comp[2],
        "comp_C2H4_molpct": comp[3],
        "comp_C3_molpct": comp[4],
    }
    ts_resp = run_ts_prediction(sc)
    ts_dm = ts_resp["domain_check"]["mahalanobis_distance"]
    
    dm_diff = abs(ts_dm - py_dm)
    if dm_diff <= 0.001:
        results_summary["task2_dm_matches"] += 1
        dm_status = "PASS"
    else:
        results_summary["task2_dm_fails"] += 1
        dm_status = "FAIL"
    print(f"Comp: {cc['name']:<18} | Py D_M: {py_dm:7.4f} | TS D_M: {ts_dm:7.4f} | Diff: {dm_diff:7.4f} | {dm_status}")

print("\n--- TEST 3: Interlocks and Process Boundaries ---")
interlock_cases = [
    {
        "desc": "Anti-surge floor violation (MCR = 475.0 < 480.0)",
        "scenario": {"feed_flow_t_h": 200.0, "mcr_flow_t_h": 475.0},
        "expect_violation": "4UV-53",
    },
    {
        "desc": "Anti-surge floor compliant (MCR = 480.0)",
        "scenario": {"feed_flow_t_h": 200.0, "mcr_flow_t_h": 480.0},
        "expect_no_violation": "4UV-53",
    },
    {
        "desc": "Suction TAL alarm (T_suct = -45.5 <= -45.0 C)",
        "scenario": {"feed_flow_t_h": 200.0, "mcr_flow_t_h": 500.0, "H4TI004B": -45.5},
        "expect_violation": "4TV-510",
    },
    {
        "desc": "Suction TALL trip (T_suct = -52.0 <= -51.0 C)",
        "scenario": {"feed_flow_t_h": 200.0, "mcr_flow_t_h": 500.0, "H4TI004B": -52.0},
        "expect_violation": "TALL",
    },
    {
        "desc": "Suction compliant (T_suct = -41.0 C)",
        "scenario": {"feed_flow_t_h": 200.0, "mcr_flow_t_h": 500.0, "H4TI004B": -41.0},
        "expect_no_violation": "TAL",
    },
    {
        "desc": "Propane suction vacuum (< 1.033 kg/cm2A)",
        "scenario": {"feed_flow_t_h": 200.0, "p_c3_suct_kgcm2a": 0.98},
        "expect_violation": "atmosferik",
    },
    {
        "desc": "MITA pinch approach (< 1.50 C)",
        "scenario": {"feed_flow_t_h": 200.0, "mita_pinch_c": 1.20},
        "expect_violation": "MITA",
    },
    {
        "desc": "Train H Capacity Exceeded (Feed = 380.0 > 350.0 t/h)",
        "scenario": {"feed_flow_t_h": 380.0},
        "expect_capacity_warning": True,
    },
]

for ic in interlock_cases:
    results_summary["task2_interlocks_tested"] += 1
    ts_resp = run_ts_prediction(ic["scenario"])
    viols = " ".join(ts_resp["safety_check"]["violations"])
    warns = " ".join(ts_resp["safety_check"]["warnings"])
    cap_exceeded = ts_resp["prediction"]["capacity_exceeded"]
    
    passed = True
    if "expect_violation" in ic:
        if ic["expect_violation"] not in viols:
            passed = False
    if "expect_no_violation" in ic:
        if ic["expect_no_violation"] in viols:
            passed = False
    if "expect_capacity_warning" in ic:
        if not cap_exceeded:
            passed = False
            
    if passed:
        results_summary["task2_interlocks_passed"] += 1
        print(f"Interlock: {ic['desc']:<55} | PASS")
    else:
        print(f"Interlock: {ic['desc']:<55} | FAIL (viols: {viols})")

print("\n--- TEST 4: Recommendation Engine Parity (api.ts vs optimizer_engine.py) ---")
rec_feeds = [140.0, 200.0, 250.0, 300.0]
for rf in rec_feeds:
    # Python
    py_rec = get_pareto_fallback_recommendation(rf)
    # TypeScript
    ts_rec = run_ts_recommendation(rf)
    
    mcr_diff = abs(ts_rec["mcr_flow_t_h"] - py_rec["mcr_flow_t_h"])
    c1_diff = abs(ts_rec["comp_C1_molpct"] - py_rec["comp_C1_molpct"])
    c2_diff = abs(ts_rec["comp_C2_molpct"] - py_rec["comp_C2_molpct"])
    c3_diff = abs(ts_rec["comp_C3_molpct"] - py_rec["comp_C3_molpct"])
    
    print(f"Feed: {rf} t/h | MCR Diff: {mcr_diff:.1f} t/h | C1 Diff: {c1_diff:.2f}% | C2 Diff: {c2_diff:.2f}% | C3 Diff: {c3_diff:.2f}%")
    print(f"  Py DM: {py_rec['mahalanobis_distance']} | TS DM: {ts_rec['mahalanobis_distance']} (TS hardcoded=0.85)")

print("\n" + "=" * 70)
print("FINAL TEST HARNESS SUMMARY:")
print(f"  Scenarios Tested: {results_summary['task1_scenarios_tested']}")
print(f"  Power Matches (< 0.5%): {results_summary['task2_power_matches_under_0_5_pct']}")
print(f"  Power Fails (> 0.5%): {results_summary['task2_power_fails_over_0_5_pct']}")
print(f"  Mahalanobis D_M Matches: {results_summary['task2_dm_matches']}")
print(f"  Interlocks Passed: {results_summary['task2_interlocks_passed']} / {results_summary['task2_interlocks_tested']}")
print(f"  Power Decomposition Passed: {results_summary['task2_power_decomposition_passed']}")
print("=" * 70)
