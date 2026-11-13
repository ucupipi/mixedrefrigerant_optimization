# REKONSTRUKSI ALUR CERITA ILMIAH (STAGE 3)
## ARSITEKTUR NARASI PENELITIAN C3MR TRAIN H KILANG BADAK LNG (IKMS 2026)
### REKONSTRUKSI BERBASIS BUKTI MUTLAK (PATH B: METODOLOGI, INVESTIGASI OPERASIONAL & KUALIFIKASI FISIK)

---

## 1. ARGUMEN SENTRAL RISET (CENTRAL RESEARCH ARGUMENT)

Studi ini membuktikan bahwa penuaan reservoir gas alam di Kalimantan Timur menimbulkan **kopel ganda yang merugikan (dual operational mismatch)** pada Unit Pencairan C3MR Train H PT Badak NGL: pasokan gas umpan semakin *lean* (mencapai 94,5 mol% $C_1$) yang memperbesar beban pendinginan kriogenik spesifik (+2,40%), sementara penurunan laju pasokan gas (*turndown* hingga 258,4 ton/jam) memicu lonjakan konsumsi energi spesifik (SEC) hingga +12,7% akibat sirkulasi mixed refrigerant (MR) berlebih yang tertahan oleh batas keselamatan *anti-surge flow floor* kompresor sentrifugal ($\ge 480,0\text{ ton/jam}$) dan interlock suhu hisap kriogenik (TAL $\ge -45,0^\circ\text{C}$).

Untuk menjawab tantangan ini, penelitian merekonstruksi kerangka kerja integratif berbasis data DCS riil (2024–2026), kromatografi gas rutin (2.531 sampel), geometri simpleks *Isometric Log-Ratio* (ILR 4-DoF), dan pemodelan *surrogate* berpembatas fisik. Secara kritis, studi ini mengungkap temuan fundamental: **model machine learning empiris tabular konvensional gagal menangkap dinamika jepit suhu kriogenik internal MCHE (menghasilkan prediksi jepit semu yang beku pada $7,17^\circ\text{C}$)**. Dengan menerapkan simulasi termodinamika PR-EOS terdiskritisasi 100-slice, penelitian ini mengidentifikasi residual penutupan neraca energi MCHE ($-4,3\%$ s.d. $+15,3\%$) dan menetapkan **peta jalan kualifikasi lapangan bertahap (*staged field qualification pathway*)** yang wajib dipenuhi sebelum strategi penyesuaian komposisi dapat diimplementasikan secara aman tanpa risiko trip pabrik.

---

## 2. FORMULASI PIRAMIDA TERBALIK (GENERAL-TO-SPECIFIC NARRATIVE)

```
[Level 1: Konteks Industri Global & Nasional]
Pencairan gas alam (LNG) adalah proses padat energi di mana 
efisiensi siklus refrigerasi kompresi menentukan konsumsi bahan bakar pabrik.
                   │
                   ▼
[Level 2: Karakteristik Proses C3MR]
Siklus Propane-Precooled Mixed Refrigerant (C3MR) mengandalkan integrasi 
dua tahap pendinginan: prapendinginan propana dan pencairan kriogenik MCHE.
                   │
                   ▼
[Level 3: Masalah Spesifik Lapangan di Train H Badak LNG]
Penuaan lapangan gas memicu fenomena lean feed (94,5% C1) dan operasi turndown.
Saat umpan turun, sirkulasi MR tidak dapat diturunkan bebas karena tertahan 
anti-surge floor kompresor (>= 480 t/h) & interlock TAL (-45 °C), memicu lonjakan SEC +12,7%.
                   │
                   ▼
[Level 4: Tantangan Rekayasa & Kelemahan Praktik Eksisting]
Penyetelan rasio MR secara manual shift-by-shift bersifat reaktif.
Ruang fraksi mol terikat batas simpleks tertutup S^5 (total 100%), 
membuat manipulasi variabel kimia rentan memicu korelasi palsu & crossover suhu MCHE.
                   │
                   ▼
[Level 5: Kesenjangan Riset Ilmiah (Research Gap)]
Ketiadaan metodologi yang mengintegrasikan data DCS lapangan, geometri simpleks ILR,
surrogate model berpembatas fisik, dan audit termodinamika multi-stream yang jujur 
terhadap batas penutupan neraca energi (energy balance closure).
                   │
                   ▼
[Level 6: Tujuan & Kontribusi Penelitian (Path B Mandate)]
Membangun kerangka kerja karakterisasi operasional, memetakan ruang operasi simpleks 4-DoF,
membongkar keterbatasan model ML empiris pada penukar panas kriogenik, 
dan merumuskan kriteria kualifikasi rekayasa yang teruji sebelum penerapan di kilang.
```

