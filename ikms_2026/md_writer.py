# Markdown writer helper for IKMS 2026 Full Paper
def write_markdown_paper(OUTPUT_MD, abs_id, abs_en, p1, p2, p3, p4, p_met1, p_met2a, p_met2b, p_met2c, p_met3a, p_met3b, p_met4a, p_met4b, p_met4c, p_res1, p_res2, p_res3, p_res4, p_conc, refs, p_res3b="", p_res4b=""):
    sections = []
    sections.append("# Optimasi Komposisi dan Laju Sirkulasi Mixed Refrigerant Berbasis Machine Learning untuk Efisiensi Energi Kilang Badak LNG\n")
    sections.append("**Bilqiis Dara Ramadhan Sasongko¹*, Mukhammad Yusuf Iqbal¹, Hizkia Dhiego Gurning¹, Afdal Elang Arifin¹**  \n¹Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Jl. Prof. DR. G.A. Siwabessy, Kukusan, Kec. Beji, Kota Depok, Jawa Barat 16425, Indonesia  \n*Penulis korespondensi: bilqiiisdara@gmail.com  \n\n---")
    sections.append(f"### Abstrak\n{abs_id}\n\n**Kata kunci:** Efisiensi energi spesifik, lean feed gas, liquefied natural gas, machine learning, optimasi mixed refrigerant\n\n---")
    sections.append(f"### Abstract\n{abs_en}\n\n**Keywords:** Energy efficiency, lean feed gas, liquefied natural gas, machine learning, mixed refrigerant optimization\n\n---")
    
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

| Parameter Operasi | Satuan | 141 t/jam | 167 t/jam | 195 t/jam | 218 t/jam | 248 t/jam | 280 t/jam | 308 t/jam |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Laju Gas Umpan Mentah | kNm³/jam | 228,39 | 269,72 | 315,57 | 352,30 | 415,72 | 453,26 | 479,33 |
| Laju Gas Terolah | t/jam | 185,82 | 219,45 | 256,75 | 286,63 | 325,91 | 367,96 | 399,74 |
| Laju Produksi LNG | t/jam | 141,22 | 166,78 | 195,13 | 217,84 | 247,69 | 279,65 | 308,30 |
| Laju Sirkulasi MCR | t/jam | 504,0 | 507,8 | 508,4 | 534,8 | 546,5 | 662,5 | 681,4 |
| Rasio MCR / LNG | kg/kg | 3,569 | 2,956 | 2,522 | 2,369 | 2,182 | 2,283 | 2,210 |
| Laju Uap Turbin Penggerak | t/jam | 355,29 | 361,69 | 363,10 | 376,79 | 412,61 | 465,63 | 484,74 |
| Konsumsi Energi Spesifik (SEC) | kWh/t LNG | 523,00 | 453,17 | 421,96 | 384,58 | 373,68 | 372,97 | 350,49 |
| Jam Operasi per Tahun | jam/thn | 13,6 | 5,0 | 38,5 | 130,7 | 112,1 | 329,1 | 7.220,9 |
| Proporsi Durasi Beban | % | 0,17% | 0,06% | 0,49% | 1,67% | 1,43% | 4,19% | 91,99% |
"""
    sections.append(t1_md + "\n")
    sections.append("![Gambar 4. Hubungan konsumsi energi spesifik (SEC) terhadap laju produksi LNG melintasi seluruh spektrum operasi kilang](figures/image4.png)\n*Gambar 4. Hubungan konsumsi energi spesifik (SEC) terhadap laju produksi LNG melintasi seluruh spektrum operasi kilang*\n")
    
    sections.append("### 3.2 Validasi Akurasi Model Surrogate Machine Learning dan Batasan Ruang Operasi\n")
    sections.append(p_res2 + "\n")
    
    t2_md = """#### Tabel 2. Metrik Evaluasi Model Surrogate Machine Learning pada Data Telemetri DCS Lapangan dan Termodinamika PR-EOS

