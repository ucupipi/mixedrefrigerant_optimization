"""FastAPI Application Entry Point for Operator Decision-Support Website.

System: Badak LNG Plant-3 Train H C3MR Decision-Support Suite
Mode: READ-ONLY (Zero write-back to DCS / SIS / ESD)
Governance: AGENTS.md (Hukum Anti-Dosa Rekayasa, Pasal 1–13)
"""
from __future__ import annotations

import os
import sys

# Ensure backend root and src directory are in sys.path for serverless and container runtimes
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
_src_dir = os.path.join(_backend_dir, "src")
if os.path.exists(_src_dir) and _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("c3mr_operator_backend")

app = FastAPI(
    title="Badak LNG Train H C3MR Operator Decision-Support API",
    description=(
        "Sistem pendukung keputusan operator berbasis machine learning fisika-terkendali "
        "untuk pemodelan daya poros dan evaluasi efisiensi energi Train C3MR Badak LNG Plant-3. "
        "Aplikasi ini berspesifikasi READ-ONLY dan tidak mengirim sinyal kontrol ke DCS."
    ),
    version="1.0.0",
)

# Enable CORS for local development and plant workstation browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount static frontend build if present (serves single-container fullstack deployment)
import os
from fastapi.staticfiles import StaticFiles

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    alt_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
    if os.path.exists(alt_static):
        static_dir = alt_static

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"Mounted static frontend from: {static_dir}")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize model cache and log system state."""
    logger.info("==================================================================")
    logger.info("Badak LNG Plant-3 Train H C3MR Operator Decision-Support System")
    logger.info("MODE: READ-ONLY (DCS write-back strictly disabled)")
    logger.info("GOVERNANCE: AGENTS.md compliance active")
    logger.info("==================================================================")
    try:
        from core.model_loader import load_surrogate_model
        model = load_surrogate_model()
        logger.info(f"Surrogate model successfully loaded: {type(model).__name__}")
    except Exception as exc:
        logger.warning(f"Surrogate model preload warning (will retry on demand): {exc}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)

