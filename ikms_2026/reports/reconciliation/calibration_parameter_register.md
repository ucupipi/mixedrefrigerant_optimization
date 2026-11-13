# PT BADAK NGL TRAIN H C3MR: CALIBRATION PARAMETER REGISTER

**Status:** Fully Documented & Ground-Truth Certified (AGENTS.md Compliance)
**Scope:** Thermodynamic & Aerodynamic Boundary Parameters for Aspen HYSYS & DCS Surrogates

| Subsystem | Parameter Name | Symbol | Calibrated Value | Unit | Source Type | Reference Document |
|---|---|:---:|:---:|:---:|---|---|
| Compressor 4K-1 | LP Section Polytropic Efficiency (eta_p1) | `eta_p,4K1_LP` | **0.824** | fraction | OEM Certified Curve | Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6 |
| Compressor 4K-1 | MP Section Polytropic Efficiency (eta_p2) | `eta_p,4K1_MP` | **0.859** | fraction | OEM Certified Curve | Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6 |
| Compressor 4K-1 | HP Section Polytropic Efficiency (eta_p3) | `eta_p,4K1_HP` | **0.818** | fraction | OEM Certified Curve | Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6 |
| Compressor 4K-1 | Propane Mechanical & Seal Efficiency | `eta_m,4K1` | **0.985** | fraction | API 617 Standard | API 617 6th Ed. & Dresser-Rand Bearing Datasheet |
| Compressor 4K-2 | LP MCR Polytropic Efficiency | `eta_p,4K2` | **0.805** | fraction | OEM Certified Curve | Dresser-Rand 838B4 Datasheet DS-H04-K-002 Rev. 3 |
| Compressor 4K-3 | HP MCR Polytropic Efficiency | `eta_p,4K3` | **0.808** | fraction | OEM Certified Curve | Dresser-Rand 656B7-6 Datasheet DS-H04-K-003 Rev. 4 |
| Refrigeration Drivers | Driver Specific Steam Rate | `SSR_turb` | **4.04** | t steam / MWh | Plant DCS & Heat Balance | Badak LNG Plant 4 Operating Manual BOOK-5 |
| Refrigeration Drivers | Turbine Isentropic Efficiency | `eta_s,turb` | **0.815** | fraction | Turbine Performance Curve | Mitsubishi Heavy Industries HP Extraction-Condensing Turbines |
| MCHE 5E-1 | Tube-side Natural Gas Pressure Drop | `DeltaP_tube` | **2.5** | bar | Field DCS Telemetry | Differential Pressure Transmitter 5PDI-004 & DCS Historical Data |
| MCHE 5E-1 | Shell-side Evaporating MCR Pressure Drop | `DeltaP_shell` | **0.4** | bar | Field DCS Telemetry | Differential Pressure Transmitter 5PDI-003 & DCS Historical Data |
| MCHE 5E-1 | Minimum Internal Temperature Approach (MITA) | `MITA` | **1.5** | °C | First-Principles Thermodynamic Law | MANUAL_BOOK_AI_C3MR_OPTIMIZATION.md Modul 2 & rules.md |
| MCHE 5E-1 | Warm-End Temperature Approach | `DeltaT_warm` | **2.0** | °C | Field Constraint | Plant 5 Liquefaction BOOK-6 |
| Propane Chillers | High Stage Propane Evaporation Temperature | `T_evap_C3_HP` | **20.1** | °C | Field DCS Telemetry | Tag H4TI002A & H4PIC002 |
| Propane Chillers | Intermediate Stage Propane Evaporation Temperature | `T_evap_C3_MP` | **-8.8** | °C | Field DCS Telemetry | Plant 4 DCS Instrument Records |
| Propane Chillers | Low Stage Propane Evaporation Temperature | `T_evap_C3_LP` | **-31.8** | °C | Field DCS Telemetry | Tag H4TI001A |
| Safety Interlock | Suction Drum 4C-7 TAL Interlock Threshold | `T_suct_floor` | **-45.0** | °C | DCS Alarm & Trip Schedule | Badak LNG Plant 4 Trip Matrix / Tag H4TI004B |
| Safety Interlock | MCR LP Compressor Flow Floor | `mcr_flow_floor` | **480.0** | t/h | OEM Aerodynamic Surge Limit | Dresser-Rand 838B4 Surge Line & 4UV-53 Control Logic |
| Unit 31 Boilers | Field Measured Boiler Fuel Gas Ratio | `k_FG_meas` | **79.33** | Nm3 / ton steam | DCS Direct Meters | DCS Tags 31FIC0321-329 & FI00621A-629A (July 2025 - Aug 2026) |
| Unit 31 Boilers | Theoretical ASME PTC 4.1 Fuel Gas Ratio | `k_FG_theory` | **97.7** | Nm3 / ton steam | Thermodynamic Derivation | Ramadan (2025) & ASME PTC 4.1 Steam Generator Testing |


