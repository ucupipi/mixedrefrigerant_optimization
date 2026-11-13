# REBUILD v3.2.1 EXECUTIVE SUMMARY
## BADAK LNG TRAIN H C3MR ENERGY EFFICIENCY RESEARCH & FORENSIC QUALIFICATION
**PT Badak NGL — IKMS 2026 Independent Qualification Suite**

---

### 1. Core Engineering Directive & Context
This report establishes the final forensic qualification of the C3MR refrigeration optimization framework for Badak LNG Train H. All historical approximations, synthetic formulas, arbitrary multipliers, and reporting ambiguities have been permanently resolved through calculation-level physics-based reconstruction.

---

### 2. Primary Engineering Findings & Operational Decisions

#### Decision A: Primary Immediate Recommendation — Candidate R (Passive Robust)
- **5-Component Composition:**
  - Nitrogen ($N_2$): **$4.50\text{ mol\%}$**
  - Methane ($C_1$): **$42.50\text{ mol\%}$**
  - Ethane ($C_2$): **$46.80\text{ mol\%}$**
  - Propane ($C_3$): **$5.85\text{ mol\%}$**
  - Ethylene ($C_2H_4$): **$0.35\text{ mol\%}$**
- **Safety & Thermodynamic Margin:**
  - Mahalanobis Distance: **$D_M = 1.88$** (well within $95\%$ field confidence bound $D_M \le 3.0802$).
  - Nominal MITA: **$2.550^\circ\text{C}$** ($+1.050^\circ\text{C}$ operating margin above the $1.500^\circ\text{C}$ trip threshold).
  - Statistical Compliance: Pinch violation probability is **$4.57\% < 5.0\%$**, satisfying the strict one-sided 95% confidence limit ($P_5 = 1.527^\circ\text{C} \ge 1.500^\circ\text{C}$).
- **Quantified Annual Benefits:**
  - **Shaft Power Reduction:** **$13.92\text{ GWh/yr}$** ($1.92\%$ total Train H energy reduction).
    - MCR Compressors (4K-2/3): $9.22\text{ GWh/yr}$ ($66.2\%$).
    - Propane Compressor (4K-1): $4.70\text{ GWh/yr}$ ($33.8\%$).
  - **Motive Steam Savings:** **$58.37\text{ kt/yr}$** (IAPWS-IF97 basis, $4.193\text{ t/MWh}$).
  - **Boiler Fuel Gas Savings:**
    - ASME PTC 4.1 Basis ($97.70\text{ Nm}^3/\text{t}$): **$5.703\text{ MNm}^3/\text{yr}$**.
    - DCS Field Basis ($79.76\text{ Nm}^3/\text{t}$): **$4.656\text{ MNm}^3/\text{yr}$**.
  - **IPCC Greenhouse Gas Abatement:**
    - ASME Basis: **$11,595.3\text{ t CO}_2/\text{yr}$**.
    - Field Basis: **$9,464.9\text{ t CO}_2/\text{yr}$**.
  - **Commercial Valuation (Asian LNG Contract @ USD 10.50/MMBtu):**
    - ASME Basis: **USD 2.059 million / yr**.
    - Field Basis: **USD 1.681 million / yr**.
  - **Implementation Cost & Readiness:** **ZERO CAPEX**, requires zero new software or APC licenses; operable immediately via standard Yokogawa Centum VP manual setpoint trim.

#### Decision B: Conditional Long-Term Target — Candidate B (APC Implementation)
- **Composition:** $N_2 = 4.10\%$, $C_1 = 41.20\%$, $C_2 = 47.30\%$, $C_3 = 7.15\%$, $C_2H_4 = 0.25\%$.
- **Potential Savings:** **$16.85\text{ GWh/yr}$** (USD 1.68M to 2.49M / yr).
- **Operational Condition:** Requires commissioning a dedicated Supervisory Multivariable APC system (12-18 months lead time, USD 250k-400k CAPEX) to continuously ride the tighter $+0.345^\circ\text{C}$ MITA margin.

#### Decision C: Rejection of Candidate A ($C_3 = 10.00\%$)
- **Status: REJECTED.** 44.1% probability of temperature pinch violation under real plant measurement uncertainty ($u_c = 0.622^\circ\text{C}$). It represents an unphysical artifact of surrogate boundary arrest.

---

### 3. Synergistic Factorial Interaction
Simultaneous optimization of circulation flow and mixed refrigerant composition unlocks a non-linear thermodynamic synergy:
$$\Delta E_{\text{int}} = \mathbf{+1.77\text{ GWh/yr}} \quad (+10.5\%\text{ of total joint savings})$$
proving that joint optimization achieves energy efficiency gains unobtainable through isolated single-variable tuning.
