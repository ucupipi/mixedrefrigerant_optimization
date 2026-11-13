# MASTER HANDOVER & TECHNICAL EXECUTION PROMPT — REBUILD v3.3
## PT BADAK NGL — TRAIN H C3MR ENERGY EFFICIENCY RESEARCH (IKMS 2026)
### TRUE PHYSICAL RECONSTRUCTION, ML ASSET TAXONOMY, AND COMPLETE STATUS LEDGER

> **STATUS DOKUMEN:** DOKUMEN HANDOVER RESMI & INSTRUKSI KERJA LENGKAP UNTUK MODEL PENERUS.  
> **LOKASI WORKSPACE:** `d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK`  
> **TANGGAL PEMBARUAN:** 13 November 2026  
> **KONTEKS:** Sesi sebelumnya mencapai batas kuota token/antigravity. Dokumen ini merangkum seluruh fondasi kebenaran teknis, temuan forensik, taksonomi direktori Machine Learning, apa yang telah selesai 100%, dan rincian pekerjaan yang belum selesai untuk diselesaikan oleh model AI berikutnya tanpa kehilangan konteks sedikitpun.

---

# BAGIAN 0: DIRECTIVE MUTLAK & ATURAN DISIPLIN MODEL PENERUS

Bagi setiap model AI / Principal Process Engineer AI yang membaca dokumen ini:
1. **Patuhi `AGENTS.md` (Undang-Undang Disiplin Mutlak & Anti-Dosa Rekayasa):**
   - **Pasal 1:** Haram angka gaib & pengali arbitrer (*Zero Magic Numbers*). Dilarang menulis pengali tanpa rujukan fisika (`sf = 0.840`, `sf = 0.694`, `eff_factor`, `power * 0.982`).
   - **Pasal 2:** Haram pseudo-ML & regresi palsu (*Zero Fake Regression*).
   - **Pasal 3:** Haram memalsukan komposisi gas & analyzer (*Zero Invented Compositions*).
   - **Pasal 4:** Haram offset statis penipuan termal (*Zero Fake Delta Offsets*).
   - **Pasal 5:** Kepatuhan mutlak pada First-Principles Manual Book.
   - **Pasal 6:** Kepatuhan mutlak pada P&ID dan PFD kilang Badak LNG Train H.
   - **Pasal 8:** Haram jargon bombastis/hiperbolis AI (*Zero Pretentious AI Jargon*). Gunakan bahasa rekayasa proses yang presisi, lugas, dan terukur.
   - **Pasal 10:** Mandat dekomposisi transparan batas sistem kompresor (MCR direct vs C3 precooling).
   - **Pasal 12:** Dilarang membela data warisan yang cacat (*Zero Defending Unjustified Legacy Data*).
   - **Pasal 13:** Metrik model wajib menggunakan satuan proporsional (**MW**, bukan kW mentah) dan persentase relatif ($< 1.0\%$).
2. **Karakter Eksekusi:** Anda adalah *Independent Multidisciplinary Engineering Verification Team*, bukan asisten pembuat laporan naratif. Utamakan keabsahan matematis, keterlacakan data (*traceability*), dan kalkulasi numerik nyata.
3. **Hasil yang Sah:** Jika simulasi HYSYS tidak dapat dieksekusi secara otomatis, nyatakan secara jujur: `PHYSICAL OPTIMIZATION BLOCKED — REQUIRED SIMULATOR RUNTIME UNAVAILABLE`. Dilarang keras mengarang angka penghematan energi atau membuat dataset DoE tiruan dengan rumus aljabar.

---

# BAGIAN 1: RINGKASAN MISI & TUJUAN REBUILD v3.3

### 1.1 Tujuan Riset Pusat
> **"Menentukan apakah terdapat satu resep komposisi Mixed Refrigerant (MR) multikomponen (N2, C1, C2, C2H4, C3) yang achievable secara fisik dan satu jadwal sirkulasi MR kontinu bergantung-beban yang dapat menurunkan konsumsi energi Train H C3MR, dengan secara ketat mematuhi seluruh batasan termodinamika (MCHE MITA >= 1.50 °C), hidraulika, mekanikal (anti-surge >= 480 t/h), kendali, dan operasional aktual kilang."**

### 1.2 Kegagalan Fatal Rebuild Sebelumnya (v3, v3.1, v3.2, v3.2.1)
- **Rebuild v3:** Hanya menyelesaikan optimasi kuantil untuk Candidate A (titik batas $C_3 = 10.0\%$). Candidate A gagal audit karena risiko pelanggaran pinch $44.1\%$.
- **Rebuild v3.1 & v3.2:** Mengganti Candidate A dengan Candidate B dan Candidate R, tetapi **TIDAK PERNAH MENJALANKAN ULANG OPTIMASI**. Seluruh angka penghematan diturunkan dari perkalian skalar tetap ($sf = 0.840 \rightarrow 16.85\text{ GWh}$, $sf = 0.558 \rightarrow 11.20\text{ GWh}$, $sf = 0.694 \rightarrow 13.92\text{ GWh}$).
- **Surrogate Training DoE:** 2.500 titik DoE dalam `physical_doe_training_dataset.csv` dibuat dari rumus aljabar tertutup Python dengan noise Gaussian tiruan `np.random.normal(0, 0.02)`. Nol panggilan ke simulator termodinamika PR-EOS.
- **Sirkularitas Daya Baseline:** Kolom daya kompresor `total_compressor_power_steam_MW` dibentuk dari `total_driver_steam_t_h / 4.040`. Tidak ada pembacaan torquemeter poros independen di DCS.

