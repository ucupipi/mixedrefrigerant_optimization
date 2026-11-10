# Data Dictionary: Badak LNG Train H C3MR Compressor Mapped Operating Points
**Project**: PT Badak NGL Train H C3MR Optimization Suite for IKMS 2026  
**Document Revision**: 1.0 (2026-11-10)  
**Author**: Rotating Equipment & Thermodynamic Process Specialist (Worker M3)  
**Classification**: Proprietary Engineering Operating Points & Telemetry Lineage Ledger  
**Primary Datasets**:
- Parquet: `D:\User\Documents\KULIAH\LOMBA\IKMS 2026\data\processed\compressor_mapped_operating_points.parquet`
- CSV: `D:\User\Documents\KULIAH\LOMBA\IKMS 2026\data\processed\compressor_mapped_operating_points.csv`

---

## 1. Document Overview & Certified OEM Provenance

This data dictionary establishes the physical, thermodynamic, and mechanical definitions of the mapped operating points dataset for the centrifugal compressors operating in the Train H Propane Precooled Mixed Refrigerant (C3MR) cycle at PT Badak NGL, Bontang, East Kalimantan, Indonesia.

The dataset bridges historical steady-state DCS telemetry across 7 operating quantiles (P10, P25, P40, P50, P60, P75, P90) under both historical baseline and thermodynamic-optimized operation to certified vendor performance curves manufactured by **Dresser-Rand** for PERTAMINA / Proyek Kilang Pengolahan (PKP) under the Bontang LNG Expansion Project Train H (PGH Project):

| Equipment Tag | Service Description | OEM Manufacturer | Model Number | Contract Doc No. | Revision & Date | Driver Tag | Certified Source Document |
|---|---|---|---|---|---|---|---|
| **4K-1** | Propane Refrigeration Compressor (3 Sections) | Dresser-Rand | **939B6/4** | `DS-H04-K-001` | Rev. 6, 25 May 1998 | `H4KT-1` | `H4K-1.pdf` (14 Pages) |
| **4K-2** | MCR First Stage / Low Pressure (LP) Compressor | Dresser-Rand | **838B4** | `DS-H04-K-002` | Rev. 3, 24 March 1997 | `H4KT-2` | `H4K-2.pdf` (16 Pages) |
| **4K-3** | MCR Second Stage / High Pressure (HP) Compressor | Dresser-Rand | **656B7-6** | `DS-H04-K-003` | Rev. 4, 16 April 1997 | `H4KT-3` | `H4K-3.pdf` (16 Pages) |

### 1.1 Contractual and Project Lineage
- **Purchaser**: Perusahaan Pertambangan Minyak dan Gas Bumi Negara (PERTAMINA)
- **EPC Contractors**: PT Inti Karya Persada Tehnik (IKPT) & Kellogg Overseas Corporation
- **Job No.**: 95038 / 6413
- **Purchase Order**: PGH-KPO-K-003
- **Requisition No.**: PGH-MR-K-003
- **Plant Location**: Bontang, East Kalimantan, Indonesia (Badak LNG Plant 3)

---

## 2. Equipment Specifications & Operational Mechanical Limits

### 2.1 Mechanical Rotor & Speed Limits
Each centrifugal compressor is driven by a dedicated variable-speed mechanical drive steam turbine taking high-pressure superheated steam (42.0 bar g, 380°C to 400°C) exhausting to surface condensers or medium-pressure headers:

| Parameter | 4K-1 (Propane 939B6/4) | 4K-2 (LP MCR 838B4) | 4K-3 (HP MCR 656B7-6) | Engineering Standard / Source |
|---|:---:|:---:|:---:|---|
| **Casing Construction** | Horizontally Split, Cast Steel | Radially Split (Barrel), ASTM A216 WCC | Radially Split (Barrel), ASTM A516 Gr 70 | API 617-6th Edition |
| **Impeller Stages** | 6 Impellers total (3LP + 2MP + 1HP) | 4 Impellers (Single Section) | 7 Impellers (Single Section) | OEM Mechanical Datasheets |
| **Rated Operating Speed ($N_{100}$)** | **3,058 RPM** (Range: 3023–3083) | **4,610 RPM** | **4,462 RPM** | Datasheet Page 2 |
| **Max Continuous Speed (MCS)** | **3,216 RPM** (105.17%) | **4,873 RPM** (105.70%) | **4,835 RPM** (108.36%) | API 617 requirement |
| **Mechanical Trip Speed ($N_{\text{trip}}$)** | **3,538 RPM** (115.70%) | **5,360 RPM** (116.27%) | **5,319 RPM** (119.21%) | Turbine Emergency Governor Trip |
| **1st Lateral Critical Speed** | 1,900 RPM (Flexible Shaft) | 2,500 RPM (Flexible Shaft) | 2,800 RPM (Flexible Shaft) | API 617 Vibration Resonance |
| **Shaft Seal Type** | Mechanical Contact / Oil Film | Oil Film Seal | Oil Film Seal | API 614 Lube & Seal Console |

