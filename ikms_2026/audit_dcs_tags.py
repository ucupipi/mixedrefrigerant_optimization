import pandas as pd

reg_path = r"D:/User/Documents/KULIAH/LOMBA/OILWEEK2026/01_tags/FULL_AUTHORITATIVE_TAG_REGISTER_2025.csv"
df = pd.read_csv(reg_path)

print("=== ALL UNIQUE CAUSAL ROLES & PRIORITIES ===")
print(df[["CAUSAL_ROLE", "EXPORT_PRIORITY"]].value_counts())

print("\n=== P0 CORE MODEL TAGS (35 tags) ===")
p0 = df[df["EXPORT_PRIORITY"] == "P0_CORE_MODEL"]
for idx, r in p0.iterrows():
    print(f"{r['ROW2_TAG']:<12} | Context: {str(r['ROW1_PROCESS_CONTEXT']):<25} | Unit: {str(r['UNIT_IF_KNOWN']):<10} | Sys: {r['SYSTEM']}")

print("\n=== P1 SAFETY / CONSTRAINTS / KEY CONTROL TAGS ===")
p1 = df[df["EXPORT_PRIORITY"].str.contains("P1", na=False) | df["CAUSAL_ROLE"].str.contains("SAFETY|CONSTRAINT", case=False, na=False)]
for idx, r in p1.iterrows():
    print(f"{r['ROW2_TAG']:<12} | Context: {str(r['ROW1_PROCESS_CONTEXT']):<25} | Unit: {str(r['UNIT_IF_KNOWN']):<10} | Prio: {r['EXPORT_PRIORITY']:<15} | Role: {r['CAUSAL_ROLE']}")

print("\n=== ALL OTHER DCS TRANSMITTER TAGS BY SYSTEM ===")
for sys_name, group in df.groupby("SYSTEM"):
    print(f"\n--- System: {sys_name} ({len(group)} tags) ---")
    for idx, r in group.iterrows():
        print(f"  {r['ROW2_TAG']:<12} | {str(r['ROW1_PROCESS_CONTEXT']):<25} | {str(r['UNIT_IF_KNOWN']):<10} | {r['EXPORT_PRIORITY']:<15} | {r['NOTES'][:60]}")

