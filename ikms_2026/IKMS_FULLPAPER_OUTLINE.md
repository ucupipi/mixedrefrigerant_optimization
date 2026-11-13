# ARSITEKTUR LENGKAP MANUSKRIP (STAGE 4)
## OUTLINE RINCI MANUSKRIP ILMIAH IKMS 2026
### JUDUL: Investigasi Operasional, Pemodelan Simpleks ILR, dan Evaluasi Termodinamika Siklus C3MR Train H PT Badak NGL Menghadapi Gas Umpan Lean

---

## IKHTISAR ARSITEKTUR DOKUMEN

| Bagian Dokumen | Jumlah Subbab | Fokus Pertanyaan Ilmiah Utama | Tabel / Gambar Pendukung |
|:---|:---:|:---|:---:|
| **Judul & Abstrak** | - | Apa masalah riil Train H, apa temuan empirisnya, dan apa batas validitas hasilnya? | - |
| **1. Pendahuluan** | 4 subtopik | Mengapa operasi gas lean & turndown memicu penalti SEC, dan mengapa pendekatan ML naif gagal? | Gambar 1, Gambar 2 |
| **2. Metodologi** | 7 subbab | Bagaimana batas sistem, pembersihan data DCS, geometri simpleks, arsitektur ML, dan PR-EOS dirumuskan? | Gambar 1, Tabel 1, Tabel 2 |
| **3. Hasil & Pembahasan** | 7 subbab | Apa bukti empiris data kilang, bagaimana performa ML vs PR-EOS, mengapa neraca energi menyisakan residual, dan bagaimana roadmap kualifikasinya? | Tabel 3, Tabel 4, Tabel 5, Tabel 6, Gambar 2, Gambar 3, Gambar 4 |
| **4. Kesimpulan** | 2 subtopik | Apa kesimpulan yang defensibel dan apa rekomendasi operasional bagi manajemen kilang? | - |
| **Daftar Pustaka** | - | Apakah seluruh sitasi relevan, terverifikasi, dan mutakhir? | 26 referensi |

---

## 1. JUDUL DAN ABSTRAK

### Judul Manuskrip
**Bahasa Indonesia:**  
*Investigasi Operasional, Pemodelan Simpleks ILR, dan Evaluasi Termodinamika Siklus C3MR Train H PT Badak NGL Menghadapi Gas Umpan Lean*  
**Bahasa Inggris:**  
*Operational Investigation, Simplex ILR Modeling, and Thermodynamic Evaluation of the C3MR Cycle at PT Badak NGL Train H Under Lean Feed Gas Conditions*

### Abstrak
- **Tujuan:** Menjelaskan fenomena pembengkakan energi spesifik pada Train H akibat penuaan reservoir gas, memetakan ruang operasi komposisi refrigeran multikomponen, menguji keandalan model surrogate ML berpembatas fisik, serta mengevaluasi kelayakan termodinamika penukar panas kriogenik MCHE.
- **Metode:** Menganalisis 44.641 menit data telemetri DCS (2024–2026) dan 2.531 sampel kromatografi gas rutin shift; menerapkan transformasi Isometric Log-Ratio (ILR 4-DoF) berpembatas elipsoid Mahalanobis ($D_M \le 3,0802$); melatih model HistGradientBoostingRegressor (HGBR) dengan batasan monotonik; serta memvalidasi kesetimbangan termodinamika Peng-Robinson EOS terdiskritisasi 100-slice pada MCHE.
- **Temuan Kunci:** Telemetri membuktikan bahwa saat laju umpan gas turun 32,7% (384,0 ke 258,4 t/jam), laju sirkulasi MCR tertahan batas anti-surge kompresor sentrifugal ($\ge 480,0\text{ t/jam}$) dan interlock suction drum (TAL $\ge -45,0^\circ\text{C}$), memicu lonjakan rasio MCR/umpan (+10,4%) dan peningkatan SEC (+12,7%). Model surrogate HGBR sangat akurat untuk variabel mekanikal ($R^2 = 0,9557$, MAE 0,82 MW pada daya poros total; $R^2 = 0,9997$ pada uap penggerak), namun model tabular empiris gagal memprediksi temperatur jepit MCHE internal (menghasilkan nilai konstan semu $7,17^\circ\text{C}$). Audit termodinamika 100-slice mengungkap residual penutupan neraca energi MCHE berkisar $-4,3\%$ (P10) hingga $+15,3\%$ (P90).
- **Kesimpulan & Rekomendasi:** Optimasi komersial instan tidak dapat diklaim valid sebelum penutupan neraca energi diselesaikan. Diusulkan peta jalan kualifikasi lapangan bertahap dan implementasi panduan supervisori berbasis data historis untuk mitigasi operasional yang aman.

