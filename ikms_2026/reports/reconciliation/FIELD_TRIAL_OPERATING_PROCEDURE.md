# PT BADAK NGL TRAIN H C3MR: FIELD-TESTABLE TRIAL OPERATING PROCEDURE (MOP-H04-OPT)
## Engineering Protocol for Controlled Plant Operating Trial on Mixed Refrigerant Optimization

**Governance:** Badak LNG Process Safety Management & Management of Change (MOC) Protocols  
**Scope:** Controlled Field Implementation of Model-Predicted MCR Optimization on Train H  
**Status:** Pre-Trial Engineering Specification (Model-Predicted Operating Recommendation)  
**Notice:** This document constitutes a technical proposal for an engineering evaluation. Actual plant execution is strictly subject to formal Badak LNG Operations Approval, Process Hazard Analysis (PHA), and Plant Management of Change (MOC) clearance.

---

## 1. OBJECTIVE & SCOPE OF TRIAL

The purpose of this procedure is to specify the operational steps required to test the single model-predicted C3MR optimization solution on Train H under controlled conditions. The objective is to verify predicted driver steam reduction (**9.68 t/h weighted**, corresponding to **2.40 MW shaft power**) while preserving 100% mechanical and aerodynamic integrity across all three refrigeration compressors (4K-1, 4K-2, 4K-3).

---

## 2. SUMMARY OF RECOMMENDED OPTIMIZATION SOLUTION

### 2.1 Recommended Mixed Refrigerant Recipe
The optimized composition maintains high subcooling driving force at the cold end while optimizing condensation duty at the warm end:
- **Nitrogen ($N_2$):** **$3.77 \pm 0.15\text{ mol\%}$** (Baseline: $3.20\text{ mol\%}$)
- **Methane ($C_1$):** **$42.22 \pm 0.50\text{ mol\%}$** (Baseline: $43.35\text{ mol\%}$)
- **Ethane ($C_2$):** **$43.67 \pm 0.50\text{ mol\%}$** (Baseline: $45.65\text{ mol\%}$)
- **Ethylene ($C_2H_4$):** **$1.53 \pm 0.20\text{ mol\%}$** (Baseline: $0.12\text{ mol\%}$)
- **Propane ($C_3$):** **$8.82 \pm 0.30\text{ mol\%}$** (Baseline: $7.67\text{ mol\%}$)
- **Mahalanobis Distance:** $D_M = 1.84$ (Threshold $\chi^2_{0.95, 4} = 3.0802$). Fully within historical operating envelope.

### 2.2 Circulation-Rate Schedule vs LNG Production Load
| Production Load Regime | Feed Gas Flow (`H1FI0009`) | LNG Production Rate | Baseline MCR Circulation | Recommended MCHE MCR Flow | 4K-2/3 Compressor Suction Flow | 4UV-53 Kickback Position | 4TV-510 Reheat Position | Predicted Steam Reduction |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseload (P90)** | $303.8\text{ t/jam}$ ($402\text{ kNm}^3/\text{h}$) | $265.4\text{ t/jam}$ | $927.1\text{ t/jam}$ | **$769.7\text{ t/jam}$** | $769.7\text{ t/jam}$ | Fully Closed | Minimum ($\le 1.0\%$) | **$13.25\text{ t/jam}$** |
| **High Load (P75)** | $279.7\text{ t/jam}$ ($370\text{ kNm}^3/\text{h}$) | $244.3\text{ t/jam}$ | $895.7\text{ t/jam}$ | **$705.4\text{ t/jam}$** | $705.4\text{ t/jam}$ | Fully Closed | Minimum ($\le 1.0\%$) | **$11.80\text{ t/jam}$** |
| **Mid Load (P50)** | $217.8\text{ t/jam}$ ($288\text{ kNm}^3/\text{h}$) | $190.3\text{ t/jam}$ | $720.5\text{ t/jam}$ | **$559.4\text{ t/jam}$** | $559.4\text{ t/jam}$ | Fully Closed | Modulating ($2\text{--}4\%$) | **$8.90\text{ t/jam}$** |
| **Turndown (P25)** | $166.8\text{ t/jam}$ ($221\text{ kNm}^3/\text{h}$) | $145.7\text{ t/jam}$ | $690.3\text{ t/jam}$ | **$436.8\text{ t/jam}$** | **$480.0\text{ t/jam}$** | Armed ($43.2\text{ t/jam}$) | Modulating ($12\text{--}15\%$) | **$7.20\text{ t/jam}$** |
| **Turndown (P10)** | $141.2\text{ t/jam}$ ($187\text{ kNm}^3/\text{h}$) | $123.4\text{ t/jam}$ | $690.1\text{ t/jam}$ | **$373.6\text{ t/jam}$** | **$480.0\text{ t/jam}$** | Armed ($106.4\text{ t/jam}$) | Active ($18\text{--}22\%$) | **$6.50\text{ t/jam}$** |

---

## 3. PRE-TRIAL PREREQUISITES & SAFETY ENVELOPE

Prior to commencing the trial:
1. **Instrument Calibration Check:**
   - Verify zero and span for condensate meters `H4FI031A` (4G-3), `H4FI029A` (4G-4), and `H4FI030A` (4G-5).
   - Calibrate suction temperature transmitter `H4TI004B` and differential pressure transmitters `5PDI-003` and `5PDI-004`.
   - Perform online calibration of gas chromatograph for 4C-8 MCR composition.
