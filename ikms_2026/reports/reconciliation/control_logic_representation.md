# PT BADAK NGL TRAIN H C3MR: CONTROL-LOGIC AND OPERATING PHILOSOPHY SPECIFICATION
## Reconciling Physics-Based Flowsheet Simulation with Field DCS Automation (IKMS 2026)

**Governance:** AGENTS.md (Pasal 1, 5, 8, 9, 10, 12, 13) | Zero AI Jargon | Plain Industrial Engineering Language  
**Scope:** Operating Philosophy, Instrument Loops, Surge Envelope, and Re-governing Feasibility for Train H  
**Reference Source:** Badak LNG Plant 4 (MCR BOOK-5), Plant 5 (Liquefaction BOOK-6), Dresser-Rand OEM Manuals (`H4K-1.pdf`, `H4K-2.pdf`, `H4K-3.pdf`), and DCS Telemetry (110,137 minute records).

---

## 1. Executive Summary: The Field Controllability Principle

A fundamental defect in classical process optimization is assuming all simulation parameters are "free decision variables" in the field. In an industrial baseload LNG facility like PT Badak NGL Train H, rotating equipment and cryogenic heat exchangers are strictly constrained by automated DCS control loops, OEM anti-surge systems, and hardwired safety interlocks.

This document formalizes the exact control logic of Train H to establish:
1. **Case A (Current-Control Optimization / Achievable Field Saving):** Optimization strictly within existing DCS governor loops, maintaining 4KT-1 speed constant, respecting compressor surge floors ($480.0\text{ t/h}$), and engaging suction reheat / kickback valves during turndown.
2. **Case B (Proposed Control Modification / Advanced Re-governing Potential):** Evaluating the physical and aerodynamic feasibility of re-governing 4KT-1 to capture propane precooling credits, and defining its OEM mechanical limitations.

---

## 2. Equipment-by-Equipment Control Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        BADAK LNG TRAIN H REFRIGERATION CONTROL INTERACTION                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                    │
         ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
         ▼                                          ▼                                          ▼
