"""
REST API Routes — Cold-Chain Logistics Optimizer

All algorithm endpoints follow a consistent pattern:
  1. Parse and validate request body (Pydantic)
  2. Execute algorithm with timing
  3. Return standardized AlgorithmResult response

The /api/optimize endpoint chains algorithms together as a pipeline:
  Knapsack → TSP → Dijkstra → A* (on failure)

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
    PipelineRequest,
    GenerateGraphRequest,
    AlgorithmResult,
    GraphResponse,
)
from data.sample_data import build_sample_graph, CARGO_ITEMS
from data.dynamic_graph import generate_random_graph
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


@router.post("/graph/generate", response_model=GraphResponse)
def generate_new_graph(request: GenerateGraphRequest):
    """
    Generate a new random logistics graph and update the server state.
    """
    global graph
    graph = generate_random_graph(request.num_cities)
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


# ── Full Pipeline ────────────────────────────────────────────────────────

@router.post("/optimize")
def run_pipeline(request: PipelineRequest):
    """
    Run the full cold-chain optimization pipeline:

    Step 1 — Knapsack: Select optimal cargo for the truck
    Step 2 — TSP (Held-Karp or NN): Plan multi-stop delivery route
    Step 3 — Dijkstra: Find shortest safe segment between consecutive stops
    Step 4 — A*: Dynamically reroute if any edges are blocked

    All algorithms work together on the same graph and data.
    """
    blocked = None
    if request.blocked_edges:
        blocked = [(e[0], e[1]) for e in request.blocked_edges]

    # Pre-flight Connectivity Check
    reachable = graph.get_reachable_nodes(request.start, blocked)
    if len(reachable) < len(graph.nodes):
        unreachable = set(graph.nodes.keys()) - reachable
        unreachable_names = [graph.nodes[nid].name for nid in unreachable]
        raise HTTPException(
            status_code=400,
            detail=f"Simulation Failed: Due to blocked edges, {len(unreachable_names)} cities are completely cut off from the network (e.g. {unreachable_names[0]})."
        )

    results = {}
    total_start = time.perf_counter()

    # ── Step 1: Cargo Selection (Knapsack) ───────────────────────────
    try:
        t0 = time.perf_counter()
        knapsack_result = knapsack_01(
            request.items if request.items else CARGO_ITEMS,
            request.capacity,
        )
        knapsack_time = (time.perf_counter() - t0) * 1000
        results["knapsack"] = {
            "algorithm": "0/1 Knapsack DP",
            "purpose": "Cargo Load Balancing",
            "result": knapsack_result,
            "execution_time_ms": round(knapsack_time, 3),
        }
    except Exception as e:
        results["knapsack"] = {"error": str(e)}

    # ── Step 2: Route Planning (TSP) ─────────────────────────────────
    try:
        t0 = time.perf_counter()
        if request.tsp_method == "held-karp":
            tsp_result = held_karp_tsp(graph, request.start, request.temp_penalty)
            tsp_name = "Held-Karp (Exact TSP)"
        else:
            tsp_result = nearest_neighbour_tsp(graph, request.start, request.temp_penalty)
            tsp_name = "Nearest Neighbour (Heuristic TSP)"
        tsp_time = (time.perf_counter() - t0) * 1000
        results["tsp"] = {
            "algorithm": tsp_name,
            "purpose": "Multi-Stop Route Planning",
            "result": tsp_result,
            "execution_time_ms": round(tsp_time, 3),
        }
    except Exception as e:
        results["tsp"] = {"error": str(e)}

    # ── Step 3: Shortest Safe Segments (Dijkstra) ────────────────────
    tsp_path = results.get("tsp", {}).get("result", {}).get("path", [])
    if len(tsp_path) >= 2:
        segments = []
        total_segment_cost = 0
        t0 = time.perf_counter()
        for i in range(len(tsp_path) - 1):
            try:
                seg = dijkstra(graph, tsp_path[i], tsp_path[i + 1], request.temp_penalty)
                segments.append({
                    "from": tsp_path[i],
                    "to": tsp_path[i + 1],
                    "path": seg["path"],
                    "cost": seg["total_cost"],
                })
                if seg["total_cost"] > 0:
                    total_segment_cost += seg["total_cost"]
            except Exception:
                segments.append({
                    "from": tsp_path[i],
                    "to": tsp_path[i + 1],
                    "error": "No path found",
                })
        dijkstra_time = (time.perf_counter() - t0) * 1000
        results["dijkstra"] = {
            "algorithm": "Dijkstra's Algorithm",
            "purpose": "Shortest Safe Path (per segment)",
            "segments": segments,
            "total_segment_cost": round(total_segment_cost, 2),
            "execution_time_ms": round(dijkstra_time, 3),
        }

    # ── Step 4: Dynamic Rerouting (A*) ───────────────────────────────
    blocked = None
    if request.blocked_edges:
        blocked = [(e[0], e[1]) for e in request.blocked_edges]

    if blocked and len(tsp_path) >= 2:
        rerouted_segments = []
        t0 = time.perf_counter()
        for i in range(len(tsp_path) - 1):
            try:
                seg = astar_search(graph, tsp_path[i], tsp_path[i + 1], blocked)
                rerouted_segments.append({
                    "from": tsp_path[i],
                    "to": tsp_path[i + 1],
                    "path": seg["path"],
                    "cost": seg["total_cost"],
                    "was_affected": seg["total_cost"] != graph.get_weight(tsp_path[i], tsp_path[i + 1]),
                })
            except Exception:
                rerouted_segments.append({
                    "from": tsp_path[i],
                    "to": tsp_path[i + 1],
                    "error": "No alternate route found",
                })
        astar_time = (time.perf_counter() - t0) * 1000
        results["astar"] = {
            "algorithm": "A* Search",
            "purpose": "Dynamic Rerouting (blocked edges)",
            "blocked_edges": request.blocked_edges,
            "segments": rerouted_segments,
            "execution_time_ms": round(astar_time, 3),
        }

    total_time = (time.perf_counter() - total_start) * 1000
    return {
        "pipeline": results,
        "total_execution_time_ms": round(total_time, 3),
    }


# ── Individual Endpoints ─────────────────────────────────────────────────

@router.post("/tsp", response_model=AlgorithmResult)
def run_held_karp(request: TSPRequest):
    """Solve TSP exactly using the Held-Karp DP algorithm."""
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


@router.post("/dijkstra", response_model=AlgorithmResult)
def run_dijkstra(request: DijkstraRequest):
    """Find shortest path using Dijkstra's algorithm."""
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


@router.post("/astar", response_model=AlgorithmResult)
def run_astar(request: AStarRequest):
    """A* search with optional blocked edges for dynamic rerouting."""
    try:
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


@router.post("/knapsack", response_model=AlgorithmResult)
def run_knapsack(request: KnapsackRequest):
    """0/1 Knapsack optimization for cargo loading."""
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


@router.post("/nearest-neighbour", response_model=AlgorithmResult)
def run_nearest_neighbour(request: TSPRequest):
    """Nearest Neighbour TSP heuristic."""
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
