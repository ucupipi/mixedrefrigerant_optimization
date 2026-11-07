"""Pure-Python Peng-Robinson Equation of State (PR-EOS) Thermodynamic Engine.

Provides dependency-light, JVM-free phase equilibrium (VLE), compressibility factor,
density, molar enthalpy departure, dew/bubble point temperatures, 100-slice MCHE
pinch verification, and Riemann-sum exergy destruction calculations.
Units: pressure bar(a), temperature K, molar enthalpy J/mol, density kg/m3.
Governance: AGENTS.md (Pasal 1, 5, 11), ORIGINAL_REQUEST.md (§R4, F10).
"""
from __future__ import annotations

from typing import Any, Dict, Tuple
import numpy as np
from scipy.optimize import brentq

R: float = 8.31446261815324
BAR: float = 1e5
NAMES: Tuple[str, ...] = ("N2", "C1", "C2", "C2H4", "C3")
TC = np.array([126.20, 190.56, 305.32, 282.34, 369.83], dtype=float)
PC = np.array([33.90, 45.99, 48.72, 50.41, 42.48], dtype=float) * BAR
OMEGA = np.array([0.037, 0.011, 0.099, 0.087, 0.152], dtype=float)
MW = np.array([28.013, 16.042, 30.070, 28.054, 44.096], dtype=float) / 1000.0
KIJ = np.zeros((5, 5), dtype=float)
KIJ[0, 1] = KIJ[1, 0] = 0.038
KIJ[1, 2] = KIJ[2, 1] = 0.008
KIJ[1, 4] = KIJ[4, 1] = 0.015
CP = np.array([29.1, 35.7, 52.5, 43.6, 73.6], dtype=float)


def _x(x: Any) -> np.ndarray:
    arr = np.asarray(x, dtype=float).ravel()
    if arr.size != 5 or np.any(arr < 0.0) or not np.isfinite(arr).all() or arr.sum() <= 0.0:
        raise ValueError("x_mole_frac must contain five finite non-negative values with positive sum")
    return arr / arr.sum()


def _params(T: float, x: Any) -> Tuple[float, float, float, np.ndarray, np.ndarray, np.ndarray]:
    x_norm = _x(x)
    m = 0.37464 + 1.54226 * OMEGA - 0.26992 * OMEGA ** 2
    alpha = (1.0 + m * (1.0 - np.sqrt(T / TC))) ** 2
    ai = 0.45724 * R ** 2 * TC ** 2 / PC * alpha
    bi = 0.07780 * R * TC / PC
    aij = np.sqrt(ai[:, None] * ai[None, :]) * (1.0 - KIJ)
    a = float(x_norm @ aij @ x_norm)
    b = float(x_norm @ bi)
    dalpha = -(m * (1.0 + m * (1.0 - np.sqrt(T / TC)))) / np.sqrt(T * TC)
    dai = 0.45724 * R ** 2 * TC ** 2 / PC * dalpha
    daij = 0.5 * aij * (dai[:, None] / ai[:, None] + dai[None, :] / ai[None, :])
    da = float(x_norm @ daij @ x_norm)
    return a, b, da, ai, bi, aij


def _roots(P_bar: float, T_K: float, x: Any) -> Tuple[np.ndarray, float, float]:
    if P_bar <= 0.0 or T_K <= 0.0:
        raise ValueError("P_bar and T_K must be strictly positive")
    a, b, *_ = _params(T_K, x)
    P = float(P_bar) * BAR
    A = a * P / (R * T_K) ** 2
    B = b * P / (R * T_K)
    c = [1.0, -(1.0 - B), A - 3.0 * B ** 2 - 2.0 * B, -(A * B - B ** 2 - B ** 3)]
    roots = np.roots(c)
    real = np.sort(roots.real[np.abs(roots.imag) < 1e-7])
    real = real[real > B - 1e-10]
    if not len(real):
        raise ValueError("PR cubic has no physical real root (Z > B)")
    return real, float(A), float(B)


def pr_compressibility(P_bar: float, T_K: float, x_mole_frac: Any) -> Tuple[float, float]:
    """Return (Z_vapor, Z_liquid) compressibility factors from Peng-Robinson EOS."""
    r, _, B = _roots(P_bar, T_K, x_mole_frac)
    zv = float(r[-1])
    zl = float(r[0]) if len(r) > 1 else float(max(B * 1.05, min(zv * 0.15, zv - 1e-4)))
    return zv, zl


