# MCHE (5E-1 / 4C-8) Operational Reference Synthesis, Differential Pressure Dynamics, Thermal Safety Limits, and Thermodynamic Regime Analysis

**Author:** Technical Architecture & Process Engineering Group (Teamwork M6)  
**Target Unit:** Badak LNG Plant-5 Liquefaction Unit (Train-H Main Cryogenic Heat Exchanger 5E-1 & Plant-4 MCR Suction Drums 4C-7 / 4C-8)  
**Governance Compliance:** `AGENTS.md` (Pasals 1–13), `ORIGINAL_REQUEST.md` (§R1, §R2, §R3), `/unlazy`, `/ml-best-practices`  
**Date:** November 2026  
**Status:** Canonical Reference & Verification Synthesis  

---

## 1. Executive Summary

This research and reference synthesis establishes an exhaustive, first-principles and empirically grounded engineering specification for the Main Cryogenic Heat Exchanger (MCHE, designated **5E-1** in Plant-5 / Train-H, coupled with Multi-Component Refrigerant [MCR] suction drums **4C-7** and **4C-8** in Plant-4) at PT Badak NGL, Bontang, East Kalimantan, Indonesia.

Under changing feed gas conditions—ranging from high nameplate capacity baseload operation ($\ge 279.8\text{ t/h}$ treated gas, equivalent to $\ge 780\text{ m}^3\text{/h}$ LNG rundown) to deep turndown/underload conditions ($\le 226.8\text{ t/h}$ treated gas, representing a 20% to 50% capacity curtailment)—the liquefaction system experiences non-linear shifts in hydraulic resistance, two-phase vapor-liquid distribution, and cold-end thermal approaches.

This synthesis integrates:
1. **Mechanical and Equipment Specifications:** Verified design geometries, metallurgy, and pass arrangements from Badak LNG Operating Manuals `BOOK-6 (Plant-5_Liquefaction Unit)` and `BOOK-5 (Plant-4_MCR Refrigeration System)`.
2. **Operational Limits and Interlock Envelopes:** Differential pressure (dP) trip setpoints ($0.51–0.54\text{ kg/cm}^2$), alarm thresholds ($0.42\text{ kg/cm}^2$), suction drum Temperature Alarm Low ($\text{TAL} \ge -45.0^\circ\text{C}$), Temperature Alarm Low-Low trip ($\text{TALL} = -51.0^\circ\text{C}$), LNG rundown control ($-148.0^\circ\text{C}$ to $-150.0^\circ\text{C}$), Minimum Internal Temperature Approach ($\text{MITA} \ge 1.50^\circ\text{C}$), and Minimum Metal Design Temperature ($\text{MMDT} = -173.0^\circ\text{C}$).
3. **Empirical Ground Truth from Shift Historian Data (`master_shift_level.parquet`):** Forensic statistical analysis across 10,318 active shifts (including 2,587 underload, 5,150 transition, and 2,581 baseload shifts) establishing non-Darcy dP power-law scaling ($W^{1.497}$ warm, $W^{1.593}$ cold) and hydraulic ratio shifts ($\Delta P_{\text{warm}}/\Delta P_{\text{cold}}$ shifting from $2.41$ to $3.13$).
4. **Thermodynamic Coupling Mechanisms:** The physics of nitrogen bubble-point depression causing cold bundle temperature depression ($r = -0.6867$), and operator manual MCR adjustments (lowering $C_3$, elevating $C_1$) to prevent liquid pooling and suction drum freezing ($r = -0.7601$).

---

## 2. Equipment Nomenclature, Mechanical Architecture & Metallurgy

### 2.1 Multi-Train Equipment Coding & Nomenclature
In Badak LNG engineering taxonomy, equipment tags are strictly categorized by process plant section:
- **`5E-1` (or `H5E-1` for Train-H):** Main Cryogenic Heat Exchanger (MCHE), located in Plant-5 ("Liquefaction Unit"). This is an Air Products and Chemicals, Inc. (APCI) spool-wound coil heat exchanger (CWHE).
- **`5C-1`:** High Pressure MCR Separator drum, separating mixed refrigerant into heavy liquid bottoms and light vapor overhead.
- **`5C-2`:** LNG Flash Drum, flashing subcooled liquid LNG from 5E-1 rundown before atmospheric storage transfer.
- **`4C-7`:** MCR 1st Stage Suction Drum, knock-out vessel located in Plant-4 upstream of low-pressure MCR compressor `4K-2`.
- **`4C-8`:** MCR 2nd Stage Suction Drum, knock-out vessel located in Plant-4 upstream of high-pressure MCR compressor `4K-3`.
- **`4K-1` / `4KT-1`:** Propane Refrigeration Compressor and steam turbine driver (Plant-4).
- **`4K-2` / `4KT-2`:** MCR 1st Stage (LP) Centrifugal Compressor and steam turbine driver (Plant-4).
- **`4K-3` / `4KT-3`:** MCR 2nd Stage (HP) Centrifugal Compressor and steam turbine driver (Plant-4).

*(Citation Note: The prompt references "MCHE (4C-8)". In Badak LNG plant equipment coding, `4C-8` is the 2nd Stage MCR Suction Drum in Plant-4, while the MCHE itself is `5E-1` in Plant-5. Both vessels operate in closed thermodynamic coupling).*