---

# BAGIAN 2: 10 BLOKER FORENSIK YANG SUDAH TERSELESAIKAN (GROUND TRUTH)

Hasil audit forensik v3.2.1 telah membuktikan akar penyebab secara matematis (tersimpan di `ikms_2026/rebuild_v3_2_1_audit/13_blocker_resolution/TEN_FORENSIC_BLOCKERS_RESOLVED.md`):

| Blocker | Masalah Teknis | Akar Masalah & Bukti Forensik | Putusan Audit |
|:---:|:---|:---|:---:|
| **Q1** | Selisih Penghematan Candidate R (11.20 vs 13.92 GWh) | v3.2 `p5_joint_optimization.py:94` memakai `sf = 0.558` ($20.058 \times 0.558 = 11.20\text{ GWh}$). v3.2.1 `p6_joint_optimization_v3_2_1.py:101` mengubah manual `sf = 0.694` ($13.92\text{ GWh}$). Candidate R tidak pernah dioptimasi independen. | **ARBITRARY SCALING FACTOR MODIFICATION** |
| **Q2** | Candidate B Memiliki 3 Komposisi Berbeda | v3.1 ($D_M = 1.821$), v3.2 ($D_M = 1.820$), v3.2.1 ($D_M = 2.410$). Fraksi mol dibulatkan manual dengan tangan agar total 100%, bukan titik konvergensi solver. | **MANUAL HEURISTIC RECIPE DRIFT** |
| **Q3** | Penghematan B & R Berasal dari Scaling Candidate A | `p6_joint_optimization_v3_2_1.py:108-112` menerapkan tabel pengali tetap: Cand A (1.000), B (0.840), C (0.668), D (0.000), R (0.694). Penghematan tidak valid. | **NON-PHYSICAL LINEAR MULTIPLIER** |
| **Q4** | Kolom Daya Total = Steam / 4.040 | `01_build_reconciliation_dataset.py:30,114` mendefinisikan `shaft_mw = tot_steam / 4.04`. DCS tidak memiliki torquemeter poros. $\sigma_{\text{ratio}} = 0.0001$. | **CIRCULAR SYNTHETIC DERIVATIVE** |
| **Q5** | Selisih Uap Tahunan (3,172.83 vs 2,935.9 kt/th) | 2,935.9 kt = rata-rata 3 turbin ($374.02\text{ t/h} \times 7,849.6\text{ h}$). 3,172.83 kt = integrasi numerik penuh meteran header ($404.20\text{ t/h}$) mencakup kuantil P62–P100 yang missing di tag individual. | **DIFFERING DATA POPULATION BASES** |
| **Q6** | Kontradiksi Steam Rate (4.040 vs 4.193 t/MWh) | 4.040 t/MWh adalah pembagian sirkular ($2,935.9\text{ kt} / 726.7\text{ GWh}$). 4.193 t/MWh adalah rata-rata terbobot ekspansi IAPWS-IF97 mesin aktual (4KT-1: 4.262, 4KT-2: 4.184, 4KT-3: 4.109 t/MWh). | **CIRCULAR FACTOR VS IAPWS-IF97 EXPANSION** |
| **Q7** | Kekuatan Statistik Risiko MITA Candidate R (4.6%) | 4.57% murni kurva analitis Gaussian normal CDF. Pada $N=1.000$ draws Monte Carlo ($k=46$), exact Clopper-Pearson 95% CI adalah $[3.39\%, \mathbf{6.09\%}]$, menembus batas 5.0%. Butuh $N \ge 7.299$ draws untuk menolak $P \ge 5\%$. | **EMPIRICALLY UNDERPOWERED AT N=1000** |
| **Q8** | Asal Target 2.500 DoE (Simulator vs Rumus Aljabar) | `p4_surrogate_rebuild.py:103-146` menggunakan persamaan aljabar manual + noise Gaussian tiruan. Panggilan HYSYS/CoolProp = NOL. $R^2 > 0.98$ hanya mengevaluasi fit rumus sendiri. | **SYNTHETIC CLOSED-FORM ALGEBRAIC** |
| **Q9** | Jalur 4E-40, Kelayakan Makeup, dan Zero-CAPEX | Split cairan 4E-40 (13.5%) tidak bermeter di DCS (estimasi HYSYS). Makeup etana/propana via batch unmetered. Zero-CAPEX VALID untuk Candidate R (manual trim DCS); REFUTED untuk Candidate B (butuh APC USD 300k). | **ESTIMATED SPLIT; CONDITIONAL ZERO-CAPEX** |
| **Q10** | Batas Aliran Kompresor & Governor Turbin | Batas surge 480 t/h divalidasi dari kurva OEM Dresser-Rand 838B4 (margin 10% di atas surge 458-509 t/h). Posisi governor 94.5% adalah estimasi kapasitas, nol tag ZT di telemetri DCS. | **SURGE VALIDATED; GOVERNOR ESTIMATED** |

---