def pr_density(P_bar: float, T_K: float, x_mole_frac: Any, phase: str = "vapor") -> float:
    """Compute fluid mass density in kg/m3 for specified phase ('vapor' or 'liquid')."""
    x_norm = _x(x_mole_frac)
    r, _, _ = _roots(P_bar, T_K, x_norm)
    z = float(r[0]) if phase.lower().startswith("l") else float(r[-1])
    return float(P_bar * BAR * (x_norm @ MW) / (z * R * T_K))


def _lnphi(P_bar: float, T: float, x: Any, phase: str) -> np.ndarray:
    x_norm = _x(x)
    P = float(P_bar) * BAR
    a, b, _, ai, bi, aij = _params(T, x_norm)
    r, _, _ = _roots(P_bar, T, x_norm)
    Z = float(r[0]) if phase.startswith("l") else float(r[-1])
    A = a * P / (R * T) ** 2
    B = b * P / (R * T)
    S = aij @ x_norm
    q = np.log((Z + (1.0 + np.sqrt(2.0)) * B) / (Z + (1.0 - np.sqrt(2.0)) * B))
    return bi / b * (Z - 1.0) - np.log(Z - B) - A / (2.0 * np.sqrt(2.0) * B) * (2.0 * S / a - bi / b) * q


def _equilibrate(P: float, T: float, z: Any, beta0: float = 0.5) -> Tuple[np.ndarray, np.ndarray, float]:
    z_norm = _x(z)
    r, _, _ = _roots(P, T, z_norm)
    if len(r) == 1:
        K = (PC / (P * BAR)) * np.exp(5.373 * (1.0 + OMEGA) * (1.0 - TC / T))
        if np.sum(z_norm / K) < 1.0:
            return z_norm, z_norm, 1.0
        if np.sum(z_norm * K) < 1.0:
            return z_norm, z_norm, 0.0
        return (z_norm, z_norm, 1.0) if float(r[0]) > 0.5 else (z_norm, z_norm, 0.0)
    ln_phi_l = _lnphi(P, T, z_norm, "l")
    ln_phi_v = _lnphi(P, T, z_norm, "v")
    K = np.exp(np.clip(ln_phi_l - ln_phi_v, -20.0, 20.0))
    if np.all(np.abs(K - 1.0) < 1e-5):
        return (z_norm, z_norm, 1.0) if float(r[-1]) > 0.5 else (z_norm, z_norm, 0.0)
    beta = beta0
    xl = z_norm.copy()
    yv = z_norm.copy()
    for _ in range(100):
        def rr(b: float) -> float:
            return float(np.sum(z_norm * (K - 1.0) / (1.0 + b * (K - 1.0))))
        f0 = rr(0.0)
        f1 = rr(1.0)
        if f0 <= 0.0:
            return z_norm, z_norm, 0.0
        if f1 >= 0.0:
            return z_norm, z_norm, 1.0
        beta = float(brentq(rr, 0.0, 1.0))
        xl = z_norm / (1.0 + beta * (K - 1.0))
        yv = K * xl
        xl /= xl.sum()
        yv /= yv.sum()
        knew = np.exp(np.clip(_lnphi(P, T, xl, "l") - _lnphi(P, T, yv, "v"), -20.0, 20.0))
        if np.max(np.abs(np.log(knew / K))) < 1e-7:
            return xl, yv, beta
        K = 0.5 * K + 0.5 * knew
    return xl, yv, beta