### 2.2 Physical Geometry and Construction
*(Source: `BOOK-6 (Plant-5_Liquefaction Unit)`, Bab 2, Section 2.2.3, pp. 27–43)*
- **Manufacturer:** Air Products and Chemicals, Inc. (APCI).
- **Vessel Profile:** Vertical, two-stage cylindrical coil-wound shell with hemispherical heads.
- **Total Height:** **43.0 meters** from base skirt to top head.
- **Lower Section Diameter (Warm Bundle):** **4,458 mm** outer shell diameter.
- **Upper Section Diameter (Cold Bundle):** **2,498 mm** outer shell diameter.
- **Shell Transition:** Stepped swage conical transition between lower warm section and upper cold section.
- **Insulation:** Cryogenic expanded perlite and polyurethane cellular insulation ranging from **89 mm to 229 mm** thickness.
- **Tubing:** High-surface-area helically wound coils with an outer tube diameter of **15.0 mm** (wall thickness 1.25 mm).

### 2.3 Metallurgy and Cryogenic Ratings
*(Source: `BOOK-6 (Plant-5_Liquefaction Unit)`, Bab 2, pp. 30–35)*
- **Tubes and Tube Sheets:** Cryogenic Aluminum Alloy (ASTM B209/B210 alloy 5083-O or 3003-O). Aluminum alloys are selected because face-centered cubic (FCC) crystal structures exhibit no ductile-to-brittle transition temperature, maintaining high impact toughness down to absolute zero.
- **Internal Shell Distributors ("Chinese Hats"):** Fabricated aluminum conical splash plates welded directly to the central structural core mandrel.
- **Shell Plate:** Cryogenic low-temperature carbon steel (LTCS) or cryogenic aluminum with expansion bellows to absorb axial thermal contraction.
- **Design and Operating Limits:**
  - **Mechanical Design Pressure (Tube Side):** **62.2 kg/cm²g (885 psig)** across feed gas, heavy liquid MCR, and light vapor MCR circuits.
  - **Mechanical Design Pressure (Shell Side):** **10.55 kg/cm²g (150 psig)**, protected by relief valves `5PSV-26`, `5PSV-40`, and `5PSV-41` set at 10.55 kg/cm²g.
  - **Design Operating Temperature Range:** **-173.0°C to +65.6°C (-280°F to +150°F)**.
  - **Minimum Metal Design Temperature (MMDT / MDMT):** **-173.0°C**.

### 2.4 Internal Tube Pass Arrangement
- **Warm Bundle (Lower Stage):** 4 separate parallel tube passes:
  1. *Feed Gas Pass 1:* Pre-cooled natural gas from Scrub Column 3C-1 overhead entering at ~36.0 kg/cm²g and -34.0°C.
  2. *Feed Gas Pass 2:* Parallel feed gas coil entering at ~36.0 kg/cm²g and -34.0°C.
  3. *MCR Liquid Pass:* Subcooling heavy MCR liquid from 5C-1 bottom entering at ~42.0 kg/cm²g and -34.0°C.
  4. *MCR Vapor Pass:* Condensing light MCR vapor from 5C-1 overhead entering at ~42.0 kg/cm²g and -34.0°C.
- **Cold Bundle (Upper Stage):** 2 separate parallel tube passes:
  1. *Feed Gas Liquefaction Pass:* Continuing from warm bundle outlet (-120.0°C), fully condensing and subcooling natural gas into liquid LNG at -148.0°C to -150.0°C.
  2. *MCR Vapor Subcooling Pass:* Continuing from warm bundle outlet (-120.0°C), subcooling condensed light MCR liquid prior to light letdown JT valve `5PV-15`.

---

## 3. Operational Limits, Differential Pressure Thresholds & Safety Interlocks

### 3.1 Sensor Tag Directory & Sensing Architecture
*(Source: `BOOK-6 (Plant-5_Liquefaction Unit)`, pp. 47–52, 65–66; `CANONICAL_TAG_DICTIONARY.csv`)*

| DCS Tag | Parquet Column | Engineering Unit | Physical Measurement Location |
|:---|:---|:---|:---|
| **H5PDI003** | `pp_H5PDI003_mean` | kg/cm² | Shell-side differential pressure across **Warm Bundle** (Middle Shell to Bottom Shell). |
| **H5PDI004** | `pp_H5PDI004_mean` | kg/cm² | Shell-side differential pressure across **Cold Bundle** (Top Shell to Middle Shell). |
| **H5PDI25A** | `pp_H5PDI25A_mean` | kg/cm² | Redundant Warm Bundle dP safety transmitter, channel A (`5PDAHH-25A`). |
| **H5PDI25B** | `pp_H5PDI25B_mean` | kg/cm² | Redundant Warm Bundle dP safety transmitter, channel B (`5PDAHH-25B`, binding DCS trip). |
| **H5TI0025** | `pp_H5TI0025_mean` | °C | Cold Bundle MR vapor outlet tube temperature before JT valve `5PV-15`. |
| **H5TI0027** | `pp_H5TI0027_mean` | °C | Intermediate feed gas temperature between Warm Bundle outlet and Cold Bundle inlet. |
| **H5TI0029** | `pp_H5TI0029_mean` | °C | Subcooled LNG temperature exiting Cold Bundle tube pass upstream of flash letdown. |
| **H5TI0047** | `pp_H5TI0047_mean` | °C | High-pressure MCR vapor entering Warm Bundle bottom tube nozzle. |
| **H5TIC01A** | `pp_H5TIC01A_mean` | °C | Primary temperature control variable for rundown LNG entering Flash Drum 5C-2. |
| **H4TI004B** | `pp_H4TI004B_mean` | °C | Suction gas temperature entering 1st stage MCR compressor `4K-2` from drum 4C-7. |
| **H5TI0020** | `pp_H5TI0020_mean` | °C | MCHE top overhead vapor temperature (quarantined due to 2025/2026 sensor re-pointing). |

