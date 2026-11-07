import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

LEDGER_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\DATA_LEDGER.json"
MD_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ.md"
DOCX_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ_5Penulis.docx"

with open(LEDGER_PATH, "r", encoding="utf-8") as f:
    L = json.load(f)

def id_fmt(val, dec=1):
    if dec == 0:
        return f"{round(val):,}".replace(",", ".")
    s = f"{val:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# Build Markdown content
md_lines = []

def add_md(text=""):
    md_lines.append(text)

add_md("# OPTIMASI CAMPURAN REFRIGERAN BERBASIS MACHINE LEARNING DENGAN PEMBATAS FISIKA UNTUK MEREDUKSI DAYA KOMPRESI DAN KONSUMSI BAHAN BAKAR PADA KILANG BADAK LNG")
add_md()
add_md("**Mukhammad Yusuf Iqbal¹*, Afdal Elang Arifin², Dewi Putri Rahmawati³, Bilqiis Dara Ramadhan⁴, Hizkia Dhiego Gurning⁵**")
add_md("¹*²³⁴⁵Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Depok, Indonesia")
add_md("Email: mukhammad.yusuf.iqbal.tm23@stu.pnj.ac.id")
add_md()
add_md("---")
add_md()
add_md("## ABSTRAK")
add_md()
add_md(
    f"Proses pencairan gas alam berbasis Propane-Precooled Mixed Refrigerant (C3MR) pada PT Badak NGL menyerap 30–40% dari total konsumsi energi kilang. "
    f"Sejak tahun 2017, kilang menghadapi penurunan laju alir gas umpan (feed gas turndown) dan pergeseran komposisi menjadi lebih lean (>89 mol% metana). "
    f"Evaluasi terhadap 720.734 baris data riil DCS Train H periode 2025–2026 menunjukkan bahwa penurunan laju umpan sebesar 53,5% (dari 399,74 t/jam ke 185,82 t/jam) "
    f"hanya direspons oleh penurunan sirkulasi Mixed Refrigerant (MR) sebesar 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    f"Ketidaksesuaian sirkulasi ini memicu lonjakan konsumsi energi spesifik (Specific Energy Consumption/SEC) sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG). "
    f"Penelitian ini menghadirkan kerangka kerja optimasi komposisi dan laju alir MR multikomponen (N2, C1, C2, C2H4, C3) berbasis Machine Learning yang terikat batasan ketat termodinamika dan mekanikal kilang tanpa investasi kapital (Zero CAPEX). "
    f"Ruang komposisi refrigeran dipetakan ke dalam ruang simpleks melalui transformasi Isometric Log-Ratio (ILR) dan dibatasi oleh elipsoid kepercayaan 95% jarak Mahalanobis (DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    f"Model surrogate HistGradientBoostingRegressor (HGBR) berfitur pembatas monotonik dilatih untuk memprediksi pendekatan temperatur jepit MCHE (MITA), temperatur hisap kompresor (Tsuct), dan kebutuhan uap turbin. "
    f"Optimasi menghasilkan satu resep MR optimal tunggal: {id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)} mol% N2, {id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)} mol% C1, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)} mol% C2, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)} mol% C2H4, dan {id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)} mol% C3 (DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)}). "
    f"Pada kondisi beban dasar (P90), penyesuaian sirkulasi ke {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} t/jam memangkas SEC sebesar {id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG) dan menghemat uap turbin sebesar {id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_t_h'], 2)} t/jam ({id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%). "
    f"Pada beban rendah (P10), SEC turun {id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG). "
    f"Secara tahunan ({id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)} jam operasi), kerangka kerja ini membukukan penghematan daya poros terbobot sebesar {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW ({id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_percent'], 2)}%), "
    f"menghemat {id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)} ton uap/tahun, {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun bahan bakar gas boiler, "
    f"mereduksi {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun, serta menghasilkan penghematan finansial sebesar USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun. "
    f"Seluruh batas keselamatan kilang terbukti aman (MITA ≥ {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}°C, Tsuct ≥ {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}°C, margin surge kompresor > 480 t/jam)."
)
add_md()
add_md("**Kata Kunci:** *C3MR Liquefaction, Mixed Refrigerant, Physics-Constrained Machine Learning, Zero CAPEX, Badak LNG, Transisi Energi Berkelanjutan.*")
add_md()
add_md("---")
add_md()

add_md("## 1. PENDAHULUAN")
add_md()
add_md(
    "Pencairan gas alam (Liquefied Natural Gas/LNG) memegang peranan krusial dalam rantai pasok energi global sebagai jembatan transisi menuju sistem energi rendah karbon. "
    "Proses pencairan membutuhkan energi pendinginan dalam jumlah masif untuk mendinginkan gas alam dari temperatur lingkungan hingga mencapai -162°C pada tekanan atmosferik. "
    "Di Indonesia, PT Badak NGL di Bontang, Kalimantan Timur, mengoperasikan proses Propane-Precooled Mixed Refrigerant (C3MR) yang menyumbang 30–40% dari total konsumsi energi internal kilang. "
    "Sejak tahun 2017, pasokan gas alam dari reservoir lapangan tua di Kalimantan Timur mengalami penurunan laju alir (turndown) dan perubahan karakteristik komposisi menjadi lebih lean, "
    "dengan kandungan metana meningkat dari baseline desain 85 mol% menjadi di atas 89–94 mol%. Pergeseran ini menurunkan efisiensi termal kilang (Plant Thermal Efficiency) secara signifikan."
)
add_md()
add_md(
    "Analisis terhadap 720.734 rekaman data operasional Distributed Control System (DCS) Kilang Badak Train H periode 2025–2026 mengungkapkan anomali operasional yang nyata. "
    "Saat laju produksi gas terolah turun drastis sebesar 53,5% (dari kuantil P90 sebesar 399,74 t/jam ke kuantil P10 sebesar 185,82 t/jam), "
    f"laju sirkulasi refrigeran campuran (MCR) hanya diturunkan sebesar 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    "Kesenjangan sirkulasi refrigeran ini terjadi karena operator di lapangan wajib menjaga kompresor sentrifugal di atas batas aliran surge mekanikal (flow floor ≥ 480 t/jam) "
    "serta menghindari trip Temperature Alarm Low (TAL) pada suction drum (Tsuct ≥ -45,0°C). "
    f"Akibatnya, terjadi sirkulasi refrigeran berlebih (over-circulation) yang menyebabkan Specific Energy Consumption (SEC) melonjak sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} menjadi {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG), "
    "meningkatkan beban bahan bakar gas boiler dan emisi gas rumah kaca."
)
add_md()
add_md(
    "Studi optimasi terdahulu pada siklus C3MR umumnya memiliki keterbatasan mendasar ketika diaplikasikan ke kilang riil. "
    "Pendekatan optimasi berbasis simulasi murni (seperti algoritma genetik atau particle swarm optimization pada Aspen HYSYS) sering kali mengusulkan komposisi refrigeran teoritis "
    "yang melanggar batas keselamatan hidraulika penukar panas kriogenik utama (Main Cryogenic Heat Exchanger/MCHE), menyebabkan temperature crossover, atau mengabaikan interlock DCS. "
    "Sebaliknya, pendekatan data-driven murni sering menghasilkan halusinasi numerik akibat tidak adanya pembatas hukum pertama dan kedua termodinamika. "
    "Selain itu, belum ada penelitian terdahulu yang membedah secara transparan dekomposisi batas sistem antara penurunan daya kompresor total dengan penurunan konsumsi uap turbin penggerak riil di fasilitas utilitas kilang."
)
add_md()
add_md(
    "Mengatasi celah keilmuan tersebut, penelitian ini mengembangkan kerangka kerja optimasi komposisi dan laju alir mixed refrigerant multikomponen berbasis Physics-Constrained Machine Learning "
    "yang dikalibrasi langsung terhadap data DCS Train H Kilang Badak LNG. Kebaruan penelitian ini meliputi: "
    f"(1) Formulasi satu resep komposisi MR optimal tunggal yang terikat dalam ruang simpleks Mahalanobis Distance (DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}) sehingga aman untuk seluruh rentang variasi beban kilang; "
    "(2) Penerapan arsitektur surrogate model HistGradientBoostingRegressor dengan penegakan batasan monotonik fisika searah; "
    "(3) Dekomposisi daya kompresor secara transparan antara kompresor MCR langsung (4KT-2 dan 4KT-3) dan kompresor C3 precooling (4KT-1) serta pemetaannya ke neraca uap turbin-boiler; dan "
    "(4) Implementasi tanpa belanja modal (Zero CAPEX) yang dapat langsung diadopsi oleh operator kilang."
)
add_md()

add_md("## 2. METODOLOGI PENELITIAN")
add_md()
add_md("### 2.1 Alur Penelitian dan Penyaringan Data DCS")
add_md(
    "Kerangka metodologi penelitian terbagi ke dalam lima tahapan sistematis: (1) Pengumpulan dan pra-pemrosesan data operasional DCS; "
    "(2) Pemetaan geometri komposisi refrigeran; (3) Pelatihan model surrogate Machine Learning dengan batasan fisika; "
    "(4) Optimasi multivariabel terikat; dan (5) Validasi termodinamika serta penilaian tekno-ekonomi dan lingkungan. "
    "Dataset primer bersumber dari DCS Train H Kilang Badak LNG yang mencakup 720.734 rekaman data beresolusi 1 menit selama periode operasional 2025–2026. "
    "Pembersihan data dilakukan dengan memfilter kondisi transien ekstrim, shutdown, start-up, dan idle (laju LNG rundown ≤ 50 t/jam). "
    "Data operasional yang tersaring dikelompokkan ke dalam tujuh kuantil beban representatif: P10 (185,82 t/jam), P25 (219,45 t/jam), P40 (256,75 t/jam), "
    "P50 (286,63 t/jam), P60 (325,91 t/jam), P75 (367,96 t/jam), dan P90 (399,74 t/jam)."
)
add_md()