---

## 2. DETAIL PER SUBBAB: PENDAHULUAN (SECTION 1)

### 1.1 Konteks Operasional Pencairan Gas Alam dan Unit C3MR Train H
- **Tujuan:** Menempatkan siklus C3MR Train H sebagai unit pemrosesan gas alam berskala besar yang sangat sensitif terhadap efisiensi energi kompresi pendinginan.
- **Pertanyaan Dijawab:** Mengapa efisiensi termal siklus C3MR di Train H sangat vital bagi operasional kilang Badak LNG?
- **Bukti Diperlukan:** Deskripsi konfigurasi dua siklus (propana prapendinginan dan MCR pencairan kriogenik), penggerak turbin uap multi-stage, dan integrasi uap bertekanan tinggi dari boiler utilitas.
- **Gambar/Tabel:** Gambar 1 (Diagram alir skematik batas baterai Train H C3MR).
- **Kesimpulan Subtopik:** Efisiensi termal siklus refrigerasi secara langsung mengendalikan konsumsi uap boiler dan emisi bahan bakar kilang.

### 1.2 Fenomena Pergeseran Gas Lean dan Pembengkakan SEC Saat Turndown
- **Tujuan:** Menguraikan masalah rekayasa aktual akibat penuaan sumur gas hulu.
- **Pertanyaan Dijawab:** Apa dampak pergeseran komposisi gas umpan dari desain kaya (rich) ke lean, dan mengapa laju pasokan yang fluktuatif memperburuk efisiensi?
- **Bukti Diperlukan:** Data desain awal (metana $\le 91,6\text{ mol\%}$, acuan historis $88,1\text{ mol\%}$) vs telemetri riil 2024–2026 ($94,5\text{ mol\%}$); kenaikan beban pendinginan spesifik MCHE (+2,40%, 637,6 ke 652,9 kJ/kg); data DCS pembengkakan SEC dari 448,2 kWh/t LNG pada beban puncak ke 505,1 kWh/t LNG pada beban turndown (+12,7%).
- **Gambar/Tabel:** Gambar 2 (Tren historis pergeseran gas umpan lean dan efisiensi termal kilang).
- **Kesimpulan Subtopik:** Fluktuasi pasokan dan karakteristik gas lean menciptakan penalti efisiensi ganda yang membebani utilitas uap pabrik.

### 1.3 Batasan Keselamatan Kompresor Sentrifugal dan Suction Drum Kriogenik
- **Tujuan:** Menjelaskan akar penyebab fisik mengapa sirkulasi refrigeran tidak bisa diturunkan secara bebas oleh operator.
- **Pertanyaan Dijawab:** Mengapa operator kilang terpaksa mempertahankan laju alir MCR tinggi saat beban kilang turun?
- **Bukti Diperlukan:** Spesifikasi teknis kompresor sentrifugal MCR 4K-2/3 (anti-surge flow floor minimum $480,0\text{ ton/jam}$); interlock keselamatan suhu hisap kriogenik drum 4C-8 (TAL $\ge -45,0^\circ\text{C}$); bahaya pembentukan droplet cairan (*liquid carryover*) ke impeller kompresor jika refrigeran terlalu dingin.
- **Gambar/Tabel:** Matriks batasan keselamatan proses pada teks.
- **Kesimpulan Subtopik:** Penahanan laju sirkulasi MCR saat turndown adalah tindakan defensif operator yang mutlak diperlukan demi keselamatan mesin, bukan kelalaian operasional.

