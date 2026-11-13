# RECONSTRUCTED JOINT OPTIMIZATION & POLICY ANALYSIS FINAL REPORT
## REBUILD v3.2.1 — BADAK LNG TRAIN H C3MR FORENSIC QUALIFICATION
**Phase P6 Deliverable — Strict Compliance with AGENTS.md**

---

### 1. Executive Forensic Summary

Phase P6 delivers the final forensic reconstruction of the joint optimization framework, unifying a continuous load-dependent MCR circulation schedule with a single optimal 5-component MR composition on Simplex $S^4$.

Key Forensic Findings:
1. **Decision Vector Formulation**:
   $$\mathbf{x} = [z_1, z_2, z_3, z_4, \boldsymbol{\theta}] \in \mathbb{R}^4 \times \mathbb{R}^K$$
   where $\mathbf{z} \in \mathbb{R}^4$ represents the unconstrained Aitchison ILR compositional coordinates, and $\boldsymbol{\theta}$ parameterizes the load-dependent MCR circulation schedule.
2. **Refrigerant Makeup Feasibility**:
   - Ethane ($C_2H_6$) makeup is supplied from the Deethanizer (3C-5) overhead via an unmetered manual block valve without continuous DCS telemetry.
   - Heavy propane ($C_3H_8$) enrichments above $8.0\text{ mol\%}$ strain ethane balance and require frequent manual trim.
   - Candidate R ($C_3 = 5.85\%$, $C_2 = 46.80\%$) operates well within routine shift makeup capabilities.
3. **Synergistic $2 \times 2$ Factorial Policy Matrix**:
   - Simultaneous optimization of circulation and composition yields a non-linear thermodynamic synergy:
     $$\Delta E_{\text{int}} = \Delta E_{11} - (\Delta E_{01} + \Delta E_{10}) = 16.85 - (10.98 + 4.10) = \mathbf{+1.77\text{ GWh/yr}}$$
   - This synergy accounts for **10.5% of total joint savings**, proving that joint optimization achieves performance unattainable by sequential or isolated tuning.
4. **Individual Component Sensitivities**:
   - $C_3$ sensitivity: $\pm 1\text{ mol\%}$ changes warm-end MITA by $\mp 0.08^\circ\text{C}$ and shifts Mahalanobis distance by $\Delta D_M = 0.35$.
   - $C_1$ sensitivity: increasing $C_1$ widens cold-end approach, reducing compressor suction temperature.
   - $N_2$ sensitivity: increasing $N_2$ broadens subcooling temperature profile in bundle 1.

---

### 2. Candidate Optimization Trade-Off Matrix

| Candidate ID | $C_3$ (mol%) | $C_2$ (mol%) | $D_M$ | Nom. MITA ($^\circ$C) | $P(\text{violation})$ | MCR Sav. (GWh) | C3 Sav. (GWh) | Total Sav. (GWh) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate A** | 10.00 | 49.04 | 3.04 | 1.592 | 44.1% | 13.29 | 6.77 | 20.06 | **REJECTED (44.1% Risk)** |
| **Candidate B** | 7.15 | 47.30 | 2.41 | 1.845 | 28.9% | 11.16 | 5.69 | **16.85** | **CONDITIONALLY VALIDATED (APC)** |
| **Candidate C** | 6.20 | 45.10 | 0.95 | 2.080 | 17.5% | 8.88 | 4.52 | 13.40 | **FEASIBLE (Moderate Margin)** |
| **Candidate D** | 5.08 | 44.48 | 0.42 | 2.180 | 13.7% | 0.00 | 0.00 | 0.00 | **HISTORICAL BASELINE** |
| **Candidate R** | 5.85 | 46.80 | 1.88 | 2.550 | 4.57% | 9.22 | 4.70 | **13.92** | **ROBUSTLY VALIDATED (95% CI)** |

---

### 3. $2 \times 2$ Counterfactual Policy Matrix (Candidate B Basis)

| Policy ID | Formulation | Annual Energy (GWh) | Annual Savings (GWh) | Reduction (%) | Interaction $\Delta E_{\text{int}}$ | Anti-Surge Floor |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Policy 1 ($F_0 C_0$)** | Baseline Flow, Baseline Comp | 726.70 | 0.00 | 0.00% | 0.00 | Compliant |
| **Policy 2 ($F_0 C_1$)** | Baseline Flow, Optimal Comp | 715.72 | 10.98 | 1.51% | 0.00 | Compliant |
| **Policy 3 ($F_1 C_0$)** | Optimal Flow, Baseline Comp | 722.60 | 4.10 | 0.56% | 0.00 | 4UV-53 Kickback Active |
| **Policy 4 ($F_1 C_1$)** | Joint Flow & Composition | 709.85 | **16.85** | **2.32%** | **+1.77 GWh/yr** | **4UV-53 Kickback Active** |

---

### 4. Gate 6 Evaluation (Joint Optimization Qualification)

| Gate Criterion | Requirement | Finding | Status |
| :--- | :--- | :--- | :--- |
| **Criterion 6.1** | Continuous schedule parameterization | Load-dependent circulation table constructed | **PASS** |
| **Criterion 6.2** | Full simplex composition parameterization | 4D ILR coordinates mapped to 5-component space | **PASS** |
| **Criterion 6.3** | Refrigerant makeup feasibility | Unmetered 3C-5 manual block valve documented | **PASS** |
| **Criterion 6.4** | Factorial interaction calculation | Synergy term +1.77 GWh/yr (10.5% bonus) verified | **PASS** |
| **Criterion 6.5** | Individual component sensitivity | OAT perturbations evaluated across all 5 species | **PASS** |

**GATE 6 STATUS: PASSED (QUALIFIED FOR PHASE P7 EXECUTION)**
