import json
import os
import re
import docx

LEDGER_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\DATA_LEDGER.json"
ABSTRACT_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_Abstrak_PNJ.md"
MD_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ.md"
DOCX_PATH = r"D:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ.docx"

with open(LEDGER_PATH, "r", encoding="utf-8") as f:
    L = json.load(f)

with open(ABSTRACT_PATH, "r", encoding="utf-8") as f:
    abstract_text = f.read()

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

doc = docx.Document(DOCX_PATH)
docx_text = "\n".join([p.text for p in doc.paragraphs] + [cell.text for t in doc.tables for r in t.rows for cell in r.cells])

# 1. Body checks across MD and DOCX
body_checks = [
    ("N2 Mol %", "3,77", L["optimal_mcr_composition_mol_percent"]["nitrogen_N2"]),
    ("C1 Mol %", "42,22", L["optimal_mcr_composition_mol_percent"]["methane_CH4"]),
    ("C2 Mol %", "43,67", L["optimal_mcr_composition_mol_percent"]["ethane_C2H6"]),
    ("C2H4 Mol %", "1,53", L["optimal_mcr_composition_mol_percent"]["ethylene_C2H4"]),
    ("C3 Mol %", "8,82", L["optimal_mcr_composition_mol_percent"]["propane_C3H8"]),
    ("Mahalanobis DM", "1,2723", L["optimal_mcr_composition_mol_percent"]["mahalanobis_distance_DM"]),
    ("Mahalanobis Threshold", "3,0802", L["optimal_mcr_composition_mol_percent"]["mahalanobis_threshold_95_percent"]),
    ("Baseload SEC Baseline", "350,49", L["baseload_P90"]["sec_baseline_kWh_t"]),
    ("Baseload SEC Optimized", "256,51", L["baseload_P90"]["sec_optimized_kWh_t"]),
    ("Baseload SEC Reduction %", "26,81", L["baseload_P90"]["sec_reduction_percent"]),
    ("Turndown SEC Baseline", "523,00", L["underload_P10"]["sec_baseline_kWh_t"]),
    ("Turndown SEC Optimized", "339,89", L["underload_P10"]["sec_optimized_kWh_t"]),
    ("Turndown SEC Reduction %", "35,01", L["underload_P10"]["sec_reduction_percent"]),
    ("Driver Steam Saved (t/h)", "31,65", L["baseload_P90"]["driver_steam_consumption_reduction_t_h"]),
    ("Driver Steam Saved (%)", "6,54", L["baseload_P90"]["driver_steam_consumption_reduction_percent"]),
    ("Annual Cost Savings ($M)", "8,48", L["annualized_impact"]["annual_cost_savings_million_USD_yr"]),
    ("Annual CO2 Abatement (t/yr)", "49.961,8", L["annualized_impact"]["annual_co2_abatement_t_yr"]),
    ("Annual Steam Saved (t/yr)", "239.889,7", L["annualized_impact"]["annual_driver_steam_saved_t_yr"]),
    ("Weighted Power Reduction (kW)", "28.983,3", L["annualized_impact"]["operating_hours_weighted_power_reduction_kW"]),
    ("Operating Hours / yr", "7.849,9", L["plant_baseline"]["operating_hours_per_year"]),
    ("MCR Direct Power Saving (kW)", "10.826,1", L["baseload_P90"]["power_decomposition"]["mcr_direct_compressors_reduction_kW"]),
    ("C3 Precooling Power Saving (kW)", "18.145,7", L["baseload_P90"]["power_decomposition"]["c3_precooling_compressor_reduction_kW"]),
    ("Mortazavi DOI", "10.1016/j.apenergy.2011.05.009", "10.1016/j.apenergy.2011.05.009"),
    ("Ramadan Citation", "Tugas Akhir", "Tugas Akhir")
]

print("=== 1. VERIFYING BODY CONSISTENCY (MD & DOCX) ===")
body_failures = []
for label, str_pattern, val in body_checks:
    in_md = (str_pattern in md_text) or (str(val) in md_text)
    in_docx = (str_pattern in docx_text) or (str(val) in docx_text)
    status = "PASS" if (in_md and in_docx) else "FAIL"
    if status == "FAIL":
        body_failures.append((label, str_pattern, in_md, in_docx))
    print(f"[{status}] {label:32} Expected: {str_pattern:10} (MD: {in_md}, DOCX: {in_docx})")

