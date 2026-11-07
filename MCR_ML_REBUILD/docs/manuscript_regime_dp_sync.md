# Sinkronisasi Naskah Ilmiah & Laporan Kompetisi OILWEEK 2026
## Optimasi Komposisi Mixed Refrigerant (MCR) & Laju Sirkulasi C3MR dengan Kendala Hidraulik $\Delta P$ MCHE `5E-1` dan Batas Termal *Cold Bundle* pada Rezim *Underload* vs *Baseload*

Dokumen ini menyajikan teks naskah siap pakai (*ready-to-insert manuscript sections*), tabel evaluasi, serta sitasi halaman buku manual resmi Badak LNG untuk disinkronkan langsung ke dalam paper/laporan kompetisi **OILWEEK 2026**.

---

## 1. Abstrak yang Disinkronkan (*Synchronized Abstract — Ready to Insert*)

> **Abstract:**  
> When incoming feed gas to an industrial propane-precooled mixed refrigerant (C3MR) liquefaction train drops below design capacity, centrifugal refrigerant compressors (`4K-2`/`4K-3`) cannot reduce mass throughput below the anti-surge flow floor ($\ge 480.0\text{ t/h}$). Consequently, specific energy consumption rises sharply during turndown. This study develops a physics-constrained machine learning surrogate and multi-component refrigerant (MCR) optimization framework for Badak LNG Plant-5 Main Cryogenic Heat Exchanger (`5E-1`) and Plant-4 Suction Drums (`4C-7`/`4C-8`) using 10,318 active shift records (`master_shift_level.parquet`) and official plant operating manuals (`BOOK-5`, `BOOK-6`, and Technical Memorandum `156/BP31/2020-113`). Empirical partitioning across Underload ($\le 226.8\text{ t/h}$ treated gas, $N=2{,}587$), Transition ($226.8–279.8\text{ t/h}$, $N=5{,}150$), and Baseload ($\ge 279.8\text{ t/h}$, $N=2{,}581$) reveals two distinct thermodynamic and hydraulic regimes:
> 1. **Underload Regime ($\le 226.8\text{ t/h}$):** Because refrigerant circulation is pinned near the anti-surge floor, MCR composition variations account for only $\Delta R^2 = +2.98\%$ of shaft power variance. Reduced feed gas heat input causes heavy hydrocarbons ($C_2, C_3$) to pool in the lower shell, increasing the warm-to-cold bundle differential pressure ratio ($\Delta P_{\text{warm}}/\Delta P_{\text{cold}} = \text{H5PDI003}/\text{H5PDI004}$) by $+29.9\%$ from $2.412$ (Baseload) to $3.131$ (Underload). Furthermore, raising nitrogen ($N_2$) during underload lowers the mixture bubble point across expansion valve `5PV-15`, depressing Cold Bundle LNG rundown temperature (`H5TI0029`, $r = -0.6867$) to $-154.8^\circ\text{C}$. Optimal underload operation caps $N_2$ at its first-quartile efficient level ($2.28\text{ mol\%}$), trims propane ($C_3$, $r = -0.7601$ with suction temperature `H4TI004B`) to prevent liquid carryover above the Temperature Alarm Low ($\text{TAL} \ge -45.0^\circ\text{C}$) and trip ($\text{TALL} = -51.0^\circ\text{C}$) interlocks, and minimizes MCR circulation toward $480.0\text{ t/h}$.
> 2. **Baseload Regime ($\ge 279.8\text{ t/h}$):** Composition sensitivity increases $2.35\times$ ($\Delta R^2 = +7.00\%$). High vapor velocity pushes Warm Bundle differential pressure (`H5PDI003`) toward the pre-shutdown alarm (`PDAH` $0.42\text{ kg/cm}^2$) and emergency trip (`5PDAHH-25A/B` $0.51–0.54\text{ kg/cm}^2$) required to protect the internal aluminum liquid distributor (*"chinese hat"*) welds, while HP MCR turbine `4KT-3` reaches 100% high-pressure steam valve opening. Shifting the 5-component MCR recipe toward the empirical efficient centroid ($N_2 = 3.56\text{ mol\%}$, $C_1 = 43.46\text{ mol\%}$, $C_2 = 44.89\text{ mol\%}$, $C_2H_4 = 0.13\text{ mol\%}$, $C_3 = 7.96\text{ mol\%}$) within the 95% Aitchison Isometric Log-Ratio ellipsoid ($D_M \le 3.0802$) lowers Warm Bundle $\Delta P$ from $0.298$ to $0.276\text{ kg/cm}^2$ ($0.43$ to $0.40\text{ kg/cm}^2$ at peak rate) and transfers cooling load to propane compressor `4KT-1`.
> 
> Evaluated on an out-of-sample chronological test split with a 14-feature monotonic `HistGradientBoostingRegressor`, the surrogate achieves $R^2_{\text{test}} = 0.9954$, $\text{MAE} = 0.278\text{ MW}$ (95% CI: $[0.229, 0.347]\text{ MW}$), and relative error $\text{NMAE} = 0.325\% < 1.0\%$. Across the full Train C3MR battery limit (`4KT-2/3` MCR + `4KT-1` propane), the framework delivers $28.9718\text{ MW}$ ($-26.81\%$) shaft power reduction at P90 ($10.8261\text{ MW}$ direct MCR + $18.1457\text{ MW}$ indirect propane precooling) while satisfying $\text{MITA} \ge 1.50^\circ\text{C}$, $\text{H5PDI003} < 0.42\text{ kg/cm}^2$, and $\text{H4TI004B} \ge -45.0^\circ\text{C}$.

