# PANDUAN PENGGUNAAN WEBSITE OPERATOR (OPERATOR GUIDE)
## Plant-3 Train H — C3MR Optimization & Make-Up Advisory
**Versi Panduan:** 2.0  
**Target Pengguna:** Operator Konsol DCS, Panel Operator, Process Engineer Train H.  
**Sifat Panduan:** Panduan teknis penggunaan aplikasi (BUKAN Prosedur Operasi Standar / SOP Pengoperasian Kilang).

---

## 1. Tujuan & Batasan Aplikasi
Aplikasi ini dibangun untuk membantu operator konsol dan *process engineer* menganalisis skenario operasi (*what-if analysis*) dan memahami dampak perubahan laju gas umpan (*feed gas*) serta komposisi refrigerant campuran (*mixed refrigerant* / MCR) terhadap efisiensi daya kompresor Train H.

### Hal yang DAPAT dilakukan aplikasi:
- Menampilkan kondisi proses aktual (snapshot DCS dan GC laboratorium per shift) secara terpisah.
- Menjalankan solver optimasi non-linear (*Live SLSQP*) untuk mencari rekomendasi laju alir MCR dan resep komposisi optimal.
- Menghitung rekomendasi laju injeksi *make-up* hidrokarbon ($N_2, C_1, C_2, C_3$) untuk transisi resep.
- Memprediksi estimasi penghematan daya poros kompresor total Train H (MW).
- Memeriksa batas keselamatan teknis: batas bawah sirkulasi $480.0\text{ t/h}$, batas suhu suction drum $\ge -45.0^\circ\text{C}$, superheat PR-EOS $\ge 3.0^\circ\text{C}$, dan elipsoid $D_M \le 3.0802$.

### Hal yang TIDAK DAPAT dilakukan aplikasi:
- **TIDAK BISA dan TIDAK AKAN PERNAH menulis set point ke DCS, PLC, atau SIS.**
- **Bukan sistem autopilot atau pengendali proses otomatis.**
- **Tidak menggantikan pembacaan alarm, panel trip, interlock DCS, atau keputusan *shift supervisor*.**
- **Tidak menjamin keselamatan kilang secara keseluruhan** (status sistem hanya membuktikan parameter yang tercantum dalam register kendala).

---

## 2. Definisi Kategori Nilai pada Spreadsheet
Tabel utama spreadsheet membedakan 5 jenis nilai yang tidak boleh tertukar:
1. **Aktual DCS (Kolom D - Biru)**: Nilai riil yang tercatat dari instrumen lapangan atau GC laboratorium. Bersifat *read-only* terhadap skenario dan tidak akan pernah tertimpa oleh simulasi skenario.
2. **Target Skenario (Kolom E - Hijau)**: Nilai hipotetis atau rekomendasi yang dimasukkan untuk simulasi *what-if*. Nilai ini dapat diedit manual oleh operator atau diisi otomatis oleh solver optimasi AI.
3. **Hasil Perhitungan (Calculated - Abu-Abu)**: Nilai yang dihitung dari rumus deterministik (misalnya selisih $\Delta$, rasio sirkulasi, atau konversi satuan).
4. **Hasil Prediksi Model (Predicted - Hijau Tua)**: Estimasi keluaran daya kompresor yang dihasilkan oleh model Machine Learning (`PhysicsResidualSurrogate`).
5. **Kandidat Optimasi (Optimized Candidate - Ungu)**: Titik operasi yang direkomendasikan oleh solver matematis live SLSQP.

---

## 3. Langkah Operasional (Workflow) di Sheet 1

### Langkah 1: Periksa Kolom Aktual DCS
- Pastikan angka pada kolom **Aktual DCS** mencerminkan kondisi shift terkini:
  - Laju alir gas umpan (`H1FI012`) dalam satuan t/h.
  - Laju sirkulasi MCR (`H4FI001`) dalam satuan t/h.
  - Hasil analisa GC laboratorium terakhir untuk 5 komponen MCR ($N_2, C_1, C_2, C_2H_4, C_3$).
- Jika total GC belum tepat 100.00% (misal 99.82%), klik tombol **`⚡ 100%`** di baris A8 untuk menormalisasi secara proporsional.

### Langkah 2: Dapatkan Rekomendasi AI
- Klik tombol ungu **`✨ Hitung Rekomendasi AI`** pada header.
- Sistem akan menjalankan Live SLSQP Solver (~1.5 – 3.8 detik) untuk mencari titik operasi dengan konsumsi steam/daya terendah yang mematuhi seluruh batas fisik.
- Kolom Target Skenario (Kolom E) akan otomatis terisi dengan rekomendasi laju MCR dan komposisi target yang presisi 100.00%.

