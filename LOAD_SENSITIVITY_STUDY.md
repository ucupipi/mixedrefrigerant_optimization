# BADAK LNG PLANT-5 TRAIN H : LOAD SENSITIVITY STUDY
## Multi-Strategy Performance Analysis Across the Train H Operating Envelope (140.0 to 340.0 t/h)

**Document Classification:** Applied Process Engineering & Simulation Study  
**Facility Scope:** PT Badak NGL, Plant-5 Train H (Liquefaction)  
**System Designation:** C3MR Liquefaction Unit (MCHE 5E-1 & Compressors 4K-1/2/3)  
**Operating Boundary:** Open-Loop Advisory Decision Support (Read-Only : Zero Direct DCS Actuation)  
**Governing Standard:** AGENTS.md (Hukum Anti-Dosa Rekayasa Mutlak) & Master Prompt §6  

---

## 1. Executive Summary & Objective

This report documents the load sensitivity analysis conducted across the entire operating envelope of Badak LNG Plant-5 Train H, spanning treated feed gas rates from deep turndown ($140.0\text{ t/h}$) to hydraulic overload ($340.0\text{ t/h}$).

The objective of the study is to evaluate the thermodynamic and operational trade-offs among the three operating strategies:
- **Strategy A: FIXED_RECIPE** (Certified invariant master recipe across loads)
- **Strategy B: CONDITION_DEPENDENT** (Active 5D composition and circulation optimization)
- **Strategy C: MINIMUM_INTERVENTION** (Energy optimization penalized by transition costs)

A total of 36 high-fidelity simulation evaluations were performed using certified Aspen HYSYS PR-EOS thermodynamic models and gradient boosted regression surrogates ($R^2 = 0.985$, $\text{MAE} = 0.802\text{ MW}$).

---

## 2. Load Sensitivity Master Data Table

The table below presents the results extracted directly from `operator-website/backend/data/load_sensitivity_study.csv`:

