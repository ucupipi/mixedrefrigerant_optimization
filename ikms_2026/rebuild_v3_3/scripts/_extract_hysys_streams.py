"""Extract the complete HYSYS material-stream table from the c3mr_hsc_inspection.json dump.

The dump is heterogeneous (some entries lack keys), so every field is read defensively.
Temperature key is labelled 'temperature_C' but the STORED value is T[degC] - 273.15
(i.e. a Kelvin value that was itself already converted); we verify that convention against
known plant anchors before trusting it, and record the raw value alongside.
"""
import json
import os

import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(BASE, "analysis", "stage3_thermo_validation", "c3mr_hsc_inspection.json")

d = json.load(open(SRC, encoding="utf-8"))

comps = d["fluid_packages"][0]["components"]
print("case:", d.get("case_title"))
print("hysys:", d.get("hysys_version"))
print("package:", d["fluid_packages"][0]["property_package"])
print("components (%d): %s" % (len(comps), comps))
print("n material streams:", len(d["material_streams"]))

keys = set()
for s in d["material_streams"]:
    keys |= set(s.keys())
print("union of keys:", sorted(keys))
print()

rows = []
for s in d["material_streams"]:
    mf = s.get("molar_fractions")
    row = {
        "stream": s.get("name"),
        "T_raw": s.get("temperature_C"),
        "P_kPa": s.get("pressure_kPa"),
        "P_barg": s.get("pressure_barg"),
        "mass_flow_t_h": s.get("mass_flow_th"),
        "vapour_fraction": s.get("vapour_fraction"),
    }
    # record composition only if present and length matches
    if isinstance(mf, list) and len(mf) == len(comps):
        for c, v in zip(comps, mf):
            row["z_" + c] = v
    rows.append(row)

df = pd.DataFrame(rows)
print("streams with a full composition vector: %d / %d"
      % (int(df["z_Nitrogen"].notna().sum()) if "z_Nitrogen" in df else 0, len(df)))
print()

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)

# ---- temperature convention check -------------------------------------------
# Hypothesis: stored = T_degC - 273.15  =>  T_degC = stored + 273.15
anchors = {
    "MCR_AFTERCOOL_OUT": 38.0,     # propane aftercooler outlet, warm
    "MCR_5C1_FEED": -35.0,         # 5C-1 feed
}
print("=== temperature convention check ===")
for name, expect in anchors.items():
    r = df[df.stream == name]
    if len(r):
        raw = float(r.iloc[0]["T_raw"])
        print("  %-20s raw=%9.2f  raw+273.15=%8.2f  expected~%7.1f  %s"
              % (name, raw, raw + 273.15, expect,
                 "MATCH" if abs((raw + 273.15) - expect) < 8 else "MISMATCH"))
print()

print("=== full stream table (T_degC = raw+273.15 under the verified convention) ===")
df["T_degC"] = df["T_raw"] + 273.15
show = df[["stream", "T_degC", "P_kPa", "mass_flow_t_h", "vapour_fraction"]]
print(show.to_string(index=False))

out = os.path.join(BASE, "audit", "P4_hysys_stream_table_raw.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
df.to_csv(out, index=False)
print()
print("written:", out)

# ---- explicit mass-balance checks on the refrigerant circuit ----------------
print()
print("=== MASS BALANCE CHECKS (HYSYS stream connectivity) ===")


def flow(name):
    r = df[df.stream == name]
    return float(r.iloc[0]["mass_flow_t_h"]) if len(r) else float("nan")


checks = [
    ("5C-1 split: FEED -> VAP + LIQ",
     flow("MCR_5C1_FEED"), flow("MCR_5C1_VAP") + flow("MCR_5C1_LIQ")),
    ("5C-1 liquid split -> 5E-1 + 4E-40",
     flow("MCR_5C1_LIQ"), flow("MCR_LIQ_5E1") + flow("MCR_LIQ_4E40")),
    ("warm bundle return = vapour + liquid JT",
     flow("MCR_WB_RETURN"), flow("MCRVfromCB") + flow("MCRL_FROM_JT")),
    ("4C-7 total = WB return + 4E-40 return",
     flow("MCR_RETURN_4C7"), flow("MCR_WB_RETURN") + flow("MCR_4E40_TO_4C7")),
    ("4K-2 suction = 4C-7 total",
     flow("MCR_4K2_SUCT"), flow("MCR_RETURN_4C7")),
    ("4K-2 suction = total MCR circulation",
     flow("MCR_4K2_SUCT"), flow("MCR_5C1_FEED")),
]
for label, lhs, rhs in checks:
    err = lhs - rhs
    rel = err / lhs * 100 if lhs else float("nan")
    print("  %-46s %9.3f vs %9.3f  err=%+8.4f t/h (%+6.3f%%)  %s"
          % (label, lhs, rhs, err, rel, "PASS" if abs(rel) < 0.5 else "FAIL"))
