# DOKUMEN AUDIT AWAL REKAYASA (INITIAL AUDIT)
## Plant-3 Train H — C3MR Optimization & Make-Up Advisory Website
**Tanggal Audit:** 5 November 2026  
**Status:** Confidential / Engineering Review  
**Tim Auditor:** Senior Full-Stack Engineer, LNG Process Engineer, Machine-Learning Engineer, Operator-Interface Designer, Software Quality Engineer.  
**Kepatuhan Tata Kelola:** AGENTS.md (Hukum Disiplin Mutlak & Anti-Dosa Rekayasa Badak LNG) dan Master Prompt Rebuild v1.0.

---

## 1. Ringkasan Eksekutif & Karakteristik Aplikasi

Aplikasi **Plant-3 Train H — C3MR Optimization & Make-Up Advisory** adalah perangkat lunak pendukung keputusan operator (*operator advisory decision-support tool*) berbasis web untuk menganalisis dampak skenario perubahan kondisi gas umpan (*treated feed gas*) dan refrigerant campuran (*mixed refrigerant* / MCR) terhadap konsumsi daya poros kompresor Train H.

### Prinsip Operasional Mutlak:
1. **Advisory / What-If Analysis Only**: Sistem ini murni bersifat penasihat (*read-only advisory*). Tidak ada jalur penulisan (*zero write path*) ke Distributed Control System (Yokogawa Centum VP DCS), Programmable Logic Controller (PLC), Safety Instrumented System (Triconex SIS), interlock, maupun sistem kontrol plant lainnya.
2. **Pemisahan Ketat Dua Kolom (Dual-Column Strict Boundary)**:
   - **Kolom D ("Aktual DCS")**: Berisi pembacaan sensor proses terkini (feed flow, MCR flow) dan komposisi kromatografi gas (GC) laboratorium per shift. Nilai ini *read-only* terhadap skenario dan tidak pernah tertimpa.
   - **Kolom E ("Rekomendasi AI / Target Skenario")**: Berisi kandidat variabel keputusan yang dioptimasi oleh solver SLSQP live atau diubah oleh operator untuk analisis *what-if*.
3. **Pemberantasan Klaim Global "SEMUA AMAN"**: Dilarang menggunakan label "SEMUA AMAN", "ALL SAFE", atau "100% SAFE". Status diganti dengan verifikasi batas terbatas yang transparan.

---

## 2. Arsitektur Perangkat Lunak & Aliran Data

### 2.1. Komponen Arsitektur
- **Frontend**: React 18, TypeScript 5, Vite 8. Berjalan di `http://localhost:5173`. Menampilkan antarmuka spreadsheet 3-sheet (Sheet 1: Input & Hasil, Sheet 2: Grafik & Analisis, Sheet 3: Panduan Operator).
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2. Berjalan di `http://localhost:3001`. Bertanggung jawab atas inferensi model machine learning, optimasi live non-linear SLSQP, perhitungan neraca make-up, validasi fisika, dan evaluasi batas aman.
- **Model Machine Learning**:
  - `c3mr_power_surrogate_real.joblib`: Model `PhysicsResidualSurrogate` berbasis `HistGradientBoostingRegressor` dengan batasan monotonik fisika (`monotonic_cst`) memprediksi total daya poros Train H (MW).
  - `surrogate_total_steam_t_h.joblib`: Model surrogate GBRT konsumsi steam total penggerak turbin kompresor.
  - `surrogate_H4TI004B.joblib`: Model surrogate temperatur suction drum kompresor MCR 4C-8.
  - `mcr_ilr_envelope.joblib`: Pemodelan ruang komposisi Simpleks $\mathcal{S}^5$ menggunakan transformasi Isometric Log-Ratio (ILR) Aitchison dan kovariansi Mahalanobis ($D_M \le 3.0802$).
- **First-Principles Engine**: Peng-Robinson Equation of State (PR-EOS) iterative flash calculation untuk menghitung *dew point* campuran gas riil dan menjamin *suction superheat* $\ge 3.0^\circ\text{C}$.

### 2.2. Diagram Aliran Data (Data Flow Pipeline)
```
[DCS / GC Snapshot] ───► [Input Validation Layer] ───► [Unit Normalization & ILR Forward]
                                                                  │
                                 ┌────────────────────────────────┴────────────────────────────────┐
                                 ▼                                                                 ▼
                    [Live SLSQP Optimizer Engine]                                     [Surrogate ML Inference]
                    - Objective: Min Steam/Power                                      - Target State Power (MW)
                    - 5 Physical Constraints:                                         - Actual DCS State Power (MW)
                      1. T_suct >= -45.0 °C (TAL)                                     - Honest Delta Power (MW)
                      2. MCR Flow >= 480.0 t/h                                        - Regime & Confidence
                      3. D_M <= 3.0802 (Envelope)
                      4. Superheat >= 3.0 °C (PR-EOS)
                      5. Simplex Closure (C1 balance)
                                 │                                                                 │
                                 └────────────────────────────────┬────────────────────────────────┘
                                                                  ▼
                                                   [Make-Up Injection Calculation]
                                                   - Component delta (target - actual)
                                                   - Density & Inventory basis (24,000 kg)
                                                                  │
                                                                  ▼
                                                    [Constraint & Status Engine]
                                                    - Individual constraint margins
                                                    - Bounded verification status
                                                                  │
                                                                  ▼
                                                      [FastAPI JSON Response]
                                                                  │
                                                                  ▼
                                                  [React Frontend Spreadsheet UI]
                                                  - Sheet 1: Input & Hasil
                                                  - Sheet 2: Grafik & Analisis
                                                  - Sheet 3: Panduan Operator
```

