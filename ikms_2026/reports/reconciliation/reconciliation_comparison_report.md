# PT BADAK NGL TRAIN H C3MR: MULTI-DOMAIN RECONCILIATION REPORT

**Status:** Fully Reconciled & Audited across 4 Operating & Thermodynamic Domains
**Governance:** AGENTS.md (Pasal 1, 2, 8, 9, 10, 11, 12, 13) | Zero AI Jargon | Proportional Engineering Units

## 1. Summary Reconciliation Matrix

| Evaluation Domain | Operating Philosophy | Equipment Boundary | Shaft Power Saving (MW) | Steam Saving (t/h) | Annual Steam (t/yr) | Fuel Gas Saving (kNm³/yr) | Scope 1 CO₂ (t/yr) | Annual Benefit (USD) | Audit Classification |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Domain A** | Idealized Re-governing (4KT-1 slashed by... | Total C3MR System (4K-1 + 4K-2 + 4K | **28.98 MW** | 30.56 t/h | 239,890 | 23,437.3 | 49,961.8 | **$8,480,000** | `UNCONSTRAINED` |
| **Domain C** | Historical Control (4KT-1 speed held con... | Direct MCR Compression (4K-2 + 4K-3 | **4.14 MW** | 4.37 t/h | 34,297 | 2,720.8 | 5,379.2 | **$291,528** | `VALIDATED` |
| **Calibrated Model Case A** | Current DCS Control (4KT-1 constant spee... | Direct MCR Compression + Surge-Boun | **6.14 MW** | 6.37 t/h | 50,004 | 3,966.8 | 7,842.4 | **$425,033** | `RECOMMENDED` |
| **Calibrated Model Case B** | Proposed Governor Co-Optimization (4KT-1... | Total C3MR System with Validated OE | **15.33 MW** | 15.48 t/h | 121,516 | 9,639.9 | 19,058.1 | **$1,032,890** | `VALIDATED` |


## 2. Root Cause Analysis: The 7x Discrepancy Explained

The approximately 7-fold difference between the legacy flowsheet prediction (28.98 MW) and the DCS telemetry surrogate (4.14 MW) is completely explained by two fundamental physical factors:

### A. The 4KT-1 Propane Governor Lock (62.6% of Discrepancy)
- **In Legacy Flowsheet (Domain A):** Reducing MCR circulation dropped the thermal precooling duty on chillers 4E-7/8/9. HYSYS automatically calculated an **18.15 MW** reduction in 4K-1 propane compressor power, assuming the 4KT-1 steam turbine governor throttles down by 60.7%.
- **In Actual Field DCS Telemetry (Domain C):** The 4KT-1 speed is held constant by its mechanical-hydraulic governor at ~3,000 RPM (mean 3,040 ± 39 RPM). Furthermore, propane compressor 4K-1 also chills natural gas feed (4E-10/12/14/40). Throttling 4K-1 by 60.7% would drive its three sections deep into destructive aerodynamic surge. Under safe OEM surge margins (SM >= 8.0%), 4K-1 power can drop at most by 1.50 to 2.50 MW.
- **Conclusion:** The 18.15 MW propane credit in Domain A was an unconstrained simulation artifact that cannot be realized under current plant control.

### B. Conservative DCS Surrogate vs Thermodynamic Potential (37.4% of Discrepancy)
- **In DCS Surrogates (Domain C):** The models were trained on historical operational data where operators never lowered MCR circulation below 473.5 t/h during turndown due to fears of suction drum TAL trip (-45 °C). Consequently, the surrogate model predicted a conservative saving of **4.14 MW** (4.37 t/h steam) across the two MCR compressors 4K-2 and 4K-3.
- **In Validated Flowsheet (Case B):** When MCR composition is co-optimized with the 4UV-53 kickback and 4TV-510 reheat systems, direct MCR compression power is reduced by **10.83 MW** at P90 (weighted annual 6.85 MW), which is physically achievable.

## 3. Boiler Fuel Gas & Scope 1 CO₂ Reconciliation

- **Direct DCS Measurement:** Analysis of 110,137 minute records from Unit 31 boilers (31-F21 to 31-F29) reveals an actual fuel gas-to-steam conversion ratio of **79.33 Nm³/ton steam** (mean = 79.97 Nm³/ton steam).
- **Theoretical ASME PTC 4.1 Factor:** The literature factor of **97.70 Nm³/ton steam** (Ramadan, 2025) assumes a conservative fuel gas LHV of 33.10 MJ/Nm³ and 85% boiler efficiency. Because Badak LNG fuel gas has a higher actual heating value (~39.5 MJ/Nm³), the theoretical factor overestimates fuel gas savings by 23.2%.
- **Reporting Protocol:** The revised manuscript reports both values side-by-side, citing 79.33 Nm³/ton as the primary empirical baseline and 97.70 Nm³/ton as the theoretical comparison benchmark.