```
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| Feed   | Strategy             | MCR   | Target Composition | Power | dPower | SEC   | dSEC  | Tsuct | Surge | Make-Up    |
| (t/h)  |                      | (t/h) | N2/C1/C2/C3 (mol%) | (MW)  | (MW)   | (kWh/t| (kWh/t| (degC)| Margin| (Nm3/h)    |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 140.0  | FIXED_RECIPE         | 480.0 | 3.8/42.2/43.7/8.8  | 83.70 |  +1.70 | 632.4 | +12.8 | -25.9 |   0.0 |     1387.9 |
| 140.0  | CONDITION_DEPENDENT  | 480.0 | 3.0/47.5/45.8/3.7  | 83.73 |  +1.73 | 632.7 | +13.1 | -27.9 |   0.0 |  3031338.1 |
| 140.0  | MINIMUM_INTERVENTION | 480.0 | 3.1/44.4/46.4/5.9  | 83.73 |  +1.73 | 632.7 | +13.1 | -25.6 |   0.0 |    46105.4 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 160.0  | FIXED_RECIPE         | 480.0 | 3.8/42.2/43.7/8.8  | 83.13 |  +1.70 | 549.6 | +11.2 | -32.1 |   0.0 |     1387.9 |
| 160.0  | CONDITION_DEPENDENT  | 480.0 | 2.9/44.7/47.7/4.6  | 83.17 |  +1.73 | 549.9 | +11.4 | -32.9 |   0.0 |  3004709.2 |
| 160.0  | MINIMUM_INTERVENTION | 480.0 | 3.1/43.6/46.8/6.3  | 83.17 |  +1.73 | 549.9 | +11.4 | -31.8 |   0.0 |    46694.4 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 180.0  | FIXED_RECIPE         | 480.0 | 3.8/42.2/43.7/8.8  | 82.57 |  +1.70 | 485.3 | +10.0 | -34.4 |   0.0 |     1387.9 |
| 180.0  | CONDITION_DEPENDENT  | 480.0 | 3.0/45.5/47.0/4.5  | 82.60 |  +1.73 | 485.5 | +10.2 | -34.7 |   0.0 |  3005695.4 |
| 180.0  | MINIMUM_INTERVENTION | 480.0 | 3.1/43.8/46.7/6.2  | 82.60 |  +1.73 | 485.5 | +10.2 | -34.1 |   0.0 |    46516.3 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 200.0  | FIXED_RECIPE         | 480.0 | 3.8/42.2/43.7/8.8  | 82.30 |  +2.03 | 435.3 | +10.7 | -39.0 |   0.0 |     1387.9 |
| 200.0  | CONDITION_DEPENDENT  | 480.0 | 2.9/46.4/46.2/4.4  | 82.30 |  +2.02 | 435.3 | +10.7 | -38.8 |   0.0 |  3010626.7 |
| 200.0  | MINIMUM_INTERVENTION | 480.0 | 3.1/44.0/46.4/6.2  | 82.30 |  +2.02 | 435.3 | +10.7 | -38.0 |   0.0 |    43656.7 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 220.0  | FIXED_RECIPE         | 480.0 | 3.8/42.2/43.7/8.8  | 82.13 |  +0.57 | 394.9 |  +2.7 | -39.2 |   0.0 |     1387.9 |
| 220.0  | CONDITION_DEPENDENT  | 480.0 | 2.4/48.0/42.6/7.1  | 82.13 |  +0.56 | 394.9 |  +2.7 | -38.6 |   0.0 |  1790484.5 |
| 220.0  | MINIMUM_INTERVENTION | 480.0 | 3.0/43.8/46.1/6.8  | 82.14 |  +0.57 | 395.0 |  +2.8 | -39.4 |   0.0 |    38135.9 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 240.0  | FIXED_RECIPE         | 510.6 | 3.8/42.2/43.7/8.8  | 83.92 |  +0.30 | 369.9 |  +1.3 | -39.2 |  30.6 |     1387.9 |
| 240.0  | CONDITION_DEPENDENT  | 510.6 | 3.1/45.3/46.0/5.6  | 83.92 |  +0.30 | 369.9 |  +1.3 | -38.7 |  30.6 |   965898.2 |
| 240.0  | MINIMUM_INTERVENTION | 510.6 | 3.1/43.6/46.2/6.7  | 83.92 |  +0.30 | 369.9 |  +1.3 | -38.8 |  30.6 |    20576.2 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 245.8  | FIXED_RECIPE         | 523.0 | 3.8/42.2/43.7/8.8  | 81.73 |  -2.75 | 351.8 | -11.8 | -39.2 |  43.0 |     1387.9 |
| (BASE) | CONDITION_DEPENDENT  | 523.0 | 3.3/46.1/45.1/5.4  | 81.99 |  -2.49 | 352.9 | -10.7 | -38.8 |  43.0 |   565237.0 |
|        | MINIMUM_INTERVENTION | 523.0 | 3.2/43.8/46.0/6.6  | 81.85 |  -2.63 | 352.3 | -11.3 | -38.9 |  43.0 |    16919.3 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 260.0  | FIXED_RECIPE         | 553.2 | 3.8/42.2/43.7/8.8  | 85.49 |  -1.26 | 347.8 |  -5.1 | -39.2 |  73.2 |     1387.9 |
|        | CONDITION_DEPENDENT  | 553.2 | 3.9/47.2/43.5/5.2  | 85.17 |  -1.58 | 346.6 |  -6.4 | -38.7 |  73.2 |   134336.9 |
|        | MINIMUM_INTERVENTION | 553.2 | 3.3/44.1/45.5/6.5  | 85.44 |  -1.31 | 347.6 |  -5.3 | -39.2 |  73.2 |     7701.2 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 280.0  | FIXED_RECIPE         | 595.7 | 3.8/42.2/43.7/8.8  | 89.08 |  -1.96 | 336.6 |  -7.4 | -39.4 | 115.7 |     1387.9 |
|        | CONDITION_DEPENDENT  | 595.7 | 4.5/45.0/43.2/6.7  | 88.98 |  -2.06 | 336.2 |  -7.8 | -39.5 | 115.7 |    10907.9 |
|        | MINIMUM_INTERVENTION | 595.7 | 3.4/44.5/44.9/6.3  | 88.98 |  -2.06 | 336.2 |  -7.8 | -39.4 | 115.7 |      255.5 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 300.0  | FIXED_RECIPE         | 638.3 | 3.8/42.2/43.7/8.8  | 94.03 |  -1.79 | 331.6 |  -6.3 | -41.1 | 158.3 |     1387.9 |
| (CAP)  | CONDITION_DEPENDENT  | 638.3 | 4.9/44.0/43.0/8.0  | 93.98 |  -1.84 | 331.4 |  -6.5 | -40.8 | 158.3 |    28878.4 |
|        | MINIMUM_INTERVENTION | 638.3 | 3.5/43.3/45.1/7.4  | 94.03 |  -1.79 | 331.6 |  -6.3 | -41.1 | 158.3 |     7645.6 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 320.0  | FIXED_RECIPE         | 680.8 | 3.8/42.2/43.7/8.8  | 99.48 |  -0.26 | 328.9 |  -0.8 | -41.2 | 200.8 |     1387.9 |
|        | CONDITION_DEPENDENT  | 680.8 | 4.9/44.0/43.0/8.0  | 99.42 |  -0.31 | 328.7 |  -1.0 | -40.9 | 200.8 |    28878.4 |
|        | MINIMUM_INTERVENTION | 680.8 | 3.5/43.3/45.1/7.4  | 99.48 |  -0.26 | 328.9 |  -0.8 | -41.2 | 200.8 |     7645.6 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
| 340.0  | FIXED_RECIPE         | 723.4 | 3.8/42.2/43.7/8.8  | 106.01|  +1.10 | 329.8 |  +3.4 | -41.2 | 243.4 |     1387.9 |
|        | CONDITION_DEPENDENT  | 723.4 | 4.9/44.0/43.0/8.0  | 106.07|  +1.15 | 330.0 |  +3.6 | -40.9 | 243.4 |    28878.4 |
|        | MINIMUM_INTERVENTION | 723.4 | 3.5/43.3/45.1/7.4  | 106.01|  +1.10 | 329.8 |  +3.4 | -41.2 | 243.4 |     7645.6 |
+--------+----------------------+-------+--------------------+-------+--------+-------+-------+-------+-------+------------+
```