### 2.2 OEM Design Guarantee Conditions (Case 1 Normal Basis)

| Parameter | 4K-1 Sect 1 (LP) | 4K-1 Sect 2 (MP) | 4K-1 Sect 3 (HP) | 4K-2 LP MCR | 4K-3 HP MCR | Units |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Working Fluid** | Pure Propane | Propane | Propane | Mixed Refrigerant | Mixed Refrigerant | — |
| **Molecular Weight ($M$)** | 44.097 | 44.097 | 44.097 | 25.075 | 25.075 | kg/kmol |
| **Inlet Suction Pressure ($P_s$)** | **1.49** | **3.75** | **7.35** | **3.16** | **15.45** | $kg/cm^2A$ |
| **Inlet Suction Temperature ($T_s$)** | **-31.8** | **-8.8** (Mix) | **+20.1** (Mix) | **-32.7** | **+20.0** | $^\circ C$ |
| **Inlet Compressibility ($Z_1$)** | 0.966 | 0.918 | 0.868 | 0.967 | 0.908 | — |
| **Specific Heat Ratio ($k_1$)** | 1.155 | 1.148 | 1.152 | 1.258 | 1.207 | $C_p / C_v$ |
| **Inlet Mass Flow ($\dot{m}$)** | 339,731 | 749,751 | 1,024,880 | 545,000 | 545,000 | kg/h |
| **Inlet Actual Volume ($Q_{\text{actual}}$)** | 216,835 | 148,093 | 102,488 | 148,807 | 48,807 | $m^3/h$ |
| **Curve Reference Density ($\rho$)** | 1.5668 | 5.0627 | 10.0000 | 3.6625 | 11.1664 | $kg/m^3$ |
| **Discharge Pressure ($P_d$)** | **3.75** | **7.35** | **14.50** | **15.65** | **53.65** | $kg/cm^2A$ |
| **Pressure Ratio ($P_d / P_s$)** | 2.517 | 1.960 | 1.973 | 4.953 | 3.472 | — |
| **Polytropic Head ($H_p$)** | 5,655 | 4,302 | 4,072 | 14,008 | 13,945 | $m \cdot kg / kg$ |
| **Polytropic Efficiency ($\eta_p$)** | 82.4% | 85.9% | 81.8% | 80.5% | 80.8% | % |
| **Shaft Power ($\dot{W}$)** | Combined Sect 1–3: **38,409 kW** | *(Included)* | *(Included)* | **30,754 kW** | **36,681 kW** | kW |

---

## 3. Dataset Schema & Complete 39-Column Data Dictionary

The dataset contains exactly **74 rows** and **39 columns** covering:
- 7 Production Load Quantiles (P10, P25, P40, P50, P60, P75, P90) × 2 Operating Modes (Baseline, Optimized) × 5 Compressor Sections = 70 rows
- 1 Diagnostic Case: P10 Unmitigated (hypothetical zero-kickback operating point proving surge line violation) = 1 row
- 3 OEM Design Guarantee Points (4K-1 Sect 1, 4K-2 Case 1, 4K-3 Case 1) = 3 rows
- Total = **74 rows**.

