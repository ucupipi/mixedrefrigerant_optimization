# CONTINUOUS MIXED REFRIGERANT CIRCULATION SCHEDULE
## Load-Dependent Circulation Optimization for Badak LNG Train H
**Document ID:** IKMS-2026-REP-D07  
**Classification:** Standard Operating Guidance & DCS Control Schedule  
**Governance:** AGENTS.md (Pasal 5, 6, 8, 9)  

---

### 1. Continuous Circulation Architecture
To eliminate operational dead zones and ensure seamless DCS setpoint tracking across the complete production envelope (123.0 to 265.0 t/h LNG), the optimized mixed refrigerant circulation schedule is formulated as a piecewise continuous function:

$$\dot{m}_{\text{MR}}(\text{LNG}) = \begin{cases} 
2.9047 \cdot \dot{m}_{\text{LNG}}, & \dot{m}_{\text{LNG}} \ge 190.0 \text{ t/h} \quad [\text{Baseload Domain}] \\[6pt]
436.80 + 10.744 \cdot (\dot{m}_{\text{LNG}} - 165.0), & 165.0 \le \dot{m}_{\text{LNG}} < 190.0 \text{ t/h} \quad [\text{Bridge Domain}] \\[6pt]
373.60 + 1.5048 \cdot (\dot{m}_{\text{LNG}} - 123.0), & \dot{m}_{\text{LNG}} < 165.0 \text{ t/h} \quad [\text{Turndown MCHE Domain}]
\end{cases}$$

---

### 2. Operational Modes Across Production Ranges

#### Domain 1: Baseload High-Load Operation (190.0 to 265.0 t/h LNG)
- **MCHE Flow:** Matches compressor flow directly ($559.4\text{ to }769.7\text{ t/h}$).
- **Kickback Valve 4UV-53:** Fully **CLOSED** ($0.0\text{ t/h}$ recycle).
- **Compressor Suction Flow:** Well above aerodynamic floor ($> 559.4\text{ t/h} \gg 480.0\text{ t/h}$).
- **Suction Reheat 4TV-510:** Minimum bias ($1.0\%\text{ to }3.0\%$).

#### Domain 2: Continuous Bridge Interval (165.0 to 190.0 t/h LNG)
- **MCHE Flow:** Modulates continuously from $436.8\text{ t/h}$ to $559.4\text{ t/h}$.
- **Transition Smoothness:** Derivative continuous ($d\dot{m}/d\text{LNG} = 10.744\text{ t/h per t/h LNG}$), avoiding abrupt controller windup.
- **Compressor Suction Flow:** Transitions toward the $480.0\text{ t/h}$ floor.
- **Kickback Valve 4UV-53:** Armed and seated; modulation begins at $165.0\text{ t/h}$.

#### Domain 3: Turndown Operation (< 165.0 t/h LNG)
- **MCHE Heat Exchanger Flow:** Continues to decrease ($373.6\text{ to }436.8\text{ t/h}$) matching reduced thermal liquefaction duty.
- **Compressor Suction Floor Control:** Compressor suction flow is strictly clamped at the safe floor:
  $$\dot{m}_{\text{comp, suct}} \equiv 480.0\text{ t/h}$$
- **Kickback Valve 4UV-53 Modulation:** Modulates open ($43.2\text{ to }106.4\text{ t/h}$) through the second-stage recycle cooler to protect impellers from aerodynamic surge.
- **Suction Reheat Valve 4TV-510:** Modulates open ($12.0\%\text{ to }22.0\%$) injecting LP steam reheat to ensure 4C-7 suction temperature remains $\ge -41.49^\circ\text{C}$ (safe above TAL $-45.0^\circ\text{C}$).

---

### 3. Key Percentile Operational Reference Table

| Operating Percentile | LNG Production (t/h) | Baseline MCR Flow (t/h) | Optimized MCHE Flow (t/h) | Compressor Suct Flow (t/h) | Kickback 4UV-53 Flow (t/h) | Reheat 4TV-510 Position (%) | 4C-7 Suct Temp (°C) | MCHE MITA (°C) | Total Steam Saving (t/h) |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **P100 (Max)** | 265.0 | 927.1 | 769.7 | 769.7 | 0.0 (Closed) | 1.0% | -36.00 | 2.35 | 18.28 |
| **P90 (Design)** | 258.4 | 898.5 | 750.6 | 750.6 | 0.0 (Closed) | 1.0% | -35.87 | 2.31 | 17.20 |
| **P75 (Nominal)** | 244.2 | 845.2 | 709.3 | 709.3 | 0.0 (Closed) | 1.0% | -35.58 | 2.22 | 15.80 |
| **P50 (Median)** | 190.1 | 682.4 | 559.4 | 559.4 | 0.0 (Closed) | 3.0% | -34.50 | 1.90 | 10.42 |
| **P35 (Bridge)** | 175.0 | 610.0 | 544.2 | 544.2 | 0.0 (Closed) | 5.8% | -36.08 | 1.81 | 7.65 |
| **P25 (Turndown)**| 146.3 | 550.2 | 408.7 | 480.0 | 71.3 (Modulating) | 16.5% | -39.09 | 1.64 | 5.92 |
| **P10 (Minimum)** | 123.0 | 480.0 | 373.6 | 480.0 | 106.4 (Modulating)| 21.0% | -41.49 | 1.50 | 3.86 |