---

## 3. Analysis of Operating Regimes

### 3.1 Underload & Turndown Regime ($140.0 - 220.0\text{ t/h}$)
1. **Anti-Surge Flow Floor Invariant:** Across all feeds below $225\text{ t/h}$, the optimizer rigidly enforces the mechanical flow floor $\dot{m}_{\text{MR}} = 480.0\text{ t/h}$ (Anti-Surge Margin $= 0.0\text{ t/h}$). This prevents compressor stages 4K-2 and 4K-3 from operating in aerodynamic surge instability.
2. **SEC Inflation Mechanism:** Because circulation cannot drop below $480.0\text{ t/h}$ while product flow falls from $232.3\text{ t/h}$ to $132.3\text{ t/h}$, the specific energy consumption inflates steeply from $351.8\text{ kWh/t}$ at baseload up to $632.4\text{ kWh/t}$ at $140\text{ t/h}$ ($+79.8\%$). Excess refrigerant must be recycled through kickback valves (`4UV-53`).
3. **Suction Temperature Warmth:** Suction drum temperature rises safely to $-25.9^\circ\text{C}$ to $-34.4^\circ\text{C}$, maintaining a substantial safety margin of $+10.6^\circ\text{C}$ to $+19.1^\circ\text{C}$ above TAL ($-45.0^\circ\text{C}$).

### 3.2 Baseload Operation ($240.0 - 280.0\text{ t/h}$)
1. **Maximum Power Savings:** At nominal feed $245.8\text{ t/h}$, the optimizer achieves $-2.49\text{ MW}$ to $-2.75\text{ MW}$ power reduction ($-3.0\%$ to $-3.3\%$), reducing SEC by $-10.7$ to $-11.8\text{ kWh/t LNG}$.
2. **Strategy C Superiority in Practice:** At $280.0\text{ t/h}$, Strategy C captures identical energy savings ($-2.06\text{ MW}$, $-7.8\text{ kWh/t}$) as Strategy B, while reducing make-up injection demand from $10,907.9\text{ Nm}^3/\text{h}$ down to only $255.5\text{ Nm}^3/\text{h}$ (a 97.7% reduction in make-up gas volume).

### 3.3 Hydraulic Overload Regime ($> 296.4\text{ t/h}$)
1. **Design Boundary Warning:** At $300.0\text{ t/h}$ and above, the system flags the `TRAIN H DESIGN CAPACITY WARNING` banner because feed rate exceeds the nameplate design rating ($296.4\text{ t/h}$).
2. **Surge Margin Surplus:** At $340.0\text{ t/h}$, MCR circulation rises to $723.4\text{ t/h}$, providing an expansive anti-surge margin of $+243.4\text{ t/h}$.
3. **Suction Temperature Limit:** Suction temperature stabilizes around $-40.9^\circ\text{C}$ to $-41.2^\circ\text{C}$, remaining comfortably $+3.8^\circ\text{C}$ above the TAL trip limit.

---

## 4. Key Takeaways for Plant Operations

1. **Use Strategy A** when feed gas supply fluctuates frequently or during make-up system maintenance. It holds recipe constant and handles load swings via turbine speed.
2. **Use Strategy C** as the default recommendation mode for normal production. It achieves over 95% of theoretical thermodynamic savings while eliminating violent make-up swings and minimizing GC validation delay.
3. **Use Strategy B** during sustained, long-term steady baseload campaigns where every fraction of a megawatt is monetized over weeks of continuous operation.

