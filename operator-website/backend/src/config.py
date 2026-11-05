"""Configuration Management Framework for MCR_ML_REBUILD.

Provides strongly-typed, immutable dataclass configuration loaded safely from YAML
with dynamic environment variable overrides (MCR_ prefix) and cross-platform path resolution.
Governance: AGENTS.md (Pasals 1-13), ORIGINAL_REQUEST.md (§R2).
"""
from __future__ import annotations

import os
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union, get_type_hints
import yaml


# ── Sub-Configurations ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PathsConfig:
    """Filesystem path configuration with environment-independent defaults."""
    raw_dir: str = "data/raw"
    interim_dir: str = "data/interim"
    processed_dir: str = "data/processed"
    manifest_path: str = "data/manifests/sha256_manifest.json"
    models_dir: str = "models"
    reports_dir: str = "reports"


@dataclass(frozen=True)
class DataConfig:
    """Data paths, canonical raw file inventory, and leakage quarantine specifications."""
    raw_dir: str = "data/raw"
    interim_dir: str = "data/interim"
    processed_dir: str = "data/processed"
    manifest_path: str = "data/manifests/sha256_manifest.json"
    models_dir: str = "models"
    reports_dir: str = "reports"
    canonical_files: Tuple[str, ...] = (
        "OverallComposition_2023_2024.xlsx",
        "OverallComposition_August_2026.tsv",
        "OverallComposition_July_2025.tsv",
        "ProcessParameter_2023_2024.xlsx",
        "ProcessParameter_August_2026.xlsx",
        "ProcessParameter_July_2025.xlsx",
    )
    quarantined_tags: Tuple[str, ...] = (
        "H4FI029A",
        "H4FI030A",
        "H4FI031A",
        "H5FI006A",
        "H1FI0009",
        "total_steam_t_h",
        "total_shaft_power_mw",
        "mcr_shaft_power_mw",
        "c3_shaft_power_mw",
        "exergy_destruction_mw",
    )


@dataclass(frozen=True)
class ThermoConfig:
    """Pure-Python Peng-Robinson thermodynamic constants and operational constraints."""
    t0_k: float = 288.15
    p0_kpa: float = 101.325
    components: Tuple[str, ...] = ("N2", "C1", "C2", "C2H4", "C3")
    tc_k: Tuple[float, ...] = (126.20, 190.56, 305.32, 282.34, 369.83)
    pc_bar: Tuple[float, ...] = (33.90, 45.99, 48.72, 50.41, 42.48)
    omega: Tuple[float, ...] = (0.037, 0.011, 0.099, 0.087, 0.152)
    mw_g_mol: Tuple[float, ...] = (28.013, 16.042, 30.070, 28.054, 44.096)
    cp_ideal_j_mol_k: Tuple[float, ...] = (29.1, 35.7, 52.5, 43.6, 73.6)
    kij: Tuple[Tuple[float, ...], ...] = (
        (0.000, 0.038, 0.000, 0.000, 0.000),
        (0.038, 0.000, 0.008, 0.000, 0.015),
        (0.000, 0.008, 0.000, 0.000, 0.000),
        (0.000, 0.000, 0.000, 0.000, 0.000),
        (0.000, 0.015, 0.000, 0.000, 0.000),
    )
    mita_min_c: float = 1.50
    mita_guardband_c: float = 2.00
    tal_suction_c: float = -45.0
    suction_superheat_min_c: float = 3.0
    flow_floor_t_h: float = 480.0
    mche_slices: int = 100
    chi2_critical_5comp: float = 3.080216
    chi2_critical_4comp: float = 2.795488


@dataclass(frozen=True)
class FeaturesConfig:
    """Feature engineering, ILR simplex projection, and discrete shift alignment."""
    rolling_window_minutes: int = 120
    rolling_metrics: Tuple[str, ...] = ("mean", "std", "min", "max")
    max_timestamp_gap_minutes: int = 10
    zero_replacement_delta: float = 1e-5
    sbp_5comp: Tuple[Tuple[int, ...], ...] = (
        ( 1, -1, -1, -1, -1),
        ( 0,  1, -1, -1, -1),
        ( 0,  0,  1, -1, -1),
        ( 0,  0,  0,  1, -1),
    )
    gc_sampling_location: str = "4C-8"


FeatureConfig = FeaturesConfig


@dataclass(frozen=True)
class ModelsConfig:
    """Model training hyperparameters, monotonic constraints, and acceptance thresholds."""
    test_split_ratio: float = 0.20
    cv_folds: int = 5
    random_state: int = 42
    hgb_max_iter: int = 150
    hgb_learning_rate: float = 0.05
    hgb_max_leaf_nodes: int = 31
    hgb_min_samples_leaf: int = 20
    hgb_l2_regularization: float = 0.1
    monotonic_cst: Tuple[int, ...] = (1, 1, 0, 0, 0, 0)
    ridge_alpha: float = 1.0
    max_mae_mw: float = 1.0
    max_nmae_pct: float = 1.0
    min_r2: float = 0.60
    composition_closure_atol: float = 1e-6


