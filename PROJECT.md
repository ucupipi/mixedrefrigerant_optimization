# Project: Badak LNG Plant-3 Train H C3MR Compressor Performance Curve Digitization & ML Optimization Suite (IKMS 2026)

## Architecture
This project integrates OEM compressor performance curves for 4K-1, 4K-2, and 4K-3 (Dresser-Rand 939B6/4, 838B4, 656B7-6) with historical DCS telemetry (720,734 records, 2,531 GC routine samples), rigorous PR-EOS thermodynamic simulation, and machine learning surrogate models into a verified optimization framework for Train H liquefaction at PT Badak NGL.

The architecture decouples modeling into three distinct layers conforming strictly to `AGENTS.md` (Pasal 1 to Pasal 13):
1. **Domain 1 — PR-EOS Thermodynamic Surrogates (Deterministic Physics):**
   - High-fidelity surrogate models trained on 2,000 Latin Hypercube Sampling (LHS) DoE simulation points.
   - Predicts internal unmeasurable thermodynamic variables: Warm Bundle Pinch ($\text{MITA}_{\text{WB}}$), Cold Bundle Pinch ($\text{MITA}_{\text{CB}}$), Isentropic Shaft Power ($\dot{W}_{\text{shaft}}$), and MCHE Exergy Destruction ($\dot{E}_{D, \text{MCHE}}$).
   - Metrics: $R^2 \ge 0.989$, $\text{MAE} < 0.2\text{ MW}$ (proportional unit), $\text{NMAE} < 0.2\%$, with physics monotonicity constraints ($\text{monotonic\_cst} = +1$).
2. **Domain 2 — DCS Operational Telemetry Surrogates (Field Stochastic Sensor Models):**
   - Empirical machine learning models trained on 67,916 steady-state chronological minutes (2025–2026).
   - Predicts plant utility steam ($m_{\text{steam}}$), suction drum mixed temperature ($T_{\text{suct}}$ / `H4TI004B`), and turbine driver condensate flows (`H4FI031A`, `H4FI029A`, `H4FI030A`).
   - Metrics: Realistic industrial $R^2 \approx 0.8419\text{--}0.9664$, $\text{NMAE} < 1.0\%$.
3. **Deterministic Physical Post-Processing & Boundary Validation Layer:**
   - Computes deterministic variables via exact algebraic mass/energy balances without ML models: Specific Energy Consumption ($\text{SEC} = \dot{W}_{\text{shaft}} / \dot{m}_{\text{LNG}}$), Boiler Fuel Gas Demand ($\dot{V}_{\text{FG}} = \dot{m}_{\text{steam}} \times 97.70\text{ Nm}^3/\text{t}$), Scope 1 $\text{CO}_2$ emissions, and suction drum flow balance ($\dot{m}_{\text{comp}} = \dot{m}_{\text{MCHE}} + \dot{m}_{\text{4UV-53}} + \dot{m}_{\text{4TV-510}}$).
   - Digitized OEM Compressor Performance Curves (4K-1, 4K-2, 4K-3) provide explicit operating envelope boundaries (surge limit, stonewall/choke, minimum flow floor $\ge 480.0\text{ t/h}$, speed window 70%–105% MCS) and independent aerodynamic validation.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|:---:|:---:|
