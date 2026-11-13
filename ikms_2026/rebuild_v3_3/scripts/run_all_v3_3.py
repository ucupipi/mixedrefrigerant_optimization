"""
MASTER ORCHESTRATION RUNNER — REBUILD v3.3
PT Badak NGL Train H C3MR Research (IKMS 2026)

Executes Priorities P1 through P10 sequentially and runs master regression test suite.
"""

import os
import sys
import subprocess
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "scripts")
TESTS_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "tests")

PIPELINE_SCRIPTS = [
    ("Priority 1: Legacy Retirement", "p1_legacy_retirement.py"),
    ("Priority 2: Energy Baseline Reconstruction", "p2_energy_baseline.py"),
    ("Priority 3: Simulator Case Audit", "p3_simulator_audit.py"),
    ("Priority 4: 4E-40 Hydraulics & MCHE Profiles", "p4_mche_4e40.py"),
    ("Priority 5: Rotating Equipment & Surge Limits", "p5_compressor_turbine.py"),
    ("Priority 6: Composition Control & Makeup Feasibility", "p6_composition_control.py"),
    ("Priority 7: Genuine Physical DoE & Surrogates", "p7_physical_doe.py"),
    ("Priority 8: True Joint Optimization", "p8_true_joint_optimization.py"),
    ("Priority 9: Monte Carlo N=10k Robustness", "p9_robustness_decision.py"),
    ("Priority 10: Final Acceptance Ledger & Matrix", "p10_acceptance_and_ledger.py"),
]

def main():
    print("=" * 80)
    print("STARTING MASTER REBUILD v3.3 PIPELINE EXECUTION")
    print("PT Badak NGL Train H C3MR Research Suite")
    print("=" * 80)
    t_start = time.time()
    
    for title, script_name in PIPELINE_SCRIPTS:
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        print(f"\n[*] Executing {title} ({script_name})...")
        t0 = time.time()
        res = subprocess.run([sys.executable, script_path], cwd=BASE_DIR, capture_output=True, text=True)
        elapsed = time.time() - t0
        
        if res.returncode != 0:
            print(f"[!] FAILED ({elapsed:.2f}s): {script_name}")
            print(res.stderr)
            sys.exit(res.returncode)
        else:
            print(f"[+] SUCCESS ({elapsed:.2f}s)")
            if res.stdout.strip():
                for line in res.stdout.strip().split("\n")[:4]:
                    print(f"    {line}")
                    
    # Execute Master Regression Test Suite
    test_file = os.path.join(TESTS_DIR, "test_rebuild_v3_3.py")
    print(f"\n[*] Executing Master Regression Test Suite ({test_file})...")
    t_test = time.time()
    res_test = subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"], cwd=BASE_DIR, capture_output=True, text=True)
    elapsed_test = time.time() - t_test
    
    print(res_test.stdout)
    if res_test.returncode != 0:
        print(f"[!] Master Test Suite FAILED ({elapsed_test:.2f}s)")
        sys.exit(res_test.returncode)
    else:
        print(f"[+] Master Test Suite PASSED 100% ALL GREEN ({elapsed_test:.2f}s)")
        
    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"MASTER REBUILD v3.3 COMPLETE — ALL DELIVERABLES VERIFIED IN {total_time:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()