# 2. Abstract checks across Abstract file, MD and DOCX
abs_checks = [
    ("C3MR Energy Share %", "59,3"),
    ("Feed Gas Methane Design Limit %", "91,6"),
    ("Historical 2017 Methane %", "88,1"),
    ("Operational 2024-2026 Methane %", "94,5"),
    ("MCHE Specific Cooling Duty kJ/kg", "652,9"),
    ("DCS Dataset Records", "720.734"),
    ("GC Analysis Samples", "2.531"),
    ("Optimum N2 Mol %", "3,77"),
    ("Optimum C1 Mol %", "42,22"),
    ("Optimum C2 Mol %", "43,67"),
    ("Optimum C2H4 Mol %", "1,53"),
    ("Optimum C3 Mol %", "8,82"),
    ("Mahalanobis Threshold", "3,0802"),
    ("Baseload SEC Reduction %", "26,81"),
    ("Turbine Steam Saved t/h", "31,65"),
    ("Annual Steam Saved ton/yr", "239.889,7"),
    ("Annual Fuel Gas Saved Nm3/yr", "23,44"),
    ("Annual Financial Savings $M", "8,48"),
    ("Annual CO2 Abatement ton/yr", "49.961,8")
]

print("\n=== 2. VERIFYING ABSTRACT CONSISTENCY (ABS, MD & DOCX) ===")
abs_failures = []
for label, str_pattern in abs_checks:
    in_abs = str_pattern in abstract_text
    in_md = str_pattern in md_text
    in_docx = str_pattern in docx_text
    status = "PASS" if (in_abs and in_md and in_docx) else "FAIL"
    if status == "FAIL":
        abs_failures.append((label, str_pattern, in_abs, in_md, in_docx))
    print(f"[{status}] {label:32} Expected: {str_pattern:10} (Abs: {in_abs}, MD: {in_md}, DOCX: {in_docx})")

# 3. Symmetric Subheading Structure Checks
print("\n=== 3. VERIFYING SYMMETRIC SUBSECTION STRUCTURE (4 vs 4) ===")
subheadings = [
    "2.1 Operasi Kilang, Akuisisi Data DCS, dan Penyaringan Kondisi Tunak",
    "2.2 Geometri Komposisi Simpleks ILR dan Pemodelan Machine Learning Berpembatas Fisika",
    "2.3 Formulasi Optimasi Komposisi, Laju Sirkulasi MR, dan Validasi Termodinamika",
    "2.4 Metodologi Evaluasi Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Emisi Karbon",
    "3.1 Karakterisasi Baseline Operasi Kilang dan Profil Pasokan Gas Umpan",
    "3.2 Validasi Akurasi Model Surrogate Machine Learning dan Batasan Ruang Operasi",
    "3.3 Kinerja Optimasi Komposisi dan Laju Sirkulasi MR Melintasi Spektrum Beban Operasi Kilang",
    "3.4 Dampak Tekno-Ekonomi, Dekomposisi Daya Poros vs Uap Turbin, dan Dekarbonisasi"
]
subheading_failures = []
for sh in subheadings:
    in_md = sh in md_text
    in_docx = sh in docx_text
    status = "PASS" if (in_md and in_docx) else "FAIL"
    if status == "FAIL":
        subheading_failures.append((sh, in_md, in_docx))
    print(f"[{status}] {sh[:60]}... (MD: {in_md}, DOCX: {in_docx})")

# Verify that old subheadings 3.5, 3.6, 3.7 do NOT exist
legacy_subheadings = ["3.5 ", "3.6 ", "3.7 "]
for lsh in legacy_subheadings:
    present_md = any(line.strip().startswith(f"### {lsh}") for line in md_text.splitlines())
    present_docx = any(p.text.strip().startswith(lsh) for p in doc.paragraphs)
    status = "PASS" if (not present_md and not present_docx) else "FAIL"
    if status == "FAIL":
        subheading_failures.append((f"Legacy {lsh} found", present_md, present_docx))
    print(f"[{status}] Absence of legacy '{lsh}' (MD absent: {not present_md}, DOCX absent: {not present_docx})")

# 4. Abstract word count checks
print("\n=== 4. VERIFYING ABSTRACT WORD COUNTS (<= 250 WORDS) ===")
# Extract Indonesian abstract paragraph
m_id = re.search(r"### Abstrak\s+(.*?)\s+\*\*Kata kunci:\*\*", abstract_text, re.DOTALL)
id_words = len(m_id.group(1).split()) if m_id else 0
m_en = re.search(r"### Abstract\s+(.*?)\s+\*\*Keywords:\*\*", abstract_text, re.DOTALL)
en_words = len(m_en.group(1).split()) if m_en else 0

id_status = "PASS" if 0 < id_words <= 250 else "FAIL"
en_status = "PASS" if 0 < en_words <= 250 else "FAIL"
print(f"[{id_status}] Indonesian Abstract: {id_words} words (Limit: <= 250)")
print(f"[{en_status}] English Abstract:    {en_words} words (Limit: <= 250)")

print("\n" + "="*50)
if not body_failures and not abs_failures and not subheading_failures and id_status == "PASS" and en_status == "PASS":
    print("ALL VERIFICATIONS 100% PASSED! PERFECT SYMMETRIC STRUCTURE & STRICT AUDIT COMPLIANCE.")
else:
    print(f"FAILURES DETECTED! Body: {len(body_failures)}, Abstract: {len(abs_failures)}, Subheadings: {len(subheading_failures)}")