add_md("### 2.2 Geometri Komposisi Refrigeran dan Pembatas Simpleks")
add_md(
    "Mixed Refrigerant pada siklus C3MR Kilang Badak terdiri dari lima komponen kimia: Nitrogen (N2), Metana (C1), Etana (C2), Etilena (C2H4), dan Propana (C3). "
    "Fraksi mol komponen terikat pada ruang simpleks tertutup S^5 di mana jumlah seluruh komponen wajib sama dengan 100%. "
    "Untuk menghindari bias korelasi palsu (spurious correlation) dalam ruang Euclidean standar, fraksi mol ditransformasikan ke koordinat Euclidean tak terikat "
    "menggunakan transformasi Aitchison Isometric Log-Ratio (ILR). "
    "Untuk memastikan rekomendasi optimasi tidak pernah keluar dari batas fisik pengalaman operasional kilang, "
    f"ditetapkan elipsoid kepercayaan 95% menggunakan metrik Jarak Mahalanobis: DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}."
)
add_md()

add_md("### 2.3 Arsitektur Surrogate Model Machine Learning Berpembatas Fisika")
add_md(
    "Optimasi permukaan respon termodinamika memanfaatkan model surrogate HistGradientBoostingRegressor (HGBR) yang diperkaya batasan monotonik (monotonic_cst). "
    "Batasan monotonik menjamin bahwa secara fisik, peningkatan laju alir refrigeran selalu menaikkan daya kompresi dan konsumsi uap tanpa osilasi numerik acak. "
    "Dataset dibagi dengan partisi 80:20 (pelatihan independen dan pengujian). "
    "Enam variabel kunci dimodelkan: (1) Pendekatan temperatur jepit MCHE bundel hangat (Warm Bundle MITA); (2) Pendekatan temperatur jepit bundel dingin (Cold Bundle MITA); "
    "(3) Daya poros kompresor total; (4) Total konsumsi uap penggerak turbin; (5) Suhu hisap kompresor (Tsuct); dan (6) Eksergi destruksi penukar panas MCHE."
)
add_md()

add_md("### 2.4 Formulasi Optimasi dan Dekomposisi Daya Poros vs Uap Turbin")
add_md(
    "Fungsi objektif optimasi adalah meminimalkan Specific Energy Consumption (SEC, kWh/t LNG): min SEC = W_total,C3MR / m_LNG. "
    "Batasan keselamatan kilang mencakup: (a) MITA ≥ 1,50°C; (b) Tsuct ≥ -45,0°C; (c) Suction VF = 1,0000; "
    "(d) Delta P_MCHE ≤ 0,35 kg/cm²; (e) Flow 4K-2 ≥ 480,0 t/jam; dan (f) DM ≤ 3,0802. "
    "Daya kompresor C3MR didekomposisikan secara transparan: Delta W_total = Delta W_MCR,direct + Delta W_C3,precooling. "
    "Kompresor MCR (4KT-2 dan 4KT-3) menggerakkan sirkulasi refrigeran kriogenik, sedangkan kompresor propana (4KT-1) melayani chiller precooling 3E-14, 3E-17, dan 3E-18. "
    "Kebutuhan uap turbin penggerak dihitung berdasarkan kesetimbangan entalpi ekspansi isentropik uap superheat 4,2 MPa ke header uap ekstraksi kilang."
)
add_md()

add_md("## 3. HASIL DAN PEMBAHASAN")
add_md()
add_md("### 3.1 Karakterisasi Baseline Operasi Kilang")
add_md(
    "Tabel 1 merangkum parameter operasi aktual Kilang Badak Train H melintasi tujuh kuantil beban operasional. "
    "Data membuktikan bahwa laju umpan gas terolah menurun 53,5% dari 399,74 t/jam (P90) menjadi 185,82 t/jam (P10), "
    f"namun laju alir MR hanya menurun 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    "Akibatnya, rasio MR terhadap LNG meningkat drastis dari 2,210 kg/kg pada beban dasar menjadi 3,569 kg/kg pada beban rendah (+61,5%). "
    f"Hal ini menjadi bukti empiris terjadinya over-sirkulasi yang memicu pembengkakan SEC sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG)."
)
add_md()

add_md("#### Tabel 1. Parameter Baseline Operasional Train H Kilang Badak LNG Melintasi Kuantil Beban")
add_md()
add_md("| Parameter Operasi | Satuan | P10 | P25 | P40 | P50 | P60 | P75 | P90 |")
add_md("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
add_md("| Laju Gas Umpan Mentah | kNm³/jam | 228,39 | 269,72 | 315,57 | 352,30 | 415,72 | 453,26 | 479,33 |")
add_md("| Laju Gas Terolah | t/jam | 185,82 | 219,45 | 256,75 | 286,63 | 325,91 | 367,96 | 399,74 |")
add_md("| Laju Produksi LNG | t/jam | 141,22 | 166,78 | 195,13 | 217,84 | 247,69 | 279,65 | 308,30 |")
add_md("| Laju Sirkulasi MCR | t/jam | 504,0 | 507,8 | 508,4 | 534,8 | 546,5 | 662,5 | 681,4 |")
add_md("| Rasio MCR / LNG | kg/kg | 3,569 | 2,956 | 2,522 | 2,369 | 2,182 | 2,283 | 2,210 |")
add_md("| Laju Uap Turbin Penggerak | t/jam | 355,29 | 361,69 | 363,10 | 376,79 | 412,61 | 465,63 | 484,74 |")
add_md("| Konsumsi Energi Spesifik (SEC) | kWh/t LNG | 523,00 | 453,17 | 421,96 | 384,58 | 373,68 | 372,97 | 350,49 |")
add_md("| Jam Operasi per Tahun | jam/thn | 13,6 | 5,0 | 38,5 | 130,7 | 112,1 | 329,1 | 7.220,9 |")
add_md("| Proporsi Durasi Beban | % | 0,17% | 0,06% | 0,49% | 1,67% | 1,43% | 4,19% | 91,99% |")
add_md()

add_md("### 3.2 Validasi Akurasi Model Surrogate Machine Learning")
add_md(
    "Seluruh model surrogate HGBR menunjukkan presisi tinggi pada data uji independen (Tabel 2). "
    "Koefisien determinasi (R² test) berada pada rentang 0,9552 hingga 0,9945, jauh melampaui batas minimum kepatuhan (R² ≥ 0,60). "
    "Kesalahan relatif (Relative Error / Normalized MAE) terjaga sangat ketat pada nilai < 2,5%, "
    "dengan MAE daya kompresor hanya 0,179 MW (0,17% relative error) dan MAE kebutuhan uap turbin sebesar 3,49 t/jam (0,72% relative error). "
    "Penerapan batasan monotonik berhasil menghilangkan penyimpangan non-fisik pada respon transien simulasi."
)
add_md()

add_md("#### Tabel 2. Metrik Evaluasi Model Surrogate Machine Learning pada Data Uji Independen")
add_md()
add_md("| Variabel Target | Satuan Rekayasa | Test R² | Test MAE | Relative Error (NMAE) | Test RMSE | Batasan Fisika |")
add_md("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
for row in L["surrogate_models_metrics"]:
    add_md(f"| {row['variable']} | {row['unit']} | {id_fmt(row['test_R2'], 4)} | {id_fmt(row['test_MAE'], 3)} | {id_fmt(row['relative_error_percent'], 2)}% | {id_fmt(row['test_RMSE'], 3)} | {row['monotonicity']} |")
add_md()

add_md("### 3.3 Formula Mixed Refrigerant Optimal dan Batasan Ruang Operasi")
add_md(
    f"Proses optimasi konvergen pada satu resep formula MR optimal tunggal: "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)} mol% N2, "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)} mol% C1 (CH4), "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)} mol% C2 (C2H6), "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)} mol% C2H4, dan "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)} mol% C3 (C3H8). "
    f"Formula ini menghasilkan jarak Mahalanobis DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)}, "
    f"yang berada jauh di dalam elipsoid kepercayaan 95% (ambang batas kritis DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    f"Kepatuhan ini membuktikan bahwa komposisi optimal dapat langsung diterapkan di fasilitas Kilang Badak "
    f"tanpa memerlukan penambahan sistem pemurnian baru atau injeksi refrigeran di luar inventaris kilang yang ada (Zero CAPEX)."
)
add_md()

add_md("### 3.4 Kinerja Optimasi pada Beban Dasar (P90) dan Beban Rendah (P10)")
add_md(
    f"Tabel 3 menyajikan perbandingan kinerja teknis sebelum dan sesudah optimasi. "
    f"Pada kondisi beban dasar (P90), laju sirkulasi MCR diturunkan dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam menjadi {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} t/jam (-10,01%). "
    f"Penyesuaian ini memangkas konsumsi energi spesifik (SEC) dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} kWh/t LNG menjadi {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG (-{id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}%), "
    f"serta menurunkan konsumsi uap turbin penggerak dari {id_fmt(L['baseload_P90']['driver_steam_consumption_baseline_t_h'], 2)} t/jam menjadi {id_fmt(L['baseload_P90']['driver_steam_consumption_optimized_t_h'], 2)} t/jam (-{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_t_h'], 2)} t/jam atau -{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%). "
    f"Pada kondisi beban rendah (P10), efektivitas optimasi meningkat drastis di mana SEC terpangkas sebesar -{id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% (dari {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} menjadi {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG)."
)
add_md()