ModelConfig = ModelsConfig


@dataclass(frozen=True)
class EvaluationConfig:
    """Acceptance gate limits, reporting parameters, and engineering metrics."""
    max_mae_mw: float = 1.0
    max_nmae_pct: float = 1.0
    min_r2: float = 0.60
    composition_closure_atol: float = 1e-6
    report_format: str = "json"


@dataclass(frozen=True)
class EconomicsConfig:
    """Plant operating hours, energy pricing, and carbon emissions factors."""
    annual_operating_hours: float = 8000.0
    fuel_gas_price_usd_per_mmbtu: float = 10.04
    fuel_gas_lhv_mj_per_nm3: float = 38.0
    boiler_efficiency_pct: float = 88.0
    co2_emission_factor_kg_per_gj: float = 56.1


# ── Root Configuration ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Config:
    """Root configuration tree encapsulating all subsystem settings."""
    paths: PathsConfig = field(default_factory=PathsConfig)
    data: DataConfig = field(default_factory=DataConfig)
    thermo: ThermoConfig = field(default_factory=ThermoConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    models: ModelsConfig = field(default_factory=ModelsConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    economics: EconomicsConfig = field(default_factory=EconomicsConfig)

    @property
    def model(self) -> ModelsConfig:
        """Alias for models configuration."""
        return self.models

    @property
    def project_root(self) -> Path:
        """Dynamically resolved project root directory."""
        return Path(__file__).resolve().parents[1]

    def resolve_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a project-relative path to an absolute path cross-platform."""
        p = Path(relative_path)
        return p if p.is_absolute() else (self.project_root / p).resolve()


# ── Loader & Environment Override Utilities ───────────────────────────────────

def _apply_env_overrides(raw_dict: Dict[str, Any], prefix: str = "MCR_") -> Dict[str, Any]:
    """Recursively override dictionary values from environment variables matching prefix.

    Example: MCR_MODELS__HGB_LEARNING_RATE=0.01 overrides raw_dict['models']['hgb_learning_rate'].
    """
    for key, val in os.environ.items():
        if key.startswith(prefix):
            path_parts = key[len(prefix):].lower().split("__")
            d = raw_dict
            for part in path_parts[:-1]:
                if part not in d or not isinstance(d[part], dict):
                    d[part] = {}
                d = d[part]
            try:
                parsed_val = yaml.safe_load(val)
            except Exception:
                parsed_val = val
            d[path_parts[-1]] = parsed_val
    return raw_dict


def _dict_to_dataclass(cls: Type[Any], data: Dict[str, Any]) -> Any:
    """Recursively populate a typed dataclass from a nested dictionary with tuple casting."""
    init_kwargs = {}
    type_hints = get_type_hints(cls)
    for f in fields(cls):
        name = f.name
        f_type = type_hints.get(name, f.type)
        if name in data:
            val = data[name]
            if is_dataclass(f_type) and isinstance(val, dict):
                init_kwargs[name] = _dict_to_dataclass(f_type, val)
            elif getattr(f_type, "__origin__", None) is tuple and isinstance(val, (list, tuple)):
                args = getattr(f_type, "__args__", ())
                if args and getattr(args[0], "__origin__", None) is tuple:
                    init_kwargs[name] = tuple(tuple(row) for row in val)
                else:
                    init_kwargs[name] = tuple(val)
            else:
                init_kwargs[name] = val
        else:
            if f.default is not MISSING:
                init_kwargs[name] = f.default
            elif f.default_factory is not MISSING:
                init_kwargs[name] = f.default_factory()
    return cls(**init_kwargs)


def load_config(
    config_path: Optional[Union[str, Path]] = None,
    env_prefix: str = "MCR_",
    allow_missing: bool = True,
) -> Config:
    """Load configuration from a YAML file with environment variable overrides.

    If config_path is None, defaults to configs/default.yaml relative to project root.
    If allow_missing is False and target_path does not exist, raises FileNotFoundError.
    """
    default_path = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"
    target_path = Path(config_path) if config_path else default_path

    if not allow_missing and not target_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {target_path}")

    raw_dict: Dict[str, Any] = {}
    if target_path.exists():
        with open(target_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                raw_dict = loaded

    raw_dict = _apply_env_overrides(raw_dict, prefix=env_prefix)
    return _dict_to_dataclass(Config, raw_dict)