┌─────────────────────────────────┐        ┌─────────────────────────────────┐        ┌─────────────────────────────────┐
│     PROPANE SYSTEM (4K-1/4KT-1) │        │    LP MCR SYSTEM (4K-2/4KT-2)   │        │    HP MCR SYSTEM (4K-3/4KT-3)   │
├─────────────────────────────────┤        ├─────────────────────────────────┤        ├─────────────────────────────────┤
│• Driver: Steam Turbine H4KT-1   │        │• Driver: Steam Turbine H4KT-2   │        │• Driver: Steam Turbine H4KT-3   │
│• Control: Isochronous Governor  │        │• Control: Variable Speed PIC/FIC│        │• Control: Variable Speed PIC    │
│• DCS Speed: Locked ~3,000 RPM   │        │• Operating Speed: 4,383-4,631   │        │• Operating Speed: 4,370-4,626   │
│  (Mean: 3,040 ± 39 RPM)         │        │  RPM (89.9% - 95.0% MCS)        │        │  RPM (90.4% - 95.7% MCS)        │
│• Suction: 3-stage cascade       │        │• Suction: 4C-7 Suction Drum     │        │• Suction: 4C-8 Interstage Drum  │
│  (1.49, 3.75, 7.35 kg/cm²A)     │        │  (H4PI014B: ~3.16 kg/cm²A)      │        │  (H4PI016B: ~15.5 kg/cm²A)      │
│• Protection: Armed Kickback     │        │• Protection: 4UV-53 Kickback    │        │• Discharge: Water Coolers 4E-6  │
│  (SM >= 8.0% design limit)      │        │• Interlock: TAL >= -45.0 °C     │        │  (H4PI017B: ~53.6 kg/cm²A)      │
└─────────────────────────────────┘        └─────────────────────────────────┘        └─────────────────────────────────┘
```

### 2.1 Propane Compressor (4K-1) & Turbine Driver (4KT-1)
- **OEM Machine:** Dresser-Rand 939B6/4 (Horizontally split, 6 impellers across 3 stages: LP, MP, HP).
- **Operating Philosophy:**
  - 4K-1 supplies refrigeration to chill both natural gas feed (4E-10, 4E-12, 4E-14, 4E-40) and mixed refrigerant (4E-7, 4E-8, 4E-9).
  - The turbine driver `H4KT-1` is equipped with a mechanical-hydraulic governor set to maintain a virtually constant operating speed:
    $$\bar{N}_{\text{4KT-1}} = 3.039{,}98\text{ RPM} \quad (\sigma = 39{,}29\text{ RPM})$$
    Across all 110,137 active operational minutes, speed varies by only $\pm 1{,}3\%$.
  - Turbine steam consumption (`H4FI031A`) modulates automatically via the governor steam rack to satisfy the torque demand imposed by the three suction stages (`H4PIC002`, `H4TI001A`, `H4TI002A`).
- **Controllability Assessment:**
  - Under current plant operations, operators **do not re-govern or adjust the speed setpoint** of 4KT-1 during load changes.
  - Furthermore, 4K-1 is subject to OEM surge limits: Section 1 minimum volumetric flow is $142.753\text{ m}^3/\text{h}$, corresponding to a minimum mass flow floor of $223{,}66\text{ t/h}$ (giving an armed kickback margin of $+8{,}00\%$).
  - **Critical Finding:** Reducing MCR circulation from $927\text{ t/h}$ to $769\text{ t/h}$ reduces heat duty on MCR chillers 4E-7/8/9, but the natural gas chillers 4E-10/12/14/40 continue to operate at duties dictated by the feed gas throughput. Consequently, 4K-1 shaft power cannot drop by $18{,}15\text{ MW}$ (60.7%) without driving 4K-1 into destructive aerodynamic surge. The maximum realistic power reduction on 4K-1 under safe surge buffers ($\text{SM} \ge 8{,}0\%$) is **$1{,}48\text{ s.d. }2{,}50\text{ MW}$**, not $18{,}15\text{ MW}$.

### 2.2 LP Mixed Refrigerant Compressor (4K-2) & Driver (4KT-2)
- **OEM Machine:** Dresser-Rand 838B4 (Radially split barrel casing, 4 impellers).
- **Operating Philosophy:**
  - 4K-2 takes vapor from the suction drum 4C-7 and compresses it from $\sim 3{,}16\text{ kg/cm}^2\text{A}$ to $\sim 15{,}65\text{ kg/cm}^2\text{A}$.
  - The driver `H4KT-2` operates with speed modulation ($4.383{,}6\text{ to }4.631{,}0\text{ RPM}$, $89{,}96\%\text{ to }95{,}03\%\text{ MCS}$), tracking MCR mass circulation demand and suction pressure.
- **Safety Interlocks & Anti-Surge Constraints:**
  1. **Minimum Flow Floor ($480{,}0\text{ t/h}$):** OEM surge line establishes an aerodynamic minimum suction flow of $480{,}0\text{ t/h}$. If MCHE process demand drops below this threshold (e.g. $373{,}55\text{ t/h}$ at P10 turndown), secondary kickback valve `4UV-53` modulates open to recirculate $107{,}59\text{ t/h}$, maintaining compressor throughput at $604{,}68\text{ t/h}$ ($+26{,}0\%$ safety margin above surge).
  2. **Suction Drum Low Temperature Alarm / Interlock (TAL $\ge -45{,}0^\circ\text{C}$):**
     - Low suction temperatures risk droplet condensation in 4C-7 and liquid carryover into the 4K-2 impeller.
     - Controller `4TC-4B` acts on reheat valve `4TV-510` (hot gas bypass from 4K-2 discharge to 4C-7 inlet). When turndown chills MCHE return vapor (reaching $-71{,}68^\circ\text{C}$ unmitigated), `4TV-510` injects warm vapor to keep $T_{\text{suct}} \ge -41{,}5^\circ\text{C}$ to $-21{,}1^\circ\text{C}$, fully compliant with TAL.

### 2.3 HP Mixed Refrigerant Compressor (4K-3) & Driver (4KT-3)
- **OEM Machine:** Dresser-Rand 656B7-6 (Radially split barrel casing, 7 impellers).
- **Operating Philosophy:**
  - 4K-3 compresses interstage vapor from 4C-8 from $\sim 15{,}45\text{ kg/cm}^2\text{A}$ to $\sim 53{,}65\text{ kg/cm}^2\text{A}$.
  - Driver `H4KT-3` speed modulates from $4.369{,}6\text{ to }4.625{,}7\text{ RPM}$ ($90{,}37\%\text{ to }95{,}67\%\text{ MCS}$).
  - Compressor discharge is desuperheated and condensed across propane chiller 4E-9 and cooling water coolers 4E-6 before routing to high-pressure separator 4C-8 and MCHE 5E-1.

---

## 3. Distinction of Two Optimization Scenarios

To maintain complete transparency and intellectual honesty as mandated by AGENTS.md (Pasal 8, 9, 10, 12):

### Scenario 1: Case A — Current-Control Optimization (Direct Field Achievable)
- **Definition:** Optimization of MCR composition ($N_2, C_1, C_2, C_2H_4, C_3$) and circulation rate strictly executable by plant operators using current DCS setpoints without modifying turbine governors or plant control software.
- **Rules:**
  - 4KT-1 speed held constant at baseline (`H4SI018A` = baseline).
  - Propane compressor savings bounded by aerodynamic surge margin ($\Delta \dot{W}_{4K-1} \le 1{,}5\text{--}2{,}5\text{ MW}$).
  - 4K-2 and 4K-3 optimized with MCR surge floor ($480{,}0\text{ t/h}$) and TAL interlock ($-45{,}0^\circ\text{C}$) fully enforced.
  - **Predicted Total Shaft Power Saving:** **$4{,}14\text{ to }6{,}64\text{ MW}$** ($34.300\text{ to }55.000\text{ t steam/year}$).

### Scenario 2: Case B — Proposed Control-System Modification (Thermodynamic Potential with Advanced Re-governing)
- **Definition:** Upgrading the plant control philosophy to allow co-optimization of 4KT-1 speed governor in tandem with MCR composition.
- **Rules:**
  - 4KT-1 governor re-tuned to throttle speed proportionally to reduced total chiller duty, subject to the $8{,}0\%$ minimum surge buffer.
  - Direct MCR savings ($10{,}83\text{ MW}$ at P90) are augmented by validated bounded propane savings ($4{,}50\text{ to }6{,}00\text{ MW}$).
  - **Predicted Total Shaft Power Saving:** **$15{,}33\text{ to }16{,}83\text{ MW}$**.
  - **Note on Legacy 28.98 MW Claim:** The unconstrained $28{,}98\text{ MW}$ claim (incorporating $18{,}15\text{ MW}$ propane credit) is classified as an **idealized unconstrained thermodynamic potential** that violates the OEM surge envelope of 4K-1 and cannot be realized in the field without extensive equipment redesign.
