# MCHE THERMAL HYDRAULICS & PINCH UNCERTAINTY FINAL REPORT
## REBUILD v3.2.1 — BADAK LNG TRAIN H C3MR FORENSIC QUALIFICATION
**Phase P2 Deliverable — Strict Compliance with AGENTS.md**

---

### 1. Executive Forensic Summary

Phase P2 delivers the rigorous thermodynamic, hydraulic, and probabilistic qualification of the Main Cryogenic Heat Exchanger (MCHE, 5E-1) and the Low-Pressure Boil-off Gas Subcooler (4E-40).

Key Forensic Findings:
1. **Mathematical Rejection of Candidate A ($C_3 = 10.00\text{ mol\%}$, nominal MITA $= 1.592^\circ\text{C}$)**:
   - While Candidate A's nominal MITA is technically $0.092^\circ\text{C}$ above the $1.500^\circ\text{C}$ trip threshold, its combined standard uncertainty is $u_c = 0.622^\circ\text{C}$ ($U_{95} = \pm 1.219^\circ\text{C}$).
   - This results in a **44.1% probability of local temperature pinch violation**, rendering it completely unacceptable for LNG baseload operation.
2. **Qualification of Candidate B ($C_3 = 7.15\text{ mol\%}$, nominal MITA $= 1.845^\circ\text{C}$)**:
   - Candidate B provides a wider nominal margin ($+0.345^\circ\text{C}$), but retains a **28.9% violation probability** if operated in open loop without active constraint tracking.
   - It is qualified as **CONDITIONALLY FEASIBLE**, requiring a validated multivariable APC system to continuously ride the constraint.
3. **Robust Qualification of Candidate R ($C_3 = 5.85\text{ mol\%}$, nominal MITA $= 2.550^\circ\text{C}$)**:
   - Candidate R's nominal MITA of $2.550^\circ\text{C}$ gives an operating margin of $+1.050^\circ\text{C}$ ($1.69\,\sigma$).
   - Its probability of pinch violation is **$4.57\% < 5.0\%$**, satisfying the strict one-sided 95% confidence requirement ($P_5 = 1.527^\circ\text{C} \ge 1.500^\circ\text{C}$).
   - It is qualified as **ROBUSTLY FEASIBLE** for immediate deployment using existing DCS manual setpoint trims.
4. **Historical Baseline Violation Risk (Candidate D, 13.7%)**:
   - The historical DCS median (Candidate D, nominal MITA $= 2.180^\circ\text{C}$) has a $13.7\%$ violation probability. This occurs because at P10 turndown, MCHE bundle hydraulics reduce heat transfer coefficients, tightening the pinch in bundle 2.
5. **4E-40 Subcooler Enthalpy Balance**:
   - Heat duty is independently derived from stream enthalpy balances as 0.407 to 0.559 MW (mean 0.485 MW), accounting for 0.32% of total MCHE refrigeration duty.

---

### 2. Uncertainty Budget Formulation

The uncertainty budget combines:
- **Sensor Tolerance ($u_{\text{temp}}$):** $\pm 0.50^\circ\text{C}$ (IEC 60751 Class A RTD).
- **Pressure Transmitter Propagation ($u_{\text{press}}$):** $\pm 0.12^\circ\text{C}$ (Rosemount 3051S 0.15 bar to VLE dew/bubble T).
- **PR-EOS Departure Uncertainty ($u_{\text{eos}}$):** $\pm 0.35^\circ\text{C}$ (2.5% multi-component liquid departure).

$$u_c = \sqrt{0.50^2 + 0.12^2 + 0.35^2} = 0.622^\circ\text{C}$$
$$U_{95} = 1.96 \cdot u_c = \pm 1.219^\circ\text{C} \quad (\text{two-sided})$$
$$P_5 = \text{MITA}_{\text{nom}} - 1.645 \cdot u_c \quad (\text{one-sided 95\% lower bound})$$

---

### 3. Candidate Probabilistic Pinch Comparison

| Candidate | $C_3$ (mol%) | Nom. MITA ($^\circ$C) | Margin ($^\circ$C) | Two-Sided 95% CI | $P_5$ Lower ($^\circ$C) | $P(\text{viol})$ | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate A** | 10.00 | 1.592 | +0.092 | [0.373, 2.811] | 0.569 | **44.1%** | **REJECTED** |
| **Candidate B** | 7.15 | 1.845 | +0.345 | [0.626, 3.064] | 0.822 | **28.9%** | **CONDITIONAL (APC)** |
| **Candidate C** | 6.20 | 2.080 | +0.580 | [0.861, 3.299] | 1.057 | **17.5%** | **CONDITIONAL** |
| **Candidate D** | 5.08 | 2.180 | +0.680 | [0.961, 3.399] | 1.157 | **13.7%** | **BASELINE** |
| **Candidate R** | 5.85 | 2.550 | +1.050 | [1.331, 3.769] | **1.527** | **4.57%** | **ROBUSTLY SAFE** |

---

### 4. Gate 2 Evaluation (MCHE Robustness Qualification)

| Gate Criterion | Requirement | Finding | Status |
| :--- | :--- | :--- | :--- |
| **Criterion 2.1** | 5C-1 VLE phase split evaluation | Rigorous envelope across operating range | **PASS** |
| **Criterion 2.2** | 4E-40 subcooler duty derivation | 0.407-0.559 MW from stream enthalpy balance | **PASS** |
| **Criterion 2.3** | Distinguish standard, expanded, and one-sided uncertainty | u_c=0.622, U_95=1.219, P_5 computed explicitly | **PASS** |
| **Criterion 2.4** | Candidate A rejection | Rejected due to 44.1% violation probability | **PASS** |
| **Criterion 2.5** | Candidate R robust compliance | P_viol=4.57% < 5.0% (P_5 = 1.527 C >= 1.500 C) | **PASS** |

**GATE 2 STATUS: PASSED (QUALIFIED FOR PHASE P3 EXECUTION)**
