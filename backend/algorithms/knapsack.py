"""
0/1 Knapsack Algorithm — Cargo Load Balancing for Cold-Chain Trucks

Solves the classic 0/1 Knapsack problem using Dynamic Programming to determine
the optimal subset of cargo items to load onto a refrigerated truck with
limited capacity, maximizing total value (priority × monetary value).

Time Complexity:  O(n · W) where n = number of items, W = truck capacity
Space Complexity: O(n · W) for the DP table (can be optimized to O(W) if
                  only the max value is needed, but we need item selection)

This is a pseudo-polynomial algorithm — polynomial in the numeric value of W,
but exponential in the number of bits needed to represent W.

Reference: Kellerer, H., Pferschy, U., & Pisinger, D. (2004).
           "Knapsack Problems." Springer.
"""

from __future__ import annotations


def knapsack_01(
    items: list[dict],
    capacity: float,
) -> dict:
    """
    Solve the 0/1 Knapsack problem for cargo load balancing.

    Each item has:
      - id:        unique cargo identifier
      - name:      descriptive name
      - weight_kg: weight of the cargo package
      - value:     monetary/priority value of the cargo

    The algorithm builds a 2D DP table where:
      dp[i][w] = maximum value achievable using the first i items
                 with total weight ≤ w

    Transition:
      dp[i][w] = max(
          dp[i-1][w],                              # Don't take item i
          dp[i-1][w - weight_i] + value_i           # Take item i (if fits)
      )

    Args:
        items:    List of cargo item dicts with 'id', 'name', 'weight_kg', 'value'.
        capacity: Maximum truck capacity in kg.

    Returns:
        dict with keys:
            - selected_items: list of selected item dicts
            - total_value: maximum achievable value
            - total_weight: total weight of selected items
            - capacity: truck capacity used
            - utilization_pct: percentage of capacity utilized
            - complexity: time/space complexity strings

    Time:  O(n · W)
    Space: O(n · W)
    """
    n = len(items)
    W = int(capacity)

    if n == 0 or W <= 0:
        return {
            "selected_items": [],
            "total_value": 0,
            "total_weight": 0,
            "capacity": capacity,
            "utilization_pct": 0.0,
            "complexity": {"time": "O(0)", "space": "O(0)"},
        }

    # Extract weights and values
    weights = [int(item["weight_kg"]) for item in items]
    values = [item["value"] for item in items]

    # ── Phase 1: Build DP Table ──────────────────────────────────────────
    # dp[i][w] = max value using items 0..i-1 with capacity w
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            # Option 1: Don't include item i
            dp[i][w] = dp[i - 1][w]

            # Option 2: Include item i (if it fits)
            if weights[i - 1] <= w:
                include_val = dp[i - 1][w - weights[i - 1]] + values[i - 1]
                dp[i][w] = max(dp[i][w], include_val)

    # ── Phase 2: Backtrack to find selected items ────────────────────────
    selected = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            # Item i was included
            selected.append(items[i - 1])
            w -= weights[i - 1]

    selected.reverse()  # Maintain original order

    total_weight = sum(int(item["weight_kg"]) for item in selected)
    total_value = sum(item["value"] for item in selected)

    return {
        "selected_items": selected,
        "total_value": total_value,
        "total_weight": total_weight,
        "capacity": capacity,
        "utilization_pct": round((total_weight / capacity) * 100, 1) if capacity > 0 else 0,
        "complexity": {
            "time": f"O(n · W) = O({n} · {W}) = O({n * W:,})",
            "space": f"O(n · W) = O({n} · {W}) = O({n * W:,})",
        },
    }