### 3.2 Operational Limits & Safety Interlock Threshold Matrix

| Parameter / Tag | Normal Range | Pre-Shutdown Alarm (`PDAH` / `TAL`) | Emergency Trip (`PDAHH` / `TALL`) | Action / Consequence | Direct Citation |
|:---|:---|:---|:---|:---|:---|
| **Warm Bundle dP (`H5PDI003`, `H5PDI25A/B`)** | 0.30–0.40 kg/cm² | **0.42 kg/cm²** | **0.51–0.54 kg/cm²** | 2oo2 voting trips 5E-1: isolates `5HV-21`, shuts `5FV-2`/`5PV-15`, opens kickback `4UV-53`. | `BOOK-6`, pp. 52, 65; Memo `156-BP31-2020-113` |
| **Cold Bundle dP (`H5PDI004`)** | 0.05–0.13 kg/cm² | 0.17 kg/cm² (monitoring) | None (non-limiting) | Monitored for heavy hydrocarbon / benzene freezing or liquid flooding. | `BOOK-6`, p. 45; Memo `156-BP31-2020-113`, p. 2 |
| **MCR Suction Temp (`H4TI004B`)** | -38.0°C to -42.0°C | **-45.0°C (`TAL`)** | **-51.0°C (`TALL`)** | At TAL (-45°C): open reheat `4TV-510`. At TALL (-51°C): 2oo3 trip of compressor `4KT-2`. | `BOOK-5`, pp. 16, 109; Iqbal Fauzan (2025), p. 67 |
| **LNG Rundown Temp (`H5TIC01A`)** | -148.0°C to -150.0°C | -152.0°C (low warning) | None (throttling limit) | Controls final subcooling; throttles `5PV-15` or trims MCR circulation. | `BOOK-6`, p. 53 |
| **Minimum Temperature Approach (MITA)** | 1.80°C to 4.50°C | **1.50°C (hard lower bound)** | 0.00°C (Temperature Crossover) | Halts heat transfer; violates Second Law of Thermodynamics; liquid carryover. | `AGENTS.md` Pasal 5; Pure-Python PR-EOS Engine |
| **Minimum Metal Design Temp (MMDT)** | -155.0°C to -162.0°C | -165.0°C | **-173.0°C** | Lowest permissible equipment temperature to prevent mechanical embrittlement. | `BOOK-6`, p. 32 |

### 3.3 Mechanical Failure Consequence of High Warm Bundle dP
*(Source: `BOOK-6 (Plant-5_Liquefaction Unit)`, Bab 2, pp. 65–66)*
The warm bundle dP trip threshold ($0.51\text{ kg/cm}^2$ general, $0.54\text{ kg/cm}^2$ in Train-H DCS interlock) is a strict mechanical structural constraint.
- Inside the MCHE shell, heavy liquid refrigerant from separator `5LR-3` is sprayed onto the warm tube bundle via an internal aluminum conical splash distributor ("chinese hat").
- The distributor plate is secured to the central mandrel by aluminum fillet welds.
- Excessive shell-side differential pressure ($\ge 0.51–0.54\text{ kg/cm}^2$) generates an upward aerodynamic drag force that exceeds the shear yield strength of the aluminum welds.
- In Badak LNG historical operation (documented in Train-A), weld failure caused the heavy distributor assembly to tear free and drop violently onto the underlying aluminum tube bundle, crushing and puncturing coils, causing severe cross-contamination between feed gas and refrigerant, and enforcing a multi-month total shutdown.

### 3.4 Upstream Impurity, Fractionation LPBS, Propane Precooling & Turbine Condenser Limits (`BOOK-1` to `BOOK-5`)
*(Sources: `BOOK-1 (Plant-1_Gas Purification)`, `BOOK-2 (Plant-2_Dehydration & Mercury Removal)`, `BOOK-3 (Plant-3_Fractionation Unit)`, `BOOK-4 (Plant-4_Propane Refrigeration System)`, `BOOK-5 (Plant-4_MCR Refrigeration System)`)*

