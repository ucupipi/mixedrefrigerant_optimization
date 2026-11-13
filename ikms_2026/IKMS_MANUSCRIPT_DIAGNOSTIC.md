# DIAGNOSTIK MANUSKRIP IKMS 2026 (STAGE 1)
## AUDIT KRITIS & BEDAH FORENSIK MANUSKRIP "IKMS2026_FullPaper_PNJ_Final.md"
### PT BADAK NGL — TRAIN H C3MR ENERGY EFFICIENCY RESEARCH

---

## 1. IKHTISAR DIAGNOSTIK

Audit diagnostik ini dilakukan terhadap draf manuskrip terkini `ikms_2026/IKMS2026_FullPaper_PNJ_Final.md` (36.446 karakter, 220 baris) sebelum dilakukan penulisan ulang total. Evaluasi mengintegrasikan perspektif *Senior Process Engineer*, *Thermodynamics Reviewer*, *Machine Learning Researcher*, dan *Scientific Editor*.

Hasil audit menemukan bahwa meskipun draf telah mengadopsi sejumlah terminologi rekayasa dan membuang jargon metaforis ekstrem, **manuskrip masih mengusung alur klaim optimasi lama (Path A) yang secara fundamental cacat secara termodinamika dan bertentangan dengan bukti forensik Rebuild v3.2/v3.3**. Secara khusus, manuskrip masih mempertahankan klaim penghematan daya kuantitatif 14,805 MW (116.215,3 MWh/tahun, USD 8,42 Juta/tahun, 73.845,9 ton CO2/tahun) yang diturunkan dari model surrogate MITA yang beku pada 7,169 °C, formula refrigeran yang melanggar batas fisika historis (C3 = 2,01 mol%), serta mengabaikan residual neraca energi MCHE yang belum tertutup (-4,3% hingga +15,3%).

Berdasarkan mandat **Path B**, manuskrip harus direkonstruksi secara total menjadi studi investigasi operasional, perumusan kerangka kerja data-driven berpembatas termodinamika riil, evaluasi keterbatasan surrogate empiris, dan penegasan syarat kelayakan fisik sebelum optimasi dapat diterapkan secara aman di kilang.

---

## 2. EVALUASI ALUR CERITA (STORYLINE) SAAT INI

| Elemen Alur | Kondisi dalam Manuskrip Saat Ini | Diagnosis Kritis & Cacat Ilmiah |
|:---|:---|:---|
| **Alur Utama (Central Narrative)** | Memaksakan narasi keberhasilan optimasi komersial instan (*successful turn-key optimization*) berbasis AI. | **Palsu & Tidak Defensibel.** Model termodinamika MCHE belum mencapai *energy closure* tervalidasi (residual P10: -4,3%, P50: +10,6%, P90: +15,3%). Mengklaim optimasi siap terap melanggar etika rekayasa proses. |
| **Pernyataan Masalah (Problem Statement)** | Disempitkan hanya pada penuaan reservoir gas yang menyebabkan *lean feed gas* (94,5 mol% C1). | Kurang komprehensif. Masalah kilang sebenarnya adalah **kopel ganda (dual-mismatch)**: gas umpan menjadi lebih *lean*, sementara laju umpan sering turun (*turndown*), namun operator terpaksa mempertahankan laju sirkulasi MR tinggi karena dibatasi oleh *flow floor* anti-surge kompresor 4K-2/3 (>= 480 t/h) dan interlock suhu dingin suction drum (TAL >= -45 °C). |
| **Kesenjangan Riset (Research Gap)** | Menyebut studi terdahulu terlalu teoritis atau melanggar simpleks Euclidean. | Terlalu umum. Kesenjangan spesifik yang belum terjawab di literatur adalah: **ketiadaan kerangka integrasi komposisi empiris multikomponen (ILR simplex) dengan batasan hidraulika kompresor nyata dan neraca uap utilitas terkopel pada kondisi turndown kilang baseload**. |
| **Kontribusi Ilmiah** | Mengklaim resep optimal tunggal (C3 = 2,01%) dan penghematan daya 14,805 MW. | **Cacat.** Formula C3 = 2,01% berada jauh di bawah batas operasi aman historis P05 (4,19 mol%) dan Jarak Mahalanobis berada di 99,87% batas kritis ($D_M = 3,0762$ vs 3,0802). Angka penghematan adalah angka *quarantined* dari model cacat. |