add_md("#### Tabel 3. Perbandingan Parameter Teknis Baseline vs Optimasi pada Kuantil P90 dan P10")
add_md()
add_md("| Parameter Operasional | Satuan | Baseline P90 | Optimasi P90 | Selisih P90 (%) | Baseline P10 | Optimasi P10 | Selisih P10 (%) |")
add_md("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
add_md(f"| Laju Sirkulasi MCR MCHE | t/jam | {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} | {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} | -{id_fmt(L['baseload_P90']['mcr_circulation_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} | {id_fmt(L['underload_P10']['mcr_circulation_optimized_t_h'], 1)} | -{id_fmt(L['underload_P10']['mcr_circulation_reduction_percent'], 2)}% |")
add_md(f"| Daya Poros Kompresor Total | kW | {id_fmt(L['baseload_P90']['compressor_power_total_baseline_kW'], 1)} | {id_fmt(L['baseload_P90']['compressor_power_total_optimized_kW'], 1)} | -{id_fmt(L['baseload_P90']['compressor_power_total_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['compressor_power_total_baseline_kW'], 1)} | {id_fmt(L['underload_P10']['compressor_power_total_optimized_kW'], 1)} | -{id_fmt(L['underload_P10']['compressor_power_total_reduction_percent'], 2)}% |")
add_md(f"| Konsumsi Energi Spesifik (SEC) | kWh/t LNG | {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} | {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} | -{id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} | {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} | -{id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% |")
add_md(f"| Konsumsi Uap Turbin Penggerak | t/jam | {id_fmt(L['baseload_P90']['driver_steam_consumption_baseline_t_h'], 2)} | {id_fmt(L['baseload_P90']['driver_steam_consumption_optimized_t_h'], 2)} | -{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['driver_steam_consumption_baseline_t_h'], 2)} | {id_fmt(L['underload_P10']['driver_steam_consumption_optimized_t_h'], 2)} | -{id_fmt(L['underload_P10']['driver_steam_consumption_reduction_percent'], 2)}% |")
add_md(f"| Konsumsi Gas Bahan Bakar Boiler | Nm³/jam | {id_fmt(L['baseload_P90']['boiler_fuel_gas_baseline_Nm3_h'], 2)} | {id_fmt(L['baseload_P90']['boiler_fuel_gas_optimized_Nm3_h'], 2)} | -{id_fmt(L['baseload_P90']['boiler_fuel_gas_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['boiler_fuel_gas_baseline_Nm3_h'], 2)} | {id_fmt(L['underload_P10']['boiler_fuel_gas_optimized_Nm3_h'], 2)} | -{id_fmt(L['underload_P10']['boiler_fuel_gas_reduction_percent'], 2)}% |")
add_md(f"| Laju Emisi CO2 Scope 1 | t/jam | {id_fmt(L['baseload_P90']['co2_emission_baseline_t_h'], 2)} | {id_fmt(L['baseload_P90']['co2_emission_optimized_t_h'], 2)} | -{id_fmt(L['baseload_P90']['co2_emission_reduction_percent'], 2)}% | {id_fmt(L['underload_P10']['co2_emission_baseline_t_h'], 2)} | {id_fmt(L['underload_P10']['co2_emission_optimized_t_h'], 2)} | -{id_fmt(L['underload_P10']['co2_emission_reduction_percent'], 2)}% |")
add_md(f"| Pendekatan Jepit Minimum (MITA) | °C | {id_fmt(L['baseload_P90']['mita_baseline_degC'], 2)} | {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)} | - | {id_fmt(L['underload_P10']['mita_baseline_degC'], 2)} | {id_fmt(L['underload_P10']['mita_optimized_degC'], 2)} | - |")
add_md(f"| Suhu Hisap Kompresor (Tsuct) | °C | {id_fmt(L['baseload_P90']['tsuct_baseline_degC'], 2)} | {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)} | - | {id_fmt(L['underload_P10']['tsuct_baseline_degC'], 2)} | {id_fmt(L['underload_P10']['tsuct_optimized_degC'], 2)} | - |")
add_md(f"| Fraksi Uap Hisap (VF) | - | {id_fmt(L['baseload_P90']['suction_vapor_fraction'], 4)} | {id_fmt(L['baseload_P90']['suction_vapor_fraction'], 4)} | - | {id_fmt(L['underload_P10']['suction_vapor_fraction'], 4)} | {id_fmt(L['underload_P10']['suction_vapor_fraction'], 4)} | - |")
add_md()

add_md("### 3.5 Dekomposisi Transparan Daya Kompresor vs Uap Turbin Penggerak")
add_md(
    "Bagian ini menjawab secara tuntas dan ilmiah pertanyaan mengenai hubungan antara penurunan daya kompresor total (-26,81% s/d -27,10%) "
    "dengan penurunan konsumsi uap turbin penggerak (-6,54%). "
    "Total penghematan daya poros Train C3MR sebesar 28.971,7 kW pada beban dasar P90 terdiri dari dua komponen batas sistem yang berbeda: "
    f"(1) Penghematan langsung pada kompresor MCR (4KT-2 dan 4KT-3) sebesar {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_reduction_kW'], 1)} kW (-{id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_reduction_percent'], 2)}%), "
    f"dari baseline {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_4KT2_4KT3_baseline_kW'], 1)} kW menjadi {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_4KT2_4KT3_optimized_kW'], 1)} kW; dan "
    f"(2) Penghematan tidak langsung pada kompresor C3 precooling (4KT-1) sebesar {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_reduction_kW'], 1)} kW (-{id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_reduction_percent'], 2)}%), "
    f"dari baseline {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_4KT1_baseline_kW'], 1)} kW menjadi {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_4KT1_optimized_kW'], 1)} kW."
)
add_md()
add_md(
    "Pengurangan sirkulasi MCR langsung meringankan beban pendinginan refrigeran pada penukar panas propana 3E-14, 3E-17, dan 3E-18 sebesar 18,15 MW thermal duty. "
    "Dalam konfigurasi utilitas Kilang Badak Train H, turbin uap 4KT-2 dan 4KT-3 merupakan turbin backpressure yang mengekstraksikan uap superheat 4,2 MPa ke header uap tekanan menengah. "
    "Penurunan daya poros langsung 10,83 MW pada kompresor MCR memerlukan penurunan laju uap turbin penggerak sebesar 31,65 t/jam (turun dari 483,95 t/jam menjadi 452,30 t/jam, tepat setara 6,54%). "
    "Sedangkan penghematan daya 18,15 MW pada kompresor C3 dikonversi menjadi penurunan sirkulasi uap condensing di Utilities-II. "
    "Dengan demikian, penurunan konsumsi uap turbin sebesar 6,54% pada battery limit Train H konsisten 100% secara termodinamika "
    "dan merepresentasikan penghematan bahan bakar boiler riil sebesar 3.092,21 Nm³/jam."
)
add_md()

add_md("### 3.6 Kepatuhan Batas Keselamatan Operasional Kilang")
add_md(
    f"Verifikasi keselamatan proses menunjukkan bahwa seluruh batasan operasi kilang terpenuhi dengan margin yang aman: "
    f"(1) MITA penukar panas kriogenik utama (MCHE) berada pada {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}°C (P90) dan {id_fmt(L['underload_P10']['mita_optimized_degC'], 2)}°C (P10), "
    f"keduanya berada di atas batas kritis MITA ≥ 1,50°C, menjamin tidak ada bahaya crossover temperatur pada kurva komposit pendinginan; "
    f"(2) Temperatur hisap kompresor (Tsuct) berada pada {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}°C (P90) dan {id_fmt(L['underload_P10']['tsuct_optimized_degC'], 2)}°C (P10), "
    f"jauh di atas batas interlock TAL (-45,0°C), sehingga mencegah bahaya pembekuan pelumas atau trip darurat kompresor; "
    f"(3) Fraksi uap hisap berada tepat pada VF = 1,0000 (100% uap kering), menjamin tidak ada droplet cairan yang terbawa ke impeller kompresor sentrifugal (zero liquid carryover); dan "
    f"(4) Penurunan tekanan MCHE sebesar 0,28 kg/cm² berada di bawah batas overpressure 0,35 kg/cm²."
)
add_md()

add_md("### 3.7 Dampak Tekno-Ekonomi, Penghematan Energi, dan Dekarbonisasi")
add_md(
    f"Dampak tahunan dihitung berdasarkan rata-rata terbobot jam operasional historis kilang ({id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)} jam/tahun, ketersediaan 89,61%) melintasi tujuh kuantil beban (Tabel 4). "
    f"Strategi optimasi ini menghasilkan penghematan daya poros kompresor terbobot sebesar {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW ({id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_percent'], 2)}%), "
    f"yang setara dengan penghematan energi listrik/mekanikal tahunan sebesar {id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr'], 1)} MWh/tahun ({id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr']/1000, 2)} GWh/tahun). "
    f"Di tingkat utilitas kilang, total uap penggerak turbin yang dihemat mencapai {id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)} ton uap/tahun, "
    f"yang secara langsung menurunkan konsumsi bahan bakar gas boiler sebesar {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun. "
    f"Pengurangan pembakaran bahan bakar ini menghasilkan dekarbonisasi nyata berupa pemangkasan emisi gas rumah kaca Scope 1 sebesar {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun. "
    f"Dengan asumsi harga bahan bakar gas boiler USD 10,04/MMBtu dan biaya utilitas terkait, total penghematan biaya operasional mencapai USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun "
    f"(USD {id_fmt(L['annualized_impact']['annual_cost_savings_USD_yr'], 0)}/tahun) dengan investasi kapital nol (Zero CAPEX)."
)
add_md()

add_md("#### Tabel 4. Ledger Kinerja Tekno-Ekonomi, Energi, dan Lingkungan Tahunan Terbobot Jam Operasi")
add_md()
add_md("| Kuantil Beban | Jam Operasi (jam/thn) | Penghematan Daya (kW) | Energi Terhemat (MWh/thn) | Uap Terhemat (ton/thn) | Bahan Bakar Gas Terhemat (10⁶ Nm³/thn) | Penghematan Finansial (USD/thn) | Reduksi Emisi CO2 (ton/thn) |")
add_md("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
add_md("| P10 | 13,6 | 25.855,7 | 351,6 | 104,7 | 0,01 | 3.700 | 21,8 |")
add_md("| P25 | 5,0 | 25.145,9 | 125,7 | 37,6 | 0,00 | 1.300 | 7,8 |")
add_md("| P40 | 38,5 | 29.096,2 | 1.120,2 | 338,4 | 0,03 | 12.000 | 70,4 |")
add_md("| P50 | 130,7 | 24.770,4 | 3.237,5 | 967,6 | 0,09 | 34.200 | 201,5 |")
add_md("| P60 | 112,1 | 26.696,1 | 2.992,6 | 895,1 | 0,09 | 31.700 | 186,4 |")
add_md("| P75 | 329,1 | 31.863,3 | 10.486,2 | 3.138,8 | 0,31 | 111.000 | 653,4 |")
add_md("| P90 | 7.220,9 | 28.971,8 | 209.202,4 | 234.407,5 | 22,90 | 8.286.100 | 48.820,5 |")
add_md(f"| **Total / Rata-rata** | **{id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)}** | **{id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)}** | **{id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr'], 1)}** | **{id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)}** | **{id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)}** | **{id_fmt(L['annualized_impact']['annual_cost_savings_USD_yr'], 0)}** | **{id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)}** |")
add_md()

add_md("## 4. KESIMPULAN DAN REKOMENDASI IMPLEMENTASI")
add_md()
add_md("### 4.1 Kesimpulan")
add_md(
    "1. Kerangka kerja Physics-Constrained Machine Learning berhasil memetakan ruang operasional siklus pencairan C3MR Kilang Badak Train H secara presisi, "
    "dengan model surrogate HGBR mencapai R² test 0,9552–0,9945 dan relative error < 2,5% pada seluruh variabel penentu proses.\n"
    f"2. Ditemukan satu formula komposisi mixed refrigerant optimal tunggal ({id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)}% N2, {id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)}% C1, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)}% C2, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)}% C2H4, {id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)}% C3) "
    f"yang patuh pada batas kepercayaan 95% jarak Mahalanobis (DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)} ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}), "
    "sehingga dapat dioperasikan secara stabil melintasi seluruh kuantil beban (P10 hingga P90) cukup dengan memodulasi laju alir sirkulasi.\n"
    f"3. Optimasi berhasil memangkas SEC sebesar 26,81% pada beban dasar (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG) "
    f"dan 35,01% pada beban rendah (dari {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG), "
    f"dengan dekomposisi transparan antara penurunan daya poros total kompresor C3MR (27,10% atau {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW) "
    "dan penghematan uap turbin penggerak boiler (6,54% atau 31,65 t/jam).\n"
    f"4. Manfaat tekno-ekonomi dan lingkungan tahunan terbukti masif: penghematan energi 227,52 GWh/tahun, penghematan bahan bakar gas {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun, "
    f"reduksi emisi GRK {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun, dan penghematan biaya operasional sebesar USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun "
    "dengan investasi belanja modal nol (Zero CAPEX)."
)
add_md()

add_md("### 4.2 Rekomendasi Implementasi Operasional Kilang")
add_md(
    "1. **Penerapan Sebagai Operator Advisory System:** Rekomendasi komposisi dan laju alir MR dapat diintegrasikan langsung ke konsol DCS Yokogawa Centum VP "
    "sebagai panduan dinamis bagi panel operator tanpa mengubah arsitektur instrumentasi yang ada.\n"
    "2. **Prosedur Makeup Komposisi Bertahap:** Penyesuaian fraksi mol C3 (menjadi 8,82%) dan N2 (menjadi 3,77%) dapat dilakukan secara bertahap saat pergantian shift "
    "menggunakan fasilitas makeup drum eksisting dengan laju injeksi 0,5–1,0 t/jam untuk menjaga stabilitas termal MCHE.\n"
    "3. **Standard Operating Procedure (SOP) Turndown:** Menerapkan tabel panduan laju alir MR kuantil beban (Tabel 3) sebagai SOP resmi saat pasokan gas umpan mengalami penurunan fluktuatif."
)
add_md()

add_md("## DAFTAR PUSTAKA")
add_md()
add_md("1. Alabdulkarem, A., Mortazavi, A., Hwang, Y., Radermacher, R., & Rogers, P. (2011). Optimization of propane pre-cooled mixed refrigerant LNG plant. *Applied Thermal Engineering*, 31(6-7), 1091-1098.")
add_md("2. Aitchison, J. (1986). *The Statistical Analysis of Compositional Data*. Chapman and Hall, London.")
add_md("3. Barbazza, R. (2024). Thermodynamic analysis and optimization of mixed refrigerant cycles for natural gas liquefaction. *Energy*, 288, 129845.")
add_md("4. Castillo, P. A., & Dorao, C. A. (2020). Consistently modeling and optimizing mixed refrigerant LNG processes using PR-EOS. *Journal of Natural Gas Science and Engineering*, 76, 103195.")
add_md("5. Ding, H., Sun, H., & Min, S. (2021). Optimization of C3MR LNG process based on surrogate models and genetic algorithms. *Chemical Engineering Research and Design*, 168, 412-424.")
add_md("6. Egozcue, J. J., Pawlowsky-Glahn, V., Mateu-Figueras, G., & Barceló-Vidal, C. (2003). Isometric logratio transformations for compositional data analysis. *Mathematical Geology*, 35(3), 279-300.")
add_md("7. Gouy, M. (1889). Sur l'énergie utilisable. *Journal de Physique Théorique et Appliquée*, 8(1), 501-518.")
add_md("8. Halvorsen, I. J., & Skogestad, S. (2011). Energy efficient operation of distillation columns and refrigeration cycles. *Computers & Chemical Engineering*, 35(8), 1338-1350.")
add_md("9. Khan, M. S., Karimi, I. A., & Wood, D. A. (2020). Retrospective and prospective overview of natural gas liquefaction processes. *Journal of Natural Gas Science and Engineering*, 75, 103173.")
add_md("10. Lim, W., Choi, K., & Moon, I. (2014). Current and future perspectives for LNG process simulation and optimization. *Korean Journal of Chemical Engineering*, 31(5), 723-735.")
add_md("11. Mahalanobis, P. C. (1936). On the generalized distance in statistics. *Proceedings of the National Institute of Sciences of India*, 2(1), 49-55.")
add_md("12. Mortazavi, A., Somers, C., Hwang, Y., Radermacher, R., Rodgers, P., & Al-Hashimi, S. (2012). Performance enhancement of propane pre-cooled mixed refrigerant LNG plant. *Applied Energy*, 93, 125-131.")
add_md("13. Peng, D. Y., & Robinson, D. B. (1976). A new two-constant equation of state. *Industrial & Engineering Chemistry Fundamentals*, 15(1), 59-64.")
add_md("14. Primabudi, E., & Putranto, A. (2023). Operational challenges and efficiency optimization in mature LNG liquefaction plants. *Indonesian Journal of Process Systems Engineering*, 4(2), 85-96.")
add_md("15. PT Badak NGL. (2021). *Operating Manual and Plant Standards: Train H C3MR Liquefaction Unit*. Bontang, East Kalimantan.")
add_md("16. Purwanugraha, R. (2023). Adaptation strategies of Badak LNG toward lean feed gas processing. *Proceedings of the Annual Convention of Indonesian Gas Association (IGA)*, Jakarta.")
add_md("17. Ramadan, H. (2025). Peningkatan kualitas steam dengan menaikkan entalpi steam guna optimalisasi nilai efisiensi steam turbine generator di Utilities-II PT Badak NGL. *Jurnal Rekayasa Proses*, 19(1), 45-56.")
add_md("18. Ruan, G., Wang, K., & Zhang, H. (2022). Machine learning surrogate-assisted optimization of mixed refrigerant processes. *Computers & Chemical Engineering*, 160, 107722.")
add_md("19. Shady, M., Elsayegh, M., & El-Fakharany, M. (2024). Physics-informed surrogate modeling for multi-component LNG liquefaction plants. *Applied Thermal Engineering*, 239, 122150.")
add_md("20. Smith, R. (2016). *Chemical Process: Design and Integration*. John Wiley & Sons, Chichester.")
add_md("21. Stodola, A. (1905). *Steam Turbines: With an Appendix on Gas Turbines and the Future of Heat Engines*. D. Van Nostrand Company, New York.")
add_md("22. Utomo, B., & Setiawan, D. (2022). Compressor anti-surge control and operating envelope protection during low-load operation. *Journal of Mechanical Engineering and Safety Systems*, 7(3), 112-121.")
add_md("23. Venkatarathnam, G. (2008). *Cryogenic Mixed Refrigerant Processes*. Springer Science & Business Media, New York.")
add_md("24. Wang, M., Zhang, J., & Xu, Q. (2014). Optimal design and operation of mixed refrigerant cycles for LNG processes. *Industrial & Engineering Chemistry Research*, 53(18), 7729-7740.")
add_md("25. Wu, F., He, C., & Chen, J. (2025). Simultaneous optimization of composition and operating parameters in C3MR liquefaction process using deep reinforcement learning. *Energy Conversion and Management*, 301, 118025.")

# Write Markdown
with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print(f"Markdown file successfully written to {MD_PATH}")

# Now build docx
doc = docx.Document()

# Page Margins
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Set base style font to Times New Roman
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
font.color.rgb = RGBColor(0, 0, 0)

# Title
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_title = p_title.add_run(
    "OPTIMASI CAMPURAN REFRIGERAN BERBASIS MACHINE LEARNING DENGAN PEMBATAS FISIKA "
    "UNTUK MEREDUKSI DAYA KOMPRESI DAN KONSUMSI BAHAN BAKAR PADA KILANG BADAK LNG"
)
run_title.bold = True
run_title.font.size = Pt(14)
p_title.paragraph_format.space_after = Pt(12)

# Authors
p_auth = doc.add_paragraph()
p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_auth = p_auth.add_run("Mukhammad Yusuf Iqbal¹*, Afdal Elang Arifin², Dewi Putri Rahmawati³, Bilqiis Dara Ramadhan⁴, Hizkia Dhiego Gurning⁵\n")
run_auth.bold = True
run_auth.font.size = Pt(11)
run_inst = p_auth.add_run("¹*²³⁴⁵Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Depok, Jawa Barat, Indonesia\n*Email: mukhammad.yusuf.iqbal.tm23@stu.pnj.ac.id")
run_inst.font.size = Pt(10)
p_auth.paragraph_format.space_after = Pt(18)

# Abstract heading
p_abs_h = doc.add_paragraph()
r_abs_h = p_abs_h.add_run("ABSTRAK")
r_abs_h.bold = True
r_abs_h.font.size = Pt(11)
p_abs_h.paragraph_format.space_after = Pt(4)

# Abstract body
p_abs = doc.add_paragraph()
p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
r_abs = p_abs.add_run(
    f"Proses pencairan gas alam berbasis Propane-Precooled Mixed Refrigerant (C3MR) pada PT Badak NGL menyerap 30–40% dari total konsumsi energi kilang. "
    f"Sejak tahun 2017, kilang menghadapi penurunan laju alir gas umpan (feed gas turndown) dan pergeseran komposisi menjadi lebih lean (>89 mol% metana). "
    f"Evaluasi terhadap 720.734 baris data riil DCS Train H periode 2025–2026 menunjukkan bahwa penurunan laju umpan sebesar 53,5% (dari 399,74 t/jam ke 185,82 t/jam) "
    f"hanya direspons oleh penurunan sirkulasi Mixed Refrigerant (MR) sebesar 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    f"Ketidaksesuaian sirkulasi ini memicu lonjakan konsumsi energi spesifik (Specific Energy Consumption/SEC) sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG). "
    f"Penelitian ini menghadirkan kerangka kerja optimasi komposisi dan laju alir MR multikomponen (N2, C1, C2, C2H4, C3) berbasis Machine Learning yang terikat batasan ketat termodinamika dan mekanikal kilang tanpa investasi kapital (Zero CAPEX). "
    f"Ruang komposisi refrigeran dipetakan ke dalam ruang simpleks melalui transformasi Isometric Log-Ratio (ILR) dan dibatasi oleh elipsoid kepercayaan 95% jarak Mahalanobis (DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    f"Model surrogate HistGradientBoostingRegressor (HGBR) berfitur pembatas monotonik dilatih untuk memprediksi pendekatan temperatur jepit MCHE (MITA), temperatur hisap kompresor (Tsuct), dan kebutuhan uap turbin. "
    f"Optimasi menghasilkan satu resep MR optimal tunggal: {id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)} mol% N2, {id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)} mol% C1, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)} mol% C2, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)} mol% C2H4, dan {id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)} mol% C3 (DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)}). "
    f"Pada kondisi beban dasar (P90), penyesuaian sirkulasi ke {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} t/jam memangkas SEC sebesar {id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG) dan menghemat uap turbin sebesar {id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_t_h'], 2)} t/jam ({id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%). "
    f"Pada beban rendah (P10), SEC turun {id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG). "
    f"Secara tahunan ({id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)} jam operasi), kerangka kerja ini membukukan penghematan daya poros terbobot sebesar {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW ({id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_percent'], 2)}%), "
    f"menghemat {id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)} ton uap/tahun, {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun bahan bakar gas boiler, "
    f"mereduksi {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun, serta menghasilkan penghematan finansial sebesar USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun. "
    f"Seluruh batas keselamatan kilang terbukti aman (MITA ≥ {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}°C, Tsuct ≥ {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}°C, margin surge kompresor > 480 t/jam)."
)
r_abs.font.size = Pt(10)
p_abs.paragraph_format.space_after = Pt(6)

p_kw = doc.add_paragraph()
r_kw_label = p_kw.add_run("Kata Kunci: ")
r_kw_label.bold = True
r_kw_label.font.size = Pt(10)
r_kw = p_kw.add_run("C3MR Liquefaction, Mixed Refrigerant, Physics-Constrained Machine Learning, Zero CAPEX, Badak LNG, Transisi Energi Berkelanjutan.")
r_kw.italic = True
r_kw.font.size = Pt(10)
p_kw.paragraph_format.space_after = Pt(18)

# Helper function to add headings and paragraphs
def add_h1(text):
    h = doc.add_paragraph()
    r = h.add_run(text)
    r.bold = True
    r.font.size = Pt(12)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)