| Subsystem / Equipment | Operational / Safety Parameter | Threshold / Design Spec | Direct Manual Book Citation |
|:---|:---|:---|:---|
| **Plant-1 Amine Absorber (`1C-2`)** | Treated gas $\text{CO}_2$ & $\text{H}_2\text{S}$ ceiling (`1AI-4`) | $\text{CO}_2 < 50\text{ ppmv}$, $\text{H}_2\text{S} < 4\text{ ppmv}$ (prevents solid $\text{CO}_2$ dry-ice plugging in 5E-1) | `BOOK-1`, Bab 2, pp. 2–5 |
| **Plant-2 Driers (`2C-2A/B/C`) & Hg Bed (`2C-4`)** | Moisture (`2AI-2`) & Mercury ceiling | $\text{H}_2\text{O} < 0.5\text{ ppmv}$ (`HAH = 1.0 ppmv`), $\text{Hg} < 0.01\text{ ppb}$ (prevents 5E-1 aluminum LME; `2C-4` $\Delta P \le 0.7\text{ kg/cm}^2$) | `BOOK-2`, pp. 3–6, 87–88 |
| **Plant-3 Scrub Column (`3C-1`) & LPBS (`4E-40`/`4C-40`)** | Minimum reflux (`3FSL-19` / `H3FIC003`) & Train G/H LPBS subcooling | Reflux $\ge 16.0\text{ m}^3/\text{h}$; Train G/H LPBS subcools `3C-1`/`4E-14` overhead with MCR to $-50.7^\circ\text{C}$ (`H3TI0176` / `H5TI0023` $-51.2^\circ\text{C}$) | `BOOK-3`, pp. 25, 29–31; `BOOK-5`, p. 8 |
| **Plant-4 Propane Compressor (`4K-1`)** | 3-Stage Anti-Surge Minimum Flow Floors (`4UIC-50/51/52` $\rightarrow$ `4UV-50/51/52`) | Stage 1 (`H4FI001A`) $\ge 155.0\text{ kNm}^3/\text{h}$; Stage 2 (`H4FI002B`) $\ge 55.0\text{ kNm}^3/\text{h}$; Stage 3 (`H4FI003B`) $\ge 38.0\text{ kNm}^3/\text{h}$ | `BOOK-4`, pp. 146–149 |
| **Plant-4 `4K-1` Suction & Desuperheater (`4E-1AB`)** | Stage 1 Suction Pressure (`H4PIC002`) & Desuperheater Outlet (`H4TI0296`) | `H4PIC002` normal $1.05–1.10\text{ kg/cm}^2\text{A}$ ($\ge 1.033\text{ kg/cm}^2\text{A}$ strictly positive to prevent O2 ingress); `H4TI0296` $\le 39.0^\circ\text{C}$; $C_3$ purity $> 97\text{ mol\%}$ | `BOOK-4`, pp. 3, 72, 149 |
| **Plant-4 HP MCR Evaporator (`4E-9`)** | Train E/F/H Level (`H4LIC012`) & MCR Outlet Temp (`H4TI0214`) | `H4LIC012` held at $0\%$ manually in Train E/F/H; propane cooling adequacy verified via `H4TI0214` $\approx -34.1^\circ\text{C}$ | `BOOK-4`, p. 95 |
| **Plant-4 MCR Compressors (`4K-2` / `4K-3`) & `4C-8`** | `4K-2` Disch Temp (`H4TI007B`), `4K-3` Disch Pressure (`H4PI017B`), `4C-8` Level | `4K-2` `TAH = 160°C`, `TAHH = 176°C`; `4K-3` normal $45–50\text{ kg/cm}^2\text{A}$, Train E–H `PAH = 54.0 kg/cm²`; `4C-8` `4PAL-41 = 4.3 kg/cm²G`, `4LAH-42 = 762 mm`, `4LAHH-43 Trip = 1753 mm` | `BOOK-5`, pp. 80, 103 |
| **Steam Turbine Surface Condensers (`4E-15/20/25`)** | Condenser Vacuum (`H4PI042/044/046`) & Hotwell Level (`H4LIC015/016/017`) | Normal $-600\text{ mmHg}$, `PAH = -500 mmHg`, `PAHH Trip = -380 mmHg`; Hotwell level normal $40–50\%$ (operating range $20–70\%$) | `BOOK-5`, pp. 128–151 |

---

## 4. Empirical Regime Analysis (Baseload vs Underload)

### 4.1 Sample Counts & Operating Regime Partitioning
Based on the empirical distribution of `treated_gas_mass_flow_t_h_mean` across 10,318 active production shifts (> 10.0 t/h) in `master_shift_level.parquet`:
- **Underload Regime ($W_{\text{feed}} \le 226.8\text{ t/h}$):** 2,587 active shifts (25.07% global; represents the 2025 deep turndown campaign).
- **Transition Regime ($226.8 < W_{\text{feed}} < 279.8\text{ t/h}$):** 5,150 active shifts (49.91% global; operating interquartile band).
- **Baseload Regime ($W_{\text{feed}} \ge 279.8\text{ t/h}$):** 2,581 active shifts (25.01% global; represents the 2026 baseload campaign up to 342.25 t/h).

For shifts with active MCHE differential pressure instrumentation (1,617 active records across 231 discrete operating shifts):
- **Underload ($W_{\text{feed}} \le 226.8\text{ t/h}$):** 959 records (137 discrete shifts).
- **Transition ($226.8 < W_{\text{feed}} < 279.8\text{ t/h}$):** 231 records (33 discrete shifts).
- **Baseload ($W_{\text{feed}} \ge 279.8\text{ t/h}$):** 427 records (61 discrete shifts).

### 4.2 Statistical Distribution of MCHE dP & Temperature Tags Across Regimes