### 1.4 Kesenjangan Riset dan Tujuan Penelitian (Path B)
- **Tujuan:** Mengidentifikasi celah dalam literatur terdahulu dan merumuskan tujuan penelitian yang realistis dan defensibel.
- **Pertanyaan Dijawab:** Apa kelemahan metodologi optimasi C3MR sebelumnya, dan apa kontribusi spesifik riset ini?
- **Bukti Diperlukan:** Kritik terhadap optimasi algoritma genetika/PSO tanpa konstrain simpleks (ruang Euclidean bebas memicu korelasi palsu); kritik terhadap model ML black-box yang memprediksi suhu semu; ketiadaan pengujian neraca energi tertutup multi-stream MCHE.
- **Gambar/Tabel:** Diagram metodologi penelitian terpadu (Gambar 3).
- **Kesimpulan Subtopik:** Penelitian bertujuan membangun kerangka kerja integratif berbasis data DCS riil, geometri simpleks ILR 4-DoF, pemodelan ML teruji batas fisiknya, serta audit neraca energi termodinamika terbuka untuk merumuskan panduan operasi yang aman.

---

## 3. DETAIL PER SUBBAB: METODOLOGI PENELITIAN (SECTION 2)

### 2.1 Objek Penelitian dan Batas Sistem
- **Tujuan:** Mendefinisikan secara tegas batas fisik peralatan (*battery limits*) yang dianalisis pada Train H.
- **Pertanyaan Dijawab:** Peralatan apa saja yang masuk ke dalam cakupan model dan neraca energi?
- **Bukti Diperlukan:** Kompresor propana 4K-1, kompresor MCR tahap rendah 4K-2, tahap tinggi 4K-3; turbin uap penggerak 4KT-1/2/3; penukar panas tabung spiral MCHE 5E-1; rangkaian chiller propana 4E-7/8/9; drum hisap kriogenik 4C-8; jalur uap utilitas HP Steam ($60\text{ kg/cm}^2\text{G}$, $450^\circ\text{C}$) dan kondensat ekstraksi.
- **Gambar/Tabel:** Diagram Alir Proses PFD Train H C3MR (Gambar 4).
- **Kesimpulan Subtopik:** Batas sistem mencakup seluruh loop refrigerasi C3MR dan kopelnya dengan neraca uap pembangkit.

### 2.2 Data Operasi dan Pra-pemrosesan Kondisi Tunak
- **Tujuan:** Menjelaskan sumber data, protokol penapisan, dan verifikasi kualitas data DCS.
- **Pertanyaan Dijawab:** Bagaimana data operasional dihimpun dan disaring agar representatif untuk pemodelan tunak?
- **Bukti Diperlukan:** 44.641 rekaman menit telemetri DCS (Januari 2024 – Januari 2026) pada 172 tag instrumen; algoritma penapisan tunak berbasis varians bergerak (*moving-window standard deviation*) pada laju umpan dan temperatur MCHE; eliminasi periode trip, startup, dan shutdown menyisakan 43.334 menit tunak; pembagian 100 medoid persentil beban (P1–P100).
- **Gambar/Tabel:** Tabel 1 (Deskripsi parameter instrumen kunci DCS Train H).
- **Kesimpulan Subtopik:** Dataset DCS yang bersih dan terverifikasi mencakup spektrum operasi tunak kilang dari beban terendah hingga beban puncak.

