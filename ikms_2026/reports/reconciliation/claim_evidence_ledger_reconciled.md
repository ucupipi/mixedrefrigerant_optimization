# PT BADAK NGL TRAIN H C3MR: RECONCILED CLAIM EVIDENCE LEDGER (FOUR-TIER CLASSIFICATION)
## Pre-Restructuring Audit & Validation Status (IKMS 2026)

**Governance:** AGENTS.md (Pasal 1 s.d. 14) | Strict Integrity | Intellectual Honesty  
**Classification Hierarchy:**
1. `[VALIDATED_BY_INDEPENDENT_EVIDENCE]`: Directly verified against empirical plant measurements, independent sensor data, or physical thermodynamic laws.
2. `[SUPPORTED_BY_MODEL_CONDITIONAL]`: Predicted by calibrated models, but conditional on specific operating requirements (e.g. active kickback, reheat modulation, or stable feed).
3. `[ESTIMATED_USING_ASSUMPTIONS]`: Derived through engineering conversions (e.g. rankine enthalpy drop, marginal regression, IPCC emission factor).
4. `[UNSUPPORTED_OR_SUPERSEDED]`: Legacy claims retired due to physical impossibility, unvalidated control assumptions, or refuted premises.

---

## 1. Summary Claim Register Matrix

