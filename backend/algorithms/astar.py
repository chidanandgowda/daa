"""
A* Search Algorithm — Dynamic Rerouting with Edge Failure Simulation

Finds the shortest path using an informed search strategy with a heuristic
function (Haversine distance). Supports blocked edges to simulate route
failures in cold-chain logistics (e.g., road closures, accidents).

Time Complexity:  O(E · log V) with an admissible, consistent heuristic
Space Complexity: O(V) for open/closed sets and path reconstruction
                  (worst case O(V + E) if all nodes are explored)

The Haversine heuristic is admissible (never overestimates) for geographic
graphs, guaranteeing optimal solutions.

Reference: Hart, P. E., Nilsson, N. J., & Raphael, B. (1968).
           "A Formal Basis for the Heuristic Determination of Minimum Cost Paths."
           IEEE Transactions on SSC, 4(2), 100-107.
"""

from __future__ import annotations
import heapq
import math
from models.graph import Graph


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.

    Args:
        lat1, lon1: Latitude/longitude of point 1 (degrees).
        lat2, lon2: Latitude/longitude of point 2 (degrees).

    Returns:
        Distance in kilometers.

    Time: O(1)
    """
    R = 6371.0  # Earth's radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def _heuristic(graph: Graph, node_id: str, goal_id: str, min_cost_per_km: float) -> float:
    """
    Compute the heuristic estimate (h) from node to goal.

    Uses Haversine distance scaled by a cost factor to estimate
    the minimum possible cost (ensures admissibility).
    """
    node = graph.nodes.get(node_id)
    goal = graph.nodes.get(goal_id)
    if not node or not goal:
        return 0.0

    # Haversine gives straight-line distance
    dist_km = haversine_distance(node.latitude, node.longitude, goal.latitude, goal.longitude)

    # Use the dynamic minimum cost-per-km to ensure admissibility
    return dist_km * min_cost_per_km


def astar_search(
    graph: Graph,
    source: str,
    destination: str,
    blocked_edges: list[tuple[str, str]] | None = None,
) -> dict:
    """
    Find the optimal path from source to destination using A* search,
    with optional edge failure simulation.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not found in graph.")
    if destination not in graph.nodes:
        raise ValueError(f"Destination node '{destination}' not found in graph.")

    V = len(graph.nodes)
    E = len(graph.get_all_edges())

    # Pre-calculate minimum cost per km in the current graph for the heuristic
    # This ensures the heuristic is always admissible for any graph.
    all_edges = []
    for neighbors in graph.adj.values():
        all_edges.extend(neighbors.values())
    
    if not all_edges:
        min_cost_per_km = 12.0 # Fallback
    else:
        # Avoid division by zero and pick a safe minimum
        min_cost_per_km = min((edge.cost / max(edge.distance_km, 1.0)) for edge in all_edges)

    # Build set of blocked edges for O(1) lookup
    blocked = set()
    if blocked_edges:
        for s, t in blocked_edges:
            blocked.add((s, t))
            blocked.add((t, s))  # Undirected

    # ── Initialize ───────────────────────────────────────────────────────
    INF = float("inf")
    g_score = {node_id: INF for node_id in graph.nodes}
    g_score[source] = 0

    f_score = {node_id: INF for node_id in graph.nodes}
    f_score[source] = _heuristic(graph, source, destination, min_cost_per_km)

    came_from: dict[str, str | None] = {node_id: None for node_id in graph.nodes}

    # Priority queue: (f_score, tiebreaker_counter, node_id)
    counter = 0
    open_set = [(f_score[source], counter, source)]
    closed_set = set()
    nodes_explored = 0

    # ── Main Loop ────────────────────────────────────────────────────────
    while open_set:
        current_f, _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        closed_set.add(current)
        nodes_explored += 1

        # Goal reached
        if current == destination:
            break

        # Expand neighbors
        for neighbor_id, edge in graph.get_neighbors(current).items():
            # Skip blocked edges
            if (current, neighbor_id) in blocked:
                continue

            if neighbor_id in closed_set:
                continue

            tentative_g = g_score[current] + edge.cost

            if tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = current
                g_score[neighbor_id] = tentative_g
                f_score[neighbor_id] = tentative_g + _heuristic(graph, neighbor_id, destination, min_cost_per_km)
                counter += 1
                heapq.heappush(open_set, (f_score[neighbor_id], counter, neighbor_id))

    # ── Reconstruct Path ─────────────────────────────────────────────────
    if g_score[destination] == INF:
        return {
            "path": [],
            "total_cost": -1,
            "nodes_explored": nodes_explored,
            "blocked_edges": blocked_edges or [],
            "complexity": {
                "time": f"O(E · log V) = O({E} · log {V})",
                "space": f"O(V) = O({V})",
            },
            "error": f"No path from '{source}' to '{destination}' (possibly blocked).",
        }

    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return {
        "path": path,
        "total_cost": round(g_score[destination], 2),
        "nodes_explored": nodes_explored,
        "blocked_edges": blocked_edges or [],
        "complexity": {
            "time": f"O(E · log V) = O({E} · log {V})",
            "space": f"O(V) = O({V})",
        },
    }