# BAGIAN 3: TAKSONOMI LENGKAP DIREKTORI, DATASET & MODEL ML

Berikut adalah peta struktur folder di `d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK`:

```
FINAL_FIX_OILWEEK/
├── AGENTS.md                                   # Undang-Undang Disiplin Mutlak & Anti-Dosa Rekayasa
├── MASTER_AUDIT_PROMPT.md                      # Audit prompt master sebelumnya
├── MASTER_HANDOVER_REBUILD_v3_3.md             # DOKUMEN INI (Master Handover)
├── hysys_models/                               # Model simulasi Aspen HYSYS
│   ├── C3MR.hsc                                # Flowsheet dasar C3MR Train H
│   ├── MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc # Model termutakhir + 4E-40 + 4UV-53 + 4TV-510
│   └── validation_cases/                       # 15 kasus validasi per kuantil (P10 to P90 Baseline & Opt)
│       ├── P10_Baseline.hsc, P10_Optimized.hsc
│       ├── P25_Baseline.hsc, P25_Optimized.hsc
│       ├── P40_Baseline.hsc, P40_Optimized.hsc
│       ├── P50_Baseline.hsc, P50_Optimized.hsc
│       ├── P60_Baseline.hsc, P60_Optimized.hsc
│       ├── P75_Baseline.hsc, P75_Optimized.hsc
│       ├── P90_Baseline.hsc, P90_Optimized.hsc
│       └── test_p10_enhanced.hsc
│
├── data/
│   └── MASTER_DATASET_REBUILD_20261014/
│       └── data/processed/
│           ├── master_minute_level.parquet     # 1.051.200 baris data DCS sensor per menit (2024-2026)
│           ├── master_shift_level.parquet      # Data rata-rata per shift
│           ├── composition_2023_2024_imputed.parquet # Komposisi GC laboratorium (2.531 sampel shift)
│           ├── process_parameters_unleaked.parquet   # Parameter proses terbebas data leakage
│           └── target_energy.parquet           # Target konsumsi energi historis
│
├── ikms_2026/                                  # Folder kerja utama publikasi IKMS 2026
│   ├── data/
│   │   ├── digitized/                          # Kurva kompresor OEM terdigitalisasi
│   │   │   ├── compressor_curves_4K1.csv       # Kurva C3 compressor (Head, Eff, Power vs Flow)
│   │   │   ├── compressor_curves_4K2.csv       # Kurva MCR LP compressor (1.617 baris kurva)
│   │   │   ├── compressor_curves_4K3.csv       # Kurva MCR HP compressor
│   │   │   └── COMPRESSOR_CURVES_DATA_DICTIONARY.md
│   │   ├── processed/
│   │   │   └── compressor_mapped_operating_points.csv # Titik operasi kompresor terpetakan
│   │   └── reconciliation/
│   │       ├── baseline_hysys_vs_dcs_validation_p1_p100.csv # 100 kuantil baseline operasi Train H
│   │       ├── dcs_to_hysys_dictionary.json    # Pemetaan tag DCS ke stream HYSYS
│   │       └── calibration_parameter_register.csv
│   │
│   ├── rebuild_v3/                             # [ARCHIVED/SUPERSEDED] Rebuild v3
│   ├── rebuild_v3_1_audit/                     # [ARCHIVED/SUPERSEDED] Audit forensik v3.1
│   ├── rebuild_v3_2/                           # [ARCHIVED/SUPERSEDED] Rebuild v3.2 (memuat surrogate lama)
│   │   └── 05_surrogate_rebuild/
│   │       ├── models/                         # Model LightGBM surrogate lama (DILATIH DARI RUMUS ALJABAR!)
│   │       │   ├── surrogate_power_total_shaft_MW.joblib
│   │       │   ├── surrogate_mita_approach_C.joblib
│   │       │   └── surrogate_exergy_loss_MCHE_MW.joblib
│   │       └── training/
│   │           └── physical_doe_training_dataset.csv # 2.500 sampel DoE sintetis (TERBUKTI FAKE)
│   │
│   ├── rebuild_v3_2_1_audit/                   # [COMPLETED & VERIFIED] Audit forensik v3.2.1
│   │   ├── 00_manifest/                        # sha256_before.csv (175 file), sha256_after.csv (74 file)
│   │   ├── 01_source_forensics/ to 10_field_testability/ # Register & laporan per fase P0-P9
│   │   ├── 11_manuscript_ledger/               # claim_evidence_ledger_final.csv & .md
│   │   ├── 12_independent_verification/        # independent_checks.csv (39 checks independen)
│   │   ├── 13_blocker_resolution/              # forensic_blocker_resolution.json & TEN_FORENSIC_BLOCKERS_RESOLVED.md
│   │   ├── scripts/                            # Skrip audit p0 s.d. p9, v1, v2, run_all_v3_2_1.py
│   │   └── tests/test_rebuild_v3_2_1.py        # 12 regression tests (100% PASSED)
│   │
│   └── rebuild_v3_3/                           # [DIREKTORI AKTIF SAAT INI — DALAM PENGERJAAN]
│       ├── 00_manifest/                        # sha256_source_baseline.csv (354 file ter-hash)
│       ├── 01_legacy_retirement/               # Canonical candidate registry & retirement ledger
│       ├── 02_energy_baseline/                 # Pemisahan uap header vs turbin, daya model-derived
│       ├── 03_simulator_audit/                 # Audit 38+ kasus .hsc, status COM automation
│       ├── 04_mche_4e40/                       # [PENDING] Analisis hidraulika 4E-40 & 100-slice MCHE
│       ├── 05_compressor_turbine/              # Analisis surge speed-dependent & governor stroke
│       ├── 06_composition_control/             # [PENDING] Neraca massa batch makeup & inventori
│       ├── 07_physical_doe/                    # [PENDING] DoE fisik murni (HYSYS / CoolProp PR-EOS)
│       ├── 08_joint_optimization/              # [PENDING] Optimasi simultan resep + schedule
│       ├── 09_robustness/                      # [PENDING] UQ Monte Carlo N >= 10.000 draws
│       ├── 10_acceptance/                      # [PENDING] Ledger penerimaan & laporan akhir v3.3
│       ├── scripts/                            # Skrip eksekusi p1 s.d. p10
│       └── tests/                              # Rangkaian pengujian unit & regresi v3.3
```

