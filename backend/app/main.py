"""
Cold-Chain Logistics Optimizer — FastAPI Application Entry Point

Configures CORS, mounts API routes, and provides a health check endpoint.
Run with: uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

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
