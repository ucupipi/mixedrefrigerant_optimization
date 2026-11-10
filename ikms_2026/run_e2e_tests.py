#!/usr/bin/env python3
"""E2E Test Runner for Badak LNG Train H C3MR Performance Optimization Suite (IKMS 2026).

Executes the requirement-driven, opaque-box E2E test suite across Tiers 1-4:
- Tier 1: Feature Coverage (F1 to F18)
- Tier 2: Boundary & Corner Cases (F1 to F18)
- Tier 3: Cross-Feature Pairwise Interactions
- Tier 4: Real-World Operational Scenarios

Usage:
    python run_e2e_tests.py
    python run_e2e_tests.py --tier 1
    python run_e2e_tests.py --tier 2
    python run_e2e_tests.py --tier 3
    python run_e2e_tests.py --tier 4
    python run_e2e_tests.py --json-out reports/e2e_results.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS_E2E_DIR = ROOT / "tests" / "e2e"
DEFAULT_JSON_OUT = ROOT / "reports" / "e2e_results.json"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IKMS 2026 E2E Test Suite Runner")
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Run specific test tier (1: Coverage, 2: Boundary, 3: Cross, 4: Scenarios, all: Everything)",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=DEFAULT_JSON_OUT,
        help="Path to output structured test results JSON report",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run pytest in verbose mode with detailed failure traces",
    )
    parser.add_argument(
        "-k", "--filter",
        type=str,
        default="",
        help="Pytest substring expression filter (-k)",
    )
    parser.add_argument(
        "--progressive",
        action="store_true",
        help="Progressive mode: exit code 0 if runner successfully finishes execution and generates report",
    )
    return parser.parse_args()


def get_target_test_files(tier: str) -> list[str]:
    mapping = {
        "1": ["tests/e2e/test_tier1_feature_coverage.py"],
        "2": ["tests/e2e/test_tier2_boundary_corner.py"],
        "3": ["tests/e2e/test_tier3_cross_feature.py"],
        "4": ["tests/e2e/test_tier4_real_world_scenarios.py"],
        "all": [
            "tests/e2e/test_tier1_feature_coverage.py",
            "tests/e2e/test_tier2_boundary_corner.py",
            "tests/e2e/test_tier3_cross_feature.py",
            "tests/e2e/test_tier4_real_world_scenarios.py",
        ],
    }
    return mapping.get(tier, mapping["all"])


def execute_tests(target_files: list[str], verbose: bool, filter_expr: str) -> dict:
    """Execute pytest as a subprocess and parse stdout into structured test metrics."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *target_files,
        "-v",
        "--tb=short",
    ]
    if filter_expr:
        cmd.extend(["-k", filter_expr])

    print(f"\n[E2E Runner] Executing: {' '.join(cmd)}")
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed_sec = time.perf_counter() - t0
    stdout = proc.stdout
    stderr = proc.stderr

    # Pattern to match: tests/e2e/test_tier...py::test_... PASSED/FAILED/SKIPPED/ERROR
    test_pattern = re.compile(
        r"^(tests/e2e/test_tier\d_[a-z_]+\.py::([a-zA-Z0-9_]+))\s+(PASSED|FAILED|SKIPPED|ERROR)",
        re.MULTILINE,
    )
    matches = test_pattern.findall(stdout)

    results = []
    tier_counts = defaultdict(lambda: {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0})
    feature_counts = defaultdict(lambda: {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0})

    for full_node, test_name, status in matches:
        tier_match = re.search(r"test_tier(\d)", full_node)
        tier_num = f"Tier {tier_match.group(1)}" if tier_match else "Other"
        tier_counts[tier_num][status] += 1

        # Extract feature tag (e.g. f1, f2, ... f18)
        feat_match = re.search(r"_f(\d{1,2})_", test_name)
        if feat_match:
            feat_tag = f"F{feat_match.group(1)}"
            feature_counts[feat_tag][status] += 1
        elif "scen" in test_name:
            scen_match = re.search(r"scen(\d)", test_name)
            scen_tag = f"Scenario {scen_match.group(1)}" if scen_match else "Scenario"
            feature_counts[scen_tag][status] += 1
        elif "cross" in test_name:
            feature_counts["Tier 3 (Cross)"][status] += 1
        else:
            feature_counts["Other"][status] += 1

        results.append({
            "nodeid": full_node,
            "test_name": test_name,
            "status": status,
            "tier": tier_num,
        })

    total_passed = sum(1 for r in results if r["status"] == "PASSED")
    total_failed = sum(1 for r in results if r["status"] == "FAILED")
    total_skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    total_error = sum(1 for r in results if r["status"] == "ERROR")
    total_count = len(results)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pytest_returncode": proc.returncode,
        "elapsed_seconds": round(elapsed_sec, 2),
        "summary": {
            "total": total_count,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "error": total_error,
        },
        "by_tier": dict(tier_counts),
        "by_feature": dict(feature_counts),
        "tests": results,
        "raw_stdout_tail": stdout[-3000:],
    }
    return report


