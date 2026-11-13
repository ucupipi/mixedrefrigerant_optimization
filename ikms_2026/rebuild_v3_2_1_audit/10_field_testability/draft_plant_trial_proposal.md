# CONCEPTUAL PLANT TRIAL PROTOCOL: TRAIN H C3MR OPTIMIZATION
## PT Badak NGL — Engineering Management of Change (MOC) Specification
**Rebuild v3.2.1 Independent Forensic Qualification**

---

### 1. Trial Objectives & Scope
The objective is to execute a phased, risk-controlled plant trial on Badak LNG Train H C3MR refrigeration to validate the energy reduction predicted by Rebuild v3.2.1.
- **Phase 1 Trial (Immediate Deployment):** Candidate R ($N_2: 4.50\%$, $C_1: 42.50\%$, $C_2: 46.80\%$, $C_3: 5.85\%$, $C_2H_4: 0.35\%$). Operates via manual DCS setpoint trims with zero software CAPEX.
- **Phase 2 Trial (Long-Term Conditional):** Candidate B ($N_2: 4.10\%$, $C_1: 41.20\%$, $C_2: 47.30\%$, $C_3: 7.15\%$, $C_2H_4: 0.25\%$). Requires commissioning of supervisory multivariable APC.

---

### 2. Pre-Trial Prerequisites & Verification Checklist
1. **Instrument Recalibration**:
   - Class A Pt100 RTDs on MCHE (`H4TI004B`, `H4TI016`, `H4TI001`, `H4TI008`) recertified within $\pm 0.20^\circ\text{C}$.
   - Pressure transmitters on 4K-2 and 4K-3 suction headers zero-checked within $\pm 0.05\text{ bar}$.
   - Online gas chromatograph for MCR stream calibrated against standard certified blend.
2. **Deethanizer Overhead Ethane Makeup Readiness**:
   - Verify 3C-5 overhead manual block valve operation and line purging.
   - Confirm pure propane and nitrogen injection header availability.
3. **Control System Interlock Verification**:
   - Confirm CCC anti-surge controller response time ($< 50\text{ ms}$) on kickback valve `4UV-53`.
   - Confirm suction drum 4C-7 Temperature Alarm Low (TAL) trip setpoint at **$-45.0^\circ\text{C}$**.
   - Confirm `4TV-510` suction reheat valve modulates proportionally when suction temperature falls below $-38.0^\circ\text{C}$.

---

### 3. Step-by-Step Field Execution Procedure (Phase 1: Candidate R)

```
[Step 1: Steady-State Baseline Stabilization (24 Hours)]
  - Hold Train H at stable feed flow (P50 baseload: ~370 t/h).
  - Record 24-hour baseline: DCS steam flows (H4FI029A, H4FI030A, H4FI031A),
    casing power, suction temperatures, MCHE delta-T, and GC analyses.
                         │
                         ▼
[Step 2: Composition Transition (12-16 Hours)]
  - Target: Candidate R recipe (C3: 5.85 mol%, C2: 46.80 mol%, C1: 42.50 mol%).
  - Action: Trim ethane makeup from 3C-5 overhead.
  - Rate of Change: Maximum composition drift rate <= 0.2 mol% per hour.
  - Monitor: Online GC routine every 2 hours; verify Mahalanobis distance D_M <= 1.90.
                         │
                         ▼
[Step 3: Load-Dependent Circulation Trim (8-12 Hours)]
  - Action: Gradually adjust 4FIC-001.SP according to the Candidate R circulation schedule.
  - Step Size: Decrement MCR mass circulation by 10 t/h per 30-minute interval.
  - Constraint Verification: At each step, confirm nominal MITA >= 2.40 °C.
                         │
                         ▼
[Step 4: 72-Hour Steady Performance Run]
  - Collect minute-level telemetry for power, steam, MCHE temperatures, and fuel gas.
  - Compare measured shaft power against direct simulator prediction (target: -1.77 MW at P50).
```

---

### 4. Hard Safety Interlocks & Abort Criteria
The plant trial shall be **IMMEDIATELY ABORTED** and MCR circulation restored to baseline if any of the following boundaries are breached:
1. **MCHE Minimum Temperature Approach (MITA)**:
   - *Abort Threshold:* Local calculated approach $\text{MITA} \le 1.650^\circ\text{C}$ (Trigger manual feed-forward circulation boost; auto-abort at $1.500^\circ\text{C}$).
2. **Compressor Suction Flow**:
   - *Abort Threshold:* Total 4K-2 suction flow $< 480.0\text{ t/h}$. If `4UV-53` fails to open, manual trip override required.
3. **Suction Drum Temperature**:
   - *Abort Threshold:* Temperature `H4TI004B` $\le -40.0^\circ\text{C}$ (Interlock trips at $-45.0^\circ\text{C}$).
4. **Turbine Governor Stroke**:
   - *Abort Threshold:* 4HKT-3 governor valve stroke $> 95.0\%$.
5. **Vibration Limits**:
   - *Abort Threshold:* Compressor shaft radial vibration $> 45\,\mu\text{m}$ pk-pk.

---

### 5. Post-Trial Evaluation & Reporting
- Reconcile steam turbine shaft work differences using machine-specific IAPWS-IF97 formulations.
- Reconcile boiler fuel gas flow reduction against ASME PTC 4.1 and DCS field baselines.
- Document trial results in formal Badak LNG Performance Trial Report for MOC closure.
