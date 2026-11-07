# Definisi Variabel Target, Satuan Rekayasa, dan Batas Sistem (Target Definition)

Dokumen ini menetapkan definisi matematis, satuan rekayasa proporsional, batas sistem (*battery limit*), pemisahan sumber data DCS terhadap simulasi termodinamika, serta horizon prediksi untuk seluruh target pemodelan pada `MCR_ML_REBUILD`.

---

## 1. Batas Sistem (Battery Limit) & Dekomposisi Daya C3MR

Sesuai aturan tata kelola rekayasa proses (`AGENTS.md` Pasal 10), variabel target daya kompresi mencakup **Total Train C3MR Shaft Power** pada Badak LNG Plant-3 Train H. Sistem ini mengkopel secara termal siklus *Propane Precooling* (`4K-1` / penggerak turbin uap `4KT-1`) dan siklus *Mixed Component Refrigerant* (`4K-2` LP / `4KT-2` serta `4K-3` HP / `4KT-3`) melalui rangkaian chiller propana (`3E-14`, `3E-17`, `3E-18`) dan *Main Cryogenic Heat Exchanger* (`4E-1`).

Dekomposisi daya poros total dinyatakan secara eksplisit dalam satuan **Megawatt (MW)**:

$$W_{\text{total, C3MR}} \text{ (MW)} = W_{\text{MCR, direct}} \text{ (MW)} + W_{\text{C3, precooling}} \text{ (MW)}$$

di mana:
- **$W_{\text{MCR, direct}}$ (`mcr_shaft_power_mw`):** Daya poros langsung kompresor sentrifugal MCR tingkat pertama (`4K-2` / `4KT-2`) dan tingkat kedua (`4K-3` / `4KT-3`), dengan rentang operasi fisik $[25.0, 95.0]\text{ MW}$ (nominal P90 sekitar $68.2\text{ MW}$).
- **$W_{\text{C3, precooling}}$ (`c3_shaft_power_mw`):** Daya poros kompresor propana (`4K-1` / `4KT-1`) yang menyerap beban kondensasi awal MCR dan pendinginan umpan gas alam, dengan rentang operasi fisik $[15.0, 60.0]\text{ MW}$ (nominal P90 sekitar $39.8\text{ MW}$).
- **$W_{\text{total, C3MR}}$ (`total_shaft_power_mw`):** Total daya poros gabungan Train C3MR dengan rentang operasi fisik **$[40.0, 150.0]\text{ MW}$** (nominal P90 sekitar $108.0\text{ MW}$ atau $108{,}000\text{ kW}$, dan kondisi turndown teroptimasi sekitar $79.0\text{ MW}$).

---

## 2. Formulasi Matematis Target Daya Poros & Eksergi

### 2.1 Daya Poros Kompresor Sentrifugal ($W_{\text{shaft}}$)
Untuk setiap tingkat kompresi $k \in \{\text{4K-1}, \text{4K-2}, \text{4K-3}\}$, daya poros dihitung dari laju alir massa refrigeran $\dot{m}_k$, kenaikan entalpi isentropik $\Delta h_{s,k}$ dari persamaan keadaan Peng-Robinson (PR-EOS), dan efisiensi politropik/isentropik $\eta_{p,k}$:

$$W_{\text{shaft}, k} \text{ (MW)} = \frac{\dot{m}_k \cdot \Delta h_{s,k}}{\eta_{p,k}} \times 10^{-3}$$

Untuk penelusuran berbasis pengukuran plant DCS, daya poros juga diturunkan dari neraca entalpi uap turbin penggerak (`H4FI029A`, `H4FI030A`, `H4FI031A` dalam $\text{t/h}$):

$$P_{\text{shaft}, k} \text{ (MW)} = \frac{\dot{m}_{\text{steam}, k} \cdot \Delta h_{\text{turbine}, k} \cdot \eta_{\text{mech}}}{3600}$$

Karena tag aliran uap (`H4FI029A`, `H4FI030A`, `H4FI031A`, `total_steam_t_h`) merupakan pembentuk langsung target $P_{\text{shaft}}$, seluruh tag tersebut dikarantina secara ketat dari matriks fitur input `X`.

### 2.2 Destruksi Eksergi Terdiskritisasi (`exergy_destruction_mw`)
Sesuai `AGENTS.md` Pasal 11, perhitungan destruksi eksergi pada MCHE (`4E-1`) dilarang menggunakan pendekatan suhu rata-rata tunggal (*lumped temperature*). Target `exergy_destruction_mw` (dalam satuan **MW**, rentang fisik $[10.0, 65.0]\text{ MW}$) dihitung melalui integral Riemann 100-slice sepanjang kurva komposit panas dan dingin ditambah ireversibilitas kompresor menggunakan teorema Gouy-Stodola:

