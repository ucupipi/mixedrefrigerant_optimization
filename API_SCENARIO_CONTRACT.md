# BADAK LNG PLANT-5 TRAIN H : API SCENARIO CONTRACT
## Formal Interface Specifications, JSON Schemas & Concurrency Architecture

**Document Classification:** Software Engineering & Systems Integration Contract  
**Facility Scope:** PT Badak NGL, Plant-5 Train H (Liquefaction)  
**System Designation:** C3MR Decision-Support Suite Backend API  
**Operating Boundary:** Open-Loop Advisory Decision Support (Read-Only : Zero Direct DCS Actuation)  
**Governing Standard:** AGENTS.md (Hukum Anti-Dosa Rekayasa Mutlak)  

---

## 1. Executive Summary & Communication Architecture

The Badak LNG Plant-5 Train H decision-support backend exposes a high-performance RESTful API constructed with FastAPI. The API communicates with the React frontend through validated JSON contracts, enforcing schema conformity, input sanity bounds, and thermodynamic physical constraints.

### Air-Gapped Network Topology
```
[ Yokogawa Centum VP DCS / Field Sensors ]
                  |
         (Read-Only OPC-UA)
                  v
[ Industrial Data Gateway / Historian ]
                  |
         (Encrypted Read Feed)
                  v
[ Train H Decision-Support Backend (FastAPI) ] <--- READ-ONLY ADVISORY BOUNDARY
                  ^
         (REST / JSON API)
                  v
[ Operator Web UI (React + TypeScript) ]
```

---

## 2. Endpoint Specifications

### 2.1 Optimization Advisory: `POST /api/v1/optimize`

Solves for optimal mixed refrigerant composition and circulation rate under the requested operating strategy.

#### Request JSON Schema (`OptimizeRequest`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OptimizeRequest",
  "type": "object",
  "required": ["feed_flow_t_h"],
  "properties": {
    "feed_flow_t_h": {
      "type": "number",
      "minimum": 50.0,
      "maximum": 1000.0,
      "description": "Treated feed gas flow rate to MCHE 5E-1 in metric tons per hour [t/h]"
    },
    "strategy": {
      "type": "string",
      "enum": ["CONDITION_DEPENDENT", "FIXED_RECIPE", "MINIMUM_INTERVENTION"],
      "default": "CONDITION_DEPENDENT",
      "description": "Operating strategy selection governing decision space and recipe adaptability"
    },
    "alpha_trim": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.30,
      "description": "Step-size weighting parameter for Strategy C (MINIMUM_INTERVENTION)"
    },
    "actual_mcr_flow_t_h": {
      "type": "number",
      "minimum": 300.0,
      "maximum": 1000.0,
      "description": "Current DCS actual MCR circulation flow rate [t/h]"
    },
    "actual_comp_N2_molpct": { "type": "number", "minimum": 0.0, "maximum": 20.0 },
    "actual_comp_C1_molpct": { "type": "number", "minimum": 10.0, "maximum": 80.0 },
    "actual_comp_C2_molpct": { "type": "number", "minimum": 10.0, "maximum": 80.0 },
    "actual_comp_C2H4_molpct": { "type": "number", "minimum": 0.0, "maximum": 20.0 },
    "actual_comp_C3_molpct": { "type": "number", "minimum": 0.0, "maximum": 30.0 }
  }
}
```

#### Response JSON Schema (`OptimizeResponse`)
```json
{
  "feed_t_h": 245.8,
  "mcr_flow_t_h": 523.0,
  "comp_N2_molpct": 3.31,
  "comp_C1_molpct": 46.08,
  "comp_C2_molpct": 45.15,
  "comp_C2H4_molpct": 0.05,
  "comp_C3_molpct": 5.41,
  "mahalanobis_distance": 0.858,
  "expected_suction_temp_c": -38.8,
  "suction_tal_ok": true,
  "antisurge_floor_applied": false,
  "envelope_shrink_applied": false,
  "extrapolated": false,
  "feed_span_t_h": [141.2, 296.4],
  "source": "Live SLSQP Solver (PR-EOS + GBRT Surrogate)",
  "solver_converged": true,
  "strategy": "CONDITION_DEPENDENT",
  "effective_inputs": {
    "feed_flow_t_h": 245.8,
    "strategy": "CONDITION_DEPENDENT",
    "alpha_trim": 0.30
  },
  "constraint_residuals": {
    "antisurge_margin_t_h": 43.0,
    "suction_tal_margin_c": 6.2,
    "superheat_margin_c": 20.76,
    "mahalanobis_margin": 2.222
  },
  "explanation": "Strategy B (Condition-Dependent): Full 5-dimensional optimization active for feed 245.8 t/h. MCR composition and circulation dynamically minimize specific shaft power while satisfying all safety boundaries."
}
```

---

### 2.2 Performance & Safety Evaluation: `POST /api/v1/predict`

Evaluates compressor shaft power, specific energy consumption (SEC), thermodynamic envelopes, and make-up injection schedules for a complete operator scenario.

#### Request JSON Schema (`PredictRequest`)
Accepts the full 5-tier parameter set, including `feed_flow_t_h`, `mcr_flow_t_h`, 5-component scenario mole percentages, actual DCS state, and `transition_hours` (default 2.0 h).

#### Response Payload Fields (`PredictResponse`)
- `prediction.total_shaft_power_mw`: Total Train C3MR compressor shaft work ($MW$).
- `prediction.power_mcr_mw`: MCR compressor (4K-2/3) shaft work ($MW$).
- `prediction.power_c3_mw`: Propane compressor (4K-1) shaft work ($MW$).
- `prediction.sec_lng_kwh_per_t`: Specific Energy Consumption per metric ton of LNG produced ($kWh/\text{t LNG}$).
- `prediction.capacity_warning`: Flagged string if feed $> 296.4\text{ t/h}$.
- `domain_check.mahalanobis_distance`: Statistical distance from historical centroid.
- `safety_check.all_safe`: Boolean summary of physical safety.
- `makeup_advisory`: Component-resolved make-up injection schedule with dual units ($Nm^3/\text{h}$ and $kg/\text{h}$).

---

### 2.3 System Telemetry & Model Readiness: `GET /api/v1/status`

Returns runtime health and machine learning model validation status.

#### Response Example
```json
{
  "status": "HEALTHY",
  "facility": "Badak LNG Plant-5 Train H",
  "advisory_mode": "READ_ONLY",
  "model_loaded": true,
  "model_r2": 0.985,
  "model_mae_mw": 0.802,
  "active_features": 20,
  "timestamp": "2026-11-07T14:30:00Z"
}
```

---

## 3. Concurrency & Race Condition Guards

To protect against race conditions caused by rapid UI changes:
1. **Frontend AbortController:** Every new scenario dispatch calls `.abort()` on the previous in-flight HTTP request.
2. **Stateless Solver Isolation:** The FastAPI calculation routines maintain zero shared mutable state between concurrent requests, ensuring 100% thread safety and deterministic outputs.
3. **HTTP 422 Client Validation:** Payloads failing structural or boundary checks are rejected with descriptive JSON error structures, preventing backend solver exceptions.
