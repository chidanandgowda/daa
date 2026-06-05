"""
Cold-Chain Logistics Optimizer — FastAPI Application Entry Point

Configures CORS, mounts API routes, and provides a health check endpoint.
Run with: uvicorn app.main:app --reload --port 8000
"""

import logging
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

# Configure logging for Docker stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cold-Chain Logistics Optimizer",
    description=(
        "A DAA project that models cold-chain logistics as a graph problem. "
        "Provides optimal routing (Held-Karp TSP, Dijkstra, A*), cargo "
        "optimization (0/1 Knapsack), and interactive visualization."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Global Exception Handler ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ── CORS Configuration ──────────────────────────────────────────────────
# Allow frontend (served separately or on different port) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API Routes ────────────────────────────────────────────────────
app.include_router(router)


# ── Health Check ─────────────────────────────────────────────────────────
@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "project": "Cold-Chain Logistics Optimizer",
        "version": "1.0.0",
        "docs": "/docs",
    }
