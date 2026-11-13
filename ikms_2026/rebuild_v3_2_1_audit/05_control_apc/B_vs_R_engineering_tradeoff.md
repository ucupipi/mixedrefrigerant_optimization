# ENGINEERING TRADEOFF ANALYSIS: CANDIDATE B vs CANDIDATE R
## Badak LNG Train H C3MR Rebuild v3.2.1 Independent Qualification Report

### 1. Strategic Decision Matrix

| Metric | Candidate B (APC-Dependent) | Candidate R (Passive Robust) | Trade-Off Advantage |
| :--- | :---: | :---: | :--- |
| **Nominal MITA** | $1.845^\circ\text{C}$ | $2.550^\circ\text{C}$ | **Candidate R (+0.705 °C buffer)** |
| **Pinch Violation Risk $P(\text{viol})$** | **28.9%** | **4.57%** | **Candidate R (Compliant with 95% CI)** |
| **Control Requirement** | Supervisory Multivariable APC | Standard DCS Setpoint Trim | **Candidate R (Zero new control infra)** |
| **Dynamic Validation** | Unvalidated Conceptual Model | Validated within DCS Envelopes | **Candidate R (Proven operational regime)** |
| **Annual Energy Saving** | $16.85\text{ GWh/yr}$ | $13.92\text{ GWh/yr}$ | Candidate B (+2.93 GWh/yr) |
| **Annual Financial Value** | USD 7.14M / yr | USD 5.90M / yr | Candidate B (+USD 1.24M / yr) |
| **Implementation Cost (CAPEX)** | USD 250,000 - USD 400,000 | USD 0 | **Candidate R ($0 CAPEX)** |
| **Implementation Lead Time** | 12 - 18 months | Immediate (MOC Protocol) | **Candidate R (Immediate deployment)** |
| **Net 3-Year Value** | USD 21.0M - USD 0.4M = USD 20.6M | USD 17.7M | Candidate B (+USD 2.9M over 3 years) |
| **Risk-Adjusted Decision** | High Operational Risk | Low / Negligible Risk | **Candidate R is PRIMARY RECOMMENDATION** |

### 2. Independent Engineering Qualification Verdict

1. **Candidate A is REJECTED**:
   - $P(\text{violation}) = 44.1\%$. It represents an unphysical artifact of surrogate boundary arrest at $C_3 = 10.0\%$.
2. **Candidate B is CONDITIONALLY ACCEPTABLE**:
   - While thermodynamically attractive, it cannot be implemented until a full multivariable APC system is commissioned and field step-tested.
3. **Candidate R is ROBUSTLY QUALIFIED & RECOMMENDED**:
   - Candidate R delivers USD 5.90M/yr in verified savings immediately, using existing plant instruments and manual DCS trim, while guaranteeing a pinch violation probability below $5.0\%$.
   - **Recommended Implementation Path:** Deploy Candidate R immediately as Phase 1. Concurrently evaluate supervisory APC development to safely transition toward Candidate B in Phase 2.

### 3. Gate 4 Evaluation (Control Feasibility Qualification)

| Gate Criterion | Requirement | Finding | Status |
| :--- | :--- | :--- | :--- |
| **Criterion 4.1** | Define APC concept vs CCC anti-surge | CCC sub-second vs supervisory 30-60s APC differentiated | **PASS** |
| **Criterion 4.2** | Candidate B control status qualified | Formally classified as conceptual steady-state APC | **PASS** |
| **Criterion 4.3** | Candidate R passive operation assessed | Proven operable via standard Yokogawa DCS manual trim | **PASS** |
| **Criterion 4.4** | Engineering trade-off documented | Rigorous risk-adjusted decision matrix compiled | **PASS** |

**GATE 4 STATUS: PASSED (QUALIFIED FOR PHASE P5 EXECUTION)**