def print_dashboard(report: dict):
    """Print industrial dashboard to console."""
    summary = report["summary"]
    total = max(1, summary["total"])
    pass_pct = (summary["passed"] / total) * 100.0

    print("\n" + "=" * 80)
    print("      BADAK LNG TRAIN H C3MR COMPRESSOR & ML OPTIMIZATION (IKMS 2026)")
    print("                   END-TO-END VERIFICATION DASHBOARD")
    print("=" * 80)
    print(f" Timestamp      : {report['timestamp']}")
    print(f" Execution Time : {report['elapsed_seconds']} s")
    print(f" Total Tests    : {summary['total']}")
    print(f" Passed         : {summary['passed']:<4} ({pass_pct:.1f}%)")
    print(f" Failed         : {summary['failed']}")
    print(f" Skipped        : {summary['skipped']}")
    print(f" Error          : {summary['error']}")
    print("-" * 80)

    print("\n[BREAKDOWN BY TIER]")
    print(f" {'Tier':<25} | {'Passed':<8} | {'Failed':<8} | {'Total':<8} | {'Pass Rate':<10}")
    print("-" * 72)
    for tier, counts in sorted(report["by_tier"].items()):
        tot = sum(counts.values())
        rate = f"{(counts['PASSED'] / tot * 100):.1f}%" if tot > 0 else "0.0%"
        print(f" {tier:<25} | {counts['PASSED']:<8} | {counts['FAILED']:<8} | {tot:<8} | {rate:<10}")

    print("\n[BREAKDOWN BY FEATURE / COMPONENT]")
    print(f" {'Feature / Component':<25} | {'Passed':<8} | {'Failed':<8} | {'Total':<8} | {'Pass Rate':<10}")
    print("-" * 72)
    # Sort feature keys nicely
    def sort_key(k: str):
        if k.startswith("F") and k[1:].isdigit():
            return (1, int(k[1:]))
        elif k.startswith("Scenario"):
            parts = k.split()
            return (2, int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 99)
        elif "Cross" in k:
            return (3, 0)
        return (4, k)

    for feat in sorted(report["by_feature"].keys(), key=sort_key):
        counts = report["by_feature"][feat]
        tot = sum(counts.values())
        rate = f"{(counts['PASSED'] / tot * 100):.1f}%" if tot > 0 else "0.0%"
        print(f" {feat:<25} | {counts['PASSED']:<8} | {counts['FAILED']:<8} | {tot:<8} | {rate:<10}")

    print("\n" + "=" * 80)


def main():
    args = parse_arguments()
    target_files = get_target_test_files(args.tier)
    report = execute_tests(target_files, args.verbose, args.filter)
    print_dashboard(report)

    # Save structured JSON report
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[E2E Runner] Structured test results saved to: {args.json_out.resolve()}")

    if args.progressive:
        return 0

    return 0 if (report["summary"]["failed"] == 0 and report["summary"]["error"] == 0) else report["pytest_returncode"]


if __name__ == "__main__":
    sys.exit(main())