---

## 3. ARGUMEN BERULANG & LATAR BELAKANG MUBAZIR

1. **Pengulangan Definisi 5 Komponen MR:**
   - Komponen MR ($N_2, C_1, C_2, C_2H_4, C_3$) dan jumlah fraksi 100% dijelaskan berulang kali di Abstrak (L9, L15), Pendahuluan (L22), dan Metodologi 2.2 (L48).
   - *Tindakan:* Cukup definisikan satu kali secara formal di Metodologi 2.3.
2. **Latar Belakang Transisi Energi Generik:**
   - Paragraf pembuka Pendahuluan (L22) memuat klise umum mengenai peran LNG dalam transisi energi global yang tidak menambah substansi masalah teknis Train H.
   - *Tindakan:* Pangkas narasi makro energi; langsung buka dengan konteks operasional Kilang Badak LNG Train H yang menghadapi pergeseran karakteristik gas umpan dan pola operasi turndown.
3. **Pengulangan Batasan Operasi (TAL, Anti-surge, MITA):**
   - Batasan operasional kompresor sentrifugal diulang di Abstrak, Pendahuluan L24, Metodologi 2.3 L64, dan Pembahasan 3.3 L130.
   - *Tindakan:* Konsolidasikan seluruh batasan fisik dan operasional kilang ke dalam satu tabel matriks batasan terpadu di Metodologi.

---

## 4. KLAIM TANPA BUKTI & ASUMSI TIDAK TERDOKUMENTASI (UNSUPPORTED CLAIMS)

1. **Klaim Pangsa Konsumsi Energi 59,3% (L9, L15, L22):**
   - *Klaim:* "Sistem C3MR menyumbang 59,3% konsumsi energi internal di Kilang Badak LNG."
   - *Status:* **UNSUPPORTED / QUARANTINED.** Tidak ada dokumen primer atau kalkulasi neraca energi pabrik lengkap yang membuktikan angka 59,3% pada batas baterai Train H yang spesifik.
   - *Tindakan:* Kualifikasikan pernyataan menjadi: sistem pencairan C3MR merupakan konsumen energi uap dan bahan bakar terbesar di kilang, tanpa menyebut angka 59,3% tanpa sitasi audit primer.
2. **Klaim Baseline Historis 2017 (88,1 mol% C1 dan 1.051.200 Rekaman DCS) (L9, L15, L22):**
   - *Klaim:* "tercatat 88,1 mol% pada 2017" dan perbandingan dataset menit 2017 vs 2026.
   - *Status:* **INVALIDATED.** Investigasi forensik membuktikan data menit DCS tahun 2017 tidak tersedia di repositori. Data operasional aktual yang sahih dan dapat ditelusuri secara independen adalah periode 2024–2026.
   - *Tindakan:* Hapus seluruh klaim perbandingan langsung dataset menit 2017. Jadikan 88,1 mol% hanya sebagai catatan desain historis referensi literatur internal, bukan dataset pembanding langsung.
3. **Klaim Zero-CAPEX Instan (L9, L15, L31, L178, L186):**
   - *Klaim:* "seluruh batas keselamatan operasional kilang terbukti aman... zero CAPEX", "Payback Period tercapai secara instan (0 bulan)".
   - *Status:* **UNSUPPORTED.** Mengklaim nol CAPEX tanpa membuktikan modifikasi instrumentasi, validasi prosedur transisi make-up MCR di lapangan, dan risiko dinamis kolom fraksinasi/drum kriogenik adalah penyederhanaan yang menyesatkan (*hand-waving*).
   - *Tindakan:* Nyatakan secara jujur bahwa kerangka kerja ini memanfaatkan infrastruktur DCS eksisting, namun implementasi lapangan memerlukan pengujian bertahap (*staged field trial*) dan evaluasi keandalan sistem pendingin.

---

## 5. KONTRAKDIKSI ANGKA & CACAT NUMERIK (NUMERICAL DEFECTS)

