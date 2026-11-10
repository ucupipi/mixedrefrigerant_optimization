"""Shared fixtures, reference implementations, and physical constants for IKMS 2026 E2E tests.

Authoritative Sources:
- AGENTS.md (Hukum Anti-Dosa Rekayasa, Pasals 1 to 13)
- ORIGINAL_REQUEST.md (Requirements R1 to R5)
- TEST_INFRA.md (Test Philosophy & Inventory)
- PROJECT.md (Architecture, Interface Contracts 1-3, Milestones M1-M5)
- DATA_LEDGER.json (Single Source of Truth / SSOT Ledger)
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple

import numpy as np
import pytest


# ── Directory Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def ikms_root() -> Path:
    """Root working directory of IKMS 2026 submission."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def oilweek_root() -> Path:
    """Primary telemetry and historical model archive repository."""
    return Path(r"D:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK")


@pytest.fixture(scope="session")
def data_ledger_path(ikms_root: Path) -> Path:
    """Path to Single Source of Truth DATA_LEDGER.json."""
    return ikms_root / "DATA_LEDGER.json"


@pytest.fixture(scope="session")
def data_ledger(data_ledger_path: Path) -> Dict[str, Any]:
    """Loaded dictionary of the Single Source of Truth ledger."""
    with open(data_ledger_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def pdf_paths(ikms_root: Path) -> Dict[str, Path]:
    """Paths to the 3 Dresser-Rand compressor performance curves."""
    return {
        "4K-1": ikms_root / "H4K-1.pdf",
        "4K-2": ikms_root / "H4K-2.pdf",
        "4K-3": ikms_root / "H4K-3.pdf",
    }


# ── SSOT Constants & Baselines ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def optimal_mcr_recipe(data_ledger: Dict[str, Any]) -> Dict[str, Any]:
    """Optimal 5-component MCR composition and statistical envelope."""
    return data_ledger["optimal_mcr_composition_mol_percent"]


@pytest.fixture(scope="session")
def baseload_p90(data_ledger: Dict[str, Any]) -> Dict[str, Any]:
    """Baseload P90 operational baseline and optimized parameters."""
    return data_ledger["baseload_P90"]


@pytest.fixture(scope="session")
def underload_p10(data_ledger: Dict[str, Any]) -> Dict[str, Any]:
    """Underload P10 turndown baseline and safety parameters."""
    return data_ledger["underload_P10"]


@pytest.fixture(scope="session")
def surrogate_metrics(data_ledger: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List of reported surrogate models metrics in DATA_LEDGER.json."""
    return data_ledger["surrogate_models_metrics"]


# ── Physical & Thermodynamic Constants ────────────────────────────────────────

# IUPAC Standard Atomic Weights & Molecular Weights (g/mol)
MW_COMPONENTS = {
    "N2": 28.0134,
    "CH4": 16.0425,
    "C2H6": 30.0690,
    "C2H4": 28.0532,
    "C3H8": 44.0956,
    "iC4": 58.1222,
    "nC4": 58.1222,
    "iC5": 72.1488,
}

# Critical properties for Peng-Robinson EOS: (Tc [K], Pc [bar], omega)
CRITICAL_PROPS = {
    "N2":   (126.2, 33.98, 0.0377),
    "CH4":  (190.56, 45.99, 0.0115),
    "C2H6": (305.32, 48.72, 0.0995),
    "C2H4": (282.34, 50.41, 0.0866),
    "C3H8": (369.83, 42.48, 0.1523),
}

R_GAS_J_MOL_K = 8.314462618  # Universal gas constant (J / (mol * K))
RAMADAN_BOILER_FACTOR = 97.70  # Nm³ fuel gas / ton steam (Ramadan, 2025)
IPCC_CO2_FACTOR = 56.10  # kg CO2 / GJ
FUEL_GAS_LHV_MJ_NM3 = 38.0  # MJ / Nm³ fuel gas


# ── Reference ILR Simplex Geometry (AGENTS.md Pasal 5) ────────────────────────

SBP5 = np.array([
    [+1, -1, -1, -1, -1],  # xi1: N2 vs (C1, C2, C2H4, C3)
    [ 0, +1, -1, -1, -1],  # xi2: C1 vs (C2, C2H4, C3)
    [ 0,  0, +1, -1, -1],  # xi3: C2 vs (C2H4, C3)
    [ 0,  0,  0, +1, -1],  # xi4: C2H4 vs C3
], dtype=float)


def compute_v_matrix(sbp: np.ndarray) -> np.ndarray:
    """Compute orthonormal contrast matrix V from Sequential Binary Partition."""
    d1, d = sbp.shape
    v = np.zeros((d, d1), dtype=float)
    for j, row in enumerate(sbp):
        r = float((row > 0).sum())
        s = float((row < 0).sum())
        v[row > 0, j] = +math.sqrt(s / (r * (r + s)))
        v[row < 0, j] = -math.sqrt(r / (s * (r + s)))
    return v


V_MATRIX_5 = compute_v_matrix(SBP5)  # shape (5, 4)


def ref_closure(x: np.ndarray) -> np.ndarray:
    """Project composition vector(s) onto Simplex S^D (sum=1.0)."""
    x = np.asarray(x, dtype=float)
    return x / x.sum(axis=-1, keepdims=True)


def ref_replace_zeros(x: np.ndarray, delta: float = 1e-5) -> np.ndarray:
    """Multiplicative zero replacement (Martin-Fernandez et al. 2003)."""
    x = ref_closure(x)
    is_zero = x <= 0.0
    if not np.any(is_zero):
        return x
    d = np.full(x.shape[-1], delta, dtype=float)
    if x.ndim == 1:
        if is_zero.all():
            return np.full_like(x, 1.0 / len(x))
        out = np.where(is_zero, d, x * (1.0 - (is_zero * d).sum()))
    else:
        out = np.where(is_zero, d, x * (1.0 - (is_zero * d).sum(axis=-1, keepdims=True)))
    return ref_closure(out)


def ref_ilr_forward(x: np.ndarray) -> np.ndarray:
    """Isometric Log-Ratio forward transform from S^5 to R^4."""
    x = np.atleast_2d(x)
    x_safe = ref_replace_zeros(x)
    lx = np.log(x_safe)
    clr = lx - lx.mean(axis=-1, keepdims=True)
    return clr @ V_MATRIX_5


def ref_ilr_inverse(xi: np.ndarray) -> np.ndarray:
    """Isometric Log-Ratio inverse transform from R^4 to S^5."""
    xi = np.atleast_2d(xi)
    return ref_closure(np.exp(xi @ V_MATRIX_5.T))


@pytest.fixture(scope="session")
def ilr_engine():
    """Reference ILR engine fixture."""
    return {
        "sbp": SBP5,
        "v_matrix": V_MATRIX_5,
        "closure": ref_closure,
        "replace_zeros": ref_replace_zeros,
        "forward": ref_ilr_forward,
        "inverse": ref_ilr_inverse,
        "chi2_critical": 3.0802,  # sqrt(chi2(df=4, p=0.95))
    }


# ── Reference PR-EOS Thermodynamic Solver ────────────────────────────────────

def solve_pr_eos_z(p_bar: float, t_k: float, z_mol: np.ndarray) -> float:
    """Pure-Python Peng-Robinson EOS compressibility factor Z solver for gas phase.
    
    Implements standard van der Waals one-fluid mixing rules without binary interaction params.
    """
    comp_keys = ["N2", "CH4", "C2H6", "C2H4", "C3H8"]
    z_mol = np.asarray(z_mol, dtype=float)
    z_mol = z_mol / z_mol.sum()

    a_i = []
    b_i = []
    for i, key in enumerate(comp_keys):
        tc, pc, omega = CRITICAL_PROPS[key]
        tr = t_k / tc
        kappa = 0.37464 + 1.54226 * omega - 0.26992 * (omega ** 2)
        alpha = (1.0 + kappa * (1.0 - math.sqrt(tr))) ** 2
        ai = 0.45724 * (R_GAS_J_MOL_K * tc) ** 2 / (pc * 1e5) * alpha
        bi = 0.07780 * (R_GAS_J_MOL_K * tc) / (pc * 1e5)
        a_i.append(ai)
        b_i.append(bi)

    # Van der Waals mixing
    a_mix = 0.0
    for i in range(len(comp_keys)):
        for j in range(len(comp_keys)):
            a_mix += z_mol[i] * z_mol[j] * math.sqrt(a_i[i] * a_i[j])
    b_mix = sum(z_mol[i] * b_i[i] for i in range(len(comp_keys)))

    p_pa = p_bar * 1e5
    A = a_mix * p_pa / ((R_GAS_J_MOL_K * t_k) ** 2)
    B = b_mix * p_pa / (R_GAS_J_MOL_K * t_k)

    # Cubic equation: Z^3 - (1 - B)*Z^2 + (A - 3B^2 - 2B)*Z - (AB - B^2 - B^3) = 0
    c2 = -(1.0 - B)
    c1 = A - 3.0 * (B ** 2) - 2.0 * B
    c0 = -(A * B - (B ** 2) - (B ** 3))

    roots = np.roots([1.0, c2, c1, c0])
    real_roots = [float(r.real) for r in roots if abs(r.imag) < 1e-6 and r.real > B]
    if not real_roots:
        return 1.0
    # For gas phase, take the largest real root
    return max(real_roots)


def compute_mcr_density(p_bar: float, t_k: float, z_mol: np.ndarray) -> float:
    """Compute density [kg/m³] from PR-EOS: rho = (P * MW) / (Z * R * T)."""
    comp_keys = ["N2", "CH4", "C2H6", "C2H4", "C3H8"]
    mw_mix = sum(z_mol[i] * MW_COMPONENTS[k] for i, k in enumerate(comp_keys)) * 1e-3  # kg/mol
    z = solve_pr_eos_z(p_bar, t_k, z_mol)
    p_pa = p_bar * 1e5
    rho = (p_pa * mw_mix) / (z * R_GAS_J_MOL_K * t_k)
    return float(rho)


@pytest.fixture(scope="session")
def thermo_engine():
    """Thermodynamic PR-EOS calculation utilities."""
    return {
        "pr_eos_z": solve_pr_eos_z,
        "mcr_density": compute_mcr_density,
        "mw_components": MW_COMPONENTS,
        "ramadan_boiler_factor": RAMADAN_BOILER_FACTOR,
        "ipcc_co2_factor": IPCC_CO2_FACTOR,
        "fuel_gas_lhv": FUEL_GAS_LHV_MJ_NM3,
    }


# ── File Hashing Fixture ──────────────────────────────────────────────────────

def compute_file_sha256(filepath: Path, chunk_size: int = 1024 * 1024) -> str:
    """Stream-hash file to avoid memory spikes on large archives."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


@pytest.fixture(scope="session")
def file_hasher():
    return compute_file_sha256