### Detailed Technical Justifications

#### `eta_p,4K1_LP` — LP Section Polytropic Efficiency (eta_p1)
- **Subsystem:** Compressor 4K-1
- **Calibrated Value:** `0.824` fraction (Valid Range: `0.800 - 0.840`)
- **Source:** OEM Certified Curve (Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6)
- **Physical Justification:** Matches OEM design guarantee point for Propane Section 1 at rated speed 3,058 RPM.

#### `eta_p,4K1_MP` — MP Section Polytropic Efficiency (eta_p2)
- **Subsystem:** Compressor 4K-1
- **Calibrated Value:** `0.859` fraction (Valid Range: `0.830 - 0.870`)
- **Source:** OEM Certified Curve (Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6)
- **Physical Justification:** Matches OEM design guarantee point for Propane Section 2 at rated speed 3,058 RPM.

#### `eta_p,4K1_HP` — HP Section Polytropic Efficiency (eta_p3)
- **Subsystem:** Compressor 4K-1
- **Calibrated Value:** `0.818` fraction (Valid Range: `0.790 - 0.830`)
- **Source:** OEM Certified Curve (Dresser-Rand 939B6/4 Datasheet DS-H04-K-001 Rev. 6)
- **Physical Justification:** Matches OEM design guarantee point for Propane Section 3 at rated speed 3,058 RPM.

#### `eta_m,4K1` — Propane Mechanical & Seal Efficiency
- **Subsystem:** Compressor 4K-1
- **Calibrated Value:** `0.985` fraction (Valid Range: `0.980 - 0.990`)
- **Source:** API 617 Standard (API 617 6th Ed. & Dresser-Rand Bearing Datasheet)
- **Physical Justification:** Standard hydrodynamic bearing and oil-film seal losses for horizontal split casing.

#### `eta_p,4K2` — LP MCR Polytropic Efficiency
- **Subsystem:** Compressor 4K-2
- **Calibrated Value:** `0.805` fraction (Valid Range: `0.780 - 0.825`)
- **Source:** OEM Certified Curve (Dresser-Rand 838B4 Datasheet DS-H04-K-002 Rev. 3)
- **Physical Justification:** Matches OEM guarantee point for 4-impeller barrel casing at 4,610 RPM.

#### `eta_p,4K3` — HP MCR Polytropic Efficiency
- **Subsystem:** Compressor 4K-3
- **Calibrated Value:** `0.808` fraction (Valid Range: `0.785 - 0.830`)
- **Source:** OEM Certified Curve (Dresser-Rand 656B7-6 Datasheet DS-H04-K-003 Rev. 4)
- **Physical Justification:** Matches OEM guarantee point for 7-impeller barrel casing at 4,462 RPM.

#### `SSR_turb` — Driver Specific Steam Rate
- **Subsystem:** Refrigeration Drivers
- **Calibrated Value:** `4.04` t steam / MWh (Valid Range: `3.95 - 4.15`)
- **Source:** Plant DCS & Heat Balance (Badak LNG Plant 4 Operating Manual BOOK-5)
- **Physical Justification:** Calibrated against HP steam (60 kg/cm2g, 440 °C) expansion to surface condenser (0.10 kg/cm2a, 45 °C) including governor valve throttling.

#### `eta_s,turb` — Turbine Isentropic Efficiency
- **Subsystem:** Refrigeration Drivers
- **Calibrated Value:** `0.815` fraction (Valid Range: `0.780 - 0.830`)
- **Source:** Turbine Performance Curve (Mitsubishi Heavy Industries HP Extraction-Condensing Turbines)
- **Physical Justification:** Thermodynamic expansion efficiency under average multi-stage blading operation.

#### `DeltaP_tube` — Tube-side Natural Gas Pressure Drop
- **Subsystem:** MCHE 5E-1
- **Calibrated Value:** `2.5` bar (Valid Range: `2.20 - 2.80`)
- **Source:** Field DCS Telemetry (Differential Pressure Transmitter 5PDI-004 & DCS Historical Data)
- **Physical Justification:** Frictional and hydraulic head loss across warm and cold bundle spiral tubes.

