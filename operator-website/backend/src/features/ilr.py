"""5-Component Isometric Log-Ratio (ILR) Compositional Geometry Engine.

Maps 5-component Mixed Refrigerant compositions (N2, C1, C2, C2H4, C3) from the
Aitchison Simplex S^5 to unconstrained Euclidean space R^4 via orthonormal
Sequential Binary Partition (SBP) contrast matrices, with Mahalanobis envelope screening.
Governance: AGENTS.md (Pasal 5, 12), ORIGINAL_REQUEST.md (§R4, F9).
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple
import numpy as np
from scipy.spatial.distance import mahalanobis


SBP_5COMP = np.array([
    [+1, -1, -1, -1, -1],  # xi_1: N2 vs (C1, C2, C2H4, C3)
    [ 0, +1, -1, -1, -1],  # xi_2: C1 vs (C2, C2H4, C3)
    [ 0,  0, +1, -1, -1],  # xi_3: C2 vs (C2H4, C3)
    [ 0,  0,  0, +1, -1],  # xi_4: C2H4 vs C3
], dtype=float)

CHI2_CRITICAL_5COMP: float = 3.080216  # sqrt(chi2.ppf(0.95, df=4))


def build_contrast_matrix(sbp: np.ndarray = SBP_5COMP) -> np.ndarray:
    """Compute orthonormal contrast matrix V of shape (D, D-1) from Sequential Binary Partition."""
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
    """Project non-negative composition vector(s) onto Simplex S^D (sum = 1.0)."""
    arr = np.asarray(x, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("Negative mole fraction prohibited in simplex closure")
    row_sums = arr.sum(axis=-1, keepdims=True)
    if np.any(row_sums <= 0.0):
        raise ValueError("Composition sum must be strictly positive")
    return arr / row_sums


def replace_zeros(x: np.ndarray, delta: float = 1e-5) -> np.ndarray:
    """Multiplicative zero replacement (Martin-Fernandez et al. 2003) preserving closure."""
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


def ilr_forward(x: np.ndarray, delta: float = 1e-5, v_matrix: np.ndarray = V_MATRIX_5) -> np.ndarray:
    """Transform composition vector(s) from S^5 (N, 5) to Euclidean ILR coordinates R^4 (N, 4)."""
    arr = np.atleast_2d(np.asarray(x, dtype=float))
    x_safe = replace_zeros(arr, delta=delta)
    lx = np.log(x_safe)
    clr = lx - lx.mean(axis=-1, keepdims=True)
    return clr @ v_matrix


def ilr_inverse(xi: np.ndarray, v_matrix: np.ndarray = V_MATRIX_5) -> np.ndarray:
    """Transform Euclidean ILR coordinates R^4 (N, 4) back to Simplex S^5 (N, 5) with exact closure."""
    xi_arr = np.atleast_2d(np.asarray(xi, dtype=float))
    return closure(np.exp(xi_arr @ v_matrix.T))


def compute_mahalanobis_distance(
    xi_point: np.ndarray,
    mean_xi: np.ndarray,
    cov_inv: np.ndarray,
) -> float:
    """Compute Mahalanobis distance D_M in 4D ILR space."""
    pt = np.asarray(xi_point, dtype=float).ravel()
    mu = np.asarray(mean_xi, dtype=float).ravel()
    return float(mahalanobis(pt, mu, cov_inv))


def fit_ilr_envelope(xi_train: np.ndarray, reg_eps: float = 1e-6) -> Dict[str, np.ndarray]:
    """Fit mean vector and inverse covariance matrix exclusivamente on training ILR coordinates."""
    xi_arr = np.atleast_2d(np.asarray(xi_train, dtype=float))
    mean_xi = np.mean(xi_arr, axis=0)
    cov = np.cov(xi_arr, rowvar=False) + np.eye(xi_arr.shape[1]) * float(reg_eps)
    cov_inv = np.linalg.inv(cov)
    return {"mean_xi": mean_xi, "cov": cov, "cov_inv": cov_inv}


def check_mahalanobis_envelope(
    xi_point: np.ndarray,
    mean_xi: np.ndarray,
    cov_inv: np.ndarray,
    critical_limit: float = CHI2_CRITICAL_5COMP,
) -> Tuple[bool, float]:
    """Verify whether an ILR composition vector lies inside the 95% historical operating ellipsoid."""
    dm = compute_mahalanobis_distance(xi_point, mean_xi, cov_inv)
    return (dm <= float(critical_limit)), dm