| # | Column Name | Physical Data Type | Engineering Units | Permissible Range / Values | Physical Meaning & Detailed Description |
|---|---|---|---|---|---|
| 1 | `load_quantile` | String (Categorical) | — | `P10`, `P25`, `P40`, `P50`, `P60`, `P75`, `P90`, `P10_Unmitigated`, `OEM_Design` | Production throughput percentile from historical shift-level telemetry (2,531 steady-state shifts). |
| 2 | `operating_mode` | String (Categorical) | — | `Baseline`, `Optimized`, `Hypothetical_No_Kickback`, `OEM_Guarantee` | Operating strategy: Historical baseline vs AI C3MR thermodynamic optimized case vs OEM design case. |
| 3 | `compressor_tag` | String (Categorical) | — | `4K-1_Sec1`, `4K-1_Sec2`, `4K-1_Sec3`, `4K-2`, `4K-3` | Detailed aerodynamic section or casing identifier. |
| 4 | `casing_tag` | String (Categorical) | — | `4K-1`, `4K-2`, `4K-3` | Overall compressor casing equipment tag. |
| 5 | `stage_or_section` | String (Categorical) | — | `Section-1`, `Section-2`, `Section-3`, `Single-Casing` | Stage group or section designation within the physical casing. |
| 6 | `fluid_description` | String | — | `Pure Propane`, `Mixed Refrigerant (MCR)` | Chemical working fluid handled by the compressor. |
| 7 | `molecular_weight_g_mol` | Float64 | $g/mol$ | $24.40 \le MW \le 44.10$ | Fluid molecular weight calculated from stream composition. |
| 8 | `suction_pressure_bar_a` | Float64 | $bar\ a$ | $1.15 \le P_s \le 16.50$ | Absolute suction pressure at the compressor suction nozzle. |
| 9 | `suction_pressure_kgcm2a` | Float64 | $kg/cm^2A$ | $1.17 \le P_s \le 16.82$ | Absolute suction pressure in Indonesian engineering unit ($kg/cm^2A$). |
| 10 | `suction_temperature_c` | Float64 | $^\circ C$ | $-43.0 \le T_s \le +35.0$ | Suction gas temperature at suction drum / nozzle (Interlock TAL: $\ge -45.0^\circ C$). |
| 11 | `suction_temperature_k` | Float64 | $K$ | $230.15 \le T_s \le 308.15$ | Absolute suction temperature in Kelvin ($T_K = T_C + 273.15$). |
| 12 | `suction_density_kg_m3` | Float64 | $kg/m^3$ | $1.56 \le \rho_s \le 15.50$ | Gas density at compressor suction conditions. |
| 13 | `compressibility_factor_z` | Float64 | — | $0.850 \le Z_s \le 0.995$ | Vapor compressibility factor from Peng-Robinson EOS. |
| 14 | `isentropic_exponent_k` | Float64 | — | $1.140 \le k \le 1.270$ | Isentropic specific heat ratio ($k = C_p / C_v$) from PR-EOS. |
| 15 | `mass_flow_t_h` | Float64 | $t/h$ | $130.0 \le \dot{m} \le 1050.0$ | Total mass flow entering the compressor suction (including recycle if active). |
| 16 | `mass_flow_kg_h` | Float64 | $kg/h$ | $130,000 \le \dot{m} \le 1,050,000$ | Total mass flow in $kg/h$ ($\dot{m}_{kg/h} = \dot{m}_{t/h} \times 1000$). |
| 17 | `flow_basis` | String | — | `AM3/HR`, `m3/h` | Volumetric flow basis used for OEM curve lookup. |
| 18 | `actual_volumetric_flow` | Float64 | $m^3/h$ | $35,000 \le Q \le 260,000$ | Actual inlet volumetric flow ($Q_{\text{actual}} = \frac{\dot{m}}{\rho_s}$). |
| 19 | `speed_rpm` | Float64 | $RPM$ | $2,700 \le N \le 4,950$ | Operating rotor speed in revolutions per minute. |
| 20 | `speed_pct_rated` | Float64 | % | $88.0 \le \%N_{100} \le 106.0$ | Operating speed as percentage of rated speed ($N / N_{100} \times 100$). |
| 21 | `speed_pct_mcs` | Float64 | % | $80.0 \le \%MCS \le 101.5$ | Operating speed as percentage of Maximum Continuous Speed (API 617 limit $\le 105.0\%$). |
| 22 | `polytropic_head_m` | Float64 | $m$ | $3,500 \le H_p \le 15,500$ | Aerodynamic polytropic head produced across the compressor section. |
| 23 | `pressure_ratio` | Float64 | — | $1.70 \le P_d/P_s \le 5.40$ | Pressure compression ratio ($r_p = P_d / P_s$). |
| 24 | `discharge_pressure_kgcm2a` | Float64 | $kg/cm^2A$ | $3.50 \le P_d \le 55.0$ | Absolute discharge pressure at compressor outlet flange. |
| 25 | `discharge_pressure_bar_a` | Float64 | $bar\ a$ | $3.43 \le P_d \le 53.93$ | Absolute discharge pressure in bar absolute. |
| 26 | `polytropic_efficiency` | Float64 | — | $0.750 \le \eta_p \le 0.865$ | Flange-to-flange polytropic efficiency ($\eta_p$). |
| 27 | `shaft_power_kw` | Float64 | $kW$ | $4,500 \le \dot{W} \le 39,500$ | Required compressor mechanical shaft input power in kilowatts. |
| 28 | `shaft_power_mw` | Float64 | $MW$ | $4.50 \le \dot{W} \le 39.50$ | Required shaft power in megawatts ($\dot{W}_{MW} = \dot{W}_{kW} / 1000$). |
| 29 | `surge_flow` | Float64 | $m^3/h$ | $30,000 \le Q_{\text{surge}} \le 145,000$ | OEM surge limit flow at current operating speed. |
| 30 | `surge_margin_pct` | Float64 | % | $-5.0 \le SM \le +85.0$ | Aerodynamic surge margin ($\frac{Q - Q_{\text{surge}}}{Q_{\text{surge}}} \times 100\%$). |
| 31 | `choke_flow` | Float64 | $m^3/h$ | $55,000 \le Q_{\text{choke}} \le 270,000$ | Stonewall / choke limit flow at current operating speed. |
| 32 | `choke_margin_pct` | Float64 | % | $+5.0 \le CM \le +60.0$ | Margin to stonewall limit ($\frac{Q_{\text{choke}} - Q}{Q_{\text{choke}}} \times 100\%$). |
| 33 | `is_surge_safe` | Boolean | — | `True`, `False` | Compliance flag: True if $Q > Q_{\text{surge}}$ and $SM \ge 5.0\%$. |
| 34 | `is_head_compliant` | Boolean | — | `True`, `False` | Compliance flag: True if compressor develops required process head. |
| 35 | `is_speed_compliant` | Boolean | — | `True`, `False` | Compliance flag: True if $70.0\% \le \%MCS \le 105.0\%$. |
| 36 | `mechanical_status` | String (Categorical) | — | `HEAD_COMPLIANT`, `FEASIBLE`, `SURGE_VIOLATION` | Comprehensive mechanical integrity status classification. |
| 37 | `anti_surge_kickback_flow_t_h` | Float64 | $t/h$ | $0.0 \le \dot{m}_{\text{kickback}} \le 120.0$ | Mass flow modulated through secondary kickback valve `4UV-53` to prevent surge. |
| 38 | `suction_reheat_flow_t_h` | Float64 | $t/h$ | $0.0 \le \dot{m}_{\text{reheat}} \le 15.0$ | Mass flow added via suction reheat valve `4TV-510` to satisfy TAL ($\ge -45.0^\circ C$). |
| 39 | `net_process_flow_t_h` | Float64 | $t/h$ | $130.0 \le \dot{m}_{\text{net}} \le 1050.0$ | Net forward process refrigerant flow through chillers / MCHE. |

