"""Unit tests for the Pure-Python Peng-Robinson Thermodynamic Engine."""
from __future__ import annotations

import numpy as np
import pytest

from src.thermo.pr_thermo import (
    _equilibrate,
    _h,
    _roots,
    compute_compressor_gouy_stodola_exergy_mw,
    compute_mche_riemann_exergy_mw,
    mche_pinch_check,
    pr_compressibility,
    pr_density,
    pr_dew_bubble_temperatures,
)


def test_pr_compressibility_and_density():
    x_nom = np.array([0.02168, 0.44411, 0.46880, 0.00010, 0.06531])
    zv, zl = pr_compressibility(4.1, 380.0, x_nom)
    assert 0.70 <= zv <= 1.05
    assert zl < zv
    rho_liq = pr_density(45.0, 110.0, x_nom, phase="liquid")
    assert rho_liq > 400.0


def test_vle_dew_bubble_and_vapor_fraction():
    x_nom = np.array([0.02168, 0.44411, 0.46880, 0.00010, 0.06531])
    _, _, beta = _equilibrate(4.1, 379.78, x_nom)
    assert beta == 1.0
    t_dew, t_bub = pr_dew_bubble_temperatures(4.1, x_nom)
    assert t_bub <= t_dew


def test_enthalpy_monotonicity_and_non_physical_rejection():
    x_nom = np.array([0.02168, 0.44411, 0.46880, 0.00010, 0.06531])
    assert _h(380.0, 4.1, x_nom, "vapor") > _h(350.0, 4.1, x_nom, "vapor")
    with pytest.raises(ValueError):
        _roots(-1.0, 300.0, x_nom)


def test_mche_pinch_and_riemann_exergy():
    q = np.linspace(0.0, 1.0, 20)
    t_hot_c = np.linspace(-158.0, 25.0, 20)
    t_cold_c = t_hot_c - 2.5
    res = mche_pinch_check(np.column_stack([t_hot_c, q]), np.column_stack([t_cold_c, q]))
    assert abs(res["pinch_delta_T_C"] - 2.5) < 1e-6

    ex_mche = compute_mche_riemann_exergy_mw(t_hot_c + 273.15, t_cold_c + 273.15, total_duty_mw=120.0)
    assert ex_mche > 0.0
    ex_comp = compute_compressor_gouy_stodola_exergy_mw(100.0, 0.78)
    assert abs(ex_comp - 22.0) < 1e-6


def test_hysys_stream_deck_and_parity_report(tmp_path):
    from src.thermo.hysys_parity import generate_hysys_parity_report, kgcm2g_to_bara

    assert abs(kgcm2g_to_bara(3.15) - (3.15 * 0.980665 + 1.01325)) < 1e-5
    rep = generate_hysys_parity_report(reports_dir=tmp_path / "reports", docs_dir=tmp_path / "docs")
    assert rep["parity_passed"] is True
    assert len(rep["stream_deck"]) == 18
    for s in rep["stream_deck"]:
        assert abs(s["comp_sum_mol_pct"] - 100.0) < 1e-3
    assert (tmp_path / "reports" / "hysys_stream_input_deck.csv").exists()
    assert (tmp_path / "reports" / "hysys_parity_report.json").exists()
    assert (tmp_path / "docs" / "hysys_parity_table.md").exists()