2. **Anti-Surge & Governor Validation:**
   - Confirm anti-surge controller `4UV-53` is in automatic cascade mode with margin trigger $\ge 10.0\%$.
   - Confirm suction drum reheat controller `4TC-4B` (`4TV-510`) is in automatic with setpoint $-42.0^\circ\text{C}$ (ensuring $\ge 3.0^\circ\text{C}$ buffer above TAL $-45.0^\circ\text{C}$).
   - Confirm 4KT-1 governor is locked at $3,040 \pm 20\text{ RPM}$.
3. **MOC Approval:**
   - Formally sign off Temporary Operating Procedure under Badak LNG MOC Policy.

---

## 4. STEP-BY-STEP TRIAL EXECUTION PROTOCOL

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        FIELD TRIAL EXECUTION PHASES (TRAIN H C3MR)                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                    │
         ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
         ▼                                          ▼                                          ▼
┌─────────────────────────────────┐        ┌─────────────────────────────────┐        ┌─────────────────────────────────┐
│     PHASE 1: STABLE BASELINE    │        │    PHASE 2: COMPOSITION SHIFT   │        │   PHASE 3: FLOW OPTIMIZATION    │
├─────────────────────────────────┤        ├─────────────────────────────────┤        ├─────────────────────────────────┤
│• 24-hr steady-state logging     │───────►│• Incremental makeup injection   │───────►│• Stepwise MCR reduction (25 t/h)│
│• Measure steam, power, fuel gas │        │  (N2/C3 trim per shift)         │        │• Monitor SM, TAL, rundown temp  │
│• Verify surge margin >= 20%     │        │• Confirm DM <= 2.50 via lab GC  │        │• Settle 4 hrs per step          │
└─────────────────────────────────┘        └─────────────────────────────────┘        └─────────────────────────────────┘
```

### Phase 1: Baseline Characterization (24 Hours)
- Record steady-state operating parameters at stable feed gas rate:
  - Feed Gas Flow (`H1FI0009`), LNG Production Rate, Rundown Temp (`H5TIC01A`).
  - Total Steam Flow (`H4FI031A` + `H4FI029A` + `H4FI030A`) and Boiler Fuel Gas (`31FIC0321-329`).
  - Compressor speeds (`H4SI018A`, `H4SI023A`, `H4SI028A`) and suction pressures.

### Phase 2: Composition Adjustment (12 to 24 Hours)
- Adjust MCR composition gradually towards the recommended recipe via standard makeup headers:
  - Inject Nitrogen makeup to raise $N_2$ to $3.77\%$.
  - Adjust Propane makeup to bring $C_3$ to $8.82\%$.
  - Perform shift-level GC sampling every 4 hours to verify convergence.
  - Maintain Mahalanobis distance $D_M \le 2.50$ throughout the transition.

### Phase 3: Stepwise Circulation Reduction
- Reduce MCR mass circulation rate in discrete decrements of **$25.0\text{ t/jam}$ every 4 hours**:
  - Monitor LNG rundown temperature (`H5TIC01A` target: $-158.0 \pm 1.0^\circ\text{C}$).
  - Monitor MCHE warm-end approach ($T_{\text{mcr,in}} - T_{\text{suct}} \ge 2.0^\circ\text{C}$).
  - If LNG temperature begins to rise above $-157.0^\circ\text{C}$, pause flow decrement.
  - At turndown loads ($< 165\text{ t/h}$ LNG), confirm `4UV-53` kickback modulates open automatically to keep total suction flow $\ge 480.0\text{ t/h}$.

---

## 5. HARD REVERSION AND EMERGENCY ABORT CRITERIA

The field trial must be **immediately suspended, and operating conditions reverted to baseline**, if any of the following conditions occur:

1. **Surge Margin Alarm:**
   - Any compressor section surge margin drops below **$+8.0\%$** on 4K-1, or below **$+10.0\%$** on 4K-2/4K-3.
2. **Suction Temperature Low (TAL Risk):**
   - Suction drum 4C-7 temperature (`H4TI004B`) drops to **$-43.5^\circ\text{C}$** ($1.5^\circ\text{C}$ above TAL $-45.0^\circ\text{C}$) without immediate recovery from `4TV-510`.
3. **MCHE Pinch / Temperature Crossover:**
   - Differential temperature across any MCHE bundle approaches $\Delta T < 1.5^\circ\text{C}$ or warm-end approach $< 1.5^\circ\text{C}$.
4. **LNG Rundown Off-Spec:**
   - LNG product temperature warms above **$-156.0^\circ\text{C}$** or storage tank flash gas increases abnormally.
5. **Driver Vibration / Mechanical Anomaly:**
   - Shaft vibration exceeds API 617 alarm threshold ($28.0\text{ }\mu\text{m}$ peak-to-peak).
   - Bearing temperature exceeds $105.0^\circ\text{C}$.

---

## 6. FIELD MONITORING & PERFORMANCE VERIFICATION

To verify the predicted savings during the trial:
- **Measured Variable:** Avoided steam flow $\Delta \dot{m}_{\text{steam}} = \dot{m}_{\text{steam,base}} - \dot{m}_{\text{steam,trial}}$ at equivalent feed throughput.
- **Boiler Fuel Gas Verification:** Measured delta $\Delta \dot{V}_{\text{FG}} = \text{FIC0321-329}_{\text{base}} - \text{FIC0321-329}_{\text{trial}}$. Expected marginal response: **$76.98\text{ Nm}^3/\text{ton steam}$**.
- **Model Uncertainty Tolerance:** A trial result within **$\pm 8.5\%$** of predicted values ($9.68 \pm 0.82\text{ t/h}$ steam reduction) constitutes statistical validation of the model.