| 1 | ML Lineage & Dataset Catalog | Complete lineage table mapping every target to script, dataset, split method, and ground truth source | M1 | Survey 1 |
| 2 | Metric Reproduction & Dual-Domain Validation | Reproduce R², MAE (in MW), RMSE, NMAE on holdout test sets without data leakage | M1 | Survey 1 |
| 3 | Target Decoupling (Deterministic Balances) | Decouple SEC, Boiler Fuel Gas (V_FG), and CO2 from ML into exact physical algebraic balances | M1 | Survey 1 |
| 4 | Audit of R² ≈ 0.99 Claims | Reconcile legacy random-split temporal leakage vs authentic dual-domain metrics | M1 | Survey 1 |
| 5 | Steam Meter Metadata Verification | Confirm H4FI030A/029A/031A as 4G-5/4/3 condensate pump discharges from 4KT-3/2/1 surface condensers | M1 | Survey 1, Survey 3 |
| 6 | 4K-1 Curve Extraction & Digitization | Digitize Dresser-Rand 939B6/4 propane compressor curves (PR & kW vs AM³/HR for Sections 1, 2, 3) | M2 | Survey 2 |
| 7 | 4K-2 Curve Extraction & Digitization | Digitize Dresser-Rand 838B4 LP MCR compressor curves (Head, Eff, kW, Pd vs m³/h for Cases 1, 2, 3) | M2 | Survey 2 |
| 8 | 4K-3 Curve Extraction & Digitization | Digitize Dresser-Rand 656B7-6 HP MCR compressor curves (Head, Eff, kW, Pd vs m³/h for Cases 1, 2, 3) | M2 | Survey 2 |
| 9 | Curve Calibration & Data Dictionary | Calibrate axes from original tick marks; produce CSV/Parquet with confidence ratings and dictionary | M2 | Survey 2 |
| 10 | Historical DCS Telemetry Linking | Map historical steady-state operating points across full 100 percentiles (P1 to P100) and 7 anchor quantiles (P10 to P90) onto curves | M3 | Survey 3 |
| 11 | Suction Thermodynamic Conversions | Compute suction Z, k, density via PR-EOS to convert mass flow into OEM actual volumetric flow | M3 | Survey 3 |
| 12 | Operating Envelope & Surge Verification | Project baseline vs candidate optimum MR operating points onto curves; verify surge margins | M4 | Survey 2, Survey 3 |
| 13 | 480 t/h Floor & 4UV-53 / 4TV-510 Enforcement | Verify anti-surge kickback modulation (107.6 t/h at P10) and TAL (-45°C) superheated vapor | M4 | Survey 3 |
| 14 | Thermodynamic Feasibility & Power Decomposition | Verify candidate optimum MR recipe ($D_M = 1.2723 \le 3.0802$) and -27.10% power decomposition | M4 | Survey 3 |
| 15 | Publication Visualizations (Figures 1–5) | High-resolution publication plots of operating maps, baseline vs optimized points, and power/head | M5 | Survey 2, Survey 3 |
| 16 | Standalone Technical Reports | Generate ML Audit Report, Target Selection Report, Compressor Evaluation Report, Integration Report | M5 | Survey 1, Survey 2, Survey 3 |
| 17 | IKMS 2026 Paper Revision Draft | Produce manuscript revision text, tables, and figure citations conforming to AGENTS.md rules | M5 | Survey 1, Survey 2, Survey 3 |
| 18 | Standalone Reproducible Validation Scripts | Standalone scripts to verify digitization, thermodynamic conversions, and evaluation metrics | M5 | Survey 1, Survey 2, Survey 3 |

---

## Milestones
| # | Milestone Name | Scope | Dependencies | Status | Key Outputs |
|---|---|---|:---:|:---:|---|
| M1 | Baseline and Optimized Case Reconstruction (P1-P100 + 7 Anchors) | Reconstruct baseline operating points across all 100 percentiles (P1 to P100) and 7 anchor quantiles (P10 to P90) under strict throughput parity from primary source data; train ML surrogates and optimize via SLSQP | None | PLANNED | `100_percentiles_baseline_optimized.parquet/.csv`, `7_anchors_reconciliation.csv`, dual-domain validation |
| M2 | Rotating Equipment & Utilities Energy Revalidation | Independently calculate 4K-1/2/3 shaft power, total C3MR power decomposition, turbine steam savings (H4FI031A/029A/030A density conversion), boiler fuel gas savings (97.70 Nm3/t & DCS regression) across P1-P100 | M1 | PLANNED | Shaft power models, steam savings register, boiler fuel gas ledger across 100 percentiles |
| M3 | Environmental & Techno-Economic Revalidation | Compute Scope 1 GHG reductions (IPCC 56.1 kg/GJ on HHV vs LHV basis), Spot ($10.04) vs Domestic ($8.00) valuation, CAPEX audit (zero equipment vs MOC), 100-bin Riemann sum annualization | M1, M2 | PLANNED | Economic models, GHG emission balances, 100-bin Riemann sum annual savings ledger |
| M4 | Reconciliation, Evidence Ledger & Reproducibility | Update `audit_deliverables_v3/01_SOURCE_AND_EXECUTION_REGISTER.csv` with side-by-side reconstructed vs historical figures and flags; run and verify `ikms_2026/scripts/validate_all_reproducible.py` | M1, M2, M3 | PLANNED | Updated 01_SOURCE_AND_EXECUTION_REGISTER.csv, reproducible test suite green log, final audit report |

---

## Interface Contracts

