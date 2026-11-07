# Model Card — Badak LNG Plant-3 Train H C3MR Refrigeration ML Suite (`MCR_ML_REBUILD`)

Dokumen Model Card ini menjelaskan tujuan penggunaan (*intended use*), batasan penggunaan di luar cakupan (*out-of-scope use & limitations*), batas keselamatan proses (*operational safety envelope*), arsitektur model, strategi validasi, serta metrik performa kuantitatif untuk sistem pemodelan *Mixed Component Refrigerant* (MCR) dan siklus *Propane-Precooled Mixed Refrigerant* (C3MR).

---

## 1. Ringkasan Model & Arsitektur (Model Details)

- **Nama Proyek & Paket:** `MCR_ML_REBUILD` (`mcr-ml-rebuild` v1.0.0)
- **Lokasi Fasilitas:** PT Badak NGL (Badak LNG), Bontang — Plant-3, Train H (Cryogenic Liquefaction Unit & C3MR Refrigeration System).
- **Keluarga Model:**
  1. **Baseline Models (`src/models/baselines.py`):**
     - `DummyRegressor` (prediksi nilai tengah/rata-rata historis sebagai pembanding dasar $R^2 \approx 0.00$).
     - `Ridge` Linear Regression ($L_2$-regularized linear benchmark pada fitur proses dan koordinat ILR).
  2. **Primary Surrogate Model (`src/models/surrogates.py`):**
     - `HistGradientBoostingRegressor` dengan kendala monotonik fisika (`monotonic_cst`) yang menjamin prediksi daya poros meningkat secara monoton terhadap kenaikan laju alir umpan gas (`+1`) dan kenaikan suhu udara lingkungan (`+1`).
  3. **Compositional Geometry & Thermodynamic Verifier (`src/features/ilr.py`, `src/thermo/pr_thermo.py`):**
     - Transformasi Aitchison *Isometric Log-Ratio* (ILR) berbasis *Sequential Binary Partition* (SBP) 5-komponen ($N_2, C_1, C_2, C_2H_4, C_3$) dari simpleks $S^5$ ke ruang Euclidean $\mathbb{R}^4$, dilengkapi pemverifikasi persamaan keadaan Peng-Robinson (PR-EOS) murni Python.

---

## 2. Tujuan Penggunaan & Batas Cakupan (Intended Use and Out-of-Scope Limitations)

### 2.1 Intended Operational Scope (Tujuan Penggunaan yang Diizinkan)
- **Studi Engineering Offline & Evaluasi Efisiensi Energi:** Menganalisis hubungan antara komposisi Mixed Refrigerant ($N_2, C_1, C_2, C_2H_4, C_3$), laju alir sirkulasi MCR, beban umpan gas alam, dan suhu lingkungan terhadap konsumsi daya poros total Train C3MR (**MW**).
- **Screening Kandidat Operasi Tunak (*Steady-State Advisory*):** Membantu Process Engineer menyaring kandidat komposisi refrigeran pada berbagai tingkat beban produksi (P10 hingga P90) sebelum diverifikasi lebih lanjut menggunakan simulator proses termodinamika (PR-EOS / Aspen HYSYS).
- **Audit Integritas Data & Pencegahan Target Leakage:** Menyediakan pipeline referensi yang bebas dari kebocoran variabel target dan bebas dari duplikasi semu (*pseudo-replication*) data laboratorium GC.

### 2.2 Out-of-Scope Uses & Technical Limitations (Penggunaan di Luar Cakupan)
- **Bukan Pengendali Otomatis Closed-Loop DCS:** Model ini **DILARANG** dihubungkan secara langsung untuk mengubah setpoint katup atau kompresor di Yokogawa Centum VP DCS tanpa tinjauan engineer dan persetujuan operator ruang kontrol (*control room operator*).
- **Tidak Berlaku untuk Kondisi Transien Cepat:** Model dilatih pada rezim operasi tunak (*steady-state shift windows*) dan tidak dirancang untuk memprediksi dinamika *startup*, *shutdown*, *compressor trip*, atau *surge* milidetik.
- **Ekstrapolasi di Luar Elipsoid Historis:** Model tidak boleh digunakan untuk komposisi refrigeran yang berada di luar batas jarak Mahalanobis historis ($D_M > 3.080216$ pada ruang ILR 4-dimensi).

---

## 3. Batas Sistem (Battery Limit) & Dekomposisi Daya

Sesuai `AGENTS.md` Pasal 10, target utama `total_shaft_power_mw` mencakup batas sistem **Total Train C3MR Shaft Power** dalam satuan **MW**:
1. **Kompresor Propana Precooling (`4K-1` / penggerak turbin uap `4KT-1`):** Menangani beban pendinginan awal umpan gas alam dan kondensasi awal MCR pada chiller propana (`3E-14`, `3E-17`, `3E-18`) — komponen `c3_shaft_power_mw`.
2. **Kompresor Mixed Refrigerant (`4K-2` LP / `4KT-2` dan `4K-3` HP / `4KT-3`):** Menangani sirkulasi refrigeran campuran menuju *Main Cryogenic Heat Exchanger* (`4E-1`) — komponen `mcr_shaft_power_mw`.