---

## 3. KESENJANGAN RISET & KONTRIBUSI ILMIAH SPESIFIK

### Kesenjangan Riset (Research Gaps):
1. **Kesenjangan Geometris:** Sebagian besar literatur optimasi refrigeran memperlakukan fraksi mol pada ruang Euclidean bebas, mengabaikan konstrain simpleks $S^D$ sehingga menghasilkan rekomendasi formula refrigeran yang secara matematis bias dan secara fisik tidak dapat dicapai di kilang.
2. **Kesenjangan Dinamika Turndown:** Studi optimasi C3MR di literatur hampir selalu mengasumsikan kilang beroperasi pada 100% *design baseload*. Ketiadaan pembahasan interaksi antara batas aliran minimum anti-surge kompresor dengan efisiensi MCHE pada kondisi *turndown* ekstrem meninggalkan kekosongan panduan operasional industri.
3. **Kesenjangan Validitas Machine Learning:** Publikasi terdahulu sering mengklaim keberhasilan model *surrogate* AI dengan metrik statistik tinggi ($R^2 > 0,95$) tanpa menguji apakah model tersebut benar-benar mematuhi hukum termodinamika kekekalan energi dan tidak mengalami kegagalan *boundary-hugging* atau prediksi semu (*frozen output*).

### Kontribusi Ilmiah Spesifik (Defensible Contributions):
1. **Karakterisasi Empiris Penalti Turndown:** Membuktikan secara kuantitatif melalui telemetri DCS 2024–2026 bahwa penurunan laju umpan sebesar 32,7% memicu kenaikan rasio MR/umpan sebesar +10,4% dan pembengkakan SEC sebesar +12,7% akibat kekakuan batas mekanikal kompresor sentrifugal.
2. **Pemetaan Geometri Simpleks ILR 4-DoF:** Mengembangkan kerangka pemetaan komposisi MR 5-komponen ke dalam koordinat Euclidean tak terikat menggunakan transformasi Aitchison ILR dengan pembatas elipsoid Jarak Mahalanobis 95% ($D_M \le 3,0802$ pada derajat kebebasan 4), membuktikan ruang operasi aktual kilang secara statistik.
3. **Pembuktian Keterbatasan Model Surrogate Empiris:** Membuktikan secara eksperimental bahwa arsitektur ML tabular konvensional (HGBR) sangat presisi dalam memprediksi daya mekanikal poros kompresor ($R^2 = 0,9557$, MAE 0,82 MW) dan kebutuhan uap turbin ($R^2 = 0,9997$), namun gagal total pada variabel termal internal MCHE (menghasilkan MITA konstan $7,17^\circ\text{C}$ akibat ketiadaan kopel entalpi PR-EOS).
4. **Audit Neraca Energi & Peta Jalan Kualifikasi Lapangan (Path B):** Mengkuantifikasi residual neraca energi kriogenik 100-slice ($-4,3\%$ s.d. $+15,3\%$) serta menetapkan kriteria verifikasi hidraulika pipa, prosedur injeksi *make-up* bertahap, dan protokol keselamatan operasi sebelum optimasi dapat dijalankan di Train H.

---

## 4. MATRIKS RETENSI, REVISI, DAN ELIMINASI MATERI