1. **Klaim Penghematan Daya Poros 14,805 MW (L9, L15, L100, L159, L172, L187):**
   - *Cacat:* Angka 14,805 MW berasal dari model Rebuild v3.2 yang menggunakan penskalaan heuristik dari Kandidat A lama dan mengandalkan surrogate MITA yang beku pada 7,169 °C. Nilai ini tidak didukung oleh simulasi termodinamika tertutup.
   - *Status:* **QUARANTINED / UNSUPPORTED.**
   - *Tindakan:* Ganti narasi hasil optimasi menjadi evaluasi kesenjangan operasional (*operational opportunity gap*) dan potensi reduksi sirkulasi, dengan mencantumkan batas ketidakpastian secara transparan.
2. **Nilai MITA Konstan 7,169 °C Melintasi Seluruh Spektrum Beban (L121, L130, L145):**
   - *Cacat:* Model surrogate MITA dalam draf lama memprediksi MITA tepat 7,169 °C (dibulatkan menjadi 7,17 °C) pada P1 hingga P100. Investigasi menunjukkan fitur komposisi ($N_2, C_2, C_3$) tidak berpengaruh dalam model tersebut, dan variasi hanya dikendalikan 98,6% oleh temperatur lingkungan $T_{\text{amb}}$.
   - *Status:* **FATAL DEFECT (Pasal 2 & 4 AGENTS.md).**
   - *Tindakan:* Tampilkan kegagalan model surrogate empiris ini sebagai temuan ilmiah penting (*scientific finding*): bahwa model ML tabular standar tanpa hukum konservasi entalpi gagal menangkap fenomena termal internal MCHE.
3. **Komposisi C3 = 2,01 mol% dan Jarak Mahalanobis $D_M = 3,0762$ (L9, L15, L130):**
   - *Cacat:* Data GC historis (2.531 sampel) menunjukkan rentang C3 adalah 0,00–10,11 mol% dengan P05 = 4,19 mol% dan median 5,85 mol%. Formula optimal yang diajukan (C3 = 2,01 mol%) berada jauh di luar batas operasi normal kilang. Selain itu, $D_M = 3,0762$ berada di 99,87% batas elipsoid kritis ($D_M \le 3,0802$), menandakan solusi berada tepat di ujung tebing ekstrapolasi.
   - *Status:* **HIGH-RISK EXTRAPOLATION.**
   - *Tindakan:* Paparkan temuan ini sebagai bukti bahwa optimasi tanpa batasan margin konservatif cenderung mengeksploitasi tepi ruang data (*boundary hugging*).
4. **Ketidaksesuaian Jumlah Data DCS:**
   - Pada baris 9 dan 38 tertulis 44.641 data menit DCS dan 43.334 data tunak. Namun di file lain terdapat angka 720.734 atau 67.916 data.
   - *Tindakan:* Rekonsiliasi dan nyatakan secara eksplisit periode akuisisi data primer (misal: 1 Januari 2024 – 31 Januari 2025), resolusi waktu (1 menit), kriteria penapisan tunak, dan jumlah baris akhir yang lolos uji kestabilan secara terverifikasi.
5. **Dekomposisi Daya Terbalik / Inkonsisten:**
   - Pada draf lama, porsi penghematan MCR langsung diklaim 89,51% (13,251 MW) dan propana hanya 10,49% (1,554 MW). Padahal secara fisika prapendinginan, penurunan laju sirkulasi MCR sebesar 27% secara langsung memangkas beban termal penukar panas propana 3E-14/17/18 dalam proporsi yang signifikan.
   - *Tindakan:* Sajikan dekomposisi berbasis kurva kinerja kompresor OEM terkalibrasi dan jelaskan interaksi termal antar siklus pendingin secara fisik.

---

## 6. TRANSISI LEMAH & PENJELASAN REKAYASA YANG HILANG