```
Table 1: Statistical Distribution Across Operating Regimes (master_shift_level.parquet)
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| Parameter / Tag       | Regime     | Count  | Mean      | Std     | P10       | P50       | P90       | Max       |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H5PDI003 [kg/cm²]     | Underload  |    959 | 0.1640    | 0.0619  | 0.0794    | 0.1738    | 0.2436    | 0.3330    |
| (Warm Bundle dP)      | Transition |    231 | 0.2646    | 0.0321  | 0.2242    | 0.2677    | 0.3051    | 0.3174    |
|                       | Baseload   |    427 | 0.2950    | 0.0304  | 0.2643    | 0.2898    | 0.3323    | 0.3744    |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H5PDI004 [kg/cm²]     | Underload  |    959 | 0.0507    | 0.0115  | 0.0355    | 0.0503    | 0.0658    | 0.0850    |
| (Cold Bundle dP)      | Transition |    231 | 0.1080    | 0.0195  | 0.0812    | 0.1076    | 0.1337    | 0.1461    |
|                       | Baseload   |    427 | 0.1257    | 0.0257  | 0.0977    | 0.1230    | 0.1601    | 0.1704    |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| Hydraulic dP Ratio    | Underload  |    959 | 3.131     | 0.652   | 2.214     | 3.142     | 4.012     | 4.620     |
| (Warm dP / Cold dP)   | Baseload   |    427 | 2.412     | 0.318   | 2.051     | 2.378     | 2.814     | 3.150     |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H5TI0025 [°C]         | Underload  |  2,587 | -124.9281 | 5.6923  | -130.1372 | -125.5549 | -120.0421 |  -33.4973 |
| (MRV cold outlet)     | Baseload   |  2,581 | -122.3649 | 2.5578  | -125.8423 | -122.3308 | -119.3017 | -116.1091 |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H5TI0027 [°C]         | Underload  |  2,587 | -122.1845 | 5.0370  | -125.7126 | -122.6104 | -118.5885 |  -29.2672 |
| (Feed Gas cb inlet)   | Baseload   |  2,581 | -120.8281 | 2.0530  | -123.5265 | -120.7906 | -118.2311 | -114.4786 |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H5TI0029 [°C]         | Underload  |    959 | -153.0805 | 1.0218  | -154.7673 | -152.8867 | -151.8542 | -151.1316 |
| (Rundown LNG)         | Baseload   |    427 | -152.8346 | 0.6649  | -153.8406 | -152.8097 | -152.0617 | -151.6466 |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
| H4TI004B [°C]         | Underload  |    959 |  -30.9863 | 7.1144  |  -39.1245 |  -31.7346 |  -20.1732 |  -15.0468 |
| (Suction Drum Temp)   | Baseload   |    427 |  -41.2380 | 0.4563  |  -41.7608 |  -41.2887 |  -40.6223 |  -39.9693 |
+-----------------------+------------+--------+-----------+---------+-----------+-----------+-----------+-----------+
```

### 4.3 Non-Darcy Hydraulic Scaling Laws
Classical single-phase turbulent pipe flow scales quadratically with flow rate according to Darcy-Weisbach ($\Delta P \propto W^{2.0}$). In the two-phase shell side of MCHE 5E-1, regression across all valid operating observations reveals distinct power-law scaling exponents:

1. **Warm Bundle Shell-Side dP (`H5PDI003`):**
   $$\Delta P_{\text{warm}} = \exp(-9.6558) \cdot W_{\text{feed}}^{1.497} \quad (R^2 = 0.8432)$$
   - *Physical Mechanism:* The scaling exponent $\beta = 1.497 \approx 1.50$ deviates from pure quadratic flow because during turndown, shell Reynolds numbers drop into the transitional Blasius regime ($Re \sim 2{,}000 - 8{,}000$), where friction factors scale as $f \propto Re^{-0.25}$.
   - Furthermore, fitting a quadratic model with intercept yields:
     $$\Delta P_{\text{warm}} = 2.6627 \times 10^{-6} \cdot W_{\text{feed}}^2 + 0.0738\text{ kg/cm}^2 \quad (R^2 = 0.7962)$$
     The positive intercept ($0.0738\text{ kg/cm}^2$) represents the hydrostatic liquid head of unvaporized heavy refrigerant pooling in the lower shell basin above the suction nozzle.

2. **Cold Bundle Shell-Side dP (`H5PDI004`):**
   $$\Delta P_{\text{cold}} = \exp(-11.1937) \cdot W_{\text{feed}}^{1.593} \quad (R^2 = 0.8861)$$
   - *Physical Mechanism:* In the cold bundle, fluid is primarily vapor and high-velocity flash mist. The higher exponent $\beta = 1.593$ reflects lower liquid holdup and higher shear velocity.
   - When fitted to a quadratic model, the intercept is near zero ($0.0099\text{ kg/cm}^2$), confirming minimal static liquid holdup in the upper bundle.

### 4.4 Hydraulic Ratio Shift & Warm Bundle Liquid Pooling
The hydraulic dP ratio ($\Delta P_{\text{warm}} / \Delta P_{\text{cold}}$) exhibits a critical operational shift:
- **Baseload Mean Ratio:** **$2.41$** (P10: 2.05, P90: 2.81).
- **Underload Mean Ratio:** **$3.13$** (P10: 2.21, P90: 4.01).
- **Physical Interpretation:** In underload conditions, the reduction in feed gas thermal heat input causes heavy refrigerant fractions ($C_2/C_3$) to remain unvaporized as they trickle through the warm bundle. Liquid pools in the lower shell, increasing local liquid holdup and elevation head, driving the warm/cold dP ratio up by **$+29.9\%$**.

---

## 5. Thermodynamic Mechanisms & Operator Control Strategies