---

## 4. Thermodynamic Property Conversion Formulations (PR-EOS & CoolProp)

The thermodynamic state at the compressor suction nozzle is evaluated using the Peng-Robinson Equation of State (PR-EOS):

$$P = \frac{R T}{v - b} - \frac{a(T)}{v(v + b) + b(v - b)}$$

Where:
- $a(T) = 0.45724 \frac{R^2 T_c^2}{P_c} \alpha(T_r, \omega)$
- $b = 0.07780 \frac{R T_c}{P_c}$
- $\alpha(T_r, \omega) = \left[ 1 + (0.37464 + 1.54226\omega - 0.26992\omega^2)(1 - \sqrt{T_r}) \right]^2$

### 4.1 Cubic Resolvent Equation for Compressibility Factor ($Z$)
The cubic equation in dimensionless compressibility factor $Z = \frac{P v}{R T}$ is solved:

$$Z^3 - (1 - B)Z^2 + (A - 3B^2 - 2B)Z - (AB - B^2 - B^3) = 0$$

Where $A = \frac{a P}{R^2 T^2}$ and $B = \frac{b P}{R T}$. For vapor suction conditions, the largest real root ($Z_{\text{vapor}}$) is extracted.

### 4.2 Actual Suction Density and Specific Volume
$$\rho_{\text{suct}} = \frac{P \cdot MW}{Z \cdot R \cdot T} \quad \left[\frac{\text{kg}}{\text{m}^3}\right]$$

