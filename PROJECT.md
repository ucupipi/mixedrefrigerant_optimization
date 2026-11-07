# Project: Badak NGL Plant-5 OTS Standalone Web & Cooling Seawater Hybrid C3MR Optimization

## Architecture
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS (`operator-website/frontend/`)
  - Standalone Client-Side Architecture: Fully functional in browser (Vercel) without external backend API dependency
  - Hybrid Inference Engine: `hybridSurrogate.ts` attempting ONNX Runtime Web with automatic fallback to pure TypeScript physics engine `physicsEngine.ts`
  - Thermodynamics Engine: `thermoFlash.ts` (PR-EOS 5C-1 Flash Drum VLE phase split, 5C-2 MCR separator phase split)
  - Cooling Seawater Model: Teluk Bontang sea water inlet temperature T_CW = 30.0 C internal parameter governing propane condenser 3E-10 and chillers 3E-14/17/18
  - Operator UI: DCS replica `TabGrafik.tsx`, `TabInputResults.tsx`, `ExcelWorkbookView.tsx`, `SpreadsheetTable.tsx`, `ResultPanel.tsx`, `TopNavbar.tsx`
- **Backend & Verification Suite**:
  - Test Suite: 24 unit tests in `operator-website/backend/tests/` (13 in `test_calculations.py`, 11 in `test_ui_empirical.py`)
  - Verification: `npm test` in frontend executes and validates all 24 unit tests

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Internal Cooling Seawater T_CW = 30.0 C | Internal model parameter T_CW = 30.0 C without operator slider, driving P_sat = 14.164 kg/cm2A and T_cond = 40.5 C | M1 | R1 Survey |
| 2 | Chiller & Condenser Thermodynamics | Physical modeling of propane chillers 3E-14/17/18 and condenser 3E-10 duties and LMTD | M1 | R1 Survey |
| 3 | Read-only T_CW Display in UI | Display T_CW = 30.0 C and chiller duties in ExcelWorkbookView without adding interactive sliders | M1 | R1 Survey |
| 4 | Bundled Default Snapshot Data | Static offline snapshot data in `src/data/defaultSnapshot.ts` ensuring zero-dependency initial load | M2 | R2 Survey |
| 5 | Pure TypeScript Physics Engine | First-principles feature builder (20 features), ILR geometry, Mahalanobis D_M <= 3.0802, DCS quantile baseline, exact Ridge surrogate | M2 | R2 Survey |
| 6 | Hybrid ONNX Runtime Web with TS Fallback | Hybrid inference wrapper in `src/utils/hybridSurrogate.ts` that tries ONNX then silently falls back to TS physics | M2 | R2 Survey |
| 7 | Standalone Client-Side API Adapter | Seamless fallback in `src/api.ts` so `predictScenario` and `fetchDemoSnapshot` work 100% offline | M2 | R2 Survey |
| 8 | Em-Dash and En-Dash Elimination | Eradicate all 74 Unicode em-dash (U+2014) and en-dash (U+2013) in frontend and 1 in backend test | M3 | R3 Survey |
| 9 | Frontend npm test Script Integration | Add `"test"` script to `operator-website/frontend/package.json` that runs 24/24 unit tests green | M3 | R3 Survey |
| 10 | Strict AGENTS.md & Plant-5 Alignment | Zero magic numbers, verify Afdal as Process Control Engineer, Plant-5 Train H terminology | M3 | R3 Survey |
| 11 | Production Build & Lint Pass | `npm run build` exit code 0 and `npm run lint` clean pass without errors | M3 | R3 Survey |
| 12 | Final Gate Verification | Full review, adversarial challenge, and forensic audit of all acceptance criteria | M4 | Final Gate |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Cooling Seawater T_CW & Chiller/Condenser Integration | Implement internal parameter T_CW = 30.0 C in types.ts, thermoFlash.ts, and ExcelWorkbookView.tsx without UI slider | none | DONE (Gate PASS: T_CW=30.0C internal, 3E-10/14/17/18 duties, read-only UI, 24/24 tests green) |
| 2 | M2: Client-Side Standalone Hybrid ONNX & TypeScript Physics Engine | Implement physicsEngine.ts, hybridSurrogate.ts, defaultSnapshot.ts, and wire api.ts for 100% standalone Vercel operation | M1 | DONE (Gate PASS: standalone offline fallback, exact 20-feat Ridge, hybrid ONNX, 24/24 tests green) |
| 3 | M3: Em/En-Dash Sanitization, Frontend npm test, and Build Verification | Sanitize 75 dash violations, add npm test script (24/24 tests green), verify npm run build exit 0, AGENTS.md compliance | M1, M2 | DONE (Gate PASS: npm test exit 0, 24/24 green, 0 em/en-dashes, Plant-5 consistency) |
| 4 | M4: Final Review, Adversarial Challenge, and Forensic Audit | Independent reviewer, challenger stress testing, and forensic auditor integrity verification | M1, M2, M3 | DONE (Gate PASS: 100% criteria verified, CLEAN audit verdict) |

