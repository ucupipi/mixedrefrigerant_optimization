# MASTER PROMPT — FORENSIC ML & THERMODYNAMIC AUDIT SUITE
## BADAK LNG PLANT-3 C3MR OPTIMIZATION (OILWEEK 2026)
### GOVERNANCE: /unlazy + /caveman + /ponytail + /unslop + /humanized-writing + /mlflow
### PACKAGES: NeqSim | Aspen HYSYS | CoolProp | IAPWS-IF97 | Scikit-Learn | LightGBM

Salin dan tempelkan prompt di bawah ini ke terminal `python chat_gateway.py` (Lead: DeepSeek V4.1 Flash, Architect: GPT-6 Sol).

---

```text
# MANDAT AUDIT FORENSIK MULTI-AGENT: BADAK LNG C3MR OPTIMIZATION SUITE
# PERAN: Lead Engineer (DeepSeek) & Principal Architect (GPT-6 Sol)

## I. PROTOKOL GAYA DAN DISIPLIN EKSEKUSI MUTLAK:
1. /caveman: Jawab langsung to-the-point. Format: `[objek] [tindakan] [alasan/bukti]. [langkah berikutnya].`
   - Hapus basa-basi (No "Halo", "Tentu", "Berikut adalah", "Semoga membantu").
   - Maksimal 20 kata per kalimat aktif. Pertahankan 100% payload teknis: angka desimal persis, tag DCS (`4UV-53`, `4TV-510`, `H4TI004B`, `H4TI016`), persamaan matematis, dan path file.
2. /unslop & /humanized-writing: Dilarang keras memakai jargon klise AI ("delve into", "tapestry", "pivotal", "spearhead", "testament to", "game changer", "turndown paradox", "thermal glove", "aerodynamic bypass"). Gunakan istilah rekayasa proses riil kilang Badak LNG.
3. /unlazy: Zero placeholders. Dilarang menulis `// TODO`, `# nanti dilengkapi`, fungsi kosong, atau potongan kode terpotong. Selesaikan kode 100% utuh dan uji dengan `run_command`.
4. /ponytail: Solusi terkecil yang menyelesaikan 100% masalah (minimal working diff). Wajib sertakan sitasi spesifik `file:baris` untuk setiap temuan audit.
5. /mlflow: Selidiki pencatatan parameter, metrik holdout (`r2_test`, `mae_test`, `nmae_relative_pct`), dan tracking artefak. Validasi bahwa data splitting 80:20 dilakukan SEBELUM fitting scaler.
6. Thermodynamic Tooling:
   - NeqSim: Verifikasi kesetimbangan VLE multikomponen N2-C1-C2-C3-C4, kurva envelope, dew point shell MCHE (-75.35°C), dan enthalpy departure PR-EOS.
   - Aspen HYSYS: Validasi flowsheet C3MR Train H, model MCHE 100-slice rigorous (MITA >= 1.50°C, tanpa temperature crossover ΔT <= 0), kurva kompresor sentrifugal 4K-1/2/3/4, batas surge floor >= 480 t/h, dan interlock TAL >= -45.0°C.
   - CoolProp: Helmholtz EOS untuk siklus chiller propana (3E-14/17/18).
   - Steam Tables (IAPWS-IF97): Laju uap turbin 4KT-1/2/3 (weighted 4.193 t/MWh).

---

## II. TARGET AUDIT FORENSIK 8 PILAR:

### PILAR 1: Audit Pipeline Data & Anti-Data Leakage
Gunakan `read_file` dan `search_code` untuk membaca:
- `data/MASTER_DATASET_REBUILD_20261014/scripts/04_clean_process_parameters.py`
- `data/MASTER_DATASET_REBUILD_20261014/scripts/08_enrich_physics_features.py`
- `data/MASTER_DATASET_REBUILD_20261014/scripts/09_baseline_envelope.py`
Cek dengan teliti:
a. Apakah scaler/imputer di-fit sebelum pemisahan train/test? (Data leakage = FATAL FAIL).
b. Apakah ada magic numbers pada kalkulasi enthalpy departure atau Gouy-Stodola exergy?
c. Apakah penanganan missing value merusak kontinuitas run operasional DCS?

### PILAR 2: Validasi 7 Surrogate Models & Monotonic Constraints
Baca `ikms_2026/clean_rebuild_v2/final_output/15_surrogate_models_evaluation.json`.
Konsultasikan ke GPT-6 Sol (`consult_gpt6_architect`):
a. Evaluasi arah `monotonic_cst` pada HistGradientBoostingRegressor:
   - Daya total C3MR vs mcr_flow (+1) & feed_flow (+1).
   - Suction drum temp vs feed_flow (-1), suct_p (+1).
   - MCHE MITA vs feed_flow (-1) & opt_mche_mcr (+1).
b. Mengapa fitur `tamb` menghasilkan korelasi NaN pada beberapa model? Periksa dampaknya pada inferensi.
c. Model MITA hanya memiliki N=300 sampel DoE. Buktikan secara statistik kecukupan sampel (sample sufficiency) berdasarkan hukum diminishing returns PR-EOS.
d. Periksa mengapa model propana precooling memiliki R²=0.7809. Identifikasi fitur laten yang hilang.

