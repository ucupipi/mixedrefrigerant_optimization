"""Verification tests for Phase 3 interconnected C3MR optimization, closed-loop make-up, and 5C-1 VLE modules in MCR_ML_REBUILD."""
from __future__ import annotations

import math
import pytest

from src.cli import main as cli_main
from src.core.makeup_calculator import calculate_makeup_recommendations
from src.core.optimizer_engine import OptimizationStrategy, recommend
from src.thermo.flash_drum_vle import calculate_flash_drum_5c1


def test_multi_strategy_optimizer_interconnected() -> None:
    """Verify CONDITION_DEPENDENT, FIXED_RECIPE, and MINIMUM_INTERVENTION in MCR_ML_REBUILD."""
    actual = {"N2": 3.39, "C1": 44.45, "C2": 45.02, "C2H4": 0.85, "C3": 6.29}

    res_cond = recommend(
        feed_t_h=245.8,
        actual_comp=actual,
        strategy=OptimizationStrategy.CONDITION_DEPENDENT,
    )
    res_fixed = recommend(
        feed_t_h=245.8,
        actual_comp=actual,
        strategy=OptimizationStrategy.FIXED_RECIPE,
    )
    res_min = recommend(
        feed_t_h=245.8,
        actual_comp=actual,
        alpha_trim=0.30,
        strategy=OptimizationStrategy.MINIMUM_INTERVENTION,
    )

    assert res_cond["strategy"] == "CONDITION_DEPENDENT"
    assert res_fixed["strategy"] == "FIXED_RECIPE"
    assert res_min["strategy"] == "MINIMUM_INTERVENTION"

    for res in (res_cond, res_fixed, res_min):
        comp_sum = (
            res["comp_N2_molpct"]
            + res["comp_C1_molpct"]
            + res["comp_C2_molpct"]
            + res["comp_C2H4_molpct"]
            + res["comp_C3_molpct"]
        )
        assert abs(comp_sum - 100.0) < 0.05
        assert res["mcr_flow_t_h"] >= 480.0
        assert res["expected_suction_temp_c"] >= -45.0
        assert res["mahalanobis_distance"] <= 3.0802
        assert "constraint_residuals" in res
        assert "effective_inputs" in res
        assert "explanation" in res


def test_closed_loop_makeup_mass_balance_and_null_guards() -> None:
    """Verify closed-loop inventory dilution make-up balance and NOT EVALUATED guard."""
    actual = {"N2": 3.39, "C1": 44.45, "C2": 45.02, "C2H4": 0.85, "C3": 6.29}
    target = {"N2": 3.77, "C1": 42.22, "C2": 43.67, "C2H4": 1.53, "C3": 8.82}

    res = calculate_makeup_recommendations(
        actual_molpct=actual,
        target_molpct=target,
        transition_hours=8.0,
        inventory_kg=24000.0,
    )
    assert res["status"] in ("EVALUATED", "PARTIAL_PURGE_OR_BLEED_REQUIRED")
    assert res["total_makeup_flow_nm3_h"] is not None and res["total_makeup_flow_nm3_h"] > 0.0
    assert res["total_makeup_flow_kg_h"] is not None and res["total_makeup_flow_kg_h"] > 0.0
    assert res["total_makeup_flow_scfd"] is not None and res["total_makeup_flow_scfd"] > 0.0
    assert res["expansion_ratio"] is not None and res["expansion_ratio"] > 1.0

    # Verify NOT EVALUATED null guard when inventory is invalid
    res_invalid = calculate_makeup_recommendations(
        actual_molpct=actual,
        target_molpct=target,
        transition_hours=8.0,
        inventory_kg=-500.0,
    )
    assert res_invalid["status"] == "NOT EVALUATED"
    assert res_invalid["total_makeup_flow_nm3_h"] is None
    assert res_invalid["total_makeup_flow_kg_h"] is None


def test_flash_drum_5c1_vle_parity() -> None:
    """Verify PR-EOS 5C-1 Flash Drum VLE equilibrium and liquid yield at 150 t/h and 245.8 t/h."""
    vle_150 = calculate_flash_drum_5c1(feed_flow_t_h=150.0)
    assert abs(vle_150.lng_liquid_flow_t_h - 141.80) <= 0.50
    assert -158.5 <= vle_150.t_flash_c <= -157.0

    vle_245 = calculate_flash_drum_5c1(feed_flow_t_h=245.8)
    assert vle_245.lng_liquid_flow_t_h > 225.0
    assert 0.0 < vle_245.vapor_fraction_mol < 0.15


def test_cli_optimize_and_makeup_subcommands() -> None:
    """Verify CLI subcommands optimize and makeup return exit code 0."""
    rc_opt = cli_main(["optimize", "--feed-flow", "245.8", "--strategy", "CONDITION_DEPENDENT"])
    assert rc_opt == 0

    rc_mk = cli_main(["makeup", "--inventory-kg", "24000.0", "--transition-hours", "8.0"])
    assert rc_mk == 0
