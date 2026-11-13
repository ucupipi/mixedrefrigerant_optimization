# BOILER FUEL GAS CONSUMPTION AND CO2 RECALCULATION REPORT
## High-Pressure Steam Generation, Fuel Gas Intensity, Combustion Telemetry, and Carbon Accounting
**Document ID:** IKMS-2026-REP-D10  
**Classification:** Environmental & Utility Telemetry Verification  
**Governance:** AGENTS.md (Pasal 1, 2, 8, 10)  

---

### 1. Executive Summary & Sensor Telemetry Integration
This report provides the full telemetry and stoichiometric foundation for avoided boiler fuel gas consumption and greenhouse gas emission reductions.

Following recent physical tag verification of the Plant-3 utility system (`ProcessParameter_August_2026.xlsx`, Sheet1, 44,641 valid minutes), telemetry data from Unit 31 Boilers (31-F21 through 31-F29) and Power Generation Turbines (PG-9 through PG-14) were analyzed:
- **Combustion Air Flow:** `FIC4521A` to `FIC4529A` (kNm³/h)
- **Superheated / Main Steam Flow:** `FI00621A` to `FI00629A` (t/h)
- **Boiler Fuel Gas Consumption:** `31FIC0321` to `31FIC0329` (kNm³/h)
- **Flue Gas Oxygen Analyzer:** `AI000621`, `AIC00626` to `AIC00629b` (%)
- **Power Generation HP Steam Inlet:** `FI002439`, `FI024310` to `FI024314` (turbines 31PT-9 to 31PT-14, t/h)

---

### 2. Plant-3 Boiler Fleet Operational Telemetry (August 2026)
During normal operations, four high-pressure water-tube boilers operate continuously in parallel to meet plant baseload steam demand:

| Boiler Identity | Steam Flow Tag | Fuel Gas Tag | Combustion Air Tag | Mean Steam (t/h) | Mean Fuel Gas (Nm³/h) | Mean Air (kNm³/h) | Air/Fuel Ratio (Nm³/Nm³) | Flue Gas $O_2$ (%) | Fuel/Steam Ratio (Nm³/ton) |
|:---|:---:|:---:|:---:|---:|---:|---:|---:|---:|---:|
| **31-F22** | FI00622A | 31FIC0322 | FIC4522A | 222.49 | 17,454.0 | 218.66 | 12.53 | ~3.3% | 78.45 |
| **31-F27** | FI00627A | 31FIC0327 | FIC4527A | 223.12 | 18,710.6 | 235.26 | 12.57 | ~3.1% | 83.86 |
| **31-F28** | FI00628A | 31FIC0328 | FIC4528A | 223.84 | 17,386.8 | 236.98 | 13.63 | 3.29% | 77.67 |
| **31-F29** | FI00629A | 31FIC0329 | FIC4529A | 224.86 | 17,971.6 | 236.69 | 13.17 | ~3.2% | 79.92 |
| **Total Active Fleet** | — | — | — | **894.34** | **71,523.5** | **927.59** | **12.97** | **3.22%** | **79.98 (Mean) / 79.90 (Med)** |

**Combustion Stoichiometry & Excess Air:**
- Theoretical stoichiometric air for Badak fuel gas ($94.5\%\text{ C}_1, 2.7\%\text{ C}_2, 1.7\%\text{ C}_3$): $9.52\text{ Nm}^3\text{ air / Nm}^3\text{ fuel gas}$.
- Actual measured air-to-fuel ratio: $12.97\text{ Nm}^3/\text{Nm}^3$, corresponding to excess air ratio $\lambda = 1.36$ ($36\%$ excess air).
- This aligns with the measured oxygen analyzer reading `AIC00628b` = $3.29\%\text{ O}_2$ dry basis ($3.0\%\text{--}3.5\%$ operating design envelope).

---

