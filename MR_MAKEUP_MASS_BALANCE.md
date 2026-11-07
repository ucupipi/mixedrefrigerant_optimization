# BADAK LNG PLANT-5 TRAIN H : MR MAKE-UP MASS & VOLUME BALANCE
## Closed-Loop Inventory Dilution Kinetics, Header Purity Matrix & Dual-Rate Conversions

**Document Classification:** Applied Chemical Engineering & Process Systems Specification  
**Facility Scope:** PT Badak NGL, Plant-5 Train H (Liquefaction)  
**System Designation:** Mixed Refrigerant Inventory Management & Make-Up System  
**Operating Boundary:** Open-Loop Advisory Decision Support (Read-Only : Zero Direct DCS Actuation)  
**Governing Standard:** AGENTS.md (Hukum Anti-Dosa Rekayasa Mutlak) & Master Prompt §3  

---

## 1. Executive Summary & Decoupling Principle

A fundamental rule of industrial process engineering (Master Prompt §3) is that **Composition Optimization must be strictly decoupled from Make-Up Injection Calculations**:
1. **Target Composition is a Thermodynamic State:** The optimized mole fractions ($y_{\text{target}, i}$) represent the ideal thermodynamic vapor-liquid equilibrium (VLE) boiling distribution required inside the MCHE tube bundle to minimize compression work. It is NOT a valve command.
2. **Make-Up Schedule is a Dynamic Inventory Mass Balance:** Moving the circulating refrigerant loop ($M_{\text{inv}} \approx 85,000\text{ kg}$) from actual state $\mathbf{y}_{\text{actual}}$ to target state $\mathbf{y}_{\text{target}}$ requires solving a component-resolved dilution balance over a defined operating transition time ($\tau$, typically 2.0 to 4.0 hours).
3. **The "Closer is Less Waste" Fallacy:** A recipe close to current inventory minimizes immediate make-up mass, but may forfeit thousands of dollars per day in thermodynamic compressor power savings. Material use and energy savings must be evaluated together over an operational horizon.

---

## 2. Closed-Loop Inventory Dilution Mathematical Model

### 2.1 Closed-Loop Inventory Balance
Let $M_{\text{inv}}$ be the total mass inventory of the MCR loop (including suction drum 4C-8, MCHE shell 5E-1, interstage coolers, and piping). When make-up streams are injected into the low-pressure suction drum without active loop venting, the loop inventory expands by factor $\lambda$:
$$\lambda = 1 + \sum_{k \in \mathcal{K}_{\text{inj}}} \frac{m_{\text{inj}, k}}{M_{\text{inv}}}$$
where $m_{\text{inj}, k}$ is the mass of pure make-up stream $k$ injected over transition period $\tau$.

### 2.2 Component-Resolved Mass Balance
For each refrigerant component $i \in \{\text{N2}, \text{C1}, \text{C2}, \text{C2H4}, \text{C3}\}$:
$$w_{\text{target}, i} \cdot M_{\text{inv}} \cdot \lambda = w_{\text{actual}, i} \cdot M_{\text{inv}} + \sum_{k} Y_{w, i, k} \cdot m_{\text{inj}, k}$$
where:
- $w_i$ is the mass fraction of component $i$, converted from mole fraction $y_i$ via molecular weight vector $\mathbf{M} = [28.0134, 16.0425, 30.0690, 28.0532, 44.0956]\text{ kg/kmol}$:
  $$w_i = \frac{y_i M_i}{\sum_{j=1}^5 y_j M_j}$$
- $Y_{w, i, k}$ is the mass purity of component $i$ in make-up injection stream $k$.

### 2.3 Make-Up Header Purity Matrix at Badak LNG
In industrial operations, make-up gases are not 100% analytically pure chemicals; they are sourced from plant fractionation columns and utilities:

```
+---------------------------------------------------------------------------------------------------+
|                            BADAK LNG PLANT MAKE-UP HEADER SPECIFICATIONS                          |
+---------------------+-------------------+------------+--------------------------------------------+
| Component           | Source DCS Tag    | Nominal MW | Primary Composition & Impurities           |
+---------------------+-------------------+------------+--------------------------------------------+
| Nitrogen (N2)       | H4FV045           | 28.013     | Utility Air Separation Unit:               |
|                     |                   |            | 99.90 mol% N2, 0.10 mol% Ar/O2             |
+---------------------+-------------------+------------+--------------------------------------------+
| Methane (C1)        | H4FV041           | 16.043     | Scrub Column 3C-1 Overhead Fuel Gas:       |
|                     |                   |            | 98.50 mol% C1, 1.20 mol% N2, 0.30 mol% C2  |
+---------------------+-------------------+------------+--------------------------------------------+
| Ethane (C2)         | H4FV042           | 30.069     | De-ethanizer 3C-4 Overhead Liquid:         |
|                     |                   |            | 99.00 mol% C2, 0.80 mol% C1, 0.20 mol% C3  |
+---------------------+-------------------+------------+--------------------------------------------+
| Ethylene (C2H4)     | H4FV044           | 28.053     | Refrigerant Storage Cylinder:              |
|                     |                   |            | 99.50 mol% C2H4, 0.50 mol% C2              |
+---------------------+-------------------+------------+--------------------------------------------+
| Propane (C3)        | H4FV043           | 44.096     | De-propanizer 3C-6 Overhead Liquid:        |
|                     |                   |            | 98.80 mol% C3, 1.00 mol% iC4, 0.20 mol% C2 |
+---------------------+-------------------+------------+--------------------------------------------+
```

