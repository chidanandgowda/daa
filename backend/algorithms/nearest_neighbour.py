"""
Nearest Neighbour Heuristic — TSP Approximation

A greedy heuristic for the Travelling Salesman Problem that builds a tour
by always visiting the nearest unvisited city. Fast but suboptimal — used
as a baseline comparison against the exact Held-Karp algorithm.

Time Complexity:  O(n²) — for each of n cities, scan n candidates
Space Complexity: O(n)  — track visited set and path

Approximation Ratio: Can produce tours up to O(log n) times the optimal
                     in worst case, but typically within 20-25% of optimal
                     for geographic/Euclidean instances.

This is the standard greedy heuristic taught in DAA courses to illustrate
the trade-off between polynomial runtime and solution quality.
"""

from __future__ import annotations
from models.graph import Graph
from algorithms.dijkstra import dijkstra


def nearest_neighbour_tsp(graph: Graph, start: str, temp_penalty: bool = True) -> dict:
    """
    Approximate TSP using the Nearest Neighbour greedy heuristic.
    Supports sparse graphs by using Dijkstra for step-wise shortest paths.
    """
    nodes = graph.get_node_ids()
    n = len(nodes)

    if start not in nodes:
        raise ValueError(f"Start node '{start}' not found in graph.")
    if n < 2:
        raise ValueError("Graph must have at least 2 nodes for TSP.")

    # ── Phase 0: Pre-calculate distance matrix ───────────────────────────
    dist_matrix = {}
    for node_id in nodes:
        res = dijkstra(graph, node_id, None, temp_penalty)
        dist_matrix[node_id] = res["distances"]

    # ── Greedy Construction ──────────────────────────────────────────────
    visited = {start}
    path = [start]
    total_cost = 0.0
    current = start

    for _ in range(n - 1):
        # Find the nearest unvisited neighbor
        best_next = None
        best_cost = float("inf")

        for neighbor_id, cost in dist_matrix[current].items():
            if neighbor_id not in visited and cost < best_cost:
                best_cost = cost
                best_next = neighbor_id

        if best_next is None:
            # Cannot complete the tour (disconnected graph)
            return {
                "path": path,
                "total_cost": total_cost,
                "complexity": {"time": "O(n²)", "space": "O(n²)"},
                "error": "Cannot complete tour — graph is not fully connected.",
            }

        visited.add(best_next)
        path.append(best_next)
        total_cost += best_cost
        current = best_next

    # ── Return to start ──────────────────────────────────────────────────
    return_cost = dist_matrix[current].get(start, float("inf"))
    if return_cost == float("inf"):
        return {
            "path": path,
            "total_cost": total_cost,
            "complexity": {"time": "O(n²)", "space": "O(n²)"},
            "error": f"Cannot return to start '{start}' from '{current}'.",
        }

    total_cost += return_cost
    path.append(start)

    return {
        "path": path,
        "total_cost": round(total_cost, 2),
        "complexity": {"time": "O(n²)", "space": "O(n²)"},
    }
