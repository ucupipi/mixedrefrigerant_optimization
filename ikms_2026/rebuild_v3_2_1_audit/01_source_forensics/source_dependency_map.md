# SOURCE DEPENDENCY MAP & DATAFLOW TRACEABILITY
## Badak LNG Plant-3 / Train H C3MR Rebuild v3.2.1 Independent Qualification

```
[Raw Engineering Data Sources]
  ├── Book1.csv (Minute-level DCS telemetries for Plant 3 & Train H: 65,535 rows)
  ├── Plant3_Instrumentation_Tag_List.xlsx (Tag metadata, ranges, engineering units)
  ├── OverallComposition_2023_2024.xlsx (2,531 GC routine analyses, gas_routine sheet)
  └── tag_conflicts.csv (Official tag conflict and measurement boundary resolution)
           │
           ▼
[Rebuild v3 Initial Processing (Preserved Read-Only)]
  ├── 03_gc/mcr_retained_2531.parquet (Cleaned GC dataset)
  ├── 04_constraints/oem_maps_digitized/ (Compressor 4K-1/2/3 head & flow curves)
  └── data/reconciliation/baseline_hysys_vs_dcs_validation_p1_p100.csv (Operating quantiles P1..P100)
           │
           ▼
[Rebuild v3.1 Forensic Audit Findings (Preserved Read-Only)]
  ├── audit_01: Proved Candidate A (C3=10%) was an optimizer boundary arrest artifact
  ├── audit_02: Proved 0.48 GWh/yr discrepancy was caused by np.maximum clipping
  ├── audit_03: Proved 4.040 t/MWh was an aggregate quotient; IAPWS-IF97 yields 4.193 t/MWh
  ├── audit_04: Proved Candidate A has 44.1% probability of violating MITA >= 1.50 C
  ├── audit_05: Proved 148.3 t/h at P10 is 4UV-53 secondary kickback; P90 limit is governor stroke (94.5%)
  ├── audit_06: Exposed synthetic models lacking composition features
  └── audit_07: Exposed code secretly using 33.10 MJ/Nm3 while text claimed 38.21 MJ/Nm3
           │
           ▼
[Rebuild v3.2 Reconstruction (Preserved Read-Only)]
  ├── First unclipped casing energy balance (zero closure error)
  ├── PR-EOS 100-slice MITA and Gouy-Stodola exergy destruction models
  ├── Machine-specific IAPWS-IF97 steam rates (4KT-1: 4.262, 4KT-2: 4.183, 4KT-3: 4.107)
  └── Robust Candidate R identification (nominal MITA = 2.550 C, P_viol = 4.57%)
           │
           ▼
[Rebuild v3.2.1 Independent Forensic Qualification Workspace (ikms_2026/rebuild_v3_2_1_audit/)]
  ├── 00_manifest/ (Cryptographic baseline & integrity verification)
  ├── 01_source_forensics/ (Phase P0: Dependency mapping, formula register, constants catalog)
  ├── 02_steam_balance/ (Phase P1: IAPWS-IF97 steam balance, condensate boundary clarification)
  ├── 03_mche_uncertainty/ (Phase P2: 5C-1 VLE, 4E-40 duty, 100-slice MITA uncertainty)
  ├── 04_rotating_equipment/ (Phase P3: OEM compressor curves, P10 kickback, P90 governor)
  ├── 05_control_apc/ (Phase P4: APC concept definition, Candidate B vs Candidate R feasibility)
  ├── 06_surrogate_qualification/ (Phase P5: Surrogate feature provenance, monotonicity, direct check)
  ├── 07_joint_optimization/ (Phase P6: Continuous load-dependent schedule, 4-cell factorial synergy)
  ├── 08_accounting/ (Phase P7: Exact unclipped casing balance, dual SFC, GC fuel LHV)
  ├── 09_robustness/ (Phase P8: Joint constraint probability & engineering recommendation)
  ├── 10_field_testability/ (Phase P9: Draft plant trial protocol, MOC safeguards)
  ├── 11_manuscript_ledger/ (Phase P9: Claim Evidence Ledger & executive audit reports)
  └── reports/ & tests/ (Master verification runner, regression tests, cryptographic sign-off)
```