### 3. Reconciling Marginal vs Average Boiler Fuel Gas Ratio
A critical source of past confusion was the distinction between **aggregate average consumption** and **marginal operational response**:

1. **Aggregate Fleet Average:**
   $$\frac{\sum \text{Fuel Gas}}{\sum \text{Steam}} = \mathbf{79.97\text{ Nm}^3/\text{ton steam}} \quad (\text{July 2025: } 79.33\text{ Nm}^3/\text{t})$$
   Represents total fuel burned divided by total steam generated, including fixed boiler radiation losses and base draft fans.

2. **Marginal OLS Response (Avoided Fuel on Load Shedding):**
   Ordinary least squares regression across 44,641 operational minute records reveals:
   $$\dot{V}_{\text{FG}} (\text{Nm}^3/\text{h}) = 2,679.03 + \mathbf{76.98} \cdot \dot{m}_{\text{steam}} (\text{t/h}) \quad (R^2 = 0.9677)$$
   The marginal derivative $\partial \dot{V}_{\text{FG}} / \partial \dot{m}_{\text{steam}} = \mathbf{76.98\text{ Nm}^3/\text{ton steam}}$.

**Engineering Conclusion:**
When Train H reduces steam consumption by $9.68\text{ t/h}$, the active boilers modulate down along their operating curve at the marginal rate of **$76.98\text{ Nm}^3/\text{ton steam}$**, avoiding fuel gas over-estimation.

---

### 4. Annual Fuel Gas Savings & Dual-Basis Carbon Accounting
With normalized annual operating hours $H_{\text{active}} = 7,849.9\text{ hours/year}$ and weighted steam reduction $\Delta \dot{m}_{\text{steam}} = 9.679\text{ t/h}$:

$$\Delta m_{\text{steam, annual}} = 9.679 \times 7,849.9 = \mathbf{75,972.9\text{ tons steam / year}}$$

#### Marginal Avoided Fuel Gas Volume:
$$\Delta V_{\text{FG, marginal}} = 75,972.9\text{ tons} \times 76.98\text{ Nm}^3/\text{ton} = \mathbf{5,848,394\text{ Nm}^3/\text{year}} \quad (5.848\text{ million Nm}^3/\text{year})$$

#### Net Thermal Energy Avoidance:
- Badak Fuel Gas Lower Heating Value: $\text{LHV} = 39.50\text{ MJ/Nm}^3$ ($1,060.4\text{ BTU/scf}$).
$$\Delta E_{\text{thermal}} = 5,848,394\text{ Nm}^3 \times 39.50\text{ MJ/Nm}^3 = 230,999,000\text{ MJ/year} = \mathbf{230,999\text{ GJ/year}} \quad (218,945\text{ MMBtu/year})$$

#### Carbon Dioxide Emission Reduction:
1. **Primary IPCC 2006 Stationary Combustion Method (LHV Basis):**
   - Emission factor for natural gas: $\text{EF}_{\text{IPCC}} = 56.10\text{ kg CO}_2/\text{GJ}$.
   $$\Delta m_{\text{CO}_2, \text{IPCC}} = 230,999\text{ GJ/year} \times 56.10\text{ kg/GJ} \times 10^{-3} = \mathbf{12,959.0\text{ metric tons CO}_2 / \text{year}}$$

2. **Stoichiometric Fuel Carbon Balance (Sensitivity Check):**
   - Carbon mass fraction in fuel gas: $1.977\text{ kg CO}_2 / \text{Nm}^3$ fuel gas.
   $$\Delta m_{\text{CO}_2, \text{stoich}} = 5,848,394\text{ Nm}^3 \times 1.977\text{ kg/Nm}^3 \times 10^{-3} = \mathbf{11,561.6\text{ metric tons CO}_2 / \text{year}}$$

Both methods demonstrate substantial Scope 1 emissions abatement ($> 11,500\text{ t CO}_2/\text{yr}$), confirming the environmental merit of circulation rate optimization.
