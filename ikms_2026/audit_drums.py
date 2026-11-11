import pandas as pd

loc_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_PHYSICAL_LOCATION_FORENSIC_2025.csv"
df_loc = pd.read_csv(loc_path)

tags_to_check = ['4TI4B', '4TI1A', '4TI2A', '4TI6B', '4TI7B', '4TI8B', 'H4TI004B', '4PI201', '4PIC2', '4PI3B']

print("=== CHECKING TAGS AND EQUIPMENT ===")
for t in tags_to_check:
    sub = df_loc[df_loc['TAG'].astype(str).str.lower() == t.lower()]
    if len(sub) > 0:
        for _, r in sub.iterrows():
            print(f"TAG: {r['TAG']:<10} | Eq: {r['EQUIPMENT']:<40} | RawContext: {r['RAW_PROCESS_CONTEXT']:<20} | Loc: {r['MEASUREMENT_LOCATION']}")

print("\n=== ALL ROWS MENTIONING 4C- IN LOC ===")
for idx, r in df_loc.iterrows():
    text = f"{r['EQUIPMENT']} {r['MEASUREMENT_LOCATION']} {r['RAW_PROCESS_CONTEXT']}"
    if '4C-' in text or '4C' in text:
        print(f"TAG: {r['TAG']:<10} | Eq: {str(r['EQUIPMENT']):<35} | Context: {str(r['RAW_PROCESS_CONTEXT']):<20} | Loc: {str(r['MEASUREMENT_LOCATION'])[:70]}")
