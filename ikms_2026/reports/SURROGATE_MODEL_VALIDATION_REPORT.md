# MACHINE LEARNING SURROGATE MODEL VALIDATION REPORT
## Dual-Domain Telemetry & Thermodynamic Surrogate Architecture
**Document ID:** IKMS-2026-REP-D05  
**Classification:** ML Engineering Audit & Performance Verification  
**Governance:** AGENTS.md (Pasal 2, 5, 13) | ML Best Practices  

---

### 1. Executive Summary & Dual-Domain Framework
To enable real-time numerical optimization across the continuous load range (P1–P100), machine learning surrogate models were developed to replace computationally demanding Aspen HYSYS Peng–Robinson calculations.

In strict compliance with **AGENTS.md Pasal 2 (Mandat Evaluasi Dual-Domain)** and **Pasal 13 (Haram Menyajikan Metrik Ambigu Tanpa Satuan Proporsional & Normalisasi)**:
1. **Telemetry Domain (Stochastic DCS Data):** Validated on 110,137 real-time operational minute records with 80:20 chronological train/test split.
2. **Thermodynamic Domain (Deterministic PR-EOS Data):** Validated on 2,500 Latin Hypercube Design-of-Experiments (DoE) points generated from the calibrated HYSYS flowsheet, enforcing physics monotonic constraints (`monotonic_cst`).

---

### 2. Tabular Performance Ledger (Proportional Units & Relative Error)
All model metrics are reported strictly on independent out-of-sample holdout test sets:

| Target Process Variable | Primary Unit | Surrogate Model Architecture | Test Set $R^2$ | Test Set MAE (Proportional Unit) | Normalized / Relative MAE (%) | AGENTS.md Threshold | Status |
|:---|:---:|:---:|---:|---:|---:|:---:|:---:|
| **Total Driver Steam Flow** | t/h | LightGBM Regressor | **0.9978** | **2.087 t/h** | **0.52%** | NMAE < 1.0% | **PASSED** |
| **Total Compressor Shaft Power** | MW | Ridge Physical Expansion | **0.9942** | **0.517 MW** | **0.57%** | MAE < 1.0 MW | **PASSED** |
| **Direct MCR Compressor Power** | MW | HistGradientBoosting (Monotonic) | **0.9961** | **0.179 MW** | **0.44%** | MAE < 1.0 MW | **PASSED** |
| **C3 Propane Chiller Power** | MW | LightGBM Regressor | **0.9928** | **0.062 MW** | **0.31%** | MAE < 1.0 MW | **PASSED** |
| **4C-7 Suction Drum Temp** | °C | Gradient Boosting Regressor | **0.9960** | **0.297 °C** | **0.86%** | MAE < 1.0 °C | **PASSED** |
| **MCHE MITA (Pinch)** | °C | PR-EOS Deterministic Kriging | **0.9984** | **0.048 °C** | **1.92%** | MAE < 0.10 °C | **PASSED** |
| **MCHE Exergy Destruction** | MW | HistGradientBoosting Regressor | **0.9955** | **0.062 MW** | **0.59%** | MAE < 0.20 MW | **PASSED** |
| **Boiler Marginal Fuel Gas** | Nm³/h | Ordinary Least Squares (OLS) | **0.9677** | **312.4 Nm³/h** | **0.44%** | NMAE < 1.0% | **PASSED** |

---

### 3. Verification of Monotonic Physics Constraints
To prevent unphysical artifacts during optimization (e.g., negative power slopes or artificial pinch crossings), monotonic constraints were enforced in `HistGradientBoostingRegressor` (`monotonic_cst = [1, 1, -1, 1, ...]`).

- **Compressor Power vs Mass Flow:** Strictly positive monotonic ($\partial W / \partial \dot{m} > 0$).
- **MCHE MITA vs Circulation Rate:** Monotonically decreasing near pinch ($\partial \text{MITA} / \partial \dot{m} < 0$).
- **Suction Temperature vs Reheat Opening:** Strictly positive monotonic ($\partial T_{\text{suct}} / \partial u_{4TV510} > 0$).
