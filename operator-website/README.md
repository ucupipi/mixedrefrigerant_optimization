# Baseload LNG Plant-5 Train H (Liquefaction) C3MR Operator Decision-Support & Make-Up Advisory Suite

Read-only operator decision-support and engineering scenario analysis web application for the Propane-Precooled Mixed Refrigerant (C3MR) liquefaction process at **Baseload LNG Facility, Plant-5 Train H (Liquefaction)**.

---

## 1. Operating Boundary & Safety Invariants

- **Advisory Mode Only**: This software is strictly a read-only operator decision-support and engineering scenario tool. It contains zero network drivers, OPC-UA write clients, Modbus coils, or communication paths capable of writing setpoints or commands to the Yokogawa Centum VP DCS, SIS, PLC, or field control valves (`4UV-53`, `4TV-510`, `H4FIC006`, `H4FIC005`, `H4FI00C8`, `H4FIC007`).
- **Interconnected with `MCR_ML_REBUILD/`**: Consumes the leakage-free monotonic surrogate models (`c3mr_power_surrogate_real.joblib`, `surrogate_total_steam_t_h.joblib`, `surrogate_H4TI004B.joblib`), Aitchison ILR covariance envelope (`mcr_ilr_envelope.joblib`), pure-Python Peng-Robinson EOS (`flash_drum_vle.py`, `pr_thermo.py`), and assumption guardrails established in [`../MCR_ML_REBUILD/`](../MCR_ML_REBUILD/).
- **Once-Through Seawater Cooling**: All propane condensers (`3E-10`), compressor intercoolers/aftercoolers (`4E-5`, `4E-6`), and steam surface condensers operate with once-through seawater cooling ($T_{CW,\text{in}} = 30.0^\circ\text{C}$, $T_{\text{cond}} = 40.5^\circ\text{C}$, $P_{\text{C3,disch}} = 14.164\text{ kg/cm}^2\text{A}$).

---

## 2. Core Engineering Capabilities

1. **Explicit Multi-Strategy C3MR Optimization (`backend/core/optimizer_engine.py`)**:
   - **Strategy B (`CONDITION_DEPENDENT`)**: Active 5D SLSQP optimization ($\dot{m}_{\text{MR}}, \xi_1, \xi_2, \xi_3, \xi_4$) minimizing total turbine steam consumption subject to suction drum TAL ($T_{\text{suct}} \ge -45.0^\circ\text{C}$), PR-EOS dew-point superheat ($\Delta T_{\text{sh}} \ge 3.0^\circ\text{C}$), compressor anti-surge floor ($\dot{m}_{\text{MR}} \ge 480.0\text{ t/h}$), and Mahalanobis ellipsoid ($D_M \le 3.0802$) with zero proximity anchoring ($w_{\text{prox}} = 0$).
   - **Strategy A (`FIXED_RECIPE`)**: 1D SLSQP circulation optimization holding MR composition constant at the certified invariant recipe ($3.77\%\text{ N}_2$, $42.22\%\text{ C}_1$, $43.67\%\text{ C}_2$, $1.53\%\text{ C}_2\text{H}_4$, $8.82\%\text{ C}_3$) across load variations.
   - **Strategy C (`MINIMUM_INTERVENTION`)**: 5D SLSQP optimization penalizing squared Aitchison ILR distance from the current DCS inventory composition ($w_{\text{int}} = 4.0 / \alpha_{\text{trim}}$) to minimize make-up gas consumption during minor load fluctuations.
2. **Closed-Loop Inventory Dilution Make-Up Calculator (`backend/core/makeup_calculator.py`)**:
   - Solves the coupled molar conservation and loop expansion balance $\mathbf{u} = n_f (\mathbf{Y}^{-1} \mathbf{x}_{\text{target}}) - n_0 (\mathbf{Y}^{-1} \mathbf{x}_0) \ge \mathbf{0}$ using the plant header purity matrix $\mathbf{Y}$ (`H4FIC006` $N_2$, `H4FIC005`/`H4FIC009` $C_1$, `H4FI00C8` $C_2$ from De-Ethanizer `3C-4`, and `H4FIC007` $C_3$ from De-Propanizer `3C-6`).
   - Reports component injection rates in dual engineering units ($Nm^3/\text{h}$, $kg/\text{h}$, $t/\text{h}$, $scfd$) and enforces strict `NOT EVALUATED` / `TIDAK DAPAT DIEVALUASI` null guards when inventory or composition inputs are missing or invalid.
3. **Hybrid Full-Stack & Offline Browser Execution**:
   - **Backend (`backend/`)**: FastAPI server exposing `/api/health`, `/api/baseline`, `/api/predict`, `/api/optimize`, `/api/makeup`, `/api/simulate`, and `/api/sensitivity`.
   - **Frontend (`frontend/`)**: React 19 + TypeScript + Tailwind CSS interface with Yokogawa Centum VP PFD mimic (`MchePfdTab.tsx`), strategy selector (`TabInputResults.tsx`), `AbortController` concurrency protection (`App.tsx`), and client-side TypeScript/ONNX fallback (`physicsEngine.ts`).

---

## 3. Running & Verifying the Application

### 3.1 Backend Server & Test Suite (198 Passed Tests)
```bash
cd operator-website/backend
pip install -r requirements.txt
python -m pytest tests/ -v
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3.2 Frontend Build & Test Suite (26 Passed Vitest Tests + 64 Node Reviewer Gates)
```bash
cd operator-website/frontend
npm install
npm test
npm run build
```

---

## 4. Reference Engineering Documentation

See the root directory for the 8 comprehensive Phase 3 engineering reports:
- [`../MR_OPTIMIZATION_STRATEGY.md`](../MR_OPTIMIZATION_STRATEGY.md)
- [`../OPTIMIZER_DATA_FLOW_AUDIT.md`](../OPTIMIZER_DATA_FLOW_AUDIT.md)
- [`../OBJECTIVE_AND_CONSTRAINT_REGISTER.md`](../OBJECTIVE_AND_CONSTRAINT_REGISTER.md)
- [`../MR_MAKEUP_MASS_BALANCE.md`](../MR_MAKEUP_MASS_BALANCE.md)
- [`../LOAD_SENSITIVITY_STUDY.md`](../LOAD_SENSITIVITY_STUDY.md)
- [`../API_SCENARIO_CONTRACT.md`](../API_SCENARIO_CONTRACT.md)
- [`../KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md)
- [`../PHASE_3_FINAL_VERIFICATION_REPORT.md`](../PHASE_3_FINAL_VERIFICATION_REPORT.md)