---

# BAGIAN 4: STATUS PROGRESS REBUILD v3.3 (APA YANG SUDAH & BELUM SELESAI)

### 4.1 Prioritas yang SUDAH SELESAI di Rebuild v3.3
1. **Inisialisasi Direktori & Manifest Kriptografis (`00_manifest/`):**
   - Direktori `ikms_2026/rebuild_v3_3/` dan 11 subfolder telah dibuat.
   - `sha256_source_baseline.csv` berhasil membuat sidik jari SHA-256 untuk **354 file sumber** tanpa ada file lama yang dimodifikasi.
2. **Prioritas 1 — Pensiunkan Klaim Optimasi Lama (`01_legacy_retirement/`):**
   - Skrip: `ikms_2026/rebuild_v3_3/scripts/p1_legacy_retirement.py` telah dibuat dan dijalankan.
   - Hasil:
     - `canonical_candidate_registry.csv`: Setiap resep memiliki ID permanen tak-berubah:
       - `CID-A-v3`: Candidate A ($N_2=3.77, C_1=42.22, C_2=43.67, C_2H_4=1.53, C_3=8.82$, $D_M=2.98$, saving $20.06\text{ GWh}$) $\rightarrow$ **REJECTED (44.1% MITA Risk)**.
       - `CID-B-v3.1`: Candidate B v3.1 ($N_2=3.65, C_1=42.10, C_2=46.85, C_2H_4=0.25, C_3=7.15$, $D_M=1.821$, saving $16.85\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.840)**.
       - `CID-B-v3.2`: Candidate B v3.2 ($N_2=4.15, C_1=42.10, C_2=46.20, C_2H_4=0.40, C_3=7.15$, $D_M=1.820$, saving $16.85\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.840)**.
       - `CID-B-v3.2.1`: Candidate B v3.2.1 ($N_2=4.10, C_1=41.20, C_2=47.30, C_2H_4=0.25, C_3=7.15$, $D_M=2.410$, saving $16.85\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.840)**.
       - `CID-C-v3`: Candidate C (Komposisi tidak tercatat, saving $13.40\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.668)**.
       - `CID-D-v3`: Baseline ($0.00\text{ GWh}$) $\rightarrow$ **SUPERSEDED**.
       - `CID-R-v3.2`: Candidate R v3.2 ($N_2=3.77, C_1=42.22, C_2=46.80, C_2H_4=1.36, C_3=5.85$, $D_M=1.89$, saving $11.20\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.558)**.
       - `CID-R-v3.2.1`: Candidate R v3.2.1 (Komposisi sama, saving $13.92\text{ GWh}$) $\rightarrow$ **UNSUPPORTED (Scaled sf=0.694)**.
     - `legacy_claims_retirement.csv`: Seluruh penghematan berskala, interaksi $1.77\text{ GWh}$, dan surrogate $R^2 > 0.98$ resmi dipensiunkan dengan label `UNSUPPORTED`.
     - `interaction_term_retirement.json`: Istilah sinergi $1.77\text{ GWh}$ dipensiunkan sebagai konstanta hardcoded.
3. **Prioritas 2 — Rekonstruksi Baseline Energi Sejati (`02_energy_baseline/`):**
   - Skrip: `ikms_2026/rebuild_v3_3/scripts/p2_energy_baseline.py` telah dibuat dan dijalankan.
   - Hasil:
     - `steam_budget_decomposition.csv`: Pemisahan uap header ($404.20\text{ t/h}$ mean) vs uap individual turbin ($373.75\text{ t/h}$ mean) vs residual balancing/bypass.
     - `turbine_thermodynamic_scenarios.csv`: Skenario ekspansi IAPWS-IF97 per mesin:
       - 4KT-1 (C3): $\eta_s = 75.2\%, \eta_m = 98.5\% \implies SR = 4.262\text{ t/MWh}$ (Kondisi inlet: 60 barg, 440 °C).
       - 4KT-2 (MCR LP): $\eta_s = 76.6\%, \eta_m = 98.5\% \implies SR = 4.184\text{ t/MWh}$.
       - 4KT-3 (MCR HP): $\eta_s = 78.0\%, \eta_m = 98.5\% \implies SR = 4.109\text{ t/MWh}$.
       - Rata-rata terbobot daya: $\overline{SR}_{\text{wtd}} = 4.194\text{ t/MWh}$.
     - `model_derived_shaft_power.csv`: Daya poros kompresor direkonstruksi dari kurva OEM digital (`compressor_mapped_operating_points.csv`) per kuantil dan diklasifikasikan sebagai `MODEL-DERIVED (OEM CURVE INTERPOLATION)`, BUKAN pembagian steam/4.040.
     - `annual_steam_reconciliation.json`: Resolusi selisih uap tahunan:
       - Header terintegrasi penuh: **$3,172.83\text{ kt/tahun}$** (Primary physical boundary).
       - Prediksi jumlah 3 turbin: **$2,935.90\text{ kt/tahun}$** (Model-derived 3-turbine sum).
       - Selisih: $+236.93\text{ kt/tahun}$ ($+8.07\%$).
