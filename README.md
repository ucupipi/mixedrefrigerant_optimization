# Badak LNG Plant-5 Train H (Liquefaction) C3MR Optimization & Closed-Loop Make-Up Advisory Suite

First-principles Peng-Robinson EOS thermodynamic modeling, leakage-free monotonic machine learning surrogates, multi-strategy SLSQP refrigerant optimization, and closed-loop make-up mass balance decision-support suite for **PT Badak NGL (Bontang, East Kalimantan), Plant-5 Train H (Liquefaction)**.

---

## 1. Repository Architecture & Interconnected Modules

This repository is organized into three interconnected layers so that operators, process engineers, and external open-source contributors have complete traceability from raw plant data governance to live browser decision support:

| Layer | Directory / File | Description | Verification Status |
| :--- | :--- | :--- | :--- |
| **1. Reproducible Contributor Core** | [`MCR_ML_REBUILD/`](MCR_ML_REBUILD/) | Self-contained Python package (`mcr-ml` CLI) excluding legacy assumptions and target-leaked data. Includes shift-level datasets (`master_shift_level.parquet`), SHA-256 manifest auditor, 10-tag leakage firewall, 5-component Aitchison ILR transform, 100-slice MCHE PR-EOS solver, 5C-1 Flash Drum VLE, multi-strategy SLSQP optimizer, and closed-loop make-up calculator. | **46 / 46 Pytest Passed** |
| **2. Operator Decision-Support Web Suite** | [`operator-website/`](operator-website/) | Read-only React 19 + TypeScript + FastAPI + ONNX/PR-EOS hybrid web application with Yokogawa Centum VP PFD mimic (`5E-1`, `5C-1`, `5C-2`, `4K-1/2/3`, `4C-7/8`), explicit strategy selector (`CONDITION_DEPENDENT`, `FIXED_RECIPE`, `MINIMUM_INTERVENTION`), and component make-up advisory cards (`H4FIC006`, `H4FIC005`, `H4FI00C8`, `H4FIC007`). | **198 / 198 Backend Pytest + 26 / 26 Frontend Vitest + 64 / 64 Reviewer Gates Passed** |
| **3. Technical Audit & Strategy Reports** | Root `.md` Documents | Complete mathematical derivations, data-flow root-cause audits, 36-scenario load sensitivity tables ($140 - 340\text{ t/h}$), API contracts, and assumption ledgers. | **0 Em/En-Dashes, 100% Traceable** |

---

## 2. Core Engineering Reports & Documentation Index

1. [`MR_OPTIMIZATION_STRATEGY.md`](MR_OPTIMIZATION_STRATEGY.md): Mathematical formulation and operational comparison of **Strategy A (`FIXED_RECIPE`)**, **Strategy B (`CONDITION_DEPENDENT`)**, and **Strategy C (`MINIMUM_INTERVENTION`)**.
2. [`OPTIMIZER_DATA_FLOW_AUDIT.md`](OPTIMIZER_DATA_FLOW_AUDIT.md): End-to-end forensic trace from React UI state (`App.tsx`) through FastAPI (`main.py`) to `optimizer_engine.py`, proving why legacy MR targets appeared constant and how the 3-strategy architecture resolves it.
3. [`OBJECTIVE_AND_CONSTRAINT_REGISTER.md`](OBJECTIVE_AND_CONSTRAINT_REGISTER.md): Complete register of objective functions, 5D decision variables ($\dot{m}_{\text{MR}}, \xi_1..\xi_4$), turbomachinery anti-surge floor ($\ge 480.0\text{ t/h}$), suction drum TAL ($\ge -45.0^\circ\text{C}$), PR-EOS superheat ($\ge +3.0^\circ\text{C}$), and Mahalanobis boundary ($D_M \le 3.0802$).
4. [`MR_MAKEUP_MASS_BALANCE.md`](MR_MAKEUP_MASS_BALANCE.md): Coupled closed-loop molar dilution mass balance, Badak LNG stream purity matrix $\mathbf{Y}$, dual-unit conversions ($Nm^3/\text{h}$, $kg/\text{h}$, $t/\text{h}$, $scfd$), and `NOT EVALUATED` safety guards.
5. [`LOAD_SENSITIVITY_STUDY.md`](LOAD_SENSITIVITY_STUDY.md): 36-scenario empirical sensitivity study across $140.0 - 340.0\text{ t/h}$ MCHE feed gas load (backed by [`operator-website/backend/data/load_sensitivity_study.csv`](operator-website/backend/data/load_sensitivity_study.csv)).
6. [`API_SCENARIO_CONTRACT.md`](API_SCENARIO_CONTRACT.md): Request/response JSON schemas, unit conventions, and error contracts for all FastAPI endpoints.
7. [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md): Epistemic boundaries, steady-state vs transient limits, and hardware safety interlocks.
8. [`PHASE_3_FINAL_VERIFICATION_REPORT.md`](PHASE_3_FINAL_VERIFICATION_REPORT.md): Master verification ledger summarizing all 270+ automated test gates.
9. [`MCR_ML_REBUILD/docs/assumption_register.md`](MCR_ML_REBUILD/docs/assumption_register.md): 64-entry forensic Assumption Register classifying every project assumption into `REJECTED` (20), `VERIFIED` (26), `USER_CONFIRMED` (7), `HYPOTHESIS` (5), and `UNKNOWN` (6).
10. [`PROJECT.md`](PROJECT.md): System architecture, canonical 170-tag DCS dictionary summary, and Teluk Bontang once-through seawater cooling ($T_{CW,\text{in}} = 30.0^\circ\text{C}$) specification.