| Variabel Target & Simbol | Satuan | Sumber Data Uji Ground Truth | Ukuran Sampel (N) | Test R² | Test MAE | Relative Error (NMAE) | Batasan Fisika |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| Total Plant Power (W_plant, DCS) | MW | Telemetri Daya Poros DCS Riil | 67.916 data | 0,8419 | 0,461 | 0,43% | Monoton beban umpan |
| Specific Energy Consumption (SEC) | kWh/t | Telemetri DCS & Neraca Massa | 67.916 data | 0,8419 | 1,510 | 0,43% | Monoton beban umpan |
| Total Driver Steam Flow (m_steam) | t/jam | Telemetri Uap Fiskal DCS | 67.916 data | 0,9552 | 3,487 | 0,72% | Monoton beban umpan |
| Boiler Fuel Gas Demand (V_FG) | Nm³/jam | Telemetri DCS & Neraca Boiler | 67.916 data | 0,9552 | 340,7 | 0,72% | Monoton beban uap (97,7 Nm³/t) |
| Turbin MCR 1st Stage (4KT-2) | t/jam | Transmitter DCS H4FI029A | 65.535 data | 0,9450 | 0,828 | 0,65% | Monoton beban kompresor MCR |
| Turbin MCR 2nd Stage (4KT-3) | t/jam | Transmitter DCS H4FI030A | 65.535 data | 0,9361 | 1,828 | 1,67% | Monoton beban kompresor MCR |
| Turbin Propana Steam (4KT-1) | t/jam | Transmitter DCS H4FI031A | 65.535 data | 0,8115 | 1,479 | 1,12% | Monoton beban chiller |
| Suction Temperature (T_suct) | °C | Transmitter DCS H4TI004B | 67.916 data | 0,9664 | 0,866 | 0,95% | Bound TAL (>= -45,0 °C) |
| Warm Bundle Pinch (MITA_WB) | °C | Diskritisasi PR-EOS HYSYS | 2.000 kasus | 0,9924 | 0,082 | 2,12% | Non-negatif (>= 0 °C) |
| Cold Bundle Pinch (MITA_CB) | °C | Diskritisasi PR-EOS HYSYS | 2.000 kasus | 0,9891 | 0,095 | 2,45% | Non-negatif (>= 0 °C) |
| MCHE Exergy Destruction (E_D) | MW | Integral Riemann PR-EOS | 2.000 kasus | 0,9942 | 0,062 | 0,17% | Non-negatif (Hukum II Termo) |
"""
    sections.append(t2_md + "\n")
    sections.append("![Gambar 5. Parity plot evaluasi akurasi model surrogate HGBR terhadap data uji independen untuk empat variabel kunci proses](figures/image9.png)\n*Gambar 5. Parity plot evaluasi akurasi model surrogate HGBR terhadap data uji independen untuk empat variabel kunci proses*\n")
    
    sections.append("### 3.3 Kinerja Optimasi Komposisi dan Laju Sirkulasi MR Melintasi Spektrum Beban Operasi Kilang\n")
    sections.append(p_res3 + "\n")
    
    t3_md = """#### Tabel 3. Perbandingan Parameter Teknis Baseline vs Optimasi pada Beban Penuh dan Kondisi Turndown