4. **Prioritas 3 — Audit Simulator Fisik (`03_simulator_audit/`):**
   - Skrip: `ikms_2026/rebuild_v3_3/scripts/p3_simulator_audit.py` telah dibuat dan dijalankan.
   - Hasil:
     - `hysys_case_inventory.csv`: Berhasil menginventarisasi dan mem-fingerprint **38 file kasus `.hsc`** di workspace.
     - `simulator_audit_report.json`:
       - Model utama: `C3MR.hsc` dan `MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc`.
       - Property package: Peng-Robinson EOS (PR-EOS).
       - Evaluasi antarmuka COM: Pengecekan `win32com.client.Dispatch("HYSYS.Application")`. Jika Aspen HYSYS terinstal dan memiliki lisensi aktif di Windows host, COM automation dapat berjalan. Jika tidak, dilaporkan secara transparan.
5. **Prioritas 5 — Rekonstruksi Batas Kompresor & Turbin (`05_compressor_turbine/`):**
   - Skrip: `ikms_2026/rebuild_v3_3/scripts/p5_compressor_turbine.py` telah dibuat dan dijalankan.
   - Hasil:
     - `speed_dependent_surge_analysis.csv`: Rekonstruksi garis batas surge bergantung kecepatan putaran kompresor dari kurva OEM Dresser-Rand 838B4 (interpolasi speed-dependent surge line + margin 10%). Menghitung kebutuhan recycle kickback `4UV-53` pada setiap kuantil.
     - `governor_valve_assessment.json`: Menghapus klaim pembacaan bukaan valve 94.5% dari DCS. Diklasifikasikan sebagai `THEORETICAL CAPACITY ESTIMATE (NOT DCS MEASUREMENT)` karena tidak ada sensor posisi valve di DCS.
     - `flow_decomposition.csv`: Dekomposisi aliran hisap proses, aliran recycle kickback, dan total aliran kompresor.
6. **Investigasi 4 Cacat Fatal & Rekonstruksi Model Fisik Baseline (`02_energy_baseline/`):**
   - Skrip: `ikms_2026/rebuild_v3_3/scripts/p0_investigate_four_defects.py` dan `p4_independent_baseline_model.py`.
   - Laporan Deliverable: `ikms_2026/rebuild_v3_3/02_energy_baseline/BASELINE_RECONSTRUCTION_REPORT.md`.
   - Hasil:
     - `four_critical_defects_investigation.json`: Pembuktian komputasional 4 cacat fatal (MITA buta komposisi, statis 7.169 °C, sirkularitas 4.040, dan pelanggaran batas operasi).
     - `independent_physical_baseline_quantiles.csv`: Simulasi NeqSim PR-EOS 100-slice MCHE dan kurva daya OEM kompresor (80.79 s.d. 101.32 MW, MCR 69.6%, C3 30.4%, error uap 4.05%).
     - `tests/test_baseline_reconstruction.py`: 6/6 uji regresi pembatalan pendekatan cacat lama LULUS (100% all green).

---

### 4.2 Prioritas yang BELUM SELESAI (Pekerjaan Rumah Model Penerus)

Model AI berikutnya **WAJIB MENYELESAIKAN PRIORITAS BERIKUT** di `ikms_2026/rebuild_v3_3/`:

```
[ ] PRIORITAS 4: Reconstruct 4E-40 and MCHE Distribution (p4_mche_4e40.py)
[ ] PRIORITAS 6: Prove Actual Composition Control Feasibility (p6_composition_control.py)
[ ] PRIORITAS 7: Generate Real Physical DoE or Reduced-Fidelity CoolProp PR-EOS (p7_physical_doe.py)
[ ] PRIORITAS 8: True Joint Optimization (p8_true_joint_optimization.py)
[ ] PRIORITAS 9: Full Robustness & Decision Engine (p9_robustness_decision.py)
[ ] PRIORITAS 10: Final Acceptance Ledger & Executive Summary (p10_acceptance_and_ledger.py)
[ ] MASTER RUNNER: Buat scripts/run_all_v3_3.py
```

---

# BAGIAN 5: PANDUAN TEKNIS RINCI UNTUK 5 PRIORITAS YANG BELUM SELESAI

Berikut adalah instruksi implementasi presisi tinggi untuk masing-masing skrip yang harus Anda bangun:

