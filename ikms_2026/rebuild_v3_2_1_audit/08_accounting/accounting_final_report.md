# INDEPENDENT ENERGY, FUEL GAS, EMISSIONS & ECONOMIC ACCOUNTING REPORT
## REBUILD v3.2.1 — BADAK LNG TRAIN H C3MR FORENSIC QUALIFICATION
**Phase P7 Deliverable — Strict Compliance with AGENTS.md**

---

### 1. Executive Forensic Summary

Phase P7 establishes the final closed accounting framework spanning shaft work, steam production, boiler fuel gas demand, IPCC CO2 abatement, and commercial economics.

Key Forensic Determinations:
1. **Unclipped Casing Energy Decomposition Closure**:
   - The $0.48\text{ GWh/yr}$ discrepancy in Rebuild v3 was formally traced to `np.maximum(..., 0.0)` clipping of local negative power adjustments during turndown.
   - Rebuild v3.2.1 integrates all casing power variations without clipping, achieving **exact closure ($\sum \Delta E_k - \Delta E_{\text{total}} = 0.000000\text{ GWh/yr}$)** across all operating points.
   - For Recommended Candidate B ($16.85\text{ GWh/yr}$ total savings):
     - **MCR Compressors (4K-2 + 4K-3):** $11.16\text{ GWh/yr}$ ($66.23\%$).
     - **Propane Compressor (4K-1):** $5.69\text{ GWh/yr}$ ($33.77\%$).
   - For Robust Candidate R ($13.92\text{ GWh/yr}$ total savings):
     - **MCR Compressors (4K-2 + 4K-3):** $9.22\text{ GWh/yr}$ ($66.24\%$).
     - **Propane Compressor (4K-1):** $4.70\text{ GWh/yr}$ ($33.76\%$).
2. **Dual-Basis Boiler Fuel Gas Reconciliation**:
   - Both **ASME PTC 4.1 Theoretical ($97.70\text{ Nm}^3/\text{t}$)** and **DCS Field Empirical ($79.76\text{ Nm}^3/\text{t}$)** specific fuel consumption metrics are reported side-by-side.
   - For Candidate B: Annual fuel gas savings equal **$6.903\text{ MNm}^3/\text{yr}$** (ASME) and **$5.635\text{ MNm}^3/\text{yr}$** (Field).
   - For Candidate R: Annual fuel gas savings equal **$5.703\text{ MNm}^3/\text{yr}$** (ASME) and **$4.656\text{ MNm}^3/\text{yr}$** (Field).
3. **GC-Derived Fuel Gas Heating Value**:
   - Reconciled from 2,531 field gas chromatograms as **$\text{LHV} = 36.24\text{ MJ/Nm}^3$** ($972.5\text{ BTU/scf}$), resolving the historical discrepancy between stated text ($38.21\text{ MJ/Nm}^3$) and code ($33.10\text{ MJ/Nm}^3$).
4. **IPCC 2006 CO2 Abatement**:
   - Emission factor: $56.10\text{ t CO}_2/\text{TJ}$ (natural gas combustion).
   - Candidate B avoids **$14,034.4\text{ t CO}_2/\text{yr}$** (ASME) and **$11,455.5\text{ t CO}_2/\text{yr}$** (Field).
   - Candidate R avoids **$11,595.3\text{ t CO}_2/\text{yr}$** (ASME) and **$9,464.9\text{ t CO}_2/\text{yr}$** (Field).
5. **Economic Valuation & Zero Double Counting**:
   - Economic value is realized strictly through diverted boiler fuel gas retained as LNG product. Double counting between shaft work, steam, and fuel gas is strictly avoided.
   - At long-term Asian LNG contract pricing (USD 10.50 / MMBtu):
     - Candidate B delivers **USD 2.492M/yr** (ASME) or **USD 2.034M/yr** (Field).
     - Candidate R delivers **USD 2.059M/yr** (ASME) or **USD 1.681M/yr** (Field).

---

### 2. Equipment-Specific Energy Decomposition Matrix (Unclipped)

| Candidate ID | Propane (4K-1) | MCR LP (4K-2) | MCR HP (4K-3) | Total MCR | Total Train C3MR | Closure Error |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate A** | 6.77 GWh | 5.95 GWh | 7.34 GWh | 13.29 GWh | **20.06 GWh** | **0.000000 GWh** |
| **Candidate B** | 5.69 GWh | 5.00 GWh | 6.16 GWh | 11.16 GWh | **16.85 GWh** | **0.000000 GWh** |
| **Candidate C** | 4.52 GWh | 3.97 GWh | 4.91 GWh | 8.88 GWh | **13.40 GWh** | **0.000000 GWh** |
| **Candidate D** | 0.00 GWh | 0.00 GWh | 0.00 GWh | 0.00 GWh | **0.00 GWh** | **0.000000 GWh** |
| **Candidate R** | 4.70 GWh | 4.13 GWh | 5.09 GWh | 9.22 GWh | **13.92 GWh** | **0.000000 GWh** |

---

### 3. Fuel Gas, Steam & CO2 Emissions Accounting

| Candidate ID | Steam Saved (kt/yr) | Fuel Gas ASME (MNm$^3$) | Fuel Gas Field (MNm$^3$) | CO$_2$ ASME (t/yr) | CO$_2$ Field (t/yr) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Candidate A** | 84.11 | 8.218 | 6.709 | 16,707.9 | 13,637.7 |
| **Candidate B** | 70.65 | 6.903 | 5.635 | 14,034.4 | 11,455.5 |
| **Candidate C** | 56.19 | 5.489 | 4.481 | 11,160.0 | 9,109.3 |
| **Candidate D** | 0.00 | 0.000 | 0.000 | 0.0 | 0.0 |
| **Candidate R** | 58.37 | 5.703 | 4.656 | 11,595.3 | 9,464.9 |

---

### 4. Economic Valuation Matrix (No Double Counting)

All figures in **Million USD / year**:

| Candidate ID | DMO (USD 6/MMBtu) | Asian Contract (USD 10.50) | Spot (USD 14/MMBtu) | Carbon Credit (USD 15/t) |
| :--- | :---: | :---: | :---: | :---: |
| **Candidate B (ASME)** | $1.424M | **$2.492M** | $3.323M | +$0.211M (Conditional) |
| **Candidate B (Field)**| $1.162M | **$2.034M** | $2.712M | +$0.172M (Conditional) |
| **Candidate R (ASME)** | $1.176M | **$2.059M** | $2.745M | +$0.174M (Conditional) |
| **Candidate R (Field)**| $0.960M | **$1.681M** | $2.241M | +$0.142M (Conditional) |

---

### 5. Gate 7 Evaluation (Accounting Qualification)

| Gate Criterion | Requirement | Finding | Status |
| :--- | :--- | :--- | :--- |
| **Criterion 7.1** | Unclipped casing energy closure | Closure error = 0.000000 GWh/yr verified | **PASS** |
| **Criterion 7.2** | Dual SFC reporting | ASME 97.70 vs Field 79.76 Nm3/t reported side-by-side | **PASS** |
| **Criterion 7.3** | GC-derived LHV application | 36.24 MJ/Nm3 applied consistently | **PASS** |
| **Criterion 7.4** | IPCC 2006 CO2 abatement | Stoichiometric combustion verified without arbitrary multipliers | **PASS** |
| **Criterion 7.5** | Non-double-counted economics | Fuel gas diversion economics verified; carbon credits conditional | **PASS** |

**GATE 7 STATUS: PASSED (QUALIFIED FOR PHASE P8 EXECUTION)**
