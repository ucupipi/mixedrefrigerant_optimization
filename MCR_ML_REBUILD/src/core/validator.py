"""Process Safety and Domain Validation Module.

Audits operator scenario against verified plant limits, Mahalanobis envelope, and physical bounds.
Governance: AGENTS.md (Pasal 1, 2, 5, 12, 13).
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np

try:
    from .ilr_engine import check_composition_envelope
except ImportError:
    from core.ilr_engine import check_composition_envelope

# Verified Plant Limits (BOOK-4, BOOK-5, AGENTS.md)
ANTISURGE_FLOW_FLOOR_T_H: float = 480.0
SUCTION_TAL_DEG_C: float = -45.0
SUCTION_TALL_DEG_C: float = -51.0
MCHE_WARM_DP_ALARM_KG_CM2: float = 0.42
MCHE_WARM_DP_TRIP_KG_CM2: float = 0.54
MCHE_COLD_DP_MAX_KG_CM2: float = 0.17
C3_SUCTION_MIN_KG_CM2A: float = 1.033

# Verified Training Data Envelopes
FEED_FLOW_MIN_T_H: float = 130.0
FEED_FLOW_MAX_T_H: float = 340.0
MCR_FLOW_MIN_T_H: float = 400.0
MCR_FLOW_MAX_T_H: float = 750.0


def validate_operating_point(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Audit user scenario against safety interlocks, training domain, and composition rules."""
    violations: List[str] = []
    warnings: List[str] = []

    feed_flow = float(scenario.get("feed_flow_t_h", 250.0))
    mcr_flow = float(scenario.get("mcr_flow_t_h", 560.0))

    # 1. Compressor Anti-Surge Verification (MCR mass flow = H4FI011B x 36.8 >= 480.0 t/h;
    #    model key "H4FI001" is a legacy column name, not DCS tag H4FI001A = 4K-1 propane suction)
    if mcr_flow < ANTISURGE_FLOW_FLOOR_T_H:
        violations.append(
            f"Laju alir MCR ({mcr_flow:.1f} t/h) berada di bawah batas minimum anti-surge ({ANTISURGE_FLOW_FLOOR_T_H:.1f} t/h). "
            f"Katup kickback 4UV-53 wajib membuka untuk melindungi kompresor 4K-2/3."
        )

    # 2. Suction Drum Temperature Alarm Low (H4TI004B >= -45.0 °C)
    t_suct = float(scenario.get("H4TI004B", scenario.get("t_suct_4c8_c", -40.5)))
    if t_suct <= SUCTION_TALL_DEG_C:
        violations.append(
            f"Suhu suction drum ({t_suct:.1f} °C) melanggar batas trip darurat TALL ({SUCTION_TALL_DEG_C:.1f} °C). "
            f"Risiko tinggi kondensasi cairan dan kerusakan sudu impeller kompresor!"
        )
    elif t_suct <= SUCTION_TAL_DEG_C:
        violations.append(
            f"Suhu suction drum ({t_suct:.1f} °C) melanggar batas alarm TAL ({SUCTION_TAL_DEG_C:.1f} °C). "
            f"Katup reheat 4TV-510 wajib membuka proporsional."
        )

    # 3. MCHE Bundle Differential Pressures
    dp_w = float(scenario.get("dp_mche_warm_kgcm2", 0.213))
    dp_c = float(scenario.get("dp_mche_cold_kgcm2", 0.079))
    if dp_w >= MCHE_WARM_DP_TRIP_KG_CM2:
        violations.append(
            f"Beda tekan warm bundle MCHE ({dp_w:.3f} kg/cm2) melanggar batas trip ({MCHE_WARM_DP_TRIP_KG_CM2:.2f} kg/cm2)."
        )
    elif dp_w >= MCHE_WARM_DP_ALARM_KG_CM2:
        warnings.append(
            f"Beda tekan warm bundle MCHE ({dp_w:.3f} kg/cm2) mendekati batas alarm ({MCHE_WARM_DP_ALARM_KG_CM2:.2f} kg/cm2)."
        )

    if dp_c > MCHE_COLD_DP_MAX_KG_CM2:
        warnings.append(
            f"Beda tekan cold bundle MCHE ({dp_c:.3f} kg/cm2) melebihi batas tipikal ({MCHE_COLD_DP_MAX_KG_CM2:.2f} kg/cm2)."
        )

    # 4. Propane Suction Vacuum Check
    p_c3_suct = float(scenario.get("p_c3_suct_kgcm2a", 1.045))
    if p_c3_suct < C3_SUCTION_MIN_KG_CM2A:
        violations.append(
            f"Tekanan suction propana 4K-1 ({p_c3_suct:.3f} kg/cm2A) berada di bawah tekanan atmosferik "
            f"(risiko kebocoran udara masuk ke sistem pendingin)."
        )

    # 5. Composition Sum & Mahalanobis Envelope
    raw_n2 = float(scenario.get("comp_N2_molpct", 3.38))
    raw_c1 = float(scenario.get("comp_C1_molpct", 44.37))
    raw_c2 = float(scenario.get("comp_C2_molpct", 44.94))
    raw_c2h4 = float(scenario.get("comp_C2H4_molpct", 0.85))
    raw_c3 = float(scenario.get("comp_C3_molpct", 6.28))

    raw_comp = np.array([raw_n2, raw_c1, raw_c2, raw_c2h4, raw_c3], dtype=float)
    comp_sum = float(np.sum(raw_comp))

    if any(k < 0.0 for k in raw_comp):
        violations.append("Fraksi mol komponen refrigeran dilarang bernilai negatif.")

    if comp_sum > 1.5:  # mol% basis
        closure_error = abs(comp_sum - 100.0)
        if closure_error > 0.5:
            warnings.append(f"Total fraksi mol MCR berjumlah {comp_sum:.2f} mol% (diharapkan mendekati 100.0 mol%). Normalisasi otomatis diterapkan.")
        norm_frac = raw_comp / max(comp_sum, 1e-6)
    else:  # fraction basis
        closure_error = abs(comp_sum - 1.0)
        norm_frac = raw_comp / max(comp_sum, 1e-6)

    # Mahalanobis Distance Check
    env_res = check_composition_envelope(norm_frac)
    dm = float(env_res["mahalanobis_distance"])
    crit = float(env_res["critical_threshold"])
    in_envelope = bool(env_res["in_envelope"])

    if not in_envelope:
        warnings.append(
            f"Jarak Mahalanobis komposisi MCR (D_M = {dm:.3f}) melampaui elipsoid historis kilang (batas {crit:.3f}). "
            f"Model ML berada pada rezim ekstrapolasi statistik. Konsultasikan dengan Process Engineer."
        )

    # 6. Feed Flow Training Domain Check
    in_feed_domain = True
    if feed_flow < FEED_FLOW_MIN_T_H or feed_flow > FEED_FLOW_MAX_T_H:
        in_feed_domain = False
        warnings.append(
            f"Laju umpan gas ({feed_flow:.1f} t/h) berada di luar rentang dataset pelatihan [{FEED_FLOW_MIN_T_H:.0f}, {FEED_FLOW_MAX_T_H:.0f}] t/h."
        )

    all_safe = len(violations) == 0
    in_domain = in_envelope and in_feed_domain

    return {
        "all_safe": all_safe,
        "in_domain": in_domain,
        "violations": violations,
        "warnings": warnings,
        "mahalanobis_distance": dm,
        "mahalanobis_limit": crit,
        "composition_sum": round(comp_sum, 3),
        "xi_coordinates": env_res["xi_coordinates"],
    }