### 5.1 PRIORITAS 4 — `p4_mche_4e40.py` (Analisis Hidraulika 4E-40 & Profil MCHE)
1. **Tujuan:** Memvalidasi split fraksi cairan 13.5% pada penukar panas 4E-40 dan menghitung profil suhu komposit 100-slice MCHE tanpa angka asumsi gaib.
2. **Formulasi Matematis & Rekonstruksi Hidraulika:**
   - 4E-40 adalah heavy MCR subcooler yang disuplai dari cairan bawah separator 5C-1 melalui valve pengatur `5FIC-2`.
   - Di DCS tidak ada sensor aliran massa pada cabang 4E-40.
   - Rekonstruksi aliran cairan cabang:
     $$\dot{m}_{\text{4E-40}} = C_v \sqrt{\frac{\Delta P_{\text{valve}}}{\text{SG}}} \quad \text{atau estimasi hidraulika cabang paralel}$$
   - Hitung beban termal penukar panas 4E-40:
     $$\dot{Q}_{\text{4E-40}} = \dot{m}_{\text{liquid}} \cdot (h_{\text{in}} - h_{\text{out}})$$
     di mana entalpi $h$ dihitung menggunakan CoolProp PR-EOS atau HYSYS steady-state.
   - Profil 100-slice MCHE:
     Hitung kurva komposit fluida panas (gas alam umpan + sirkulasi MCR bertekanan tinggi) versus fluida dingin (MCR berekspansi di shell side).
     $$\Delta T_i = T_{\text{hot}, i} - T_{\text{cold}, i}, \quad i = 1, \dots, 100$$
     $$\text{MITA} = \min_{i} (\Delta T_i)$$
   - Evaluasi probabilitas pelanggaran batas aman $\text{MITA} < 1.50^\circ\text{C}$ pada baseline aktual Train H di seluruh kuantil.
3. **Output File:**
   - `ikms_2026/rebuild_v3_3/04_mche_4e40/hydraulic_4e40_reconstruction.csv`
   - `ikms_2026/rebuild_v3_3/04_mche_4e40/mche_100_slice_profiles.csv`
   - `ikms_2026/rebuild_v3_3/04_mche_4e40/mche_baseline_mita_evaluation.json`

---

### 5.2 PRIORITAS 6 — `p6_composition_control.py` (Kelayakan Kontrol Komposisi & Inventori Batch)
1. **Tujuan:** Membuktikan apakah pergeseran komposisi MR dari baseline ke kandidat baru dapat dicapai menggunakan fasilitas kilang yang ada (*plant makeup and inventory system*).
2. **Kondisi Lapangan Aktual Kilang Badak:**
   - **Sumber Etana ($C_2$):** Overhead kolom De-Ethanizer (3C-5) via pipa manual block valve (tanpa flow transmitter kontinu).
   - **Sumber Propana ($C_3$):** Overhead akumulator De-Propanizer (3C-6) via pipa charging batch manual.
   - **Sumber Nitrogen ($N_2$):** Header N2 bertekanan tinggi dari Unit Utilitas.
   - **Sumber Metana ($C_1$):** Gas umpan kering dari Scrub Column overhead.
   - **Laboratorium GC:** Analisis kromatografi gas rutin shift (3x per hari, data `OverallComposition_2023_2024.xlsx`).
3. **Formulasi Neraca Massa Batch Makeup:**
   - Total inventori MCR dalam sirkuit tertutup ($M_{\text{inv}} \approx 45.000\text{--}60.000\text{ kg}$).
   - Kebutuhan injeksi komponen $k$ untuk mengubah fraksi mol dari $x_{\text{base}, k}$ ke $x_{\text{target}, k}$:
     $$\Delta m_k = M_{\text{inv}} \cdot \frac{MW_k}{\overline{MW}} \cdot (x_{\text{target}, k} - x_{\text{base}, k})$$
   - Sertakan ketidakpastian pengukuran GC ($\pm 0.15\text{ mol\%}$) dan kemurnian komponen injeksi (Etana 3C-5: $\approx 92\% C_2, 5\% C_1, 3\% C_3$).
   - Evaluasi waktu stabilisasi sirkuit ($t_{\text{mix}} \approx 2\text{--}4\text{ jam}$ per siklus pergantian).
4. **Analisis CAPEX:**
   - **Candidate R:** Memiliki nominal MITA $2.550^\circ\text{C}$ (margin $+1.050^\circ\text{C}$). Dapat dioperasikan dengan manual setpoint trim pada DCS Yokogawa Centum yang ada. Biaya modal = **USD 0 (ZERO-CAPEX VALID)**.
   - **Candidate B:** Memiliki nominal MITA $1.845^\circ\text{C}$ (margin sempit $+0.345^\circ\text{C}$). Wajib memasang multivariable Model Predictive Control (APC) dan sensor gas chromatograph online berkecepatan tinggi. Biaya modal = **USD 250.000 – 400.000 (ZERO-CAPEX REFUTED)**.
5. **Output File:**
   - `ikms_2026/rebuild_v3_3/06_composition_control/makeup_mass_balance.csv`
   - `ikms_2026/rebuild_v3_3/06_composition_control/inventory_uncertainty_analysis.json`
   - `ikms_2026/rebuild_v3_3/06_composition_control/capex_and_control_tradeoff.md`

---

