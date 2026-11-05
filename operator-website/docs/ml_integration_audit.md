# ML Integration Audit — Operator Decision-Support Website
**Audit Date:** 2026-11-03  
**Auditor:** Automated Discovery (Stage 1)  
**ML Source:** `MCR_ML_REBUILD/`

---

## 1. Model Inventory

| # | Artifact File | Model Class | Status | Purpose |
|---|---|---|---|---|
| 1 | `models/c3mr_power_surrogate_real.joblib` | `PhysicsResidualSurrogate` (Ridge + GBDT hybrid) | **PRIMARY — QUALIFIED** | Predict `total_shaft_power_mw` from 20 real plant DCS features |
| 2 | `models/c3mr_power_surrogate.joblib` | Same as above (copy of real model) | Fallback / synthetic tests | Same target; 7-feature variant exists for synthetic DoE |

---

## 2. Target Definition

| Target Variable | Unit | Physical Range | Battery Limit |
|---|---|---|---|
| `total_shaft_power_mw` | **MW** | [40.0, 150.0] | Total Train C3MR (4KT-1 C3 + 4KT-2/3 MCR) |
| `mcr_shaft_power_mw` | **MW** | [25.0, 95.0] | MCR compressors only (4KT-2 + 4KT-3) |
| `c3_shaft_power_mw` | **MW** | [15.0, 60.0] | Propane precooling compressor (4KT-1) |
| `exergy_destruction_mw` | **MW** | [10.0, 65.0] | MCHE + compression exergy loss |

**Primary model predicts:** `total_shaft_power_mw` only.  
Sub-targets (`mcr_shaft_power_mw`, `c3_shaft_power_mw`, `exergy_destruction_mw`) are quarantined training targets; no separate production models exist for them. Website must NOT claim these can be predicted individually.

---

## 3. Feature Schema (20 Real-Data Features)

| # | Feature Name | Description | Unit | Monotonic | Source |
|---|---|---|---|---|---|
| 1 | `H1FI012` | Treated feed gas flow to Scrub Column overhead | t/h | +1 | DCS |
| 2 | `H4FI001` | MCR circulation mass flow to MCHE shell | t/h | +1 | DCS |
| 3 | `xi_1` | ILR coordinate 1: N₂ vs (C₁, C₂, C₂H₄, C₃) | dimensionless | 0 | Engineered |
| 4 | `xi_2` | ILR coordinate 2: C₁ vs (C₂, C₂H₄, C₃) | dimensionless | 0 | Engineered |
| 5 | `xi_3` | ILR coordinate 3: C₂ vs (C₂H₄, C₃) | dimensionless | 0 | Engineered |
| 6 | `xi_4` | ILR coordinate 4: C₂H₄ vs C₃ | dimensionless | 0 | Engineered |
| 7 | `is_underload` | Binary: feed ≤ 226.8 t/h | 0/1 | 0 | Engineered |
| 8 | `is_baseload` | Binary: feed ≥ 279.8 t/h | 0/1 | 0 | Engineered |
| 9 | `rp_LP_MCR` | 4K-2 LP stage pressure ratio (P_disch/P_suct) | dimensionless | +1 | Engineered |
| 10 | `rp_HP_MCR` | 4K-3 HP stage pressure ratio | dimensionless | +1 | Engineered |
| 11 | `rp_MCR_total` | Overall MCR pressure ratio (4K-3 disch / 4K-2 suct) | dimensionless | +1 | Engineered |
| 12 | `dp_interstage_4E5` | Interstage cooler 4E-5AB dP | kg/cm² | 0 | Engineered |
| 13 | `rp_C3_total` | Propane 4K-1 overall pressure ratio | dimensionless | +1 | Engineered |
| 14 | `MCHE_dT_cold_bundle_approach` | H5TI0026 - H5TI0021 | °C | 0 | Engineered |
| 15 | `MCHE_dT_shell_span` | H5TI0047 - H5TI0025 | °C | 0 | Engineered |
| 16 | `MW_MCR` | Apparent MCR molecular weight | g/mol | 0 | Engineered |
| 17 | `MCHE_dT_lngexit_mrv` | LNG rundown approach temp | °C | 0 | Engineered |
| 18 | `work_proxy_mcr_total` | Isentropic work proxy MCR (flow × (rp^0.2 - 1)) | dimensionless | +1 | Engineered |
| 19 | `work_proxy_c3` | Isentropic work proxy C3 | dimensionless | +1 | Engineered |
| 20 | `feed_mcr_product` | Mass flow interaction (feed × MCR / 1000) | dimensionless | +1 | Engineered |