### 2.4 Linear Matrix System Solution
Rearranging the conservation equations yields the linear system:
$$(\mathbf{Y}_w - \mathbf{w}_{\text{target}} \mathbf{1}^T) \mathbf{m}_{\text{inj}} = M_{\text{inv}} (\mathbf{w}_{\text{target}} - \mathbf{w}_{\text{actual}})$$
Since negative injection is physically impossible without dedicated chromatographic separation, the solution is bounded non-negatively:
$$m_{\text{inj}, k} \ge 0 \quad \forall k$$
Components whose target fraction is lower than actual ($w_{\text{target}, i} < w_{\text{actual}, i}$) are diluted by injecting the deficit components, or managed via controlled loop purge if loop inventory pressure reaches the high threshold.

---

## 3. Dual-Rate Engineering Unit Conversions

The advisory engine reports make-up rates simultaneously in standard volumetric units ($Nm^3/\text{h}$ and $scfd$) and mass units ($kg/\text{h}$ and $t/\text{h}$):

### 3.1 Normal Standard Gas Volume ($Nm^3/\text{h}$)
Evaluated at Normal Reference Conditions ($T_{\text{norm}} = 0.0^\circ\text{C} = 273.15\text{ K}$, $P_{\text{norm}} = 1.01325\text{ bar} = 101.325\text{ kPa}$, molar volume $V_m = 22.414\text{ Nm}^3/\text{kmol}$):
$$\dot{V}_{\text{norm}, k} = \frac{\dot{m}_k}{M_k} \times 22.414 \quad [\text{Nm}^3/\text{h}]$$

### 3.2 Standard Cubic Feet per Day ($scfd$)
Evaluated at US Standard Conditions ($60.0^\circ\text{F} = 15.56^\circ\text{C}$, $14.696\text{ psia}$, conversion factor $1.0\text{ Nm}^3 = 37.324\text{ scf}$):
$$\dot{V}_{\text{std, US}, k} = \dot{V}_{\text{norm}, k} \times 37.324 \times 24 \quad [\text{scfd}]$$

### 3.3 Mass Rates
$$\dot{m}_k = \frac{m_{\text{inj}, k}}{\tau} \quad [\text{kg/h}], \quad \dot{M}_{t, k} = \frac{\dot{m}_k}{1000.0} \quad [\text{t/h}]$$

---

## 4. Unevaluated Guard & Zero-False-Zeros Protocol

In strict adherence to Master Prompt §3.4 and AGENTS.md:
- **No False Zeros:** If required inputs (actual composition, target composition, loop inventory mass, transition hours) are missing, unmeasured, or physically corrupted, the calculation engine **MUST NOT** return zero ($0.0\text{ Nm}^3/\text{h}$). Returning zero falsely indicates that no make-up is needed and that valves should remain closed.
- **Unevaluated Schema:** On validation failure, the engine returns:
  ```json
  {
    "status": "TIDAK DAPAT DIEVALUASI",
    "total_makeup_flow_nm3_h": null,
    "total_makeup_flow_kg_h": null,
    "estimated_inventory_kg": null,
    "transition_hours": null,
    "items": [],
    "operational_notes": [
      "[INPUT VALIDATION FAILURE] Reason: Corrupted sensor data or missing component..."
    ]
  }
  ```

### Official DCS Action Constants
When inputs are valid, each component item is assigned an explicit action status:
- `INJEKSI`: Component is in deficit ($w_{\text{target}} > w_{\text{actual}}$). Recommends positive injection flow.
- `TAHAN / STOP`: Component is in excess ($w_{\text{target}} < w_{\text{actual}}$). Recommends holding valve closed while dilution proceeds.
- `STABIL / SEIMBANG`: Component is within tolerance ($|w_{\text{target}} - w_{\text{actual}}| \le 0.05\%$). Loop is balanced.
- `TIDAK DAPAT DIEVALUASI`: Parameter failed input verification.

---

## 5. Automated Verification Evidence

The make-up mass balance engine is verified across 49 unit tests in `test_makeup_calculator.py` and `test_adversarial_m2_challenger.py`:
- 100% test pass rate across extreme inputs, non-numeric sensor noise, infinite inventory values, missing keys, and boundary tolerances.
- Strict preservation of molar conservation and dual-rate conversion consistency.