---

## 2. Tabel Standar untuk Bab Metodologi & Hasil (*Publication-Ready Tables*)

### Tabel 1 — Spesifikasi Mekanikal, Hidraulik $\Delta P$, dan Interlock Keselamatan MCHE `5E-1` & `4C-7/8`
*(Sumber: `BOOK-6 (Plant-5_Liquefaction Unit)` hlm. 27–43, 52, 65–66; `BOOK-5 (Plant-4_MCR Refrigeration System)` hlm. 16, 109; Memo `156/BP31/2020-113` hlm. 2–4)*

| Parameter / Instrumen DCS | Lokasi Fisik | Rentang Operasi Normal | Ambang Alarm (`PDAH` / `TAL`) | Ambang Trip Darurat (`PDAHH` / `TALL`) | Konsekuensi Fisik & Tindakan Pengaman |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`H5PDI003` (`5PDI-3`)** | Shell-Side $\Delta P$ Warm Bundle `5E-1` | $0.30–0.40\text{ kg/cm}^2$ | **$0.42\text{ kg/cm}^2$** | **$0.51–0.54\text{ kg/cm}^2$** (`5PDAHH-25A/B` 2oo2) | Mencegah patahnya las aluminium pelat distributor cairan (*"chinese hat"*) akibat gaya angkat uap. |
| **`H5PDI004` (`5PDI-4`)** | Shell-Side $\Delta P$ Cold Bundle `5E-1` | $0.05–0.13\text{ kg/cm}^2$ | **$0.17\text{ kg/cm}^2$** | Non-trip (Monitoring) | Deteksi dini pembekuan hidrokarbon berat/benzena atau *liquid flooding* di *Cold Bundle*. |
| **`H4TI004B` (`4TI-4B`)** | Suhu Gas Masuk Suction Drum `4C-7/8` | $-38.0^\circ\text{C}$ s/d $-42.0^\circ\text{C}$ | **$-45.0^\circ\text{C}$ (`TAL`)** | **$-51.0^\circ\text{C}$ (`TALL`)** (`4TALL-4ABC` 2oo3) | Saat $\text{TAL}$: katup *reheat* `4TV-510` membuka. Saat $\text{TALL}$: trip turbin `4KT-2` untuk cegah *liquid carryover*. |
| **`H5TIC01A` / `H5TI0029`** | Suhu Produk LNG Keluar Cold Bundle | $-148.0^\circ\text{C}$ s/d $-150.0^\circ\text{C}$ | **$-152.0^\circ\text{C}$** (Batas *Overcooling*) | **$-173.0^\circ\text{C}$ (`MMDT`)** | Menjaga subcooling LNG tanpa memicu *overcooling* akibat kelebihan fraksi volatil $N_2$. |
| **`H4FI001` (`4FI-1`)** | Laju Sirkulasi Massal MCR Total | $480.0–720.0\text{ t/h}$ | **$480.0\text{ t/h}$** (Lantai *Anti-Surge*) | Surge Kompresor `4K-2/3` | Katup *kickback* `4UV-53` membuka sebagai pengaman batas bawah aliran ($\ge 480.0\text{ t/h}$). |
| **$\text{MITA}$ MCHE `5E-1`** | Pendekatan Suhu Internal 100-Slice | $1.80^\circ\text{C}$ s/d $4.50^\circ\text{C}$ | **$1.50^\circ\text{C}$** (Batas Bawah) | $\le 0.00^\circ\text{C}$ (Crossover) | Mencegah pelanggaran Hukum II Termodinamika dan hilangnya kapasitas pindah panas. |

