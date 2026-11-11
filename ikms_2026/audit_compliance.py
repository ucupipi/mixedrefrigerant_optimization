import docx
import re
import os

DOCX_PATH = r"d:\User\Documents\KULIAH\LOMBA\IKMS 2026\IKMS2026_FullPaper_PNJ.docx"
doc = docx.Document(DOCX_PATH)

print("=== 1. SECTIONS & MARGINS ===")
for s_idx, s in enumerate(doc.sections):
    print(f"Section {s_idx}: W={s.page_width.cm:.2f}cm, H={s.page_height.cm:.2f}cm, Top={s.top_margin.cm:.2f}cm, Bottom={s.bottom_margin.cm:.2f}cm, Left={s.left_margin.cm:.2f}cm, Right={s.right_margin.cm:.2f}cm")
    print(f"Footer paragraphs count: {len(s.footer.paragraphs)}")
    for fp in s.footer.paragraphs:
        print(f"  Footer text: '{fp.text}', align={fp.alignment}, xml={fp._p.xml[:200]}")

print("\n=== 2. TITLE & METADATA RUNS ===")
for i in range(min(12, len(doc.paragraphs))):
    p = doc.paragraphs[i]
    if p.text.strip():
        runs = [(r.text[:25], r.font.name, r.font.size.pt if r.font.size else None, r.font.bold, r.font.italic) for r in p.runs]
        print(f"P{i} [align={p.alignment}]: '{p.text[:60]}...'")
        print(f"    Runs: {runs}")

print("\n=== 3. KEYWORDS CHECK ===")
for p in doc.paragraphs:
    if p.text.startswith("Kata kunci:") or p.text.startswith("Keywords:"):
        print(f"'{p.text}'")
        raw_kw = p.text.split(":", 1)[1].strip()
        kws = [k.strip() for k in raw_kw.split(",") if k.strip()]
        print(f"  Count: {len(kws)}, List: {kws}")
        is_sorted = kws == sorted(kws, key=str.lower)
        print(f"  Alphabetical? {is_sorted} (Sorted should be: {sorted(kws, key=str.lower)})")

print("\n=== 4. HEADINGS & SUBHEADINGS ===")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if txt in ["PENDAHULUAN", "METODE", "HASIL DAN PEMBAHASAN", "KESIMPULAN", "DAFTAR PUSTAKA"] or re.match(r"^[1-4]\.[1-4]", txt):
        runs = [(r.text[:20], r.font.name, r.font.size.pt if r.font.size else None, r.font.bold) for r in p.runs]
        print(f"P{i}: '{txt}' -> Runs: {runs}")

print("\n=== 5. TABLES IN TEXT ===")
print(f"Total tables: {len(doc.tables)}")
for t_idx, t in enumerate(doc.tables):
    print(f"Table {t_idx}: rows={len(t.rows)}, cols={len(t.columns)}, alignment={t.alignment}")
    row0 = [c.text.strip().replace('\n', ' ') for c in t.rows[0].cells]
    print(f"  Headers: {row0[:4]}...")

print("\n=== 6. FIGURES IN TEXT ===")
fig_count = 0
for i, p in enumerate(doc.paragraphs):
    if p.text.strip().startswith("Gambar "):
        fig_count += 1
        print(f"Fig {fig_count} at P{i}: '{p.text}'")

print("\n=== 7. REFERENCES IN TEXT ===")
ref_count = 0
for i, p in enumerate(doc.paragraphs):
    if re.match(r"^\[\d+\]", p.text.strip()):
        ref_count += 1
        print(f"Ref {ref_count}: '{p.text[:80]}...'")
print(f"Total references: {ref_count}")