def pr_dew_bubble_temperatures(P_bar: float, x_mole_frac: Any) -> Tuple[float, float]:
    """Return (T_dew_K, T_bubble_K) at pressure P_bar for mixture x_mole_frac."""
    z_norm = _x(x_mole_frac)

    def k_w(T: float) -> np.ndarray:
        return (PC / (P_bar * BAR)) * np.exp(5.373 * (1.0 + OMEGA) * (1.0 - TC / T))

    def f_b(T: float) -> float:
        return float(np.sum(z_norm * k_w(T)) - 1.0)

    def f_d(T: float) -> float:
        return float(np.sum(z_norm / k_w(T)) - 1.0)

    grid = np.linspace(80.0, 450.0, 200)

    def solve_bracket(fn: Any) -> float:
        vals = [fn(t) for t in grid]
        for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
            if np.isfinite(fa) and np.isfinite(fb) and fa * fb <= 0.0:
                return float(brentq(fn, a, b))
        return float("nan")

    tb = solve_bracket(f_b)
    td = solve_bracket(f_d)
    if np.isfinite(tb) and np.isfinite(td) and tb > td:
        tb, td = td, tb
    return float(td), float(tb)


def _h(T: float, P: float, x: Any, phase: str = "vapor") -> float:
    """Compute molar enthalpy (J/mol) including PR-EOS enthalpy departure."""
    x_norm = _x(x)
    a, b, da, *_ = _params(T, x_norm)
    r, _, _ = _roots(P, T, x_norm)
    z = float(r[-1]) if phase == "vapor" else float(r[0])
    B = b * P * BAR / (R * T)
    q = np.log((z + (1.0 + np.sqrt(2.0)) * B) / (z + (1.0 - np.sqrt(2.0)) * B))
    return float((x_norm @ CP) * (T - 273.15) + R * T * (z - 1.0) + (T * da - a) / (2.0 * np.sqrt(2.0) * b) * q)


def mche_pinch_check(feed_cooling_curve: Any, mcr_warming_curve: Any) -> Dict[str, Any]:
    """Evaluate Minimum Internal Temperature Approach (MITA) across composite curves."""
    hot = np.asarray(feed_cooling_curve, dtype=float)
    cold = np.asarray(mcr_warming_curve, dtype=float)
    if hot.ndim != 2 or cold.ndim != 2 or hot.shape[1] != 2 or cold.shape[1] != 2:
        raise ValueError("Composite curves must have shape (N, 2) as (temperature_C, duty_fraction)")
    hot = hot[np.argsort(hot[:, 1])]
    cold = cold[np.argsort(cold[:, 1])]
    q_profile = np.linspace(0.0, 1.0, 100)
    q_eval = np.unique(np.concatenate((q_profile, hot[:, 1], cold[:, 1])))
    d_eval = np.interp(q_eval, hot[:, 1], hot[:, 0]) - np.interp(q_eval, cold[:, 1], cold[:, 0])
    idx = int(np.argmin(d_eval))
    return {
        "pinch_delta_T_C": float(d_eval[idx]),
        "pinch_index": idx,
        "q_fraction": float(q_eval[idx]),
        "delta_T_profile_C": np.interp(q_profile, q_eval, d_eval),
    }


def compute_mche_riemann_exergy_mw(
    hot_temp_k_slices: np.ndarray,
    cold_temp_k_slices: np.ndarray,
    total_duty_mw: float,
    t0_k: float = 288.15,
) -> float:
    """Compute MCHE exergy destruction in MW via 100-slice Riemann integral (AGENTS.md Pasal 11)."""
    t_hot = np.asarray(hot_temp_k_slices, dtype=float).ravel()
    t_cold = np.asarray(cold_temp_k_slices, dtype=float).ravel()
    if t_hot.size != t_cold.size or t_hot.size < 2:
        raise ValueError("Hot and cold temperature slice arrays must have identical length >= 2")
    if np.any(t_hot <= 0.0) or np.any(t_cold <= 0.0):
        raise ValueError("Absolute temperatures in Kelvin must be strictly positive")
    dq_mw = float(total_duty_mw) / float(t_hot.size)
    exergy_dest_mw = float(t0_k) * float(np.sum(dq_mw * (1.0 / t_cold - 1.0 / t_hot)))
    return max(0.0, exergy_dest_mw)


def compute_compressor_gouy_stodola_exergy_mw(shaft_power_mw: float, isentropic_eff: float) -> float:
    """Compute compressor irreversibility in MW using pure Gouy-Stodola theorem (no magic multiplier)."""
    if not (0.0 < isentropic_eff <= 1.0):
        raise ValueError(f"Isentropic efficiency must be in (0, 1], got {isentropic_eff}")
    return float(shaft_power_mw) * (1.0 - float(isentropic_eff))

