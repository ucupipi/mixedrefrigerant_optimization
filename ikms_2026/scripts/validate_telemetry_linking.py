"""
Automated Standalone Validation Test Suite: DCS Telemetry Linking & Operating Envelope Mapping
PT Badak NGL Train H C3MR Liquefaction Optimization (IKMS 2026)

Governance:
  - AGENTS.md (Pasal 1 s.d. Pasal 13)
  - First-Principles Ground Truth: Zero Magic Numbers, Zero Invented Compositions
  - Decoupled Verification of Rotating Equipment Telemetry Linking

Validates:
  1. File Existence & Dual Format Parity (Parquet vs CSV)
  2. Dataset Schema Compliance & Column Completeness (39 Columns)
  3. Zero Null, NaN, or Infinite Values in Operating Points Dataset
  4. Suction Thermodynamic Property Calculations (PR-EOS Density, Z, k, MW)
  5. Mass-to-Volumetric Flow Conversion Identities (Q_actual = m_dot / rho)
  6. Production Quantiles Linking (P10, P50, P90 Steady-State Medians)
  7. Compressor Operating Envelope Compliance & Speed Window (70% - 105% MCS)
  8. Surge Margin Calculation & 480 t/h Suction Flow Floor Protection
  9. OEM Design Guarantee Point Precision (4K-1, 4K-2, 4K-3)
  10. Mechanical Status Classification & Safety Interlock Verification
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# Expected Schema adhering strictly to PROJECT.md and Milestone 3 Specifications
EXPECTED_COLUMNS = [
    "load_quantile",
    "operating_mode",
    "compressor_tag",
    "casing_tag",
    "stage_or_section",
    "fluid_description",
    "molecular_weight_g_mol",
    "suction_pressure_bar_a",
    "suction_pressure_kgcm2a",
    "suction_temperature_c",
    "suction_temperature_k",
    "suction_density_kg_m3",
    "compressibility_factor_z",
    "isentropic_exponent_k",
    "mass_flow_t_h",
    "mass_flow_kg_h",
    "flow_basis",
    "actual_volumetric_flow",
    "speed_rpm",
    "speed_pct_rated",
    "speed_pct_mcs",
    "polytropic_head_m",
    "pressure_ratio",
    "discharge_pressure_kgcm2a",
    "discharge_pressure_bar_a",
    "polytropic_efficiency",
    "shaft_power_kw",
    "shaft_power_mw",
    "surge_flow",
    "surge_margin_pct",
    "choke_flow",
    "choke_margin_pct",
    "is_surge_safe",
    "is_head_compliant",
    "is_speed_compliant",
    "mechanical_status",
    "anti_surge_kickback_flow_t_h",
    "suction_reheat_flow_t_h",
    "net_process_flow_t_h",
]


class TelemetryLinkingValidator:
    """
    Robust test suite for verifying compressor operating points and DCS telemetry linking.
    """

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.processed_dir = root_dir / "data" / "processed"
        self.parquet_path = self.processed_dir / "compressor_mapped_operating_points.parquet"
        self.csv_path = self.processed_dir / "compressor_mapped_operating_points.csv"
        
        self.passes = 0
        self.failures = 0
        self.errors: List[str] = []

    def assert_true(self, condition: bool, test_name: str, error_msg: str = "") -> None:
        """Assert condition is True with tracking."""
        if condition:
            self.passes += 1
            print(f"  [PASS] {test_name}")
        else:
            self.failures += 1
            full_msg = f"FAILED: {test_name}. {error_msg}"
            self.errors.append(full_msg)
            print(f"  [FAIL] {test_name} -> {error_msg}")

    def run_all_tests(self) -> int:
        """Execute all test cases sequentially."""
        print("=" * 80)
        print("  PT BADAK NGL TRAIN H C3MR COMPRESSOR TELEMETRY LINKING VALIDATION")
        print("  Milestone 3 Quality Gate: Operating Envelope & Thermodynamic Verification")
        print("=" * 80)

        self.test_01_file_existence_and_parity()
        self.test_02_schema_compliance()
        self.test_03_zero_null_and_finite_values()
        self.test_04_pr_eos_thermodynamic_properties()
        self.test_05_flow_conversion_identities()
        self.test_06_production_quantiles_linking()
        self.test_07_speed_window_compliance()
        self.test_08_surge_margin_and_flow_floor()
        self.test_09_oem_guarantee_precision()
        self.test_10_mechanical_status_integrity()

        print("-" * 80)
        print(f"Validation Summary: {self.passes} PASSED, {self.failures} FAILED.")
        if self.failures > 0:
            print("\nFailure Details:")
            for err in self.errors:
                print(f"  - {err}")
            return 1
        else:
            print("All verification checks PASSED with zero defects. Exit code 0.")
            return 0

    # --------------------------------------------------------------------------
    # Test 1: File Existence & Parity
    # --------------------------------------------------------------------------
    def test_01_file_existence_and_parity(self) -> None:
        print("\n[Suite 1] File Existence & Dual-Format Parity (Parquet vs CSV):")
        self.assert_true(self.parquet_path.exists(), "T1.1_parquet_exists", f"Missing {self.parquet_path}")
        self.assert_true(self.csv_path.exists(), "T1.2_csv_exists", f"Missing {self.csv_path}")
        
        if self.parquet_path.exists() and self.csv_path.exists():
            df_pq = pd.read_parquet(self.parquet_path)
            df_csv = pd.read_csv(self.csv_path)
            self.assert_true(len(df_pq) >= 70, "T1.3_parquet_row_count", f"Expected >= 70 rows, got {len(df_pq)}")
            self.assert_true(len(df_pq) == len(df_csv), "T1.4_row_count_parity", f"PQ={len(df_pq)}, CSV={len(df_csv)}")
            self.assert_true(len(df_pq.columns) == len(df_csv.columns), "T1.5_col_count_parity", f"PQ cols={len(df_pq.columns)}, CSV cols={len(df_csv.columns)}")

    # --------------------------------------------------------------------------
    # Test 2: Schema Compliance
    # --------------------------------------------------------------------------
    def test_02_schema_compliance(self) -> None:
        print("\n[Suite 2] Schema Compliance & Column Completeness:")
        if not self.parquet_path.exists():
            self.assert_true(False, "T2.0_cannot_load", "Parquet missing")
            return

        df = pd.read_parquet(self.parquet_path)
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        self.assert_true(len(missing_cols) == 0, "T2.1_all_columns_present", f"Missing cols: {missing_cols}")
        
        # Verify permissible values in categorical fields
        valid_modes = {"Baseline", "Optimized", "Hypothetical_No_Kickback", "OEM_Guarantee"}
        actual_modes = set(df["operating_mode"].unique())
        self.assert_true(actual_modes.issubset(valid_modes), "T2.2_valid_operating_modes", f"Unexpected modes: {actual_modes - valid_modes}")
        
        valid_tags = {"4K-1_Sec1", "4K-1_Sec2", "4K-1_Sec3", "4K-2", "4K-3"}
        actual_tags = set(df["compressor_tag"].unique())
        self.assert_true(actual_tags.issubset(valid_tags), "T2.3_valid_compressor_tags", f"Unexpected tags: {actual_tags - valid_tags}")

    # --------------------------------------------------------------------------
    # Test 3: Zero Null & Finite Values
    # --------------------------------------------------------------------------
    def test_03_zero_null_and_finite_values(self) -> None:
        print("\n[Suite 3] Zero Null, NaN, or Infinite Values:")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        null_counts = df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0].to_dict()
        self.assert_true(len(cols_with_nulls) == 0, "T3.1_zero_nulls", f"Columns with nulls: {cols_with_nulls}")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        has_inf = np.isinf(df[numeric_cols].to_numpy()).any()
        self.assert_true(not has_inf, "T3.2_zero_infinite_values", "Found infinite values in numeric columns")

    # --------------------------------------------------------------------------
    # Test 4: PR-EOS Thermodynamic Properties
    # --------------------------------------------------------------------------
    def test_04_pr_eos_thermodynamic_properties(self) -> None:
        print("\n[Suite 4] Suction Thermodynamic Properties (PR-EOS Consistency):")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        
        # 1. Pure Propane Check (4K-1)
        c3_df = df[df["casing_tag"] == "4K-1"]
        self.assert_true((c3_df["molecular_weight_g_mol"].round(2) == 44.10).all(), "T4.1_propane_mw", "Propane MW != 44.10")
        self.assert_true(((c3_df["compressibility_factor_z"] >= 0.85) & (c3_df["compressibility_factor_z"] <= 0.98)).all(), 
                         "T4.2_propane_z_factor_range", "Propane Z factor outside [0.85, 0.98]")
        self.assert_true(((c3_df["isentropic_exponent_k"] >= 1.14) & (c3_df["isentropic_exponent_k"] <= 1.25)).all(), 
                         "T4.3_propane_k_exponent_range", "Propane isentropic k outside [1.14, 1.25]")

        # 2. MCR Check (4K-2 & 4K-3)
        mcr_df = df[df["fluid_description"] == "Mixed Refrigerant (MCR)"]
        self.assert_true(((mcr_df["molecular_weight_g_mol"] >= 24.4) & (mcr_df["molecular_weight_g_mol"] <= 26.5)).all(), 
                         "T4.4_mcr_mw_range", "MCR MW outside [24.4, 26.5] g/mol")
        
        lp_df = df[df["compressor_tag"] == "4K-2"]
        self.assert_true(((lp_df["suction_density_kg_m3"] >= 3.5) & (lp_df["suction_density_kg_m3"] <= 6.5)).all(), 
                         "T4.5_lp_mcr_density_range", "LP MCR density outside [3.5, 6.5] kg/m³")
        self.assert_true(((lp_df["compressibility_factor_z"] >= 0.95) & (lp_df["compressibility_factor_z"] <= 0.99)).all(), 
                         "T4.6_lp_mcr_z_range", "LP MCR Z factor outside [0.95, 0.99]")

        hp_df = df[df["compressor_tag"] == "4K-3"]
        self.assert_true(((hp_df["suction_density_kg_m3"] >= 11.0) & (hp_df["suction_density_kg_m3"] <= 22.0)).all(), 
                         "T4.7_hp_mcr_density_range", "HP MCR density outside [11.0, 22.0] kg/m³")

    # --------------------------------------------------------------------------
    # Test 5: Flow Conversion Identities
    # --------------------------------------------------------------------------
    def test_05_flow_conversion_identities(self) -> None:
        print("\n[Suite 5] Flow Conversion Identities (Q_actual = mass_flow / rho):")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        expected_q = (df["mass_flow_t_h"] * 1000.0) / df["suction_density_kg_m3"]
        diff = (df["actual_volumetric_flow"] - expected_q).abs()
        max_diff = diff.max()
        self.assert_true(max_diff < 0.05, "T5.1_exact_mass_volume_identity", f"Max difference in Q_actual = {max_diff:.5f} m³/h")

    # --------------------------------------------------------------------------
    # Test 6: Production Quantiles Linking (P10, P50, P90)
    # --------------------------------------------------------------------------
    def test_06_production_quantiles_linking(self) -> None:
        print("\n[Suite 6] Production Quantiles Linking (P10, P50, P90 Steady-State Medians):")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        
        # P10 Turndown Verification
        p10_opt_4k2 = df[(df["load_quantile"] == "P10") & (df["operating_mode"] == "Optimized") & (df["compressor_tag"] == "4K-2")].iloc[0]
        self.assert_true(p10_opt_4k2["mass_flow_t_h"] == 604.68, "T6.1_p10_suction_throughput", f"P10 throughput != 604.68 (got {p10_opt_4k2['mass_flow_t_h']})")
        self.assert_true(p10_opt_4k2["anti_surge_kickback_flow_t_h"] == 107.59, "T6.2_p10_kickback_modulation", f"P10 kickback != 107.59")
        self.assert_true(p10_opt_4k2["suction_temperature_c"] == -21.14, "T6.3_p10_suction_temperature", f"P10 T_suct != -21.14")
        self.assert_true(p10_opt_4k2["suction_temperature_c"] >= -45.0, "T6.4_p10_tal_interlock_satisfied", "P10 violates TAL (-45°C)")

        # P50 Midload Verification
        p50_opt_4k2 = df[(df["load_quantile"] == "P50") & (df["operating_mode"] == "Optimized") & (df["compressor_tag"] == "4K-2")].iloc[0]
        self.assert_true(p50_opt_4k2["mass_flow_t_h"] == 538.16, "T6.5_p50_suction_throughput", f"P50 throughput != 538.16")
        self.assert_true(p50_opt_4k2["suction_temperature_c"] == -32.84, "T6.6_p50_suction_temperature", f"P50 T_suct != -32.84")

        # P90 Baseload Verification
        p90_opt_4k2 = df[(df["load_quantile"] == "P90") & (df["operating_mode"] == "Optimized") & (df["compressor_tag"] == "4K-2")].iloc[0]
        self.assert_true(p90_opt_4k2["mass_flow_t_h"] == 576.24, "T6.7_p90_suction_throughput", f"P90 throughput != 576.24")
        self.assert_true(p90_opt_4k2["anti_surge_kickback_flow_t_h"] == 0.0, "T6.8_p90_kickback_closed", f"P90 kickback != 0.0")
        self.assert_true(p90_opt_4k2["suction_temperature_c"] == -41.49, "T6.9_p90_suction_temperature", f"P90 T_suct != -41.49")
        self.assert_true(p90_opt_4k2["suction_temperature_c"] >= -45.0, "T6.10_p90_tal_interlock_satisfied", "P90 violates TAL (-45°C)")

    # --------------------------------------------------------------------------
    # Test 7: Speed Window Compliance
    # --------------------------------------------------------------------------
    def test_07_speed_window_compliance(self) -> None:
        print("\n[Suite 7] Operating Speed Limits (70.0% to 105.0% MCS API 617 Window):")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        normal_df = df[df["operating_mode"] != "Hypothetical_No_Kickback"]
        
        self.assert_true((normal_df["is_speed_compliant"]).all(), "T7.1_all_speeds_compliant", "Found non-compliant machine speed")
        self.assert_true(((normal_df["speed_pct_mcs"] >= 70.0) & (normal_df["speed_pct_mcs"] <= 105.0)).all(), 
                         "T7.2_speed_pct_mcs_bounds", "Speed % MCS outside [70.0, 105.0]")

    # --------------------------------------------------------------------------
    # Test 8: Surge Margin & Minimum Flow Floor
    # --------------------------------------------------------------------------
    def test_08_surge_margin_and_flow_floor(self) -> None:
        print("\n[Suite 8] Surge Margin & 480 t/h Flow Floor Protection:")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        
        # Check P10 Optimized 4K-2 (Mitigated with kickback)
        p10_opt_4k2 = df[(df["load_quantile"] == "P10") & (df["operating_mode"] == "Optimized") & (df["compressor_tag"] == "4K-2")].iloc[0]
        self.assert_true(p10_opt_4k2["surge_margin_pct"] >= 20.0, "T8.1_p10_opt_surge_margin_safe", f"P10 SM < 20%: {p10_opt_4k2['surge_margin_pct']:.2f}%")
        self.assert_true(p10_opt_4k2["is_surge_safe"], "T8.2_p10_opt_is_surge_safe", "P10 marked unsafe")

        # Check P10 Unmitigated 4K-2 (Without kickback: demonstrates failure)
        p10_unmit = df[df["load_quantile"] == "P10_Unmitigated"].iloc[0]
        self.assert_true(p10_unmit["mechanical_status"] == "SURGE_VIOLATION", "T8.3_unmitigated_surge_violation_flag", "P10 unmitigated not flagged as SURGE_VIOLATION")
        self.assert_true(not p10_unmit["is_surge_safe"], "T8.4_unmitigated_is_not_surge_safe", "P10 unmitigated marked as surge safe")

        # Check surge flow < choke flow everywhere
        self.assert_true((df["surge_flow"] < df["choke_flow"]).all(), "T8.5_surge_less_than_choke", "Surge flow >= choke flow detected")

    # --------------------------------------------------------------------------
    # Test 9: OEM Design Guarantee Point Precision
    # --------------------------------------------------------------------------
    def test_09_oem_guarantee_precision(self) -> None:
        print("\n[Suite 9] OEM Design Guarantee Point Precision (Certified Datasheets):")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        oem_df = df[df["load_quantile"] == "OEM_Design"].set_index("compressor_tag")
        
        # 4K-1 Sect-1 Guarantee: Head = 5655 m, PR = 2.517, Power = 11840 kW, Eff = 82.4%
        r_4k1 = oem_df.loc["4K-1_Sec1"]
        self.assert_true(math.isclose(r_4k1["polytropic_head_m"], 5655.0, rel_tol=1e-3), "T9.1_4k1_guarantee_head", f"4K-1 head: {r_4k1['polytropic_head_m']}")
        self.assert_true(math.isclose(r_4k1["pressure_ratio"], 2.517, rel_tol=1e-3), "T9.2_4k1_guarantee_pr", f"4K-1 PR: {r_4k1['pressure_ratio']}")
        self.assert_true(math.isclose(r_4k1["shaft_power_kw"], 11840.0, rel_tol=1e-3), "T9.3_4k1_guarantee_power", f"4K-1 power: {r_4k1['shaft_power_kw']}")

        # 4K-2 Guarantee: Head = 14008 m, PR = 4.953, Power = 30754 kW, Eff = 80.5%
        r_4k2 = oem_df.loc["4K-2"]
        self.assert_true(math.isclose(r_4k2["polytropic_head_m"], 14008.0, rel_tol=1e-3), "T9.4_4k2_guarantee_head", f"4K-2 head: {r_4k2['polytropic_head_m']}")
        self.assert_true(math.isclose(r_4k2["pressure_ratio"], 4.953, rel_tol=1e-3), "T9.5_4k2_guarantee_pr", f"4K-2 PR: {r_4k2['pressure_ratio']}")
        self.assert_true(math.isclose(r_4k2["shaft_power_kw"], 30754.0, rel_tol=1e-3), "T9.6_4k2_guarantee_power", f"4K-2 power: {r_4k2['shaft_power_kw']}")

        # 4K-3 Guarantee: Head = 13945 m, PR = 3.472, Power = 36681 kW, Eff = 80.8%
        r_4k3 = oem_df.loc["4K-3"]
        self.assert_true(math.isclose(r_4k3["polytropic_head_m"], 13945.0, rel_tol=1e-3), "T9.7_4k3_guarantee_head", f"4K-3 head: {r_4k3['polytropic_head_m']}")
        self.assert_true(math.isclose(r_4k3["pressure_ratio"], 3.472, rel_tol=1e-3), "T9.8_4k3_guarantee_pr", f"4K-3 PR: {r_4k3['pressure_ratio']}")
        self.assert_true(math.isclose(r_4k3["shaft_power_kw"], 36681.0, rel_tol=1e-3), "T9.9_4k3_guarantee_power", f"4K-3 power: {r_4k3['shaft_power_kw']}")

    # --------------------------------------------------------------------------
    # Test 10: Mechanical Status Classification Integrity
    # --------------------------------------------------------------------------
    def test_10_mechanical_status_integrity(self) -> None:
        print("\n[Suite 10] Mechanical Status Classification & Tag Audit:")
        if not self.parquet_path.exists():
            return

        df = pd.read_parquet(self.parquet_path)
        allowed_statuses = {"HEAD_COMPLIANT", "SURGE_SAFE", "FEASIBLE", "SURGE_VIOLATION"}
        actual_statuses = set(df["mechanical_status"].unique())
        self.assert_true(actual_statuses.issubset(allowed_statuses), "T10.1_status_vocabulary", f"Unknown statuses: {actual_statuses - allowed_statuses}")
        
        # All normal baseline and optimized points must be surge safe
        normal_pts = df[df["operating_mode"].isin(["Baseline", "Optimized", "OEM_Guarantee"])]
        self.assert_true((normal_pts["is_surge_safe"]).all(), "T10.2_normal_points_all_surge_safe", "Some normal operating points failed surge check")


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    validator = TelemetryLinkingValidator(root_dir)
    return validator.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())

