import pandas as pd

p_audit = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/REFRIGERANT_TURBINE_STEAM_TAG_AUDIT.csv"
p_fg = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/BOILER_FUEL_GAS_TAG_MAPPING_2025.csv"
p_lvl = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/LEVEL_INVENTORY_TAG_MAPPING_2025.csv"

print("--- TURBINE STEAM TAG AUDIT ---")
try:
    df_st = pd.read_csv(p_audit)
    print(df_st.to_string())
except Exception as e:
    print(e)

print("\n--- LEVEL INVENTORY TAGS ---")
try:
    df_l = pd.read_csv(p_lvl)
    print(df_l[['TAG_CANONICAL', 'SYSTEM', 'EQUIPMENT', 'MEASUREMENT_LOCATION', 'CAUSAL_ROLE']].to_string())
except Exception as e:
    print(e)

