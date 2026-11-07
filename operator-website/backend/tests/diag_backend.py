"""Diagnostic script to inspect power calculation components in Python backend.
Zero em-dash and en-dash rule applied.
"""
import sys
import json
from pathlib import Path
import numpy as np

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

from core.feature_builder import build_feature_vector
from core.model_loader import load_surrogate_model
from api.routes import get_plant3_baseline_power

model = load_surrogate_model()

scenarios = [
    {"name": "turndown 120", "feed_flow_t_h": 120.0, "mcr_flow_t_h": 480.0},
    {"name": "baseline 150", "feed_flow_t_h": 150.0, "mcr_flow_t_h": 560.0},
    {"name": "baseload 303.8", "feed_flow_t_h": 303.8, "mcr_flow_t_h": 620.0},
    {"name": "overload 380", "feed_flow_t_h": 380.0, "mcr_flow_t_h": 680.0},
]

for sc in scenarios:
    feed = sc["feed_flow_t_h"]
    vec, fdict = build_feature_vector(sc)
    
    baseline_phys = get_plant3_baseline_power(feed)
    raw_pred = float(model.predict(vec)[0])
    
    # Also inspect base_model_ (Ridge) and res_model_ (GBDT) separately
    vec_scaled = model.scaler_.transform(vec)
    base_ridge = float(model.base_model_.predict(vec_scaled)[0])
    res_gbdt = float(model.res_model_.predict(vec)[0])
    
    ref_req = dict(sc)
    ref_req["feed_flow_t_h"] = 245.8
    ref_req["mcr_flow_t_h"] = 505.3
    ref_vec, _ = build_feature_vector(ref_req)
    ref_raw_pred = float(model.predict(ref_vec)[0])
    ref_scaled = model.scaler_.transform(ref_vec)
    ref_base_ridge = float(model.base_model_.predict(ref_scaled)[0])
    ref_res_gbdt = float(model.res_model_.predict(ref_vec)[0])
    
    delta_tuning = raw_pred - ref_raw_pred
    delta_ridge = base_ridge - ref_base_ridge
    
    if abs(feed - 245.8) < 1.0:
        final_py = raw_pred
    else:
        final_py = baseline_phys + delta_tuning
        
    final_ridge_only = baseline_phys + delta_ridge
    
    print(f"=== {sc['name']} ===")
    print(f"  feed: {feed}")
    print(f"  baseline_phys: {baseline_phys:.4f}")
    print(f"  raw_pred (Ridge+GBDT): {raw_pred:.4f} (base_ridge={base_ridge:.4f}, res_gbdt={res_gbdt:.4f})")
    print(f"  ref_raw_pred: {ref_raw_pred:.4f} (ref_base_ridge={ref_base_ridge:.4f}, ref_res_gbdt={ref_res_gbdt:.4f})")
    print(f"  delta_tuning: {delta_tuning:.4f}")
    print(f"  delta_ridge: {delta_ridge:.4f}")
    print(f"  Final Backend (routes.py): {final_py:.4f}")
    print(f"  Final Ridge-only: {final_ridge_only:.4f}")
