"""
Dijkstra's Algorithm — Shortest Safe Path in Cold-Chain Network

Finds the shortest (minimum cost) path from a source city to a destination,
considering cold-chain safety constraints via temperature-aware edge weighting.

Time Complexity:  O((V + E) · log V) using a binary heap
Space Complexity: O(V + E)

Reference: Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs."
           Numerische Mathematik, 1(1), 269-271.
"""

from __future__ import annotations
import heapq
from models.graph import Graph


def dijkstra(
    graph: Graph,
    source: str,
    destination: str,
    temp_penalty: bool = True,
) -> dict:
    """
    Find the shortest path from source to destination using Dijkstra's algorithm.

    Uses a min-heap priority queue for efficient extraction of the minimum-cost
    node at each step. Optionally applies temperature-zone penalties to edge
    weights to model cold-chain safety.

    Temperature Penalty Model:
        If source or target node is in a 'hot' zone, edge cost is multiplied
        by 1.15 (15% surcharge for additional refrigeration).

    Args:
        graph:        The logistics network graph.
        source:       Starting city node_id.
        destination:  Target city node_id.
        temp_penalty: Whether to apply temperature-based cost adjustments.

    Returns:
        dict with keys:
            - path: list of node_ids from source to destination
            - total_cost: total path cost
            - distances: dict of shortest distances from source to all visited nodes
            - nodes_explored: number of nodes popped from the priority queue
            - complexity: time/space complexity strings

    Raises:
        ValueError: If source or destination not in graph.

    Time:  O((V + E) · log V)
    Space: O(V)
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not found in graph.")
    if destination not in graph.nodes:
        raise ValueError(f"Destination node '{destination}' not found in graph.")

    V = len(graph.nodes)
    E = len(graph.get_all_edges())

    # ── Initialize ───────────────────────────────────────────────────────
    INF = float("inf")
    dist = {node_id: INF for node_id in graph.nodes}
    prev = {node_id: None for node_id in graph.nodes}
    dist[source] = 0

    # Min-heap: (cost, node_id)
    pq = [(0, source)]
    visited = set()
    nodes_explored = 0

    # ── Main Loop ────────────────────────────────────────────────────────
    while pq:
        current_cost, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1

        # Early termination if we reached the destination
        if u == destination:
            break

        # Relax all neighbors of u
        for neighbor_id, edge in graph.get_neighbors(u).items():
            if neighbor_id in visited:
                continue

            # Calculate effective edge weight
            weight = edge.cost

            # Apply temperature penalty if enabled
            if temp_penalty:
                src_node = graph.nodes.get(u)
                tgt_node = graph.nodes.get(neighbor_id)
                if src_node and src_node.temp_zone == "hot":
                    weight *= 1.10
                if tgt_node and tgt_node.temp_zone == "hot":
                    weight *= 1.05

            new_dist = current_cost + weight

            if new_dist < dist[neighbor_id]:
                dist[neighbor_id] = new_dist
                prev[neighbor_id] = u
                heapq.heappush(pq, (new_dist, neighbor_id))

    # ── Reconstruct Path ─────────────────────────────────────────────────
    if dist[destination] == INF:
        return {
            "path": [],
            "total_cost": -1,
            "distances": {k: v for k, v in dist.items() if v != INF},
            "nodes_explored": nodes_explored,
            "complexity": {
                "time": f"O((V + E) · log V) = O(({V} + {E}) · log {V})",
                "space": f"O(V) = O({V})",
            },
            "error": f"No path exists from '{source}' to '{destination}'.",
        }

    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()

    return {
        "path": path,
        "total_cost": round(dist[destination], 2),
        "distances": {k: round(v, 2) for k, v in dist.items() if v != INF},
        "nodes_explored": nodes_explored,
        "complexity": {
            "time": f"O((V + E) · log V) = O(({V} + {E}) · log {V})",
            "space": f"O(V) = O({V})",
        },
    }
