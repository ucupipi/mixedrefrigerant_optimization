# BADAK LNG PLANT-5 TRAIN H : OBJECTIVE AND CONSTRAINT REGISTER
## Rigorous Industrial Parameter Classification, Mathematical Formulation & Safety Margins

**Document Classification:** Engineering Process Safety & Mathematical Register  
**Facility Scope:** PT Badak NGL, Plant-5 Train H (Liquefaction)  
**System Designation:** C3MR Liquefaction Optimization Engine  
**Operating Boundary:** Open-Loop Advisory Decision Support (Read-Only : Zero Direct DCS Actuation)  
**Governing Standard:** AGENTS.md (Hukum Anti-Dosa Rekayasa Mutlak) & Engineering Manual Book  

---

## 1. Executive Summary & Battery Limits

This register establishes the authoritative mathematical formulation, objective criteria, 5-tier parameter classifications, and constraint residual boundaries for the Badak LNG Plant-5 Train H C3MR decision-support engine.

### Explicit Battery Limit Definition
In accordance with AGENTS.md Pasal 10, all power and specific energy calculations encompass the entire Train H C3MR battery limit:
$$\dot{W}_{\text{shaft, total}} = \dot{W}_{\text{MCR, direct}} + \dot{W}_{\text{C3, precooling}}$$
- **MCR Compression Circuit:** Centrifugal compressors 4K-2 (LP casing) and 4K-3 (HP casing), driven by mechanical drive steam turbines 4KT-2 and 4KT-3.
- **Propane Precooling Circuit:** Propane compressor 4K-1 (3-stage suction: High, Medium, Low), driven by steam turbine 4KT-1. Propane duty includes chilling treated natural gas feed and condensing mixed refrigerant in exchangers 3E-14, 3E-17, and 3E-18.

---

## 2. Five-Tier Parameter Classification

The process variables within the Train H decision-support suite are structured into five distinct engineering categories to prevent cross-contamination between disturbances, control actions, and dependent states.

