# MANUSCRIPT CLAIM FORENSIC AUDIT REPORT
## Audit of Academic Manuscript Claims against Rebuild v3.2.1 Engineering Registers

### 1. Audit Scope & Methodology
An independent cross-examination was conducted comparing all textual, tabular, and graphical claims in the draft manuscript against the underlying Rebuild v3.2.1 calculation registers and CSV outputs.

### 2. Key Audit Findings & Textual Corrections

1. **Specific Steam Rate Attribution**:
   - *Draft Statement:* "Motive steam consumption is converted using a plant steam rate of 4.040 t/MWh."
   - *Audit Finding:* Erroneous. 4.040 t/MWh is an arithmetic quotient of total plant steam over lumped electrical equivalent. True physical weighted steam rate across the 3 driver casings (4KT-1, 4KT-2, 4KT-3) is **4.193 t/MWh** based on IAPWS-IF97 isentropic expansions.
   - *Correction:* Updated text to explicitly cite machine-specific steam rates (4.262, 4.183, 4.107 t/MWh) and the 4.193 t/MWh weighted average.
2. **Compressor Choke vs Turbine Governor Saturation**:
   - *Draft Statement:* "Baseload throughput is restricted by compressor aerodynamic choke at P90."
   - *Audit Finding:* Erroneous. Digitized Dresser-Rand OEM curves prove aerodynamic choke occurs at > 775 t/h (> 33% flow margin). The true operational bottleneck is **4HKT-3 turbine governor valve stroke (94.5% saturation)**.
   - *Correction:* Text and conclusions updated to identify governor valve saturation as the primary baseload limit.
3. **Candidate A Feasibility Status**:
   - *Draft Statement:* "Candidate A represents the global optimum, delivering 20.06 GWh/yr savings."
   - *Audit Finding:* Defective and dangerous. Candidate A ($C_3 = 10.00\%$, MITA $= 1.592^\circ\text{C}$) has a **44.1% probability of pinch crossover violation** under real plant measurement uncertainty ($u_c = 0.622^\circ\text{C}$).
   - *Correction:* Formally reclassified as **REJECTED**. Candidate R is designated as the primary immediate recommendation, with Candidate B as a conditional long-term APC target.
4. **Energy Closure Discrepancy (0.48 GWh/yr)**:
   - *Draft Statement:* "Component contributions sum to 20.54 GWh/yr against total savings of 20.06 GWh/yr."
   - *Audit Finding:* Discrepancy caused by `np.maximum(..., 0.0)` clipping of local turndown power adjustments.
   - *Correction:* Unclipped integration eliminates the clipping artifact; exact closure ($\sum \Delta E_k - \Delta E_{	ext{total}} = 0.000000	ext{ GWh/yr}$) is achieved across all candidates.
5. **Surrogate Training Generator Provenance**:
   - *Draft Statement:* "Surrogates were trained on a 2,500-run PR-EOS Latin Hypercube design of experiments."
   - *Audit Finding:* Erroneous. The script `p4_surrogate_rebuild.py` generated `physical_doe_training_dataset.csv` using closed-form algebraic formulas (`mita_val = 1.95 - 1.80*(ratio - 1.05)...`, `cop_c3 = ...`) with Gaussian noise, not direct PR-EOS calls.
   - *Correction:* Reclassified CLM-008 as `UNSUPPORTED`. Noted that holdout metrics validate regression accuracy on the synthetic formula, not empirical thermodynamic ground truth.
6. **Candidate Scaling Factors and Synergy Calculation**:
   - *Draft Statement:* "Candidate B delivers 16.85 GWh/yr and joint optimization achieves +1.77 GWh/yr synergy."
   - *Audit Finding:* Discovered that `p6_joint_optimization_v3_2_1.py` did not optimize Candidates B, C, D, R independently; it applied fixed scaling multipliers (0.840 for B, 0.694 for R) to Candidate A. Furthermore, the +1.77 GWh/yr synergy was computed by subtracting hardcoded terms `13.07*sf` and `4.88*sf`.
   - *Correction:* Formally classified CLM-011 as `UNSUPPORTED` and CLM-009/010 as `CONDITIONAL`.
7. **Baseline Power/Steam Circularity**:
   - *Draft Statement:* "DCS telemetry validates baseline compressor shaft power of 100.05 MW."
   - *Audit Finding:* In `baseline_hysys_vs_dcs_validation_p1_p100.csv`, `total_compressor_power_steam_MW` is exactly `total_driver_steam_t_h / 4.040` (std = 0.0001). The "power" column is a synthetic derivative of steam flow, not an independent shaft torque measurement.
   - *Correction:* Documented in forensic report. Machine-specific rates (4.262, 4.183, 4.107) are maintained as the correct IAPWS-IF97 expansion basis.