---

### Tabel 2 — Perbandingan Empiris Rezim *Underload* vs *Transition* vs *Baseload* (`master_shift_level.parquet`)
*(Sumber: Analisis 10.318 shift aktif & 1.475 shift kromatografi gas `4C-8` pada `master_shift_level.parquet`)*

| Variabel Proses / Komposisi | Satuan | Underload ($\le 226.8\text{ t/h}$) | Transition ($226.8–279.8\text{ t/h}$) | Baseload ($\ge 279.8\text{ t/h}$) | Interpretasi Termodinamika & Hidraulik |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Laju Gas Umpan (`H1FI012`)** | $\text{t/h}$ | $193.34$ ($\le 226.8$) | $254.31$ | $295.63$ ($\ge 279.8$) | Kuartil operasi alami kilang ($P_{25} = 226.8\text{ t/h}$, $P_{75} = 279.8\text{ t/h}$). |
| **Warm Bundle $\Delta P$ (`H5PDI003`)** | $\text{kg/cm}^2$ | $0.1640 \pm 0.0619$ | $0.2646 \pm 0.0321$ | $0.2950 \pm 0.0304$ | Mengikuti hukum *non-Darcy* $\Delta P_{\text{warm}} = \exp(-9.6558) W^{1.497}$ ($R^2 = 0.8432$). |
| **Cold Bundle $\Delta P$ (`H5PDI004`)** | $\text{kg/cm}^2$ | $0.0507 \pm 0.0115$ | $0.1080 \pm 0.0195$ | $0.1257 \pm 0.0257$ | Mengikuti hukum *non-Darcy* $\Delta P_{\text{cold}} = \exp(-11.1937) W^{1.593}$ ($R^2 = 0.8861$). |
| **Rasio $\Delta P_{\text{warm}} / \Delta P_{\text{cold}}$** | — | **$3.131 \pm 0.652$** | $2.518 \pm 0.395$ | **$2.412 \pm 0.318$** | Naik $+29.9\%$ saat *underload* akibat genangan cairan berat ($C_2/C_3$) di *Warm Bundle*. |
| **Resep Q1 Terbaik ($N_2 / C_1 / C_2 / C_2H_4 / C_3$)** | $\text{mol\%}$ | $2.28 / 44.09 / 47.03 / 0.00 / 6.59$ | $3.40 / 44.70 / 45.27 / 1.89 / 4.75$ | $3.56 / 43.46 / 44.89 / 0.13 / 7.96$ | Pada *underload*, $N_2$ dibatasi rendah ($2.28\%$ vs $2.87\%$ Q4) agar tidak memicu *overcooling*. |
| **Cold Bundle MR Out (`H5TI0025`)** | $^\circ\text{C}$ | $-124.93$ (P50: $-125.55$) | $-123.41$ | $-122.36$ (P50: $-122.33$) | Penurunan $-2.56^\circ\text{C}$ pada *underload* akibat kelebihan rasio pendingin terhadap gas umpan. |
| **Suction Drum Temp (`H4TI004B`)** | $^\circ\text{C}$ | $-30.99$ (Q1: $-38.91$) | $-38.45$ (Q1: $-40.75$) | $-41.24$ (Q1: $-41.42$) | Dijaga aman di atas $\text{TAL} = -45.0^\circ\text{C}$ melalui pemangkasan $C_3$ ($r = -0.7601$). |