### 5.1 Nitrogen Volatility, Bubble Point Depression & Cold Bundle Temperature Depression
In MCHE 5E-1, mixed refrigerant is expanded across light JT letdown valve `5PV-15` from ~42.0 kg/cm²g to ~2.5 kg/cm²g.
- **Thermodynamic Behavior of Nitrogen ($N_2$):** Nitrogen is the most volatile component in the refrigerant mixture ($T_b = -195.8^\circ\text{C}$). Increasing nitrogen concentration lowers the mixture bubble point and shifts the vapor-liquid equilibrium (VLE) flash curve toward lower temperatures.
- **Empirical Correlation:** In the underload regime ($W_{\text{feed}} \le 226.8\text{ t/h}$), nitrogen mole fraction (`comp_N2`) displays an exceptionally strong negative correlation with cold rundown LNG temperature (`pp_H5TI0029_mean`):
  $$r(N_2, T_{\text{rundown}}) = -0.6867 \quad (\text{intensifying from } r = -0.4999 \text{ at baseload})$$
- **Underload Overchilling Mechanism:**
  Under low feed gas throughput, the compressor anti-surge floor enforces a minimum circulation rate of $\ge 480.0\text{ t/h}$. If the MCR contains elevated nitrogen, the expansion across `5PV-15` produces excessive flash cooling, depressing cold bundle temperatures (`H5TI0025` drops by $-2.56^\circ\text{C}$ to $-125.55^\circ\text{C}$; `H5TI0029` drops to $-156.0^\circ\text{C}$). This overchills the LNG product, increasing thermal stresses and risking trace hydrocarbon freeze-out.

### 5.2 Operator MCR Adjustments & Suction Drum Liquid Carryover Protection
*(Source: `BOOK-5 (Plant-4_MCR Refrigeration System)`, pp. 16, 109; Memo `156-BP31-2020-113`; DCS Historian Data)*
- **The Suction Chilling Hazard:** Centrifugal compressor `4K-2` cannot tolerate liquid droplets. If bottom shell exit temperature drops to **$-45.0^\circ\text{C}$**, alarm **`TAL`** activates on `H4TI004B`; at **$-51.0^\circ\text{C}$**, interlock **`4TALL-4ABC`** trips the compressor turbine.
- **Empirical Operator Modulation:**
  Laboratory GC shift analyses (`comp_C3` vs. `H4TI004B`) reveal a definitive correlation:
  $$r(C_3, T_{\text{suct}}) = -0.7601 \quad \text{and} \quad r(C_1, T_{\text{suct}}) = +0.5958$$
  - Higher propane ($C_3$) concentration increases mixture boiling temperatures in the warm bundle. Under low feed gas heat input, propane fails to fully vaporize, causing cold liquid droplets to pool and depress suction temperature toward the $-45.0^\circ\text{C}$ TAL limit.
  - Consequently, plant operators systematically **trim propane ($C_3$)** (from $6.49\text{ mol\%}$ down to $4.78\text{ mol\%}$) and **elevate methane ($C_1$)** (from $44.09\text{ mol\%}$ to $44.75\text{ mol\%}$) during turndown.
  - Concurrently, suction reheat valve **`4TV-510`** modulates open to inject warm discharge gas into drum 4C-7, maintaining suction superheat $\ge 3.0^\circ\text{C}$ and holding $T_{\text{suct}} \ge -45.0^\circ\text{C}$.

---

## 6. Analytical Synthesis & Mathematical Formulation for ML Pipeline

To implement these findings into `MCR_ML_REBUILD` without hardcoded constants, the following mathematical formulations are established:

### 6.1 Regime Classification Function
$$\text{regime}(W_{\text{feed}}) = \begin{cases} 
\text{underload } (0), & \text{if } W_{\text{feed}} \le 226.8\text{ t/h} \\
\text{transition } (1), & \text{if } 226.8\text{ t/h} < W_{\text{feed}} < 279.8\text{ t/h} \\
\text{baseload } (2), & \text{if } W_{\text{feed}} \ge 279.8\text{ t/h}
\end{cases}$$
- `is_underload` $= \mathbb{I}(W_{\text{feed}} \le 226.8)$
- `is_baseload` $= \mathbb{I}(W_{\text{feed}} \ge 279.8)$
- `is_transition` $= \mathbb{I}(226.8 < W_{\text{feed}} < 279.8)$

### 6.2 Hydraulic & Thermal Engineered Features
1. **Dimensionless Bundle dP Ratio:**
   $$\text{feat\_mche\_dp\_ratio\_warm\_cold} = \frac{\Delta P_{\text{warm}}}{\Delta P_{\text{cold}} + 10^{-6}} = \frac{\text{pp\_H5PDI003\_mean}}{\text{pp\_H5PDI004\_mean} + 10^{-6}}$$
2. **Total Shell dP:**
   $$\text{feat\_mche\_shell\_dp\_total} = \Delta P_{\text{warm}} + \Delta P_{\text{cold}} = \text{pp\_H5PDI003\_mean} + \text{pp\_H5PDI004\_mean}$$
3. **Specific Normalized Warm Bundle dP:**
   $$\text{feat\_mche\_norm\_warm\_dp} = \frac{\text{pp\_H5PDI003\_mean}}{W_{\text{feed}} + 10^{-6}} \times 1000 \quad \left[\frac{\text{kg/cm}^2}{\text{t/h}} \times 1000\right]$$
4. **Vertical Thermal Lift:**
   $$\text{feat\_mche\_vertical\_thermal\_lift} = T_{\text{suct}} - T_{\text{cb\_lng}} = \text{pp\_H4TI004B\_mean} - \text{pp\_H5TI0029\_mean} \quad [^\circ\text{C}]$$