$$\dot{E}_{D, \text{MCHE}} \text{ (MW)} = T_0 \sum_{i=1}^{100} \Delta Q_i \left( \frac{1}{T_{\text{cold, mean}, i}} - \frac{1}{T_{\text{hot, mean}, i}} \right)$$

$$\dot{E}_{D, \text{comp}} \text{ (MW)} = \sum_{k} W_{\text{shaft}, k} \cdot (1 - \eta_{s,k})$$

dengan suhu lingkungan referensi $T_0 = 288.15\text{ K}$ ($15.0^\circ\text{C}$) dan tekanan referensi $P_0 = 101.325\text{ kPa}$.

---

## 3. Pemisahan Sumber Data: Pengukuran Plant DCS vs Simulasi Termodinamika

Proyek ini memisahkan secara tegas dua jenis asal data target agar tidak terjadi pencampuran label tanpa penanda asal (*provenance flag*):

1. **Target Berbasis Plant Historis (DCS & Lab GC):**
   - Diukur langsung dari instrumen lapangan Badak LNG (`ProcessParameter_*.xlsx`) dan hasil kromatografi gas laboratorium (`OverallComposition_*.xlsx` / `.tsv` pada titik sampel `4C-8`).
   - Mencerminkan kondisi operasi aktual termasuk pengaruh fouling penukar panas, variasi suhu udara sekitar, dan bukaan katup recycle anti-surge (`4UV-53`) maupun katup pemanas ulang suction (`4TV-510`).
2. **Target Berbasis Evaluasi Termodinamika (PR-EOS / Aspen HYSYS Validation):**
   - Dihitung menggunakan mesin termodinamika Peng-Robinson (`src/thermo/pr_thermo.py`) dan kurva komposit MCHE untuk memverifikasi kelayakan fisik kandidat komposisi (batas $\text{MITA} \ge 1.50^\circ\text{C}$, fraksi uap masuk kompresor $\beta = 1.0000$, suhu suction $\ge -45.0^\circ\text{C}$).
   - Digunakan khusus sebagai pemeriksa batas fisika (*physics constraint verifier*) dan studi sensitivitas termodinamika, bukan dicampur secara buta dengan rekaman sensor DCS mentah.

---

## 4. Horizon Prediksi, Resolusi Waktu, dan Keselarasan Fungsi Loss (Loss Alignment)

1. **Horizon Prediksi (`Prediction Horizon`):**
   - Model memprediksi performa daya poros dan konsumsi energi spesifik pada kondisi **tunak per shift operasi 8 jam (*steady-state shift horizon*)** yang disinkronkan dengan waktu pengambilan sampel laboratorium GC (3 kali sehari: pukul 07:00, 15:00, dan 23:00).
   - Agregasi jendela waktu (*time-window median/mean aggregation*) dilakukan pada data DCS beresolusi 1-menit (`minute` resolution) yang berada dalam rezim operasi stabil sebelum waktu pengambilan sampel GC, guna mencegah duplikasi semu (*pseudo-replication*) 480 menit per sampel GC.
2. **Keselarasan Fungsi Loss dan Metrik Evaluasi (`Loss Function Alignment`):**
   - Pelatihan model regresi dan evaluasi performa diselaraskan menggunakan fungsi kerugian berbasis kesalahan absolut (**Mean Absolute Error / MAE**) dan kesalahan kuadrat (**Root Mean Squared Error / RMSE**) dalam satuan proporsional **MW**.
   - Sesuai `AGENTS.md` Pasal 2 dan Pasal 13, kriteria kelulusan model surrogate pada *out-of-sample test set* wajib memenuhi:
     - **Absolute MAE:** $\text{MAE} < 1.0\text{ MW}$
     - **Normalized / Relative MAE:** $\text{NMAE} < 1.0\%$
     - **Koefisien Determinasi:** $R^2_{\text{test}} \ge 0.60$
   - Untuk prediksi komposisi Mixed Refrigerant pada ruang simpleks 5-komponen ($N_2, C_1, C_2, C_2H_4, C_3$), kesalahan dievaluasi dalam satuan **$\text{mol\%}$** setelah transformasi balik ILR (*inverse ILR*) dengan syarat total penjumlahan komponen tepat $100.0\text{ mol\%}$ ($\sum x_i = 1.0 \pm 10^{-6}$).