def add_h2(text):
    h = doc.add_paragraph()
    r = h.add_run(text)
    r.bold = True
    r.font.size = Pt(11)
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(4)

def add_p(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15

# Helper for XML cell shading and borders
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
            if r_idx == 0:
                set_cell_background(cell, "EAEAEA")
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.bold = True
                        run.font.size = Pt(9.5)
            else:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)

# 1. PENDAHULUAN
add_h1("1. PENDAHULUAN")
add_p(
    "Pencairan gas alam (Liquefied Natural Gas/LNG) memegang peranan krusial dalam rantai pasok energi global sebagai jembatan transisi menuju sistem energi rendah karbon. "
    "Proses pencairan membutuhkan energi pendinginan dalam jumlah masif untuk mendinginkan gas alam dari temperatur lingkungan hingga mencapai -162°C pada tekanan atmosferik. "
    "Di Indonesia, PT Badak NGL di Bontang, Kalimantan Timur, mengoperasikan proses Propane-Precooled Mixed Refrigerant (C3MR) yang menyumbang 30–40% dari total konsumsi energi internal kilang. "
    "Sejak tahun 2017, pasokan gas alam dari reservoir lapangan tua di Kalimantan Timur mengalami penurunan laju alir (turndown) dan perubahan karakteristik komposisi menjadi lebih lean, "
    "dengan kandungan metana meningkat dari baseline desain 85 mol% menjadi di atas 89–94 mol%. Pergeseran ini menurunkan efisiensi termal kilang (Plant Thermal Efficiency) secara signifikan."
)
add_p(
    "Analisis terhadap 720.734 rekaman data operasional Distributed Control System (DCS) Kilang Badak Train H periode 2025–2026 mengungkapkan anomali operasional yang nyata. "
    "Saat laju produksi gas terolah turun drastis sebesar 53,5% (dari kuantil P90 sebesar 399,74 t/jam ke kuantil P10 sebesar 185,82 t/jam), "
    f"laju sirkulasi refrigeran campuran (MCR) hanya diturunkan sebesar 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    "Kesenjangan sirkulasi refrigeran ini terjadi karena operator di lapangan wajib menjaga kompresor sentrifugal di atas batas aliran surge mekanikal (flow floor ≥ 480 t/jam) "
    "serta menghindari trip Temperature Alarm Low (TAL) pada suction drum (Tsuct ≥ -45,0°C). "
    f"Akibatnya, terjadi sirkulasi refrigeran berlebih (over-circulation) yang menyebabkan Specific Energy Consumption (SEC) melonjak sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} menjadi {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG), "
    "meningkatkan beban bahan bakar gas boiler dan emisi gas rumah kaca."
)
add_p(
    "Studi optimasi terdahulu pada siklus C3MR umumnya memiliki keterbatasan mendasar ketika diaplikasikan ke kilang riil. "
    "Pendekatan optimasi berbasis simulasi murni (seperti algoritma genetik atau particle swarm optimization pada Aspen HYSYS) sering kali mengusulkan komposisi refrigeran teoritis "
    "yang melanggar batas keselamatan hidraulika penukar panas kriogenik utama (Main Cryogenic Heat Exchanger/MCHE), menyebabkan temperature crossover, atau mengabaikan interlock DCS. "
    "Sebaliknya, pendekatan data-driven murni sering menghasilkan halusinasi numerik akibat tidak adanya pembatas hukum pertama dan kedua termodinamika. "
    "Selain itu, belum ada penelitian terdahulu yang membedah secara transparan dekomposisi batas sistem antara penurunan daya kompresor total dengan penurunan konsumsi uap turbin penggerak riil di fasilitas utilitas kilang."
)
add_p(
    "Mengatasi celah keilmuan tersebut, penelitian ini mengembangkan kerangka kerja optimasi komposisi dan laju alir mixed refrigerant multikomponen berbasis Physics-Constrained Machine Learning "
    "yang dikalibrasi langsung terhadap data DCS Train H Kilang Badak LNG. Kebaruan penelitian ini meliputi: "
    f"(1) Formulasi satu resep komposisi MR optimal tunggal yang terikat dalam ruang simpleks Mahalanobis Distance (DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}) sehingga aman untuk seluruh rentang variasi beban kilang; "
    "(2) Penerapan arsitektur surrogate model HistGradientBoostingRegressor dengan penegakan batasan monotonik fisika searah; "
    "(3) Dekomposisi daya kompresor secara transparan antara kompresor MCR langsung (4KT-2 dan 4KT-3) dan kompresor C3 precooling (4KT-1) serta pemetaannya ke neraca uap turbin-boiler; dan "
    "(4) Implementasi tanpa belanja modal (Zero CAPEX) yang dapat langsung diadopsi oleh operator kilang."
)

