# BADAK LNG PLANT-3 TRAIN H — C3MR OPERATOR DECISION-SUPPORT SUITE

A high-integrity, physics-constrained machine learning decision-support website for Badak LNG Plant-3 Train H Mixed Refrigerant (C3MR) cycle.

---

## 1. System Overview & Safety Principles

- **Mode:** **READ-ONLY Decision-Support & What-If Simulation**
- **Strict Plant Protection:** Zero control command write-back to Yokogawa Centum DCS, PLC, or Triconex SIS/ESD. No setpoint modifications.
- **Primary Users:** Control Room Boardmen, Field Operators, Process Engineers, Turbomachinery Specialists.
- **Model Foundation:** `PhysicsResidualSurrogate` (Ridge isentropic work scaling + regularized GBDT residual) trained on 1,475 discrete historical plant shifts ($R^2 = 0.8365$, $\text{MAE} = 0.802\text{ MW}$, $\text{NMAE} = 0.931\%$).
- **Aitchison Compositional Geometry:** 5-component simplex $S^5$ ($N_2, C_1, C_2, C_2H_4, C_3$) via 4D Isometric Log-Ratio (ILR) with Mahalanobis envelope check ($D_M \le 3.0802$).

---

## 2. Directory Structure

```text
operator-website/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── requirements.txt         # Pinned backend dependencies
│   ├── api/
│   │   ├── routes.py            # Read-only REST API endpoints
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── core/
│   │   ├── model_loader.py      # Surrogate model singleton & cache
│   │   ├── feature_builder.py   # 20-feature physics extraction
│   │   ├── validator.py         # Interlocks, bounds & Mahalanobis audit
│   │   └── ilr_engine.py        # 5-component SBP contrast & ILR mapping
│   └── data/
│       └── demo_snapshot.json   # Baseline plant snapshot (DEMO labeled)
├── frontend/
│   ├── package.json             # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx              # Application layout & state coordination
│   │   ├── api.ts               # HTTP client service
│   │   ├── types.ts             # Strongly typed data models
│   │   └── components/
│   │       ├── Header.tsx           # DCS status banner & DEMO indicator
│   │       ├── TabNavigation.tsx    # 3-tab navigation bar
│   │       ├── SpreadsheetTable.tsx # Tab 01: Spreadsheet-style editor
│   │       ├── ResultPanel.tsx      # Tab 01: Power, SEC & safety card
│   │       ├── TabGrafik.tsx        # Tab 02: Power curve, bars & envelope
│   │       └── TabPanduan.tsx       # Tab 03: Bahasa Indonesia operator manual
│   └── dist/                    # Production static build
├── config/
│   └── variable_registry.yaml   # Verified tag, unit & role registry
├── docs/
│   ├── ml_integration_audit.md  # Audit of models, features & targets
│   └── operator_quick_guide.md  # Operator handbook (Bahasa Indonesia)
├── GATES.md                     # Acceptance ledger (7 automated gates)
├── start_backend.bat            # One-click backend launcher
├── start_frontend.bat           # One-click frontend launcher
└── start_app.bat                # Unified dual-process launcher
```

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.10+ (with `numpy`, `scipy`, `scikit-learn`, `fastapi`, `uvicorn`, `joblib`, `pyyaml`, `pandas`)
- Node.js 18+ (for frontend development server or preview)

### Step 1: Start Backend (Port 3001)
```cmd
cd backend
python main.py
```
*Health check URL:* `http://localhost:3001/health`

### Step 2: Start Frontend (Port 5173)
```cmd
cd frontend
npm run dev
```
*Browser URL:* `http://localhost:5173`

---

## 4. Verification Gates Ledger (`GATES.md`)

| Gate | Description | Command | Status |
|---|---|---|---|
| **GATE-01** | Model & Module Import | `python -c "from core.model_loader import ..."` | ✅ PASS (`PhysicsResidualSurrogate`) |
| **GATE-02** | 20-Feature ILR Extraction | `python -c "from core.feature_builder import ..."` | ✅ PASS (`(1, 20) shape`) |
| **GATE-03** | Safety & Domain Audits | `python -c "from core.validator import ..."` | ✅ PASS (Surge violation caught) |
| **GATE-04** | Bound Compliance | `python -c "assert 40.0 <= p <= 150.0"` | ✅ PASS (`84.19 MW`) |
| **GATE-05** | FastAPI Endpoint Integration | `TestClient(app).post('/api/v1/predict')` | ✅ PASS (`200 OK`) |
| **GATE-06** | TypeScript Build | `npm run build` | ✅ PASS (`built in 217ms`) |
| **GATE-07** | Read-Only & Zero Write-Back | Assert 0 control / write routes | ✅ PASS (`ZERO WRITE-BACK ROUTES`) |

---

## 5. Governance & Compliance
All algorithms and calculations strictly comply with `AGENTS.md`:
- **Pasal 1:** Zero magic numbers (all constants sourced from plant datasheets or first-principles).
- **Pasal 2 & 13:** Proportional engineering units (**MW** for compressor power, **mol%** for composition).
- **Pasal 9:** Primary optimization focus on MR composition ($N_2, C_1, C_2, C_2H_4, C_3$) and circulation rate ($H_4FI001$), with recycle valves treated strictly as safety boundaries.
- **Pasal 10:** Transparent power decomposition ($W_{\text{total}} = W_{\text{MCR}} + W_{\text{C3}}$).

