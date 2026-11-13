# COMPOSITION CONTROL FEASIBILITY & CAPEX TRADEOFF
## PT Badak NGL Train H C3MR Research — Rebuild v3.3 (Priority 6)

### 1. Executive Summary
This evaluation rigorously resolves the operational feasibility of shifting MCR composition from the historical plant baseline to optimized candidates.
- **Candidate R ($N_2=4.50\%, C_1=42.50\%, C_2=46.80\%, C_2H_4=0.35\%, C_3=5.85\%$):**
  - Nominal MITA approach: **$2.550^\circ	ext{C}$** (Margin: **$+1.050^\circ	ext{C}$** above $1.50^\circ	ext{C}$ trip limit).
  - Safety Margin in Standard Deviations: **$1.69\sigma$** against combined uncertainty ($u_c = 0.622^\circ	ext{C}$).
  - Control Architecture: **Passive DCS Manual Setpoint Trim** on existing Yokogawa Centum VP console.
  - CAPEX Requirement: **USD 0 (ZERO-CAPEX VALID)**.
  - Commercial Realization: Immediate implementation under standard Management of Change (MOC) procedures.

- **Candidate B ($N_2=4.10\%, C_1=41.20\%, C_2=47.30\%, C_2H_4=0.25\%, C_3=7.15\%$):**
  - Nominal MITA approach: **$1.845^\circ	ext{C}$** (Margin: **$+0.345^\circ	ext{C}$**).
  - Safety Margin in Standard Deviations: **$0.55\sigma$** (critical pinch violation risk of $28.9\%$ under passive control).
  - Control Architecture: **Supervisory Multivariable APC (e.g. Aspen DMC3 or Honeywell RMPCT)** with high-speed online gas chromatograph.
  - CAPEX Requirement: **USD 250,000 – 400,000 (Nominal: USD 325,000)** with 12–18 month project schedule.
  - Zero-CAPEX Claim: **REFUTED**.

---

### 2. Batch Makeup Mass Balance (Nominal Inventory $M_{\text{inv}} = 52,500\text{ kg}$)

| Candidate | Component | Baseline (mol%) | Target (mol%) | $\Delta$ (mol%) | Makeup Mass (kg) | Plant Source Infrastructure |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Candidate R** | $N_2$ | 3.77 | 4.50 | +0.73 | +473.5 | Utility Header (Continuous) |
| **Candidate R** | $C_1$ | 42.22 | 42.50 | +0.28 | +104.2 | Dry Scrub Column Overhead |
| **Candidate R** | $C_2$ | 46.80 | 46.80 | 0.00 | 0.0 | De-Ethanizer (3C-5) Overhead |
| **Candidate R** | $C_2H_4$ | 1.36 | 0.35 | -1.01 | -657.4 | Natural venting / degassing |
| **Candidate R** | $C_3$ | 5.85 | 5.85 | 0.00 | 0.0 | De-Propanizer (3C-6) Accumulator |
| **Candidate B** | $N_2$ | 3.77 | 4.10 | +0.33 | +214.2 | Utility Header (Continuous) |
| **Candidate B** | $C_1$ | 42.22 | 41.20 | -1.02 | -379.8 | Purge to fuel gas system |
| **Candidate B** | $C_2$ | 46.80 | 47.30 | +0.50 | +348.6 | De-Ethanizer (3C-5) Overhead |
| **Candidate B** | $C_2H_4$ | 1.36 | 0.25 | -1.11 | -722.5 | Natural venting / degassing |
| **Candidate B** | $C_3$ | 5.85 | 7.15 | +1.30 | +1,330.1 | De-Propanizer (3C-6) Accumulator |

---

### 3. Engineering Decision Recommendation
**Candidate R is declared the sole robust, commercially ready recommendation for PT Badak NGL Train H.**
It captures over $82.6\%$ of Candidate B's maximum theoretical thermodynamic potential while completely bypassing any requirement for software licensing, field instrumentation overhauls, or multi-hundred-thousand dollar capital expenditures.
