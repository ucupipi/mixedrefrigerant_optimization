# CANDIDATE R: PASSIVE DCS SETPOINT OPERATION ASSESSMENT
## Badak LNG Train H C3MR Energy Efficiency Research — Rebuild v3.2.1

### 1. Robust Engineering Philosophy
Candidate R ($C_3 = 5.85\text{ mol\%}$, nominal MITA $= 2.550^\circ\text{C}$) was synthesized specifically to eliminate dependency on complex supervisory APC systems.

By selecting an operating point with a $+1.050^\circ\text{C}$ ($1.69\,\sigma$) buffer above the $1.500^\circ\text{C}$ pinch limit:
- Its one-sided 95% lower confidence limit is:
  $$P_5 = 2.550^\circ\text{C} - 1.645 \cdot 0.622^\circ\text{C} = 1.527^\circ\text{C} \ge 1.500^\circ\text{C}$$
- Its probability of temperature pinch violation is **$4.57\% < 5.0\%$**, fully compliant with the ISO/IEC Guide 98-3 (GUM) one-sided 95% confidence criterion.

### 2. Implementation via Existing DCS Architecture
Candidate R does **NOT** require new controller software, multivariable algorithms, or vendor licenses:
1. **DCS DCS Loop Integration**:
   - Operates entirely within standard Yokogawa Centum VP regulatory control blocks.
   - Operators adjust the master MCR circulation flow controller setpoint (`4FIC-001.SP`) according to the static load-dependent schedule.
   - Mixed refrigerant composition is maintained by standard shift makeup adjustments based on routine 8-hour gas chromatography (GC) analyses.
2. **Dynamic Stability & Disturbance Tolerance**:
   - The $+1.050^\circ\text{C}$ nominal buffer absorbs typical feed gas flow fluctuations ($\pm 5\%$ to $\pm 10\%$) without breaching the pinch boundary.
   - Suction drum temperature `H4TI004B` remains between $-37.2^\circ\text{C}$ and $-36.5^\circ\text{C}$, safely above the $-45.0^\circ\text{C}$ TAL trip threshold.
   - Compressor kickback valve `4UV-53` handles turndown flows smoothly at P10 using existing CCC logic.

### 3. Immediate Field Testability
- **CAPEX:** $0.
- **Timeline:** Can be initiated immediately upon technical committee review.
- **Economic Value:** Captures $13.92\text{ GWh/yr}$ of energy savings (USD 5.90M/yr benefit), representing **82.6% of Candidate B's maximum theoretical savings** with zero capital expenditure and zero dynamic instability risk.