```
+-------------------------------------------------------------------------------------------------------+
| Category 1: Disturbance Inputs (Uncontrolled boundary conditions imposed on Train H)                  |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Parameter           | DCS Tag / Source  | Unit       | Design Range  | Engineering Significance       |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Treated Feed Gas    | H3FI0004 x 0.760  | t/h        | 141.2 - 296.4 | Natural gas mass feed rate     |
| Mass Flow Rate      | (or H1FI012)      |            | (nom. 245.8)  | into MCHE 5E-1 tube bundle     |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Feed Gas            | Plant-3 GC Stream | mol%       | N2: 0.05-0.15 | Gas composition setting dew    |
| Composition         | AI25A - AI25G     |            | C1: 94.0-95.0 | point, bubble point, and       |
|                     |                   |            | C2: 2.50-3.00 | latent heat in MCHE            |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Sea Water Cooling   | Sea Water Header  | deg C      | 26.0 - 32.0   | Primary heat sink setting      |
| Temperature         | Plant Common      |            | (nom. 28.5)   | propane condensing pressure    |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Category 2: Decision Variables (Advisory variables optimized by the calculation engine)               |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Parameter           | DCS Tag / Sensor  | Unit       | Operating Span| Optimization Role              |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Circulation     | H4FI011B x 36.8   | t/h        | 480.0 - 750.0 | Total refrigerant mass rate;   |
| Flow Rate           |                   |            |               | subject to anti-surge floor    |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Nitrogen (N2)   | comp_4C-8_N2      | mol%       | 0.70 - 7.80   | Sets coldest boiling point     |
| Mole Fraction       |                   |            | (nom. 3.39)   | at MCHE cold end (-152.5 deg C)|
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Methane (C1)    | comp_4C-8_C1      | mol%       | 39.10 - 52.67 | Governs subcooling bundle duty |
| Mole Fraction       |                   |            | (nom. 44.45)  | and suction drum temperature   |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Ethane (C2)     | comp_4C-8_C2      | mol%       | 31.67 - 51.06 | Middle refrigeration carrier;  |
| Mole Fraction       |                   |            | (nom. 45.02)  | bulk liquefaction duty         |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Ethylene (C2H4) | comp_4C-8_C2H4    | mol%       | 0.00 - 4.50   | Volatility tuning component    |
| Mole Fraction       |                   |            | (nom. 0.85)   | for warm/cold transition pinch |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCR Propane (C3)    | comp_4C-8_C3      | mol%       | 0.00 - 10.11  | Heavy refrigeration carrier;   |
| Mole Fraction       |                   |            | (nom. 6.29)   | MCHE warm bundle bottom boiling|
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Category 3: Dependent State Variables (Mechanical and physical responses of the liquefaction loop)    |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Parameter           | DCS Tag / Sensor  | Unit       | Normal Range  | Process Constraint Check       |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Compressor Suction  | H4TI004B          | deg C      | -41.5 to -35.0| Interlock boundary:            |
| Temperature         |                   |            | (TAL -45.0)   | Prevents liquid droplet carryover|
+---------------------+-------------------+------------+---------------+--------------------------------+
| Compressor Suction  | H4PI013           | kg/cm2 G   | 2.70 - 3.10   | MCR LP compressor 4K-2 suction |
| Pressure            |                   |            |               | pressure balance               |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCHE Warm Bundle DP | H5PDI003          | kg/cm2     | 0.12 - 0.25   | High Alarm: 0.280 kg/cm2       |
|                     |                   |            |               | Hydraulic flooding prevention  |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCHE Cold Bundle DP | H5PDI004          | kg/cm2     | 0.04 - 0.10   | High Alarm: 0.120 kg/cm2       |
|                     |                   |            |               | Hydraulic limit check          |
+---------------------+-------------------+------------+---------------+--------------------------------+
| MCHE Rundown Temp   | H5TI008           | deg C      | -152.0 - -154 | Target subcooled temperature   |
|                     |                   |            |               | before rundown flash valve     |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Category 4: Coupled Product Output (Governed by phase equilibrium thermodynamics)                     |
+---------------------+-------------------+------------+---------------+--------------------------------+
| Parameter           | DCS Tag / Source  | Unit       | Nominal Value | Thermodynamic Coupling         |
+---------------------+-------------------+------------+---------------+--------------------------------+
| LNG Rundown         | H5FI6A /          | t/h LNG    | 232.3 t/h     | Rigorous PR-EOS VLE balance in |
| Production Flow     | Flash Drum 5C-1   |            | (at 245.8 feed| 5C-1 separator: LNG liquid     |
|                     | calculation       |            | feed)         | product fraction ~94.5% mass   |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Category 5: Constraint Residuals (Direct margin verification: value >= 0 indicates compliance)        |
+---------------------+-----------------------------------+------------+--------------------------------+
| Margin Parameter    | Mathematical Definition           | Safe Limit | Residual Requirement           |
+---------------------+-----------------------------------+------------+--------------------------------+
| Suction TAL Margin  | R_TAL = T_suct - (-45.0 deg C)    | >= 0.0 deg | Strict positive margin         |
+---------------------+-----------------------------------+------------+--------------------------------+
| Anti-Surge Margin   | R_surge = m_dot_MR - 480.0 t/h    | >= 0.0 t/h | Mechanical floor compliance    |
+---------------------+-----------------------------------+------------+--------------------------------+
| Superheat Margin    | R_SH = T_suct - T_dew - 3.0 deg C | >= 0.0 deg | Dry vapor entering impeller    |
+---------------------+-----------------------------------+------------+--------------------------------+
| Mahalanobis Margin  | R_Maha = 3.080216 - D_M           | >= 0.0     | Inside 95% operating ellipsoid |
+---------------------+-----------------------------------+------------+--------------------------------+
| MITA Approach Margin| R_MITA = MITA - 1.50 deg C        | >= 0.0 deg | Zero temperature crossover     |
+---------------------+-----------------------------------+------------+--------------------------------+
| Simplex Closure Res | R_Simplex = 0.01 - |100 - sum(y)| | >= 0.0 mol%| Exact molar mass conservation  |
+-------------------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulation of the Optimization Problem

### 3.1 Objective Function
The primary objective is the minimization of total Train C3MR shaft power, augmented with log-barrier penalty functions for boundary violation prevention:
$$\min_{\mathbf{z}, \dot{m}_{\text{MR}}} \Phi(\mathbf{z}, \dot{m}_{\text{MR}}) = \dot{W}_{\text{total, C3MR}}(\mathbf{z}, \dot{m}_{\text{MR}}) - \mu_{\text{barrier}} \sum_{k=1}^K \ln\left(g_k(\mathbf{z}, \dot{m}_{\text{MR}})\right) + \mathcal{P}_{\text{strategy}}(\mathbf{z})$$

where:
- $\dot{W}_{\text{total, C3MR}} = \dot{W}_{\text{MCR}} + \dot{W}_{\text{C3}}$ is evaluated via the certified surrogate model (Gradient Boosted Trees with monotonic physical constraints).
- $\mu_{\text{barrier}} = 10^{-4}$ is the barrier regularization parameter.
- $g_k \ge 0$ represents the inequality constraints.
- $\mathcal{P}_{\text{strategy}}(\mathbf{z})$ is the strategy-specific regularization term:
  - For `CONDITION_DEPENDENT`: $\mathcal{P} \equiv 0$.
  - For `FIXED_RECIPE`: $\mathbf{z} \equiv \mathbf{z}_{\text{certified}}$, decision space reduces to $\dot{m}_{\text{MR}}$.
  - For `MINIMUM_INTERVENTION`: $\mathcal{P} = \lambda_{\text{trans}} \cdot D_M^2(\mathbf{z}, \mathbf{z}_{\text{actual}})$.

### 3.2 Specific Energy Consumption (SEC) Formulation
To ensure uncompromised engineering clarity, two distinct Specific Energy Consumption metrics are computed and reported:
1. **Specific Shaft Power per Feed ($SEC_{\text{feed}}$):**
   $$SEC_{\text{feed}} = \frac{\dot{W}_{\text{total, C3MR}} \times 1000}{F_{\text{feed}}} \quad [\text{kWh / t Feed}]$$
2. **Specific Energy Consumption per LNG Rundown ($SEC_{\text{LNG}}$):**
   $$SEC_{\text{LNG}} = \frac{\dot{W}_{\text{total, C3MR}} \times 1000}{F_{\text{LNG}}} \quad [\text{kWh / t LNG}]$$
   where $F_{\text{LNG}}$ is measured by Coriolis meter `H5FI6A` or calculated via flash drum 5C-1 thermodynamic equilibrium.

---

## 4. Constraint Residual Invariants & Verification

The decision-support system recalculates all constraint residuals dynamically on every request. A recommendation is approved for operator presentation if and only if all residuals are non-negative:
$$\min\left(R_{\text{TAL}}, \, R_{\text{surge}}, \, R_{\text{SH}}, \, R_{\text{Maha}}, \, R_{\text{MITA}}, \, R_{\text{Simplex}}\right) \ge 0.0$$

Any negative residual immediately trips the UI status badge to a safety violation alert and suppresses the `Apply AI Target` recommendation.
