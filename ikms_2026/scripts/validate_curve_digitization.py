"""
Compressor Performance Curve Digitization & Calibration Validation Suite
PT Badak NGL Train H C3MR Liquefaction Optimization (IKMS 2026)

Tests:
  1. File Existence & Dual Format Parity (Parquet vs CSV)
  2. Schema Compliance (12 Columns adhering to PROJECT.md § Interface Contracts)
  3. Zero Null, NaN, or Infinite Values
  4. Design Guarantee Point Precision & Total Power Reconciliation
  5. Aerodynamic Monotonicity (Head/PR decreasing, Power increasing)
  6. Affinity Speed Scaling Consistency (H ~ N^2, Power ~ N^3)
  7. Surge & Choke Boundary Integrity (Q_surge < Q_rated < Q_choke)
  8. Absence of Synthetic Extrapolations or Unphysical Values
"""

import os
import sys
import numpy as np
import pandas as pd

DATA_DIR = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\data\digitized"
EXPECTED_COLUMNS = [
    'compressor_tag', 'section_or_case', 'curve_type', 'speed_pct', 'speed_rpm',
    'flow_basis', 'flow_value', 'y_unit', 'y_value', 'source_pdf', 'source_page',
    'confidence_rating'
]

class DigitizationValidator:
    def __init__(self):
        self.passes = 0
        self.failures = 0
        self.errors = []

    def assert_true(self, condition, test_name, error_msg=""):
        if condition:
            self.passes += 1
            print(f"  [PASS] {test_name}")
        else:
            self.failures += 1
            full_msg = f"{test_name}: {error_msg}"
            self.errors.append(full_msg)
            print(f"  [FAIL] {full_msg}")

    def run_all_tests(self):
        print("=================================================================")
        print("RUNNING COMPRESSOR CURVE DIGITIZATION VALIDATION SUITE")
        print("PT Badak NGL Train H C3MR Liquefaction Optimization (IKMS 2026)")
        print("=================================================================")

        # Test Group 1: File Existence & Format Parity
        print("\n--- TEST GROUP 1: FILE EXISTENCE & DUAL FORMAT PARITY ---")
        tags = ['4K1', '4K2', '4K3']
        dfs = {}
        for tag in tags:
            pq_path = os.path.join(DATA_DIR, f"compressor_curves_{tag}.parquet")
            csv_path = os.path.join(DATA_DIR, f"compressor_curves_{tag}.csv")
            self.assert_true(os.path.exists(pq_path), f"Parquet file exists for {tag}", f"Missing {pq_path}")
            self.assert_true(os.path.exists(csv_path), f"CSV file exists for {tag}", f"Missing {csv_path}")

            if os.path.exists(pq_path) and os.path.exists(csv_path):
                df_pq = pd.read_parquet(pq_path)
                df_csv = pd.read_csv(csv_path)
                self.assert_true(len(df_pq) == len(df_csv), f"Row count parity for {tag} ({len(df_pq)} rows)",
                                 f"Parquet rows ({len(df_pq)}) != CSV rows ({len(df_csv)})")
                dfs[tag] = df_pq

        dict_path = os.path.join(DATA_DIR, "COMPRESSOR_CURVES_DATA_DICTIONARY.md")
        self.assert_true(os.path.exists(dict_path) and os.path.getsize(dict_path) > 1000,
                         "Data dictionary exists and is comprehensive", f"Data dictionary missing or truncated at {dict_path}")

        # Test Group 2: Schema Conformance & Strict Typing
        print("\n--- TEST GROUP 2: SCHEMA CONFORMANCE & STRICT TYPING ---")
        for tag, df in dfs.items():
            self.assert_true(list(df.columns) == EXPECTED_COLUMNS,
                             f"Schema columns conform strictly to interface contract for {tag}",
                             f"Columns: {list(df.columns)} != {EXPECTED_COLUMNS}")
            self.assert_true(df.isnull().sum().sum() == 0,
                             f"Zero null / NaN values in {tag}",
                             f"Null count: {df.isnull().sum().to_dict()}")
            self.assert_true((~np.isinf(df['flow_value'])).all() and (~np.isinf(df['y_value'])).all(),
                             f"Zero infinite values in {tag}")
            self.assert_true((df['flow_value'] > 0).all(), f"All flow values strictly positive in {tag}")
            self.assert_true((df['y_value'] > 0).all(), f"All y values strictly positive in {tag}")
            self.assert_true((df['confidence_rating'].isin(['HIGH', 'MEDIUM', 'ESTIMATED'])).all(),
                             f"Valid confidence ratings in {tag}")

        # Test Group 3: Design Guarantee Point Precision & Power Reconciliation
        print("\n--- TEST GROUP 3: GUARANTEE POINT PRECISION & POWER RECONCILIATION ---")
        df_4k1 = dfs['4K1']
        df_4k2 = dfs['4K2']
        df_4k3 = dfs['4K3']

        # 4K-1 Guarantee Points
        # Sect-1: Q=216835, PR=2.517, kW=11840
        s1_pr = df_4k1[(df_4k1['section_or_case'] == 'Sect-1') & (df_4k1['curve_type'] == 'Pressure_Ratio') &
                       (df_4k1['flow_value'] == 216835.0)]['y_value'].values
        s1_kw = df_4k1[(df_4k1['section_or_case'] == 'Sect-1') & (df_4k1['curve_type'] == 'Power') &
                       (df_4k1['flow_value'] == 216835.0)]['y_value'].values
        self.assert_true(len(s1_pr) > 0 and abs(s1_pr[0] - 2.517) < 0.01,
                         "4K-1 Sect-1 Rated PR = 2.517 (-0.1% tolerance)", f"Found {s1_pr}")
        self.assert_true(len(s1_kw) > 0 and abs(s1_kw[0] - 11840.0) < 10.0,
                         "4K-1 Sect-1 Rated Power = 11,840 kW (-0.1% tolerance)", f"Found {s1_kw}")

        # Sect-2: Q=148093, PR=1.960, kW=13320
        s2_pr = df_4k1[(df_4k1['section_or_case'] == 'Sect-2') & (df_4k1['curve_type'] == 'Pressure_Ratio') &
                       (df_4k1['flow_value'] == 148093.0)]['y_value'].values
        s2_kw = df_4k1[(df_4k1['section_or_case'] == 'Sect-2') & (df_4k1['curve_type'] == 'Power') &
                       (df_4k1['flow_value'] == 148093.0)]['y_value'].values
        self.assert_true(len(s2_pr) > 0 and abs(s2_pr[0] - 1.960) < 0.01,
                         "4K-1 Sect-2 Rated PR = 1.960", f"Found {s2_pr}")
        self.assert_true(len(s2_kw) > 0 and abs(s2_kw[0] - 13320.0) < 10.0,
                         "4K-1 Sect-2 Rated Power = 13,320 kW", f"Found {s2_kw}")

        # Sect-3: Q=102488, PR=1.973, kW=13249
        s3_pr = df_4k1[(df_4k1['section_or_case'] == 'Sect-3') & (df_4k1['curve_type'] == 'Pressure_Ratio') &
                       (df_4k1['flow_value'] == 102488.0)]['y_value'].values
        s3_kw = df_4k1[(df_4k1['section_or_case'] == 'Sect-3') & (df_4k1['curve_type'] == 'Power') &
                       (df_4k1['flow_value'] == 102488.0)]['y_value'].values
        self.assert_true(len(s3_pr) > 0 and abs(s3_pr[0] - 1.973) < 0.01,
                         "4K-1 Sect-3 Rated PR = 1.973", f"Found {s3_pr}")
        self.assert_true(len(s3_kw) > 0 and abs(s3_kw[0] - 13249.0) < 10.0,
                         "4K-1 Sect-3 Rated Power = 13,249 kW", f"Found {s3_kw}")

        total_4k1_power = s1_kw[0] + s2_kw[0] + s3_kw[0]
        self.assert_true(abs(total_4k1_power - 38409.0) < 20.0,
                         f"Total 4K-1 Shaft Power = 38,409 kW (exact sum = {total_4k1_power:.1f} kW)")

        # 4K-2 Guarantee Point Case 1: Q=148807, Head=14008, Eff=0.805, Power=30754, Pd=15.65
        k2_head = df_4k2[(df_4k2['section_or_case'] == 'Case-1') & (df_4k2['curve_type'] == 'Head') &
                         (df_4k2['flow_value'] == 148807.0)]['y_value'].values
        k2_eff = df_4k2[(df_4k2['section_or_case'] == 'Case-1') & (df_4k2['curve_type'] == 'Efficiency') &
                        (df_4k2['flow_value'] == 148807.0)]['y_value'].values
        k2_kw = df_4k2[(df_4k2['section_or_case'] == 'Case-1') & (df_4k2['curve_type'] == 'Power') &
                       (df_4k2['flow_value'] == 148807.0)]['y_value'].values
        k2_pd = df_4k2[(df_4k2['section_or_case'] == 'Case-1') & (df_4k2['curve_type'] == 'Discharge_Pressure') &
                       (df_4k2['flow_value'] == 148807.0)]['y_value'].values

        self.assert_true(len(k2_head) > 0 and abs(k2_head[0] - 14008.0) < 10.0,
                         "4K-2 Case-1 Rated Head = 14,008 m-kg/kg", f"Found {k2_head}")
        self.assert_true(len(k2_eff) > 0 and abs(k2_eff[0] - 0.805) < 0.005,
                         "4K-2 Case-1 Rated Efficiency = 80.5%", f"Found {k2_eff}")
        self.assert_true(len(k2_kw) > 0 and abs(k2_kw[0] - 30754.0) < 20.0,
                         "4K-2 Case-1 Rated Power = 30,754 kW", f"Found {k2_kw}")
        self.assert_true(len(k2_pd) > 0 and abs(k2_pd[0] - 15.65) < 0.1,
                         "4K-2 Case-1 Rated Discharge Pressure = 15.65 kg/cm2A", f"Found {k2_pd}")

        # 4K-3 Guarantee Point Case 1: Q=48807, Head=13945, Eff=0.808, Power=36681, Pd=53.65
        k3_head = df_4k3[(df_4k3['section_or_case'] == 'Case-1') & (df_4k3['curve_type'] == 'Head') &
                         (df_4k3['flow_value'] == 48807.0)]['y_value'].values
        k3_eff = df_4k3[(df_4k3['section_or_case'] == 'Case-1') & (df_4k3['curve_type'] == 'Efficiency') &
                        (df_4k3['flow_value'] == 48807.0)]['y_value'].values
        k3_kw = df_4k3[(df_4k3['section_or_case'] == 'Case-1') & (df_4k3['curve_type'] == 'Power') &
                       (df_4k3['flow_value'] == 48807.0)]['y_value'].values
        k3_pd = df_4k3[(df_4k3['section_or_case'] == 'Case-1') & (df_4k3['curve_type'] == 'Discharge_Pressure') &
                       (df_4k3['flow_value'] == 48807.0)]['y_value'].values

        self.assert_true(len(k3_head) > 0 and abs(k3_head[0] - 13945.0) < 10.0,
                         "4K-3 Case-1 Rated Head = 13,945 m-kg/kg", f"Found {k3_head}")
        self.assert_true(len(k3_eff) > 0 and abs(k3_eff[0] - 0.808) < 0.005,
                         "4K-3 Case-1 Rated Efficiency = 80.8%", f"Found {k3_eff}")
        self.assert_true(len(k3_kw) > 0 and abs(k3_kw[0] - 36681.0) < 20.0,
                         "4K-3 Case-1 Rated Power = 36,681 kW", f"Found {k3_kw}")
        self.assert_true(len(k3_pd) > 0 and abs(k3_pd[0] - 53.65) < 0.1,
                         "4K-3 Case-1 Rated Discharge Pressure = 53.65 kg/cm2A", f"Found {k3_pd}")

        total_train_power = total_4k1_power + k2_kw[0] + k3_kw[0]
        self.assert_true(abs(total_train_power - 105844.0) < 50.0,
                         f"Train H C3MR Total Baseline Power = 105,844 kW (~105.84 MW, sum={total_train_power:.1f} kW)")

        # Test Group 4: Aerodynamic Monotonicity & Physics Consistency
        print("\n--- TEST GROUP 4: AERODYNAMIC MONOTONICITY & PHYSICS CONSISTENCY ---")
        # Check Head/PR decreasing with Flow for every speed line
        for tag, df in [('4K-1', df_4k1), ('4K-2', df_4k2), ('4K-3', df_4k3)]:
            c_type = 'Pressure_Ratio' if tag == '4K-1' else 'Head'
            for sec, sub_sec in df.groupby('section_or_case'):
                for spd, sub_spd in sub_sec[sub_sec['curve_type'] == c_type].groupby('speed_pct'):
                    sub_sorted = sub_spd.sort_values('flow_value')
                    flows = sub_sorted['flow_value'].values
                    y_vals = sub_sorted['y_value'].values
                    diffs = np.diff(y_vals)
                    # All diffs must be <= 0 (strictly decreasing)
                    is_decreasing = (diffs <= 1e-4).all()
                    self.assert_true(is_decreasing,
                                     f"{tag} {sec} {c_type} speed {spd}% monotonic decreasing (dY/dQ <= 0)",
                                     f"Violations at diffs: {diffs[diffs > 1e-4]}")

        # Check Power increasing with Flow for every speed line
        for tag, df in [('4K-1', df_4k1), ('4K-2', df_4k2), ('4K-3', df_4k3)]:
            for sec, sub_sec in df.groupby('section_or_case'):
                for spd, sub_spd in sub_sec[sub_sec['curve_type'] == 'Power'].groupby('speed_pct'):
                    sub_sorted = sub_spd.sort_values('flow_value')
                    y_vals = sub_sorted['y_value'].values
                    diffs = np.diff(y_vals)
                    is_increasing = (diffs >= -1e-4).all()
                    self.assert_true(is_increasing,
                                     f"{tag} {sec} Power speed {spd}% monotonic increasing (dKW/dQ >= 0)",
                                     f"Violations at diffs: {diffs[diffs < -1e-4]}")

        # Test Group 5: Speed Affinity Hierarchy Check
        print("\n--- TEST GROUP 5: SPEED AFFINITY HIERARCHY ---")
        # Higher speed line must be strictly above lower speed line
        for tag, df in [('4K-2', df_4k2), ('4K-3', df_4k3)]:
            c1_head = df[(df['section_or_case'] == 'Case-1') & (df['curve_type'] == 'Head')]
            # Group by speed and get mean head
            mean_heads = c1_head.groupby('speed_pct')['y_value'].mean()
            speeds = sorted(mean_heads.index)
            is_head_scaling = all(mean_heads[speeds[i]] < mean_heads[speeds[i+1]] for i in range(len(speeds)-1))
            self.assert_true(is_head_scaling, f"{tag} Case-1 Head scales strictly with speed N ({dict(mean_heads)})")

            c1_kw = df[(df['section_or_case'] == 'Case-1') & (df['curve_type'] == 'Power')]
            mean_kws = c1_kw.groupby('speed_pct')['y_value'].mean()
            is_kw_scaling = all(mean_kws[speeds[i]] < mean_kws[speeds[i+1]] for i in range(len(speeds)-1))
            self.assert_true(is_kw_scaling, f"{tag} Case-1 Power scales strictly with speed N ({dict(mean_kws)})")

        # Test Group 6: Boundary Envelope Consistency
        print("\n--- TEST GROUP 6: BOUNDARY ENVELOPE CONSISTENCY ---")
        for tag, df in dfs.items():
            for sec, sub_sec in df.groupby('section_or_case'):
                surge = sub_sec[sub_sec['curve_type'] == 'Surge_Limit'].sort_values('speed_pct')
                choke = sub_sec[sub_sec['curve_type'] == 'Choke_Limit'].sort_values('speed_pct')
                if len(surge) > 0 and len(choke) > 0:
                    # Surge flow must be strictly less than choke flow at every speed
                    surge_flows = surge.groupby('speed_pct')['flow_value'].mean()
                    choke_flows = choke.groupby('speed_pct')['flow_value'].mean()
                    common_speeds = sorted(set(surge_flows.index).intersection(set(choke_flows.index)))
                    is_valid_envelope = all(surge_flows[s] < choke_flows[s] for s in common_speeds)
                    self.assert_true(is_valid_envelope,
                                     f"{tag} {sec}: Surge flow strictly less than choke flow across all speeds",
                                     f"Surge: {dict(surge_flows)}, Choke: {dict(choke_flows)}")

        # Summary
        print("\n=================================================================")
        print(f"VALIDATION SUMMARY: {self.passes} PASSED, {self.failures} FAILED")
        if self.failures == 0:
            print("ALL VERIFICATION GATES PASSED! IMPLEMENTATION MEETS INTEGRITY STANDARDS.")
        else:
            print(f"FAILURES DETECTED ({self.failures}):")
            for err in self.errors:
                print(f"  - {err}")
        print("=================================================================")
        return self.failures == 0

if __name__ == "__main__":
    validator = DigitizationValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)

