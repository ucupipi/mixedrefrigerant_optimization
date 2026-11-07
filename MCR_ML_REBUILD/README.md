# Badak LNG Plant-5 Train H (Liquefaction) C3MR Machine Learning & Multi-Strategy Optimization Suite (`MCR_ML_REBUILD`)

Reproducible, first-principles machine learning, thermodynamic equilibrium, multi-strategy SLSQP optimization, and closed-loop make-up mass balance contributor package for the Propane-Precooled Mixed Refrigerant (C3MR) liquefaction cycle at **PT Badak NGL (Bontang, East Kalimantan), Plant-5 Train H (Liquefaction)**.

---

## 1. Purpose & Interconnected Repository Architecture

This folder (`MCR_ML_REBUILD/`) serves as the **self-contained, reproducible scientific and engineering core** for external contributors, reviewers, and process engineers. It explicitly isolates and rejects legacy assumptions, magic numbers, and target-leaked features (documented in [`docs/assumption_register.md`](docs/assumption_register.md) and enforced by [`src/data/governance.py`](src/data/governance.py)) while interconnecting directly with the production web application and root technical reports:

1. **Reproducible Contributor Core (`MCR_ML_REBUILD/`)**:
   - **Data Governance & Leakage Firewall (`src/data/`)**: Cryptographic SHA-256 manifest verification (`data/sha256_manifest.json`), discrete 8-hour shift alignment (`data/processed/master_shift_level.parquet`, $N = 1{,}475$ shifts), and strict quarantine of 10 downstream target-reconstructing tags.
   - **Compositional Simplex & Physics Features (`src/features/`)**: 5-component ($N_2, C_1, C_2, C_2H_4, C_3$) Aitchison Sequential Binary Partition (SBP) Isometric Log-Ratio ($\text{ILR}: \mathcal{S}^5 \to \mathbb{R}^4$) transformation, Mahalanobis confidence ellipsoid screening ($D_M \le 3.0802$), MCHE bundle $\Delta P$, and once-through seawater cooling ($T_{CW} = 30.0^\circ\text{C}$).
   - **First-Principles Thermodynamics (`src/thermo/`)**: Pure-Python Peng-Robinson EOS (1976) with 100-slice MCHE pinch profiling ($\text{MITA} \ge 1.50^\circ\text{C}$), Riemann exergy integration, and 7-component PR-EOS 5C-1 Flash Drum letdown VLE (`src/thermo/flash_drum_vle.py`).
   - **Multi-Strategy SLSQP Optimizer & Closed-Loop Make-Up (`src/core/`)**: Interconnected directly with `operator-website/backend/core/`, providing `CONDITION_DEPENDENT` (5D active SLSQP), `FIXED_RECIPE` (1D circulation search), and `MINIMUM_INTERVENTION` (5D proximity-penalized SLSQP) modes (`src/core/optimizer_engine.py`) alongside the closed-loop inventory dilution make-up calculator (`src/core/makeup_calculator.py`).
2. **Operator Decision-Support Web Suite (`../operator-website/`)**:
   - Full-stack React 19 + TypeScript + FastAPI + ONNX/PR-EOS hybrid advisory application consuming the models and engines built in `MCR_ML_REBUILD/`.
   - Strict **Read-Only Advisory Boundary**: Zero write paths to Yokogawa Centum VP DCS, SIS, PLC, or field control valves.
