"""
Held-Karp Algorithm — Exact TSP Solution via Dynamic Programming + Bitmask

Solves the Travelling Salesman Problem (TSP) optimally using DP over subsets.
Used for Multi-Stop Route Planning in cold-chain logistics.

Time Complexity:  O(n² · 2ⁿ) where n = number of cities
Space Complexity: O(n · 2ⁿ) for the DP table
Optimal for:      n ≤ 20 (exponential growth makes it infeasible beyond this)

Reference: Held, M. & Karp, R. (1962). "A Dynamic Programming Approach to
           Sequencing Problems." Journal of SIAM, 10(1), 196-210.
"""

from __future__ import annotations
from models.graph import Graph


def held_karp_tsp(graph: Graph, start: str) -> dict:
    """
    Solve TSP exactly using the Held-Karp DP algorithm.

    The algorithm works in two phases:
      Phase 1 — Build DP table:
        dp[S][i] = minimum cost to visit all cities in subset S,
                   ending at city i, starting from 'start'.
        S is represented as a bitmask where bit j = 1 means city j is visited.

      Phase 2 — Reconstruct optimal path:
        Backtrack through the DP table to find the actual tour.

    Args:
        graph: The logistics network graph.
        start: The starting city node_id.

    Returns:
        dict with keys:
            - path: list of node_ids in optimal tour order
            - total_cost: minimum tour cost
            - dp_states_computed: number of DP states filled
            - complexity: dict with time and space complexity strings

    Raises:
        ValueError: If start node not in graph or graph has < 2 nodes.

    Time:  O(n² · 2ⁿ)
    Space: O(n · 2ⁿ)
    """
    nodes = graph.get_node_ids()
    n = len(nodes)

    if start not in nodes:
        raise ValueError(f"Start node '{start}' not found in graph.")
    if n < 2:
        raise ValueError("Graph must have at least 2 nodes for TSP.")

    # Map node_id → index for bitmask operations
    idx = {node: i for i, node in enumerate(nodes)}
    start_idx = idx[start]

    # ── Phase 1: Build DP Table ──────────────────────────────────────────
    # dp[visited_mask][current_city] = (min_cost, previous_city_index)
    INF = float("inf")
    FULL_MASK = (1 << n) - 1  # All cities visited

    # Initialize: dp[{start}][start] = 0
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]
    dp[1 << start_idx][start_idx] = 0

    states_computed = 0

    # Iterate over all subsets of cities
    for mask in range(1 << n):
        for last in range(n):
            # Skip if 'last' is not in the current subset
            if not (mask & (1 << last)):
                continue
            if dp[mask][last] == INF:
                continue

            # Try extending to each unvisited city
            for next_city in range(n):
                if mask & (1 << next_city):
                    continue  # Already visited

                # Get edge weight between last → next_city
                edge_cost = graph.get_weight(nodes[last], nodes[next_city])
                if edge_cost == INF:
                    continue  # No direct edge

                new_mask = mask | (1 << next_city)
                new_cost = dp[mask][last] + edge_cost

                if new_cost < dp[new_mask][next_city]:
                    dp[new_mask][next_city] = new_cost
                    parent[new_mask][next_city] = last
                    states_computed += 1

    # ── Complete the tour: return to start ───────────────────────────────
    best_cost = INF
    best_last = -1

    for last in range(n):
        if last == start_idx:
            continue
        return_cost = graph.get_weight(nodes[last], nodes[start_idx])
        if return_cost == INF:
            continue
        total = dp[FULL_MASK][last] + return_cost
        if total < best_cost:
            best_cost = total
            best_last = last

    if best_cost == INF:
        return {
            "path": [],
            "total_cost": -1,
            "dp_states_computed": states_computed,
            "complexity": {
                "time": f"O(n² · 2ⁿ) = O({n}² · 2^{n}) = O({n*n * (1 << n):,})",
                "space": f"O(n · 2ⁿ) = O({n} · 2^{n}) = O({n * (1 << n):,})",
            },
            "error": "No valid Hamiltonian cycle found. Graph may not be fully connected.",
        }

    # ── Phase 2: Reconstruct Path ────────────────────────────────────────
    path_indices = []
    mask = FULL_MASK
    current = best_last

    while current != -1:
        path_indices.append(current)
        prev = parent[mask][current]
        mask ^= (1 << current)
        current = prev

    path_indices.reverse()
    path_indices.append(start_idx)  # Return to start

    path = [nodes[i] for i in path_indices]

    return {
        "path": path,
        "total_cost": best_cost,
        "dp_states_computed": states_computed,
        "complexity": {
            "time": f"O(n² · 2ⁿ) = O({n}² · 2^{n}) = O({n*n * (1 << n):,})",
            "space": f"O(n · 2ⁿ) = O({n} · 2^{n}) = O({n * (1 << n):,})",
        },
    }
