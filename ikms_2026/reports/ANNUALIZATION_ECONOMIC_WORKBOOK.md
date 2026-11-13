# ANNUALIZATION AND ECONOMIC CALCULATION WORKBOOK
## Multi-Boundary Financial Valuation and Operating Hour Derivation
**Document ID:** IKMS-2026-REP-D11  
**Classification:** Financial & Operational Accounting  
**Governance:** AGENTS.md (Pasal 1, 2, 8, 10)  

---

### 1. Derivation of Normalized Annual Operating Hours
A source of ambiguity in early drafts was the duration of the operational dataset vs the annual reporting baseline:
- **Observed Continuous Telemetry Duration:** 110,137 steady-state minute records = **1,835.6 observation hours**.
- **Historical Plant Availability Factor:** $89.61\%$ on-stream factor (327.1 operating days per calendar year).
- **Normalized Annual Operating Hours:**
  $$H_{\text{active}} = 8,760\text{ hours/year} \times 0.8961 = \mathbf{7,849.9\text{ operating hours/year}}$$

All annual figures are calculated by integrating weighted hourly savings across the 100 operating percentiles over this standardized $7,849.9\text{ hr/yr}$ baseline.

---

### 2. Multi-Boundary Economic Valuation Framework
To prevent double-counting and eliminate confusion between internal utility charges and commercial gas markets, economic benefits are reported across three distinct, self-contained accounting boundaries:

| Economic Valuation Basis | Pricing Metric | Applicable Tariff / Price | Physical Basis | Annual Economic Benefit (USD/year) | Practical Industrial Interpretation |
|:---|:---|:---:|:---|---:|:---|
| **Boundary 1: Internal Steam Transfer** | Utility Cost Allocation | **$8.50 / ton steam** | $75,972.9\text{ tons steam/yr}$ | **$645,770** | Immediate operating cost reduction recorded by Train H production center |
| **Boundary 2: Domestic Fuel Gas Parity** | Indonesian HGBT Policy (Kepmen ESDM 91/2020) | **$6.00 / MMBtu** | $218,945\text{ MMBtu/yr}$ | **$1,313,669** | Value of conserved feed gas if re-directed to domestic pipeline customers |
| **Boundary 3: Export LNG Netback Parity** | Spot / Long-Term LNG FOB Bontang | **$6.58 / MMBtu** | $218,945\text{ MMBtu/yr}$ | **$1,440,657** | Additional LNG export revenue if conserved boiler fuel is liquefied and sold |

**Guidance for Reviewers:**
These figures represent alternative realizations of the same thermodynamic efficiency gain. They must **NOT** be summed together. The primary operational figure is **USD 645,770/year** (internal utility saving), while the macroscopic commercial value reaches **USD 1.44 million/year** under LNG export parity.