### 2.3 Rekonstruksi Komposisi Mixed Refrigerant dan Geometri Simpleks ILR
- **Tujuan:** Merumuskan penanganan matematis komposisi 5-komponen refrigeran campuran.
- **Pertanyaan Dijawab:** Bagaimana memetakan fraksi mol yang terikat penjumlahan 100% ke dalam ruang matematis yang bebas korelasi palsu?
- **Bukti Diperlukan:** 2.531 sampel analisis kromatografi gas rutin laboratorium per shift; perumusan transformasi Isometric Log-Ratio (ILR) dari ruang simpleks $S^5$ ke koordinat Euclidean $\mathbb{R}^4$ ($D-1=4$); perumusan elipsoid kepercayaan 95% menggunakan Jarak Mahalanobis dengan nilai kritis distribusi Chi-kuadrat $\chi^2_{0.95, 4} = 9,4877 \rightarrow D_M \le 3,0802$.
- **Gambar/Tabel:** Persamaan transformasi ILR dan matriks kovarian kromatografi gas.
- **Kesimpulan Subtopik:** Pemetaan ILR 4-DoF menjamin seluruh rekomendasi komposisi tetap berada dalam ruang fisika yang dapat diinjeksikan di kilang.

### 2.4 Model Termodinamika dan Evaluasi Kelayakan Fisik
- **Tujuan:** Merumuskan metodologi evaluasi kesetimbangan fase uap-cair (VLE) dan perpindahan panas multi-stream pada MCHE.
- **Pertanyaan Dijawab:** Bagaimana profil temperatur dan kurva entalpi dihitung secara fisik di dalam penukar panas tabung spiral?
- **Bukti Diperlukan:** Persamaan Keadaan Peng-Robinson (PR-EOS) dengan parameter interaksi biner terkoreksi; metode diskritisasi numerik 100-slice pada MCHE 5E-1; perumusan Minimum Internal Temperature Approach (MITA $\ge 1,50^\circ\text{C}$); evaluasi ketiadaan crossover temperatur ($\Delta T_i > 0$ untuk setiap slice $i=1..100$); fraksi uap hisap kompresor (VF = 1,0000).
- **Gambar/Tabel:** Skema diskritisasi 100-slice MCHE dan formulasi integral entalpi.
- **Kesimpulan Subtopik:** PR-EOS terdiskritisasi 100-slice adalah standar mutlak untuk menguji keabsahan fisik siklus refrigerasi kriogenik.

### 2.5 Model Surrogate Machine Learning Berpembatas Monotonik
- **Tujuan:** Mengembangkan model pengganti komputasional cepat (*surrogate model*) yang patuh pada hukum fisika searah.
- **Pertanyaan Dijawab:** Bagaimana arsitektur machine learning dirancang agar tidak melanggar prinsip fisika proses?
- **Bukti Diperlukan:** Pemilihan arsitektur HistGradientBoostingRegressor (HGBR); penerapan batasan monotonik (`monotonic_cst`) di mana laju alir umpan dan sirkulasi refrigeran berkorelasi positif monotonik terhadap daya kompresi dan konsumsi uap; pembagian dataset 80:20 (34.667 sampel latih dan 8.667 sampel uji independen); evaluasi metrik ganda: $R^2$, MAE absolut dalam satuan proporsional (MW untuk daya), dan Relative MAE (NMAE < 1,0%).
- **Gambar/Tabel:** Tabel konfigurasi hyperparameter dan fitur monotonik HGBR.
- **Kesimpulan Subtopik:** Pembatas monotonik mencegah model surrogate menghasilkan artefak komputasi non-fisik pada variabel mekanikal kompresi.

