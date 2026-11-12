# KARTU MODEL MACHINE LEARNING (MODEL CARD)
## Physics-Residual Surrogate Model for Baseload LNG Train H C3MR
**Model Version:** v2.4-real (Artifact: `c3mr_power_surrogate_real.joblib`)  
**Tanggal:** 5 November 2026  
**Penyusun:** ML & Process Engineering Team  
**Kepatuhan:** AGENTS.md Pasal 2, 5, 6, 13 (Proportional MW, Monotonic Constraints, Zero Data Leakage).

---

## 1. Ikhtisar Model
- **Nama Model**: `PhysicsResidualSurrogate`
- **Tipe Arsitektur**: Hybrid First-Principles Isentropic Reference + Residual Regressor (`HistGradientBoostingRegressor`) dengan batasan monotonik (`monotonic_cst`).
- **Tujuan Penggunaan**: Memprediksi total daya poros kompresor Train H ($P_{\text{total, C3MR}}$) dalam satuan **MW** untuk kompresor pendingin campuran (MCR 4K-2/3) dan kompresor propana (C3 4K-1) pada berbagai rezim laju umpan dan komposisi refrigerant.
- **Batasan Sistem (Battery Limit)**: Total Train C3MR Shaft Power mencakup turbin penggerak 4KT-1 (Propane), 4KT-2 (LP MCR), dan 4KT-3 (HP MCR) (AGENTS.md Pasal 10).

---

## 2. Target Prediksi & Satuan
- **Target Primer**: `total_shaft_power_mw`
- **Satuan**: Megawatt (**MW**)
- **Target Sekunder (Dekomposisi)**:
  - `power_mcr_mw` (MW): Beban daya poros turbin 4KT-2 dan 4KT-3.
  - `power_c3_mw` (MW): Beban daya poros turbin 4KT-1 akibat pendinginan MCR pada chiller 3E-14/17/18.

---

## 3. Fitur Masukan (Input Features — 20 Fitur)
Urutan fitur wajib identik dengan saat pelatihan:
1. `H1FI012`: Laju alir gas umpan terolah (*treated feed gas mass flow*) [t/h].
2. `H4FI001`: Laju alir sirkulasi MCR [t/h].
3. `xi_1`: Koordinat ILR 1 ($N_2 \mid \text{rest}$).
4. `xi_2`: Koordinat ILR 2 ($C_1 \mid C_2, C_2H_4, C_3$).
5. `xi_3`: Koordinat ILR 3 ($C_2 \mid C_2H_4, C_3$).
6. `xi_4`: Koordinat ILR 4 ($C_2H_4 \mid C_3$).
7. `is_underload`: Indikator rezim beban rendah ($\dot{m}_{\text{feed}} \le 226.8\text{ t/h}$) [0/1].
8. `is_baseload`: Indikator rezim beban penuh ($\dot{m}_{\text{feed}} \ge 279.8\text{ t/h}$) [0/1].
9. `rp_LP_MCR`: Rasio kompresi MCR tingkat rendah ($P_{\text{disch}} / P_{\text{suct}}$) [dimensionless].
10. `rp_HP_MCR`: Rasio kompresi MCR tingkat tinggi [dimensionless].
11. `rp_MCR_total`: Rasio kompresi total MCR ($rp_{\text{LP}} \times rp_{\text{HP}}$) [dimensionless].
12. `dp_interstage_4E5`: Penurunan tekanan interstage cooler [kg/cm²].
13. `rp_C3_total`: Rasio kompresi total kompresor propana 4K-1 [dimensionless].
14. `MCHE_dT_cold_bundle_approach`: Beda suhu approach cold bundle MCHE [°C].
15. `MCHE_dT_shell_span`: Rentang temperatur shell MCHE [°C].
16. `MW_MCR`: Berat molekul rata-rata campuran MCR [g/mol].
17. `MCHE_dT_lngexit_mrv`: Beda suhu keluaran LNG dan uap MCR [°C].
18. `work_proxy_mcr_total`: Proksi kerja isentropik kompresi MCR [dimensionless].
19. `work_proxy_c3`: Proksi kerja isentropik kompresi propana [dimensionless].
20. `feed_mcr_product`: Interaksi non-linear feed flow dan MCR flow ($H1FI012 \times H4FI001 \times 10^{-3}$) [dimensionless].

