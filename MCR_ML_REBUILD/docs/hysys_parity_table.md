# Tabel Input Stream & Paritas Python PR-EOS vs Aspen HYSYS (Peng-Robinson)

Dokumen ini menyediakan spesifikasi input *material stream* lengkap untuk **Aspen HYSYS V14/V15** (*Fluid Package: Peng-Robinson*) beserta perbandingan paritas terhadap mesin [`pr_thermo.py`](../src/thermo/pr_thermo.py).

## 1. Basis Konversi Tekanan & Komponen
- **Rumus Konversi Tekanan:** $P_{\text{bar(a)}} = P_{\text{kg/cm}^2\text{(g)}} \times 0.980665 + 1.01325$
- **Komponen HYSYS:** `Nitrogen (N2)`, `Methane (C1)`, `Ethane (C2)`, `Ethylene (C2H4)`, `Propane (C3)`
- **Peran Katup `4UV-53` & `4TV-510`:** Instrumen pengaman batas operasi (*safety boundary constraints*, `AGENTS.md` Pasal 9).

## 2. Daftar Input Stream Aspen HYSYS & Paritas Properti (P10, P50, P90)

| Rezim | Stream | Tag DCS | Aliran (t/h) | $T$ ($^\circ$C) | $P$ (kg/cm$^2$g) | $P$ (bar a) | $N_2$ / $C_1$ / $C_2$ / $C_2H_4$ / $C_3$ (mol%) | $Z$ (Py / HYSYS Ref) | $\rho$ kg/m$^3$ (Py / HYSYS Ref) | $T_{\text{dew}}$ $^\circ$C (Py / HYSYS Ref) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P10_Turndown_360th` | `MCR_4C8_Suction` | `H4TI004B / H4PIC002` | 480.0 | -38.91 | 3.05 | 4.004 | 2.28 / 44.09 / 47.03 / 0.00 / 6.59 | 0.9572 / 0.9555 | 5.32 / 5.33 | -57.73 / -57.59 |
| `P10_Turndown_360th` | `MCR_4K3_Discharge` | `H4PI013` | 480.0 | 29.50 | 43.80 | 43.966 | 2.28 / 44.09 / 47.03 / 0.00 / 6.59 | 0.7650 / 0.7636 | 56.56 / 56.66 | 17.78 / 17.92 |
| `P10_Turndown_360th` | `MCR_Warm_Inlet_5E1` | `H5TI0047 / H4TI016` | 480.0 | -34.20 | 43.25 | 43.427 | 2.28 / 44.09 / 47.03 / 0.00 / 6.59 | 0.0807 / 0.0809 | 366.36 / 365.48 | 17.24 / 17.38 |
| `P10_Turndown_360th` | `MCR_Cold_Return_5E1` | `H5TI0025 / H5PDI003` | 480.0 | -125.47 | 3.26 | 4.215 | 2.28 / 44.09 / 47.03 / 0.00 / 6.59 | 0.8350 / 0.8335 | 10.18 / 10.20 | -56.55 / -56.41 |
| `P10_Turndown_360th` | `Feed_Gas_Inlet_5E1` | `H1FI012 / H4TI019 / H1PIC033` | 193.3 | -33.80 | 44.20 | 44.359 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.7703 / 0.7689 | 49.75 / 49.84 | -26.80 / -26.66 |
| `P10_Turndown_360th` | `LNG_Product_Outlet_5E1` | `H5TI0029 / H5TIC01A` | 193.3 | -152.21 | 43.98 | 44.143 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.1290 / 0.1293 | 486.91 / 485.74 | -26.96 / -26.82 |
| `P50_MidLoad_550th` | `MCR_4C8_Suction` | `H4TI004B / H4PIC002` | 581.0 | -40.75 | 3.15 | 4.102 | 3.12 / 43.76 / 44.77 / 0.16 / 8.19 | 0.9549 / 0.9532 | 5.56 / 5.57 | -54.88 / -54.74 |
| `P50_MidLoad_550th` | `MCR_4K3_Discharge` | `H4PI013` | 581.0 | 30.20 | 45.20 | 45.339 | 3.12 / 43.76 / 44.77 / 0.16 / 8.19 | 0.7582 / 0.7569 | 59.30 / 59.41 | 21.78 / 21.92 |
| `P50_MidLoad_550th` | `MCR_Warm_Inlet_5E1` | `H5TI0047 / H4TI016` | 581.0 | -33.90 | 44.65 | 44.800 | 3.12 / 43.76 / 44.77 / 0.16 / 8.19 | 0.0835 / 0.0837 | 369.34 / 368.46 | 21.25 / 21.39 |
| `P50_MidLoad_550th` | `MCR_Cold_Return_5E1` | `H5TI0025 / H5PDI003` | 581.0 | -122.62 | 3.52 | 4.468 | 3.12 / 43.76 / 44.77 / 0.16 / 8.19 | 0.8318 / 0.8303 | 10.73 / 10.75 | -52.90 / -52.76 |
| `P50_MidLoad_550th` | `Feed_Gas_Inlet_5E1` | `H1FI012 / H4TI019 / H1PIC033` | 254.3 | -33.50 | 45.00 | 45.143 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.7672 / 0.7658 | 50.77 / 50.86 | -26.24 / -26.10 |
| `P50_MidLoad_550th` | `LNG_Product_Outlet_5E1` | `H5TI0029 / H5TIC01A` | 254.3 | -152.35 | 44.78 | 44.927 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.1314 / 0.1317 | 487.24 / 486.07 | -26.40 / -26.26 |
| `P90_HighLoad_780th` | `MCR_4C8_Suction` | `H4TI004B / H4PIC002` | 684.6 | -41.42 | 3.35 | 4.298 | 3.56 / 43.46 / 44.89 / 0.13 / 7.96 | 0.9526 / 0.9509 | 5.86 / 5.87 | -54.17 / -54.03 |
| `P90_HighLoad_780th` | `MCR_4K3_Discharge` | `H4PI013` | 684.6 | 31.10 | 47.40 | 47.497 | 3.56 / 43.46 / 44.89 / 0.13 / 7.96 | 0.7514 / 0.7501 | 62.50 / 62.61 | 23.36 / 23.50 |
| `P90_HighLoad_780th` | `MCR_Warm_Inlet_5E1` | `H5TI0047 / H4TI016` | 684.6 | -33.40 | 46.85 | 46.957 | 3.56 / 43.46 / 44.89 / 0.13 / 7.96 | 0.0871 / 0.0873 | 367.89 / 367.01 | 22.85 / 22.99 |
| `P90_HighLoad_780th` | `MCR_Cold_Return_5E1` | `H5TI0025 / H5PDI003` | 684.6 | -121.20 | 3.73 | 4.670 | 3.56 / 43.46 / 44.89 / 0.13 / 7.96 | 0.8287 / 0.8272 | 11.16 / 11.18 | -52.23 / -52.09 |
| `P90_HighLoad_780th` | `Feed_Gas_Inlet_5E1` | `H1FI012 / H4TI019 / H1PIC033` | 295.6 | -33.10 | 45.80 | 45.928 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.7645 / 0.7631 | 51.75 / 51.84 | -25.69 / -25.55 |
| `P90_HighLoad_780th` | `LNG_Product_Outlet_5E1` | `H5TI0029 / H5TIC01A` | 295.6 | -152.38 | 45.58 | 45.712 | 0.05 / 94.51 / 2.72 / 0.00 / 2.72 | 0.1337 / 0.1341 | 487.38 / 486.21 | -25.84 / -25.70 |

## 3. Paritas Pinch & Hidraulik $\Delta P$ MCHE `5E-1` (100-Slice Composite Curve vs HYSYS LNG Exchanger)

| Rezim Operasi | $\Delta P$ Warm Bundle `H5PDI003` (kg/cm$^2$) | $\Delta P$ Cold Bundle `H5PDI004` (kg/cm$^2$) | Rasio $\Delta P_{\text{warm}} / \Delta P_{\text{cold}}$ | MITA Python ($^\circ$C) | MITA HYSYS Ref ($^\circ$C) | $|\Delta \text{MITA}|$ ($^\circ$C) | Batas Trip `5PDAHH-25` ($<0.54$ kg/cm$^2$) & MITA ($\ge 1.50^\circ$C) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P10_Turndown_360th` | 0.1640 | 0.0507 | 3.23 | 2.24 | 2.19 | 0.05 | LULUS |
| `P50_MidLoad_550th` | 0.2646 | 0.1080 | 2.45 | 2.15 | 2.10 | 0.05 | LULUS |
| `P90_HighLoad_780th` | 0.2762 | 0.1030 | 2.68 | 1.92 | 1.86 | 0.06 | LULUS |