### 2.6 Formulasi Ruang Kelayakan Operasi dan Evaluasi Sensitivitas
- **Tujuan:** Merumuskan batasan optimasi matematis dan evaluasi batasan operasional kilang.
- **Pertanyaan Dijawab:** Variabel apa yang dioptimasi dan batasan apa yang wajib dipatuhi tanpa kompromi?
- **Bukti Diperlukan:** Fungsi objektif minimasi SEC (kWh/ton LNG); vektor keputusan laju sirkulasi MCR ($\dot{m}_{\text{MR}}$) dan koordinat ILR komposisi ($\mathbf{z}$); variabel keadaan terpantau (temperatur MCHE masuk/keluar, profil jepit internal 100-slice, tekanan hisap/lucut); batasan keras: $D_M \le 3,0802$, $\dot{m}_{\text{MCR, suction}} \ge 480,0\text{ t/h}$, $T_{\text{suct}} \ge -45,0^\circ\text{C}$, $\text{MITA} \ge 1,50^\circ\text{C}$, dan kapasitas governor turbin uap $\le 95\%$.
- **Gambar/Tabel:** Tabel 2 (Formulasi Variabel Optimasi, Masukan Proses, Variabel Keadaan, Fungsi Objektif, dan Batasan Kelayakan Operasi Siklus C3MR).
- **Kesimpulan Subtopik:** Ruang pencarian dibatasi ketat oleh elipsoid Mahalanobis dan batas keselamatan instrumen DCS kilang.

### 2.7 Perhitungan Energi dan Dampak Turunan
- **Tujuan:** Merumuskan metodologi konversi daya poros mekanikal ke konsumsi uap turbin, bahan bakar gas boiler, dan emisi $CO_2$.
- **Pertanyaan Dijawab:** Bagaimana dampak efisiensi kompresor ditranslasikan ke neraca uap utilitas dan emisi lingkungan?
- **Bukti Diperlukan:** Teorema Stodola untuk laju uap ekspansi isentropik; laju konsumsi uap spesifik turbin IAPWS-IF97 (rata-rata terbobot $4,194\text{ t/MWh}$); regresi telemetri DCS boiler fuel gas ($77,0424\text{ Nm}^3/\text{ton uap}$, $R^2 = 0,9646$) dan pembanding standar ASME PTC 4 ($97,70\text{ Nm}^3/\text{ton uap}$); faktor emisi pembakaran primer ($164,44\text{ kg CO}_2/\text{ton uap}$) dan IPCC 2006 ($56,10\text{ kg CO}_2/\text{GJ}$).
- **Gambar/Tabel:** Persamaan neraca uap dan konversi emisi.
- **Kesimpulan Subtopik:** Metodologi konversi bertingkat menghubungkan kinerja mekanikal kompresor dengan utilitas pembangkit uap secara tertelusur.

---

## 4. DETAIL PER SUBBAB: HASIL DAN PEMBAHASAN (SECTION 3)

### 3.1 Karakteristik Operasi Baseline Train H
- **Tujuan:** Memaparkan data telemetri aktual kilang dan membuktikan secara empiris terjadinya fenomena penalti turndown.
- **Pertanyaan Dijawab:** Bagaimana profil operasional kilang melintasi spektrum beban P1 hingga P100?
- **Bukti Diperlukan:** Pembuktian Tabel 3 (Baseline Operasional P1–P100): laju umpan mentah 258,4–384,0 t/jam; produksi LNG 194,8–289,5 t/jam; sirkulasi MCR 514,2–691,8 t/jam; rasio MCR/umpan melonjak dari 1,802 ke 1,990 kg/kg (+10,4%); SEC meningkat dari 448,2 ke 505,1 kWh/t LNG (+12,7%).
- **Gambar/Tabel:** Tabel 3 (Parameter Baseline Train H P1–P100) dan Gambar 2 (Kurva SEC empiris vs Laju Produksi LNG).
- **Kesimpulan Subtopik:** Data DCS membuktikan secara konklusif adanya ketidakefisienan operasional nyata saat kilang mengalami penurunan laju umpan gas.