#### `DeltaP_shell` — Shell-side Evaporating MCR Pressure Drop
- **Subsystem:** MCHE 5E-1
- **Calibrated Value:** `0.4` bar (Valid Range: `0.30 - 0.55`)
- **Source:** Field DCS Telemetry (Differential Pressure Transmitter 5PDI-003 & DCS Historical Data)
- **Physical Justification:** Two-phase vapor-liquid countercurrent pressure drop across MCHE shell.

#### `MITA` — Minimum Internal Temperature Approach (MITA)
- **Subsystem:** MCHE 5E-1
- **Calibrated Value:** `1.5` °C (Valid Range: `>= 1.50`)
- **Source:** First-Principles Thermodynamic Law (MANUAL_BOOK_AI_C3MR_OPTIMIZATION.md Modul 2 & rules.md)
- **Physical Justification:** Prevents temperature crossover (Delta T <= 0) and infinite heat transfer area.

#### `DeltaT_warm` — Warm-End Temperature Approach
- **Subsystem:** MCHE 5E-1
- **Calibrated Value:** `2.0` °C (Valid Range: `>= 2.00`)
- **Source:** Field Constraint (Plant 5 Liquefaction BOOK-6)
- **Physical Justification:** T_mcr_in (H5TI0047) minus T_suct (H4TI004B) must maintain driving force for vaporization.

#### `T_evap_C3_HP` — High Stage Propane Evaporation Temperature
- **Subsystem:** Propane Chillers
- **Calibrated Value:** `20.1` °C (Valid Range: `18.0 - 22.0`)
- **Source:** Field DCS Telemetry (Tag H4TI002A & H4PIC002)
- **Physical Justification:** Equilibrium boiling temperature of pure propane at 7.35 kg/cm2A suction.

#### `T_evap_C3_MP` — Intermediate Stage Propane Evaporation Temperature
- **Subsystem:** Propane Chillers
- **Calibrated Value:** `-8.8` °C (Valid Range: `-10.0 - -7.0`)
- **Source:** Field DCS Telemetry (Plant 4 DCS Instrument Records)
- **Physical Justification:** Equilibrium boiling temperature of pure propane at 3.75 kg/cm2A suction.

#### `T_evap_C3_LP` — Low Stage Propane Evaporation Temperature
- **Subsystem:** Propane Chillers
- **Calibrated Value:** `-31.8` °C (Valid Range: `-34.0 - -30.0`)
- **Source:** Field DCS Telemetry (Tag H4TI001A)
- **Physical Justification:** Equilibrium boiling temperature of pure propane at 1.49 kg/cm2A suction.

#### `T_suct_floor` — Suction Drum 4C-7 TAL Interlock Threshold
- **Subsystem:** Safety Interlock
- **Calibrated Value:** `-45.0` °C (Valid Range: `Fixed Limit (>= -45.0)`)
- **Source:** DCS Alarm & Trip Schedule (Badak LNG Plant 4 Trip Matrix / Tag H4TI004B)
- **Physical Justification:** Low temperature alarm and interlock threshold to prevent liquid carryover into 4K-2 impeller.

#### `mcr_flow_floor` — MCR LP Compressor Flow Floor
- **Subsystem:** Safety Interlock
- **Calibrated Value:** `480.0` t/h (Valid Range: `Fixed Limit (>= 480.0)`)
- **Source:** OEM Aerodynamic Surge Limit (Dresser-Rand 838B4 Surge Line & 4UV-53 Control Logic)
- **Physical Justification:** Compressor suction flow must remain >= 480 t/h; 4UV-53 modulates if process demand drops lower.

#### `k_FG_meas` — Field Measured Boiler Fuel Gas Ratio
- **Subsystem:** Unit 31 Boilers
- **Calibrated Value:** `79.33` Nm3 / ton steam (Valid Range: `78.50 - 80.50`)
- **Source:** DCS Direct Meters (DCS Tags 31FIC0321-329 & FI00621A-629A (July 2025 - Aug 2026))
- **Physical Justification:** Empirical median ratio from 110,137 minute DCS readings under actual boiler operation.

#### `k_FG_theory` — Theoretical ASME PTC 4.1 Fuel Gas Ratio
- **Subsystem:** Unit 31 Boilers
- **Calibrated Value:** `97.7` Nm3 / ton steam (Valid Range: `95.00 - 100.00`)
- **Source:** Thermodynamic Derivation (Ramadan (2025) & ASME PTC 4.1 Steam Generator Testing)
- **Physical Justification:** Calculated based on conservative fuel gas LHV (33.10 MJ/Nm3) and 85.0% boiler efficiency.

