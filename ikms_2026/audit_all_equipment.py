import pandas as pd

v3_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_MASTER_REGISTER_2025_V3.csv"
loc_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_PHYSICAL_LOCATION_FORENSIC_2025.csv"

df_v3 = pd.read_csv(v3_path)
df_loc = pd.read_csv(loc_path)

print("=== EQUIPMENT IN V3 ===")
eqs = df_v3['Equipment'].dropna().unique()
for eq in sorted(eqs):
    print(" ", eq)

print("\n=== SEARCHING 4C-8, 5C-1, 4E-21, 4E-22, 4E-5, 4E-6 ===")
for t in ['4C-7', '4C-8', '5C-1', '5C-2', '4E-5', '4E-6', '4E-7', '4E-8', '4E-9', '4E-10', '4E-12', '4E-14', '4E-40', '4E-21', '4E-22']:
    sub = df_loc[df_loc['EQUIPMENT'].astype(str).str.contains(t, case=False, na=False) | df_loc['MEASUREMENT_LOCATION'].astype(str).str.contains(t, case=False, na=False) | df_loc['RAW_PROCESS_CONTEXT'].astype(str).str.contains(t, case=False, na=False)]
    if len(sub) > 0:
        print(f"\n--- Matches for {t} ({len(sub)}) ---")
        for _, r in sub.iterrows():
            print(f"  TAG: {r['TAG']:<10} | Eq: {r['EQUIPMENT']} | Loc: {r['MEASUREMENT_LOCATION']}")