### 3.2 Karakteristik Kromatografi Gas dan Ruang Operasi MR
- **Tujuan:** Menyajikan analisis statistik terhadap komposisi refrigeran aktual kilang.
- **Pertanyaan Dijawab:** Bagaimana distribusi fraksi mol 5 komponen MR di lapangan dan seberapa lebar ruang operasinya?
- **Bukti Diperlukan:** Analisis 2.531 sampel GC shift: $N_2$ (median 4,50%, rentang 0,70–7,80%), $C_1$ (median 42,50%, 39,10–52,67%), $C_2$ (median 46,80%, 31,67–51,06%), $C_2H_4$ (median 0,35%, 0,00–42,61%), $C_3$ (median 5,85%, 0,00–10,11%); korelasi negatif $C_3$ terhadap suhu hisap ($r = -0,756$); visualisasi sebaran koordinat ILR terhadap elipsoid Mahalanobis 95%.
- **Gambar/Tabel:** Tabel 4 (Statistik Deskriptif Kromatografi Gas 2.531 Sampel Shift) dan Gambar sebaran simpleks ILR.
- **Kesimpulan Subtopik:** Operator kilang secara aktif memodulasi komposisi MR per shift untuk menjaga suhu hisap, namun penyesuaian tersebut belum dioptimasi secara simultan terhadap kurva komposit MCHE.

### 3.3 Kinerja Model Machine Learning dan Arsitektur Pemodelan Hibrida
- **Tujuan:** Menyajikan evaluasi model surrogate HGBR berfitur batasan monotonik pada data uji independen (8.667 sampel).
- **Pertanyaan Dijawab:** Bagaimana akurasi model machine learning pada variabel mekanikal dan mengapa evaluasi termal MCHE dialihkan ke simulasi PR-EOS?
- **Bukti Diperlukan:** Tabel 5 (Metrik Evaluasi Model ML): Presisi tinggi pada variabel mekanikal dan aliran: Total Shaft Power ($R^2 = 0,9557$, MAE 0,82 MW, NMAE 0,677%), Driver Steam ($R^2 = 0,9997$, MAE 0,27 t/h, NMAE 0,058%), Suction Drum Temp ($R^2 = 0,6677$, MAE 0,39 °C, NMAE 0,949%). Prinsip pemisahan domain (*domain decoupling*) di mana evaluasi termal jepit kriogenik MCHE diselesaikan via PR-EOS 100-slice deterministik.
- **Gambar/Tabel:** Tabel 5 (Evaluasi Model ML) dan Gambar 3 (Parity Plot variabel mekanikal).
- **Kesimpulan Subtopik:** Model surrogate ML sangat handal mengemulasi daya mekanikal dan uap turbin, sementara integritas termodinamika MCHE dijaga penuh oleh integrasi PR-EOS 100-slice.

### 3.4 Validasi Model Termodinamika MCHE dan Analisis Residual Neraca Energi (Path B Core)
- **Tujuan:** Memaparkan hasil investigasi termodinamika PR-EOS 100-slice dan mengungkap tantangan penutupan neraca energi secara transparan.
- **Pertanyaan Dijawab:** Apakah simulasi termodinamika independen berhasil mereproduksi neraca panas MCHE dengan sempurna?
- **Bukti Diperlukan:** Hasil perhitungan NeqSim PR-EOS 100-slice pada medoid beban operasional: residual neraca energi $\Delta Q_{\text{residual}} = (Q_{\text{cold}} - Q_{\text{hot}}) / Q_{\text{hot}} \times 100\%$ menghasilkan P10: $-4,3\%$, P50: $+10,6\%$, dan P90: $+15,3\%$; analisis penyebab: ketidakpastian fraksi pemisahan aliran dua-fase MCHE (*two-phase distribution*), beban subcooler 4E-40 (menyerap 0,45–0,70 MW), serta kelemahan estimasi entalpi campuran hidrokarbon-nitrogen pada tekanan transkritis kriogenik.
- **Gambar/Tabel:** Gambar 4 (Kurva komposit pendinginan T-Q) dan Tabel 6 (Hasil Evaluasi Termodinamika PR-EOS 100-Slice dan Residual Neraca Energi MCHE).
- **Kesimpulan Subtopik:** Ketiadaan penutupan neraca energi yang sempurna membuktikan bahwa klaim optimasi komersial instan adalah prematur; penelitian ini secara jujur menempatkan validasi termodinamika sebagai prasyarat kritis yang belum selesai.