---

## 3. Temuan Audit Kritis & Tindakan Perbaikan Rekayasa

### Temuan 1: Ambiguitas Rumus dan Label SEC (Specific Energy Consumption)
- **Kondisi Lama**:
  Website menampilkan kartu KPI "SEC (Konsumsi Energi Spesifik) = 321.8 kWh/t" dan baris C5 "SEC = 321.8 kWh/t". Nilai ini diperoleh dari:
  $$\text{Value} = \frac{79{,}090\text{ kW}}{245.8\text{ t/h}} = 321.76\text{ kWh/t}$$
  Di mana $245.8\text{ t/h}$ adalah laju alir gas umpan yang telah diolah (*treated feed gas flow*, `H1FI012`), BUKAN laju alir produksi LNG (*LNG rundown mass flow*, `H5FI006A`).
- **Analisis Rekayasa**:
  Menyebut nilai pembagian terhadap feed flow sebagai "SEC LNG" adalah cacat rekayasa fundamental karena rasio sirkulasi dan kehilangan gas bahan bakar (*fuel gas*) menyebabkan laju produksi LNG berbeda dengan laju feed gas (rasio tipikal $m_{\text{LNG}} \approx 0.91 \times m_{\text{feed}}$).
- **Tindakan Perbaikan Wajib**:
  1. Ubah label metrik pembagian terhadap feed gas menjadi:
     $$\mathbf{Specific\ Shaft\ Power\ per\ tonne\ of\ Treated\ Feed}\ (\text{kWh/t feed})$$
  2. Buat metrik terpisah untuk $\mathbf{SEC_{\text{LNG}}}\ (\text{kWh/t LNG})$:
     $$SEC_{\text{LNG}} = \frac{P_{\text{C3MR}}\ (\text{kW})}{\dot{m}_{\text{LNG}}\ (\text{t/h})}$$
  3. Apabila instrumen flow LNG rundown (`H5FI006A`) tidak tersedia dalam snapshot operasional, tampilkan secara jujur:
     $$SEC_{\text{LNG}} = \mathbf{N/A}\quad (\text{Data LNG rundown belum tersedia})$$
     Dilarang keras mengisi angka nol atau estimasi fiktif tanpa data primer.

### Temuan 2: Klaim Status Keselamatan Global "SEMUA AMAN" (ALL SAFE)
- **Kondisi Lama**:
  Di header spreadsheet dan KPI card terdapat badge hijau bertuliskan "SEMUA AMAN" ketika pemeriksaan kendala awal lolos.
- **Analisis Rekayasa**:
  Sebuah software penasihat berbasis AI tidak pernah memiliki otoritas untuk menyatakan plant LNG secara keseluruhan aman. Sistem hanya memeriksa sebagian kecil batas proses (suction temperature, anti-surge flow floor, simplex closure, dan Mahalanobis distance). Klaim "SEMUA AMAN" melanggar prinsip *human-factors* dan keselamatan proses karena dapat memicu rasa aman palsu (*complacency*) pada operator.
- **Tindakan Perbaikan Wajib**:
  1. Hapus total kata "SEMUA AMAN", "ALL SAFE", atau "100% SAFE".
  2. Ganti dengan status terbatas dan terperinci (*bounded verification status*):
     - **"Semua kendala yang diperiksa terpenuhi"** (*All evaluated constraints passed*)
     - **"Ada kendala yang perlu ditinjau (Peringatan Margin)"** (*Operating warning / tight margin*)
     - **"Skenario ditolak oleh sistem audit"** (*Scenario blocked*)
     - **"Belum dapat dievaluasi (Data instrumen belum lengkap)"** (*Not evaluated*)
     - **"Di luar domain operasional model"** (*Out of domain, $D_M > 3.0802$*)

### Temuan 3: Verifikasi Kompresor Anti-Surge vs Flow Floor Saja
- **Kondisi Lama**:
  Baris E2 menampilkan "Anti-Surge Flow Floor: 480.0 t/h" dengan status "AMAN".