### PILAR 3: Integritas Komposisi Optimal MR (Aitchison Simplex & Mahalanobis)
Baca `ikms_2026/clean_rebuild_v2/final_output/18_optimal_mr_composition_recommendation.json` dan data GC `gc_composition/`.
Konsultasikan ke GPT-6 Sol:
a. Periksa transformasi Isometric Log-Ratio (ILR) pada ruang Simpleks S^4.
b. Validasi jarak Mahalanobis: D_M = 3.0762 <= 3.0802 (chi-square 95%, 4 DoF). Apakah resep optimal (N2: 3.669%, C1: 51.264%, C2: 42.618%, C2H4: 0.442%, C3: 2.006%) berada di dalam elipsoid operasional riil kilang Badak?
c. Hitung dew point NeqSim/PR-EOS pada tekanan suction 3.15 bar(a): apakah margin superheat 34.35°C di atas batas TAL -45.0°C terbukti aman dari liquid carryover?

### PILAR 4: Dekomposisi Daya & Batas Sistem (Battery Limits)
Konsultasikan ke GPT-6 Sol:
a. Urai secara transparan: Mengapa file JSON mencatat total penghematan 14.805 MW (MCR 13.251 MW + C3 1.554 MW), sedangkan paper OilWeek menyebut 28.98 MW (-27.10%) pada beban P90?
b. Buktikan apakah ini perbedaan basis (rata-rata tahunan vs titik P90 turndown), dan eliminasi semua potensi ambiguitas angka.
c. Validasi konversi penghematan uap (57.21 t/h) ke konsumsi gas bahan bakar boiler (4,407.54 Nm³/h) memakai rasio terverifikasi 97.70 Nm³/t steam.

### PILAR 5: Integritas Batas Keselamatan Anti-Surge & Suction TAL
Gunakan `search_code` untuk mencari: `4UV-53`, `4TV-510`, `kickback`, `TAL`, `480.0`.
Pastikan:
a. Flow floor kompresor C3 (4K-1/2/3) dan MCR (4K-4) terkunci mutlak >= 480.0 t/h.
b. Valve 4UV-53 (kickback) dan 4TV-510 (suction reheat) berstatus MURNI sebagai safety boundary enablers, bukan sebagai variabel keputusan optimasi utama.

### PILAR 6: Audit Kode Training & MLflow Reproducibility
Gunakan `search_code` untuk menemukan skrip fitting model surrogate (cari `HistGradientBoostingRegressor` atau `train_test_split`).
Baca kodenya dan periksa:
a. Parameter regresi dan metrik test set tersimpan secara reproducible (MLflow / JSON metadata).
b. Evaluasi daya dilaporkan proporsional dalam MW dengan Relative MAE < 1.0% dan R² >= 0.60.

### PILAR 7: Verifikasi Matematis Persamaan First-Principles
Konsultasikan ke GPT-6 Sol:
a. Evaluasi eksergi destruksi MCHE: Buktikan rumus Gouy-Stodola terdiskritisasi integral Riemann 100-slice:
   E_D,MCHE = T_0 * sum(ΔQ_i * (1/T_cold,mean,i - 1/T_hot,mean,i)). Haram single lumped temperature!
b. Evaluasi daya poros kompresor: Buktikan W_shaft = m_dot * Δh_s / eta_p. Dilarang pengali arbitrer.

### PILAR 8: Konsistensi Naskah Ilmiah & Laporan Eksekutif
Baca:
- `reports/EXECUTION_PLAN_AUDITED_20261015.md`
- `ikms_2026/IKMS2026_FullPaper_PNJ_Final.md`
- `ikms_2026/rebuild_v3_2_1_audit/tests/test_rebuild_v3_2_1.py`
Jalankan `test_rebuild_v3_2_1.py` via `run_command`.
Pastikan seluruh 10 Gate pengujian lulus (10/10 PASS) dan naskah bebas dari kontradiksi angka.

---

## III. FORMAT KELUARAN WAJIB (STRUCTURED & TO THE POINT):

Tulis laporan audit ke file `audit/ML_COMPREHENSIVE_AUDIT_REPORT.md` dengan format ringkas berikut:

# LAPORAN AUDIT FORENSIK ML & TERMODINAMIKA C3MR (IKMS/OILWEEK 2026)

## 1. RINGKASAN EKSEKUTIF KELAYAKAN (PASS / FAIL TABLE)
| No | Pilar Audit | Status | Temuan Kunci [File:Baris] | Dampak Fisik / ML | Tindakan Perbaikan |
|---|---|---|---|---|---|
| 1 | Data Pipeline & Leakage | PASS/FAIL | ... | ... | ... |
| 2 | Surrogate Monotonicity | PASS/FAIL | ... | ... | ... |
| 3 | Komposisi MR & Simplex | PASS/FAIL | ... | ... | ... |
| 4 | Dekomposisi Daya C3MR | PASS/FAIL | ... | ... | ... |
| 5 | Anti-Surge & TAL Safety | PASS/FAIL | ... | ... | ... |
| 6 | MLflow & Reproducibility| PASS/FAIL | ... | ... | ... |
| 7 | First-Principles Equations | PASS/FAIL | ... | ... | ... |
| 8 | Konsistensi Naskah Paper | PASS/FAIL | ... | ... | ... |

## 2. DETAIL TEMUAN DEFECT & KODE REKOMENDASI (/ponytail minimal diff)
Untuk setiap temuan berstatus WARNING atau FAIL:
- **Lokasi:** `path/to/file.py:baris`
- **Cacat Rekayasa:** Penjelasan ringkas cacat fisik/ML (maksimal 20 kata).
- **Kode Asli:** Snippet yang salah.
- **Kode Pengganti:** Minimal working diff yang benar dan lolos first-principles.

Mulai eksekusi sekarang. Baca file primer terlebih dahulu sebelum membuat kesimpulan.
```
