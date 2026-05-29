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


def nearest_neighbour_tsp(graph: Graph, start: str) -> dict:
    """
    Approximate TSP using the Nearest Neighbour greedy heuristic.

    Algorithm:
      1. Start at the given city.
      2. At each step, move to the nearest unvisited city.
      3. After all cities are visited, return to the start.

    This is a constructive heuristic — it builds the tour incrementally
    without backtracking or improvement.

    Args:
        graph: The logistics network graph.
        start: The starting city node_id.

    Returns:
        dict with keys:
            - path: list of node_ids in tour order (ends at start)
            - total_cost: total tour cost
            - complexity: time/space complexity strings

    Raises:
        ValueError: If start node not in graph.

    Time:  O(n²)
    Space: O(n)
    """
    nodes = graph.get_node_ids()
    n = len(nodes)

    if start not in nodes:
        raise ValueError(f"Start node '{start}' not found in graph.")
    if n < 2:
        raise ValueError("Graph must have at least 2 nodes for TSP.")

    # ── Greedy Construction ──────────────────────────────────────────────
    visited = {start}
    path = [start]
    total_cost = 0.0
    current = start

    for _ in range(n - 1):
        # Find the nearest unvisited neighbor
        best_next = None
        best_cost = float("inf")

        for neighbor_id, edge in graph.get_neighbors(current).items():
            if neighbor_id not in visited and edge.cost < best_cost:
                best_cost = edge.cost
                best_next = neighbor_id

        if best_next is None:
            # No direct neighbor found — try all unvisited nodes
            for node_id in nodes:
                if node_id not in visited:
                    cost = graph.get_weight(current, node_id)
                    if cost < best_cost:
                        best_cost = cost
                        best_next = node_id

        if best_next is None:
            # Cannot complete the tour (disconnected graph)
            return {
                "path": path,
                "total_cost": total_cost,
                "complexity": {
                    "time": f"O(n²) = O({n}²) = O({n * n:,})",
                    "space": f"O(n) = O({n})",
                },
                "error": "Cannot complete tour — graph is not fully connected.",
                "visited_count": len(visited),
            }

        visited.add(best_next)
        path.append(best_next)
        total_cost += best_cost
        current = best_next

    # ── Return to start ──────────────────────────────────────────────────
    return_cost = graph.get_weight(current, start)
    if return_cost == float("inf"):
        return {
            "path": path,
            "total_cost": total_cost,
            "complexity": {
                "time": f"O(n²) = O({n}²) = O({n * n:,})",
                "space": f"O(n) = O({n})",
            },
            "error": f"Cannot return to start '{start}' from '{current}'.",
        }

    total_cost += return_cost
    path.append(start)

    return {
        "path": path,
        "total_cost": round(total_cost, 2),
        "complexity": {
            "time": f"O(n²) = O({n}²) = O({n * n:,})",
            "space": f"O(n) = O({n})",
        },
    }
