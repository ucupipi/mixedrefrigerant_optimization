import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

TEMPLATE_PATH = r"d:\User\Documents\KULIAH\LOMBA\IKMS 2026\Template Paper IKMS 2026.docx"
OUTPUT_DOCX = r"d:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ_Final.docx"
OUTPUT_MD = r"d:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ_Final.md"
FIGURES_DIR = r"d:\User\Documents\KULIAH\LOMBA\IKMS 2026\figures"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

def add_equation_row(doc, eq_text, eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Col widths: 14.5 cm and 2.0 cm
    tbl.columns[0].width = Cm(14.5)
    tbl.columns[1].width = Cm(2.0)
    
    # Remove borders
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
    
    # Add empty paragraph after table for spacing
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)
    p_after.paragraph_format.line_spacing = 1.0

print("Helper functions verified.")

