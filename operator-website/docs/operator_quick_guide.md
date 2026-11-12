# PANDUAN CEPAT OPERATOR (OPERATOR QUICK GUIDE)
## Aplikasi Pendukung Keputusan Operator C3MR — Baseload LNG Plant-3 Train H

> **PERINGATAN KESELAMATAN (SAFETY NOTICE):**  
> Aplikasi ini adalah alat bantu analisis dan simulasi **READ-ONLY (Hanya-Baca)**.  
> Aplikasi ini **TIDAK TERHUBUNG LANGSUNG** ke DCS untuk mengirim perintah kontrol, tidak mengubah setpoint, dan tidak menggerakkan katup lapangan. Setiap keputusan perubahan operasi kilang **WAJIB** melalui prosedur resmi (SOP) dan arahan Shift Supervisor / Process Engineer.

---

### 1. Cara Menjalankan Aplikasi
Aplikasi terdiri dari dua komponen ringan yang berjalan pada komputer lokal (tanpa perlu koneksi internet):

1. **Jalankan Backend (Layanan Model ML):**
   ```cmd
   cd operator-website\backend
   python main.py
   ```
   *Layanan berjalan pada: `http://localhost:3001`*

2. **Jalankan Antarmuka Web (Frontend):**
   ```cmd
   cd operator-website\frontend
   npm run dev
   ```
   *Buka peramban (browser) di: `http://localhost:5173`*

---

### 2. Tiga Tab Utama & Cara Penggunaannya

#### Tab 01 — INPUT & HASIL (Format Lembar Kerja / Spreadsheet)
- **Tabel Variabel:** Menampilkan variabel proses yang dikelompokkan (Umpan Gas, Kompresor MCR, Komposisi MCR, dan MCHE).
- **Kolom 'Kondisi Aktual':** Menampilkan data operasi acuan (baseline). Nilai ini terkunci (read-only).
- **Kolom 'Nilai Skenario':** Kolom yang dapat diedit oleh operator (ditandai dengan warna latar biru muda) untuk menguji skenario perubahan:
  - *Laju Umpan Gas (`H1FI012`)*: Uji perubahan kapasitas produksi (t/h).
  - *Laju Sirkulasi MCR (`H4FI001`)*: Uji kebutuhan aliran refrigeran (t/h).
  - *Komposisi MCR (N₂, C₁, C₂, C₂H₄, C₃)*: Uji perubahan rasio refrigeran campuran (mol%).
- **Tombol 'Hitung Prediksi':** Mengirim skenario ke model machine learning dan menampilkan hasil prediksi daya poros total (MW) serta SEC (kWh/t).
- **Tombol 'Reset ke Aktual':** Mengembalikan semua input skenario ke nilai kondisi aktual.

#### Tab 02 — GRAFIK & ANALISIS
- **Grafik Daya vs Laju Umpan:** Memetakan posisi titik skenario terhadap kurva operasi historis Train H.
- **Perbandingan Batang (Bar Chart):** Membandingkan konsumsi daya total (MW) kondisi aktual vs skenario secara langsung.
- **Distribusi Komposisi MCR:** Diagram visual 5-komponen refrigeran campuran.
- **Pemeriksa Domain Operasi (Jarak Mahalanobis):** Memvisualisasikan apakah titik skenario masih berada di dalam elipsoid kepercayaan 95% data kilang ($D_M \le 3.08$).

#### Tab 03 — PANDUAN OPERATOR
- Penjelasan detail mengenai arti setiap tag instrumen.
- Batasan keselamatan interlock dan proteksi kompresor.
- Pertanyaan umum (FAQ) dan panduan tindakan saat alarm muncul.

---

### 3. Arti Indikator Status & Warna

| Warna / Label | Status | Arti & Tindakan Operator |
| :--- | :--- | :--- |
| 🟢 **HIJAU** | **AMAN / DALAM DOMAIN** | Titik skenario aman dan model memprediksi dengan keyakinan tinggi ($D_M \le 3.08$, seluruh interlock terpenuhi). |
| 🟡 **KUNING** | **PERINGATAN / TRANSISI** | Skenario berada di rezim transisi atau mendekati batas domain. Periksa kembali input dan gunakan hasil sebagai indikasi awal. |
| 🔴 **MERAH** | **BAHAYA / DI LUAR DOMAIN** | Skenario melanggar batas keselamatan mekanikal kilang (misal: aliran MCR $< 480$ t/h atau suhu suction $< -45^\circ\text{C}$) atau berada di luar jangkauan data historis. **DILARANG menerapkan kondisi ini di plant.** |

---

### 4. Batasan Keselamatan Kritis Kilang (Hard Limits)

1. **Batas Minimum Aliran Anti-Surge Kompresor MCR (`H4FI001`):**  
   $\ge 480.0\text{ t/h}$. Jika aliran sirkulasi turun di bawah $480.0\text{ t/h}$, katup kickback `4UV-53` wajib membuka untuk melindungi impeler kompresor 4K-2 dari fenomena surge.
2. **Batas Alarm Rendah Suhu Suction Drum (`H4TI004B`):**  
   $\ge -45.0^\circ\text{C}$ (Trip darurat TALL pada $-51.0^\circ\text{C}$). Mencegah kondensasi cairan hidrokarbon masuk ke sudu kompresor (*liquid carryover*). Katup pemanas `4TV-510` membuka jika suhu mendekati $-45.0^\circ\text{C}$.
3. **Beda Tekan Bundle MCHE (`H5PDI003` / `H4PDIC024`):**  
   Warm bundle normal $\le 0.35\text{ kg/cm}^2$, Alarm pada $0.42\text{ kg/cm}^2$, Trip darurat pada $0.54\text{ kg/cm}^2$.
4. **Jarak Mahalanobis Komposisi MCR ($D_M$):**  
   Wajib $\le 3.0802$. Nilai di atas batas ini menandakan komposisi gas refrigeran belum pernah diuji secara aman di Plant-3 Train H.

---

### 5. Kontak Eskalasi & Bantuan Teknis
Jika menemukan anomali prediksi, pesan kesalahan, atau membutuhkan validasi termodinamika mendalam (simulasi Aspen HYSYS / PR-EOS):
- **Process Engineering Dept. — Plant-3**
- **Lead Reliability / Turbomachinery Engineer**
- **Control Room Shift Supervisor**