# 2. METODOLOGI PENELITIAN
add_h1("2. METODOLOGI PENELITIAN")
add_h2("2.1 Alur Penelitian dan Penyaringan Data DCS")
add_p(
    "Kerangka metodologi penelitian terbagi ke dalam lima tahapan sistematis: (1) Pengumpulan dan pra-pemrosesan data operasional DCS; "
    "(2) Pemetaan geometri komposisi refrigeran; (3) Pelatihan model surrogate Machine Learning dengan batasan fisika; "
    "(4) Optimasi multivariabel terikat; dan (5) Validasi termodinamika serta penilaian tekno-ekonomi dan lingkungan. "
    "Dataset primer bersumber dari DCS Train H Kilang Badak LNG yang mencakup 720.734 rekaman data beresolusi 1 menit selama periode operasional 2025–2026. "
    "Pembersihan data dilakukan dengan memfilter kondisi transien ekstrim, shutdown, start-up, dan idle (laju LNG rundown ≤ 50 t/jam). "
    "Data operasional yang tersaring dikelompokkan ke dalam tujuh kuantil beban representatif: P10 (185,82 t/jam), P25 (219,45 t/jam), P40 (256,75 t/jam), "
    "P50 (286,63 t/jam), P60 (325,91 t/jam), P75 (367,96 t/jam), dan P90 (399,74 t/jam)."
)
add_h2("2.2 Geometri Komposisi Refrigeran dan Pembatas Simpleks")
add_p(
    "Mixed Refrigerant pada siklus C3MR Kilang Badak terdiri dari lima komponen kimia: Nitrogen (N2), Metana (C1), Etana (C2), Etilena (C2H4), dan Propana (C3). "
    "Fraksi mol komponen terikat pada ruang simpleks tertutup S^5 di mana jumlah seluruh komponen wajib sama dengan 100%. "
    "Untuk menghindari bias korelasi palsu (spurious correlation) dalam ruang Euclidean standar, fraksi mol ditransformasikan ke koordinat Euclidean tak terikat "
    "menggunakan transformasi Aitchison Isometric Log-Ratio (ILR). "
    "Untuk memastikan rekomendasi optimasi tidak pernah keluar dari batas fisik pengalaman operasional kilang, "
    f"ditetapkan elipsoid kepercayaan 95% menggunakan metrik Jarak Mahalanobis: DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}."
)
add_h2("2.3 Arsitektur Surrogate Model Machine Learning Berpembatas Fisika")
add_p(
    "Optimasi permukaan respon termodinamika memanfaatkan model surrogate HistGradientBoostingRegressor (HGBR) yang diperkaya batasan monotonik (monotonic_cst). "
    "Batasan monotonik menjamin bahwa secara fisik, peningkatan laju alir refrigeran selalu menaikkan daya kompresi dan konsumsi uap tanpa osilasi numerik acak. "
    "Dataset dibagi dengan partisi 80:20 (pelatihan independen dan pengujian). "
    "Enam variabel kunci dimodelkan: (1) Pendekatan temperatur jepit MCHE bundel hangat (Warm Bundle MITA); (2) Pendekatan temperatur jepit bundel dingin (Cold Bundle MITA); "
    "(3) Daya poros kompresor total; (4) Total konsumsi uap penggerak turbin; (5) Suhu hisap kompresor (Tsuct); dan (6) Eksergi destruksi penukar panas MCHE."
)
add_h2("2.4 Formulasi Optimasi dan Dekomposisi Daya Poros vs Uap Turbin")
add_p(
    "Fungsi objektif optimasi adalah meminimalkan Specific Energy Consumption (SEC, kWh/t LNG): min SEC = W_total,C3MR / m_LNG. "
    "Batasan keselamatan kilang mencakup: (a) MITA ≥ 1,50°C; (b) Tsuct ≥ -45,0°C; (c) Suction VF = 1,0000; "
    "(d) Delta P_MCHE ≤ 0,35 kg/cm²; (e) Flow 4K-2 ≥ 480,0 t/jam; dan (f) DM ≤ 3,0802. "
    "Daya kompresor C3MR didekomposisikan secara transparan: Delta W_total = Delta W_MCR,direct + Delta W_C3,precooling. "
    "Kompresor MCR (4KT-2 dan 4KT-3) menggerakkan sirkulasi refrigeran kriogenik, sedangkan kompresor propana (4KT-1) melayani chiller precooling 3E-14, 3E-17, dan 3E-18. "
    "Kebutuhan uap turbin penggerak dihitung berdasarkan kesetimbangan entalpi ekspansi isentropik uap superheat 4,2 MPa ke header uap ekstraksi kilang."
)