| Parameter Operasional | Satuan | Baseline Penuh (308 t/j) | Optimasi Penuh (308 t/j) | Selisih Penuh (%) | Baseline Turndown (141 t/j) | Optimasi Turndown (141 t/j) | Selisih Turndown (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Laju Sirkulasi MCR MCHE | t/jam | 681,4 | 613,2 | -10,01% | 504,0 | 475,1 | -5,73% |
| Daya Poros Kompresor Total | kW | 108.055,1 | 79.083,4 | -26,81% | 73.855,1 | 47.999,3 | -35,01% |
| Konsumsi Energi Spesifik (SEC) | kWh/t LNG | 350,49 | 256,51 | -26,81% | 523,00 | 339,89 | -35,01% |
| Konsumsi Uap Turbin Penggerak | t/jam | 483,95 | 452,30 | -6,54% | 354,20 | 346,50 | -2,17% |
| Konsumsi Gas Bahan Bakar Boiler | Nm³/jam | 47.281,92 | 44.189,71 | -6,54% | 34.605,34 | 33.853,05 | -2,17% |
| Laju Emisi CO2 Scope 1 | t/jam | 100,79 | 94,20 | -6,54% | 73,77 | 72,16 | -2,17% |
| Pendekatan Jepit Minimum (MITA) | °C | 3,87 | 1,58 | - | 4,20 | 1,94 | - |
| Suhu Hisap Kompresor (Tsuct) | °C | -41,62 | -29,32 | - | -20,57 | -21,14 | - |
| Fraksi Uap Hisap (VF) | - | 1,0000 | 1,0000 | - | 1,0000 | 1,0000 | - |
"""
    sections.append(t3_md + "\n")
    sections.append("![Gambar 6. Validasi termodinamika MCHE 5E-1 pada kondisi beban dasar (308,3 t/jam): (a) Kurva komposit pendinginan T-Q; (b) Gaya dorong temperatur membuktikan tidak ada crossover dan MITA di atas batas 1,50 °C](figures/image7.png)\n*Gambar 6. Validasi termodinamika MCHE 5E-1 pada kondisi beban dasar (308,3 t/jam): (a) Kurva komposit pendinginan T-Q; (b) Gaya dorong temperatur membuktikan tidak ada crossover dan MITA di atas batas 1,50 °C*\n")
    sections.append("![Gambar 7. Perbandingan kurva SEC baseline operasi kilang vs. optimasi melintasi seluruh spektrum laju produksi LNG](figures/image10.png)\n*Gambar 7. Perbandingan kurva SEC baseline operasi kilang vs. optimasi melintasi seluruh spektrum laju produksi LNG*\n")
    if p_res3b:
        sections.append(p_res3b + "\n")
    
    sections.append("### 3.4 Dampak Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Dekarbonisasi\n")
    sections.append(p_res4 + "\n")
    
    t4_md = """#### Tabel 4. Ledger Kinerja Tekno-Ekonomi, Energi, dan Lingkungan Tahunan Terbobot Jam Operasi Melintasi Spektrum Beban

| Laju Produksi LNG (t/jam) | Jam Operasi (jam/thn) | Penghematan Daya (kW) | Energi Terhemat (MWh/thn) | Uap Terhemat (ton/thn) | Bahan Bakar Gas Terhemat (10⁶ Nm³/thn) | Penghematan Finansial (USD/thn) | Reduksi Emisi CO2 (ton/thn) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 141,2 | 13,6 | 25.855,7 | 351,6 | 104,7 | 0,01 | 3.700 | 21,8 |
| 166,8 | 5,0 | 25.145,9 | 125,7 | 37,6 | 0,00 | 1.300 | 7,8 |
| 195,1 | 38,5 | 29.096,2 | 1.120,2 | 338,4 | 0,03 | 12.000 | 70,4 |
| 217,8 | 130,7 | 24.770,4 | 3.237,5 | 967,6 | 0,09 | 34.200 | 201,5 |
| 247,7 | 112,1 | 26.696,1 | 2.992,6 | 895,1 | 0,09 | 31.700 | 186,4 |
| 279,7 | 329,1 | 31.863,3 | 10.486,2 | 3.138,8 | 0,31 | 111.000 | 653,4 |
| 308,3 | 7.220,9 | 28.971,8 | 209.202,4 | 234.407,5 | 22,90 | 8.286.100 | 48.820,5 |
| **Total / Rata-rata** | **7.849,9** | **28.983,3** | **227.516,0** | **239.889,7** | **23,44** | **8.480.000** | **49.961,8** |
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
