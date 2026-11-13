import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    """Set cell borders in oxml."""
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, border_style in borders.items():
        if border_style:
            tag = f'w:{border_name}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), border_style.get('val', 'single'))
            element.set(qn('w:sz'), str(border_style.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), border_style.get('color', 'auto'))
            tcBorders.append(element)
        else:
            tag = f'w:{border_name}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), 'none')
            tcBorders.append(element)
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex):
    """Set background color of a cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def create_rewritten_docx(md_path, docx_path, figures_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = docx.Document()
    
    # Configure A4 page and margins per IKMS template
    section = doc.sections[0]
    section.page_width = Inches(8.268)   # 210 mm
    section.page_height = Inches(11.693) # 297 mm
    section.top_margin = Inches(0.984)   # 2.5 cm
    section.bottom_margin = Inches(0.787)# 2.0 cm
    section.left_margin = Inches(0.984)  # 2.5 cm
    section.right_margin = Inches(0.787) # 2.0 cm

    # Set normal style font
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(10)
    font.color.rgb = RGBColor(0, 0, 0)

    lines = md_text.splitlines()
    
    i = 0
    in_abstract = False
    in_abstract_en = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # Title
        if line.startswith('# ') and not line.startswith('## '):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(title_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(16)
            run.font.bold = True
            i += 1
            continue

        # Authors
        if line.startswith('**Bilqiis Dara') or line.startswith('**Penulis') or (line.startswith('**') and '¹' in line):
            author_text = line.replace('**', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(author_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.bold = True
            i += 1
            continue

        # Affiliation
        if line.startswith('¹Jurusan') or line.startswith('1Jurusan'):
            aff_text = line.strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(aff_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(8)
            i += 1
            continue

        # Corresponding author
        if line.startswith('*Corresponding author:') or line.startswith('*Penulis korespondensi:'):
            corr_text = line.replace('*', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(14)
            run = p.add_run(corr_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(8)
            run.font.italic = True
            i += 1
            continue

        # Divider ---
        if line == '---':
            i += 1
            continue

        # Abstrak header
        if line == '### Abstrak':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run('Abstrak')
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.bold = True
            in_abstract = True
            i += 1
            continue

        # Kata kunci
        if line.startswith('**Kata kunci:**'):
            kw_text = line.replace('**Kata kunci:**', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(10)
            r_label = p.add_run('Kata kunci: ')
            r_label.font.name = 'Times New Roman'
            r_label.font.size = Pt(10)
            r_label.font.bold = True
            r_label.font.italic = True
            r_val = p.add_run(kw_text)
            r_val.font.name = 'Times New Roman'
            r_val.font.size = Pt(10)
            r_val.font.italic = True
            in_abstract = False
            i += 1
            continue

        # Abstract header
        if line == '### Abstract':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run('Abstract')
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.italic = True
            in_abstract_en = True
            i += 1
            continue

        # Keywords English
        if line.startswith('**Keywords:**'):
            kw_text = line.replace('**Keywords:**', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
            r_label = p.add_run('Keywords: ')
            r_label.font.name = 'Times New Roman'
            r_label.font.size = Pt(10)
            r_label.font.bold = True
            r_label.font.italic = True
            r_val = p.add_run(kw_text)
            r_val.font.name = 'Times New Roman'
            r_val.font.size = Pt(10)
            r_val.font.italic = True
            in_abstract_en = False
            i += 1
            continue

        # Section Heading 1 (e.g. ## 1. PENDAHULUAN)
        if line.startswith('## '):
            h_text = line[3:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text.upper())
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.bold = True
            i += 1
            continue

        # Subsection Heading 2 (e.g. ### 2.1 Objek Penelitian)
        if line.startswith('### ') and not line.startswith('#### '):
            h_text = line[4:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.font.bold = True
            i += 1
            continue

        # Table caption (e.g. #### Tabel 1. Deskripsi Tag Instrumen)
        if line.startswith('#### Tabel ') or line.startswith('Tabel '):
            caption_text = line.replace('#### ', '').strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            
            # Format "Tabel X." as Bold
            m = re.match(r'(Tabel\s+\d+\.)\s*(.*)', caption_text)
            if m:
                r1 = p.add_run(m.group(1))
                r1.font.name = 'Times New Roman'
                r1.font.size = Pt(10)
                r1.font.bold = True
                r2 = p.add_run(' ' + m.group(2))
                r2.font.name = 'Times New Roman'
                r2.font.size = Pt(10)
            else:
                r = p.add_run(caption_text)
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)
                r.font.bold = True
            i += 1
            continue

        # Markdown Table Detection
        if line.startswith('|') and '|' in line[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            
            if len(table_lines) >= 2:
                # Parse markdown table
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                data_rows = []
                for tline in table_lines[1:]:
                    if re.match(r'^[\|\s\:\-]+$', tline):
                        continue
                    cols = [c.strip() for c in tline.split('|')[1:-1]]
                    if cols:
                        data_rows.append(cols)
                
                # Create docx table
                table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.autofit = True

                top_border = {'val': 'single', 'sz': 8, 'color': '000000'}
                hdr_bottom = {'val': 'single', 'sz': 6, 'color': '000000'}
                tbl_bottom = {'val': 'single', 'sz': 8, 'color': '000000'}

                # Format Header
                hdr_cells = table.rows[0].cells
                for col_idx, h_text in enumerate(headers):
                    cell = hdr_cells[col_idx]
                    cell.text = h_text
                    set_cell_borders(cell, top=top_border, bottom=hdr_bottom)
                    set_cell_shading(cell, 'F2F2F2')
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(9)
                        r.font.bold = True

                # Format Data Rows
                for row_idx, row_data in enumerate(data_rows):
                    row_cells = table.rows[row_idx + 1].cells
                    is_last_row = (row_idx == len(data_rows) - 1)
                    bot = tbl_bottom if is_last_row else None
                    for col_idx in range(len(headers)):
                        cell = row_cells[col_idx]
                        val_text = row_data[col_idx] if col_idx < len(row_data) else ''
                        cell.text = val_text
                        set_cell_borders(cell, bottom=bot)
                        p = cell.paragraphs[0]
                        # Align numbers center or right, text left
                        if any(char.isdigit() for char in val_text) and not any(k in val_text for k in ['VALID', 'GAGAL', 'Terbuka', 'Belum']):
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        p.paragraph_format.space_before = Pt(1)
                        p.paragraph_format.space_after = Pt(1)
                        for r in p.runs:
                            r.font.name = 'Times New Roman'
                            r.font.size = Pt(8.5)
                            if 'VALID' in val_text or 'GAGAL' in val_text or 'Puncak' in val_text or 'Turndown' in val_text or 'Median' in val_text:
                                if 'GAGAL' in val_text:
                                    r.font.bold = True
                                    r.font.color.rgb = RGBColor(180, 0, 0)
                                elif 'VALID' in val_text:
                                    r.font.bold = True
                                    r.font.color.rgb = RGBColor(0, 120, 0)
                
                # Add spacing after table
                p_spacer = doc.add_paragraph()
                p_spacer.paragraph_format.space_before = Pt(0)
                p_spacer.paragraph_format.space_after = Pt(6)
            continue

        # Figure detection: ![Alt](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
        if img_match:
            img_alt = img_match.group(1)
            img_rel_path = img_match.group(2)
            img_basename = os.path.basename(img_rel_path)
            img_full_path = os.path.join(figures_dir, img_basename)
            
            if os.path.exists(img_full_path):
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(3)
                p_img.paragraph_format.keep_with_next = True
                run_img = p_img.add_run()
                run_img.add_picture(img_full_path, width=Inches(5.5))
            i += 1
            continue

        # Figure caption (e.g. *Gambar 1. ...*)
        if line.startswith('*Gambar ') or line.startswith('Gambar '):
            fig_caption = line.replace('*', '').strip()
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            run_cap = p_cap.add_run(fig_caption)
            run_cap.font.name = 'Times New Roman'
            run_cap.font.size = Pt(9.5)
            run_cap.font.italic = True
            i += 1
            continue

        # Display Equation (e.g. $$ ... $$)
        if line.startswith('$$') and line.endswith('$$') and len(line) > 4:
            eq_text = line[2:-2].strip()
            p_eq = doc.add_paragraph()
            p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_eq.paragraph_format.space_before = Pt(4)
            p_eq.paragraph_format.space_after = Pt(4)
            run_eq = p_eq.add_run(eq_text)
            run_eq.font.name = 'Cambria Math'
            run_eq.font.size = Pt(10)
            run_eq.font.italic = True
            i += 1
            continue

        # Numbered list or bullet points in conclusion or body
        if re.match(r'^\d+\.\s+', line):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Inches(0.25)
            
            # Highlight bold lead-in if exists
            m_bold = re.match(r'^(\d+\.\s+\*\*.*?\*\*)\s*(.*)', line)
            if m_bold:
                r1 = p.add_run(m_bold.group(1).replace('**', ''))
                r1.font.name = 'Times New Roman'
                r1.font.size = Pt(10)
                r1.font.bold = True
                r2 = p.add_run(' ' + m_bold.group(2))
                r2.font.name = 'Times New Roman'
                r2.font.size = Pt(10)
            else:
                r = p.add_run(line)
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)
            i += 1
            continue

        # Reference item (e.g. [1] ...)
        if line.startswith('[') and re.match(r'^\[\d+\]', line):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            run = p.add_run(line)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9)
            i += 1
            continue

        # Regular Body Paragraph
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05

        # Format inline formatting (bold, italic)
        # Parse inline bold **text** and italic *text*
        text = line
        tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|\$.*?\$)', text)
        for token in tokens:
            if not token:
                continue
            if token.startswith('**') and token.endswith('**') and len(token) >= 4:
                run = p.add_run(token[2:-2])
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.bold = True
            elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
                run = p.add_run(token[1:-1])
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.italic = True
            elif token.startswith('$') and token.endswith('$') and len(token) >= 2:
                run = p.add_run(token[1:-1])
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.italic = True
            else:
                run = p.add_run(token)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                if in_abstract_en:
                    run.font.italic = True

        i += 1

    doc.save(docx_path)
    print(f'Successfully generated {docx_path}')

if __name__ == '__main__':
    md_p = 'ikms_2026/IKMS_FULLPAPER_REWRITTEN.md'
    docx_p = 'ikms_2026/IKMS_FULLPAPER_REWRITTEN.docx'
    docx_final_p = 'ikms_2026/IKMS_FULLPAPER_REWRITTEN_FINAL.docx'
    docx_updated_p = 'ikms_2026/IKMS_FULLPAPER_REWRITTEN_UPDATED.docx'
    fig_d = 'ikms_2026/figures'
    
    # Try primary target
    target_saved = None
    for p in [docx_p, docx_final_p, docx_updated_p]:
        try:
            create_rewritten_docx(md_p, p, fig_d)
            target_saved = p
            print(f'Successfully generated {p}')
            break
        except PermissionError:
            print(f'Target {p} is locked, trying fallback...')
            continue
    
    # Also sync to other targets if unlocked
    import shutil
    for p in [docx_p, docx_final_p, docx_updated_p]:
        if p != target_saved:
            try:
                shutil.copyfile(target_saved, p)
                print(f'Successfully synchronized {p}')
            except Exception:
                pass