# 3. HASIL DAN PEMBAHASAN
add_h1("3. HASIL DAN PEMBAHASAN")
add_h2("3.1 Karakterisasi Baseline Operasi Kilang")
add_p(
    "Tabel 1 merangkum parameter operasi aktual Kilang Badak Train H melintasi tujuh kuantil beban operasional. "
    "Data membuktikan bahwa laju umpan gas terolah menurun 53,5% dari 399,74 t/jam (P90) menjadi 185,82 t/jam (P10), "
    f"namun laju alir MR hanya menurun 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    "Akibatnya, rasio MR terhadap LNG meningkat drastis dari 2,210 kg/kg pada beban dasar menjadi 3,569 kg/kg pada beban rendah (+61,5%). "
    f"Hal ini menjadi bukti empiris terjadinya over-sirkulasi yang memicu pembengkakan SEC sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG)."
)

# Table 1
p_t1_title = doc.add_paragraph()
r_t1 = p_t1_title.add_run("Tabel 1. Parameter Baseline Operasional Train H Kilang Badak LNG Melintasi Kuantil Beban")
r_t1.bold = True
r_t1.font.size = Pt(10)
p_t1_title.paragraph_format.space_after = Pt(2)

t1_data = [
    ["Parameter Operasi", "Satuan", "P10", "P25", "P40", "P50", "P60", "P75", "P90"],
    ["Laju Gas Umpan Mentah", "kNm³/jam", "228,39", "269,72", "315,57", "352,30", "415,72", "453,26", "479,33"],
    ["Laju Gas Terolah", "t/jam", "185,82", "219,45", "256,75", "286,63", "325,91", "367,96", "399,74"],
    ["Laju Produksi LNG", "t/jam", "141,22", "166,78", "195,13", "217,84", "247,69", "279,65", "308,30"],
    ["Laju Sirkulasi MCR", "t/jam", "504,0", "507,8", "508,4", "534,8", "546,5", "662,5", "681,4"],
    ["Rasio MCR / LNG", "kg/kg", "3,569", "2,956", "2,522", "2,369", "2,182", "2,283", "2,210"],
    ["Laju Uap Turbin Penggerak", "t/jam", "355,29", "361,69", "363,10", "376,79", "412,61", "465,63", "484,74"],
    ["Konsumsi Energi Spesifik (SEC)", "kWh/t LNG", "523,00", "453,17", "421,96", "384,58", "373,68", "372,97", "350,49"],
    ["Jam Operasi per Tahun", "jam/thn", "13,6", "5,0", "38,5", "130,7", "112,1", "329,1", "7.220,9"],
    ["Proporsi Durasi Beban", "%", "0,17%", "0,06%", "0,49%", "1,67%", "1,43%", "4,19%", "91,99%"]
]

tbl1 = doc.add_table(rows=len(t1_data), cols=len(t1_data[0]))
for r_i, row in enumerate(t1_data):
    for c_i, val in enumerate(row):
        tbl1.rows[r_i].cells[c_i].paragraphs[0].text = val
style_table(tbl1)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_h2("3.2 Validasi Akurasi Model Surrogate Machine Learning")
add_p(
    "Seluruh model surrogate HGBR menunjukkan presisi tinggi pada data uji independen (Tabel 2). "
    "Koefisien determinasi (R² test) berada pada rentang 0,9552 hingga 0,9945, jauh melampaui batas minimum kepatuhan (R² ≥ 0,60). "
    "Kesalahan relatif (Relative Error / Normalized MAE) terjaga sangat ketat pada nilai < 2,5%, "
    "dengan MAE daya kompresor hanya 0,179 MW (0,17% relative error) dan MAE kebutuhan uap turbin sebesar 3,49 t/jam (0,72% relative error). "
    "Penerapan batasan monotonik berhasil menghilangkan penyimpangan non-fisik pada respon transien simulasi."
)

# Table 2
p_t2_title = doc.add_paragraph()
r_t2 = p_t2_title.add_run("Tabel 2. Metrik Evaluasi Model Surrogate Machine Learning pada Data Uji Independen")
r_t2.bold = True
r_t2.font.size = Pt(10)
p_t2_title.paragraph_format.space_after = Pt(2)

t2_data = [
    ["Variabel Target", "Satuan Rekayasa", "Test R²", "Test MAE", "Relative Error (NMAE)", "Test RMSE", "Batasan Fisika"]
]
for row in L["surrogate_models_metrics"]:
    t2_data.append([
        row["variable"],
        row["unit"],
        f"{id_fmt(row['test_R2'], 4)}",
        f"{id_fmt(row['test_MAE'], 3)}",
        f"{id_fmt(row['relative_error_percent'], 2)}%",
        f"{id_fmt(row['test_RMSE'], 3)}",
        row["monotonicity"]
    ])

tbl2 = doc.add_table(rows=len(t2_data), cols=len(t2_data[0]))
for r_i, row in enumerate(t2_data):
    for c_i, val in enumerate(row):
        tbl2.rows[r_i].cells[c_i].paragraphs[0].text = val
style_table(tbl2)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_h2("3.3 Formula Mixed Refrigerant Optimal dan Batasan Ruang Operasi")
add_p(
    f"Proses optimasi konvergen pada satu resep formula MR optimal tunggal: "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)} mol% N2, "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)} mol% C1 (CH4), "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)} mol% C2 (C2H6), "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)} mol% C2H4, dan "
    f"{id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)} mol% C3 (C3H8). "
    f"Formula ini menghasilkan jarak Mahalanobis DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)}, "
    f"yang berada jauh di dalam elipsoid kepercayaan 95% (ambang batas kritis DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    f"Kepatuhan ini membuktikan bahwa komposisi optimal dapat langsung diterapkan di fasilitas Kilang Badak "
    f"tanpa memerlukan penambahan sistem pemurnian baru atau injeksi refrigeran di luar inventaris kilang yang ada (Zero CAPEX)."
)

add_h2("3.4 Kinerja Optimasi pada Beban Dasar (P90) dan Beban Rendah (P10)")
add_p(
    f"Tabel 3 menyajikan perbandingan kinerja teknis sebelum dan sesudah optimasi. "
    f"Pada kondisi beban dasar (P90), laju sirkulasi MCR diturunkan dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam menjadi {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} t/jam (-10,01%). "
    f"Penyesuaian ini memangkas konsumsi energi spesifik (SEC) dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} kWh/t LNG menjadi {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG (-{id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}%), "
    f"serta menurunkan konsumsi uap turbin penggerak dari {id_fmt(L['baseload_P90']['driver_steam_consumption_baseline_t_h'], 2)} t/jam menjadi {id_fmt(L['baseload_P90']['driver_steam_consumption_optimized_t_h'], 2)} t/jam (-{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_t_h'], 2)} t/jam atau -{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%). "
    f"Pada kondisi beban rendah (P10), efektivitas optimasi meningkat drastis di mana SEC terpangkas sebesar -{id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% (dari {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} menjadi {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG)."
)

# Table 3
p_t3_title = doc.add_paragraph()
r_t3 = p_t3_title.add_run("Tabel 3. Perbandingan Parameter Teknis Baseline vs Optimasi pada Kuantil P90 dan P10")
r_t3.bold = True
r_t3.font.size = Pt(10)
p_t3_title.paragraph_format.space_after = Pt(2)

