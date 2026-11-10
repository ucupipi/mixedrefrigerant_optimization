# Aspen HYSYS Simulation Models — PT Badak NGL C3MR Train H

Dokumen ini menjelaskan model simulasi proses Aspen HYSYS V12.1 yang digunakan untuk penelitian:
**"Optimasi Komposisi dan Laju Sirkulasi Mixed Refrigerant Berbasis Machine Learning untuk Meningkatkan Efisiensi Energi Sistem C3MR Train H PT Badak NGL."**

---

## 1. Spesifikasi Perangkat Lunak & Fluid Package
* **Simulator:** Aspen HYSYS V12.1 (atau versi kompatibel di atasnya).
* **Property Package:** Peng–Robinson Equation of State (PR-EOS).
* **Komponen Termodinamika:** Nitrogen ($N_2$), Methane ($C_1$), Ethane ($C_2$), Ethylene ($C_2H_4$), Propane ($C_3$), i-Butane ($iC_4$), n-Butane ($nC_4$), i-Pentane ($iC_5$).
* **Basis Aliran:** Data telemetri DCS Train H Kilang Badak LNG periode 2024–2026.

---

## 2. Berkas Simulasi Utama

### A. Model Alur Proses Lengkap Kilang
1. **`C3MR.hsc`**:
   * Flowsheet proses dasar C3MR Train H mencakup siklus prapendinginan propana 3-tingkat dan siklus refrigeran campuran (MCR).
   * Aliran umpan gas alam: laju alir, tekanan $41{,}2\text{ kgf/cm}^2\text{G}$, dan suhu masuk MCHE $-33{,}0^\circ\text{C}$.

2. **`MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc`**:
   * Model flowsheet termutakhir yang mengintegrasikan penukar panas **4E-40** (chiller propana subcooling lanjutan dari 4E-14 menuju reflux drum 3C-2 dan MCHE 5E-1).
   * Dilengkapi sirkuit modulasi katup kickback sekunder kompresor (`4UV-53`) dan katup pemanas hisap (`4TV-510`) untuk verifikasi batas anti-surge $480{,}0\text{ t/jam}$ serta batas interlock TAL $-45{,}0^\circ\text{C}$.

---

## 3. Kasus Validasi Beban Operasi (`validation_cases/`)
Folder `validation_cases/` memuat 15 berkas kasus independen untuk membandingkan kondisi baseline operasional aktual versus kondisi optimal terprediksi di seluruh kuantil beban produksi:

| Kasus Simulasi | Kuantil Beban | Laju Alir LNG ($\text{t/jam}$) | Deskripsi Kasus |
|---|:---:|:---:|---|
| `P10_Baseline.hsc` | P10 (Turndown Ekstrem) | 141,2 | Kondisi aktual DCS: crossover termal $\text{MITA} = -17{,}65^\circ\text{C}$, SEC tinggi. |
| `P10_Optimized.hsc` | P10 (Turndown Ekstrem) | 141,2 | Kondisi optimal: formula MR optimal, $\text{MITA} = +8{,}48^\circ\text{C}$, kickback 4UV-53 aktif. |
| `P25_Baseline.hsc` & `P25_Optimized.hsc` | P25 (Beban Rendah) | 205,8 | Evaluasi transisi turndown. |
| `P40_Baseline.hsc` & `P40_Optimized.hsc` | P40 (Beban Menengah-Bawah) | 270,4 | Validasi kenaikan efisiensi politropik kompresor. |
| `P50_Baseline.hsc` & `P50_Optimized.hsc` | P50 (Beban Median) | 313,5 | Evaluasi performa tipikal kilang. |
| `P60_Baseline.hsc` & `P60_Optimized.hsc` | P60 (Beban Menengah-Atas) | 356,5 | Validasi neraca uap turbin 4KT-1/2/3. |
| `P75_Baseline.hsc` & `P75_Optimized.hsc` | P75 (Beban Tinggi) | 421,1 | Evaluasi kapasitas MCHE. |
| `P90_Baseline.hsc` | P90 (Beban Penuh / Baseload) | 485,7 | Kondisi operasi puncak aktual: daya total $108{,}06\text{ MW}$. |
| `P90_Optimized.hsc` | P90 (Beban Penuh / Baseload) | 485,7 | Kondisi operasi optimal: daya total $79{,}08\text{ MW}$, hemat $28{,}97\text{ MW}$ ($-26{,}81\%$). |
| `test_p10_enhanced.hsc` | P10 (Uji Ekstra) | 141,2 | Kasus uji sensitivitas sirkuit reheat 4TV-510. |

---

## 4. Panduan Menjalankan Simulasi (Reproducibility)
1. Buka berkas `.hsc` yang diinginkan menggunakan **Aspen HYSYS V12.1**.
2. Pastikan Solver berada dalam mode **Active** (warna hijau di status bar).
3. Untuk menguji formula komposisi MR optimum pada stream `MCR to 5E-1`:
   - Masukkan komposisi fraksi mol: $N_2 = 0{,}0377$, $C_1 = 0{,}4222$, $C_2 = 0{,}4367$, $C_2H_4 = 0{,}0153$, $C_3 = 0{,}0882$.
   - Sesuaikan laju alir sirkulasi MCR ke $590{,}0\text{ t/jam}$ pada beban P90 atau $504{,}0\text{ t/jam}$ pada turndown.
4. Buka unit operation `5E-1` (MCHE) dan periksa tab **Performance** $\rightarrow$ **Tables**:
   - Amati kurva komposit pendinginan (*Hot and Cold Composite Curves*).
   - Verifikasi bahwa $\text{MITA} \ge +1{,}50^\circ\text{C}$ tanpa ada perpotongan suhu ($\Delta T > 0$).
5. Periksa daya poros kompresor `4K-1`, `4K-2`, dan `4K-3` untuk memverifikasi kesesuaian neraca energi.