---

### Tabel 3 — Evaluasi Model Surrogate `HistGradientBoosting` (14 Fitur Fisik, Satuan Proporsional MW)
*(Mematuhi `AGENTS.md` Pasal 2 & Pasal 13: pelaporan dalam satuan proporsional **MW** dan persentase kesalahan relatif **NMAE $< 1.0\%$**)*

| Model / Konfigurasi Evaluasi | $R^2_{\text{test}}$ ($\ge 0.60$) | $\text{MAE}$ ($\text{MW}$, $< 1.0\text{ MW}$) | $\text{RMSE}$ ($\text{MW}$) | Relative Error / $\text{NMAE}$ ($\%$, $< 1.0\%$) | 95% Bootstrap CI $\text{MAE}$ ($\text{MW}$) | Status Kualifikasi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dummy Mean Baseline** | $-1.0255$ | $6.060\text{ MW}$ | $7.215\text{ MW}$ | $7.074\%$ | — | Ditolak (Baseline) |
| **Ridge Linear Baseline (L2)** | $0.9981$ | $0.169\text{ MW}$ | $0.219\text{ MW}$ | $0.197\%$ | — | Pembanding Linier |
| **Monotonic HGB Surrogate (14 Fitur Fisik + $\Delta P$)** | **$0.9954$** | **$0.278\text{ MW}$** | **$0.345\text{ MW}$** | **$0.325\%$** | **$[0.229, 0.347]\text{ MW}$** | **LULUS KUALIFIKASI** |

---

### Tabel 4 — Dekomposisi Penghematan Daya Poros pada Batas Sistem (*Battery Limit* Train C3MR)
*(Mematuhi `AGENTS.md` Pasal 9 & Pasal 10: memisahkan penghematan langsung kompresor MCR `4KT-2/3` dan tidak langsung kompresor propana `4KT-1`)*

| Komponen Unit Kompresor | Tag Peralatan | Penghematan Daya Poros ($\text{MW}$) | Penghematan Daya Poros ($\text{kW}$) | Persentase Reduksi ($\%$) | Mekanisme Fisik Penghematan |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Kompresor MCR Tingkat 1 & 2 (Langsung)** | `4K-2` / `4K-3` (`4KT-2/3`) | **$10.8261\text{ MW}$** | $10{,}826.1\text{ kW}$ | **$-13.85\%$** | Penurunan laju sirkulasi MCR (`H4FI001`) dan pencocokan kurva komposit MCHE `5E-1`. |
| **Kompresor Propana C3 (Tidak Langsung / Precooling)** | `4K-1` (`4KT-1`) | **$18.1457\text{ MW}$** | $18{,}145.7\text{ kW}$ | **$-34.80\%$** | Penurunan beban kondensasi awal MCR pada *propane chillers* `3E-14/17/18`. |
| **Total Train C3MR (Beban P90)** | `4KT-1` + `4KT-2/3` | **$28.9718\text{ MW}$** | $28{,}971.8\text{ kW}$ | **$-26.81\%$** | Jumlah aljabar eksak $\Delta \dot{W}_{\text{MCR, direct}} + \Delta \dot{W}_{\text{C3, precooling}}$. |
| **Total Train C3MR (Rata-Rata Terbobot Tahunan)** | `4KT-1` + `4KT-2/3` | **$28.9833\text{ MW}$** | $28{,}983.3\text{ kW}$ | **$-27.10\%$** | Penghematan uap $239{,}889.7\text{ t/yr}$, biaya $\text{USD } 8.48\text{M/yr}$, emisi $49{,}961.8\text{ t CO}_2\text{/yr}$. |