---

## 3. Quick Start Guide for Contributors & Reviewers

### 3.1 Run the Reproducible Contributor Suite (`MCR_ML_REBUILD/`)
All shift-level datasets (`master_shift_level.parquet`), unleaked feature matrices, and trained model artifacts are tracked directly in Git so contributors can run all pipelines and tests immediately after cloning:
```bash
# Run all 46 tests in MCR_ML_REBUILD
python -m pytest MCR_ML_REBUILD/tests/ -v

# Run CLI multi-strategy optimization & closed-loop make-up balance
python -m MCR_ML_REBUILD.src.cli optimize --feed-flow 245.8 --strategy CONDITION_DEPENDENT
python -m MCR_ML_REBUILD.src.cli makeup --inventory-kg 24000.0 --transition-hours 8.0
```

### 3.2 Run the Operator Decision-Support Web Application (`operator-website/`)
```bash
# 1. Run backend test suite (198 tests) and start FastAPI server on port 8000
python -m pytest operator-website/backend/tests/ -v
cd operator-website/backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Run frontend test suite (26 Vitest tests) and build production bundle
cd operator-website/frontend
npm test
npm run build
```

---

## 4. Constitutional Governance & Non-Negotiable Rules

1. **Read-Only Advisory Boundary**: Never write setpoints or commands to DCS, SIS, PLC, or field equipment.
2. **Zero Magic Numbers & Zero Fake Regression (`AGENTS.md` Pasal 1-2)**: Every thermodynamic parameter and ML surrogate is grounded in Peng-Robinson EOS or chronologically split Badak LNG telemetry ($R^2_{\text{test}} = 0.9964$, $\text{MAE} = 0.098\text{ MW} < 1.0\text{ MW}$, $\text{NMAE} = 0.351\% < 1.0\%$).
3. **Primary Decision Variables (`AGENTS.md` Pasal 9)**: Mixed Refrigerant 5-component composition ($N_2, C_1, C_2, C_2H_4, C_3$) and MCR circulation flow ($\dot{m}_{\text{MR}}$) are the primary optimization variables; kickback valve `4UV-53` and suction reheat valve `4TV-510` act strictly as turbomachinery safety boundary enablers.
4. **Transparent Power Decomposition (`AGENTS.md` Pasal 10)**: Total Train H C3MR shaft power savings ($28{,}983.3\text{ kW}$, $-27.10\%$) are transparently decomposed into direct MCR compression savings (`4K-2/3`: $10{,}826.1\text{ kW}$, $-13.85\%$) and coupled propane precooling savings (`4K-1`: $18{,}145.7\text{ kW}$, $-34.80\%$).