- **Analisis Rekayasa**:
  Nilai $480.0\text{ t/h}$ adalah batas bawah aliran sirkulasi mekanikal (*mechanical safe operating flow floor*) kompresor sentrifugal MCR (4K-2/3) yang dijaga oleh modulasi kickback valve 4UV-53 (Manual Book Modul 3). Ini adalah batas envelope flow terendah, BUKAN evaluasi kurva dinamis kompresor (*dynamic compressor surge map* $\Delta p$ vs $Q_{\text{actual}}$).
- **Tindakan Perbaikan Wajib**:
  Beri keterangan transparan pada baris tersebut:
  *"Batas aliran sirkulasi minimum kompresor MCR (Safe Operating Flow Floor 4UV-53 = 480.0 t/h). Peta anti-surge dinamis kompresor: Belum dievaluasi (memerlukan kurva head/dp sentrifugal lengkap)."*

### Temuan 4: Rekonsiliasi Neraca Make-Up Hidrokarbon (Nm³/h vs kg/h)
- **Kondisi Lama**:
  Laju make-up N2, C1, C2, C3 ditampilkan dalam satuan Nm³/h dan kg/h.
- **Analisis Rekayasa**:
  Konversi volumetrik ke massa harus diverifikasi terhadap kondisi standar ($0^\circ\text{C}, 1.01325\text{ bar}$) di mana volume molar gas ideal $V_m = 22.414\text{ m}^3/\text{kmol}$.
  $$\rho_{\text{std}, i} = \frac{MW_i}{22.414\text{ Nm}^3/\text{kmol}}$$
  - $N_2$ ($MW=28.013$): $\rho = 1.2498\text{ kg/Nm}^3$
  - $C_1$ ($MW=16.043$): $\rho = 0.7158\text{ kg/Nm}^3$
  - $C_2$ ($MW=30.070$): $\rho = 1.3416\text{ kg/Nm}^3$
  - $C_3$ ($MW=44.097$): $\rho = 1.9674\text{ kg/Nm}^3$
  Total densitas campuran make-up bergeser tergantung komponen yang diinjeksikan. Basis perhitungan durasi transisi (2.0 jam) dan estimasi inventory loop MCR ($24{,}000\text{ kg}$) harus dijelaskan sebagai acuan operasional, bukan laju steady-state.

### Temuan 5: Batasan Komposisi MR & Closure 100.00%
- **Kondisi Lama**:
  Jumlah fraksi mol sempat menghasilkan $100.01\%$ karena pembulatan independen 5 float.
- **Analisis Rekayasa**:
  Dalam ruang Simpleks Aitchison $\mathcal{S}^5$, total fraksi mol wajib identik $100.00\%$.
- **Status Perbaikan**:
  Telah diperbaiki dengan penyerapan residu pembulatan ($\le \pm 0.02\%$) ke komponen mayoritas ($C_1$, ~46%). Ditambahkan tombol cepat `⚡ 100%` pada baris A8 jika operator menginput data GC manual yang belum dinormalisasi.

---

## 4. Matriks Portabilitas & Kebersihan Kode (Ponytail Principles)
1. **Zero Absolute Paths**: Seluruh referensi file menggunakan `pathlib.Path(__file__).resolve().parents[...]`. Tidak ada hardcoded path `C:\Users\...` di dalam kode produksi.
2. **Zero Magic Numbers**: Semua faktor konversi (0.8136, 0.760, 480.0 t/h, -45.0 °C, 3.0802) memiliki sitasi kode sumber dan dasar fisika di komentar/dokumentasi.
3. **Pemisahan Model & Presentasi**: Seluruh kalkulasi rekayasa dan optimasi SLSQP berjalan di Python backend domain layer. Frontend hanya bertugas me-render dan memvalidasi input UI.
4. **Keamanan Eksekusi**: Seluruh endpoint REST API memvalidasi tipe data menggunakan skema Pydantic v2 dengan batasan fisik yang ketat (`ge`, `le`).

---

## 5. Rencana Tindak Lanjut Audit (Action Plan)
- [x] Tahap 1: Pemetaan arsitektur dan penulisan `docs/INITIAL_AUDIT.md`.
- [ ] Tahap 2: Penyusunan `docs/CALCULATION_REGISTER.md` dan `docs/CONSTRAINT_REGISTER.md`.
- [ ] Tahap 3: Penyusunan `docs/DATA_DICTIONARY.md` dan `docs/MODEL_CARD.md`.
- [ ] Tahap 4: Pembaruan UI frontend (koreksi label SEC LNG vs Specific Shaft Power feed, penggantian badge "SEMUA AMAN", dan status evaluasi anti-surge).
- [ ] Tahap 5: Pembaruan panduan operator `docs/OPERATOR_GUIDE.md` pada Sheet 3.
- [ ] Tahap 6: Eksekusi rangkaian uji unit, uji regresi screenshot, dan verifikasi akhir.
