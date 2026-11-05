# ==============================================================================
# Multi-Stage Dockerfile: Badak LNG C3MR Operator Assistant (Fullstack)
# Stage 1: Build React 19 + Vite Frontend SPA
# Stage 2: Python 3.12 + FastAPI + Scikit-Learn Model Serving
# ==============================================================================

# --- STAGE 1: Frontend Build ---
FROM node:20-slim AS frontend-builder

WORKDIR /build

COPY operator-website/frontend/package*.json ./
RUN npm install

COPY operator-website/frontend/ ./
RUN npm run build

# --- STAGE 2: Python Backend Runtime ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
    PYTHONPATH=/app:/app/src

WORKDIR /app

# 1. Install Python dependencies
COPY operator-website/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy backend application source (including self-contained models, data, src)
COPY operator-website/backend/ .

# 3. Copy built frontend SPA into static directory served by FastAPI
COPY --from=frontend-builder /build/dist ./static

EXPOSE 10000

# Start Uvicorn bound to dynamic environment port (Render, Hugging Face, Fly, etc.)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