| Claim ID | Claim Statement | Classification | Category | Key Metric / Value | Technical Status |
|---|---|:---:|---|:---:|:---:|
| **CLM-01** | Baseline Train H C3MR driver steam consumption is ~404.2 t/h (mean) / 484.7 t/h (P90). | `[VALIDATED_BY_INDEPENDENT_EVIDENCE]` | Baseline Telemetry | $R^2 = 0.9978$, $\text{MAE} = 2.087\text{ t/h}$, $\text{NMAE} = 0.52\%$ | **CERTIFIED GROUND TRUTH** |
| **CLM-02** | 4KT-1 propane turbine speed is physically constant at ~3,000 RPM (3,039.98 ± 39.29 RPM) across all loads. | `[VALIDATED_BY_INDEPENDENT_EVIDENCE]` | Control Architecture | $\text{Std} = 39.29\text{ RPM}$, $\text{CV} = 1.3\%$, $N=707,142$ records | **CERTIFIED GROUND TRUTH** |
| **CLM-03** | Plant Unit 31 boilers show an aggregate fuel gas ratio of 79.97 Nm³/ton steam (July 2025: 79.33 Nm³/t). | `[VALIDATED_BY_INDEPENDENT_EVIDENCE]` | Utility Ground Truth | $44,602\text{ valid minutes}$, $\sum \text{FG} / \sum \text{Steam} = 79.97\text{ Nm}^3/\text{t}$ | **CERTIFIED GROUND TRUTH** |
| **CLM-04** | Historical MCR composition is dynamic per shift, not static or frozen. | `[VALIDATED_BY_INDEPENDENT_EVIDENCE]` | Plant Operating Practice | 2,531 shift samples ($C_3: 0.0\text{--}10.1\%$, $C_1: 39.1\text{--}52.7\%$) | **CERTIFIED GROUND TRUTH** |
| **CLM-05** | Recommended field-testable MCR recipe ($N_2: 3.77\%, C_1: 42.22\%, C_2: 43.67\%, C_2H_4: 1.53\%, C_3: 8.82\%$). | `[SUPPORTED_BY_MODEL_CONDITIONAL]` | Recommended Optimization | Mahalanobis $D_M = 1.84 \le 3.0802$, MITA $\ge 1.50^\circ\text{C}$ | **VALIDATED DESIGN ENVELOPE** |
| **CLM-06** | Total predicted driver steam reduction of 9.68 t/h (weighted) across Train H. | `[SUPPORTED_BY_MODEL_CONDITIONAL]` | Predicted Field Saving | Direct MCR: $4.37\text{ t/h}$ + Bounded Propane: $5.31\text{ t/h}$ | **FIELD-TESTABLE PREDICTION** |
| **CLM-07** | Compressor aerodynamic surge margin remains safe across all stages during trial. | `[SUPPORTED_BY_MODEL_CONDITIONAL]` | Mechanical Integrity | $\text{SM}_{4K1} \ge +18.5\%$, $\text{SM}_{4K2} \ge +22.7\%$, $\text{SM}_{4K3} \ge +11.6\%$ | **SAFE OPERATING MARGIN** |
| **CLM-08** | Mechanical shaft power reduction is ~2.40 MW (1.08 MW MCR + 1.31 MW Propane). | `[ESTIMATED_USING_ASSUMPTIONS]` | Power Equivalence | Derived from steam flow via calibrated $SSR = 4.04\text{ t/MWh}$ | **DERIVED VALUE (NOT DIRECT TORQUE)** |
| **CLM-09** | Marginal boiler fuel gas reduction is 76.98 Nm³/ton steam saved (5.85 million Nm³/yr). | `[ESTIMATED_USING_ASSUMPTIONS]` | Utility Response | OLS slope $\partial \text{FG}/\partial \text{Steam} = 76.98\text{ Nm}^3/\text{t}$ ($R^2 = 0.9678$) | **ESTIMATED MARGINAL RESPONSE** |
| **CLM-10** | Annual Scope 1 CO₂ reduction is 12,959 t CO₂/yr (IPCC) / 11,562 t CO₂/yr (Stoichiometric). | `[ESTIMATED_USING_ASSUMPTIONS]` | Emissions Accounting | $39.50\text{ MJ/Nm}^3$ LHV, $56.10\text{ kg/GJ}$ vs $1.977\text{ kg/Nm}^3$ | **STANDARDIZED GHG ESTIMATE** |
| **CLM-11** | Annual economic benefit is USD 645,770/yr (steam cost) to USD 1.44M/yr (export parity). | `[ESTIMATED_USING_ASSUMPTIONS]` | Economic Valuation | Steam: \$8.50/t; Domestic gas: \$6.00/MMBtu; Export: \$6.58/MMBtu | **SCENARIO ECONOMIC VALUE** |
| **CLM-12** | Legacy claim of 28.98 MW (27.10%) power saving as an immediate plant saving. | `[UNSUPPORTED_OR_SUPERSEDED]` | Legacy Flowsheet | Violates 4K-1 OEM surge limit by assuming 60.7% unconstrained throttling | **SUPERSEDED & RETIRED** |
| **CLM-13** | Legacy claim of 4.14 MW power saving for 4.37 t/h steam saving. | `[UNSUPPORTED_OR_SUPERSEDED]` | Legacy Derivation | Used unphysical multiplier $948.42\text{ kW/(t/h)}$ ($SSR = 1.054\text{ t/MWh}$) | **SUPERSEDED BY PHYSICAL SSR 4.04** |
| **CLM-14** | Theoretical boiler fuel gas ratio of 97.70 Nm³/ton steam as actual plant response. | `[UNSUPPORTED_OR_SUPERSEDED]` | Legacy Assumption | Overestimates fuel gas by 23.2% due to conservative LHV 33.10 MJ/Nm³ | **SUPERSEDED BY DCS 79.33-79.97** |
| **CLM-15** | Continuous online DCS stream analyzers `4AI-021` and `3AI-025`. | `[UNSUPPORTED_OR_SUPERSEDED]` | Legacy Instrumentation | Those tags represent boiler flue gas O2, not gas chromatographs | **SUPERSEDED BY LAB GC ARCHIVE** |

---

## 2. Technical Audit Conclusions

1. **Integrity of Shaft Power Reporting:**
   - Shaft power is **not directly measured** by physical torque meters on Train H. It is derived from condensate return flow using the thermodynamic specific steam rate ($4.04\text{ t/MWh}$).
   - The manuscript must explicitly report: *"Shaft power values are derived from calibrated steam consumption and are not independent physical torque measurements."*
2. **One Defensible Optimization Solution:**
   - The research focuses strictly on the single field-testable solution: **9.68 t/h steam reduction** (2.40 MW derived shaft power, 5.85 million Nm³/yr marginal fuel gas, USD 645k/yr steam cost).
   - Case A and Case B are not presented as competing choices in the manuscript results.
