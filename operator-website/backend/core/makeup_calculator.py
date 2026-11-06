"""Hydrocarbon and Nitrogen Make-up Injection Advisory Engine for MCR Loop.

Calculates recommended injection flow rates (Nm3/h and kg/h) for individual
make-up controllers (H4FIC006, H4FIC005, H4FI00C8, H4FIC007) to transition
from current analyzed GC composition to target/optimized composition.

References:
- CANONICAL_TAG_DICTIONARY.csv (Tags: H4FIC006, H4FIC005, H4FI00C8, H4FIC007)
- Badak Operating Manual BOOK-5 (Plant-4/5 MCR Refrigeration System), pp. 80-128
- Molar volume at normal conditions (0 °C, 1.01325 bar): V_m = 22.414 Nm3/kmol
Governance: AGENTS.md (Pasal 1, 9, 12, 13).
"""
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np

# Component molecular weights in g/mol or kg/kmol
MW_COMPONENTS: Dict[str, float] = {
    "N2": 28.0134,
    "C1": 16.0425,
    "C2": 30.0690,
    "C2H4": 28.0532,
    "C3": 44.0956,
}

# Real plant DCS tags for MR make-up injection controllers (CANONICAL_TAG_DICTIONARY.csv)
TAG_MAKEUP_CONTROLLERS: Dict[str, Dict[str, str]] = {
    "N2": {"tag": "H4FIC006", "desc": "Nitrogen (N₂)", "unit": "Nm3/h"},
    "C1": {"tag": "H4FIC005", "desc": "Metana (C₁)", "unit": "Nm3/h"},
    "C2": {"tag": "H4FI00C8", "desc": "Etana (C₂)", "unit": "Nm3/h"},
    "C3": {"tag": "H4FIC007", "desc": "Propana (C₃)", "unit": "Nm3/h"},
}

# Standard normal molar volume [Nm3/kmol] at 0 °C, 1 atm
NORMAL_MOLAR_VOLUME_NM3_PER_KMOL: float = 22.414

# Estimated active MCR loop inventory [kg] (MCHE shell + tubes + drum 4C-8 + accumulator)
# Plant-3 Train H typical operating inventory is ~22,000 to 26,000 kg
ESTIMATED_MCR_LOOP_INVENTORY_KG: float = 24000.0


def calculate_makeup_recommendations(
    actual_molpct: Dict[str, float],
    target_molpct: Dict[str, float],
    transition_hours: float = 2.0,
    inventory_kg: float = ESTIMATED_MCR_LOOP_INVENTORY_KG,
) -> Dict[str, Any]:
    """Calculate recommended make-up injection rates for each component.

    Parameters:
    - actual_molpct: Current GC composition {'N2': 3.38, 'C1': 44.37, ...}
    - target_molpct: Target/scenario composition
    - transition_hours: Target duration for smooth transition (default 2.0 h)
    - inventory_kg: Estimated active loop inventory in kg
    """
    t_hours = max(0.5, float(transition_hours))

    # Calculate average molecular weight of baseline mixture
    tot_act_mol = sum(actual_molpct.get(k, 0.0) for k in MW_COMPONENTS)
    norm_actual = {k: actual_molpct.get(k, 0.0) / max(tot_act_mol, 1e-6) for k in MW_COMPONENTS}
    avg_mw = sum(norm_actual[k] * MW_COMPONENTS[k] for k in MW_COMPONENTS)

    # Total active moles in the refrigeration loop [kmol]
    total_kmol_loop = inventory_kg / max(avg_mw, 10.0)

    items: List[Dict[str, Any]] = []
    total_flow_nm3_h = 0.0
    total_flow_kg_h = 0.0
    notes: List[str] = []

    for comp in ["N2", "C1", "C2", "C3"]:
        act = float(actual_molpct.get(comp, 0.0))
        tgt = float(target_molpct.get(comp, 0.0))
        delta_pct = tgt - act
        delta_frac = delta_pct / 100.0

        meta = TAG_MAKEUP_CONTROLLERS[comp]
        tag = meta["tag"]
        mw = MW_COMPONENTS[comp]

        if delta_pct > 0.02:  # Deficient component -> Needs make-up injection
            needed_kmol = delta_frac * total_kmol_loop
            needed_nm3 = needed_kmol * NORMAL_MOLAR_VOLUME_NM3_PER_KMOL
            needed_kg = needed_kmol * mw

            flow_nm3_h = float(needed_nm3 / t_hours)
            flow_kg_h = float(needed_kg / t_hours)

            total_flow_nm3_h += flow_nm3_h
            total_flow_kg_h += flow_kg_h

            action = "INJEKSI"
            instruction = (
                f"Buka katup {tag} ke "
                f"{flow_nm3_h:.1f} Nm3/h ({flow_kg_h:.1f} kg/h)."
            )
        elif delta_pct < -0.05:  # Excess component -> Hold injection, natural decay or purge
            flow_nm3_h = 0.0
            flow_kg_h = 0.0
            action = "TAHAN / STOP"
            instruction = (
                f"Tutup katup {tag} (kadar sudah berlebih +{abs(delta_pct):.2f}%)."
            )
        else:  # Balanced
            flow_nm3_h = 0.0
            flow_kg_h = 0.0
            action = "STABIL / SEIMBANG"
            instruction = f"Katup {tag} standby (kadar sudah sesuai)."

        items.append({
            "component": comp,
            "tag_dcs": tag,
            "description": meta["desc"],
            "unit": "Nm3/h",
            "actual_molpct": round(act, 2),
            "target_molpct": round(tgt, 2),
            "delta_molpct": round(delta_pct, 2),
            "recommended_flow_nm3_h": round(flow_nm3_h, 1),
            "recommended_flow_kg_h": round(flow_kg_h, 1),
            "action": action,
            "instruction": instruction,
        })

    # Ethylene (C2H4) note if present
    act_c2h4 = float(actual_molpct.get("C2H4", 0.0))
    tgt_c2h4 = float(target_molpct.get("C2H4", 0.0))
    if abs(tgt_c2h4 - act_c2h4) > 0.05:
        notes.append(
            f"Perhatian C2H4 (Etilena): Selisih {(tgt_c2h4 - act_c2h4):+.2f} mol%. "
            f"Injeksi C2H4 dilakukan manual via silinder jika diperlukan."
        )

    notes.append(
        f"Laju injeksi dihitung berdasarkan estimasi inventory loop MCR sebesar {inventory_kg:,.0f} kg "
        f"dengan durasi transisi {t_hours:.1f} jam untuk mencegah lonjakan termal pada MCHE."
    )

    return {
        "transition_hours": t_hours,
        "estimated_inventory_kg": inventory_kg,
        "total_makeup_flow_nm3_h": round(total_flow_nm3_h, 1),
        "total_makeup_flow_kg_h": round(total_flow_kg_h, 1),
        "items": items,
        "operational_notes": notes,
    }

