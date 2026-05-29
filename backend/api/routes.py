"""
REST API Routes — Cold-Chain Logistics Optimizer

All algorithm endpoints follow a consistent pattern:
  1. Parse and validate request body (Pydantic)
  2. Execute algorithm with timing
  3. Return standardized AlgorithmResult response

Base URL: /api
"""

from __future__ import annotations
import time

from fastapi import APIRouter, HTTPException

from models.schemas import (
    TSPRequest,
    DijkstraRequest,
    AStarRequest,
    KnapsackRequest,
    AlgorithmResult,
    GraphResponse,
)
from data.sample_data import build_sample_graph, CARGO_ITEMS
from algorithms.held_karp import held_karp_tsp
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar_search
from algorithms.knapsack import knapsack_01
from algorithms.nearest_neighbour import nearest_neighbour_tsp


router = APIRouter(prefix="/api", tags=["algorithms"])

# Build graph once at module level (shared across requests)
graph = build_sample_graph()


# ── Graph Data ───────────────────────────────────────────────────────────

@router.get("/graph", response_model=GraphResponse)
def get_graph():
    """
    Return the complete cold-chain logistics graph.

    Provides all nodes (cities) and edges (routes) for frontend visualization.
    """
    data = graph.to_dict()
    return GraphResponse(
        nodes=data["nodes"],
        edges=data["edges"],
        node_count=len(graph.nodes),
        edge_count=len(graph.get_all_edges()),
    )


@router.get("/cargo")
def get_cargo_items():
    """Return the list of available cargo items for knapsack optimization."""
    return {"items": CARGO_ITEMS, "count": len(CARGO_ITEMS)}


# ── Held-Karp (Exact TSP) ───────────────────────────────────────────────

@router.post("/tsp", response_model=AlgorithmResult)
def run_held_karp(request: TSPRequest):
    """
    Solve TSP exactly using the Held-Karp DP algorithm.

    Returns the optimal Hamiltonian cycle (minimum cost tour visiting
    all cities exactly once and returning to start).

    ⚠️ Exponential time — suitable for ≤ 20 cities.
    """
    try:
        start_time = time.perf_counter()
        result = held_karp_tsp(graph, request.start)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AlgorithmResult(
            algorithm="Held-Karp (Exact TSP)",
            result=result,
            execution_time_ms=round(elapsed_ms, 3),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")


# ── Dijkstra (Shortest Safe Path) ───────────────────────────────────────

@router.post("/dijkstra", response_model=AlgorithmResult)
def run_dijkstra(request: DijkstraRequest):
    """
    Find the shortest (cheapest) path between two cities using Dijkstra's algorithm.

    Optionally applies temperature-zone penalties for cold-chain safety.
    """
    try:
        start_time = time.perf_counter()
        result = dijkstra(graph, request.source, request.destination, request.temp_penalty)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AlgorithmResult(
            algorithm="Dijkstra (Shortest Safe Path)",
            result=result,
            execution_time_ms=round(elapsed_ms, 3),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")


# ── A* Search (Dynamic Rerouting) ───────────────────────────────────────

@router.post("/astar", response_model=AlgorithmResult)
def run_astar(request: AStarRequest):
    """
    Find the optimal path using A* search with Haversine heuristic.

    Supports blocked edges to simulate route failures and dynamic rerouting.
    """
    try:
        # Convert blocked edges from list of lists to list of tuples
        blocked = None
        if request.blocked_edges:
            blocked = [(e[0], e[1]) for e in request.blocked_edges]

        start_time = time.perf_counter()
        result = astar_search(graph, request.source, request.destination, blocked)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AlgorithmResult(
            algorithm="A* Search (Dynamic Rerouting)",
            result=result,
            execution_time_ms=round(elapsed_ms, 3),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")


# ── 0/1 Knapsack (Cargo Load Balancing) ─────────────────────────────────

@router.post("/knapsack", response_model=AlgorithmResult)
def run_knapsack(request: KnapsackRequest):
    """
    Optimize cargo loading using 0/1 Knapsack dynamic programming.

    Uses sample cargo items if no custom items are provided.
    """
    try:
        items = request.items if request.items else CARGO_ITEMS

        start_time = time.perf_counter()
        result = knapsack_01(items, request.capacity)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AlgorithmResult(
            algorithm="0/1 Knapsack (Cargo Load Balancing)",
            result=result,
            execution_time_ms=round(elapsed_ms, 3),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")


# ── Nearest Neighbour (TSP Heuristic) ───────────────────────────────────

@router.post("/nearest-neighbour", response_model=AlgorithmResult)
def run_nearest_neighbour(request: TSPRequest):
    """
    Approximate TSP using the Nearest Neighbour greedy heuristic.

    Faster than Held-Karp but produces suboptimal solutions.
    Used as a performance comparison baseline.
    """
    try:
        start_time = time.perf_counter()
        result = nearest_neighbour_tsp(graph, request.start)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AlgorithmResult(
            algorithm="Nearest Neighbour (TSP Heuristic)",
            result=result,
            execution_time_ms=round(elapsed_ms, 3),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")
