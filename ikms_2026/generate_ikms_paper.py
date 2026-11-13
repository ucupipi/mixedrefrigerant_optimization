# Runner for building full paper (.docx and .md)
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
from md_writer import write_markdown_paper

TEMPLATE_PATH = r"ikms_2026/Template Paper IKMS 2026.docx"
OUTPUT_DOCX = r"ikms_2026/IKMS2026_FullPaper_PNJ_Final.docx"
OUTPUT_MD = r"ikms_2026/IKMS2026_FullPaper_PNJ_Final.md"
FIGURES_DIR = r"ikms_2026/figures"

def set_cell_margins(cell, top=50, bottom=50, left=70, right=70):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)

def set_table_header_bottom_border(row):
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

def add_p(doc, text="", font_size=10, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(font_size)
        r.font.bold = bold
        r.font.italic = italic
    return p

def add_heading_1(doc, text):
    return add_p(doc, text, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=3)

def add_heading_2(doc, text):
    return add_p(doc, text, font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=2)

def add_figure(doc, img_name, caption_text, width_inch=5.4):
    img_path = os.path.join(FIGURES_DIR, img_name)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture(img_path, width=Inches(width_inch))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(6)
        p_cap.paragraph_format.line_spacing = 1.0
        
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(9.5)
        r_cap.font.bold = True
    else:
        print(f"Warning: Figure not found at {img_path}")

def add_equation_row(doc, eq_text, eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Cm(14.5)
    tbl.columns[1].width = Cm(2.0)
    
    tblPr = tbl._tbl.tblPr
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="none"/>\n'
        f'  <w:bottom w:val="none"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)
    
    cell_eq = tbl.rows[0].cells[0]
    cell_num = tbl.rows[0].cells[1]
    
    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_eq.paragraph_format.space_before = Pt(2)
    p_eq.paragraph_format.space_after = Pt(2)
    p_eq.paragraph_format.line_spacing = 1.0
    r_eq = p_eq.add_run(eq_text)
    r_eq.font.name = 'Times New Roman'
    r_eq.font.size = Pt(10)
    r_eq.font.italic = True
    
    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(2)
    p_num.paragraph_format.space_after = Pt(2)
    p_num.paragraph_format.line_spacing = 1.0
    r_num = p_num.add_run(f"({eq_num})")
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(10)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(2)
    p_after.paragraph_format.line_spacing = 1.0

def build_paper():
    doc = docx.Document(TEMPLATE_PATH)
    
    for p in list(doc.paragraphs):
        p._p.getparent().remove(p._p)
    for t in list(doc.tables):
        t._tbl.getparent().remove(t._tbl)
        
    sec = doc.sections[0]
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.0)
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    
    footer = sec.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f_run = f_p.add_run()
    f_run.font.name = 'Times New Roman'
    f_run.font.size = Pt(10)
    f_p_xml = f_p._p
    fld = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    f_p_xml.append(fld)

    # 1. TITLE
    add_p(doc, "Optimasi Komposisi dan Laju Sirkulasi Mixed Refrigerant Berbasis Machine Learning untuk Efisiensi Energi Kilang Badak LNG", 
          font_size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    
    # 2. AUTHORS
    add_p(doc, "Bilqiis Dara Ramadhan Sasongko¹*, Mukhammad Yusuf Iqbal¹, Hizkia Dhiego Gurning¹, Afdal Elang Arifin¹", 
          font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=3)
    
    # 3. AFFILIATIONS
    add_p(doc, "¹Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Jl. Prof. DR. G.A. Siwabessy, Kukusan, Kec. Beji, Kota Depok, Jawa Barat 16425, Indonesia", 
          font_size=8, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p(doc, "*Penulis korespondensi: bilqiiisdara@gmail.com", 
          font_size=8, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    
    # 4. ABSTRAK (INDONESIAN - 228 WORDS)
    add_p(doc, "Abstrak", font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    abs_id = (
        "Sistem propane-precooled mixed refrigerant (C3MR) menyumbang 59,3% konsumsi energi internal di Kilang Badak LNG. "
        "Sistem ini awalnya dirancang untuk batas gas umpan kaya 91,6 mol% metana (tercatat 88,1 mol% pada 2017). Namun, data DCS dan "
        "kromatografi gas 2024–2026 menunjukkan kilang kini beroperasi pada lean gas hingga 94,5 mol% metana. Pergeseran ini menaikkan beban "
        "pendinginan spesifik Main Cryogenic Heat Exchanger (MCHE) dari 637,6 menjadi 652,9 kJ/kg, sehingga memicu sirkulasi mixed refrigerant "
        "(MR) berlebih dan peningkatan konsumsi energi spesifik (SEC). Penelitian ini mengembangkan kerangka optimasi gabungan komposisi dan "
        "laju sirkulasi MR berbasis machine learning berpembatas fisika melintasi seluruh spektrum beban operasi kilang (258,4–384,0 ton/jam umpan). "
        "Dataset primer mencakup 44.641 data menit DCS dan 2.531 sampel kromatografi gas rutin shift. Pemetaan simpleks menerapkan transformasi "
        "Isometric Log-Ratio (ILR) berpembatas elipsoid Mahalanobis 95% (DM <= 3,0802). Model surrogate HistGradientBoostingRegressor berpembatas "
        "monotonik mencapai R2 uji 0,6677–0,9998 dengan relative error (NMAE) < 1,0% (kesalahan daya poros < 0,83 MW). Formula MR optimal tunggal "
        "(3,67% N2; 51,26% C1; 42,62% C2; 0,44% C2H4; 2,01% C3; DM = 3,0762) memangkas SEC beban puncak sebesar 12,60% (dari 448,2 menjadi "
        "391,8 kWh/ton LNG) dan menghemat uap turbin 63,17 ton/jam. Secara tahunan terbobot pada 7.849,9 jam operasi, strategi ini menghemat "
        "daya poros kompresor total 14,805 MW (12,20%, 116.215,3 MWh/tahun)—terdekomposisi atas kompresor MCR langsung 13,251 MW (89,51%) dan "
        "kompresor propana 1,554 MW (10,49%). Dampak utilitas mencakup penghematan uap boiler 449.087,3 ton/tahun, bahan bakar gas 34,60 juta "
        "Nm3/tahun (setara USD 8,42 Juta/tahun pada paritas gas bahan bakar atau USD 14,90 Juta/tahun pada paritas ekspor LNG), serta mereduksi "
        "73.845,9 ton CO2/tahun dengan seluruh batas keselamatan operasional kilang terbukti aman (MITA >= 7,17 °C, Tsuct >= -41,76 °C, zero CAPEX)."
    )
    add_p(doc, abs_id, font_size=10, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4)
    
    p_kw_id = add_p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=10)
    r1 = p_kw_id.add_run("Kata kunci: ")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(10)
    r1.font.bold = True
    r2 = p_kw_id.add_run("C3MR, dekarbonisasi, efisiensi energi spesifik, lean feed gas, machine learning, optimasi mixed refrigerant")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10)
    
    # 5. ABSTRACT (ENGLISH - 236 WORDS)
    add_p(doc, "Abstract", font_size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    abs_en = (
        "The propane-precooled mixed refrigerant (C3MR) system accounts for 59.3% of internal energy consumption at Badak LNG. "
        "Originally designed for a rich feed gas threshold of 91.6 mol% methane (recorded at 88.1 mol% in 2017), DCS telemetry and gas "
        "chromatography records from 2024–2026 indicate persistent operation under lean feed conditions reaching 94.5 mol% methane. "
        "This shift increased the main cryogenic heat exchanger (MCHE) specific cooling duty from 637.6 to 652.9 kJ/kg, prompting mixed "
        "refrigerant (MR) over-circulation and elevating specific energy consumption (SEC). This study develops a physics-constrained machine "
        "learning framework for joint optimization of MR composition and circulation rate across the full recorded operating spectrum "
        "(258.4–384.0 tons/hour feed gas). The primary dataset comprises 44,641 minute-level DCS observations and 2,531 shift-level gas chromatography "
        "samples. Simplex compositional mapping employs Isometric Log-Ratio (ILR) transformation bounded by a 95% confidence Mahalanobis distance "
        "ellipsoid (DM <= 3.0802). Monotonically constrained HistGradientBoostingRegressor models achieve test R2 of 0.6677–0.9998 with normalized "
        "mean absolute error (NMAE) < 1.0% (shaft power error < 0.83 MW). A single optimal MR formulation (3.67% N2, 51.26% C1, 42.62% C2, "
        "0.44% C2H4, 2.01% C3; DM = 3.0762) reduces baseload SEC by 12.60% (from 448.2 to 391.8 kWh/ton LNG) and saves 63.17 tons/hour of turbine steam. "
        "Across 7,849.9 annual operating hours, this yields a total mean compressor shaft power saving of 14.805 MW (12.20%, 116,215.3 MWh/year)—transparently "
        "decomposed into direct MCR compression of 13.251 MW (89.51%) and propane precooling of 1.554 MW (10.49%). The utility impact conserves "
        "449,087.3 tons/year of boiler steam and 34.60 million Nm3/year of fuel gas (worth USD 8.42 million/year under fuel gas parity or USD 14.90 "
        "million/year under LNG export parity), while cutting 73,845.9 tons CO2/year under strictly verified plant safety constraints (MITA >= 7.17 °C, "
        "Tsuct >= -41.76 °C, zero CAPEX)."
    )
    add_p(doc, abs_en, font_size=10, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4)
    
    p_kw_en = add_p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    r1_en = p_kw_en.add_run("Keywords: ")
    r1_en.font.name = 'Times New Roman'
    r1_en.font.size = Pt(10)
    r1_en.font.bold = True
    r2_en = p_kw_en.add_run("C3MR, decarbonization, energy efficiency, lean feed gas, machine learning, mixed refrigerant optimization")
    r2_en.font.name = 'Times New Roman'
    r2_en.font.size = Pt(10)
    
    # 6. PENDAHULUAN
    add_heading_1(doc, "PENDAHULUAN")
    
    p1 = (
        "Pencairan gas alam (Liquefied Natural Gas/LNG) memegang peranan krusial dalam rantai pasok energi global sebagai jembatan strategis "
        "transisi menuju sistem energi rendah karbon [1], [2]. Proses pencairan membutuhkan energi pendinginan dalam jumlah masif untuk mendinginkan "
        "gas alam dari temperatur lingkungan hingga mencapai -162 °C pada tekanan atmosferik [1]. Di Indonesia, PT Badak NGL di Bontang, Kalimantan Timur, "
        "mengoperasikan proses Propane-Precooled Mixed Refrigerant (C3MR) yang menyumbang 59,3% dari total konsumsi energi internal kilang [3], [4]. "
        "Sistem pencairan ini awalnya dirancang untuk memproses rich gas dengan batas desain kandungan metana maksimum sebesar 91,6 mol%. "
        "Dokumentasi historis operasional mencatat kandungan metana gas umpan kaya sebesar 88,1 mol% pada tahun 2017 [3], [4]. Namun, seiring "
        "penuaan reservoir gas di Kalimantan Timur, data operasional DCS dan kromatografi gas periode 2024–2026 membuktikan kilang beroperasi terus-menerus "
        "menghadapi lean gas dengan kandungan metana mencapai 94,5 mol% [4], [5]. Perubahan komposisi ini menggeser kurva pendinginan dan menaikkan "
        "specific cooling duty pada Main Cryogenic Heat Exchanger (MCHE) sebesar 2,40% (dari 637,6 menjadi 652,9 kJ/kg LNG), yang secara langsung "
        "menurunkan efisiensi termal kilang (Plant Thermal Efficiency) [5], [6]."
    )
    add_p(doc, p1)
    
    p2 = (
        "Untuk memenuhi kebutuhan beban pendinginan pada kondisi gas lean tersebut, operator kilang menyesuaikan laju sirkulasi refrigeran campuran "
        "(MR) untuk memastikan target temperatur LNG rundown tercapai. Analisis terhadap 44.641 rekaman data operasional DCS Train H periode 2024–2026 "
        "mengungkapkan bahwa laju sirkulasi MCR dipertahankan pada kisaran 514,2–691,8 ton/jam. Pada kondisi turndown rendah (laju umpan turun ke "
        "258,4 ton/jam), laju sirkulasi MCR tertahan di batas aman mekanikal kompresor sentrifugal 4K-2/3 (anti-surge flow floor >= 480,0 ton/jam) "
        "serta keharusan menghindari interlock trip dingin Temperature Alarm Low (TAL) pada suction drum (Tsuct >= -45,0 °C) [7]. Akibatnya, Specific "
        "Energy Consumption (SEC) meningkat dari 448,2 kWh/ton LNG pada beban puncak menjadi 505,1 kWh/ton LNG pada beban turndown (+12,7%). "
        "Kondisi over-sirkulasi ini memperbesar konsumsi uap penggerak turbin dan memicu emisi gas rumah kaca yang tidak perlu."
    )
    add_p(doc, p2)
    
    add_figure(doc, "image12.png", "Gambar 1. Efisiensi termal kilang historis PT Badak NGL terhadap pergeseran gas umpan lean [3]", width_inch=4.5)
    
    p3 = (
        "Penelitian optimasi terdahulu pada siklus C3MR umumnya memiliki keterbatasan saat diterapkan pada fasilitas kilang berskala industri. "
        "Pendekatan optimasi berbasis algoritma metaheuristik murni (seperti genetic algorithm atau particle swarm optimization pada simulator statis) "
        "sering menghasilkan resep refrigeran teoritis yang memicu temperature crossover pada penukar panas kriogenik atau melanggar batas operasional "
        "kompresor [8]–[10]. Di sisi lain, pendekatan data-driven tanpa pembatas hukum termodinamika rentan menghasilkan prediksi yang tidak realistis [11]–[14]. "
        "Selain itu, perlakuan komposisi fraksi mol kimia pada ruang Euclidean standar melanggar batasan geometris simpleks (total fraksi mol wajib 100%), "
        "yang menimbulkan bias korelasi palsu (spurious correlation) [15]–[17]. Yang tidak kalah penting, banyak studi tidak menyajikan dekomposisi "
        "daya secara transparan antara kompresor MCR langsung dan kompresor propana prapendinginan, serta mengabaikan integrasi neraca uap utilitas."
    )
    add_p(doc, p3)
    
    p4 = (
        "Untuk menjawab tantangan tersebut, penelitian ini mengembangkan kerangka kerja optimasi gabungan komposisi multikomponen dan laju sirkulasi "
        "mixed refrigerant berbasis Machine Learning berpembatas fisika yang dikalibrasi langsung dengan telemetri DCS Train H PT Badak NGL periode 2024–2026. "
        "Kontribusi utama penelitian ini meliputi: (1) Formulasi satu resep komposisi MR optimal tunggal yang terikat ketat dalam elipsoid Jarak Mahalanobis "
        "95% (DM <= 3,0802) sehingga terbukti dapat dioperasikan secara aman melintasi seluruh spektrum beban kilang; (2) Penerapan arsitektur model surrogate "
        "HistGradientBoostingRegressor (HGBR) berfitur batasan monotonik fisika searah; (3) Evaluasi termodinamika diskritisasi penukar panas kriogenik "
        "berdasarkan Peng-Robinson EOS untuk memastikan ketiadaan crossover temperatur (MITA >= 1,50 °C); (4) Dekomposisi daya kompresor secara transparan "
        "antara penggerak MCR langsung (4KT-2/3) dan kompresor propana (4KT-1) beserta konversi ke neraca uap boiler; dan (5) Solusi operasional tanpa biaya "
        "kapital (Zero CAPEX) yang dapat diadopsi langsung sebagai panduan kontrol supervisori DCS kilang."
    )
    add_p(doc, p4)
    
    # 7. METODE
    add_heading_1(doc, "METODE")
    
    # SUBBAB 2.1
    add_heading_2(doc, "2.1 Operasi Kilang, Akuisisi Data DCS, dan Penyaringan Kondisi Tunak")
    p_met1 = (
        "Metodologi penelitian dirancang ke dalam empat pilar yang saling terintegrasi (Gambar 2): (1) Akuisisi data operasional DCS dan pra-pemrosesan kondisi "
        "tunak; (2) Pemetaan geometri simpleks ILR dan pelatihan model surrogate Machine Learning berpembatas fisika; (3) Formulasi optimasi multivariabel "
        "dan verifikasi termodinamika simulator; serta (4) Evaluasi tekno-ekonomi, dekomposisi energi, dan akuntansi emisi karbon. Dataset primer dihimpun dari "
        "sistem historian DCS Yokogawa Centum VP Train H Kilang Badak LNG periode 2024–2026, mencakup 44.641 baris rekaman telemetri berinterval 1 menit "
        "pada 172 tag instrumen. Penyaringan data membuang periode transien ekstrem, trip, dan start-up, menghasilkan 43.334 menit operasi stabil (steady-state). "
        "Karakterisasi komposisi refrigeran didukung oleh 2.531 sampel analisis kromatografi gas (GC) rutin laboratorium per shift dari suction drum MCR 4C-8. "
        "Untuk mengevaluasi seluruh spektrum beban operasi secara kontinu, data dikelompokkan ke dalam 100 medoid persentil beban (P1–P100) melintasi rentang "
        "laju alir umpan 258,4 hingga 384,0 ton/jam. Diagram alir proses (PFD) sistem pencairan C3MR Train H disajikan pada Gambar 3."
    )
    add_p(doc, p_met1)
    
    add_figure(doc, "image6.png", "Gambar 2. Alur metodologi penelitian optimasi mixed refrigerant berbasis machine learning", width_inch=4.8)
    add_figure(doc, "image5.png", "Gambar 3. Diagram alir proses (PFD) sistem pencairan C3MR Train H PT Badak NGL [3]", width_inch=5.8)
    
    # SUBBAB 2.2
    add_heading_2(doc, "2.2 Geometri Komposisi Simpleks ILR dan Pemodelan Machine Learning Berpembatas Fisika")
    p_met2a = (
        "Refrigeran campuran (MR) pada siklus C3MR Kilang Badak tersusun atas lima komponen kimia: Nitrogen (N2), Metana (C1), Etana (C2), Etilena (C2H4), "
        "dan Propana (C3). Fraksi mol komponen terikat pada ruang simpleks tertutup S⁵ di mana jumlah seluruh komponen wajib sama dengan 100%. Untuk mengatasi "
        "kendala matematis keterikatan simpleks pada ruang Euclidean standar [15], fraksi mol komponen ditransformasikan ke koordinat Euclidean tak terikat "
        "menggunakan transformasi Aitchison Isometric Log-Ratio (ILR) [16]:"
    )
    add_p(doc, p_met2a)
    
    add_equation_row(doc, "z_i = sqrt((D - i) / (D - i + 1)) * ln( x_i / (prod_(j=i+1)^D x_j)^(1 / (D - i)) )", "1")
    
    p_met2b = (
        "di mana D = 5 adalah jumlah komponen refrigeran, menghasilkan D - 1 = 4 koordinat ILR independen. Untuk memastikan formula MR yang direkomendasikan "
        "berada di dalam domain operasional kilang yang realistis dan teruji, ditetapkan batasan elipsoid kepercayaan 95% menggunakan Jarak Mahalanobis (DM) [17]:"
    )
    add_p(doc, p_met2b)
    
    add_equation_row(doc, "D_M = sqrt( (z - mu)^T * Sigma^(-1) * (z - mu) ) <= 3,0802", "2")
    
    p_met2c = (
        "di mana mu dan Sigma masing-masing adalah vektor rata-rata dan matriks kovarian dari 2.531 sampel komposisi historis pada koordinat ILR, dan 3,0802 "
        "merupakan nilai kritis distribusi Chi-kuadrat dengan 4 derajat kebebasan pada tingkat signifikansi 95% (chi²_(0.95, 4)). Permukaan respon termodinamika "
        "dimodelkan dengan arsitektur HistGradientBoostingRegressor (HGBR) berfitur batasan monotonik fisika (monotonic_cst). Batasan monotonik memastikan "
        "bahwa peningkatan laju sirkulasi MR selalu menaikkan daya kompresi dan konsumsi uap secara konsisten tanpa artefak numerik [13]. Dataset dipartisi "
        "dengan rasio 80:20 (pelatihan independen dan pengujian) dengan validasi silang untuk memprediksi variabel daya poros, aliran uap, suhu hisap, dan pendekatan termal MCHE."
    )
    add_p(doc, p_met2c)
    
    # SUBBAB 2.3
    add_heading_2(doc, "2.3 Formulasi Optimasi Komposisi, Laju Sirkulasi MR, dan Validasi Termodinamika")
    p_met3a = (
        "Fungsi objektif optimasi adalah meminimalkan Specific Energy Consumption (SEC, kWh/ton LNG) melintasi seluruh spektrum beban kilang:"
    )
    add_p(doc, p_met3a)
    
    add_equation_row(doc, "min_(x, m_dot_MR)  SEC = W_dot_(total, C3MR) / m_dot_LNG", "3")
    
    p_met3b = (
        "dengan batasan operasional dan keselamatan kilang meliputi: (a) Pendekatan temperatur jepit minimum MITA MCHE >= 1,50 °C untuk mencegah crossover; "
        "(b) Suhu hisap kompresor Tsuct >= -45,0 °C (batas interlock TAL); (c) Fraksi uap hisap VF = 1,0000 (100% uap kering bebas droplet cairan); "
        "(d) Laju alir hisap kompresor 4K-2 >= 480,0 ton/jam (batas aman surge floor); dan (e) Jarak Mahalanobis DM <= 3,0802. Evaluasi termodinamika "
        "dilakukan secara ketat menggunakan Peng-Robinson Equation of State (PR-EOS) untuk memverifikasi profil suhu komposit pendinginan di dalam MCHE 5E-1 [18]–[21]."
    )
    add_p(doc, p_met3b)
    
    # SUBBAB 2.4
    add_heading_2(doc, "2.4 Metodologi Evaluasi Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Emisi Karbon")
    p_met4a = (
        "Daya poros isentropik kompresor sentrifugal dan dekomposisi batas sistem Train C3MR dirumuskan melalui persamaan rekayasa proses [22], [23]:"
    )
    add_p(doc, p_met4a)
    
    add_equation_row(doc, "W_dot_shaft = (m_dot * Delta h_s) / eta_p", "4")
    add_equation_row(doc, "Delta W_dot_(total, C3MR) = Delta W_dot_(MCR, direct) + Delta W_dot_(C3, precooling)", "5")
    
    p_met4b = (
        "di mana Delta W_dot_(MCR, direct) mencakup penghematan daya pada kompresor MCR 4KT-2 dan 4KT-3, sedangkan Delta W_dot_(C3, precooling) mencakup "
        "penghematan tidak langsung pada kompresor propana 4KT-1 akibat berkurangnya beban pendinginan MCR pada chiller propana (4E-7, 4E-8, 4E-9). "
        "Untuk menganalisis irreversibilitas termodinamika secara mendalam [24], eksergi destruksi MCHE dihitung menggunakan integral Riemann terdiskritisasi [25]:"
    )
    add_p(doc, p_met4b)
    
    add_equation_row(doc, "E_dot_(D, MCHE) = T_0 * sum_(i=1)^N Delta Q_i * ( 1 / T_(cold, i) - 1 / T_(hot, i) )", "6")
    add_equation_row(doc, "E_dot_(D, comp) = W_dot_shaft * (1 - eta_s)", "7")
    
    p_met4c = (
        "Hubungan antara penghematan uap turbin penggerak terhadap kebutuhan bahan bakar boiler dimodelkan melalui regresi linear OLS terkalibrasi DCS "
        "dengan koefisien marjinal 77,0424 Nm³ fuel gas per ton uap (R² = 0,9646). Perhitungan dampak tahunan dihitung terbobot pada 7.849,9 jam operasi "
        "historis kilang (ketersediaan 89,61%). Emisi Scope 1 dihitung menggunakan faktor stoikiometri pembakaran primer sebesar 164,44 kg CO2 per ton uap "
        "serta sensitivitas sekunder IPCC sebesar 76,63 kg CO2 per ton uap."
    )
    add_p(doc, p_met4c)
    
    # 8. HASIL DAN PEMBAHASAN
    add_heading_1(doc, "HASIL DAN PEMBAHASAN")
    
    # SUBBAB 3.1
    add_heading_2(doc, "3.1 Karakterisasi Baseline Operasi Kilang dan Profil Pasokan Gas Umpan")
    p_res1 = (
        "Tabel 1 merangkum parameter operasi aktual Kilang Badak Train H melintasi spektrum beban dari kondisi turndown terendah (P1, 258,4 ton/jam umpan) "
        "hingga beban puncak (P100, 384,0 ton/jam umpan) berdasarkan data DCS. Data membuktikan bahwa saat laju umpan gas mentah menurun 32,7% (dari "
        "384,0 ton/jam ke 258,4 ton/jam), laju sirkulasi MCR baseline hanya berkurang 25,7% (dari 691,8 ton/jam ke 514,2 ton/jam). Akibatnya, rasio sirkulasi "
        "MCR terhadap umpan gas meningkat dari 1,802 kg/kg pada beban puncak menjadi 1,990 kg/kg pada kondisi turndown (+10,4%). Fenomena over-sirkulasi "
        "relatif ini memicu kenaikan SEC sebesar +12,7% (dari 448,2 ke 505,1 kWh/ton LNG) sebagaimana divisualisasikan pada Gambar 4."
    )
    add_p(doc, p_res1)
    
    # TABLE 1
    add_p(doc, "Tabel 1. Parameter Baseline Operasional Train H Kilang Badak LNG Melintasi Spektrum Beban Operasi Aktual", font_size=10, bold=True, space_before=6, space_after=2)
    tbl1 = doc.add_table(rows=10, cols=9)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl1.autofit = False
    set_table_borders(tbl1)
    
    t1_widths = [Cm(3.8), Cm(1.7), Cm(1.4), Cm(1.4), Cm(1.4), Cm(1.4), Cm(1.4), Cm(1.5), Cm(1.6)]
    t1_data = [
        ["Parameter Operasi", "Satuan", "P1 (Turndown)", "P10", "P25", "P50 (Median)", "P75", "P90", "P100 (Puncak)"],
        ["Laju Gas Umpan Mentah (H1FI0009)", "kNm³/jam", "342,55", "430,90", "447,29", "459,80", "479,65", "500,76", "509,02"],
        ["Laju Gas Umpan Mentah", "ton/jam", "258,41", "325,05", "337,41", "346,85", "361,82", "377,75", "383,98"],
        ["Laju Gas Terolah (H3FI0004)", "kNm³/jam", "273,56", "354,67", "364,57", "378,58", "393,13", "400,99", "409,39"],
        ["Laju Produksi LNG Estimasi", "ton/jam", "194,84", "245,09", "254,41", "261,53", "272,82", "284,82", "289,52"],
        ["Laju Sirkulasi MCR Baseline", "ton/jam", "514,18", "648,25", "662,75", "675,07", "680,05", "687,06", "691,80"],
        ["Rasio MCR / Gas Umpan", "kg/kg", "1,990", "1,994", "1,964", "1,946", "1,880", "1,819", "1,802"],
        ["Laju Uap Turbin Penggerak", "ton/jam", "382,09", "450,21", "461,27", "471,78", "482,32", "497,89", "503,04"],
        ["Daya Poros Kompresor Total", "MW", "98,41", "116,05", "118,89", "121,74", "124,30", "128,44", "129,77"],
        ["Konsumsi Energi Spesifik (SEC)", "kWh/t LNG", "505,09", "473,51", "467,31", "465,51", "455,62", "450,95", "448,23"]
    ]
    for r_idx, row in enumerate(tbl1.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = t1_widths[c_idx]
            set_cell_margins(cell, top=35, bottom=35, left=45, right=45)
            cell.text = t1_data[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(8.5)
                if r_idx == 0:
                    run.font.bold = True
    set_table_header_bottom_border(tbl1.rows[0])
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)
    
    add_figure(doc, "image4.png", "Gambar 4. Hubungan konsumsi energi spesifik (SEC) terhadap laju produksi LNG melintasi seluruh spektrum operasi kilang", width_inch=4.5)
    
    # SUBBAB 3.2
    add_heading_2(doc, "3.2 Validasi Akurasi Model Surrogate Machine Learning dan Batasan Ruang Operasi")
    p_res2 = (
        "Evaluasi kinerja model surrogate HGBR disajikan pada Tabel 2. Seluruh model dilatih menggunakan pemisahan data 80:20 (34.667 sampel latih dan "
        "8.667 sampel uji independen) dan diverifikasi memenuhi seluruh kriteria disiplin rekayasa (R² uji >= 0,60, relative error NMAE < 1,0%, dan "
        "korelasi fitur |r| >= 0,30). Model daya poros C3MR total mencapai R² uji = 0,9557 dengan MAE hanya 0,8247 MW (NMAE = 0,677%). Dekomposisi daya "
        "membuktikan model MCR langsung mencapai R² = 0,9565 (MAE 0,6588 MW, NMAE 0,851%) dan kompresor propana mencapai R² = 0,7809 (MAE 0,3727 MW, "
        "NMAE 0,839%). Model kebutuhan uap turbin penggerak menunjukkan presisi sangat tinggi dengan R² = 0,9997 (MAE 0,2726 ton/jam, NMAE 0,058%) untuk total "
        "uap dan R² = 0,9998 (MAE 0,1851 ton/jam, NMAE 0,062%) untuk turbin MCR langsung. Suhu suction drum diprediksi dengan R² = 0,6677 (MAE 0,3892 °C, "
        "NMAE 0,949%), sedangkan pendekatan temperatur jepit MCHE mencapai R² = 0,6761 (MAE 0,0657 °C, NMAE 0,952%). Selain itu, model konsumsi bahan bakar "
        "gas boiler berbasis neraca massa pembakaran menghasilkan R² = 0,9646 dengan slope terkalibrasi 77,0424 Nm³/ton uap. Parity plot pada Gambar 5 "
        "mengonfirmasi bahwa seluruh prediksi berkumpul rapat pada garis 45°, membuktikan bahwa model terbebas dari bias overfitting."
    )
    add_p(doc, p_res2)
    
    # TABLE 2
    add_p(doc, "Tabel 2. Metrik Evaluasi Model Surrogate Machine Learning pada Data Telemetri DCS Lapangan dan Termodinamika PR-EOS", font_size=10, bold=True, space_before=6, space_after=2)
    tbl2 = doc.add_table(rows=9, cols=8)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl2.autofit = False
    set_table_borders(tbl2)
    
    t2_widths = [Cm(3.4), Cm(1.1), Cm(3.2), Cm(1.6), Cm(1.3), Cm(1.4), Cm(1.8), Cm(2.8)]
    t2_data = [
        ["Variabel Target & Simbol", "Satuan", "Sumber Ground Truth", "Sampel Uji (N)", "Test R²", "Test MAE", "Relative Error (NMAE)", "Batasan Fisika"],
        ["Total C3MR Shaft Power", "MW", "Telemetri DCS 2024–2026", "8.667 data", "0,9557", "0,8247", "0,677%", "Monotonik umpan & MCR"],
        ["MCR Direct Shaft Power", "MW", "Telemetri DCS 4KT-2/3", "8.667 data", "0,9565", "0,6588", "0,851%", "Monotonik beban kompresor MCR"],
        ["Propane Precooling Power", "MW", "Telemetri DCS 4KT-1", "8.667 data", "0,7809", "0,3727", "0,839%", "Monotonik beban chiller C3"],
        ["Total Driver Steam Demand", "ton/jam", "Telemetri Uap DCS", "8.667 data", "0,9997", "0,2726", "0,058%", "Monotonik daya poros total"],
        ["MCR Direct Driver Steam", "ton/jam", "Transmitter H4FI029/30A", "8.667 data", "0,9998", "0,1851", "0,062%", "Monotonik daya poros MCR"],
        ["Suction Drum Temperature", "°C", "Transmitter H4TI004B", "8.664 data", "0,6677", "0,3892", "0,949%", "Batas TAL (>= -45,0 °C)"],
        ["MCHE Approach Pinch (MITA)", "°C", "NeqSim PR-EOS Slicing", "60 kasus", "0,6761", "0,0657", "0,952%", "Batas Crossover (>= 1,50 °C)"],
        ["Boiler Fuel Gas Demand", "Nm³/jam", "Neraca Massa Boiler OLS", "43.334 data", "0,9646", "312,4", "0,475%", "Slope 77,0424 Nm³/ton uap"]
    ]
    for r_idx, row in enumerate(tbl2.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = t2_widths[c_idx]
            set_cell_margins(cell, top=35, bottom=35, left=45, right=45)
            cell.text = t2_data[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(8.5)
                if r_idx == 0:
                    run.font.bold = True
    set_table_header_bottom_border(tbl2.rows[0])
    
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(0)
    p_sp2.paragraph_format.space_after = Pt(4)
    
    add_figure(doc, "image9.png", "Gambar 5. Parity plot evaluasi akurasi model surrogate HGBR terhadap data uji independen untuk empat variabel kunci proses", width_inch=5.4)
    
    # SUBBAB 3.3
    add_heading_2(doc, "3.3 Kinerja Optimasi Komposisi dan Laju Sirkulasi MR Melintasi Spektrum Beban Operasi Kilang")
    p_res3 = (
        "Optimasi gabungan multivariabel menghasilkan satu formula komposisi MR optimal tunggal: 3,6690 mol% N2; 51,2644 mol% C1; 42,6182 mol% C2; "
        "0,4423 mol% C2H4; dan 2,0061 mol% C3. Formula ini menghasilkan koordinat ILR xi = [-1,864701, -0,925767, 3,301385, 1,204936] dengan Jarak "
        "Mahalanobis DM = 3,0762. Nilai ini berada aman di dalam elipsoid kepercayaan 95% (DM <= 3,0802), membuktikan kelayakan operasionalnya pada kilang riil. "
        "Tabel 3 menyajikan perbandingan kinerja baseline terhadap hasil optimasi pada kondisi puncak (P100, 384,0 t/jam umpan), median (P50, 346,9 t/jam umpan), "
        "dan turndown (P1, 258,4 t/jam umpan). Pada beban puncak, laju sirkulasi MCR diturunkan dari 691,80 menjadi 504,76 ton/jam (-27,04%), yang memangkas daya "
        "poros total kompresor dari 129,77 menjadi 113,43 MW (-12,60%, hemat 16,35 MW). Penghematan ini menurunkan SEC dari 448,23 menjadi 391,77 kWh/ton LNG "
        "(-12,60%) serta menghemat konsumsi uap turbin sebesar 63,17 ton/jam (-12,56%). Pada beban median (P50), daya poros berkurang 15,29 MW (-12,56%) dan uap "
        "terhemat 59,10 ton/jam. Pada kondisi turndown (P1), sirkulasi MCR diturunkan ke 480,00 ton/jam (-6,65%), persis memenuhi batas aman flow floor anti-surge "
        "kompresor sentrifugal (>= 480,0 ton/jam), sehingga daya poros terhemat 2,83 MW (-2,87%) dan uap terhemat 10,92 ton/jam. Validasi termodinamika membuktikan "
        "bahwa MITA MCHE tetap terjaga aman di atas batas kritis (7,17 °C melintasi seluruh beban, jauh di atas ambang 1,50 °C), suhu hisap suction drum aman "
        "(-41,76 s.d. -38,56 °C, memiliki margin aman > 3,2 °C di atas TAL -45,0 °C), dan fraksi uap VF = 1,0000 (100% uap kering). Gambar 6 memperlihatkan kurva "
        "komposit pendinginan bebas crossover temperatur, dan Gambar 7 menunjukkan penurunan kurva SEC hasil optimasi melintasi seluruh spektrum beban."
    )
    add_p(doc, p_res3)
    
    # TABLE 3
    add_p(doc, "Tabel 3. Perbandingan Parameter Teknis Baseline vs Optimasi pada Beban Puncak, Median, dan Kondisi Turndown", font_size=10, bold=True, space_before=6, space_after=2)
    tbl3 = doc.add_table(rows=12, cols=8)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl3.autofit = False
    set_table_borders(tbl3)
    
    t3_widths = [Cm(3.8), Cm(1.4), Cm(1.8), Cm(1.8), Cm(1.6), Cm(1.8), Cm(1.8), Cm(1.6)]
    t3_data = [
        ["Parameter Operasional", "Satuan", "Baseline Puncak", "Optimasi Puncak", "Selisih (%)", "Baseline Turndown", "Optimasi Turndown", "Selisih (%)"],
        ["Laju Gas Umpan Mentah", "ton/jam", "383,98", "383,98", "0,00%", "258,41", "258,41", "0,00%"],
        ["Laju Sirkulasi MCR MCHE", "ton/jam", "691,80", "504,76", "-27,04%", "514,18", "480,00", "-6,65%"],
        ["Daya Poros Kompresor Total", "MW", "129,77", "113,43", "-12,60%", "98,41", "95,58", "-2,87%"],
        [" - Daya MCR Langsung (4KT-2/3)", "MW", "83,05", "68,35", "-17,70%", "62,62", "60,09", "-4,04%"],
        [" - Daya Propana (4KT-1)", "MW", "46,72", "45,08", "-3,52%", "35,79", "35,49", "-0,84%"],
        ["Konsumsi Energi Spesifik (SEC)", "kWh/t", "448,23", "391,77", "-12,60%", "505,09", "490,57", "-2,87%"],
        ["Konsumsi Uap Turbin Penggerak", "ton/jam", "503,04", "439,87", "-12,56%", "382,09", "371,17", "-2,86%"],
        ["Konsumsi Bahan Bakar Gas Boiler", "Nm³/jam", "38.755,0", "33.888,4", "-12,56%", "29.437,1", "28.595,5", "-2,86%"],
        ["Laju Emisi CO2 Scope 1", "ton/jam", "82,72", "72,33", "-12,56%", "62,83", "61,03", "-2,86%"],
        ["Pendekatan Jepit Minimum (MITA)", "°C", "8,85", "7,17", "-", "8,85", "7,17", "-"],
        ["Suhu Hisap Suction Drum (Tsuct)", "°C", "-41,76", "-41,76", "-", "-38,56", "-38,56", "-"]
    ]
    for r_idx, row in enumerate(tbl3.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = t3_widths[c_idx]
            set_cell_margins(cell, top=35, bottom=35, left=45, right=45)
            cell.text = t3_data[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(8.5)
                if r_idx == 0:
                    run.font.bold = True
    set_table_header_bottom_border(tbl3.rows[0])
    
    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(0)
    p_sp3.paragraph_format.space_after = Pt(4)
    
    add_figure(doc, "image7.png", "Gambar 6. Validasi termodinamika MCHE 5E-1 pada beban puncak: (a) Kurva komposit pendinginan T-Q; (b) Gaya dorong temperatur membuktikan bebas crossover dan MITA aman di atas batas 1,50 °C", width_inch=5.4)
    add_figure(doc, "image10.png", "Gambar 7. Perbandingan kurva SEC baseline operasi kilang vs. optimasi melintasi seluruh spektrum laju produksi LNG", width_inch=4.8)
    
    p_res3b = (
        "Untuk menjamin kelayakan implementasi transisi komposisi di lapangan tanpa mengganggu stabilitas operasi, dirancang prosedur dinamis make-up "
        "refrigeran bertahap dengan durasi total 2,0 jam. Dengan total inventori aktif sistem MCR Train H sekitar 24.000 kg, penyesuaian fraksi mol "
        "dilakukan melalui modulasi terukur control valve DCS eksisting: H4FIC005 (nitrogen), H4FI00C8 (metana), H4FIC007 (etana/etilena), dan H4FIC006 (propana). "
        "Laju injeksi make-up dibatasi pada rentang konservatif 0,60 hingga 0,95 ton/jam dengan gradien perubahan temperatur MCHE maksimum 0,15 °C/menit. "
        "Prosedur ini mencegah terjadinya thermal shock pada bundel tabung spiral serta menjamin suhu suction drum (H4TI004B) tidak pernah mendekati ambang batas interlock TAL (-45,0 °C)."
    )
    add_p(doc, p_res3b)
    
    # SUBBAB 3.4
    add_heading_2(doc, "3.4 Dampak Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Dekarbonisasi")
    p_res4 = (
        "Dekomposisi batas sistem energi Train C3MR disajikan secara transparan untuk membedakan daya poros mekanikal, uap turbin penggerak, dan bahan bakar boiler. "
        "Total penghematan daya poros kompresor terbobot tahunan mencapai 14,805 MW (-12,20%), yang terbagi atas: (1) Penghematan langsung pada kompresor MCR "
        "(4KT-2 dan 4KT-3) sebesar 13,251 MW (porsi 89,51%, setara 104.019,7 MWh/tahun); dan (2) Penghematan tidak langsung pada kompresor propana (4KT-1) "
        "sebesar 1,554 MW (porsi 10,49%, setara 12.195,6 MWh/tahun) akibat berkurangnya beban pendinginan MCR pada rangkaian chiller 4E-7/8/9. Pengurangan daya ini "
        "secara langsung memangkas kebutuhan uap turbin penggerak rata-rata sebesar 57,21 ton/jam (-12,15%). Berdasarkan 7.849,9 jam operasi tahunan (ketersediaan 89,61%), "
        "total penghematan uap boiler mencapai 449.087,3 ton/tahun. Dengan koefisien konsumsi gas bahan bakar boiler 77,0424 Nm³/ton uap, penghematan bahan bakar gas "
        "mencapai 34.598.740,6 Nm³/tahun (34,60 juta Nm³/tahun atau 1.295.307,7 MMBtu/tahun). Penilaian ekonomi dievaluasi pada tiga batas baterai (Battery Limit/BL): "
        "(a) BL 1 (Biaya internal uap utilitas @ USD 8,50/ton) menghasilkan penghematan USD 3,817 Juta/tahun; (b) BL 2 (Paritas gas bahan bakar boiler domestik @ USD 6,50/MMBtu) "
        "menghasilkan penghematan USD 8,419 Juta/tahun; dan (c) BL 3 (Paritas penjualan ekspor LNG FOB Bontang @ USD 11,50/MMBtu) menghasilkan nilai tambah "
        "USD 14,896 Juta/tahun. Dari aspek dekarbonisasi, penghematan bahan bakar mereduksi emisi GRK Scope 1 sebesar 73.845,9 ton CO2/tahun (stoikiometri primer) "
        "atau 34.413,6 ton CO2/tahun (sensitivitas IPCC), yang berpotensi menghasilkan pendapatan kredit karbon sebesar USD 147.691/tahun pada tarif USD 2,00/ton CO2. "
        "Rincian ledger tahunan terbobot melintasi spektrum beban disajikan pada Tabel 4."
    )
    add_p(doc, p_res4)
    
    # TABLE 4
    add_p(doc, "Tabel 4. Ledger Kinerja Tekno-Ekonomi, Energi, dan Lingkungan Tahunan Terbobot Jam Operasi Melintasi Spektrum Beban", font_size=10, bold=True, space_before=6, space_after=2)
    tbl4 = doc.add_table(rows=9, cols=8)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl4.autofit = False
    set_table_borders(tbl4)
    
    t4_widths = [Cm(2.2), Cm(1.8), Cm(2.2), Cm(2.2), Cm(2.0), Cm(2.0), Cm(2.2), Cm(2.0)]
    t4_data = [
        ["Persentil Operasi", "Umpan (t/jam)", "Hemat Daya (MW)", "Energi Hemat (MWh/th)", "Uap Hemat (ton/th)", "Bahan Bakar (10⁶ Nm³/th)", "Nilai BL 2 (USD/th)", "Reduksi CO2 (ton/th)"],
        ["P1 (Turndown)", "258,41", "2,827", "221,9", "857,5", "0,066", "16.077", "141,0"],
        ["P10", "325,05", "13,760", "1.080,1", "4.174,1", "0,322", "78.256", "686,4"],
        ["P25", "337,41", "14,828", "1.164,0", "4.497,8", "0,347", "84.326", "739,6"],
        ["P50 (Median)", "346,85", "15,295", "1.200,6", "4.639,5", "0,357", "86.982", "762,9"],
        ["P75", "361,82", "15,553", "1.220,9", "4.717,9", "0,363", "88.452", "775,8"],
        ["P90", "377,75", "16,117", "1.265,2", "4.888,8", "0,377", "91.656", "803,9"],
        ["P100 (Puncak)", "383,98", "16,347", "1.283,2", "4.958,6", "0,382", "92.964", "815,4"],
        ["Total / Rata-rata", "346,85", "14,805", "116.215,3", "449.087,3", "34,60", "8.419.500", "73.845,9"]
    ]
    for r_idx, row in enumerate(tbl4.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = t4_widths[c_idx]
            set_cell_margins(cell, top=35, bottom=35, left=45, right=45)
            cell.text = t4_data[r_idx][c_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(8.5)
                if r_idx == 0 or r_idx == 8:
                    run.font.bold = True
    set_table_header_bottom_border(tbl4.rows[0])
    for cell in tbl4.rows[8].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="double" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
    p_sp4 = doc.add_paragraph()
    p_sp4.paragraph_format.space_before = Pt(0)
    p_sp4.paragraph_format.space_after = Pt(4)
    
    add_figure(doc, "image8.png", "Gambar 8. Analisis dampak tekno-ekonomi dan lingkungan optimasi C3MR: (a) Penghematan finansial tahunan dan reduksi emisi CO2; (b) Analisis sensitivitas terhadap variasi harga bahan bakar, uap, dan jam operasi", width_inch=5.4)
    
    p_res4b = (
        "Analisis sensitivitas tekno-ekonomi dilakukan terhadap variasi harga bahan bakar gas boiler melintasi tiga skenario: "
        "(a) Skenario Rendah (USD 4,50/MMBtu) menghasilkan penghematan sebesar USD 5,829 Juta/tahun; (b) Skenario Dasar (USD 6,50/MMBtu) "
        "menghasilkan penghematan sebesar USD 8,419 Juta/tahun; dan (c) Skenario Tinggi (USD 8,50/MMBtu) menghasilkan penghematan sebesar "
        "USD 11,010 Juta/tahun. Karena optimalisasi ini dilakukan murni melalui penataan resep komposisi refrigeran dan pengaturan setpoint sirkulasi "
        "pada DCS tanpa modifikasi mekanikal atau penambahan alat baru (Zero CAPEX), maka Payback Period tercapai secara instan (0 bulan). "
        "Penghematan biaya operasional tahunan sebesar USD 8,42 Juta/tahun secara simultan memberikan kontribusi dekarbonisasi nyata sebesar 73.845,9 ton CO2/tahun."
    )
    add_p(doc, p_res4b)
    
    # 9. KESIMPULAN
    add_heading_1(doc, "KESIMPULAN")
    p_conc = (
        "Berdasarkan hasil pemodelan, optimasi, dan evaluasi tekno-ekonomi pada Kilang Badak Train H periode 2024–2026, dapat ditarik beberapa kesimpulan utama:\n"
        "1. Kerangka kerja Physics-Constrained Machine Learning berhasil memetakan siklus pencairan C3MR secara presisi tinggi, di mana model surrogate HGBR "
        "mencapai R² uji 0,6677–0,9998 dengan relative error NMAE < 1,0% (kesalahan daya poros < 0,83 MW) pada seluruh variabel proses utama tanpa pelanggaran termodinamika.\n"
        "2. Formulasi satu resep komposisi mixed refrigerant optimal tunggal (3,67 mol% N2; 51,26 mol% C1; 42,62 mol% C2; 0,44 mol% C2H4; 2,01 mol% C3) "
        "terbukti patuh pada batas elipsoid Mahalanobis 95% (DM = 3,0762 <= 3,0802), membuktikan kelayakan implementasi langsung di kilang tanpa belanja modal (Zero CAPEX).\n"
        "3. Optimasi memangkas SEC beban puncak sebesar 12,60% (dari 448,2 ke 391,8 kWh/ton LNG) dan menghemat uap turbin 63,17 ton/jam. Pada kondisi turndown, "
        "laju sirkulasi MCR ditahan aman pada 480,00 ton/jam sesuai batas flow floor anti-surge kompresor sentrifugal. Dekomposisi daya kompresor membuktikan "
        "penghematan rata-rata 14,805 MW (-12,20%) terbagi atas kompresor MCR langsung 13,251 MW (89,51%) dan kompresor propana 1,554 MW (10,49%).\n"
        "4. Dampak tahunan terbobot pada 7.849,9 jam operasi menghemat 116.215,3 MWh/tahun energi mekanikal, 449.087,3 ton/tahun uap boiler, 34,60 juta Nm³/tahun "
        "gas bahan bakar (senilai USD 8,42 Juta/tahun pada paritas gas atau USD 14,90 Juta/tahun pada paritas ekspor LNG), serta mereduksi emisi Scope 1 sebesar "
        "73.845,9 ton CO2/tahun dengan margin keselamatan terverifikasi aman (MITA >= 7,17 °C, Tsuct >= -41,76 °C).\n\n"
        "Rekomendasi implementasi di kilang mencakup: (a) Integrasi formula optimal sebagai Advisory System pada DCS Yokogawa Centum VP; (b) Penerapan prosedur "
        "injeksi make-up refrigeran bertahap (0,6–0,95 ton/jam) dengan ramp suhu maksimum 0,15 °C/menit; dan (c) Adopsi jadwal laju sirkulasi MCR kuantil beban "
        "sebagai Standard Operating Procedure (SOP) resmi untuk mitigasi penuaan reservoir gas umpan."
    )
    add_p(doc, p_conc)
    
    # 10. DAFTAR PUSTAKA (IEEE FORMAT)
    add_heading_1(doc, "DAFTAR PUSTAKA")
    
    refs = [
        "[1] M. S. Khan, I. A. Karimi, and D. A. Wood, “Retrospective and prospective overview of natural gas liquefaction processes,” J. Nat. Gas Sci. Eng., vol. 75, p. 103173, Mar. 2020, doi: 10.1016/j.jngse.2019.103173.",
        "[2] W. Lim, K. Choi, and I. Moon, “Current and future perspectives for LNG process simulation and optimization,” Korean J. Chem. Eng., vol. 31, no. 5, pp. 723–735, May 2014, doi: 10.1007/s11814-014-0074-6.",
        "[3] PT Badak NGL, Operating Manual and Plant Standards: Train H C3MR Liquefaction Unit. Bontang, Indonesia: PT Badak NGL, 2021.",
        "[4] R. Purwanugraha, “Adaptation strategies of Badak LNG toward lean feed gas processing,” in Proc. Annu. Conv. Indones. Gas Assoc. (IGA), Jakarta, Indonesia, 2023, pp. 45–58.",
        "[5] E. Primabudi and A. Putranto, “Operational challenges and efficiency optimization in mature LNG liquefaction plants,” Indones. J. Process Syst. Eng., vol. 4, no. 2, pp. 85–96, Dec. 2023.",
        "[6] A. Alabdulkarem, A. Mortazavi, Y. Hwang, R. Radermacher, and P. Rogers, “Optimization of propane pre-cooled mixed refrigerant LNG plant,” Appl. Therm. Eng., vol. 31, no. 6–7, pp. 1091–1098, May 2011, doi: 10.1016/j.applthermaleng.2010.12.003.",
        "[7] B. Utomo and D. Setiawan, “Compressor anti-surge control and operating envelope protection during low-load operation,” J. Mech. Eng. Saf. Syst., vol. 7, no. 3, pp. 112–121, Sep. 2022.",
        "[8] M. Wang, J. Zhang, and Q. Xu, “Optimal design and operation of mixed refrigerant cycles for LNG processes,” Ind. Eng. Chem. Res., vol. 53, no. 18, pp. 7729–7740, May 2014, doi: 10.1021/ie500445d.",
        "[9] A. Mortazavi, C. Somers, Y. Hwang, R. Radermacher, P. Rodgers, and S. Al-Hashimi, “Performance enhancement of propane pre-cooled mixed refrigerant LNG plant,” Appl. Energy, vol. 93, pp. 125–131, May 2012, doi: 10.1016/j.apenergy.2011.05.009.",
        "[10] R. Barbazza, “Thermodynamic analysis and optimization of mixed refrigerant cycles for natural gas liquefaction,” Energy, vol. 288, p. 129845, Feb. 2024, doi: 10.1016/j.energy.2023.129845.",
        "[11] H. Ding, H. Sun, and S. Min, “Optimization of C3MR LNG process based on surrogate models and genetic algorithms,” Chem. Eng. Res. Des., vol. 168, pp. 412–424, Apr. 2021, doi: 10.1016/j.cherd.2021.02.023.",
        "[12] G. Ruan, K. Wang, and H. Zhang, “Machine learning surrogate-assisted optimization of mixed refrigerant processes,” Comput. Chem. Eng., vol. 160, p. 107722, Apr. 2022, doi: 10.1016/j.compchemeng.2022.107722.",
        "[13] M. Shady, M. Elsayegh, and M. El-Fakharany, “Physics-informed surrogate modeling for multi-component LNG liquefaction plants,” Appl. Therm. Eng., vol. 239, p. 122150, Feb. 2024, doi: 10.1016/j.applthermaleng.2023.122150.",
        "[14] F. Wu, C. He, and J. Chen, “Simultaneous optimization of composition and operating parameters in C3MR liquefaction process using deep reinforcement learning,” Energy Convers. Manag., vol. 301, p. 118025, Feb. 2025, doi: 10.1016/j.enconman.2023.118025.",
        "[15] J. Aitchison, The Statistical Analysis of Compositional Data. London, UK: Chapman and Hall, 1986.",
        "[16] J. J. Egozcue, V. Pawlowsky-Glahn, G. Mateu-Figueras, and C. Barceló-Vidal, “Isometric logratio transformations for compositional data analysis,” Math. Geol., vol. 35, no. 3, pp. 279–300, Apr. 2003, doi: 10.1023/A:1023818214614.",
        "[17] P. C. Mahalanobis, “On the generalized distance in statistics,” Proc. Natl. Inst. Sci. India, vol. 2, no. 1, pp. 49–55, 1936.",
        "[18] D. Y. Peng and D. B. Robinson, “A new two-constant equation of state,” Ind. Eng. Chem. Fundam., vol. 15, no. 1, pp. 59–64, Feb. 1976, doi: 10.1021/i160057a011.",
        "[19] P. A. Castillo and C. A. Dorao, “Consistently modeling and optimizing mixed refrigerant LNG processes using PR-EOS,” J. Nat. Gas Sci. Eng., vol. 76, p. 103195, Apr. 2020, doi: 10.1016/j.jngse.2020.103195.",
        "[20] G. Venkatarathnam, Cryogenic Mixed Refrigerant Processes. New York, NY, USA: Springer, 2008.",
        "[21] R. Smith, Chemical Process Design and Integration, 2nd ed. Chichester, UK: John Wiley & Sons, 2016.",
        "[22] A. Stodola, Steam Turbines: With an Appendix on Gas Turbines and the Future of Heat Engines, 2nd ed. New York, NY, USA: D. Van Nostrand Co., 1905.",
        "[23] H. Ramadan, “Peningkatan kualitas steam dengan menaikkan entalpi steam guna optimalisasi nilai efisiensi steam turbine generator di Utilities-II PT Badak NGL,” Tugas Akhir, Jurusan Teknik Mesin, Politeknik Negeri Jakarta, Depok, Indonesia, 2025.",
        "[24] M. Gouy, “Sur l’énergie utilisable,” J. Phys. Théor. Appl., vol. 8, no. 1, pp. 501–518, 1889.",
        "[25] I. J. Halvorsen and S. Skogestad, “Energy efficient operation of distillation columns and refrigeration cycles,” Comput. Chem. Eng., vol. 35, no. 8, pp. 1338–1350, Aug. 2011, doi: 10.1016/j.compchemeng.2011.04.004.",
        "[26] N. R. Sial, M. A. Qyyum, and M. Lee, “AI-driven surrogate modeling and design optimization of the nitrogen expansion liquefaction process,” Int. J. Thermofluids, vol. 33, p. 101618, Feb. 2026, doi: 10.1016/j.ijft.2026.101618."
    ]
    
    for r in refs:
        p_ref = add_p(doc, r, font_size=9.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=1, space_after=3)
        p_ref.paragraph_format.left_indent = Cm(0.8)
        p_ref.paragraph_format.first_line_indent = Cm(-0.8)

    doc.save(OUTPUT_DOCX)
    print(f"Full paper successfully built and saved to: {OUTPUT_DOCX}")
    
    write_markdown_paper(OUTPUT_MD, abs_id, abs_en, p1, p2, p3, p4, p_met1, p_met2a, p_met2b, p_met2c, p_met3a, p_met3b, p_met4a, p_met4b, p_met4c, p_res1, p_res2, p_res3, p_res4, p_conc, refs, p_res3b, p_res4b)

if __name__ == "__main__":
    build_paper()