3. **Root Engineering Audit & Strategy Reports (`../`)**:
   - [`../MR_OPTIMIZATION_STRATEGY.md`](../MR_OPTIMIZATION_STRATEGY.md): Formulation of Strategy A (`FIXED_RECIPE`), Strategy B (`CONDITION_DEPENDENT`), and Strategy C (`MINIMUM_INTERVENTION`).
   - [`../OPTIMIZER_DATA_FLOW_AUDIT.md`](../OPTIMIZER_DATA_FLOW_AUDIT.md): Root-cause trace of why legacy MR targets appeared static and how the multi-strategy architecture resolves it.
   - [`../OBJECTIVE_AND_CONSTRAINT_REGISTER.md`](../OBJECTIVE_AND_CONSTRAINT_REGISTER.md): Complete mathematical register of objectives, decision variables, and safety constraints.
   - [`../MR_MAKEUP_MASS_BALANCE.md`](../MR_MAKEUP_MASS_BALANCE.md): Derivation of the coupled closed-loop molar dilution balance and Badak LNG header purity matrix $\mathbf{Y}$.
   - [`../LOAD_SENSITIVITY_STUDY.md`](../LOAD_SENSITIVITY_STUDY.md): 36-scenario sensitivity sweep across $140.0 - 340.0\text{ t/h}$ feed gas load.
   - [`../API_SCENARIO_CONTRACT.md`](../API_SCENARIO_CONTRACT.md), [`../KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md), and [`../PHASE_3_FINAL_VERIFICATION_REPORT.md`](../PHASE_3_FINAL_VERIFICATION_REPORT.md).

---

## 2. What Data is Tracked in Git for Contributors

To comply with GitHub file size limits while guaranteeing 100% out-of-the-box reproducibility for contributors:
- **Included in Git (`MCR_ML_REBUILD/data/` & `models/`)**:
  - `data/processed/master_shift_level.parquet` ($3.45\text{ MB}$, $1{,}475$ real plant shifts across 2023-2026)
  - `data/processed/features_unleakaged.parquet` & `target_energy.parquet`
  - `data/processed/baseline_definitive_complete.csv`, `optimization_results_7quantiles.csv`, & `load_sensitivity_study.csv`
  - `data/interim/composition_all_periods_corrected.parquet` ($2{,}531$ shift GC analyses)
  - `data/sha256_manifest.json` (cryptographic audit ledger of all 26 raw and processed assets)
  - `models/c3mr_power_surrogate_real.joblib`, `c3mr_power_surrogate.joblib`, `surrogate_total_steam_t_h.joblib`, `surrogate_H4TI004B.joblib`, & `mcr_ilr_envelope.joblib`
- **Excluded from Git (`>25 MB` Raw/Minute Archives)**:
  - Raw Excel historian exports (`ProcessParameter_*.xlsx`, $88 - 191\text{ MB}$) and 1-minute unaggregated Parquet files (`master_minute_level.parquet`, $246.9\text{ MB}$) are excluded via `.gitignore` and verified in reference mode via `data/sha256_manifest.json`. All training, evaluation, optimization, and unit tests run directly from the tracked shift-level Parquet and CSV files.

---

## 3. Quick Start & CLI Usage

### 3.1 Environment Setup
```bash
cd MCR_ML_REBUILD
pip install -e .
```

### 3.2 Run Full Automated Test Suite (46 Tests)
```bash
python -m pytest tests/ -v
```

### 3.3 Run Multi-Strategy SLSQP Optimization via CLI
```bash
# Strategy B: Condition-Dependent 5D Optimization
python -m src.cli optimize --feed-flow 245.8 --strategy CONDITION_DEPENDENT

# Strategy A: Fixed Recipe Across Loads (1D Circulation Optimization)
python -m src.cli optimize --feed-flow 245.8 --strategy FIXED_RECIPE

# Strategy C: Minimum-Intervention Optimization (Proximity-Penalized)
python -m src.cli optimize --feed-flow 245.8 --strategy MINIMUM_INTERVENTION --alpha-trim 0.30
```

### 3.4 Run Closed-Loop Make-Up Mass Balance via CLI
```bash
python -m src.cli makeup --actual 3.39 44.45 45.02 0.85 6.29 --target 3.77 42.22 43.67 1.53 8.82 --inventory-kg 24000.0 --transition-hours 8.0
```

### 3.5 Run Data Audit, Leakage Firewall, Training, & HYSYS Parity
```bash
python -m src.cli audit
python -m src.cli verify --gate all
python -m src.cli train --data-source real --model-type all
python -m src.cli evaluate --data-source real
python -m src.cli hysys-parity
```

---

## 4. Directory Structure

```text
MCR_ML_REBUILD/
├── configs/
│   ├── default.yaml                  # Master hyperparameters, physical bounds, and tag lists
│   └── logging.yaml                  # Structured logging configuration
├── data/
│   ├── sha256_manifest.json          # Cryptographic SHA-256 manifest of all 26 data assets
│   ├── interim/                      # Tracked shift-level GC composition parquets
│   └── processed/                    # Tracked master_shift_level.parquet & Pareto CSVs
├── docs/
│   ├── assumption_register.md        # 64-entry forensic Assumption Register (ASM-REJ/VER/USR/HYP/UNK)
│   ├── model_card.md                 # Model governance, operating domain, and limitations
│   └── hysys_stream_deck.md          # Aspen HYSYS stream input deck & PR-EOS parity documentation
├── models/                           # Serialized monotonic GBRT surrogates and ILR covariance envelope
├── reports/                          # JSON evaluation metrics, evolution history, and HYSYS parity
├── src/
│   ├── cli.py & cli/commands.py      # Unified CLI (audit, verify, train, optimize, makeup, hysys-parity)
│   ├── core/                         # Multi-strategy SLSQP optimizer, closed-loop make-up, safety validator
│   ├── data/                         # SHA-256 manifest auditor, ingestion, 10-tag leakage firewall
│   ├── features/                     # 5-component SBP ILR geometry, Mahalanobis D_M, MCHE dP features
│   ├── models/                       # Monotonic HistGradientBoostingRegressor & Ridge baselines
│   ├── thermo/                       # Pure-Python PR-EOS (100-slice MCHE pinch & 5C-1 Flash Drum VLE)
│   └── agents/                       # A-Evolve surrogate evolver & 3-agent C3MR advisory crew
└── tests/                            # 46 unit, thermodynamic, leakage-firewall, and integration tests
```
