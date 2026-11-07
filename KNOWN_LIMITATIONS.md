# BADAK LNG PLANT-5 TRAIN H : KNOWN LIMITATIONS & OPERATIONAL BOUNDARIES
## Comprehensive Technical Boundaries, Domain Extrapolations & Governance Invariants

**Document Classification:** Process Safety & Technical Boundaries Specification  
**Facility Scope:** PT Badak NGL, Plant-5 Train H (Liquefaction)  
**System Designation:** C3MR Decision-Support Suite  
**Operating Boundary:** Open-Loop Advisory Decision Support (Read-Only : Zero Direct DCS Actuation)  
**Governing Standard:** AGENTS.md (Hukum Anti-Dosa Rekayasa Mutlak) & Master Prompt §7  

---

## 1. Executive Summary & Regulatory Scope

This document registers the technical limits, operational domain boundaries, physical assumptions, and known constraints of the Badak LNG Plant-5 Train H C3MR Decision-Support Suite. In accordance with industrial process safety standards (API 521, IEC 61511) and AGENTS.md:
1. **Advisory Decision Support Only:** AI model recommendations must never be interpreted as an automated substitute for licensed process engineering review or plant safety instrumentation systems (SIS).
2. **Read-Only Invariant:** The software operates exclusively in open-loop advisory mode. Direct write access to Yokogawa Centum VP DCS, SIS, PLCs, or field equipment is physically and logically barred.
3. **Fail-Safe Integrity:** When required physical inputs or plant limits are unavailable or corrupted, the system marks the calculation as `TIDAK DAPAT DIEVALUASI` (NOT EVALUATED) with null rates, avoiding misleading false-zero indicators.

---

## 2. Technical Limitations & Operational Boundaries

### L-01: Read-Only Advisory Scope (No Closed-Loop Actuation)
- **Limitation:** The software does not connect directly to DCS field controllers, SIS interlocks, or valve positioners. It cannot write setpoints or trigger valve movements.
- **Operator Requirement:** All recommendations (e.g. adjusting MCR circulation flow to $480.0\text{ t/h}$ or injecting make-up refrigerant) must be verified by the Board Operator and executed manually in the Yokogawa Centum DCS console following Badak LNG Standard Operating Procedures (SOP).
- **Safety Integrity:** Air-gapped decision support ensures that software faults, network disconnects, or numerical non-convergence can never directly cause process upsets or compressor trips.

### L-02: Operational Feed Flow Training Domain ($141.2 - 296.4\text{ t/h}$)
- **Limitation:** The surrogate model was trained on 1,475 actual Plant-5 Train H operational shifts spanning treated gas flow rates between $141.2\text{ t/h}$ and $296.4\text{ t/h}$ ($185.8 - 389.9\text{ kNm}^3/\text{h}$ feed gas).
- **Behavior Outside Domain:** 
  - For feed rates $< 141.2\text{ t/h}$ (deep plant curtailment) or $> 296.4\text{ t/h}$ (above nameplate design rating), the model flags `extrapolated = True` and displays a `TRAIN H DESIGN CAPACITY WARNING` banner.
  - The SLSQP optimizer clamps boundary lookups to the nearest certified Pareto anchor point ($141.2\text{ t/h}$ or $296.4\text{ t/h}$), enforcing the conservative anti-surge safety floor ($480.0\text{ t/h}$).
- **Mitigation:** Operators must exercise heightened caution during extreme plant curtailment ($< 140\text{ t/h}$) and verify suction temperatures manually.

### L-03: Compositional Geometry & Mahalanobis Distance Envelope ($D_M \le 3.0802$)
- **Limitation:** Recommendations are strictly constrained to the 95% historical operational ellipsoid in 4D Isometric Log-Ratio space:
  $$D_M = \sqrt{(\boldsymbol{\xi} - \boldsymbol{\mu}_{\xi})^T \boldsymbol{\Sigma}_{\xi}^{-1} (\boldsymbol{\xi} - \boldsymbol{\mu}_{\xi})} \le 3.080216$$
- **Behavior Outside Envelope:** If a plant snapshot exhibits $D_M > 3.0802$ (due to severe off-spec make-up contamination or prolonged chromatographic drift), the system marks the state as `in_domain = False` and displays a warning banner.
- **Mitigation:** Unprecedented refrigerant recipes outside the historical ellipsoid require Management of Change (MOC) process engineering review.

### L-04: Ambient Temperature Range ($24.0^\circ\text{C} - 34.5^\circ\text{C}$)
- **Limitation:** The training dataset reflects equatorial maritime coastal conditions in Bontang, East Kalimantan, where wet-bulb and dry-bulb temperatures stay within $24.0^\circ\text{C} - 34.5^\circ\text{C}$.
- **Behavior Outside Domain:** Extreme atypical weather conditions (ambient $< 20.0^\circ\text{C}$ during severe monsoon storms or $> 37.0^\circ\text{C}$ under extreme heat events) are outside the training envelope and may introduce minor bias in propane condenser duty predictions.