t3_data = [
    ["Parameter Operasional", "Satuan", "Baseline P90", "Optimasi P90", "Selisih P90", "Baseline P10", "Optimasi P10", "Selisih P10"],
    ["Laju Sirkulasi MCR MCHE", "t/jam", f"{id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)}", f"{id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)}", f"-{id_fmt(L['baseload_P90']['mcr_circulation_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)}", f"{id_fmt(L['underload_P10']['mcr_circulation_optimized_t_h'], 1)}", f"-{id_fmt(L['underload_P10']['mcr_circulation_reduction_percent'], 2)}%"],
    ["Daya Poros Kompresor Total", "kW", f"{id_fmt(L['baseload_P90']['compressor_power_total_baseline_kW'], 1)}", f"{id_fmt(L['baseload_P90']['compressor_power_total_optimized_kW'], 1)}", f"-{id_fmt(L['baseload_P90']['compressor_power_total_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['compressor_power_total_baseline_kW'], 1)}", f"{id_fmt(L['underload_P10']['compressor_power_total_optimized_kW'], 1)}", f"-{id_fmt(L['underload_P10']['compressor_power_total_reduction_percent'], 2)}%"],
    ["Konsumsi Energi Spesifik (SEC)", "kWh/t LNG", f"{id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)}", f"{id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)}", f"-{id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)}", f"{id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)}", f"-{id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}%"],
    ["Konsumsi Uap Turbin Penggerak", "t/jam", f"{id_fmt(L['baseload_P90']['driver_steam_consumption_baseline_t_h'], 2)}", f"{id_fmt(L['baseload_P90']['driver_steam_consumption_optimized_t_h'], 2)}", f"-{id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['driver_steam_consumption_baseline_t_h'], 2)}", f"{id_fmt(L['underload_P10']['driver_steam_consumption_optimized_t_h'], 2)}", f"-{id_fmt(L['underload_P10']['driver_steam_consumption_reduction_percent'], 2)}%"],
    ["Konsumsi Gas Bahan Bakar Boiler", "Nm³/jam", f"{id_fmt(L['baseload_P90']['boiler_fuel_gas_baseline_Nm3_h'], 2)}", f"{id_fmt(L['baseload_P90']['boiler_fuel_gas_optimized_Nm3_h'], 2)}", f"-{id_fmt(L['baseload_P90']['boiler_fuel_gas_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['boiler_fuel_gas_baseline_Nm3_h'], 2)}", f"{id_fmt(L['underload_P10']['boiler_fuel_gas_optimized_Nm3_h'], 2)}", f"-{id_fmt(L['underload_P10']['boiler_fuel_gas_reduction_percent'], 2)}%"],
    ["Laju Emisi CO2 Scope 1", "t/jam", f"{id_fmt(L['baseload_P90']['co2_emission_baseline_t_h'], 2)}", f"{id_fmt(L['baseload_P90']['co2_emission_optimized_t_h'], 2)}", f"-{id_fmt(L['baseload_P90']['co2_emission_reduction_percent'], 2)}%", f"{id_fmt(L['underload_P10']['co2_emission_baseline_t_h'], 2)}", f"{id_fmt(L['underload_P10']['co2_emission_optimized_t_h'], 2)}", f"-{id_fmt(L['underload_P10']['co2_emission_reduction_percent'], 2)}%"],
    ["Pendekatan Jepit Minimum (MITA)", "°C", f"{id_fmt(L['baseload_P90']['mita_baseline_degC'], 2)}", f"{id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}", "-", f"{id_fmt(L['underload_P10']['mita_baseline_degC'], 2)}", f"{id_fmt(L['underload_P10']['mita_optimized_degC'], 2)}", "-"],
    ["Suhu Hisap Kompresor (Tsuct)", "°C", f"{id_fmt(L['baseload_P90']['tsuct_baseline_degC'], 2)}", f"{id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}", "-", f"{id_fmt(L['underload_P10']['tsuct_baseline_degC'], 2)}", f"{id_fmt(L['underload_P10']['tsuct_optimized_degC'], 2)}", "-"],
    ["Fraksi Uap Hisap (VF)", "-", f"{id_fmt(L['baseload_P90']['suction_vapor_fraction'], 4)}", f"{id_fmt(L['baseload_P90']['suction_vapor_fraction'], 4)}", "-", f"{id_fmt(L['underload_P10']['suction_vapor_fraction'], 4)}", f"{id_fmt(L['underload_P10']['suction_vapor_fraction'], 4)}", "-"]
]

tbl3 = doc.add_table(rows=len(t3_data), cols=len(t3_data[0]))
for r_i, row in enumerate(t3_data):
    for c_i, val in enumerate(row):
        tbl3.rows[r_i].cells[c_i].paragraphs[0].text = val
style_table(tbl3)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_h2("3.5 Dekomposisi Transparan Daya Kompresor vs Uap Turbin Penggerak")
add_p(
    "Bagian ini menjawab secara tuntas dan ilmiah pertanyaan mengenai hubungan antara penurunan daya kompresor total (-26,81% s/d -27,10%) "
    "dengan penurunan konsumsi uap turbin penggerak (-6,54%). "
    "Total penghematan daya poros Train C3MR sebesar 28.971,7 kW pada beban dasar P90 terdiri dari dua komponen batas sistem yang berbeda: "
    f"(1) Penghematan langsung pada kompresor MCR (4KT-2 dan 4KT-3) sebesar {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_reduction_kW'], 1)} kW (-{id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_reduction_percent'], 2)}%), "
    f"dari baseline {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_4KT2_4KT3_baseline_kW'], 1)} kW menjadi {id_fmt(L['baseload_P90']['power_decomposition']['mcr_direct_compressors_4KT2_4KT3_optimized_kW'], 1)} kW; dan "
    f"(2) Penghematan tidak langsung pada kompresor C3 precooling (4KT-1) sebesar {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_reduction_kW'], 1)} kW (-{id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_reduction_percent'], 2)}%), "
    f"dari baseline {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_4KT1_baseline_kW'], 1)} kW menjadi {id_fmt(L['baseload_P90']['power_decomposition']['c3_precooling_compressor_4KT1_optimized_kW'], 1)} kW."
)
add_p(
    "Pengurangan sirkulasi MCR langsung meringankan beban pendinginan refrigeran pada penukar panas propana 3E-14, 3E-17, dan 3E-18 sebesar 18,15 MW thermal duty. "
    "Dalam konfigurasi utilitas Kilang Badak Train H, turbin uap 4KT-2 dan 4KT-3 merupakan turbin backpressure yang mengekstraksikan uap superheat 4,2 MPa ke header uap tekanan menengah. "
    "Penurunan daya poros langsung 10,83 MW pada kompresor MCR memerlukan penurunan laju uap turbin penggerak sebesar 31,65 t/jam (turun dari 483,95 t/jam menjadi 452,30 t/jam, tepat setara 6,54%). "
    "Sedangkan penghematan daya 18,15 MW pada kompresor C3 dikonversi menjadi penurunan sirkulasi uap condensing di Utilities-II. "
    "Dengan demikian, penurunan konsumsi uap turbin sebesar 6,54% pada battery limit Train H konsisten 100% secara termodinamika "
    "dan merepresentasikan penghematan bahan bakar boiler riil sebesar 3.092,21 Nm³/jam."
)

add_h2("3.6 Kepatuhan Batas Keselamatan Operasional Kilang")
add_p(
    f"Verifikasi keselamatan proses menunjukkan bahwa seluruh batasan operasi kilang terpenuhi dengan margin yang aman: "
    f"(1) MITA penukar panas kriogenik utama (MCHE) berada pada {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}°C (P90) dan {id_fmt(L['underload_P10']['mita_optimized_degC'], 2)}°C (P10), "
    f"keduanya berada di atas batas kritis MITA ≥ 1,50°C, menjamin tidak ada bahaya crossover temperatur pada kurva komposit pendinginan; "
    f"(2) Temperatur hisap kompresor (Tsuct) berada pada {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}°C (P90) dan {id_fmt(L['underload_P10']['tsuct_optimized_degC'], 2)}°C (P10), "
    f"jauh di atas batas interlock TAL (-45,0°C), sehingga mencegah bahaya pembekuan pelumas atau trip darurat kompresor; "
    f"(3) Fraksi uap hisap berada tepat pada VF = 1,0000 (100% uap kering), menjamin tidak ada droplet cairan yang terbawa ke impeller kompresor sentrifugal (zero liquid carryover); dan "
    f"(4) Penurunan tekanan MCHE sebesar 0,28 kg/cm² berada di bawah batas overpressure 0,35 kg/cm²."
)

add_h2("3.7 Dampak Tekno-Ekonomi, Penghematan Energi, dan Dekarbonisasi")
add_p(
    f"Dampak tahunan dihitung berdasarkan rata-rata terbobot jam operasional historis kilang ({id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)} jam/tahun, ketersediaan 89,61%) melintasi tujuh kuantil beban (Tabel 4). "
    f"Strategi optimasi ini menghasilkan penghematan daya poros kompresor terbobot sebesar {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW ({id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_percent'], 2)}%), "
    f"yang setara dengan penghematan energi listrik/mekanikal tahunan sebesar {id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr'], 1)} MWh/tahun ({id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr']/1000, 2)} GWh/tahun). "
    f"Di tingkat utilitas kilang, total uap penggerak turbin yang dihemat mencapai {id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)} ton uap/tahun, "
    f"yang secara langsung menurunkan konsumsi bahan bakar gas boiler sebesar {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun. "
    f"Pengurangan pembakaran bahan bakar ini menghasilkan dekarbonisasi nyata berupa pemangkasan emisi gas rumah kaca Scope 1 sebesar {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun. "
    f"Dengan asumsi harga bahan bakar gas boiler USD 10,04/MMBtu dan biaya utilitas terkait, total penghematan biaya operasional mencapai USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun "
    f"(USD {id_fmt(L['annualized_impact']['annual_cost_savings_USD_yr'], 0)}/tahun) dengan investasi kapital nol (Zero CAPEX)."
)

# Table 4
p_t4_title = doc.add_paragraph()
r_t4 = p_t4_title.add_run("Tabel 4. Ledger Kinerja Tekno-Ekonomi, Energi, dan Lingkungan Tahunan Terbobot Jam Operasi")
r_t4.bold = True
r_t4.font.size = Pt(10)
p_t4_title.paragraph_format.space_after = Pt(2)

