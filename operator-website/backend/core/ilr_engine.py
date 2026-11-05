"""Compositional Geometry Engine (ILR & Mahalanobis Distance).

Transforms 5-component Mixed Refrigerant compositions (N2, C1, C2, C2H4, C3)
from Simplex S^5 to Euclidean R^4 using Sequential Binary Partition (SBP).
Evaluates operational boundary compliance via Mahalanobis distance D_M <= 3.080216.
Governance: AGENTS.md (Pasal 5, 12).
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple, Union
import numpy as np

# SBP contrast matrix for 5 components: [N2, C1, C2, C2H4, C3]
# xi_1: N2 vs (C1, C2, C2H4, C3)
# xi_2: C1 vs (C2, C2H4, C3)
# xi_3: C2 vs (C2H4, C3)
# xi_4: C2H4 vs C3
SBP_5COMP = np.array([
    [+1, -1, -1, -1, -1],
    [ 0, +1, -1, -1, -1],
    [ 0,  0, +1, -1, -1],
    [ 0,  0,  0, +1, -1],
], dtype=float)

CHI2_CRITICAL_5COMP: float = 3.080216  # sqrt(chi2.ppf(0.95, df=4))

# Empirical envelope calibrated on 1,475 Plant-3 Train H shifts
HISTORICAL_MEAN_XI = np.array(
    [-0.6613989652, 2.0585004114, 2.8666052438, -2.2383652824],
    dtype=float
)
HISTORICAL_COV_INV = np.array([
    [ 32.346399, -23.967790,   3.522582,  1.853856],
    [-23.967790, 295.334057, -167.863704, 11.386687],
    [  3.522582, -167.863704, 107.460406, -2.449520],
    [  1.853856,  11.386687,  -2.449520,  3.673292],
], dtype=float)


def build_contrast_matrix(sbp: np.ndarray = SBP_5COMP) -> np.ndarray:
    """Compute orthonormal contrast matrix V of shape (D, D-1)."""
    sbp_arr = np.asarray(sbp, dtype=float)
    d_minus_1, d = sbp_arr.shape
    v = np.zeros((d, d_minus_1), dtype=float)
    for j, row in enumerate(sbp_arr):
        r = float((row > 0).sum())
        s = float((row < 0).sum())
        v[row > 0, j] = +math.sqrt(s / (r * (r + s)))
        v[row < 0, j] = -math.sqrt(r / (s * (r + s)))
    return v


V_MATRIX_5 = build_contrast_matrix(SBP_5COMP)


def closure(x: np.ndarray) -> np.ndarray:
    """Project composition vector(s) onto Simplex S^D (sum = 1.0)."""
    arr = np.asarray(x, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("Fraksi mol komponen tidak boleh bernilai negatif.")
    row_sums = arr.sum(axis=-1, keepdims=True)
    if np.any(row_sums <= 0.0):
        raise ValueError("Total fraksi mol komponen harus lebih besar dari nol.")
    return arr / row_sums


def replace_zeros(x: np.ndarray, delta: float = 1e-5) -> np.ndarray:
    """Multiplicative zero replacement preserving simplex closure."""
    arr = closure(x)
    is_zero = arr <= 0.0
    if not np.any(is_zero):
        return arr
    d = np.full(arr.shape[-1], float(delta), dtype=float)
    if arr.ndim == 1:
        if is_zero.all():
            return np.full_like(arr, 1.0 / len(arr))
        out = np.where(is_zero, d, arr * (1.0 - (is_zero * d).sum()))
    else:
        out = np.where(is_zero, d, arr * (1.0 - (is_zero * d).sum(axis=-1, keepdims=True)))
    return closure(out)


def ilr_forward(x: Union[List[float], np.ndarray], delta: float = 1e-5) -> np.ndarray:
    """Transform mole fractions (N2, C1, C2, C2H4, C3) from S^5 to Euclidean R^4."""
    arr = np.atleast_2d(np.asarray(x, dtype=float))
    x_safe = replace_zeros(arr, delta=delta)
    lx = np.log(x_safe)
    clr = lx - lx.mean(axis=-1, keepdims=True)
    return clr @ V_MATRIX_5


def ilr_inverse(xi: Union[List[float], np.ndarray]) -> np.ndarray:
    """Transform Euclidean ILR coordinates back to S^5 mole fractions."""
    xi_arr = np.atleast_2d(np.asarray(xi, dtype=float))
    return closure(np.exp(xi_arr @ V_MATRIX_5.T))


def compute_mahalanobis_distance(
    xi_point: np.ndarray,
    mean_xi: np.ndarray = HISTORICAL_MEAN_XI,
    cov_inv: np.ndarray = HISTORICAL_COV_INV,
) -> float:
    """Calculate Mahalanobis distance in 4D ILR coordinate space."""
    pt = np.asarray(xi_point, dtype=float).ravel()
    mu = np.asarray(mean_xi, dtype=float).ravel()
    diff = pt - mu
    dm_sq = float(diff @ cov_inv @ diff)
    return math.sqrt(max(0.0, dm_sq))


def check_composition_envelope(
    comp_mol_fracs: Union[List[float], np.ndarray],
) -> Dict[str, Union[bool, float, List[float]]]:
    """Verify whether a 5-component MCR mixture falls inside the historical operating envelope."""
    arr = np.asarray(comp_mol_fracs, dtype=float)
    xi = ilr_forward(arr)[0]
    dm = compute_mahalanobis_distance(xi)
    in_envelope = dm <= CHI2_CRITICAL_5COMP
    return {
        "in_envelope": in_envelope,
        "mahalanobis_distance": round(dm, 4),
        "critical_threshold": round(CHI2_CRITICAL_5COMP, 4),
        "xi_coordinates": [round(float(k), 4) for k in xi],
    }

