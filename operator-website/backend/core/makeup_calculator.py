"""Hydrocarbon and nitrogen make-up injection advisory engine for MCR loop.

Calculates recommended injection flow rates (Nm3/h, kg/h, t/h, scfd) for individual
make-up controllers (H4FIC006, H4FIC005, H4FI00C8, H4FIC007) to transition
from current GC composition to target composition.

Physical basis:
- Coupled closed-loop molar conservation accounting for loop expansion and dilution.
- Stream purity matrix Y modeling plant process headers (fuel gas, column distillates).
- Unified nominal loop inventory basis: 24,000.0 kg.
- Strict NOT EVALUATED boundary contracts returning null for missing or invalid inputs.
- Read-only decision-support advisory: zero direct valve commanding capability.

References:
- CANONICAL_TAG_DICTIONARY.csv (Tags: H4FIC006, H4FIC005, H4FI00C8, H4FIC007, H4FIC009)
- Operating Manual BOOK-5 (Plant-4/5 MCR Refrigeration System), pp. 80-128
- Normal conditions (0 deg C, 1.01325 bar): V_m = 22.414 Nm3/kmol
- Standard conditions (60 deg F, 14.696 psia): 1 Nm3 = 37.3263 scf
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Component molecular weights in g/mol or kg/kmol (CRC / NIST Chemistry WebBook)
MW_COMPONENTS: Dict[str, float] = {
    "N2": 28.0134,
    "C1": 16.0425,
    "C2": 30.0690,
    "C2H4": 28.0532,
    "C3": 44.0956,
}

# Canonical Plant-5 Train H DCS tags for MR make-up injection controllers
TAG_MAKEUP_CONTROLLERS: Dict[str, Dict[str, Any]] = {
    "N2": {
        "tag": "H4FIC006",
        "alt_tag": None,
        "desc": "Nitrogen (N2)",
        "header": "Utility N2 Header",
        "unit": "Nm3/h",
    },
    "C1": {
        "tag": "H4FIC005",
        "alt_tag": "H4FIC009",
        "desc": "Methane (C1)",
        "header": "Fuel Gas / Treated Feed Gas Header",
        "unit": "Nm3/h",
    },
    "C2": {
        "tag": "H4FI00C8",
        "alt_tag": None,
        "desc": "Ethane (C2)",
        "header": "De-Ethanizer 3C-4 Distillate",
        "unit": "Nm3/h",
    },
    "C3": {
        "tag": "H4FIC007",
        "alt_tag": None,
        "desc": "Propane (C3)",
        "header": "De-Propanizer 3C-6 Distillate",
        "unit": "Nm3/h",
    },
}

# Standard normal molar volume [Nm3/kmol] at 0 deg C, 1.01325 bar
NORMAL_MOLAR_VOLUME_NM3_PER_KMOL: float = 22.414

# Conversion factor: 1 Nm3 (0 deg C, 1 atm) to scf (60 deg F, 1 atm)
SCF_PER_NM3: float = 37.3263
SCFD_PER_NM3_H: float = 24.0 * SCF_PER_NM3  # ~895.83 scfd per (Nm3/h)

# Verified nominal active MCR loop inventory [kg] (MCHE shell + tubes + drum 4C-8 + accumulator)
ESTIMATED_MCR_LOOP_INVENTORY_KG: float = 24000.0

# Typical plant stream purities in Plant-5 Train H (mole fraction matrix)
# Columns represent make-up headers: [N2, C1, C2, C3, C2H4]
DEFAULT_STREAM_PURITY_MATRIX: Dict[str, Dict[str, float]] = {
    # N2 Header: high-purity utility nitrogen (>= 99.9% N2)
    "N2": {"N2": 1.000, "C1": 0.000, "C2": 0.000, "C2H4": 0.000, "C3": 0.000},
    # C1 Header: treated fuel gas (95.51% C1, 2.75% C2, 1.69% C3, 0.05% N2)
    "C1": {"N2": 0.0005, "C1": 0.9551, "C2": 0.0275, "C2H4": 0.000, "C3": 0.0169},
    # C2 Header: De-ethanizer 3C-4 overhead (96.5% C2, 2.0% C1, 1.5% C3)
    "C2": {"N2": 0.000, "C1": 0.0200, "C2": 0.9650, "C2H4": 0.000, "C3": 0.0150},
    # C3 Header: De-propanizer 3C-6 overhead (98.0% C3, 1.5% C2, 0.5% C1)
    "C3": {"N2": 0.000, "C1": 0.0050, "C2": 0.0150, "C2H4": 0.000, "C3": 0.9800},
    # C2H4 Cylinder/Sphere: pure refrigerant (> 99.5% C2H4, balance C2)
    "C2H4": {"N2": 0.000, "C1": 0.000, "C2": 0.0050, "C2H4": 0.9950, "C3": 0.000},
}


def validate_makeup_inputs(
    actual_molpct: Optional[Dict[str, float]],
    target_molpct: Optional[Dict[str, float]],
    transition_hours: Optional[float],
    inventory_kg: Optional[float],
) -> Tuple[bool, str]:
    """Validate all physical inputs for make-up inventory calculation.

    Returns (is_valid, reason). Enforces strict boundary validation.
    """
    if actual_molpct is None or not isinstance(actual_molpct, dict) or len(actual_molpct) == 0:
        return False, "Actual GC composition data (actual_molpct) is missing or empty"

    if target_molpct is None or not isinstance(target_molpct, dict) or len(target_molpct) == 0:
        return False, "Target scenario composition data (target_molpct) is missing or empty"

    # Check inventory_kg: must be numeric, finite, positive
    if (
        inventory_kg is None
        or not isinstance(inventory_kg, (int, float))
        or isinstance(inventory_kg, bool)
        or math.isnan(inventory_kg)
        or math.isinf(inventory_kg)
        or inventory_kg <= 0.0
    ):
        return False, "MCR loop inventory estimate (inventory_kg) is invalid, non-finite, or non-positive"

    # Check transition_hours: must be numeric, finite, positive
    if (
        transition_hours is None
        or not isinstance(transition_hours, (int, float))
        or isinstance(transition_hours, bool)
        or math.isnan(transition_hours)
        or math.isinf(transition_hours)
        or transition_hours <= 0.0
    ):
        return False, "Transition duration (transition_hours) is invalid, non-finite, or non-positive"

    # Check that required core components are explicitly present
    core_comps = ["N2", "C1", "C2", "C3"]
    for comp in core_comps:
        if comp not in actual_molpct:
            return False, f"Required core component {comp} missing from actual GC composition"
        if comp not in target_molpct:
            return False, f"Required core component {comp} missing from target composition"

    # Validate all present components (core + C2H4 or others)
    all_keys = set(actual_molpct.keys()).union(target_molpct.keys())
    for comp in all_keys:
        if comp in actual_molpct:
            val = actual_molpct[comp]
            if isinstance(val, bool):
                return False, f"Component {comp} in actual composition is boolean, not numeric"
            try:
                f_val = float(val)
            except (ValueError, TypeError):
                return False, f"Component {comp} in actual composition is non-numeric"
            if math.isnan(f_val) or math.isinf(f_val):
                return False, f"Component {comp} in actual composition is NaN or Inf"
            if f_val < -1e-6:
                return False, f"Component {comp} has an unphysical negative mole fraction in actual composition"

        if comp in target_molpct:
            val = target_molpct[comp]
            if isinstance(val, bool):
                return False, f"Component {comp} in target composition is boolean, not numeric"
            try:
                f_val = float(val)
            except (ValueError, TypeError):
                return False, f"Component {comp} in target composition is non-numeric"
            if math.isnan(f_val) or math.isinf(f_val):
                return False, f"Component {comp} in target composition is NaN or Inf"
            if f_val < -1e-6:
                return False, f"Component {comp} has an unphysical negative mole fraction in target composition"

    tot_act = sum(float(actual_molpct[k]) for k in core_comps)
    if "C2H4" in actual_molpct:
        tot_act += float(actual_molpct["C2H4"])

    tot_tgt = sum(float(target_molpct[k]) for k in core_comps)
    if "C2H4" in target_molpct:
        tot_tgt += float(target_molpct["C2H4"])

    if math.isnan(tot_act) or math.isinf(tot_act) or tot_act <= 10.0 or tot_act > 150.0:
        return False, f"Actual total mole percent ({tot_act:.2f}%) is outside physical range (10-150%)"

    if math.isnan(tot_tgt) or math.isinf(tot_tgt) or tot_tgt <= 10.0 or tot_tgt > 150.0:
        return False, f"Target total mole percent ({tot_tgt:.2f}%) is outside physical range (10-150%)"

    return True, "Valid"


def _build_unevaluated_response(
    reason: str,
    transition_hours: Optional[float] = None,
    inventory_kg: Optional[float] = None,
    c1_tag: str = "H4FIC005",
) -> Dict[str, Any]:
    """Construct an explicit NOT EVALUATED response with null flow fields."""
    items: List[Dict[str, Any]] = []
    comp_list = ["N2", "C1", "C2", "C3"]

    for comp in comp_list:
        meta = TAG_MAKEUP_CONTROLLERS[comp]
        tag = c1_tag if comp == "C1" else meta["tag"]
        items.append({
            "component": comp,
            "tag_dcs": tag,
            "alternate_tag_dcs": meta.get("alt_tag"),
            "description": meta["desc"],
            "unit": "Nm3/h",
            "actual_molpct": None,
            "target_molpct": None,
            "delta_molpct": None,
            "needed_kmol": None,
            "needed_kg": None,
            "recommended_flow_nm3_h": None,
            "recommended_flow_kg_h": None,
            "recommended_flow_t_h": None,
            "recommended_flow_scfd": None,
            "action": "TIDAK DAPAT DIEVALUASI",
            "instruction": f"[ADVISORY] Make-up calculation cannot be evaluated: {reason}.",
        })

    return {
        "status": "NOT EVALUATED",
        "transition_hours": transition_hours if (transition_hours is not None and transition_hours > 0) else None,
        "estimated_inventory_kg": inventory_kg if (inventory_kg is not None and inventory_kg > 0) else None,
        "initial_moles_kmol": None,
        "final_moles_kmol": None,
        "expansion_ratio": None,
        "total_makeup_flow_nm3_h": None,
        "total_makeup_flow_kg_h": None,
        "total_makeup_flow_t_h": None,
        "total_makeup_flow_scfd": None,
        "items": items,
        "recommendations": items,
        "explanation": f"Make-up advisory status is NOT EVALUATED: {reason}.",
        "operational_notes": [
            f"STATUS: NOT EVALUATED: {reason}.",
            "Safety notice: Do not initiate make-up injection without complete laboratory GC verification.",
        ],
        "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def calculate_makeup_recommendations(
    actual_molpct: Optional[Dict[str, float]],
    target_molpct: Optional[Dict[str, float]],
    transition_hours: float = 2.0,
    inventory_kg: float = ESTIMATED_MCR_LOOP_INVENTORY_KG,
    use_stream_purity: bool = True,
    purity_matrix: Optional[Dict[str, Dict[str, float]]] = None,
    c1_tag: str = "H4FIC005",
) -> Dict[str, Any]:
    """Calculate component-resolved closed-loop make-up advisory schedule.

    Parameters:
    - actual_molpct: Current GC composition {'N2': 3.38, 'C1': 44.37, ...}
    - target_molpct: Target/scenario composition
    - transition_hours: Target transition duration (hours, min 0.5 h)
    - inventory_kg: Verified active loop inventory in kg (default 24,000 kg)
    - use_stream_purity: Whether to account for non-pure plant make-up headers
    - purity_matrix: Optional override for header purity matrix
    - c1_tag: Preferred DCS tag for C1 make-up ('H4FIC005' or 'H4FIC009')

    Returns:
    Dictionary structured with status ('EVALUATED' | 'NOT EVALUATED'),
    per-component recommendations, total rates, and operational safety notes.
    """
    # 1. Boundary & Input Validation Contract
    is_valid, reason = validate_makeup_inputs(actual_molpct, target_molpct, transition_hours, inventory_kg)
    if not is_valid:
        return _build_unevaluated_response(
            reason=reason,
            transition_hours=transition_hours,
            inventory_kg=inventory_kg,
            c1_tag=c1_tag,
        )

    assert actual_molpct is not None
    assert target_molpct is not None

    t_hours = max(0.5, float(transition_hours))
    inv_kg = float(inventory_kg)

    # 2. Composition Normalization over 5 MCR components
    components = ["N2", "C1", "C2", "C2H4", "C3"]
    act_sum = sum(max(0.0, float(actual_molpct.get(k, 0.0))) for k in components)
    tgt_sum = sum(max(0.0, float(target_molpct.get(k, 0.0))) for k in components)

    if act_sum <= 1e-6 or tgt_sum <= 1e-6:
        return _build_unevaluated_response(
            reason="Actual or target composition sum is zero or near-zero",
            transition_hours=t_hours,
            inventory_kg=inv_kg,
            c1_tag=c1_tag,
        )

    x0 = np.array([max(0.0, float(actual_molpct.get(k, 0.0))) / act_sum for k in components], dtype=float)
    x_tgt = np.array([max(0.0, float(target_molpct.get(k, 0.0))) / tgt_sum for k in components], dtype=float)

    # 3. Initial Inventory Moles & Average Molecular Weight
    mw_vec = np.array([MW_COMPONENTS[k] for k in components], dtype=float)
    avg_mw_act = float(np.dot(x0, mw_vec))
    n0 = inv_kg / max(avg_mw_act, 10.0)  # kmol initial total moles

    # 4. Closed-Loop Dilution Balance & Header Purity Matrix Y
    # Header streams: [N2, C1, C2, C3, C2H4]
    active_purity = purity_matrix if purity_matrix is not None else DEFAULT_STREAM_PURITY_MATRIX

    if use_stream_purity:
        # Build 5x5 matrix Y where column j is the composition of make-up stream j
        Y = np.zeros((len(components), len(components)), dtype=float)
        for j, c_stream in enumerate(components):
            stream_dict = active_purity.get(c_stream, {})
            for i, c_comp in enumerate(components):
                Y[i, j] = stream_dict.get(c_comp, 1.0 if i == j else 0.0)

        # Ensure column sums equal 1.0
        col_sums = Y.sum(axis=0)
        col_sums[col_sums == 0.0] = 1.0
        Y = Y / col_sums[np.newaxis, :]

        try:
            Y_inv = np.linalg.inv(Y)
        except np.linalg.LinAlgError:
            Y = np.eye(len(components))
            Y_inv = np.eye(len(components))
    else:
        Y = np.eye(len(components))
        Y_inv = np.eye(len(components))

    # Check if target composition has any component with positive delta > 0.02 mol%
    # If not, the recipe is either identical, within noise deadband, or all components are in excess / balanced
    has_deficit = any(float(target_molpct.get(k, 0.0)) - float(actual_molpct.get(k, 0.0)) > 0.02 for k in components)

    if not has_deficit:
        expansion_ratio = 1.0
        n_final = n0
        u_kmol = np.zeros(len(components), dtype=float)
        needed_kmol_vec = np.zeros(len(components), dtype=float)
    else:
        # Transform target and initial composition vectors through Y_inv:
        # u = n_final * (Y_inv @ x_tgt) - n_0 * (Y_inv @ x0)
        v_vec = Y_inv @ x_tgt
        w_vec = Y_inv @ x0

        # To guarantee u >= 0 (no negative injection) across all available headers:
        # n_final / n0 >= w_i / v_i for all i where v_i > 1e-6
        expansion_ratios = [1.0]
        for i in range(len(components)):
            if v_vec[i] > 1e-5:
                ratio = float(w_vec[i] / v_vec[i])
                expansion_ratios.append(ratio)

        expansion_ratio = max(expansion_ratios)
        n_final = n0 * expansion_ratio

        # Required stream moles u [kmol]
        u_kmol = np.maximum(0.0, n_final * v_vec - n0 * w_vec)

        # Convert stream moles to component moles injected: m = Y @ u
        needed_kmol_vec = Y @ u_kmol

    # 5. Build Advisory Items for Core Controllers (N2, C1, C2, C3)
    items: List[Dict[str, Any]] = []
    total_flow_nm3_h = 0.0
    total_flow_kg_h = 0.0
    total_flow_t_h = 0.0
    total_flow_scfd = 0.0
    notes: List[str] = []

    for idx, comp in enumerate(["N2", "C1", "C2", "C3"]):
        c_idx = components.index(comp)
        act_pct = float(actual_molpct.get(comp, 0.0))
        tgt_pct = float(target_molpct.get(comp, 0.0))
        delta_pct = tgt_pct - act_pct

        meta = TAG_MAKEUP_CONTROLLERS[comp]
        tag = c1_tag if comp == "C1" else meta["tag"]

        # Stream moles associated with this controller header
        stream_kmol = float(u_kmol[c_idx])
        # Average molecular weight of make-up stream passing through meter
        stream_mw = float(np.dot(Y[:, c_idx], mw_vec))
        # Net component moles added across all streams
        kmol_add = float(needed_kmol_vec[c_idx])

        # A stream controller must inject if stream_kmol > 1e-4 kmol
        if stream_kmol > 1e-4:
            needed_kg = stream_kmol * stream_mw
            needed_nm3 = stream_kmol * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL

            flow_nm3_h = needed_nm3 / t_hours
            flow_kg_h = needed_kg / t_hours
            flow_t_h = flow_kg_h / 1000.0
            flow_scfd = flow_nm3_h * SCFD_PER_NM3_H

            action = "INJEKSI"
            instruction = (
                f"[ADVISORY] Set valve {tag} ({meta['desc']}) to "
                f"{flow_nm3_h:.1f} Nm3/h ({flow_kg_h:.1f} kg/h / {flow_scfd:,.0f} scfd)."
            )
        elif expansion_ratio > 1.0001:
            # Limiting component in excess: held while other injections dilute it
            flow_nm3_h = 0.0
            flow_kg_h = 0.0
            flow_t_h = 0.0
            flow_scfd = 0.0
            needed_kg = 0.0
            kmol_add = 0.0
            action = "TAHAN / STOP"
            instruction = (
                f"[ADVISORY] Keep valve {tag} closed (component is in excess; "
                f"will dilute as deficit components are injected)."
            )
        else:
            flow_nm3_h = 0.0
            flow_kg_h = 0.0
            flow_t_h = 0.0
            flow_scfd = 0.0
            needed_kg = 0.0
            kmol_add = 0.0
            action = "STABIL / SEIMBANG"
            instruction = f"[ADVISORY] Valve {tag} on standby (component is within target tolerance)."

        total_flow_nm3_h += flow_nm3_h
        total_flow_kg_h += flow_kg_h
        total_flow_t_h += flow_t_h
        total_flow_scfd += flow_scfd

        item_dict = {
            "component": comp,
            "tag_dcs": tag,
            "alternate_tag_dcs": meta.get("alt_tag"),
            "description": meta["desc"],
            "unit": "Nm3/h",
            "actual_molpct": round(act_pct, 2),
            "target_molpct": round(tgt_pct, 2),
            "delta_molpct": round(delta_pct, 2),
            "needed_kmol": round(kmol_add, 4),
            "needed_kg": round(needed_kg, 2),
            "recommended_flow_nm3_h": round(flow_nm3_h, 1),
            "recommended_flow_kg_h": round(flow_kg_h, 1),
            "recommended_flow_t_h": round(flow_t_h, 4),
            "recommended_flow_scfd": round(flow_scfd, 0),
            "stream_mw": round(stream_mw, 4),
            "action": action,
            "instruction": instruction,
        }
        items.append(item_dict)

    # 6. Operational Notes and Engineering Context
    c2h4_idx = components.index("C2H4")
    act_c2h4 = float(actual_molpct.get("C2H4", 0.0))
    tgt_c2h4 = float(target_molpct.get("C2H4", 0.0))
    if abs(tgt_c2h4 - act_c2h4) > 0.05:
        notes.append(
            f"Ethylene (C2H4) notice: Delta {(tgt_c2h4 - act_c2h4):+.2f} mol%. "
            f"Ethylene make-up is administered manually via refrigerant cylinders when required."
        )

    expansion_pct = (expansion_ratio - 1.0) * 100.0
    if expansion_pct > 25.0:
        notes.append(
            f"Loop inventory notice: Total mole expansion of {expansion_pct:.1f}% required "
            f"to reach target recipe without venting. Consider partial loop purge if suction drum pressure approaches high limit."
        )

    notes.append(
        f"Injection rates calculated via closed-loop dilution balance for an estimated MCR "
        f"loop inventory of {inv_kg:,.0f} kg over a {t_hours:.1f}-hour transition window."
    )
    if use_stream_purity:
        notes.append(
            "Calculation incorporates header purity matrix: treated fuel gas for C1, "
            "de-ethanizer distillate for C2, de-propanizer distillate for C3."
        )

    notes.append(
        "SAFETY ADVISORY: Recommendations are decision-support guidelines for plant operators. "
        "This software has no write access to DCS, SIS, or field controllers."
    )

    explanation = (
        f"Closed-loop make-up evaluated for a {t_hours:.1f}-hour transition "
        f"with {expansion_pct:.1f}% mole expansion. Total make-up rate: {total_flow_nm3_h:.1f} Nm3/h "
        f"({total_flow_kg_h:.1f} kg/h / {total_flow_scfd:,.0f} scfd)."
    )

    return {
        "status": "EVALUATED",
        "transition_hours": round(t_hours, 2),
        "estimated_inventory_kg": round(inv_kg, 1),
        "initial_moles_kmol": round(n0, 2),
        "final_moles_kmol": round(n_final, 2),
        "expansion_ratio": round(expansion_ratio, 4),
        "total_makeup_flow_nm3_h": round(total_flow_nm3_h, 1),
        "total_makeup_flow_kg_h": round(total_flow_kg_h, 1),
        "total_makeup_flow_t_h": round(total_flow_t_h, 4),
        "total_makeup_flow_scfd": round(total_flow_scfd, 0),
        "items": items,
        "recommendations": items,
        "explanation": explanation,
        "operational_notes": notes,
        "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
    }