### 1. Compressor Curve Data Schema (M2 ↔ M3, M4, M5)
- **Columns:**
  - `compressor_tag`: String (`4K-1`, `4K-2`, `4K-3`)
  - `section_or_case`: String (`Sect-1`, `Sect-2`, `Sect-3`, `Case-1`, `Case-2`, `Case-3`)
  - `curve_type`: String (`Head`, `Power`, `Efficiency`, `Pressure_Ratio`, `Discharge_Pressure`, `Surge_Limit`, `Choke_Limit`)
  - `speed_pct`: Float (e.g. `70.0`, `80.0`, `90.0`, `100.0`, `105.0`)
  - `speed_rpm`: Float (e.g. `4610.0`)
  - `flow_basis`: String (`AM3/HR` for 4K-1, `m3/h` for 4K-2 and 4K-3)
  - `flow_value`: Float (x-coordinate)
  - `y_unit`: String (`m-kg/kg`, `kW`, `fraction`, `ratio`, `kg/cm2A`)
  - `y_value`: Float (y-coordinate)
  - `source_pdf`: String (`H4K-1.pdf`, `H4K-2.pdf`, `H4K-3.pdf`)
  - `source_page`: Integer
  - `confidence_rating`: String (`HIGH`, `MEDIUM`, `ESTIMATED`)
- **Format:** Parquet & CSV.

### 2. Operating Point Mapping Contract (M3 ↔ M4, M5)
- **Inputs:** Raw DCS mass flow $\dot{m}$ ($t/h$), suction pressure $P_s$ ($kg/cm^2A$), suction temperature $T_s$ ($^\circ C$), gas composition ($\mathbf{z}$).
- **PR-EOS Conversion Function:**
  $$Z = \text{PR\_EOS\_Z}(P_s, T_s, \mathbf{z}), \quad \rho = \frac{P_s \cdot MW}{Z \cdot R \cdot T_s}, \quad Q_{\text{actual}} = \frac{\dot{m}}{\rho} \quad [m^3/h]$$
- **Outputs:** Operating coordinates $(Q_{\text{actual}}, H_p, \dot{W}_{\text{shaft}}, \eta_p)$ ready for overlay on digitized curve families.

### 3. Optimization Feasibility & Boundary Contract (M4 ↔ M5)
- **Inputs:** Candidate optimum operating points at P10, P50, P90.
- **Constraints Checked:**
  - Flow Floor: $\dot{m}_{\text{comp}} \ge 480.0\text{ t/h}$.
  - Surge Margin: $\text{SM} = (Q_{\text{actual}} - Q_{\text{surge}}) / Q_{\text{surge}} \ge 10.0\%$.
  - Suction Drum Temperature: $T_{\text{suct}} \ge -45.0^\circ C$ with $\text{VF} \equiv 1.0000$.
  - Maximum Speed: $N \le 105.0\%\text{ MCS}$.
  - MCHE Pinch: $\text{MITA} \ge 1.50^\circ C$ (zero crossover).
  - Mahalanobis Distance: $D_M \le 3.0802$ ($\chi^2_{0.95, 4}$).

---

## Code Layout
- `D:\User\Documents\KULIAH\LOMBA\IKMS 2026\`:
  - Source PDFs: `H4K-1.pdf`, `H4K-2.pdf`, `H4K-3.pdf`.
  - Digitized datasets: `data/digitized/compressor_curves_*.parquet` and `.csv`.
  - Standalone validation scripts: `scripts/validate_ml_surrogates.py`, `scripts/validate_curve_digitization.py`, `scripts/validate_operating_envelope.py`.
  - Visualizations: `figures/Figure_1_4K1_map.png`, `figures/Figure_2_4K2_map.png`, `figures/Figure_3_4K3_map.png`, `figures/Figure_4_baseline_vs_optimized.png`, `figures/Figure_5_power_head_efficiency_summary.png`.
  - Deliverables: `reports/ML_AUDIT_REPORT.md`, `reports/TARGET_SELECTION_REPORT.md`, `reports/COMPRESSOR_EVALUATION_REPORT.md`, `reports/OPTIMIZATION_INTEGRATION_REPORT.md`, `manuscript/IKMS_2026_PAPER_REVISION_DRAFT.md`.
- `d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\`:
  - Primary telemetry and model archive: `data/MASTER_DATASET_REBUILD_20261014/`, `MR_OPTIMIZATION_REBUILD/`, `MCR_ML_REBUILD/`.
  - Coordination and state: `.agents/teamwork/`.