### 3.5 Analisis Skenario Peluang Operasional dan Batasan Risiko
- **Tujuan:** Mengevaluasi potensi teoretis penyesuaian sirkulasi MCR dan strategi operasi konservatif dengan memperhitungkan batasan keselamatan.
- **Pertanyaan Dijawab:** Seberapa besar ruang perbaikan operasional yang secara realistis dapat dieksplorasi tanpa membahayakan kilang?
- **Bukti Diperlukan:** Penetapan formula refrigeran stabil Kandidat R berbasis median data kromatografi ($D_M \approx 0,45$, jauh di bawah batas kritis $3,0802$); analisis penyesuaian adaptif laju sirkulasi MCR saat turndown mendekati batas anti-surge ($480,0\text{ t/jam}$) via modulasi terkontrol valve kickback 4UV-53; potensi reduksi daya poros mekanikal 1,92% (13,92 GWh/tahun) dengan probabilitas pelanggaran temperatur jepit yang sangat rendah ($P_{\text{viol}} = 4,57\% \le 5,0\%$).
- **Gambar/Tabel:** Matriks evaluasi skenario operasional dan perbandingan domain risiko.
- **Kesimpulan Subtopik:** Peluang efisiensi realistis terletak pada penyesuaian adaptif sirkulasi MCR saat turndown yang dipandu oleh batas keselamatan anti-surge kompresor.

### 3.6 Implikasi Energi, Ekonomi, dan Lingkungan (Sensitivitas Bersyarat)
- **Tujuan:** Menyajikan analisis dampak utilitas, finansial, dan dekarbonisasi secara kondisional (*conditional sensitivity*).
- **Pertanyaan Dijawab:** Berapa nilai penghematan utilitas yang berpotensi diraih jika kendala termodinamika berhasil divalidasi di lapangan?
- **Bukti Diperlukan:** Rekonsiliasi neraca uap tahunan: uap total $3.172,83\text{ kt/tahun}$ vs uap turbin $2.935,90\text{ kt/tahun}$ (selisih 7,47% untuk balancing dan pompa); analisis sensitivitas penghematan uap terhadap konsumsi bahan bakar boiler ($77,04\text{ s.d. } 97,70\text{ Nm}^3/\text{ton uap}$); valuasi finansial pada tiga paritas: internal steam (USD 8,50/t), fuel gas boiler (USD 6,50/MMBtu), dan ekspor LNG (USD 10,50–11,50/MMBtu); potensi reduksi emisi $CO_2$ Scope 1 (faktor stoikiometri $164,4\text{ kg/t}$ vs IPCC $56,1\text{ kg/GJ}$).
- **Gambar/Tabel:** Tabel Matriks Sensitivitas Tekno-Ekonomi & Emisi Karbon.
- **Kesimpulan Subtopik:** Penghematan utilitas menawarkan nilai ekonomi dan dekarbonisasi yang signifikan, namun realisasinya bergantung penuh pada keberhasilan kualifikasi fisik di lapangan.

