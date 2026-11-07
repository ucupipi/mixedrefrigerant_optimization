import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

LEDGER_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\DATA_LEDGER.json"
ABSTRACT_DOCX_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\Mukhammad Yusuf Iqbal et al.docx"
ABSTRACT_MD_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_Abstrak_PNJ.md"

with open(LEDGER_PATH, "r", encoding="utf-8") as f:
    L = json.load(f)

def id_fmt(val, dec=1):
    if dec == 0:
        return f"{round(val):,}".replace(",", ".")
    s = f"{val:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

doc = docx.Document()

# Margins 1 inch
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Base Normal Style
normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(11)
normal_style.font.color.rgb = RGBColor(0, 0, 0)

# Title
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_title = p_title.add_run(
    "OPTIMASI CAMPURAN REFRIGERAN BERBASIS MACHINE LEARNING DENGAN PEMBATAS FISIKA "
    "UNTUK MEREDUKSI DAYA KOMPRESI DAN KONSUMSI BAHAN BAKAR PADA KILANG BADAK LNG"
)
r_title.bold = True
r_title.font.size = Pt(13)
p_title.paragraph_format.space_after = Pt(10)

# Authors (5 members)
p_authors = doc.add_paragraph()
p_authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_authors = p_authors.add_run("Mukhammad Yusuf Iqbal¹*, Afdal Elang Arifin², Dewi Putri Rahmawati³, Bilqiis Dara Ramadhan⁴, Hizkia Dhiego Gurning⁵\n")
r_authors.bold = True
r_authors.font.size = Pt(11)

r_affil = p_authors.add_run("¹*²³⁴⁵Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Depok 16425, Jawa Barat, Indonesia\n*Email Korespondensi: mukhammad.yusuf.iqbal.tm23@stu.pnj.ac.id")
r_affil.font.size = Pt(9.5)
r_affil.italic = True
p_authors.paragraph_format.space_after = Pt(14)

def add_section(heading, text):
    h = doc.add_paragraph()
    rh = h.add_run(heading)
    rh.bold = True
    rh.font.size = Pt(11)
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(2)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rp = p.add_run(text)
    rp.font.size = Pt(10.5)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)

urgensi_text = (
    "Proses pencairan gas alam berbasis Propane-Precooled Mixed Refrigerant (C3MR) pada PT Badak NGL menyerap 30–40% dari total konsumsi energi kilang. "
    "Sejak tahun 2017, kilang menghadapi tantangan penurunan laju alir gas umpan (feed gas turndown) dan pergeseran komposisi menjadi lebih lean (>89 mol% metana). "
    f"Evaluasi terhadap 720.734 baris data riil DCS Train H periode 2025–2026 menunjukkan bahwa penurunan laju umpan sebesar 53,5% (dari 399,74 t/jam ke 185,82 t/jam) "
    f"hanya direspons oleh penurunan sirkulasi Mixed Refrigerant (MR) sebesar 26,0% (dari {id_fmt(L['baseload_P90']['mcr_circulation_baseline_t_h'], 1)} t/jam ke {id_fmt(L['underload_P10']['mcr_circulation_baseline_t_h'], 1)} t/jam). "
    f"Ketidaksesuaian sirkulasi ini memicu lonjakan konsumsi energi spesifik (Specific Energy Consumption/SEC) sebesar +49,2% (dari {id_fmt(L['baseload_P90']['sec_baseline_kWh_t'], 2)} menjadi {id_fmt(L['underload_P10']['sec_baseline_kWh_t'], 2)} kWh/t LNG), "
    "yang berdampak langsung pada pemborosan bahan bakar boiler dan peningkatan intensitas emisi karbon."
)

tujuan_text = (
    "Penelitian ini bertujuan untuk: (1) Mengembangkan kerangka kerja optimasi komposisi dan laju alir sirkulasi MR multikomponen (N2, C1, C2, C2H4, C3) berbasis Machine Learning yang terikat batasan ketat termodinamika dan mekanikal kilang tanpa investasi kapital (Zero CAPEX); "
    "(2) Mendekomposisikan penurunan daya poros kompresor total terhadap kebutuhan uap turbin penggerak riil; dan "
    "(3) Merumuskan satu formula resep MR optimal tunggal yang adaptif dan aman melintasi seluruh kuantil beban operasional (P10 hingga P90). "
    "Pertanyaan penelitian berfokus pada bagaimana mengintegrasikan data DCS historis dan batasan proses agar diperoleh formula refrigeran dengan efisiensi termal maksimum tanpa menimbulkan risiko crossover temperatur atau trip kompresor."
)

metode_text = (
    "Objek penelitian adalah unit pencairan C3MR Train H PT Badak NGL. Instrumen pengukuran memanfaatkan data Distributed Control System (DCS) Yokogawa Centum VP beresolusi 1 menit "
    "(720.734 data riil periode 2025–2026) yang dikelompokkan ke dalam tujuh kuantil beban operasional (P10–P90). "
    f"Ruang komposisi refrigeran dipetakan ke dalam ruang simpleks melalui transformasi Isometric Log-Ratio (ILR) dan dibatasi oleh elipsoid kepercayaan 95% jarak Mahalanobis (DM ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    "Model surrogate HistGradientBoostingRegressor (HGBR) berfitur pembatas monotonik dilatih untuk memprediksi pendekatan temperatur jepit MCHE (MITA), temperatur hisap kompresor (Tsuct), dan kebutuhan uap turbin penggerak. "
    "Validasi termodinamika multi-slice dilakukan menggunakan persamaan keadaan Peng-Robinson pada simulasi Aspen HYSYS."
)