## Interface Contracts
### 1. Cooling Seawater & Chiller Contract
- **Module**: `operator-website/frontend/src/utils/thermoFlash.ts`
- **Constant**: `DEFAULT_COOLING_WATER = { T_CW_in_C: 30.0, delta_T_CW_C: 5.0, T_CW_out_C: 35.0, approach_C: 5.5, T_cond_C: 40.5, p_c3_disch_kgcm2a: 14.164 }`
- **Output Types**:
  ```typescript
  export interface ChillerDutyResult {
    q_high_stage_mw: number;   // 3E-14 (+18 C)
    q_med_stage_mw: number;    // 3E-17 (-10 C)
    q_low_stage_mw: number;    // 3E-18 (-35 C)
    q_total_precooling_mw: number;
    q_propane_condenser_mw: number; // 3E-10
    lmtd_condenser_c: number;
  }
  ```

### 2. Standalone Client-Side Prediction Contract
- **Module**: `operator-website/frontend/src/utils/physicsEngine.ts` and `src/api.ts`
- **Function**: `computeClientPrediction(scenario: ScenarioInput, actualDcs?: Partial<ScenarioInput>): PredictResponse`
- **Behavior**:
  - Matches exact return schema of `/api/v1/predict`
  - Evaluates 20 standardized features matching `feature_builder.py`
  - Evaluates Ridge surrogate with intercept `90.165461 MW` and exact trained coefficients
  - Evaluates DCS 7-quantile baseline power for Plant-5 Train H
  - Evaluates 5C-1 Flash letdown via `calculateFlashDrum5C1`
  - Evaluates safety interlocks (TAL -45 C, Anti-surge 480 t/h, MITA pinch >= 1.5 C)
  - Evaluates make-up injection advisory for N2, C1, C2, C3

## Code Layout
- Frontend: `operator-website/frontend/`
  - `src/utils/thermoFlash.ts`: 5C-1 flash drum, 5C-2 MCR phase split, cooling seawater thermodynamics
  - `src/utils/physicsEngine.ts`: Pure TypeScript first-principles physics surrogate & feature builder
  - `src/utils/hybridSurrogate.ts`: Hybrid ONNX Runtime Web loader with automatic physics fallback
  - `src/data/defaultSnapshot.ts`: Bundled plant baseline snapshot data for standalone offline initialization
  - `src/api.ts`: API client with transparent standalone client-side execution fallback
  - `src/components/ExcelWorkbookView.tsx`: Workbook view showing T_CW = 30.0 C and chiller duties (read-only)
  - `src/components/TopNavbar.tsx`: Author roster with Afdal as Process Control Engineer
  - `src/components/TabGrafik.tsx`: DCS mimic layout
  - `package.json`: Build and test scripts
- Tests: `operator-website/backend/tests/`
  - `test_calculations.py`: 13 engineering calculation unit tests
  - `test_ui_empirical.py`: 11 UI empirical unit tests
