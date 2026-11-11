import pandas as pd

df = pd.read_csv(r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/FULL_AUTHORITATIVE_TAG_REGISTER_2025.csv")
p0 = df[df['EXPORT_PRIORITY'] == 'P0_CORE_MODEL'].drop_duplicates(subset=['ROW2_TAG'])
print(f"Total Unique P0 tags: {len(p0)}")
for idx, (_, r) in enumerate(p0.iterrows(), 1):
    print(f"{idx:2d}. Tag: {r['ROW2_TAG']:<10} | Context: {str(r['ROW1_PROCESS_CONTEXT']):<25} | Unit: {str(r['UNIT_IF_KNOWN']):<10} | Sys: {r['SYSTEM']}")