temuan_text = (
    f"Optimasi menghasilkan satu formula MR optimal tunggal: {id_fmt(L['optimal_mcr_composition_mol_percent']['nitrogen_N2'], 2)} mol% N2, {id_fmt(L['optimal_mcr_composition_mol_percent']['methane_CH4'], 2)} mol% C1, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethane_C2H6'], 2)} mol% C2, {id_fmt(L['optimal_mcr_composition_mol_percent']['ethylene_C2H4'], 2)} mol% C2H4, dan {id_fmt(L['optimal_mcr_composition_mol_percent']['propane_C3H8'], 2)} mol% C3 (DM = {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_distance_DM'], 4)} ≤ {id_fmt(L['optimal_mcr_composition_mol_percent']['mahalanobis_threshold_95_percent'], 4)}). "
    f"Pada beban dasar (P90), penyesuaian sirkulasi ke {id_fmt(L['baseload_P90']['mcr_circulation_optimized_t_h'], 1)} t/jam memangkas SEC sebesar {id_fmt(L['baseload_P90']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['baseload_P90']['sec_optimized_kWh_t'], 2)} kWh/t LNG) dan menghemat uap turbin penggerak sebesar {id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_t_h'], 2)} t/jam ({id_fmt(L['baseload_P90']['driver_steam_consumption_reduction_percent'], 2)}%). "
    f"Pada beban rendah (P10), SEC turun {id_fmt(L['underload_P10']['sec_reduction_percent'], 2)}% (menjadi {id_fmt(L['underload_P10']['sec_optimized_kWh_t'], 2)} kWh/t LNG). "
    f"Secara tahunan ({id_fmt(L['plant_baseline']['operating_hours_per_year'], 1)} jam operasi), kerangka kerja ini membukukan penghematan daya poros terbobot sebesar {id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_kW'], 1)} kW ({id_fmt(L['annualized_impact']['operating_hours_weighted_power_reduction_percent'], 2)}%), "
    f"menghemat {id_fmt(L['annualized_impact']['annual_driver_steam_saved_t_yr'], 1)} ton uap/tahun, {id_fmt(L['annualized_impact']['annual_fuel_gas_saved_MNm3_yr'], 2)} juta Nm³/tahun bahan bakar gas boiler, "
    f"mereduksi {id_fmt(L['annualized_impact']['annual_co2_abatement_t_yr'], 1)} ton CO2/tahun, serta menghasilkan penghematan biaya operasional sebesar USD {id_fmt(L['annualized_impact']['annual_cost_savings_million_USD_yr'], 2)} Juta/tahun dengan investasi kapital nol (Zero CAPEX). "
    f"Seluruh batas keselamatan kilang terbukti aman (MITA ≥ {id_fmt(L['baseload_P90']['mita_optimized_degC'], 2)}°C, Tsuct ≥ {id_fmt(L['baseload_P90']['tsuct_optimized_degC'], 2)}°C, fraksi uap hisap VF = 1,0000)."
)

add_section("1. URGENSI PENELITIAN", urgensi_text)
add_section("2. TUJUAN DAN PERTANYAAN PENELITIAN", tujuan_text)
add_section("3. METODE PENELITIAN (Partisipan/Objek, Alat/Instrumen Pengukuran, dan Analisis Data)", metode_text)
add_section("4. RINGKASAN TEMUAN, KESIMPULAN, DAN IMPLIKASI PENELITIAN", temuan_text)

# Keywords
p_kw = doc.add_paragraph()
p_kw.paragraph_format.space_before = Pt(8)
r_kw_lbl = p_kw.add_run("Kata Kunci: ")
r_kw_lbl.bold = True
r_kw_lbl.font.size = Pt(10)
r_kw_val = p_kw.add_run("C3MR Liquefaction, Mixed Refrigerant, Physics-Constrained Machine Learning, Zero CAPEX, Badak LNG, Transisi Energi Berkelanjutan.")
r_kw_val.italic = True
r_kw_val.font.size = Pt(10)

doc.save(ABSTRACT_DOCX_PATH)
print(f"Extended Abstract docx successfully saved: {ABSTRACT_DOCX_PATH}")

# Also update Markdown version
md_content = f"""# EXTENDED ABSTRACT (ABSTRAK PANJANG)

**OPTIMASI MIXED REFRIGERANT BERBASIS MACHINE LEARNING UNTUK EFISIENSI ENERGI KILANG BADAK LNG**

**Mukhammad Yusuf Iqbal¹*, Afdal Elang Arifin², Dewi Putri Rahmawati³, Bilqiis Dara Ramadhan⁴, Hizkia Dhiego Gurning⁵**  
¹*²³⁴⁵Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Depok 16425, Jawa Barat, Indonesia  
*Email Korespondensi: mukhammad.yusuf.iqbal.tm23@stu.pnj.ac.id  

---

### 1. URGENSI PENELITIAN
{urgensi_text}

### 2. TUJUAN DAN PERTANYAAN PENELITIAN
{tujuan_text}

### 3. METODE PENELITIAN (Partisipan/Objek, Alat/Instrumen Pengukuran, dan Analisis Data)
{metode_text}

### 4. RINGKASAN TEMUAN, KESIMPULAN, DAN IMPLIKASI PENELITIAN
{temuan_text}

**Kata Kunci:** *C3MR Liquefaction, Mixed Refrigerant, Physics-Constrained Machine Learning, Zero CAPEX, Badak LNG, Transisi Energi Berkelanjutan.*
"""

with open(ABSTRACT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Extended Abstract md successfully saved: {ABSTRACT_MD_PATH}")
