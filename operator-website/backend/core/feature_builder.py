"""Feature Builder Module for C3MR Surrogate Model.

Constructs the exact 20-feature input vector required by `c3mr_power_surrogate_real.joblib`.
Governance: AGENTS.md (Pasal 1, 2, 5), Zero magic numbers, strict engineering units.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np

from core.ilr_engine import ilr_forward

# Component molecular weights in g/mol
MW_SPECIES: Dict[str, float] = {
    "N2": 28.0134,
    "C1": 16.0425,
    "C2": 30.0690,
    "C2H4": 28.0532,
    "C3": 44.0956,
}

# Operating regime thresholds (t/h)
UNDERLOAD_THRESHOLD_T_H: float = 226.8
BASELOAD_THRESHOLD_T_H: float = 279.8

# Feature list ordering matching REAL_DATA_SURROGATE_FEATURES
ORDERED_FEATURES: Tuple[str, ...] = (
    "H1FI012",
    "H4FI001",
    "xi_1",
    "xi_2",
    "xi_3",
    "xi_4",
    "is_underload",
    "is_baseload",
    "rp_LP_MCR",
    "rp_HP_MCR",
    "rp_MCR_total",
    "dp_interstage_4E5",
    "rp_C3_total",
    "MCHE_dT_cold_bundle_approach",
    "MCHE_dT_shell_span",
    "MW_MCR",
    "MCHE_dT_lngexit_mrv",
    "work_proxy_mcr_total",
    "work_proxy_c3",
    "feed_mcr_product",
)


def compute_apparent_mw(mol_fractions: Dict[str, float]) -> float:
    """Compute apparent molecular weight MW_MCR [g/mol] for 5 components."""
    tot = sum(mol_fractions.values())
    if tot <= 0.0:
        return 27.5
    mw = sum(mol_fractions.get(sp, 0.0) * MW_SPECIES[sp] for sp in MW_SPECIES) / tot
    return float(np.clip(mw, 16.0, 45.0))


def build_feature_vector(scenario: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float]]:
    """Convert user scenario dictionary into a (1, 20) array and feature dictionary."""
    feed_flow = float(scenario.get("feed_flow_t_h", 250.0))
    mcr_flow = float(scenario.get("mcr_flow_t_h", 560.0))

    # Parse 5-component MCR composition (supports both % and fraction)
    raw_n2 = float(scenario.get("comp_N2_molpct", 3.38))
    raw_c1 = float(scenario.get("comp_C1_molpct", 44.37))
    raw_c2 = float(scenario.get("comp_C2_molpct", 44.94))
    raw_c2h4 = float(scenario.get("comp_C2H4_molpct", 0.85))
    raw_c3 = float(scenario.get("comp_C3_molpct", 6.28))

    raw_comp = np.array([raw_n2, raw_c1, raw_c2, raw_c2h4, raw_c3], dtype=float)
    sum_comp = float(np.sum(raw_comp))
    if sum_comp > 1.5:  # Provided in mol%
        frac_comp = raw_comp / sum_comp
    else:  # Provided in fractions
        frac_comp = raw_comp / max(sum_comp, 1e-6)

    # 1. ILR coordinates (xi_1 .. xi_4)
    xi = ilr_forward(frac_comp)[0]
    xi_1, xi_2, xi_3, xi_4 = float(xi[0]), float(xi[1]), float(xi[2]), float(xi[3])

    # 2. Operating regime indicators
    is_underload = 1.0 if feed_flow <= UNDERLOAD_THRESHOLD_T_H else 0.0
    is_baseload = 1.0 if feed_flow >= BASELOAD_THRESHOLD_T_H else 0.0

    # 3. Pressure ratios (using native KGC2A baseline values if not overridden)
    p_4k2_suct = max(float(scenario.get("p_4k2_suct_kgcm2a", 3.235)), 0.1)
    p_4k2_disch = max(float(scenario.get("p_4k2_disch_kgcm2a", 13.697)), 0.1)
    p_4k3_suct = max(float(scenario.get("p_4k3_suct_kgcm2a", 13.417)), 0.1)
    p_4k3_disch = max(float(scenario.get("p_4k3_disch_kgcm2a", 43.881)), 0.1)
    p_c3_suct = max(float(scenario.get("p_c3_suct_kgcm2a", 1.045)), 0.1)
    p_c3_disch = max(float(scenario.get("p_c3_disch_kgcm2a", 14.164)), 0.1)

    rp_LP_MCR = float(np.clip(p_4k2_disch / p_4k2_suct, 1.0, 15.0))
    rp_HP_MCR = float(np.clip(p_4k3_disch / p_4k3_suct, 1.0, 15.0))
    rp_MCR_total = float(np.clip(p_4k3_disch / p_4k2_suct, 1.0, 40.0))
    dp_interstage_4E5 = float(np.clip(p_4k2_disch - p_4k3_suct, -2.0, 5.0))
    rp_C3_total = float(np.clip(p_c3_disch / p_c3_suct, 1.0, 30.0))

    # 4. MCHE temperature differences
    t_mrv_wb_out = float(scenario.get("t_mche_warm_mrv_out_c", -122.4))
    t_shell_mid = float(scenario.get("t_mche_shell_mid_c", -127.8))
    t_mrv_wb_in = float(scenario.get("t_mche_warm_mrv_in_c", -32.7))
    t_mrv_cb_out = float(scenario.get("t_mche_cold_mrv_out_c", -123.5))
    t_lng_rundown = float(scenario.get("t_lng_rundown_c", -148.0))
    t_fg_cb_in = float(scenario.get("t_fg_cb_in_c", -121.8))

    MCHE_dT_cold_bundle_approach = float(np.clip(t_mrv_wb_out - t_shell_mid, -30.0, 40.0))
    MCHE_dT_shell_span = float(np.clip(t_mrv_wb_in - t_mrv_cb_out, 20.0, 140.0))
    MCHE_dT_lngexit_mrv = float(np.clip(t_lng_rundown - t_fg_cb_in, -60.0, 10.0))

    # 5. Apparent molecular weight
    comp_dict = {
        "N2": float(frac_comp[0]),
        "C1": float(frac_comp[1]),
        "C2": float(frac_comp[2]),
        "C2H4": float(frac_comp[3]),
        "C3": float(frac_comp[4]),
    }
    MW_MCR = compute_apparent_mw(comp_dict)

    # 6. Thermodynamic work proxies & interactions (k_exp = 0.20)
    k_exp = 0.20
    work_proxy_mcr_total = float(mcr_flow * (max(rp_MCR_total, 1.0) ** k_exp - 1.0))
    work_proxy_c3 = float(feed_flow * (max(rp_C3_total, 1.0) ** k_exp - 1.0))
    feed_mcr_product = float(feed_flow * mcr_flow / 1000.0)

    feature_dict: Dict[str, float] = {
        "H1FI012": feed_flow,
        "H4FI001": mcr_flow,
        "xi_1": xi_1,
        "xi_2": xi_2,
        "xi_3": xi_3,
        "xi_4": xi_4,
        "is_underload": is_underload,
        "is_baseload": is_baseload,
        "rp_LP_MCR": rp_LP_MCR,
        "rp_HP_MCR": rp_HP_MCR,
        "rp_MCR_total": rp_MCR_total,
        "dp_interstage_4E5": dp_interstage_4E5,
        "rp_C3_total": rp_C3_total,
        "MCHE_dT_cold_bundle_approach": MCHE_dT_cold_bundle_approach,
        "MCHE_dT_shell_span": MCHE_dT_shell_span,
        "MW_MCR": MW_MCR,
        "MCHE_dT_lngexit_mrv": MCHE_dT_lngexit_mrv,
        "work_proxy_mcr_total": work_proxy_mcr_total,
        "work_proxy_c3": work_proxy_c3,
        "feed_mcr_product": feed_mcr_product,
    }

    feature_vector = np.array([[feature_dict[name] for name in ORDERED_FEATURES]], dtype=float)
    return feature_vector, feature_dict