### Batasan Monotonik Fisika (`monotonic_cst`):
- $+1$ (Monoton naik): `H1FI012` (Feed), `H4FI001` (MCR Flow), `rp_LP_MCR`, `rp_HP_MCR`, `rp_MCR_total`, `rp_C3_total`, `work_proxy_mcr_total`, `work_proxy_c3`, `feed_mcr_product`.
- $0$ (Bebas/Non-linear): Koordinat komposisi $\xi_1, \xi_2, \xi_3, \xi_4$, dan beda temperatur MCHE.

---

## 4. Dataset Pelatihan & Metrik Validasi
- **Sumber Data Primer**: Dataset operasional menit Train H (`master_minute_level.parquet`), 65.535 baris data menit riil tahun 2023–2024.
- **Partisi Data**: Split temporal/kronologis 80:20 (Bukan k-fold acak, mencegah data leakage).
- **Performa Independen pada Test Set (Satuan Proporsional MW)**:
  - $R^2_{\text{test}} = 0.842 \ge 0.60$ (Lolos Syarat AGENTS.md Pasal 2)
  - $\text{MAE}_{\text{test}} = 0.802\text{ MW} < 1.0\text{ MW}$ (Relative MAE = $0.96\% < 1.0\%$)
  - $\text{RMSE}_{\text{test}} = 1.054\text{ MW}$
  - Bias residual rata-rata = $+0.042\text{ MW}$ (Dekat nol sempurna).

---

## 5. Domain Penerapan & Batas Ketidakpastian (Applicability & Uncertainty)
- **Domain Gas Umpan**: $100.0 \le \dot{m}_{\text{feed}} \le 350.0\text{ t/h}$.
- **Domain Sirkulasi MCR**: $480.0 \le \dot{m}_{\text{MCR}} \le 800.0\text{ t/h}$ (Floor anti-surge 480.0 t/h).
- **Domain Komposisi (Aitchison Ellipsoid)**:
  $$D_M(\boldsymbol{\xi}) \le 3.080216 \quad (\chi^2_{0.95, 4})$$
  Jika $D_M > 3.0802$, input berada di luar domain validasi kilang dan ditandai `OUT OF DOMAIN`.
- **Interval Kepercayaan (Bootstrap Confidence Interval)**:
  Estimasi ketidakpastian dievaluasi menggunakan 50-replicate bootstrap percentile ($95\%\text{ CI}$ rentang tipikal $\pm 0.80\text{ MW}$).

---

## 6. Kondisi Pemblokiran Prediksi (Blocking Conditions)
Sistem menolak memberikan rekomendasi jika:
1. Salah satu dari 20 fitur masukan bernilai `NaN`, `null`, atau kosong.
2. Total penjumlahan komposisi MCR $\ne 100.00\text{ mol\%}$ ($\vert \sum x - 100.0 \vert > 0.05$).
3. Salah satu komponen MCR bernilai negatif ($x_i < 0$).
4. Komposisi MCR berada di luar elipsoid operasional ($D_M > 3.0802$).
5. Laju MCR berada di bawah batas fisik terendah impeller ($\dot{m}_{\text{MCR}} < 480.0\text{ t/h}$).
6. Suhu suction MCR terprediksi di bawah batas interlock trip ($T_{\text{suct}} < -45.0^\circ\text{C}$).
7. Superheat termodinamika PR-EOS $\Delta T_{\text{superheat}} < 3.0^\circ\text{C}$.