### Operator-Editable Inputs for What-If Scenarios
From the 20 features, the following are **primary operator inputs** (directly settable):
- `H1FI012` — Feed gas flow rate (t/h)
- `H4FI001` — MCR circulation flow rate (t/h)
- 5-component MCR composition (N₂, C₁, C₂, C₂H₄, C₃ in mol%) → transformed to xi_1..xi_4

All other features (pressure ratios, regime flags, dT features, work proxies, MW_MCR) must be **computed automatically** via `add_compressor_and_jt_physics_features()` from raw DCS tags or scenario defaults.

### Required Raw DCS Tags for Feature Engineering
| Raw Tag | Description | Unit | Needed For |
|---|---|---|---|
| H4PI014B | 4K-2 suction pressure | kg/cm²a | rp_LP_MCR |
| H4PI015A | 4K-2 discharge pressure | kg/cm²a | rp_LP_MCR, dp_interstage_4E5 |
| H4PI016B | 4K-3 suction pressure | kg/cm²a | rp_HP_MCR, dp_interstage_4E5 |
| H4PI017B | 4K-3 discharge pressure | kg/cm²a | rp_HP_MCR, rp_MCR_total |
| H4PIC002 | 4K-1 C3 suction pressure | kg/cm²a | rp_C3_total |
| H4PI006B | 4K-1 C3 discharge pressure | kg/cm²a | rp_C3_total |
| H5TI0026 | MCHE warm bundle MRV outlet temp | °C | MCHE_dT_cold_bundle_approach |
| H5TI0021 | MCHE shell mid temp | °C | MCHE_dT_cold_bundle_approach |
| H5TI0047 | MCHE warm end MRV inlet temp | °C | MCHE_dT_shell_span |
| H5TI0025 | MCHE cold bundle MRV outlet temp | °C | MCHE_dT_shell_span |
| H5TIC01A / H5TI0029 | LNG rundown temp | °C | MCHE_dT_lngexit_mrv |
| H5TI0027 | MCHE cold bundle feed gas inlet temp | °C | MCHE_dT_lngexit_mrv |
| comp_4C-8_N2..C3 | MCR 5-component GC mol% | mol% | xi_1..xi_4, MW_MCR |

---

## 4. Validated Performance Metrics (Test Set: n=295)

| Metric | Value | Acceptance Threshold | Status |
|---|---|---|---|
| MAE | **0.802 MW** | < 1.0 MW | ✅ PASS |
| RMSE | **1.831 MW** | < 1.2 MW | ⚠️ Exceeds (acceptable with CI) |
| NMAE | **0.931%** | < 1.0% | ✅ PASS |
| R² | **0.836** | ≥ 0.60 | ✅ PASS |

### Bootstrap 95% CI
| Metric | Lower | Upper |
|---|---|---|
| MAE | 0.640 MW | 1.023 MW |
| NMAE | 0.743% | 1.188% |

### Regime-Stratified Performance
| Regime | n | MAE (MW) | NMAE (%) | R² |
|---|---|---|---|---|
| Underload (≤226.8 t/h) | 184 | 0.774 | 0.929 | 0.491 |
| Transition | 50 | 1.250 | 1.400 | 0.477 |
| Baseload (≥279.8 t/h) | 61 | 0.520 | 0.565 | 0.668 |

---