| Materi / Klaim | Status | Tindakan Penyuntingan & Justifikasi Ilmiah |
|:---|:---:|:---|
| **Latar Belakang Makro Transisi Energi** | *Eliminasi* | Hapus 2 paragraf pembuka generik. Ganti langsung dengan konteks operasional Kilang Badak Train H. |
| **Klaim Konsumsi Energi 59,3%** | *Revisi / Kualifikasi* | Ubah menjadi pernyataan umum bahwa sistem kompresi C3MR adalah konsumen uap terbesar di kilang, tanpa angka spesifik tanpa sitasi audit primer. |
| **Klaim Perbandingan Data DCS 2017** | *Eliminasi* | Hapus klaim analisis 1.051.200 menit data 2017. Pertahankan 88,1 mol% hanya sebagai angka desain historis literatur. |
| **Klaim Penghematan 14,805 MW / 116 GWh** | *Eliminasi* | Hapus sebagai klaim hasil optimasi. Ganti dengan analisis potensi penghematan teoritis dan tantangan validasi model fisik. |
| **Formula MR C3 = 2,01 mol%** | *Eliminasi / Dokumentasi Cacat* | Hapus sebagai rekomendasi kilang. Paparkan sebagai contoh kegagalan optimasi tak terkendali yang mengeksploitasi batas elipsoid ($D_M = 3,0762$). |
| **Nilai MITA Konstan 7,17 °C** | *Revisi / Temuan Negatif* | Jelaskan sebagai bukti empiris kegagalan model surrogate ML tanpa pembatas hukum kekekalan energi. |
| **Tabel 1 (Baseline Operasi P1–P100)** | *Retensi & Penguatan* | Pertahankan sepenuhnya. Ini adalah data empiris DCS yang sangat berharga dan sahih. |
| **Transformasi ILR & Mahalanobis 4-DoF** | *Retensi & Koreksi* | Pertahankan metodologi ILR; pastikan derajat kebebasan tepat $D-1=4$ dengan nilai kritis 3,0802. |
| **Dekomposisi Uap Turbin & Boiler FG** | *Retensi* | Pertahankan analisis regresi konsumsi bahan bakar boiler (77,04 s.d. 79,76 Nm³/ton uap) dengan pembanding ASME PTC 4 (97,70 Nm³/ton uap). |
| **Analisis Residual Neraca Energi MCHE** | *Penambahan Baru (Wajib)* | Tambahkan tabel dan pembahasan residual neraca energi ($-4,3\%$ hingga $+15,3\%$) sebagai fondasi kejujuran ilmiah Path B. |
| **Peta Jalan Kualifikasi Lapangan (Roadmap)** | *Penambahan Baru (Wajib)* | Tambahkan protokol pengujian bertahap di lapangan dan analisis risiko operasional pada kontrol DCS. |

---

## 5. STRUKTUR BAB & LOGIKA NARRATIF (PATH B)

```
1. PENDAHULUAN
   ├── 1.1 Konteks Operasional Pencairan Gas Alam dan Unit C3MR Train H
   ├── 1.2 Fenomena Pergeseran Gas Lean dan Pembengkakan SEC Saat Turndown
   ├── 1.3 Batasan Keselamatan Kompresor Sentrifugal dan Suction Drum
   └── 1.4 Kesenjangan Riset dan Tujuan Penelitian

2. METODOLOGI PENELITIAN
   ├── 2.1 Batas Sistem Train H dan Karakterisasi Aliran Proses
   ├── 2.2 Akuisisi Data Telemetri DCS dan Pembersihan Kondisi Tunak
   ├── 2.3 Pemetaan Geometri Komposisi Simpleks ILR dan Ruang Mahalanobis 4-DoF
   ├── 2.4 Arsitektur Model Surrogate Machine Learning Berpembatas Monotonik
   ├── 2.5 Formulasi Diskritisasi Termodinamika MCHE dan Neraca Energi PR-EOS
   └── 2.6 Kerangka Rekonsiliasi Neraca Uap dan Bahan Bakar Boiler

3. HASIL DAN PEMBAHASAN
   ├── 3.1 Bukti Empiris Fenomena Penalti Turndown pada Operasi Baseline Train H
   ├── 3.2 Analisis Distribusi Kromatografi Gas dan Batas Elipsoid Operasi
   ├── 3.3 Evaluasi Kinerja Model Surrogate ML: Keberhasilan vs Kegagalan Fisik
   ├── 3.4 Investigasi Termodinamika MCHE dan Analisis Residual Neraca Energi
   ├── 3.5 Analisis Ruang Peluang Penyesuaian Operasional (Operational Window)
   └── 3.6 Peta Jalan Kualifikasi Lapangan dan Manajemen Risiko Operasi DCS

4. KESIMPULAN DAN REKOMENDASI REKAYASA
   ├── 4.1 Kesimpulan Utama Penelitian
   └── 4.2 Rekomendasi Penerapan Bertahap bagi PT Badak NGL
```

---
*Dokumen ini menjadi acuan arsitektur penulisan IKMS_FULLPAPER_OUTLINE.md (Stage 4) dan naskah lengkap IKMS_FULLPAPER_REWRITTEN.md (Stage 5).*