### 5.3 PRIORITAS 7 — `p7_physical_doe.py` (DoE Fisik Murni & Validasi Tanpa Data Palsu)
1. **Tujuan:** Menghasilkan dataset DoE termodinamika murni dan melatih model surrogate yang bebas dari rumus aljabar sintetis.
2. **Protokol Eksekusi:**
   - **Jalur A (Jika Aspen HYSYS COM tersedia):** Jalankan otomasi COM membaca `MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc`, variasikan komposisi MR ($N_2: 2-6\%, C_1: 40-48\%, C_2: 40-50\%, C_3: 4-10\%$) dan laju sirkulasi ($450-700\text{ t/h}$), catat konvergensi solver, daya kompresor 4K-1/2/3, MITA 5E-1, dan eksergi destruksi.
   - **Jalur B (Jika Aspen HYSYS COM TIDAK tersedia di environment eksekusi):**
     - **DILARANG MENGARANG ANGKA HYSYS!**
     - Gunakan pustaka termodinamika `CoolProp` dengan Peng-Robinson EOS (`PR::Methane&Ethane&Propane&Nitrogen`) untuk menghitung kesetimbangan fasa VLE, entalpi hisap/tekan kompresor, dan kurva pendinginan MCHE secara tertutup dan presisi tinggi.
     - Simpan setiap titik DoE dengan metadata transparan:
       `simulator_engine: "CoolProp PR-EOS (Reduced-Fidelity Rigorous Thermodynamic Flash)"`
       `convergence: True/False`
       `material_balance_error_kg_s: 0.0`
       `energy_balance_error_kW: <calc>`
     - **Dilarang menambahkan noise Gaussian buatan (`np.random.normal`)!**
3. **Pelatihan Surrogate Model:**
   - Pisahkan data 80:20 train/test split sebelum scaling.
   - Terapkan batasan monotonik (`monotonic_cst`): daya kompresor naik monoton terhadap laju alir, daya naik monoton terhadap rasio kompresi.
   - Laporkan metrik pada test set independen: $R^2$, MAE (dalam **MW** untuk daya), NMAE ($< 1.0\%$).
4. **Output File:**
   - `ikms_2026/rebuild_v3_3/07_physical_doe/genuine_thermodynamic_doe.csv`
   - `ikms_2026/rebuild_v3_3/07_physical_doe/surrogate_model_qualification.csv`
   - `ikms_2026/rebuild_v3_3/07_physical_doe/surrogate_monotonicity_audit.csv`

---

### 5.4 PRIORITAS 8 — `p8_true_joint_optimization.py` (Optimasi Simultan Sejati)
1. **Tujuan:** Menemukan satu resep komposisi global ($\mathbf{z}_{\text{MR}}^*$) dan jadwal laju sirkulasi kontinu ($\dot{m}_{\text{MR}}^*(q)$) secara simultan tanpa pengali skalar.
2. **Formulasi Masalah Optimasi Matematis:**
   $$\min_{\mathbf{z}_{\text{MR}}, \, \dot{m}_{\text{MR}}(q)} \sum_{q=1}^{100} H(q) \cdot \left[ \dot{W}_{\text{shaft, total}}(\mathbf{z}_{\text{MR}}, \dot{m}_{\text{MR}}(q), q) \right]$$
   dengan batasan:
   - Kesetimbangan mol: $\sum_{k=1}^5 z_k = 1.0, \quad z_k \ge 0$
   - Elipsoid operasional kilang Badak: Jarak Mahalanobis $D_M(\mathbf{z}) \le 3.0802$ ($\chi^2_{0.95, 6}$)
   - Batas minimum pendekatan suhu MCHE: $\text{MITA}(\mathbf{z}_{\text{MR}}, \dot{m}_{\text{MR}}(q)) \ge 1.50^\circ\text{C}$ (tanpa crossover $\Delta T \le 0$)
   - Batas aman anti-surge kompresor: $\dot{m}_{\text{total suct}}(q) \ge \dot{m}_{\text{surge, floor}}(\text{speed})$
   - Batas suhu dingin suction drum: $T_{\text{suct}}(q) \ge -45.0^\circ\text{C}$ (Interlock TAL)
   - Batas daya turbin uap: $\dot{W}_i \le \dot{W}_{\text{rated}, i}$
3. **Evaluasi 4 Kebijakan Operasi (Four-Policy Comparison):**
   - **Kebijakan 1 (F0C0 — Baseline Aktual):** Komposisi historis, laju alir historis.
   - **Kebijakan 2 (F1C0 — Flow Optimization Only):** Komposisi tetap baseline, optimasi laju sirkulasi MCR per kuantil.
   - **Kebijakan 3 (F0C1 — Composition Optimization Only):** Satu resep komposisi optimal, laju alir tetap historis.
   - **Kebijakan 4 (F1C1 — True Joint Optimization):** Satu resep komposisi optimal + jadwal sirkulasi optimal.
   - Hitung kontribusi sinergi interaksi fisik murni:
     $$\Delta E_{\text{interaction}} = \Delta E_{\text{joint}} - (\Delta E_{\text{flow-only}} + \Delta E_{\text{comp-only}})$$
     (Buktikan apakah angka $1.77\text{ GWh/th}$ yang lama itu riil atau gugur).
