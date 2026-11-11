import pandas as pd

v3 = pd.read_csv(r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_MASTER_REGISTER_2025_V3.csv")
for t in ['4E-7', '4E-8', '4E-9', '4E-1', '4E-2', '4E-3', '4E-4', '4E-5', '4E-6', '4E-10', '4E-12', '4E-14']:
    sub = v3[v3['Equipment'].astype(str).str.contains(t, case=False, na=False) | v3['Physical_Definition'].astype(str).str.contains(t, case=False, na=False)]
    if len(sub) > 0:
        print(f"\n--- Equipment matches for {t} ({len(sub)}) ---")
        for _, r in sub.drop_duplicates(subset=['Instrument_Tag']).iterrows():
            print(f"Tag: {r['Instrument_Tag']:<10} | Eq: {r['Equipment']:<25} | Def: {str(r['Physical_Definition'])[:75]}")