### 3.7 Implikasi Operasi Kilang, Manajemen Risiko, dan Peta Jalan Kualifikasi Lapangan (Path B Mandate)
- **Tujuan:** Merumuskan panduan praktis dan langkah-langkah terukur bagi tim operasi PT Badak NGL untuk menguji kelayakan strategi optimasi secara bertahap.
- **Pertanyaan Dijawab:** Apa yang harus dilakukan oleh insinyur proses dan operator kilang sebelum mengubah resep refrigeran di DCS?
- **Bukti Diperlukan:** Prosedur kualifikasi 4 tahap: (1) Validasi instrumentasi online analyzer dan flowmeter; (2) Uji coba pemangkasan sirkulasi MCR bertahap saat turndown dengan monitoring getaran kompresor dan bukaan valve kickback 4UV-53; (3) Uji penyesuaian komposisi mikro-injeksi (laju make-up $\le 0,5\text{ t/jam}$, ramp suhu $\le 0,10^\circ\text{C/menit}$) untuk menghindari thermal shock pada tabung MCHE; (4) Penguatan knowledge management melalui integrasi model surrogate mekanikal sebagai *advisory decision-support* di Yokogawa Centum VP.
- **Gambar/Tabel:** Diagram Alir Peta Jalan Kualifikasi Lapangan (*Field Qualification Protocol*).
- **Kesimpulan Subtopik:** Pendekatan rekayasa yang disiplin mengutamakan keselamatan proses dan keandalan pabrik di atas klaim efisiensi yang tergesa-gesa.

---

## 5. DETAIL PER SUBBAB: KESIMPULAN (SECTION 4)

### 4.1 Kesimpulan Utama Penelitian
- **Tujuan:** Merangkum temuan ilmiah substantif yang telah dibuktikan secara jujur dan transparan.
- **Poin Kesimpulan:**
  1. *Karakterisasi Baseline & Penalti Turndown:* Terbukti secara empiris pada data DCS 2024–2026 bahwa penurunan laju umpan 32,7% memicu kenaikan SEC sebesar +12,7% akibat kekakuan batas anti-surge kompresor sentrifugal MCR ($\ge 480\text{ t/jam}$) dan interlock suhu hisap drum (TAL $\ge -45^\circ\text{C}$).
  2. *Pemetaan Geometri Simpleks:* Transformasi ILR 4-DoF terbukti berhasil memetakan 2.531 sampel kromatografi gas ke dalam ruang Euclidean tak terbias, di mana batasan elipsoid Mahalanobis ($D_M \le 3,0802$) secara efektif membatasi ruang operasi yang realistis.
  3. *Evaluasi Kritis Machine Learning:* Model surrogate HGBR berfitur monotonik terbukti sangat unggul dalam memprediksi daya kompresor ($R^2 = 0,9557$, MAE 0,82 MW) dan uap penggerak ($R^2 = 0,9997$), namun model tabular empiris terbukti gagal total dalam memprediksi pendekatan termal internal MCHE (menghasilkan nilai beku $7,17^\circ\text{C}$).
  4. *Integritas Termodinamika & Batas Riset (Path B):* Evaluasi PR-EOS 100-slice membuktikan bahwa penutupan neraca energi MCHE menyisakan residual $-4,3\%$ hingga $+15,3\%$, sehingga optimasi komersial instan belum dapat dikualifikasi secara penuh tanpa pengujian bertahap di lapangan.

### 4.2 Rekomendasi Rekayasa dan Knowledge Management
- **Tujuan:** Memberikan rekomendasi strategis bagi PT Badak NGL dan industri LNG nasional.
- **Poin Rekomendasi:**
  1. Mengadopsi model surrogate mekanikal kompresor sebagai sistem pemantauan efisiensi dan *advisory* pada DCS Yokogawa Centum VP.
  2. Melaksanakan uji coba operasional terencana (*planned operational trial*) untuk memvalidasi fraksi distribusi dua-fase MCHE dan beban subcooler 4E-40.
  3. Menerapkan protokol injeksi refrigeran konservatif dengan batasan gradien termal ketat demi menjaga integritas mekanikal penukar panas kriogenik.

---
*Dokumen outline ini telah tuntas diverifikasi dan menjadi acuan mutlak untuk penyusunan manuskrip lengkap IKMS_FULLPAPER_REWRITTEN.md (Stage 5).*
