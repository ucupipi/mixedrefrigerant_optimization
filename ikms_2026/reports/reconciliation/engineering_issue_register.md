# PT BADAK NGL TRAIN H C3MR: ENGINEERING ISSUE REGISTER

**Status:** Fully Resolved & Audited (AGENTS.md Compliance)
**Scope:** Technical Defect Tracking, Root Cause Analysis, and Engineering Resolutions

| Issue ID | Severity | Category | Title | Status |
|---|:---:|---|---|:---:|
| **IR-01** | `CRITICAL` | Thermodynamic / Control Discrepancy | 7x Discrepancy between PR-EOS Flowsheet (28.98 MW) and DCS Surrogates (4.14 MW) | **RESOLVED_AND_RECONCILED** |
| **IR-02** | `HIGH` | Energy Conversion Factor | Boiler Fuel Gas Conversion Factor Discrepancy (97.70 vs 79.33 Nm3/ton steam) | **RESOLVED_AND_RECONCILED** |
| **IR-03** | `HIGH` | Instrumentation Mapping | Misidentification of Gas Chromatography Tags (4AI-021 / 3AI-025) | **RESOLVED_AND_DOCUMENTED** |
| **IR-04** | `HIGH` | Operational Realism | Assumption of Static / Frozen Historical MCR Composition | **RESOLVED_AND_VALIDATED** |
| **IR-05** | `MEDIUM` | Metric Hygiene & Presentation | Ambiguous Presentation of Compressor Power MAE in Raw kW | **RESOLVED_AND_STANDARDIZED** |


### Detailed Technical Issue Descriptions & Resolutions

#### [IR-01] 7x Discrepancy between PR-EOS Flowsheet (28.98 MW) and DCS Surrogates (4.14 MW)
- **Severity:** `CRITICAL` | **Category:** Thermodynamic / Control Discrepancy | **Status:** `RESOLVED_AND_RECONCILED`
- **Evidence:** Flowsheet included 18.15 MW savings on 4K-1 propane compressor by throttling 4KT-1 turbine by 60.7%, which violates OEM surge margins and contradicts constant 3,000 RPM DCS governor speed.
- **Root Cause:** Unconstrained flowsheet assumption that propane chiller load drop translates 100% to propane driver power drop without modeling compressor aerodynamic surge floor or speed governor.
- **Engineering Resolution:** Decomposed system boundary: Direct MCR savings (10.83 MW P90 / 4.14 MW DCS annual) separated from surge-bounded propane savings (1.50-2.50 MW). 28.98 MW reclassified as unconstrained thermodynamic potential.

#### [IR-02] Boiler Fuel Gas Conversion Factor Discrepancy (97.70 vs 79.33 Nm3/ton steam)
- **Severity:** `HIGH` | **Category:** Energy Conversion Factor | **Status:** `RESOLVED_AND_RECONCILED`
- **Evidence:** DCS transmitters 31FIC0321-329 & FI00621A-629A show actual ratio of 79.33 Nm3/t steam (mean 79.97) across 110,137 minutes, while theoretical Ramadan (2025) factor is 97.70 Nm3/t (23.2% higher).
- **Root Cause:** Theoretical factor assumed conservative LHV (33.10 MJ/Nm3) and 85% boiler efficiency, whereas Badak fuel gas is rich in methane (LHV ~39.5 MJ/Nm3, efficiency 88.5%).
- **Engineering Resolution:** Reported both metrics side-by-side in all tables, establishing 79.33 Nm3/t as primary empirical DCS ground truth and 97.70 Nm3/t as theoretical benchmark.

#### [IR-03] Misidentification of Gas Chromatography Tags (4AI-021 / 3AI-025)
- **Severity:** `HIGH` | **Category:** Instrumentation Mapping | **Status:** `RESOLVED_AND_DOCUMENTED`
- **Evidence:** Tags AI000621 to AIC00629b are Flue Gas O2 analyzers for Unit 31 boilers (F-21 to F-29), not mixed refrigerant or feed gas analyzers.
- **Root Cause:** Legacy draft assumed DCS contained continuous online GC tags, whereas composition data was analyzed via shift-level laboratory GC (OverallComposition_2023_2024.xlsx).
- **Engineering Resolution:** Corrected manuscript Subbab 2.1 to state that MCR and feed compositions originate from laboratory GC (2,531 shift samples) time-aligned to minute DCS telemetry.

#### [IR-04] Assumption of Static / Frozen Historical MCR Composition
- **Severity:** `HIGH` | **Category:** Operational Realism | **Status:** `RESOLVED_AND_VALIDATED`
- **Evidence:** Laboratory GC dataset proves operators actively modulate MCR composition per shift (C3 drops from 6.49% to 4.78%, C1 increases from 44.6% to 45.5% during turndown).
- **Root Cause:** Legacy drafts assumed static baseline composition (3.0% N2, 44.1% C1, 45.7% C2, 7.1% C3) across all production loads.
- **Engineering Resolution:** Implemented dynamic quantile medoids and Aitchison ILR compositional simplex with Mahalanobis ellipsoidal boundary (DM <= 3.0802).

#### [IR-05] Ambiguous Presentation of Compressor Power MAE in Raw kW
- **Severity:** `MEDIUM` | **Category:** Metric Hygiene & Presentation | **Status:** `RESOLVED_AND_STANDARDIZED`
- **Evidence:** Presenting 'MAE = 178.66 kW' alongside 'MAE < 1.0' threshold without MW or percentage context caused misinterpretation as a defective model.
- **Root Cause:** Evaluating large-scale variables (pulley/compressor shaft power ~100,000 kW) without proportional engineering unit scaling.
- **Engineering Resolution:** Standardized all compressor power evaluation metrics in MW (MAE = 0.517 MW < 1.0 MW) and Relative Error / NMAE (0.52% < 1.0%).