1. **Mengapa Sirkulasi MCR Tidak Boleh Turun Sembarangan Saat Turndown?**
   - Manuskrip lama menyebut "operator mempertahankan laju sirkulasi MCR pada 514,2–691,8 t/h" seolah-olah operator lalai atau tidak efisien.
   - *Penjelasan Rekayasa yang Hilang:* Operator sengaja tidak menurunkan aliran MCR lebih rendah karena **kompresor sentrifugal MCR (4K-2/3) memiliki batas batas surge minimum (480 t/h)** dan **suction drum memiliki interlock trip TAL (-45 °C)**. Jika MCR dikurangi tanpa mengubah rasio fraksi ringan/berat, temperatur hisap akan anjlok drastis ke zona bahaya carryover cairan ke sudu kompresor.
   - *Tindakan:* Berikan penjelasan fisik yang adil dan apresiatif terhadap disiplin keselamatan operasional Kilang Badak LNG.
2. **Keterbatasan Neraca Energi MCHE (The P4 Closure Reality):**
   - Manuskrip lama sama sekali tidak menyinggung tantangan konvergensi simulasi VLE kriogenik dan neraca panas multi-aliran tabung spiral (*spiral-wound heat exchanger*).
   - *Tindakan:* Tambahkan pembahasan mendalam mengenai diskritisasi 100-slice MCHE, evaluasi profil entalpi PR-EOS, dan jelaskan mengapa residual neraca energi (-4,3% s.d. +15,3%) mengharuskan pendekatan kualifikasi yang hati-hati sebelum optimasi diterapkan di lapangan.

---

## 7. RENCANA RESTRUKTURISASI SEKSI (ROADMAP REWRITING)

| Seksi Lama | Masalah Utama | Rencana Penulisan Ulang (Path B) |
|:---|:---|:---|
| **Judul & Abstrak** | Menjanjikan optimasi komersial instan dan mencantumkan angka quarantined. | Ubah judul dan abstrak menjadi studi komparatif: investigasi operasional gas lean, karakterisasi ruang simpleks MR, evaluasi model surrogate fisik, dan analisis kelayakan termodinamika C3MR. |
| **1. Pendahuluan** | Banyak basa-basi makro energi; klaim 2017 & 59,3% tidak terbukti. | Bangun alur piramida terbalik: Konteks pencairan baseload $\rightarrow$ Dinamika gas lean & turndown Train H $\rightarrow$ Dilema surge vs efisiensi $\rightarrow$ Kesenjangan metodologi integrasi $\rightarrow$ Tujuan penelitian yang jujur dan terukur. |
| **2. Metodologi** | Menyajikan metodologi seolah-olah seluruh loop tertutup dan valid 100%. | Sajikan batas sistem terperinci (Train H C3MR), metodologi filtering DCS, transformasi ILR & geometri Mahalanobis 4-DoF, arsitektur HGBR dengan batasan monotonik, serta formulasi evaluasi termodinamika PR-EOS diskritisasi 100-slice. |
| **3. Hasil & Pembahasan** | Menampilkan angka optimasi palsu (14,8 MW, MITA 7,17 °C konstan, C3=2,01%). | **Restrukturisasi total:**<br>3.1 Baseline operasional & bukti empiris fenomena penalti turndown (+12,7% SEC).<br>3.2 Karakteristik kromatografi gas & pemetaan ruang simpleks ILR (analisis 2.531 sampel).<br>3.3 Evaluasi kritis model surrogate ML: keberhasilan pada variabel mekanikal vs kegagalan pada variabel termal internal MCHE.<br>3.4 Analisis termodinamika MCHE & identifikasi tantangan validasi penutupan neraca energi.<br>3.5 Analisis sensitivitas operasional & peta jalan kualifikasi lapangan (*field qualification pathway*). |
| **4. Kesimpulan** | Mengulang klaim penghematan daya fiktif dan zero CAPEX instan. | Tarik kesimpulan substantif: (1) Fenomena penalti turndown terbukti secara data DCS; (2) Ruang operasi MR berhasil dipetakan secara matematis via ILR 4-DoF; (3) Model ML terbukti memerlukan pembatas fisik tertutup; (4) Rekomendasi teknis bagi manajemen kilang untuk pengujian bertahap. |

---
*Dokumen ini menjadi dasar verifikasi untuk penyusunan IKMS_CLAIM_EVIDENCE_REGISTER.csv (Stage 2) dan IKMS_STORYLINE_RECONSTRUCTION.md (Stage 3).*