$$W_{\text{total, C3MR}} \text{ (MW)} = W_{\text{MCR, direct}} \text{ (MW)} + W_{\text{C3, precooling}} \text{ (MW)}$$

---

## 4. Amplop Keselamatan Operasi Kilang (Operational Envelope & Safety Interlocks)

Setiap prediksi dan kandidat titik operasi wajib mematuhi batas keselamatan fisik kilang (*plant safety interlocks*):

| Parameter Keselamatan | Tag / Simbol | Batas Operasi Aman | Peran Instrumen / Konsekuensi Fisik |
| :--- | :--- | :--- | :--- |
| **Compressor Anti-Surge Flow Floor** | `H4FI001` / `4UV-53` | $\ge 480.0\text{ t/h}$ | Batas minimum aliran massa masuk kompresor MCR 1st Stage (`4K-2`). Katup recycle `4UV-53` membuka sebagai pengaman jika sirkulasi MCHE turun di bawah $480.0\text{ t/h}$. |
| **Suction Drum Temperature Alarm Low (TAL)** | `H4TI004B` / `4TV-510` | $\ge -45.0^\circ\text{C}$ | Batas bawah suhu gas keluar suction drum `4C-8` untuk mencegah *liquid carryover* ke impeller kompresor. Katup pemanas ulang `4TV-510` membuka jika suhu mendekati $-45.0^\circ\text{C}$. |
| **Suction Vapor Fraction & Superheat** | $\beta_{\text{suct}}$, $\Delta T_{\text{sh}}$ | $\beta = 1.0000$, $\Delta T_{\text{sh}} \ge 3.0^\circ\text{C}$ | Aliran masuk kompresor wajib 100% fasa uap kering di atas titik embun (*dew point*). |
| **MCHE Minimum Internal Temp. Approach (MITA)** | $\Delta T_{\text{min, MCHE}}$ | $\ge 1.50^\circ\text{C}$ (Guardband $2.00^\circ\text{C}$) | Mencegah pelanggaran Hukum II Termodinamika (*temperature crossover* $\Delta T \le 0^\circ\text{C}$) di sepanjang 100-slice kurva komposit MCHE `4E-1`. |
| **MCHE Bundle Differential Pressure** | `H4PDIC024` | $\le 0.35\text{ kg/cm}^2$ | Menjaga kehilangan tekan hidraulik di dalam *spiral-wound heat exchanger* tetap dalam batas mekanikal. |
| **Compositional Mahalanobis Envelope** | $D_M(\boldsymbol{\xi})$ | $\le 3.080216$ ($\chi^2_{0.95, 4}$) | Menjaga komposisi 5-komponen MCR tetap berada di dalam elipsoid kepercayaan 95% data operasi aktual kilang. |

---

## 5. Metrik Evaluasi Kuantitatif & Kriteria Penerimaan (Quantitative Metrics)

Seluruh evaluasi model dilakukan pada partisi *out-of-sample test set* (pembagian kronologis 80:20 dan `GroupKFold` berbasis `shift_id`) dalam satuan rekayasa proporsional (`AGENTS.md` Pasal 2 dan Pasal 13):

| Metrik Evaluasi | Satuan | Ambang Batas Kelulusan (Acceptance Threshold) | Performa Baseline (`DummyRegressor`) | Performa Surrogate (`HistGradientBoostingRegressor`) |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | **MW** | $\text{MAE} < 1.0\text{ MW}$ | $> 6.50\text{ MW}$ | $\le 0.35\text{ MW}$ (Lulus $< 1.0\text{ MW}$) |
| **Root Mean Squared Error (RMSE)** | **MW** | $\text{RMSE} < 1.2\text{ MW}$ | $> 8.10\text{ MW}$ | $\le 0.48\text{ MW}$ |
| **Normalized / Relative MAE (NMAE)** | **%** | $\text{NMAE} < 1.0\%$ | $> 6.80\%$ | $\le 0.40\%$ (Lulus $< 1.0\%$) |
| **Coefficient of Determination ($R^2$)** | Dimensionless | $R^2_{\text{test}} \ge 0.60$ | $R^2 \le 0.00$ | $R^2 \ge 0.96$ (Lulus $\ge 0.60$) |
| **Compositional Closure Sum** | **mol%** | $\sum x_i = 100.0 \pm 10^{-4}\text{ mol\%}$ | $100.0\text{ mol\%}$ | $100.000000\text{ mol\%}$ |

---

## 6. Pertimbangan Keselamatan Proses & Tanggung Jawab Operator (Safety & Governance)

1. **Prioritas Interlock Keselamatan (Safety Interlocks Override):** Sistem proteksi mekanikal dan instrumen pengaman lapangan (`H4TI004B` TAL $-45.0^\circ\text{C}$, kontrol anti-surge `4UV-53`, kontrol reheat `4TV-510`, dan *Emergency Shutdown System*) selalu memiliki otoritas tertinggi di atas setiap keluaran model machine learning.
2. **Keputusan Akhir pada Operator & Process Engineer:** Setiap perubahan rasio *make-up* refrigeran ($N_2, C_1, C_2, C_3$) harus melalui prosedur standar operasi (SOP) kilang Badak LNG oleh operator yang berwenang.

