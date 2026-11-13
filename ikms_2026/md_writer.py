# Markdown writer helper for IKMS 2026 Full Paper
def write_markdown_paper(OUTPUT_MD, abs_id, abs_en, p1, p2, p3, p4, p_met1, p_met2a, p_met2b, p_met2c, p_met3a, p_met3b, p_met4a, p_met4b, p_met4c, p_res1, p_res2, p_res3, p_res4, p_conc, refs, p_res3b="", p_res4b=""):
    sections = []
    sections.append("# Optimasi Komposisi dan Laju Sirkulasi Mixed Refrigerant Berbasis Machine Learning untuk Efisiensi Energi Kilang Badak LNG\n")
    sections.append("**Bilqiis Dara Ramadhan Sasongko¹*, Mukhammad Yusuf Iqbal¹, Hizkia Dhiego Gurning¹, Afdal Elang Arifin¹**  \n¹Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Jl. Prof. DR. G.A. Siwabessy, Kukusan, Kec. Beji, Kota Depok, Jawa Barat 16425, Indonesia  \n*Penulis korespondensi: bilqiiisdara@gmail.com  \n\n---")
    sections.append(f"### Abstrak\n{abs_id}\n\n**Kata kunci:** C3MR, dekarbonisasi, efisiensi energi spesifik, lean feed gas, machine learning, optimasi mixed refrigerant\n\n---")
    sections.append(f"### Abstract\n{abs_en}\n\n**Keywords:** C3MR, decarbonization, energy efficiency, lean feed gas, machine learning, mixed refrigerant optimization\n\n---")
    
    sections.append("## PENDAHULUAN\n")
    sections.append(p1 + "\n")
    sections.append(p2 + "\n")
    sections.append("![Gambar 1. Efisiensi termal kilang historis PT Badak NGL terhadap pergeseran gas umpan lean](figures/image12.png)\n*Gambar 1. Efisiensi termal kilang historis PT Badak NGL terhadap pergeseran gas umpan lean [3]*\n")
    sections.append(p3 + "\n")
    sections.append(p4 + "\n\n---")
    
    sections.append("## METODE\n")
    sections.append("### 2.1 Operasi Kilang, Akuisisi Data DCS, dan Penyaringan Kondisi Tunak\n")
    sections.append(p_met1 + "\n")
    sections.append("![Gambar 2. Alur metodologi penelitian optimasi mixed refrigerant berbasis machine learning](figures/image6.png)\n*Gambar 2. Alur metodologi penelitian optimasi mixed refrigerant berbasis machine learning*\n")
    sections.append("![Gambar 3. Diagram alir proses (PFD) sistem pencairan C3MR Train H PT Badak NGL](figures/image5.png)\n*Gambar 3. Diagram alir proses (PFD) sistem pencairan C3MR Train H PT Badak NGL [3]*\n")
    
    sections.append("### 2.2 Geometri Komposisi Simpleks ILR dan Pemodelan Machine Learning Berpembatas Fisika\n")
    sections.append(p_met2a + "\n")
    sections.append(r"$$z_i = \sqrt{\frac{D - i}{D - i + 1}} \ln \left( \frac{x_i}{\left( \prod_{j=i+1}^D x_j \right)^{1/(D-i)}} \right) \tag{1}" + "\n")
    sections.append(p_met2b + "\n")
    sections.append(r"$$D_M = \sqrt{(\mathbf{z} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{z} - \boldsymbol{\mu})} \le 3{,}0802 \tag{2}" + "\n")
    sections.append(p_met2c + "\n")
    
    sections.append("### 2.3 Formulasi Optimasi Komposisi, Laju Sirkulasi MR, dan Validasi Termodinamika\n")
    sections.append(p_met3a + "\n")
    sections.append(r"$$\min_{\mathbf{x}, \dot{m}_{\text{MR}}} \text{SEC} = \frac{\dot{W}_{\text{total, C3MR}}}{\dot{m}_{\text{LNG}}} \tag{3}" + "\n")
    sections.append(p_met3b + "\n")
    
    sections.append("### 2.4 Metodologi Evaluasi Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Emisi Karbon\n")
    sections.append(p_met4a + "\n")
    sections.append(r"$$\dot{W}_{\text{shaft}} = \frac{\dot{m} \cdot \Delta h_s}{\eta_p} \tag{4}" + "\n")
    sections.append(r"$$\Delta \dot{W}_{\text{total, C3MR}} = \Delta \dot{W}_{\text{MCR, direct}} + \Delta \dot{W}_{\text{C3, precooling}} \tag{5}" + "\n")
    sections.append(p_met4b + "\n")
    sections.append(r"$$\dot{E}_{D, \text{MCHE}} = T_0 \sum_{i=1}^{N} \Delta Q_i \left( \frac{1}{T_{\text{cold}, i}} - \frac{1}{T_{\text{hot}, i}} \right) \tag{6}" + "\n")
    sections.append(r"$$\dot{E}_{D, \text{comp}} = \dot{W}_{\text{shaft}} \cdot (1 - \eta_s) \tag{7}" + "\n")
    sections.append(p_met4c + "\n\n---")
    
    sections.append("## HASIL DAN PEMBAHASAN\n")
    sections.append("### 3.1 Karakterisasi Baseline Operasi Kilang dan Profil Pasokan Gas Umpan\n")
    sections.append(p_res1 + "\n")
    
    t1_md = """#### Tabel 1. Parameter Baseline Operasional Train H Kilang Badak LNG Melintasi Spektrum Beban Operasi Aktual

| Parameter Operasi | Satuan | P1 (Turndown) | P10 | P25 | P50 (Median) | P75 | P90 | P100 (Puncak) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Laju Gas Umpan Mentah (H1FI0009) | kNm³/jam | 342,55 | 430,90 | 447,29 | 459,80 | 479,65 | 500,76 | 509,02 |
| Laju Gas Umpan Mentah | ton/jam | 258,41 | 325,05 | 337,41 | 346,85 | 361,82 | 377,75 | 383,98 |
| Laju Gas Terolah (H3FI0004) | kNm³/jam | 273,56 | 354,67 | 364,57 | 378,58 | 393,13 | 400,99 | 409,39 |
| Laju Produksi LNG Estimasi | ton/jam | 194,84 | 245,09 | 254,41 | 261,53 | 272,82 | 284,82 | 289,52 |
| Laju Sirkulasi MCR Baseline | ton/jam | 514,18 | 648,25 | 662,75 | 675,07 | 680,05 | 687,06 | 691,80 |
| Rasio MCR / Gas Umpan | kg/kg | 1,990 | 1,994 | 1,964 | 1,946 | 1,880 | 1,819 | 1,802 |
| Laju Uap Turbin Penggerak | ton/jam | 382,09 | 450,21 | 461,27 | 471,78 | 482,32 | 497,89 | 503,04 |
| Daya Poros Kompresor Total | MW | 98,41 | 116,05 | 118,89 | 121,74 | 124,30 | 128,44 | 129,77 |
| Konsumsi Energi Spesifik (SEC) | kWh/t LNG | 505,09 | 473,51 | 467,31 | 465,51 | 455,62 | 450,95 | 448,23 |
"""
    sections.append(t1_md + "\n")
    sections.append("![Gambar 4. Hubungan konsumsi energi spesifik (SEC) terhadap laju produksi LNG melintasi seluruh spektrum operasi kilang](figures/image4.png)\n*Gambar 4. Hubungan konsumsi energi spesifik (SEC) terhadap laju produksi LNG melintasi seluruh spektrum operasi kilang*\n")
    
    sections.append("### 3.2 Validasi Akurasi Model Surrogate Machine Learning dan Batasan Ruang Operasi\n")
    sections.append(p_res2 + "\n")
    
    t2_md = """#### Tabel 2. Metrik Evaluasi Model Surrogate Machine Learning pada Data Telemetri DCS Lapangan dan Termodinamika PR-EOS

| Variabel Target & Simbol | Satuan | Sumber Ground Truth | Sampel Uji (N) | Test R² | Test MAE | Relative Error (NMAE) | Batasan Fisika |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| Total C3MR Shaft Power | MW | Telemetri DCS 2024–2026 | 8.667 data | 0,9557 | 0,8247 | 0,677% | Monotonik umpan & MCR |
| MCR Direct Shaft Power | MW | Telemetri DCS 4KT-2/3 | 8.667 data | 0,9565 | 0,6588 | 0,851% | Monotonik beban kompresor MCR |
| Propane Precooling Power | MW | Telemetri DCS 4KT-1 | 8.667 data | 0,7809 | 0,3727 | 0,839% | Monotonik beban chiller C3 |
| Total Driver Steam Demand | ton/jam | Telemetri Uap DCS | 8.667 data | 0,9997 | 0,2726 | 0,058% | Monotonik daya poros total |
| MCR Direct Driver Steam | ton/jam | Transmitter H4FI029/30A | 8.667 data | 0,9998 | 0,1851 | 0,062% | Monotonik daya poros MCR |
| Suction Drum Temperature | °C | Transmitter H4TI004B | 8.664 data | 0,6677 | 0,3892 | 0,949% | Batas TAL (>= -45,0 °C) |
| MCHE Approach Pinch (MITA) | °C | NeqSim PR-EOS Slicing | 60 kasus | 0,6761 | 0,0657 | 0,952% | Batas Crossover (>= 1,50 °C) |
| Boiler Fuel Gas Demand | Nm³/jam | Neraca Massa Boiler OLS | 43.334 data | 0,9646 | 312,4 | 0,475% | Slope 77,0424 Nm³/ton uap |
"""
    sections.append(t2_md + "\n")
    sections.append("![Gambar 5. Parity plot evaluasi akurasi model surrogate HGBR terhadap data uji independen untuk empat variabel kunci proses](figures/image9.png)\n*Gambar 5. Parity plot evaluasi akurasi model surrogate HGBR terhadap data uji independen untuk empat variabel kunci proses*\n")
    
    sections.append("### 3.3 Kinerja Optimasi Komposisi dan Laju Sirkulasi MR Melintasi Spektrum Beban Operasi Kilang\n")
    sections.append(p_res3 + "\n")
    
    t3_md = """#### Tabel 3. Perbandingan Parameter Teknis Baseline vs Optimasi pada Beban Puncak, Median, dan Kondisi Turndown

| Parameter Operasional | Satuan | Baseline Puncak | Optimasi Puncak | Selisih (%) | Baseline Turndown | Optimasi Turndown | Selisih (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Laju Gas Umpan Mentah | ton/jam | 383,98 | 383,98 | 0,00% | 258,41 | 258,41 | 0,00% |
| Laju Sirkulasi MCR MCHE | ton/jam | 691,80 | 504,76 | -27,04% | 514,18 | 480,00 | -6,65% |
| Daya Poros Kompresor Total | MW | 129,77 | 113,43 | -12,60% | 98,41 | 95,58 | -2,87% |
|  - Daya MCR Langsung (4KT-2/3) | MW | 83,05 | 68,35 | -17,70% | 62,62 | 60,09 | -4,04% |
|  - Daya Propana (4KT-1) | MW | 46,72 | 45,08 | -3,52% | 35,79 | 35,49 | -0,84% |
| Konsumsi Energi Spesifik (SEC) | kWh/t | 448,23 | 391,77 | -12,60% | 505,09 | 490,57 | -2,87% |
| Konsumsi Uap Turbin Penggerak | ton/jam | 503,04 | 439,87 | -12,56% | 382,09 | 371,17 | -2,86% |
| Konsumsi Bahan Bakar Gas Boiler | Nm³/jam | 38.755,0 | 33.888,4 | -12,56% | 29.437,1 | 28.595,5 | -2,86% |
| Laju Emisi CO2 Scope 1 | ton/jam | 82,72 | 72,33 | -12,56% | 62,83 | 61,03 | -2,86% |
| Pendekatan Jepit Minimum (MITA) | °C | 8,85 | 7,17 | - | 8,85 | 7,17 | - |
| Suhu Hisap Suction Drum (Tsuct) | °C | -41,76 | -41,76 | - | -38,56 | -38,56 | - |
"""
    sections.append(t3_md + "\n")
    sections.append("![Gambar 6. Validasi termodinamika MCHE 5E-1 pada beban puncak: (a) Kurva komposit pendinginan T-Q; (b) Gaya dorong temperatur membuktikan bebas crossover dan MITA aman di atas batas 1,50 °C](figures/image7.png)\n*Gambar 6. Validasi termodinamika MCHE 5E-1 pada beban puncak: (a) Kurva komposit pendinginan T-Q; (b) Gaya dorong temperatur membuktikan bebas crossover dan MITA aman di atas batas 1,50 °C*\n")
    sections.append("![Gambar 7. Perbandingan kurva SEC baseline operasi kilang vs. optimasi melintasi seluruh spektrum laju produksi LNG](figures/image10.png)\n*Gambar 7. Perbandingan kurva SEC baseline operasi kilang vs. optimasi melintasi seluruh spektrum laju produksi LNG*\n")
    if p_res3b:
        sections.append(p_res3b + "\n")
    
    sections.append("### 3.4 Dampak Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Dekarbonisasi\n")
    sections.append(p_res4 + "\n")
    
    t4_md = """#### Tabel 4. Ledger Kinerja Tekno-Ekonomi, Energi, dan Lingkungan Tahunan Terbobot Jam Operasi Melintasi Spektrum Beban

| Persentil Operasi | Umpan (t/jam) | Hemat Daya (MW) | Energi Hemat (MWh/th) | Uap Hemat (ton/th) | Bahan Bakar (10⁶ Nm³/th) | Nilai BL 2 (USD/th) | Reduksi CO2 (ton/th) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| P1 (Turndown) | 258,41 | 2,827 | 221,9 | 857,5 | 0,066 | 16.077 | 141,0 |
| P10 | 325,05 | 13,760 | 1.080,1 | 4.174,1 | 0,322 | 78.256 | 686,4 |
| P25 | 337,41 | 14,828 | 1.164,0 | 4.497,8 | 0,347 | 84.326 | 739,6 |
| P50 (Median) | 346,85 | 15,295 | 1.200,6 | 4.639,5 | 0,357 | 86.982 | 762,9 |
| P75 | 361,82 | 15,553 | 1.220,9 | 4.717,9 | 0,363 | 88.452 | 775,8 |
| P90 | 377,75 | 16,117 | 1.265,2 | 4.888,8 | 0,377 | 91.656 | 803,9 |
| P100 (Puncak) | 383,98 | 16,347 | 1.283,2 | 4.958,6 | 0,382 | 92.964 | 815,4 |
| **Total / Rata-rata** | **346,85** | **14,805** | **116.215,3** | **449.087,3** | **34,60** | **8.419.500** | **73.845,9** |
"""
    sections.append(t4_md + "\n")
    sections.append("![Gambar 8. Analisis dampak tekno-ekonomi dan lingkungan optimasi C3MR: (a) Penghematan finansial tahunan dan reduksi emisi CO2; (b) Analisis sensitivitas terhadap variasi harga bahan bakar, uap, dan jam operasi](figures/image8.png)\n*Gambar 8. Analisis dampak tekno-ekonomi dan lingkungan optimasi C3MR: (a) Penghematan finansial tahunan dan reduksi emisi CO2; (b) Analisis sensitivitas terhadap variasi harga bahan bakar, uap, dan jam operasi*\n")
    if p_res4b:
        sections.append(p_res4b + "\n")
    sections.append("\n---")
    
    sections.append("## KESIMPULAN\n")
    sections.append(p_conc + "\n\n---")
    
    sections.append("## DAFTAR PUSTAKA\n")
    sections.append("\n".join(refs) + "\n")
    
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))
    print(f"Markdown paper successfully written to: {OUTPUT_MD}")