### Langkah 3: Evaluasi Dampak Daya & Injeksi Make-Up
- Periksa **Seksi C (Dampak Kinerja)**:
  - Lihat estimasi daya poros kompresor target vs aktual DCS.
  - Lihat estimasi penghematan daya ($\Delta P\text{ MW}$) dan reduksi emisi $\text{CO}_2$.
  - Periksa *Specific Shaft Power per tonne of Treated Feed* (kWh/t feed).
- Periksa **Seksi D (Rekomendasi Make-Up)**:
  - Periksa laju alir injeksi komponen yang perlu ditambah pada katup `H4FIC005` ($C_1$), `H4FIC006` ($N_2$), `H4FI00C8` ($C_2$), atau `H4FIC007` ($C_3$).
  - Perhatikan bahwa komponen yang berlebih diberi status `TAHAN / STOP` (tutup katup make-up dan biarkan dilusi alami).

### Langkah 4: Verifikasi Batas Keselamatan & Kendala (Seksi E)
- Pastikan status pada banner dan Seksi E menunjukkan:
  - **Estimasi H4TI004B**: Harus $\ge -45.0^\circ\text{C}$ (Aman dari trip TAL).
  - **Laju Alir MCR**: Harus $\ge 480.0\text{ t/h}$ (Aman dari batas bawah anti-surge kickback 4UV-53).
  - **Jarak Mahalanobis $D_M$**: Harus $\le 3.0802$ (Di dalam elipsoid operasional kilang).
  - **Closure Komposisi**: Harus tepat $100.00\text{ mol\%}$.

---

## 4. Cara Membaca Status & Peringatan Aplikasi

| Status Tampilan | Makna Operasional | Tindakan yang Harus Dilakukan |
|---|---|---|
| **Semua kendala yang diperiksa terpenuhi** (Hijau) | 5 parameter keselamatan teknis yang dievaluasi berada dalam batas aman. | Skenario layak ditinjau lebih lanjut oleh Process Engineer / Lead Operator. |
| **Ada kendala yang perlu ditinjau (Warning)** (Kuning/Amber) | Parameter berada dalam rentang operasi tetapi mendekati batas kritis (misal $T_{\text{suct}} < -42^\circ\text{C}$ atau $D_M > 2.50$). | Evaluasi margin proses. Siapkan pembukaan katup reheat 4TV-510 jika suhu suction terus turun. |
| **Skenario ditolak oleh sistem** (Merah) | Terjadi pelanggaran batas wajib (misal $T_{\text{suct}} < -45.0^\circ\text{C}$ atau MCR $< 480\text{ t/h}$). | **DILARANG menerapkan target skenario ini.** Ubah kembali input ke kondisi aman. |
| **Di luar domain operasional model (Out of Domain)** (Ungu) | Komposisi atau beban proses berada di luar data historis kilang ($D_M > 3.0802$). | Prediksi ML tidak dapat dipercaya pada titik ini. Konsultasikan dengan Process Engineer. |
| **Belum dapat dievaluasi (Not Evaluated)** (Abu-Abu) | Data atau kurva pendukung belum tersedia (misal: Peta Anti-Surge Dinamis Kompresor). | Pahami bahwa sistem hanya memeriksa batas aliran bawah (flow floor), bukan kurva surge lengkap. |

---

## 5. Kapan Hasil Rekomendasi TIDAK BOLEH Digunakan?
Operator konsol **DILARANG MENGGUNAKAN** rekomendasi jika terjadi salah satu kondisi berikut:
1. Plant sedang mengalami transisi darurat, *hunting*, atau *upset* besar (misal: trip boiler, trip kompresor lain, atau fluktuasi tekanan feed gas parah).
2. Terdapat instrumen transmitter kunci yang *freeze*, *faulty*, atau sedang dikalibrasi (misal transmitter $H4TI004B$ atau transmitter tekanan $H4PI014B$).
3. Status aplikasi menampilkan `OUT OF DOMAIN`, `BLOCKED`, atau `DATA STALE`.
4. Rekomendasi belum ditinjau dan disetujui bersama oleh *Shift Supervisor* dan *Process Engineer*.

---

## 6. Hirarki Wewenang & Kepatuhan Prosedur
Setiap tindakan penyesuaian operasi di lapangan maupun di konsol DCS **MUTLAK MENGACU PADA**:
1. Distributed Control System (Yokogawa Centum VP DCS) dan Safety Instrumented System (SIS).
2. Prosedur Operasi Standar (SOP) resmi Plant-3 Train H.
3. Wewenang *Shift Supervisor* dan *Console Operator*.
4. Instruksi Tertulis dari *Process Engineering Section*.
