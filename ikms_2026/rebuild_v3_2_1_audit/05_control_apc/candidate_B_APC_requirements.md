# CANDIDATE B: ADVANCED PROCESS CONTROL (APC) REQUIREMENTS SPECIFICATION
## Badak LNG Train H C3MR Energy Efficiency Research — Rebuild v3.2.1

### 1. Control Philosophy & Justification
Candidate B ($C_3 = 7.15\text{ mol\%}$, nominal MITA $= 1.845^\circ\text{C}$) delivers high annual energy savings ($16.85\text{ GWh/yr}$, USD 7.14M/yr). However, its operating margin above the $1.500^\circ\text{C}$ MCHE temperature pinch threshold is only $+0.345^\circ\text{C}$ ($0.55\,\sigma$).

Under combined sensor calibration errors, pressure transmitter drift, and Peng-Robinson EOS liquid enthalpy uncertainty ($u_c = 0.622^\circ\text{C}$), Candidate B exhibits an open-loop **pinch violation probability of 28.9%**.

Therefore, Candidate B **CANNOT be safely operated using manual operator setpoint trims**. It strictly requires a dedicated Supervisory Multivariable Predictive Controller (APC) to continuously ride the constraint.

### 2. Functional Differentiation: CCC Anti-Surge vs Supervisory APC
A critical forensic distinction must be maintained:
1. **Existing CCC (Compressor Controls Corporation) Anti-Surge System**:
   - Execution rate: 10 to 50 milliseconds (sub-second fast execution).
   - Dedicated protective controller operating kickback valve `4UV-53`.
   - Objective: Prevent compressor aerodynamic surge under flow transients and machine trips.
   - Status: Active, certified, and immutable.
2. **Proposed Supervisory Multivariable APC (e.g., Aspen DMC3 / Honeywell RMPCT)**:
   - Execution rate: 30 to 60 seconds (supervisory supervisory loop).
   - Manipulated Variables (MVs):
     - `4FC001.SP`: MCR total mass circulation rate.
     - Refrigerant injection trim valves (pure C1, C2, C3 makeup valves).
     - Propane chiller level setpoints (3E-14, 3E-17, 3E-18).
   - Controlled Variables (CVs):
     - `MCHE_MITA`: Calculated 100-slice minimum temperature approach (Floor $\ge 1.50^\circ\text{C}$).
     - `H4TI004B`: MCR suction drum temperature (Floor $\ge -45.0^\circ\text{C}$, Soft constraint $\ge -38.0^\circ\text{C}$).
     - `4KT3_GOV`: 4HKT-3 turbine governor valve stroke (Ceiling $\le 94.0\%$).
     - `4K2_SUCT_FLOW`: Compressor 4K-2 suction flow (Floor $\ge 480.0\text{ t/h}$).
   - Disturbance Variables (DVs):
     - Train H natural gas feed flow (`FI-001`).
     - Feed gas composition and temperature.
     - Ambient wet-bulb cooling water temperature.

### 3. Engineering Limitation & Qualification Status
- **Status: CONCEPTUAL STEADY-STATE ONLY.**
- The proposed APC architecture for Candidate B has **NOT** undergone dynamic step-testing, empirical transfer-function identification, or closed-loop disturbance rejection testing.
- Commissioning requires:
  1. Formal Management of Change (MOC) approval.
  2. Baseline dynamic plant step tests (3 to 4 weeks of controlled PRBS perturbations).
  3. Empirical FIR/ARX model identification and state-space controller synthesis.
  4. Hardware-in-the-loop (HIL) simulation on the Yokogawa Centum VP test bench.
  5. Estimated project timeline: 12 to 18 months; estimated cost: USD 250,000 to USD 400,000.
