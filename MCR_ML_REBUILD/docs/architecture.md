# MCR_ML_REBUILD: System Architecture & Engineering Blueprint

**Document ID:** `REBUILD-ARCH-001`  
**Classification:** INDUSTRIAL PROCESS ML ARCHITECTURE  
**Target Subsystem:** Badak LNG Plant-3 Train H C3MR Liquefaction Optimization  
**Governance:** `AGENTS.md` (Pasals 1–13), `ORIGINAL_REQUEST.md` (§R2)  

---

## 1. Architectural Philosophy & Design Principles

The `MCR_ML_REBUILD` suite is engineered as an isolated, modular, pure-Python machine learning and thermodynamic optimization system for industrial refrigeration circuits.

### Core Architectural Pillars
1. **Physical Isolation**: Complete decoupling from legacy experiment scripts and archives, preventing circular dependencies and state leakage.
2. **Minimal Dependency Footprint**: Exclusively standard library CPython, NumPy, Pandas, SciPy, Scikit-learn, Joblib, and PyYAML. Strictly zero JVM bridges (`py4j`, `jpype`, `neqsim`), proprietary COM automation (`win32com`, `aspen`), or heavy DL frameworks (`torch`, `tensorflow`).
3. **First-Principles Thermodynamic Coupling**: Numerical models are constrained by first-principles physical limits:
   - Peng-Robinson Equation of State (PR-EOS) for multicomponent vapor-liquid equilibrium (VLE).
   - Suction Drum Temperature Alarm Low (TAL $\ge -45.0^\circ\text{C}$).
   - MCHE Minimum Internal Temperature Approach (MITA $\ge 1.50^\circ\text{C}$).
   - Compressor anti-surge flow floor ($\ge 480.0\text{ t/h}$).
4. **Compositional Simplex Rigor**: Mixed refrigerant compositions ($N_2, C_1, C_2, C_2H_4, C_3$) reside on Simplex $S^5$ and are projected to unconstrained 4D Euclidean space using Isometric Log-Ratio (ILR) transformations with closure guarantees ($\sum x_i \equiv 1.0$) and Mahalanobis distance validation ($D_M \le 3.0802$).
5. **Leakage Prevention & Discrete Shift Alignment**: Sensor telemetry and discrete GC samples are integrated at shift resolution ($N=2,531$), eliminating 480-minute forward-fill pseudo-replication. Quarantines 10 target-reconstructing tags.

---

## 2. End-to-End Data Pipeline Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAW DATA ASSETS (Read-Only)                       │
│  - ProcessParameter (2023-2024, July 2025, August 2026)                    │
│  - OverallComposition (2023-2024, July 2025, August 2026)                  │
│  - Cryptographic Verification: data/manifests/sha256_manifest.json          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION & GOVERNANCE FIREWALL                     │
│  - Tag Reconciliation against CANONICAL_TAG_DICTIONARY.csv                  │
│  - Discrete Shift Alignment (07:00-15:00, 15:00-23:00, 23:00-07:00 at 4C-8) │
│  - 10-Tag Target Quarantine (H4FI029A, H4FI030A, H4FI031A, H5FI006A, etc.) │
│  - Output: data/interim/shift_aligned_master.parquet                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FEATURE ENGINEERING & COMPOSITION ILR                   │
│  - 5-Component Simplex Closure & Multiplicative Zero Replacement (delta=1e-5)│
│  - Orthonormal Contrast ILR Transform (S^5 -> R^4) via SBP matrix           │
│  - 120-minute Rolling Window Aggregations (mean, std, min, max)             │
│  - Shutdown Gap Boundary Filtering (gap > 10 min)                            │
│  - Output: data/processed/features_unleaked.parquet                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATION PARTITIONING & MODEL TRAINING                 │
│  - Chronological Blocked Split (80:20 Train/Test) with Purge Gap            │
│  - Baseline Benchmarking: DummyRegressor, Mean, Ridge Regression            │
│  - Candidate Surrogate: HistGradientBoostingRegressor                       │
│    Monotonic Constraints: [feed_rate (+1), ambient_temp (+1), xi1..4 (0)]   │
│  - Output: models/surrogate_c3mr_power.joblib                               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROPORTIONAL ENGINEERING UNIT EVALUATION                 │
│  - Total Train C3MR Shaft Power Evaluation (MW basis):                      │
│    Direct MCR (4KT-2/3) + Indirect C3 Precooling (4KT-1)                    │
│  - Acceptance Gates: MAE < 1.0 MW, NMAE < 1.0%, R² >= 0.60                  │
│  - Exergy Destruction via Discretized Riemann Integral (100 MCHE slices)     │
│  - Output: reports/evaluation_metrics.json                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Specifications

### 3.1 `src/data/` — Data Ingestion & Governance
- **`audit.py`**: Computes SHA-256 digests and validates against `sha256_manifest.json`.
- **`ingestion.py`**: Reads raw telemetry, aligns discrete GC samples by shift timestamp, applies zero-order hold within active shifts only.
- **`governance.py`**: Intercepts feature columns and enforces hard quarantine on the 10 target-reconstructing tags.

### 3.2 `src/features/` — Compositional Geometry & Feature Extraction
- **`ilr.py`**: Implements Sequential Binary Partition (SBP) contrast matrix $V \in \mathbb{R}^{5 \times 4}$. Computes forward transform $\boldsymbol{\xi} = \operatorname{ilr}(\mathbf{x})$ and inverse $\mathbf{x} = \operatorname{ilr}^{-1}(\boldsymbol{\xi})$. Validates Mahalanobis distance $D_M \le 3.0802$.
- **`engineering.py`**: Computes rolling statistics over 120-minute windows, detecting gaps $>10\text{ min}$ to prevent cross-shutdown statistical pollution.

### 3.3 `src/thermo/` — Pure-Python Peng-Robinson Thermodynamic Engine
- **`pr_thermo.py`**: Native implementation of Peng-Robinson cubic equation of state:
  $$P = \frac{RT}{v - b} - \frac{a(T)}{v(v + b) + b(v - b)}$$
  Calculates mixture parameters with binary interaction matrix $k_{ij}$, cubic root-solving for vapor/liquid compressibility factors ($Z_v, Z_l$), enthalpy departure functions, dew/bubble points, and MCHE 100-slice Riemann integral exergy destruction.

### 3.4 `src/models/` — Baselines & Monotonic Surrogate Models
- **`baselines.py`**: Benchmark baseline models (`DummyRegressor`, `Ridge`) to anchor statistical validity before non-linear modeling.
- **`surrogates.py`**: Configures `HistGradientBoostingRegressor` with directional monotonic constraints (`monotonic_cst=[1, 1, 0, 0, 0, 0]`) ensuring physical plausibility.
- **`pipeline.py`**: End-to-end scikit-learn pipeline integrating scaling, feature selection, and model persistence via `joblib`.

### 3.5 `src/evaluation/` — Engineering Unit Metrics & Exergy Verification
- **`metrics.py`**: Computes MAE in MW, normalized MAE ($NMAE = MAE / \bar{y} \times 100\%$), RMSE in MW, coefficient of determination ($R^2$), and compositional closure error.

### 3.6 `src/cli/` & `src/config.py` — Runtime Dispatcher & Typed Configuration
- **`config.py`**: `@dataclass(frozen=True)` schema hierarchy supporting `yaml.safe_load`, environment variable overrides (`MCR_` prefix), and cross-platform path resolution.
- **`cli.py`**: Standard library `argparse` dispatcher supporting `audit`, `verify`, `ingest`, `preprocess`, `train`, `evaluate`, and `predict`.