4. **Output File:**
   - `ikms_2026/rebuild_v3_3/08_joint_optimization/four_policy_energy_comparison.csv`
   - `ikms_2026/rebuild_v3_3/08_joint_optimization/true_optimal_schedule_p1_p100.csv`
   - `ikms_2026/rebuild_v3_3/08_joint_optimization/synergy_term_evaluation.json`

---

### 5.5 PRIORITAS 9 & 10 — `p9_robustness_decision.py` & `p10_acceptance_and_ledger.py`
1. **Prioritas 9 (Kualifikasi Robustness & Keputusan):**
   - Jalankan simulasi Monte Carlo dengan **$N = 10.000$ draws** untuk menguji ketahanan terhadap ketidakpastian sensor ($u_c = 0.622^\circ\text{C}$).
   - Hitung probabilitas kepatuhan bersama (*Joint Feasibility Probability*):
     $$P_{\text{joint}} = P(\text{MITA} \ge 1.50 \cap \text{Surge Safe} \cap T_{\text{suct}} \ge -45.0 \cap D_M \le 3.08)$$
   - Tentukan status kualifikasi final setiap kandidat:
     - `ROBUSTLY QUALIFIED`: Jika $P_{\text{joint}} \ge 95.0\%$ dan Zero-CAPEX terbukti.
     - `CONDITIONAL QUALIFIED`: Jika butuh kontrol aktif atau batch makeup khusus.
     - `REJECTED`: Jika risiko pinch $> 5.0\%$ atau melanggar batasan mekanikal.
2. **Prioritas 10 (Ledger Penerimaan & Rekonsiliasi Emisi/Ekonomi):**
   - Konversi penghematan energi ke uap menggunakan steam rate terbobot IAPWS-IF97 ($4.194\text{ t/MWh}$, bukan 4.040).
   - Konversi uap ke gas bahan bakar boiler ($\dot{V}_{\text{FG}}$) dengan faktor ganda:
     - Standar ASME PTC 4 / Ramadan (2025): $97.70\text{ Nm}^3/\text{ton uap}$
     - Telemetri lapangan aktual Train H: $79.76\text{ Nm}^3/\text{ton uap}$
   - Emisi $\text{CO}_2$: Gunakan faktor emisi LHV gas alam Badak yang konsisten ($56.1\text{ kg CO}_2/\text{GJ}$).
   - Buat `claim_evidence_ledger_v3_3.csv` dan `ENGINEERING_ACCEPTANCE_MATRIX_v3_3.md`.
3. **Regression Test Suite:**
   - Buat `ikms_2026/rebuild_v3_3/tests/test_rebuild_v3_3.py` (minimal 12 test assertions mencakup seluruh prioritas 1 s.d. 10).
   - Buat master runner `ikms_2026/rebuild_v3_3/scripts/run_all_v3_3.py`.

---

# BAGIAN 6: INSTRUKSI LANGSUNG UNTUK MODEL PENERUS (COPY-PASTE PROMPT)

Apabila Anda adalah model AI baru yang melanjutkan sesi ini, bacalah dokumen ini dan segera jalankan langkah berikut:

```markdown
Saya telah membaca dan memahami MASTER_HANDOVER_REBUILD_v3_3.md secara menyeluruh.
Saya mengonfirmasi bahwa:
1. Rebuild v3.2.1 telah mengaudit 10 blocker forensik hingga tuntas (12/12 uji lulus).
2. Di Rebuild v3.3, Prioritas 1 (p1_legacy_retirement.py), Prioritas 2 (p2_energy_baseline.py), Prioritas 3 (p3_simulator_audit.py), dan Prioritas 5 (p5_compressor_turbine.py) telah dibangun.
3. Tugas saya adalah menyelesaikan Prioritas 4, 6, 7, 8, 9, 10, membuat test suite tests/test_rebuild_v3_3.py, dan menjalankan master runner run_all_v3_3.py.
4. Saya tidak akan menggunakan angka gaib, scaling faktor dari Candidate A, atau DoE aljabar palsu.
```

Execute Rebuild v3.3 according to the master prompt.

Your first and only immediate objective is to establish a valid independent baseline physical model.

Do not start new joint optimization.

First investigate the four critical defects identified in the latest audit:

1. MITA model missing material composition inputs and relying heavily on non-controlled ambient temperature.
2. MITA output fixed at 7.169 °C across 100 load points.
3. Steam and power circularity caused by the fixed 4.04 conversion.
4. Optimized candidates violating or approaching their own operating envelopes.

Also inspect the conflicting machine power decomposition, superheat definitions, C3 historical envelope, and Mahalanobis boundary.

For each finding:
- Open the actual source code.
- Inspect the original data.
- Reproduce the previous output.
- Calculate the result independently.
- Identify the exact root cause.
- Correct the underlying methodology.
- Add a test that rejects the old invalid approach.
- Record the final evidence and remaining uncertainty.

Preserve every previous result. Do not overwrite the historical files.

Do not create placeholder datasets or synthetic physical targets.

If an actual HYSYS case cannot be executed, report the exact limitation rather than manufacturing a substitute.

Do not declare the baseline PASS until it independently reproduces the actual operating conditions using a physical model.

The first deliverable is a baseline reconstruction report, not an optimization result.
---
*Dokumen ini disusun secara otomatis oleh AI Forensic Verification Team sebagai jaminan kontinuitas ilmiah tanpa kompromi.*

