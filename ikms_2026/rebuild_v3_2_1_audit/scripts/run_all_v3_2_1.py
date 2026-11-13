"""
Master Runner: Execute all Rebuild v3.2.1 Phases (P0-P9) sequentially.
Reports gate status for each phase.
"""
import subprocess
import sys
import os
import time

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, "..", "..", ".."))

PHASES = [
    ("P0", "p0_forensic_dependency_audit.py",     "Source Forensics"),
    ("P1", "p1_steam_reconstruction_v3_2_1.py",    "Steam & Condensate Balance"),
    ("P2", "p2_mche_robustness_v3_2_1.py",         "MCHE Uncertainty & Robustness"),
    ("P3", "p3_rotating_equipment_v3_2_1.py",       "Rotating Equipment & Anti-Surge"),
    ("P4", "p4_control_feasibility_v3_2_1.py",      "Control Feasibility"),
    ("P5", "p5_surrogate_qualification_v3_2_1.py",  "Surrogate Qualification"),
    ("P6", "p6_joint_optimization_v3_2_1.py",       "Joint Optimization & Synergy"),
    ("P7", "p7_accounting_v3_2_1.py",               "Accounting & Energy Closure"),
    ("P8", "p8_robustness_decision_v3_2_1.py",      "Robustness & Decisions"),
    ("V1", "v1_independent_verification.py",       "Independent Forensic Checks"),
    ("V2", "v2_resolve_10_blockers.py",            "Ten Forensic Blockers Resolution"),
    ("P9", "p9_field_testability_and_ledger.py",     "Field Testability & Claim Evidence"),
]

def run_phase(phase_id, script_name, description):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return phase_id, description, "SKIP (script not found)", 0.0
    
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    elapsed = time.time() - t0
    
    if result.returncode == 0:
        return phase_id, description, "PASS", elapsed
    else:
        err_lines = result.stderr.strip().split('\n')[-3:]
        err_summary = ' | '.join(err_lines)
        return phase_id, description, f"FAIL: {err_summary}", elapsed


def main():
    print("=" * 80)
    print("REBUILD v3.2.1 — MASTER RUNNER")
    print("Badak LNG Train H C3MR Independent Forensic Qualification")
    print("=" * 80)
    print()
    
    results = []
    total_t0 = time.time()
    
    for phase_id, script_name, description in PHASES:
        print(f"[{phase_id}] {description} ... ", end="", flush=True)
        try:
            r = run_phase(phase_id, script_name, description)
        except subprocess.TimeoutExpired:
            r = (phase_id, description, "FAIL: Timeout (>300s)", 300.0)
        results.append(r)
        print(f"{r[2]} ({r[3]:.1f}s)")
    
    total_elapsed = time.time() - total_t0
    
    print()
    print("=" * 80)
    print("GATE STATUS SUMMARY")
    print("=" * 80)
    passed = sum(1 for r in results if r[2] == "PASS")
    failed = sum(1 for r in results if r[2].startswith("FAIL"))
    skipped = sum(1 for r in results if r[2].startswith("SKIP"))
    
    for r in results:
        status_icon = "✓" if r[2] == "PASS" else ("✗" if r[2].startswith("FAIL") else "○")
        print(f"  {status_icon} Gate {r[0][1:]}: {r[1]:<40s} {r[2]}")
    
    print(f"\nTotal: {passed} PASS, {failed} FAIL, {skipped} SKIP  ({total_elapsed:.1f}s)")
    
    if failed > 0:
        print("\n*** QUALIFICATION INCOMPLETE — FIX FAILURES BEFORE ACCEPTANCE ***")
        sys.exit(1)
    else:
        print("\n*** ALL 10 GATES PASSED — REBUILD v3.2.1 QUALIFIED ***")
        sys.exit(0)


if __name__ == "__main__":
    main()

