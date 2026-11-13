"""
PRIORITY 3 — SIMULATOR AUDIT
Locate, hash, and document every available HYSYS case file.
Check for COM automation interface.
Record what can and cannot be executed.
"""
import os, json, hashlib
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "ikms_2026", "rebuild_v3_3", "03_simulator_audit")
os.makedirs(OUT_DIR, exist_ok=True)

# =============================================================================
# STEP 1: INVENTORY ALL .hsc FILES
# =============================================================================
hsc_files = []
for root, dirs, files in os.walk(BASE_DIR):
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', '.git', 'node_modules', '.next', '.gemini', 'dist', 'build']]
    for f in files:
        if f.endswith('.hsc'):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, BASE_DIR).replace("\\", "/")
            size = os.path.getsize(fp)
            with open(fp, 'rb') as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            hsc_files.append({
                "filename": f,
                "relative_path": rel,
                "size_bytes": size,
                "sha256": sha,
            })

df_hsc = pd.DataFrame(hsc_files)
df_hsc.to_csv(os.path.join(OUT_DIR, "hysys_case_inventory.csv"), index=False)

# =============================================================================
# STEP 2: CLASSIFY PRIMARY vs VALIDATION vs WORKING COPIES
# =============================================================================
primary_models = []
validation_cases = []
work_copies = []

for rec in hsc_files:
    p = rec["relative_path"]
    if "ikms_2026/hysys_models/" in p and "validation_cases" not in p:
        primary_models.append(rec)
    elif "validation_cases" in p:
        validation_cases.append(rec)
    elif "workcopies" in p:
        work_copies.append(rec)

# =============================================================================
# STEP 3: CHECK HYSYS COM AUTOMATION AVAILABILITY
# =============================================================================
hysys_com_available = False
hysys_com_check_result = "NOT TESTED"

try:
    import win32com.client
    try:
        app = win32com.client.Dispatch("HYSYS.Application")
        hysys_com_available = True
        hysys_com_check_result = "HYSYS COM SERVER ACCESSIBLE"
        app.Quit()
    except Exception as e:
        hysys_com_check_result = f"HYSYS COM DISPATCH FAILED: {str(e)}"
except ImportError:
    hysys_com_check_result = "win32com NOT INSTALLED — CANNOT USE HYSYS COM AUTOMATION"

# =============================================================================
# STEP 4: DOCUMENT PRIMARY MODEL SPECIFICATIONS (from README)
# =============================================================================
model_spec = {
    "simulator": "Aspen HYSYS V12.1",
    "property_package": "Peng-Robinson Equation of State (PR-EOS)",
    "eos": "Peng-Robinson (1976)",
    "binary_interaction_parameters": "HYSYS DEFAULT (NOT INDEPENDENTLY VERIFIED)",
    "components": [
        "Nitrogen (N2)", "Methane (C1)", "Ethane (C2)", "Ethylene (C2H4)",
        "Propane (C3)", "i-Butane (iC4)", "n-Butane (nC4)", "i-Pentane (iC5)"
    ],
    "flow_basis": "DCS telemetry Train H, 2024-2026",
    "primary_cases": [
        {
            "filename": "C3MR.hsc",
            "description": "Base C3MR Train H flowsheet: 3-stage propane precooling + MCR cycle",
            "feed_pressure_kgcm2g": 41.2,
            "mche_inlet_temp_C": -33.0,
        },
        {
            "filename": "MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc",
            "description": "Enhanced model with 4E-40 subcooler, 4UV-53 kickback, 4TV-510 reheat",
        },
    ],
    "validation_cases_count": len(validation_cases),
    "validation_quantiles": ["P10", "P25", "P40", "P50", "P60", "P75", "P90"],
    "convergence_status": "UNKNOWN — REQUIRES HYSYS RUNTIME TO VERIFY",
    "material_balance_closure": "UNKNOWN — REQUIRES HYSYS RUNTIME TO VERIFY",
    "energy_balance_closure": "UNKNOWN — REQUIRES HYSYS RUNTIME TO VERIFY",
    "equipment_models": {
        "MCHE_5E1": "LNG Multi-Stream Heat Exchanger",
        "4K-1": "Centrifugal Compressor (3-section, Propane)",
        "4K-2": "Centrifugal Compressor (single casing, MCR LP)",
        "4K-3": "Centrifugal Compressor (single casing, MCR HP)",
        "4KT-1": "Steam Turbine Driver (C3 compressor)",
        "4KT-2": "Steam Turbine Driver (MCR LP)",
        "4KT-3": "Steam Turbine Driver (MCR HP)",
        "4E-40": "Heavy MCR Subcooler",
    },
    "stream_boundaries": {
        "feed_gas": "From Scrub Column 3C-1 overhead",
        "lng_product": "MCHE 5E-1 cold end rundown",
        "mcr_circuit": "Closed loop: 4K-2 → 4K-3 → aftercooler → MCHE → separator → 4K-2",
        "c3_circuit": "Closed loop: 4K-1 → condensers → chillers → 4K-1",
        "steam": "HP header 60 barg / 440°C → turbines → surface condenser 0.12 bara",
    },
    "control_assumptions": "UNKNOWN — REQUIRES CASE FILE INSPECTION IN HYSYS",
}

# =============================================================================
# STEP 5: HYSYS EXECUTION CAPABILITY ASSESSMENT
# =============================================================================
execution_assessment = {
    "hysys_com_automation": hysys_com_available,
    "hysys_com_check_result": hysys_com_check_result,
    "can_execute_physical_doe": hysys_com_available,
    "can_verify_convergence": hysys_com_available,
    "can_extract_composite_curves": hysys_com_available,
    "can_read_stream_results": hysys_com_available,
    "alternative_without_hysys": (
        "CoolProp PR-EOS can compute single-phase and two-phase properties for pure components "
        "and simple mixtures. However, it CANNOT replicate the full Aspen HYSYS flowsheet "
        "(multi-stream heat exchanger rating, compressor characteristic map matching, "
        "recycle convergence, or coupled separator-MCHE-compressor loop). "
        "CoolProp-based DoE would be a REDUCED-FIDELITY SURROGATE, not a physical simulator replacement."
    ),
    "blocker_if_no_hysys": (
        "Without HYSYS COM automation, Priority 7 (Physical DoE) and Priority 8 (True Joint Optimization) "
        "CANNOT produce genuine physical simulator results. "
        "The optimization must be reported as BLOCKED PENDING HYSYS RUNTIME."
    ),
}

# =============================================================================
# SAVE ALL OUTPUTS
# =============================================================================
full_audit = {
    "model_specification": model_spec,
    "execution_assessment": execution_assessment,
    "hsc_file_count": len(hsc_files),
    "primary_model_count": len(primary_models),
    "validation_case_count": len(validation_cases),
    "working_copy_count": len(work_copies),
}

with open(os.path.join(OUT_DIR, "simulator_audit_report.json"), "w") as fp:
    json.dump(full_audit, fp, indent=2)

print(f"P3 complete:")
print(f"  Total .hsc files found: {len(hsc_files)}")
print(f"  Primary models: {len(primary_models)}")
print(f"  Validation cases: {len(validation_cases)}")
print(f"  Working copies: {len(work_copies)}")
print(f"  HYSYS COM automation: {hysys_com_check_result}")