### L-05: Equipment Fouling and Non-Darcy Hydraulic Assumptions
- **Limitation:** Hydraulic pressure drop correlations for MCHE warm bundle (`H5PDI003`) and cold bundle (`H5PDI004`) reflect normal clean-to-moderately-fouled operations:
  $$\Delta P_{\text{warm}} \le 0.280\text{ kg/cm}^2, \quad \Delta P_{\text{cold}} \le 0.120\text{ kg/cm}^2$$
- **Behavior Under Heavy Fouling:** In the event of heavy hydrocarbon freeze-out, compressor oil carryover, or wax accumulation inside the MCHE shell, actual pressure drops may exceed model estimates.
- **Mitigation:** When $\Delta P$ exceeds DCS High Alarm limits ($0.28\text{ kg/cm}^2$), the decision-support system immediately flags a **BLOCKED** hydraulic safety alarm and advises MCHE derime/defrost procedures.

### L-06: Centrifugal Compressor Steady-State Floor ($480.0\text{ t/h}$)
- **Limitation:** The optimizer enforces a conservative steady-state flow floor of $480.0\text{ t/h}$ across all loads. Detailed dynamic compressor surge curves (head vs inlet volumetric flow vs guide vane angle) require high-speed live transmitter telemetry not available in 1-minute averaged supervisory data.
- **Mitigation:** The $480.0\text{ t/h}$ floor incorporates a 10% safety margin above the highest surge line flow of casings 4K-2 and 4K-3.

### L-07: Discrete Laboratory GC Sampling Schedule
- **Limitation:** Plant routine gas chromatography for MCR (`comp_4C-8`) is sampled on a per-shift schedule (3 times daily). Real-time minute-by-minute compositional changes during dynamic make-up injections rely on calculated inventory integration.
- **Mitigation:** The make-up advisory calculator provides recommended injection rates for slow, controlled transitions over 2-4 hours, allowing shift laboratory GC to verify compositional targets before further adjustments.

### L-08: Multi-Strategy Trade-Off Limitations
- **Strategy A (FIXED_RECIPE):** Suboptimal at deep underload; cannot customize the cooling curve to eliminate pinch gaps when feed drops below $200\text{ t/h}$.
- **Strategy B (CONDITION_DEPENDENT):** Can require large make-up gas quantities if loop composition is significantly different from target. Requires verified availability of make-up stocks.
- **Strategy C (MINIMUM_INTERVENTION):** Balances energy versus transition material, but convergence to global optimum is dependent on user-selected $\alpha_{\text{trim}}$ (nominal 0.30).

---

## 3. Technical Limitations Summary Matrix

```
+-----+----------------------+---------------------+----------------------------+-----------------------------------+----------+
| ID  | Parameter / Feature  | Operational Limit   | Behavior Beyond Limit      | Safety Mitigation                 | Status   |
+-----+----------------------+---------------------+----------------------------+-----------------------------------+----------+
| L-01| DCS Architecture     | Read-Only Advisory  | N/A (Write path absent)    | Human board operator in the loop  | VERIFIED |
| L-02| Feed Gas Flow Rate   | 141.2 - 296.4 t/h   | Flagged extrapolated=True  | Bounded by anti-surge floor       | VERIFIED |
| L-03| MCR Composition (DM) | DM <= 3.0802        | Flagged in_domain=False    | Enforced by SLSQP inequality      | VERIFIED |
| L-04| Ambient Temperature  | 24.0 - 34.5 deg C   | Statistical warning        | Monitored via tag 00TI001         | VERIFIED |
| L-05| MCHE Shell Delta P   | Warm <= 0.280 kg/cm2| Triggers BLOCKED alarm     | Advises plant derime protocol     | VERIFIED |
| L-06| Anti-Surge Floor     | m_dot_MR >= 480 t/h | Hard floor enforced        | 4UV-53 kickback valve modulation  | VERIFIED |
| L-07| Suction Temperature  | T_suct >= -45.0 degC| Hard TAL safety constraint | 4TV-510 reheat valve modulation   | VERIFIED |
| L-08| Power Decomposition  | Condensate ratio    | Secondary metric           | Total Train H power audited       | VERIFIED |
| L-09| GC Sampling Rate     | Discrete (3x/day)   | Dynamic inventory model    | Controlled 2-4 hr transition      | VERIFIED |
| L-10| Make-Up Input Guard  | Molar sum 85-115%   | Status TIDAK DAPAT DIEVALU | Null flow rates (zero false zeros)| VERIFIED |
+-----+----------------------+---------------------+----------------------------+-----------------------------------+----------+
```