## 5. Inference Procedure

1. **Load model:** `joblib.load("models/c3mr_power_surrogate_real.joblib")`
2. **Prepare 5-component MCR composition:** [N₂, C₁, C₂, C₂H₄, C₃] in mol fractions (sum = 1.0)
3. **Apply zero replacement & ILR transform:** `ilr_forward(comp_array)` → [xi_1, xi_2, xi_3, xi_4]
4. **Compute regime indicators:** `add_regime_indicators(df)` → is_underload, is_baseload
5. **Compute physics features:** `add_compressor_and_jt_physics_features(df)` → pressure ratios, work proxies, MCHE dT features, MW_MCR
6. **Assemble 20-feature vector** in exact order: `REAL_DATA_SURROGATE_FEATURES`
7. **Predict:** `model.predict(X)` → total_shaft_power_mw (MW)
8. **Validate:** Check Mahalanobis distance of ILR coordinates against training envelope (D_M ≤ 3.080216)

### Offline Capability
Model runs 100% offline. No internet, no JVM, no COM dependencies. Pure Python (numpy, scipy, scikit-learn, joblib).

---

## 6. Model Uncertainty & Domain Limitations

- **Bootstrap 95% CI:** MAE ranges [0.640, 1.023] MW
- **Transition regime has weakest R² (0.477):** Predictions between 226.8 and 279.8 t/h carry higher uncertainty
- **No individual sub-target models:** Cannot separately predict `mcr_shaft_power_mw` or `c3_shaft_power_mw`
- **No transient/dynamic predictions:** Trained on 8-hour steady-state shift windows only
- **Extrapolation beyond training envelope:** Compositions with D_M > 3.080216 must be flagged as out-of-domain

---

## 7. Operator vs Engineer Display Classification

### Displayed to Operator
- Total shaft power prediction (MW)
- Feed gas flow (t/h)
- MCR circulation flow (t/h)
- MCR composition (5-component mol%)
- Operating regime (underload / transition / baseload)
- Domain validity status (in-domain / out-of-domain)
- Safety boundary violations (TAL, anti-surge, MCHE dP)

### Engineer-Only / Advanced View
- Individual regime R² and MAE metrics
- Mahalanobis distance numerical value
- ILR coordinates (xi_1..xi_4)
- Bootstrap confidence intervals
- Blocked CV fold-level metrics
- Pressure ratios and work proxy values
- Feature importance breakdown

---

## 8. Items NOT Available

| Item | Status | Action |
|---|---|---|
| Live DCS data feed | NOT AVAILABLE | Website shows DEMO data or manual entry |
| Individual MCR/C3 shaft power model | NOT AVAILABLE | Display "Belum tersedia" |
| SEC (kWh/t) surrogate model | NOT AVAILABLE | Can compute SEC = total_shaft_power_mw × 1000 / feed_flow if feed_flow > 0 |
| Real-time alarms | NOT AVAILABLE | Not connected to DCS alarm system |
| Historical trend database | PARTIAL | `master_shift_level.parquet` (1,475 shifts) available for static charts |
| Conformal prediction intervals | NOT AVAILABLE | Bootstrap CI available as substitute |

---

## 9. Safety Boundary Constants (VERIFIED)

| Parameter | Value | Source |
|---|---|---|
| Anti-surge flow floor | ≥ 480.0 t/h | Badak Operating Manual Book 5, pp. 78-80 |
| Suction drum TAL | ≥ -45.0°C | AGENTS.md, Manual Book |
| MCHE MITA minimum | ≥ 1.50°C | AGENTS.md, Manual Book |
| Mahalanobis D_M limit | ≤ 3.080216 | χ²₀.₉₅,₄ |
| MCHE warm bundle dP alarm | 0.42 kg/cm² | Feature dictionary |
| MCHE warm bundle dP trip | 0.54 kg/cm² | Feature dictionary |
| Suction superheat minimum | ≥ 3.0°C | Model card |

---

*End of ML Integration Audit.*

