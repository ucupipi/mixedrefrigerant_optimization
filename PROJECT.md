# Project: Plant-3 OTS Operator Website Refactor & C3MR VLE Optimization

## Architecture
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS (`operator-website/frontend/`)
  - DCS Mimic: SVG Yokogawa Centum VP replica (`TabGrafik.tsx`)
  - Operator Dashboard: KPI chips, TabInputResults, SpreadsheetTable, ResultPanel, TopNavbar
- **Backend**: FastAPI + Python 3.10+ (`operator-website/backend/`)
  - Thermodynamics Engine: 7-component Peng-Robinson EOS VLE Flash (`src/thermo/flash_drum_vle.py`)
  - ML Surrogate & Optimizer: Ridge + GBDT with Monotonic Constraints (`core/optimizer_engine.py`)
  - API Routes: `/api/v1/predict`, `/api/v1/status`, `/api/v1/stream-composition` (`api/routes.py`)
- **Deployment**: Vercel Serverless Multi-Service + Synchronized Static Assets (`backend/static/`)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Unified Centum VP Header | Consolidate 2 stacked headers into a single responsive 42px Centum VP window bar in `TabGrafik.tsx` | M1 | R1 Survey |
| 2 | Refrigeration Stream Disambiguation | Distinctly display and label MCR Liquid (`FIC2`), MCR Vapor (`H5TI0047`), Total MCR (`H4FI011B`), and Propane Precooling (`4K-1` / `H4FI001A` + chillers) | M1 | R1 Survey |
| 3 | Scenario Disturbance Clarification | Clarify Feed Gas Flow (`H1FI012`) as "Input Skenario / Beban Tetap" and relabel "Target AI" table heading | M1 | R2 Survey |
| 4 | UI Unslop De-AI Rewriting | Replace academic/AI titles, robotic tags ("AI -152.0°C"), and buzzwords ("Value Creation") across UI | M1 | Follow-up Survey |
| 5 | Rigorous 5C-1 VLE PR-EOS Engine | 7-component PR-EOS flash thermodynamic engine replacing static `0.9450` multiplier | M2 | R3 Survey |
| 6 | 5C-1 Flash Physical Equilibrium Parity | Match 141.80 t/h liquid at 150.0 t/h feed and ~ -157.8°C bubble point matching DCS H5TI0041 | M2 | R3 Survey |
| 7 | Full Codebase Magic Number Elimination | Audit and eliminate all 18 occurrences of `* 0.9450`, arbitrary economic multipliers, and uncalibrated constants | M3 | R4 Survey |
| 8 | First-Principles Compressor Scaling | Replace heuristic speed exponent in `optimizer_engine.py` with physical affinity laws | M3 | R4 Survey |
| 9 | Backend Routes Unslop Update | Replace "SKENARIO WHAT-IF (HASIL MODEL ML)" with "SIMULASI SKENARIO WHAT-IF" in `routes.py` | M3 | Follow-up Survey |
| 10 | Frontend Build Pipeline Verification | Compile TypeScript frontend with zero errors (`npm run build`) | M4 | R5 Survey |
| 11 | Backend Pytest Verification | Pass 100% of backend tests (`pytest operator-website/backend/tests`) with new VLE flash tests | M4 | R5 Survey |
| 12 | Static Asset Synchronization | Synchronize frontend `dist/` bundle to `operator-website/backend/static/` | M4 | R5 Survey |
| 13 | Remote Deployment Live Verification | Verify live operation and status at `https://mixedrefrigerantoptimization.vercel.app/` | M4 | R5 Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: PFD Header Consolidation & UI Stream Clarification | TabGrafik.tsx header consolidation, stream disambiguation, scenario input labels, UI unslop | none | DONE (Verified: Centum VP 42px header, stream disambiguation, unslop, npm build exit 0) |
| 2 | M2: 5C-1 Flash Drum Rigorous PR-EOS Thermodynamics | 7-component PR-EOS flash engine, backend integration, frontend thermo parity, physical 141.8 t/h validation | none | DONE (Verified: 141.79 t/h @ 150 t/h feed, -157.90°C bubble point, 82/82 pytest green) |
| 3 | M3: Codebase-wide Magic Number & Heuristic Elimination | Eradicate all static `* 0.9450`, economic constants, hardcoded FIC2, compressor speed exponent, backend unslop | M2 | PLANNED |
| 4 | M4: Test Suite Verification, Static Sync & Live Deployment | Frontend build, backend pytest, static asset sync, remote deployment verification | M1, M2, M3 | PLANNED |

## Interface Contracts
### 5C-1 Flash Drum VLE Contract: Backend ↔ Frontend
- **Module**: `operator-website/backend/src/thermo/flash_drum_vle.py`
- **Function**: `calculate_flash_drum_5c1(feed_flow_t_h: float, T_mche_exit_C: float = -152.0, P_drop_kg_cm2: float = 0.40, composition: Optional[Dict[str, float]] = None) -> FlashDrumResult`
- **Output Schema**:
  ```python
  class FlashDrumResult(BaseModel):
      feed_mass_flow_t_h: float
      lng_liquid_flow_t_h: float
      end_flash_gas_flow_t_h: float
      liquid_mass_yield_pct: float
      vapor_mol_fraction: float
      flash_temperature_C: float
      flash_pressure_bara: float
      liquid_composition_mol_pct: Dict[str, float]
      vapor_composition_mol_pct: Dict[str, float]
      status: str  # e.g., "VALID_PR_EOS_VLE"
  ```
- **Thermodynamic Ground Truth**:
  - Feed: 150.0 t/h treated gas
  - Conditions: MCHE outlet -152.0°C to -153.8°C, P_flash = 0.30 kg/cm²G
  - Liquid yield: 94.533 wt% -> 141.80 t/h LNG rundown (tolerance ±0.5 t/h)
  - Flash temperature: -157.7°C to -157.9°C (matching DCS H5TI0041 = -158.1°C)

## Code Layout
- Frontend UI: `operator-website/frontend/src/components/`
  - `TabGrafik.tsx`: Unified Centum VP header, PFD SVG, refrigeration stream tags
  - `TabInputResults.tsx`: Scenario disturbance labels, table headings, economic formulas
  - `TopNavbar.tsx`: Plant title unslop
  - `ResultPanel.tsx`: Recommendation wording unslop
  - `ExcelWorkbookView.tsx`: Dynamic flash calculation binding
  - `App.tsx`: Global state, scenario synchronization, CSV export
- Backend Python: `operator-website/backend/`
  - `src/thermo/flash_drum_vle.py`: 7-component PR-EOS flash engine
  - `api/routes.py`: FastAPI endpoints, prediction handlers, unslop labels
  - `core/optimizer_engine.py`: ML surrogate & physical compressor affinity scaling
  - `tests/test_calculations.py`: Pytest suite for VLE thermodynamics and mass balances
- Static Assets: `operator-website/backend/static/`