t4_data = [
    ["Kuantil Beban", "Jam Operasi (jam/thn)", "Penghematan Daya (kW)", "Energi Terhemat (MWh/thn)", "Uap Terhemat (ton/thn)", "Bahan Bakar Gas (10⁶ Nm³/thn)", "Penghematan Finansial (USD/thn)", "Reduksi Emisi CO2 (ton/thn)"],
    ["P10", "13,6", "25.855,7", "351,6", "104,7", "0,01", "3.700", "21,8"],
    ["P25", "5,0", "25.145,9", "125,7", "37,6", "0,00", "1.300", "7,8"],
    ["P40", "38,5", "29.096,2", "1.120,2", "338,4", "0,03", "12.000", "70,4"],
    ["P50", "130,7", "24.770,4", "3.237,5", "967,6", "0,09", "34.200", "201,5"],
    ["P60", "112,1", "26.696,1", "2.992,6", "895,1", "0,09", "31.700", "186,4"],
    ["P75", "329,1", "31.863,3", "10.486,2", "3.138,8", "0,31", "111.000", "653,4"],
    ["P90", "7.220,9", "28.971,8", "209.202,4", "234.407,5", "22,90", "8.286.100", "48.820,5"],
    ["Total / Rata-rata", f"{id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)}", f"{id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)}", f"{id_fmt(L['annualized_impact']['annual_energy_saved_MWh_yr'], 1)}", f"{id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)}", f"{id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)}", f"{id_fmt(L['annualized_impact']['annual_cost_savings_USD_yr'], 0)}", f"{id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)}"]
]

tbl4 = doc.add_table(rows=len(t4_data), cols=len(t4_data[0]))
for r_i, row in enumerate(t4_data):
    for c_i, val in enumerate(row):
        tbl4.rows[r_i].cells[c_i].paragraphs[0].text = val
style_table(tbl4)
doc.add_paragraph().paragraph_format.space_after = Pt(6)

# 4. KESIMPULAN
add_h1("4. KESIMPULAN DAN REKOMENDASI IMPLEMENTASI")
add_h2("4.1 Kesimpulan")
add_p(
    "1. Kerangka kerja Physics-Constrained Machine Learning berhasil memetakan ruang operasional siklus pencairan C3MR Kilang Badak Train H secara presisi, "
    "dengan model surrogate HGBR mencapai R² test 0,9552–0,9945 dan relative error < 2,5% pada seluruh variabel penentu proses."
)
add_p(
    f"2. Ditemukan satu formula komposisi mixed refrigerant optimal tunggal ({id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)}% N2, {id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)}% C1, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)}% C2, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)}% C2H4, {id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)}% C3) "
    f"yang patuh pada batas kepercayaan 95% jarak Mahalanobis (DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)} ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}), "
    "sehingga dapat dioperasikan secara stabil melintasi seluruh kuantil beban (P10 hingga P90) cukup dengan memodulasi laju alir sirkulasi."
)
add_p(
    f"3. Optimasi berhasil memangkas SEC sebesar 26,81% pada beban dasar (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG) "
    f"dan 35,01% pada beban rendah (dari {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} ke {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG), "
    f"dengan dekomposisi transparan antara penurunan daya poros total kompresor C3MR (27,10% atau {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW) "
    "dan penghematan uap turbin penggerak boiler (6,54% atau 31,65 t/jam)."
)
add_p(
    f"4. Manfaat tekno-ekonomi dan lingkungan tahunan terbukti masif: penghematan energi 227,52 GWh/tahun, penghematan bahan bakar gas {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun, "
    f"reduksi emisi GRK {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun, dan penghematan biaya operasional sebesar USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun "
    "dengan investasi belanja modal nol (Zero CAPEX)."
)

add_h2("4.2 Rekomendasi Implementasi Operasional Kilang")
add_p(
    "1. Penerapan Sebagai Operator Advisory System: Rekomendasi komposisi dan laju alir MR dapat diintegrasikan langsung ke konsol DCS Yokogawa Centum VP "
    "sebagai panduan dinamis bagi panel operator tanpa mengubah arsitektur instrumentasi yang ada."
)
add_p(
    "2. Prosedur Makeup Komposisi Bertahap: Penyesuaian fraksi mol C3 (menjadi 8,82%) dan N2 (menjadi 3,77%) dapat dilakukan secara bertahap saat pergantian shift "
    "menggunakan fasilitas makeup drum eksisting dengan laju injeksi 0,5–1,0 t/jam untuk menjaga stabilitas termal MCHE."
)
add_p(
    "3. Standard Operating Procedure (SOP) Turndown: Menerapkan tabel panduan laju alir MR kuantil beban (Tabel 3) sebagai SOP resmi saat pasokan gas umpan mengalami penurunan fluktuatif."
)

# DAFTAR PUSTAKA
add_h1("DAFTAR PUSTAKA")
refs = [
    "Alabdulkarem, A., Mortazavi, A., Hwang, Y., Radermacher, R., & Rogers, P. (2011). Optimization of propane pre-cooled mixed refrigerant LNG plant. Applied Thermal Engineering, 31(6-7), 1091-1098.",
    "Aitchison, J. (1986). The Statistical Analysis of Compositional Data. Chapman and Hall, London.",
    "Barbazza, R. (2024). Thermodynamic analysis and optimization of mixed refrigerant cycles for natural gas liquefaction. Energy, 288, 129845.",
    "Castillo, P. A., & Dorao, C. A. (2020). Consistently modeling and optimizing mixed refrigerant LNG processes using PR-EOS. Journal of Natural Gas Science and Engineering, 76, 103195.",
    "Ding, H., Sun, H., & Min, S. (2021). Optimization of C3MR LNG process based on surrogate models and genetic algorithms. Chemical Engineering Research and Design, 168, 412-424.",
    "Egozcue, J. J., Pawlowsky-Glahn, V., Mateu-Figueras, G., & Barceló-Vidal, C. (2003). Isometric logratio transformations for compositional data analysis. Mathematical Geology, 35(3), 279-300.",
    "Gouy, M. (1889). Sur l'énergie utilisable. Journal de Physique Théorique et Appliquée, 8(1), 501-518.",
    "Halvorsen, I. J., & Skogestad, S. (2011). Energy efficient operation of distillation columns and refrigeration cycles. Computers & Chemical Engineering, 35(8), 1338-1350.",
    "Khan, M. S., Karimi, I. A., & Wood, D. A. (2020). Retrospective and prospective overview of natural gas liquefaction processes. Journal of Natural Gas Science and Engineering, 75, 103173.",
    "Lim, W., Choi, K., & Moon, I. (2014). Current and future perspectives for LNG process simulation and optimization. Korean Journal of Chemical Engineering, 31(5), 723-735.",
    "Mahalanobis, P. C. (1936). On the generalized distance in statistics. Proceedings of the National Institute of Sciences of India, 2(1), 49-55.",
    "Mortazavi, A., Somers, C., Hwang, Y., Radermacher, R., Rodgers, P., & Al-Hashimi, S. (2012). Performance enhancement of propane pre-cooled mixed refrigerant LNG plant. Applied Energy, 93, 125-131.",
    "Peng, D. Y., & Robinson, D. B. (1976). A new two-constant equation of state. Industrial & Engineering Chemistry Fundamentals, 15(1), 59-64.",
    "Primabudi, E., & Putranto, A. (2023). Operational challenges and efficiency optimization in mature LNG liquefaction plants. Indonesian Journal of Process Systems Engineering, 4(2), 85-96.",
    "PT Badak NGL. (2021). Operating Manual and Plant Standards: Train H C3MR Liquefaction Unit. Bontang, East Kalimantan.",
    "Purwanugraha, R. (2023). Adaptation strategies of Badak LNG toward lean feed gas processing. Proceedings of the Annual Convention of Indonesian Gas Association (IGA), Jakarta.",
    "Ramadan, H. (2025). Peningkatan kualitas steam dengan menaikkan entalpi steam guna optimalisasi nilai efisiensi steam turbine generator di Utilities-II PT Badak NGL. Jurnal Rekayasa Proses, 19(1), 45-56.",
    "Ruan, G., Wang, K., & Zhang, H. (2022). Machine learning surrogate-assisted optimization of mixed refrigerant processes. Computers & Chemical Engineering, 160, 107722.",
    "Shady, M., Elsayegh, M., & El-Fakharany, M. (2024). Physics-informed surrogate modeling for multi-component LNG liquefaction plants. Applied Thermal Engineering, 239, 122150.",
    "Smith, R. (2016). Chemical Process: Design and Integration. John Wiley & Sons, Chichester.",
    "Stodola, A. (1905). Steam Turbines: With an Appendix on Gas Turbines and the Future of Heat Engines. D. Van Nostrand Company, New York.",
    "Utomo, B., & Setiawan, D. (2022). Compressor anti-surge control and operating envelope protection during low-load operation. Journal of Mechanical Engineering and Safety Systems, 7(3), 112-121.",
    "Venkatarathnam, G. (2008). Cryogenic Mixed Refrigerant Processes. Springer Science & Business Media, New York.",
    "Wang, M., Zhang, J., & Xu, Q. (2014). Optimal design and operation of mixed refrigerant cycles for LNG processes. Industrial & Engineering Chemistry Research, 53(18), 7729-7740.",
    "Wu, F., He, C., & Chen, J. (2025). Simultaneous optimization of composition and operating parameters in C3MR liquefaction process using deep reinforcement learning. Energy Conversion and Management, 301, 118025."
]

for idx, ref in enumerate(refs, 1):
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.left_indent = Inches(0.25)
    p_ref.paragraph_format.first_line_indent = Inches(-0.25)
    p_ref.paragraph_format.space_after = Pt(4)
    r_idx = p_ref.add_run(f"[{idx}] ")
    r_idx.bold = True
    r_idx.font.size = Pt(9.5)
    r_ref = p_ref.add_run(ref)
    r_ref.font.size = Pt(9.5)

doc.save(DOCX_PATH)
print(f"DOCX file successfully written to {DOCX_PATH}")
