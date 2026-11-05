# Badak LNG Plant-3 Train H C3MR Operator Decision-Support System

Autonomous Operator Decision-Support Workspace for mixed refrigerant (MR) composition optimization and energy management in Badak LNG Plant-3 Train H C3MR refrigeration cycle.

## Architecture

- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS (Industrial Operator Workspace, dual-mode: Operator / Engineering).
- **Backend**: Python 3.12 + FastAPI + Scikit-Learn + SciPy SLSQP Optimizer + Peng-Robinson EOS Thermodynamics.
- **Surrogate Models**:
  - `c3mr_power_surrogate_real.joblib`: Total C3MR Compressor Shaft Power (MW).
  - `surrogate_total_steam_t_h.joblib`: High-pressure steam consumption rate (t/h).
  - `surrogate_H4TI004B.joblib`: Suction drum temperature (°C).
  - `mcr_ilr_envelope.joblib`: Aitchison simplex $S^5$ compositional Mahalanobis distance covariance.

## Deployment on Render.com (Free Tier)

This repository includes a multi-stage `Dockerfile` and `render.yaml` blueprint ready for zero-configuration deployment on [Render](https://render.com):

1. Log in to [Render](https://render.com).
2. Click **New +** → **Blueprint** (or **Web Service**).
3. Connect repository `agentucupipi/mixedrefrigerant_optimization`.
4. Render will detect `render.yaml` and configure:
   - **Runtime**: Docker (multi-stage build: Node 20 frontend SPA build + Python 3.12 FastAPI backend)
   - **Port**: Automatic via `$PORT` environment variable (default: `10000`)
   - **Plan**: Free
   - **Region**: Singapore (`singapore`)
5. Click **Apply** or **Deploy**.
6. The service will be live at `https://<service-name>.onrender.com`.

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+

### Quick Start (Windows)
Double-click `operator-website\start_app.bat` or run:

```bash
# Terminal 1: Backend
cd operator-website/backend
pip install -r requirements.txt
uvicorn main:app --port 3001 --reload

# Terminal 2: Frontend
cd operator-website/frontend
npm install
npm run dev
```

Visit `http://localhost:5173` in your browser.

## Governance & Safety Boundaries
- **Anti-Surge Flow Floor**: MCR circulation $\ge 480.0\text{ t/h}$.
- **Suction TAL Interlock**: Suction drum temperature $T_{\text{suct}} \ge -45.0^\circ\text{C}$.
- **Thermodynamic Superheat**: PR-EOS dew point margin $\ge 3.0^\circ\text{C}$.
- **Composition Envelope**: Mahalanobis distance $D_M \le 3.0802$ ($\chi^2_{0.95, 4}$).