### 4.3 Mass to Actual Volumetric Flow Conversion
The volumetric flow entering the first impeller eye is determined by:

$$Q_{\text{actual}} = \frac{\dot{m} \cdot 1000}{\rho_{\text{suct}}} \quad \left[\frac{\text{m}^3}{\text{h}}\right]$$

This conversion guarantees physical continuity between DCS mass flow meters (`4FI-013`, `4FI-005`, `3FI-028`) and OEM volumetric performance curves.

### 4.4 Fluid Compositions Evaluated

#### Pure Propane (4K-1 Sections 1, 2, 3)
- Working Fluid: $C_3H_8 \ge 99.50\text{ mol\%}$
- Molecular Weight: $MW = 44.0956\text{ g/mol}$
- Critical Properties: $T_c = 369.89\text{ K}$, $P_c = 42.512\text{ bar}$, $\omega = 0.1523$

#### Multicomponent Mixed Refrigerant (4K-2 LP MCR & 4K-3 HP MCR)
Stream compositions based on median shift telemetry (`master_shift_level.parquet`):

| Component | Historical Baseline (mol%) | Thermodynamic Optimized (mol%) | Pure Component MW (g/mol) |
|---|:---:|:---:|:---:|
| Nitrogen ($N_2$) | 3.520% | 4.100% | 28.0134 |
| Methane ($C_1$) | 44.820% | 46.500% | 16.0425 |
| Ethane ($C_2$) | 44.150% | 43.800% | 30.0690 |
| Ethylene ($C_2H_4$) | 1.850% | 0.800% | 28.0532 |
| Propane ($C_3$) | 5.660% | 4.800% | 44.0956 |
| **Mixture MW** | **25.121 g/mol** | **24.877 g/mol** | — |

---

## 5. Aerodynamic Mapping Methodology & Performance Curve Interpolation

The mapping from operating points $(Q, N)$ to aerodynamic parameters $(H_p, r_p, \eta_p, \dot{W})$ is performed using a calibrated 2D piecewise bicubic / linear surface interpolator calibrated against the digitized OEM curve datasets (`compressor_curves_4K1.parquet`, `compressor_curves_4K2.parquet`, `compressor_curves_4K3.parquet`):

### 5.1 Fan Affinity Laws for Speed Scaling
When interpolating across variable turbine speeds ($N$), the characteristic curves follow the aerodynamic affinity laws:

$$\frac{Q_1}{Q_2} = \frac{N_1}{N_2}, \quad \frac{H_{p, 1}}{H_{p, 2}} = \left(\frac{N_1}{N_2}\right)^2, \quad \frac{\dot{W}_1}{\dot{W}_2} = \left(\frac{N_1}{N_2}\right)^3$$

Polytropic efficiency ($\eta_p$) is preserved along constant equivalent volume flow lines ($Q / N = \text{const}$).

### 5.2 Shaft Power Evaluation
Mechanical shaft power is calculated from polytropic head and mass flow:

$$\dot{W}_{\text{shaft}} = \frac{\dot{m}_{kg/s} \cdot g \cdot H_p}{\eta_p \cdot 1000 \cdot \eta_{\text{mech}}} \quad [\text{kW}]$$

Where $g = 9.80665\text{ m/s}^2$ and mechanical transmission efficiency $\eta_{\text{mech}} \approx 0.985$ accounts for bearing and seal friction losses.

### 5.3 Aerodynamic Surge Margin Formulation
The distance to the OEM surge boundary is defined as:

$$\text{SM} = \frac{Q_{\text{actual}} - Q_{\text{surge}}(N)}{Q_{\text{surge}}(N)} \times 100\%$$