5. **Cold Bundle Depression Index:**
   $$\text{feat\_cold\_bundle\_depression\_index} = T_{\text{mrv\_cb\_out}} - T_{\text{cb\_lng}} = \text{pp\_H5TI0025\_mean} - \text{pp\_H5TI0029\_mean} \quad [^\circ\text{C}]$$

### 6.3 Corrected Compressor Pressure/Temperature Ratios, JT Expansion, and Badak LNG SBHP Equations (`Titin Irawati 2024` & `BOOK-4/5`)
*(Sources: Titin Irawati 2024, Tabel 4.1 pp. 30–36, 91–92; `ProcessParameter_August_2026.xlsx`; `BOOK-4` pp. 146–149; `BOOK-5` pp. 80, 103)*

1. **Corrected Stage Pressure Ratios & Interstage 4E-5AB $\Delta P$ (Native Absolute `KGC2A` Basis):**
   - Verified from `ProcessParameter_August_2026.xlsx` (`Row 0: UNIT = KGC2A`, `Row 1: DESC`) and `Titin Irawati (2024)` (Tabel 4.1, p. 91), `H4PI015A` ($13.697\text{ kg/cm}^2\text{A}$) is **`4K-2 DISCH`** and `H4PI016B` ($13.417\text{ kg/cm}^2\text{A}$) is **`4K-3 SUCT`** (downstream of intercooler `4E-5AB`):
     $$\text{rp\_LP\_MCR} = \frac{\text{H4PI015A}}{\text{H4PI014B}}, \quad \text{rp\_HP\_MCR} = \frac{\text{H4PI017B}}{\text{H4PI016B}}, \quad \text{rp\_MCR\_total} = \frac{\text{H4PI017B}}{\text{H4PI014B}}$$
     $$\text{dp\_interstage\_4E5} = \text{H4PI015A} - \text{H4PI016B} \quad (\text{median } +0.280\text{ kg/cm}^2)$$
     $$\text{rp\_C3\_total} = \frac{\text{H4PI006B}}{\text{H4PIC002}} \quad (\text{median } 14.164 / 1.045 = 13.554)$$
2. **Corrected Compressor Stage Temperature Rise & Intercooler 4E-5AB Approach:**
   - `H4TI007B` ($+57.43^\circ\text{C}$) is **`4K-2 DISCH`** and `H4TI006B` ($+33.12^\circ\text{C}$) is **`4K-3 SUCT`**:
     $$\text{comp\_dT\_discharge\_4K2} = \text{H4TI007B} - \text{H4TI004B} \quad (+96.18^\circ\text{C})$$
     $$\text{comp\_dT\_discharge\_4K3} = \text{H4TI008B} - \text{H4TI006B} \quad (+91.96^\circ\text{C})$$
     $$\text{dT\_intercooler\_4E5} = \text{H4TI007B} - \text{H4TI006B} \quad (+24.31^\circ\text{C})$$
3. **Joule-Thomson Expansion Cooling Across Letdown Valves `5FV-2` and `5PV-15`:**
   $$\text{MCR\_dT\_JT\_5FV2} = \text{H5TI0031} - \text{H5TI0032} \quad (\text{median } +5.36^\circ\text{C})$$
   $$\text{MCR\_dT\_JT\_PV15} = \text{H5TI0030} - \text{H5TI0029} \quad (\text{median } +2.45^\circ\text{C})$$
4. **MCHE Multi-Pass Approach Temperatures & Apparent Molecular Weight (`MW_MCR`):**
   $$\text{MCHE\_dT\_cold\_bundle\_approach} = \text{H5TI0026} - \text{H5TI0021}, \quad \text{MCHE\_dT\_cold\_bundle\_approach\_B} = \text{H5TI0027} - \text{H5TI0025}$$
   $$\text{MCHE\_dT\_lngexit\_mrv} = \text{H5TIC01A} - \text{H5TI0027}, \quad \text{MCHE\_dT\_shell\_span} = \text{H5TI0047} - \text{H5TI0025}$$
   $$\text{MW\_MCR} = \sum_{i \in \{N_2, C_1, C_2, C_2H_4, C_3, iC_4, nC_4\}} y_i \cdot \text{MW}_i \quad [\text{g/mol}]$$
5. **Propane Compressor `4K-1` 3-Stage Anti-Surge Minimum Flow Margins (`BOOK-4` pp. 146–149):**
   $$\text{c3\_antisurge\_margin\_stg1} = \text{H4FI001A} - 155.0\text{ kNm}^3/\text{h}, \quad \text{c3\_antisurge\_margin\_stg2} = \text{H4FI002B} - 55.0\text{ kNm}^3/\text{h}, \quad \text{c3\_antisurge\_margin\_stg3} = \text{H4FI003B} - 38.0\text{ kNm}^3/\text{h}$$
6. **Badak LNG Specific Brake Horse Power (`SBHP`) Benchmark (`Titin Irawati 2024`, pp. 30–36):**
   $$W_s = Z_{\text{avg}} R T_1 \frac{n}{n-1} \left[ \left(\frac{P_2}{P_1}\right)^{\frac{n-1}{n}} - 1 \right], \quad \text{GHP} = \frac{\dot{n}_{\text{mol}} \cdot W_s}{\eta_p}, \quad \text{BHP} = \text{GHP}_{\text{LP}} + \text{GHP}_{\text{HP}} + 2\left(\text{GHP}_{\text{HP}}^{0.4}\right)$$
   $$\text{SBHP} = \frac{\text{BHP}}{\dot{Q}_{\text{MCHE}}\text{ [MMBTU/h]}} \le 10.0\text{ HP/(MMBTU/h)}$$

