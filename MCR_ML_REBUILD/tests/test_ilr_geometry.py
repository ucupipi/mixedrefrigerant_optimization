"""Unit tests for 5-Component Isometric Log-Ratio (ILR) Simplex Geometry."""
from __future__ import annotations

import numpy as np
import pytest

from src.features.ilr import (
    CHI2_CRITICAL_5COMP,
    check_mahalanobis_envelope,
    closure,
    fit_ilr_envelope,
    ilr_forward,
    ilr_inverse,
    replace_zeros,
)


def test_ilr_forward_and_inverse_roundtrip():
    x = np.array([
        [0.02168, 0.44411, 0.46880, 0.00010, 0.06531],
        [0.03000, 0.45000, 0.44000, 0.01000, 0.07000],
    ])
    xi = ilr_forward(x)
    assert xi.shape == (2, 4)
    x_rec = ilr_inverse(xi)
    assert x_rec.shape == (2, 5)
    np.testing.assert_allclose(x, x_rec, atol=1e-6)
    np.testing.assert_allclose(x_rec.sum(axis=1), np.ones(2), atol=1e-12)


def test_zero_component_replacement_safety():
    x_zero = np.array([0.02, 0.45, 0.45, 0.0, 0.08])
    x_safe = replace_zeros(x_zero, delta=1e-5)
    assert np.all(x_safe > 0.0)
    assert abs(x_safe.sum() - 1.0) < 1e-12
    xi = ilr_forward(x_zero)
    assert np.all(np.isfinite(xi))


def test_negative_mole_fraction_rejected():
    with pytest.raises(ValueError, match="Negative mole fraction"):
        closure(np.array([0.1, -0.2, 0.5, 0.3, 0.3]))


def test_mahalanobis_envelope_screening():
    rng = np.random.default_rng(42)
    xi_train = rng.normal(0.0, 0.5, size=(100, 4))
    env = fit_ilr_envelope(xi_train)
    inside, dm_in = check_mahalanobis_envelope(np.zeros(4), env["mean_xi"], env["cov_inv"])
    outside, dm_out = check_mahalanobis_envelope(np.full(4, 5.0), env["mean_xi"], env["cov_inv"])
    assert inside is True
    assert dm_in < CHI2_CRITICAL_5COMP
    assert outside is False
    assert dm_out > CHI2_CRITICAL_5COMP

