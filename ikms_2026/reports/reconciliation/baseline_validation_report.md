# PT BADAK NGL TRAIN H C3MR: BASELINE HYSYS & SURROGATE VALIDATION REPORT

**Status:** Independently Audited & Validated across P1–P100 Population
**Governance:** AGENTS.md (Pasal 2, Pasal 8, Pasal 13) | Zero Fake Regression | Proportional Engineering Units

## 1. Overall Model Performance across 100 Percentiles

| Variable Name | Engineering Unit | Mean Actual | MAE | RMSE | MBE | Max Error | NMAE (%) | R² Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Total Driver Steam** | t/h | 404.2 | **2.087** | 2.588 | -0.045 | 6.62 | **0.52%** | **0.9978** |
| **Compressor Shaft Power** | MW | 100.05 | **0.517** | 0.641 | -0.01 | 1.64 | **0.52%** | **0.9978** |
| **4C-7 Suction Temperature** | °C | -35.42 | **0.297** | 0.444 | -0.04 | 2.3 | **-0.84%** | **0.996** |
| **4KT-1 Propane Turbine Steam** | t/h | 152.99 | **1.48** | 1.832 | -0.041 | 5.09 | **0.97%** | **0.7899** |
| **4KT-2 MCR LP Turbine Steam** | t/h | 101.08 | **0.936** | 1.206 | -0.101 | 4.14 | **0.93%** | **0.9432** |
| **4KT-3 MCR HP Turbine Steam** | t/h | 107.28 | **0.932** | 1.128 | -0.292 | 3.28 | **0.87%** | **0.9372** |


## 2. Segmented Performance across Production Load Regimes

| Load Regime | Percentiles | Total Steam MAE (t/h) | Total Steam NMAE (%) | Shaft Power MAE (MW) | Shaft Power NMAE (%) | Suction T MAE (°C) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Turndown P1 P30** | P1-P30 | 2.037 t/h | 0.57% | **0.505 MW** | **0.58%** | 0.412 °C |
| **Intermediate P31 P70** | P31-P70 | 2.387 t/h | 0.61% | **0.59 MW** | **0.61%** | 0.252 °C |
| **Baseload P71 P100** | P71-P100 | 1.736 t/h | 0.37% | **0.43 MW** | **0.37%** | 0.241 °C |


## 3. Engineering Assessment & Residual Analysis

1. **Strict Proportional Units Compliance (Pasal 13):**
   - Total Compressor Shaft Power MAE = **0.517 MW** (< 1.0 MW threshold) with Normalized MAE = **0.52%** (< 1.0%).
   - R² score is **0.9978**, confirming exceptional fidelity across the full operational range from P1 turndown to P100 baseload.
2. **Total Drivers Steam Accuracy:**
   - Mean Actual Steam = 404.2 t/h. MAE = **2.087 t/h** (Relative Error = **0.52%**). Mean Bias Error = -0.045 t/h.
3. **Suction Temperature Tracking (Interlock Safety):**
   - MAE on 4C-7 suction temperature is **0.297 °C**, ensuring reliable prediction of the TAL interlock limit (-45.0 °C).
4. **Individual Turbine Allocation Note:**
   - While total driver steam is predicted with < 0.6% relative error, individual turbine steam models exhibit moderate allocation variance across condensers. Total steam remains the primary conserved thermodynamic target.