Operating criteria:
- $\text{SM} \ge 10.0\%$: Normal, fully safe operating margin.
- $5.0\% \le \text{SM} < 10.0\%$: Minimum allowable operational buffer with kickback control armed.
- $\text{SM} < 5.0\%$: Surge alert; secondary kickback valve `4UV-53` modulates open.
- $\text{SM} \le 0.0\%$: Surge violation; aerodynamic stall and pressure pulsation imminent.

---

## 6. Boundary Enforcement & Safety Interlocks

### 6.1 Safe Operating Envelope Flow Floor ($480.0\text{ t/h}$)
Centrifugal compressors 4K-2 (838B4) and 4K-3 (656B7-6) are subject to an inviolable mechanical flow floor:

$$\dot{m}_{\text{suct, total}} \ge 480.0\text{ t/h}$$

During production turndown (e.g., P10, where net MCHE circulation falls to $373.55\text{ t/h}$), secondary kickback valve `4UV-53` automatically opens to bypass $107.59\text{ t/h}$ of compressed MCR back to the suction drum, keeping total compressor suction flow at $604.68\text{ t/h}$ ($+26.0\%$ above the flow floor, surge margin $+59.9\%$).

### 6.2 Suction Drum Temperature Alarm Low (TAL $-45.0^\circ\text{C}$)
To prevent liquid droplet carryover into the first-stage impellers of 4K-2, suction drum temperature is interlocked:

$$T_{\text{suct}} \ge -45.0^\circ\text{C}$$

If $T_{\text{suct}}$ approaches the TAL threshold during extreme turndown, suction reheat valve `4TV-510` modulates high-pressure superheated MCR bypass vapor into the suction drum to raise the suction temperature. Across all 74 records, the minimum suction temperature is $-41.49^\circ\text{C}$ (P90 baseload) and $-21.14^\circ\text{C}$ (P10 turndown), fully satisfying the TAL interlock.

### 6.3 Variable Speed Envelope Window ($70.0\%\text{ to }105.0\%\text{ MCS}$)
In compliance with API 617 6th Edition, the permissible continuous speed window is:

$$0.70 \times N_{\text{MCS}} \le N_{\text{operating}} \le 1.05 \times N_{\text{MCS}}$$

Across the entire dataset:
- 4K-1 operating range: $2,875\text{ to }3,058\text{ RPM}$ ($89.4\%\text{ to }95.1\%\text{ MCS}$).
- 4K-2 operating range: $4,391\text{ to }4,660\text{ RPM}$ ($90.1\%\text{ to }95.6\%\text{ MCS}$).
- 4K-3 operating range: $4,249\text{ to }4,510\text{ RPM}$ ($87.9\%\text{ to }93.3\%\text{ MCS}$).
All points operate safely within the continuous governor speed window.

---

## 7. Single Source of Truth Lineage Table

| Data Class | Upstream Source File | Key Identifiers / Tags | Transformation Script | Output Destination |
|---|---|---|---|---|
| Historical DCS Telemetry | `master_shift_level.parquet` | `4FI013`, `H4TI004B`, `H4PI013`, `4UV53`, `H4KT-1/2/3` | `compressor_envelope_mapper.py` | `compressor_mapped_operating_points.parquet` |
| Thermodynamic Optimization Targets | `hysys_reconciled_validation_summary.csv` | `thru_opt_th`, `p_opt_kw`, `delta_p_pct` | `compressor_envelope_mapper.py` | `compressor_mapped_operating_points.parquet` |
| Digitized OEM Performance Curves | `compressor_curves_4K1.parquet`, `4K2`, `4K3` | `flow_value`, `y_value`, `speed_rpm` | `compressor_envelope_mapper.py` | `compressor_mapped_operating_points.parquet` |
| Thermodynamic Gas Properties | CoolProp / PR-EOS | Propane, Multicomponent MCR ($N_2/C_1/C_2/C_2H_4/C_3$) | `compressor_envelope_mapper.py` | Columns 7, 12, 13, 14, 18 |
| Automated Validation Suite | `scripts/validate_telemetry_linking.py` | 10 Test Suites / 46 Assertions | Test Runner | Exit code 0 |

---
*End of Data Dictionary — Document Revision 1.0*

