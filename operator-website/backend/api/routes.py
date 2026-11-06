"""FastAPI router defining all endpoints for Operator Decision-Support Website.

READ-ONLY: Zero DCS control commands, zero set point modification.
Governance: AGENTS.md (Pasal 1–13).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
import yaml
import numpy as np

import sys
from pathlib import Path
_backend_dir = Path(__file__).resolve().parent.parent
for p in (str(_backend_dir), str(_backend_dir / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from api.schemas import (
    ConfidenceSummary,
    DomainCheckSummary,
    FlashDrumSummary,
    MakeupAdvisorySummary,
    MakeupInjectionItem,
    OptimizeRequest,
    OptimizeResponse,
    PredictRequest,
    PredictionSummary,
    PredictResponse,
    SafetyCheckSummary,
)
from thermo.flash_drum_vle import calculate_flash_drum_5c1
from core.feature_builder import (
    ORDERED_FEATURES,
    build_feature_vector,
)
from core.makeup_calculator import calculate_makeup_recommendations
from core.optimizer_engine import recommend

def classify_regime(flow: float) -> str:
    if flow <= 226.8:
        return "underload"
    elif flow >= 279.8:
        return "baseload"
    return "transition"
from core.model_loader import get_model_info, get_rebuild_root, load_surrogate_model
from core.validator import validate_operating_point

router = APIRouter()

# Stratified R² values from evaluation_report_real.json
REGIME_METRICS: Dict[str, Dict[str, float]] = {
    "underload": {"r2": 0.491, "mae_mw": 0.774, "nmae_pct": 0.929},
    "transition": {"r2": 0.477, "mae_mw": 1.250, "nmae_pct": 1.400},
    "baseload": {"r2": 0.668, "mae_mw": 0.520, "nmae_pct": 0.565},
}

# Empirical C3 (4KT-1) power share derived from 231 valid M.C.R shifts (scratch/check_split.py)
# via per-turbine condensate meters H4FI031A / (H4FI031A + H4FI029A + H4FI030A)
C3_POWER_SHARE_BY_REGIME: Dict[str, float] = {
    "underload": 0.4225,
    "transition": 0.3775,
    "baseload": 0.3634,
}

# Physical & Decarbonization Constants (Stage 08 & Manual Book Modul 8)
STEAM_RATE_T_PER_MWH: float = 4.04         # Condensate anchor (stage 08)
FUEL_GAS_NM3_PER_T_STEAM: float = 97.7     # Modul 8: Nm3 fuel gas / t steam
FUEL_GAS_GJ_PER_NM3: float = 0.038        # Modul 8: GJ / Nm3
CO2_KG_PER_GJ: float = 56.1               # Modul 8: IPCC 2006 emission factor


def _load_baseline() -> Dict[str, float]:
    """Helper to load baseline power and feed flow from demo_snapshot.json."""
    data_path = Path(__file__).resolve().parents[1] / "data" / "demo_snapshot.json"
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                snap = json.load(f)
            total_mw = float(snap.get("baseline_model_output", {}).get("total_shaft_power_mw", 84.48))
            feed_t_h = float(snap.get("values", {}).get("H1FI012", {}).get("value", 245.8))
            return {"total_mw": total_mw, "feed_t_h": feed_t_h}
        except Exception:
            pass
    return {"total_mw": 84.48, "feed_t_h": 245.8}


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": "Badak LNG Train H C3MR Operator Decision-Support API",
        "mode": "READ_ONLY_DECISION_SUPPORT",
    }


@router.get("/api/v1/status")
def system_status() -> Dict[str, Any]:
    """Retrieve model status, runtime parameters, and governance metadata."""
    try:
        info = get_model_info()
        return {
            "status": "READY",
            "model_loaded": True,
            **info,
        }
    except Exception as exc:
        import traceback
        print(f"[ERROR] system_status failed:\n{traceback.format_exc()}", flush=True)
        return {
            "status": "ERROR",
            "model_loaded": False,
            "error": str(exc),
        }


@router.get("/api/v1/variables")
def get_variables_registry() -> Dict[str, Any]:
    """Load and return the structured variable registry from config/variable_registry.yaml."""
    config_path = Path(__file__).resolve().parents[2] / "config" / "variable_registry.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Variable registry configuration not found")
    with open(config_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
    return registry


@router.get("/api/v1/demo-snapshot")
@router.get("/snapshot")
def get_demo_snapshot() -> Dict[str, Any]:
    """Retrieve pre-configured baseline operational snapshot labeled as DEMO."""
    data_path = Path(__file__).resolve().parents[1] / "data" / "demo_snapshot.json"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Demo snapshot file not found")
    with open(data_path, "r", encoding="utf-8") as f:
        snapshot = json.load(f)
    return snapshot


@router.get("/api/v1/model/schema")
def get_model_schema() -> Dict[str, Any]:
    """Return model feature requirements, monotonic constraints, and evaluation reports."""
    rebuild_root = get_rebuild_root()
    eval_path = rebuild_root / "reports" / "evaluation_report_real.json"
    eval_data = {}
    if eval_path.exists():
        with open(eval_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
            
    return {
        "features": list(ORDERED_FEATURES),
        "target": "total_shaft_power_mw",
        "target_unit": "MW",
        "battery_limit": "Total Train C3MR (4KT-1 Propane + 4KT-2 LP MCR + 4KT-3 HP MCR)",
        "evaluation": eval_data,
    }


@router.post("/api/v1/predict", response_model=PredictResponse)
@router.post("/prediction", response_model=PredictResponse)
def predict_scenario(request: PredictRequest) -> PredictResponse:
    """Predict total C3MR shaft power from operator scenario with safety & domain audits."""
    try:
        model = load_surrogate_model()
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] predict_scenario load_surrogate_model failed:\n{tb}", flush=True)
        raise HTTPException(status_code=500, detail=f"Model loading error: {exc}")

    req_dict = request.model_dump(exclude_unset=True)

    # 1. Feature construction (20 features)
    feature_vector, feature_dict = build_feature_vector(req_dict)

    # 2. Run surrogate prediction
    power_pred_mw = float(model.predict(feature_vector)[0])
    # Sanity clipping to physical compressor limits [40.0, 150.0] MW
    power_pred_mw = float(np.clip(power_pred_mw, 40.0, 150.0))

    # 3. LNG Rundown Flow (H5FI6A) & Specific Energy Consumption SEC [kWh/t]
    feed_flow = float(req_dict.get("feed_flow_t_h", 250.0))
    flash_summary = None
    if req_dict.get("lng_flow_t_h") is not None and float(req_dict["lng_flow_t_h"]) > 10.0:
        lng_flow_t_h = float(req_dict["lng_flow_t_h"])
        sec_lng_status = "VALID (Meter Fiskal H5FI6A)"
    elif feed_flow > 10.0:
        t_mche = float(req_dict.get("t_mche_out_c", -152.5))
        p_mche = float(req_dict.get("p_mche_out_kgcm2g", 41.5))
        p_flash = float(req_dict.get("p_flash_kgcm2g", 0.30))
        flash_res = calculate_flash_drum_5c1(
            feed_flow_t_h=feed_flow,
            t_mche_out_c=t_mche,
            p_mche_out_kgcm2g=p_mche,
            p_flash_kgcm2g=p_flash,
        )
        lng_flow_t_h = round(flash_res.lng_liquid_flow_t_h, 2)
        sec_lng_status = f"VALID (PR-EOS Flash 5C-1: Yield {flash_res.mass_liquid_yield * 100:.2f} wt%, T_flash {flash_res.t_flash_c:.1f}°C)"
        flash_summary = FlashDrumSummary(
            feed_flow_t_h=flash_res.feed_flow_t_h,
            lng_liquid_flow_t_h=flash_res.lng_liquid_flow_t_h,
            efg_gas_flow_t_h=flash_res.efg_gas_flow_t_h,
            mass_liquid_yield=flash_res.mass_liquid_yield,
            vapor_fraction_mol=flash_res.vapor_fraction_mol,
            t_flash_c=flash_res.t_flash_c,
            t_bubble_c=flash_res.t_bubble_c,
            p_flash_kgcm2g=flash_res.p_flash_kgcm2g,
            status=flash_res.status,
        )
    else:
        lng_flow_t_h = None
        sec_lng_status = "N/A — data produksi LNG belum tersedia"

    sec_lng_kwh_per_t = (power_pred_mw * 1000.0 / lng_flow_t_h) if lng_flow_t_h and lng_flow_t_h > 10.0 else None
    specific_shaft_power_feed = (power_pred_mw * 1000.0 / feed_flow) if feed_flow > 10.0 else None
    sec_kwh_per_t = sec_lng_kwh_per_t if sec_lng_kwh_per_t is not None else specific_shaft_power_feed

    # 4. Operating regime classification
    regime = "underload" if feed_flow <= 226.8 else ("baseload" if feed_flow >= 279.8 else "transition")

    # 5. Process safety and domain validation
    validation = validate_operating_point(req_dict)

    # 6. Confidence and uncertainty packaging
    regime_info = REGIME_METRICS.get(regime, {"r2": 0.50, "mae_mw": 0.80})
    reg_r2 = regime_info.get("r2")
    warning_text = None
    if reg_r2 and reg_r2 < 0.60:
        warning_text = (
            f"Perhatian: Akurasi model pada rezim {regime} (R² = {reg_r2:.3f}) lebih rendah dari baseload. "
            f"Gunakan hasil sebagai estimasi awal dan konsultasikan dengan Process Engineer."
        )

    # 7. Hydrocarbon Make-up Injection Advisory
    # Actual composition = operator-entered GC values (Aktual DCS column); falls back to
    # demo snapshot GC values when the client does not send them.
    snapshot_gc = {"N2": 3.38, "C1": 44.37, "C2": 44.94, "C2H4": 0.85, "C3": 6.28}  # demo_snapshot.json GC
    actual_comp = {
        k: float(req_dict[f"actual_comp_{k}_molpct"])
        if req_dict.get(f"actual_comp_{k}_molpct") is not None else v
        for k, v in snapshot_gc.items()
    }
    target_comp = {
        "N2": float(req_dict.get("comp_N2_molpct", 3.38)),
        "C1": float(req_dict.get("comp_C1_molpct", 44.37)),
        "C2": float(req_dict.get("comp_C2_molpct", 44.94)),
        "C2H4": float(req_dict.get("comp_C2H4_molpct", 0.85)),
        "C3": float(req_dict.get("comp_C3_molpct", 6.28)),
    }
    transition_hrs = float(req_dict.get("transition_hours", 2.0))
    makeup_calc = calculate_makeup_recommendations(
        actual_molpct=actual_comp,
        target_molpct=target_comp,
        transition_hours=transition_hrs,
    )
    makeup_summary = MakeupAdvisorySummary(
        transition_hours=makeup_calc["transition_hours"],
        estimated_inventory_kg=makeup_calc["estimated_inventory_kg"],
        total_makeup_flow_nm3_h=makeup_calc["total_makeup_flow_nm3_h"],
        total_makeup_flow_kg_h=makeup_calc["total_makeup_flow_kg_h"],
        items=[MakeupInjectionItem(**item) for item in makeup_calc["items"]],
        operational_notes=makeup_calc["operational_notes"],
    )

    # 8. Power decomposition: Propane C3 (4KT-1) vs MCR (4KT-2 + 4KT-3)  [AGENTS.md Pasal 10]
    # C3 share = H4FI031A / (H4FI031A + H4FI029A + H4FI030A) per-turbine condensate meters
    # (power = condensate / 4.04 t/MWh for every driver, so the steam rate cancels).
    # Median per regime over 231 valid M.C.R shifts in master_shift_level.parquet
    # (scratch/check_split.py). Speed-cube cross-check agrees within 1.2 points.
    # shortcut: regime-median share (IQR width <= 1.5 points), upgrade to a dedicated
    # per-driver surrogate if per-stage power is needed for optimisation.
    frac_c3 = C3_POWER_SHARE_BY_REGIME[regime]
    power_c3_mw = round(power_pred_mw * frac_c3, 2)
    power_mcr_mw = round(power_pred_mw * (1.0 - frac_c3), 2)

    # 9. Deltas vs actual DCS state (evaluated ceteris-paribus at the scenario's feed flow
    #    so that capacity shifts do not distort the MCR refrigerant optimization metrics).
    baseline = _load_baseline()
    actual_power_mw = None
    actual_feed = req_dict.get("actual_feed_flow_t_h")
    if actual_feed is not None and req_dict.get("actual_mcr_flow_t_h") is not None:
        # 9a. Compute actual power at the current DCS feed flow (for display of current state)
        actual_req = dict(req_dict)
        actual_req["feed_flow_t_h"] = float(actual_feed)
        actual_req["mcr_flow_t_h"] = float(req_dict["actual_mcr_flow_t_h"])
        for comp_key in ("N2", "C1", "C2", "C2H4", "C3"):
            actual_req[f"comp_{comp_key}_molpct"] = actual_comp[comp_key]
        actual_vec, _ = build_feature_vector(actual_req)
        actual_power_mw = float(np.clip(float(model.predict(actual_vec)[0]), 40.0, 150.0))

        # 9b. Compute ceteris-paribus baseline at the SAME feed flow as the scenario (feed_flow)
        #     using unoptimized DCS baseline composition & baseline MCR flow
        base_same_feed_req = dict(actual_req)
        base_same_feed_req["feed_flow_t_h"] = feed_flow
        base_same_feed_vec, _ = build_feature_vector(base_same_feed_req)
        baseline_total_mw = float(np.clip(float(model.predict(base_same_feed_vec)[0]), 40.0, 150.0))
        baseline_feed = feed_flow
    else:
        baseline_total_mw = baseline["total_mw"]
        baseline_feed = baseline["feed_t_h"]

    actual_lng_input = req_dict.get("actual_lng_flow_t_h")
    if actual_lng_input is not None and float(actual_lng_input) > 10.0 and abs(baseline_feed - float(actual_feed or baseline_feed)) < 0.1:
        actual_lng_t_h = float(actual_lng_input)
    else:
        base_flash = calculate_flash_drum_5c1(feed_flow_t_h=baseline_feed)
        actual_lng_t_h = round(base_flash.lng_liquid_flow_t_h, 2)

    baseline_sec_lng = (baseline_total_mw * 1000.0 / actual_lng_t_h) if actual_lng_t_h > 10.0 else 0.0
    delta_power_mw = round(power_pred_mw - baseline_total_mw, 2)
    delta_power_pct = round((delta_power_mw / baseline_total_mw) * 100.0, 2) if baseline_total_mw > 0 else 0.0
    delta_sec = round(sec_lng_kwh_per_t - baseline_sec_lng, 2) if sec_lng_kwh_per_t else None

    # 10. CO2 reduction (Manual Book Modul 8 chain):
    #     dSteam [t/h] = dW [MW] x 4.04 t/MWh (stage 08 condensate anchor)
    #     dV_FG [Nm3/h] = dSteam x 97.7 Nm3/t ; CO2 [t] = dV_FG x 0.038 GJ/Nm3 x 56.1 kg/GJ x 1e-3
    co2_abatement_t_day = None
    if delta_power_mw < 0:
        d_steam_t_h = abs(delta_power_mw) * STEAM_RATE_T_PER_MWH
        d_fg_nm3_h = d_steam_t_h * FUEL_GAS_NM3_PER_T_STEAM
        co2_t_h = d_fg_nm3_h * FUEL_GAS_GJ_PER_NM3 * CO2_KG_PER_GJ * 1e-3
        co2_abatement_t_day = round(co2_t_h * 24.0, 1)

    if not validation["all_safe"]:
        status_label = "Skenario Ditolak (Pelanggaran Batas Keselamatan)"
    elif len(validation["warnings"]) > 0:
        status_label = "Ada Kendala yang Perlu Ditinjau (Peringatan Margin)"
    elif not validation["in_domain"]:
        status_label = "Di Luar Domain Operasional Model (D_M > 3.08)"
    else:
        status_label = "Semua kendala yang diperiksa terpenuhi"

    return PredictResponse(
        prediction=PredictionSummary(
            total_shaft_power_mw=round(power_pred_mw, 2),
            power_mcr_mw=power_mcr_mw,
            power_c3_mw=power_c3_mw,
            delta_power_mw=delta_power_mw,
            delta_power_pct=delta_power_pct,
            sec_kwh_per_t=round(sec_lng_kwh_per_t, 2) if sec_lng_kwh_per_t else None,
            specific_shaft_power_feed_kwh_per_t=round(specific_shaft_power_feed, 2) if specific_shaft_power_feed else None,
            sec_lng_kwh_per_t=round(sec_lng_kwh_per_t, 2) if sec_lng_kwh_per_t else None,
            sec_lng_status=sec_lng_status,
            delta_sec_kwh_per_t=delta_sec,
            co2_abatement_t_day=co2_abatement_t_day,
            operating_regime=regime,
            data_label="SIMULASI SKENARIO WHAT-IF",
        ),
        domain_check=DomainCheckSummary(
            in_domain=bool(validation["in_domain"]),
            mahalanobis_distance=float(validation["mahalanobis_distance"]),
            mahalanobis_limit=float(validation["mahalanobis_limit"]),
            composition_closure_ok=abs(validation["composition_sum"] - 100.0) < 1.0 or abs(validation["composition_sum"] - 1.0) < 0.01,
            composition_sum_molpct=float(validation["composition_sum"]),
        ),
        safety_check=SafetyCheckSummary(
            all_safe=bool(validation["all_safe"]),
            status_label=status_label,
            violations=list(validation["violations"]),
            warnings=list(validation["warnings"]),
            unverified_checks=["Peta anti-surge dinamis kompresor sentrifugal (memerlukan kurva head/dp lengkap)"],
        ),
        confidence=ConfidenceSummary(
            mae_mw=0.802,
            bootstrap_ci_lower_mw=round(max(0.0, power_pred_mw - 0.802), 2),
            bootstrap_ci_upper_mw=round(power_pred_mw + 0.802, 2),
            regime_r2=reg_r2,
            regime_warning=warning_text,
        ),
        makeup_advisory=makeup_summary,
        features_computed={k: round(float(v), 4) for k, v in feature_dict.items()},
        actual_power_mw=round(actual_power_mw, 2) if actual_power_mw is not None else None,
        flash_drum_5c1=flash_summary,
    )


@router.post("/api/v1/optimize", response_model=OptimizeResponse)
@router.post("/optimization", response_model=OptimizeResponse)
def optimize_for_feed(request: OptimizeRequest) -> OptimizeResponse:
    """Recommend MCR circulation flow and closest feasible composition for operator feed."""
    actual_comp = None
    if request.actual_comp_N2_molpct is not None:
        actual_comp = {
            "N2": float(request.actual_comp_N2_molpct),
            "C1": float(request.actual_comp_C1_molpct or 44.45),
            "C2": float(request.actual_comp_C2_molpct or 45.02),
            "C2H4": float(request.actual_comp_C2H4_molpct or 0.85),
            "C3": float(request.actual_comp_C3_molpct or 6.29),
        }
    alpha = float(request.alpha_trim or 0.30)
    try:
        rec = recommend(
            feed_t_h=request.feed_flow_t_h,
            actual_comp=actual_comp,
            actual_mcr_flow_t_h=request.actual_mcr_flow_t_h,
            alpha_trim=alpha,
        )
        return OptimizeResponse(**rec)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        print(f"[WARN] optimize_for_feed encountered error, falling back to Pareto table: {exc}\n{traceback.format_exc()}", flush=True)
        from core.optimizer_engine import get_pareto_fallback_recommendation
        rec = get_pareto_fallback_recommendation(
            feed_t_h=request.feed_flow_t_h,
            actual_comp=actual_comp,
            actual_mcr_flow_t_h=request.actual_mcr_flow_t_h,
            alpha_trim=alpha,
        )
        return OptimizeResponse(**rec)


@router.get("/api/v1/historical-summary")
def get_historical_summary() -> Dict[str, Any]:
    """Provide historical trend data points for frontend visualization."""
    rebuild_root = get_rebuild_root()
    parquet_path = rebuild_root / "data" / "processed" / "master_shift_level.parquet"
    
    if not parquet_path.exists():
        # Fallback synthetic grid for air-gapped demo
        feed_grid = [160, 180, 200, 220, 240, 260, 280, 300, 320]
        power_grid = [68.5, 72.1, 76.4, 80.2, 84.5, 89.2, 94.0, 99.5, 105.1]
        return {
            "source": "calibrated_synthetic_grid",
            "points": [{"feed_flow": f, "power_mw": p} for f, p in zip(feed_grid, power_grid)],
        }
        
    try:
        import pandas as pd
        df = pd.read_parquet(parquet_path)
        mcr = df[
            (df.get("stream", "M.C.R") == "M.C.R")
            & (pd.to_numeric(df["treated_gas_mass_flow_t_h_mean"], errors="coerce") > 50.0)
            & (pd.to_numeric(df["total_compressor_power_MW_mean"], errors="coerce") > 30.0)
        ].copy()
        
        # Sample down to 80 points to keep network payload light
        sample_df = mcr.sample(n=min(80, len(mcr)), random_state=42)
        sample_df = sample_df.sort_values("treated_gas_mass_flow_t_h_mean")
        
        points = []
        for _, row in sample_df.iterrows():
            points.append({
                "feed_flow": round(float(row["treated_gas_mass_flow_t_h_mean"]), 1),
                "power_mw": round(float(row["total_compressor_power_MW_mean"]), 2),
                "regime": "underload" if float(row["treated_gas_mass_flow_t_h_mean"]) <= 226.8 else ("baseload" if float(row["treated_gas_mass_flow_t_h_mean"]) >= 279.8 else "transition"),
            })
            
        return {
            "source": "master_shift_level.parquet",
            "n_points": len(points),
            "points": points,
        }
    except Exception as e:
        return {
            "source": "error_fallback",
            "error": str(e),
            "points": [],
        }
