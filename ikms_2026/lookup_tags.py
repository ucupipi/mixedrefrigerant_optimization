import pandas as pd

v3_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_MASTER_REGISTER_2025_V3.csv"
loc_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/TAG_PHYSICAL_LOCATION_FORENSIC_2025.csv"

df_v3 = pd.read_csv(v3_path)
df_loc = pd.read_csv(loc_path)

p0_tags = [
    '3fi4', '4TI1A', '4TI2A', '4TI4B', '4TI6B', '4TI7B', '4TI8B',
    '4PI14B', '4PI15A', '4PI16B', '4PI17B', '4TI215', '4TI214',
    '5PI10', '5PI12', '4FI10B', '4TI207', '4TI209', '5FI6A',
    '4FI31A', '4FI29A', '4FI30A', '5PDI4', '5PDI3', '5PDI25A',
    '5FI1', '5fic2', '4FI13A', '4TI218', '4TI296', '5TI23', '5TI47',
    '4SI23A', '4SI28A', '4FI11B'
]

print("--- DETAILED DCS TAG LOOKUP (35 P0 CORE TAGS) ---")
for t in p0_tags:
    v3_m = df_v3[df_v3['Instrument_Tag'].astype(str).str.lower() == t.lower()]
    loc_m = df_loc[df_loc['TAG'].astype(str).str.lower() == t.lower()]
    
    desc = v3_m['Physical_Definition'].iloc[0] if len(v3_m) > 0 and pd.notna(v3_m['Physical_Definition'].iloc[0]) else "N/A"
    unit = v3_m['Unit'].iloc[0] if len(v3_m) > 0 and pd.notna(v3_m['Unit'].iloc[0]) else "N/A"
    eq = v3_m['Equipment'].iloc[0] if len(v3_m) > 0 and pd.notna(v3_m['Equipment'].iloc[0]) else "N/A"
    loc = loc_m['MEASUREMENT_LOCATION'].iloc[0] if len(loc_m) > 0 and pd.notna(loc_m['MEASUREMENT_LOCATION'].iloc[0]) else "N/A"
    med = loc_m['RAW_DCS_MEDIAN'].iloc[0] if len(loc_m) > 0 and pd.notna(loc_m['RAW_DCS_MEDIAN'].iloc[0]) else "N/A"
    rng = loc_m['RAW_DCS_RANGE'].iloc[0] if len(loc_m) > 0 and pd.notna(loc_m['RAW_DCS_RANGE'].iloc[0]) else "N/A"
    causal = loc_m['CAUSAL_ROLE'].iloc[0] if len(loc_m) > 0 and pd.notna(loc_m['CAUSAL_ROLE'].iloc[0]) else "N/A"
    
    print(f"Tag: {t:<9} | Eq: {eq:<8} | Unit: {unit:<10} | Median: {str(med):<10} | Range: {str(rng):<15} | Loc: {loc}")
    print(f"       -> Desc: {desc}")