---

## 7. Direct Bibliographic & Operational Document Citations

1. **PT Badak NGL Operations Department (2025):** `Manual Book 5 Dekade Operation Badak LNG — 1. TRAINS: BOOK-6 (Plant-5_Liquefaction Unit) Rev_0.pdf`, 274 pages.
   - Section 2.2.3 (Equipment Description: 5E-1, 5C-1, 5C-2), pp. 27–43.
   - Section 2.3.2 (MCHE Instrumentation & PDI Thresholds), pp. 47–53.
   - Bab 2, Problem-2 (High Differential Pressure 5E-1 & Distributor Shear Failure), pp. 65–66.
   - Section 2.5 (Operating Procedures, Start-up, Shutdown & Trip Logic), pp. 230–245.
2. **PT Badak NGL Operations Department (2025):** `Manual Book 5 Dekade Operation Badak LNG — 1. TRAINS: BOOK-5 (Plant-4_MCR Refrigeration System) Rev_0.pdf`, 367 pages.
   - Section 2.2.1 (Compressors 4K-2/3 & Suction Drums 4C-7/8), pp. 12–25.
   - Section 2.3.1 (4K-2/3 Discharge TAH/TAHH, 4C-8 PAL/LAH/LAHH, 4K-3 PAH 54.0 kg/cm²), pp. 80, 103.
   - Section 2.4.3 (Temperature Alarm Low TAL -45.0°C and TALL -51.0°C Trip Interlocks), pp. 105–115.
   - Section 2.5 (Steam Turbines 4KT-1/2/3 & Surface Condensers 4E-15/20/25 Vacuum -600/-500/-380 mmHg), pp. 128–151.
   - Section 2.6.2 (Anti-Surge Kickback 4UV-53 and Suction Reheat 4TV-510 Modulation), pp. 165–180.
3. **PT Badak NGL Operations Department (2025):** `Manual Book 5 Dekade Operation Badak LNG — 1. TRAINS: BOOK-4 (Plant-4_Propane Refrigeration System) Rev_0.pdf`, 279 pages.
   - Propane refrigerant specification (>97 mol% C3), 4E-1AB desuperheater limit (`4TI-296` <= 39°C), Train E/F/H 4E-9 level (`4LIC-12` = 0%, `4TI-214` = -34.1°C), and 4K-1 3-stage anti-surge minimum flow floors (`4FI-1` >= 155, `4FI-2` >= 55, `4FI-3` >= 38 kNm³/h) and positive suction (`4PIC-2` >= 1.033 kg/cm²A), pp. 3, 72, 95, 146–149.
4. **PT Badak NGL Operations Department (2025):** `Manual Book 5 Dekade Operation Badak LNG — 1. TRAINS: BOOK-1 (Plant-1_Gas Purification) Rev_0.pdf` (258 pp.), `BOOK-2 (Plant-2_Dehydration and Mercury Removal) Rev_0.pdf` (166 pp.), and `BOOK-3 (Plant-3_Fractionation Unit) Rev_0.pdf` (308 pp.).
   - Feed gas impurity ceilings ($\text{CO}_2 < 50\text{ ppmv}$, $\text{H}_2\text{S} < 4\text{ ppmv}$, $\text{H}_2\text{O} < 0.5\text{ ppmv}$, $\text{Hg} < 0.01\text{ ppb}$), Scrub Column `3C-1` minimum reflux (`3FSL-19` = 16.0 m³/h), and Train G/H LPBS (`4E-40`/`4C-40` subcooling to -50.7°C).
5. **Process Engineering & Energy Conservation Department, PT Badak NGL (2020):** `Technical Memorandum No. 156/BP31/2020-113: RECOMMENDED MCR COMPOSITION FOR TRAIN-H ABOVE 780m3/h LNG RATE`, June 19, 2020, 5 pages.
   - Baseline MCR Recipe, Turbine 4KT-3 Steam Choking, H5PDI-3 Trip Limit ($0.54\text{ kg/cm}^2$), pp. 2–5.
6. **Fauzan, Iqbal (2025):** *Evaluation of Mixed Refrigerant Composition Sensitivity and Thermal Interlocks in Train-H C3MR Cycle*, Politeknik Negeri Jakarta & PT Badak NGL, July 2025, 76 pages.
   - TAL (-45.0°C) and TALL (-51.0°C) boundary margins and MCHE crossover prevention, pp. 62–71.
7. **Irawati, Titin (2024):** *Evaluasi Kinerja Multi Component Refrigerant (MCR) Compressor (4K-2 & 4K-3) Berdasarkan Specific Brake Horse Power (SBHP) pada Train H di PT Badak NGL*, Politeknik Negeri Jakarta & PT Badak NGL, August 2024, 128 pages.
   - Polytropic work $W_s$, Pitzer $Z$-factor, Scheel mechanical losses, SBHP <= 10.0 HP/(MMBTU/h) ceiling, verified 4K-2/4K-3 DCS tag mapping (Tabel 4.1, pp. 91–92), and Bab V Section 5.2 recommendation for non-linear ML modeling of MCR composition (p. 124).
8. **DCS Operating Historian Dataset (2023–2026):** `master_shift_level.parquet` (17,709 records, 10,318 active shifts, Train-H Process Parameters and Discrete 4C-8 MCR Gas Chromatography), PT Badak NGL Historian.
