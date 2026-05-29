# Performance Report: Cold-Chain Logistics Optimizer

> **RVCE — Design and Analysis of Algorithms Project**
> Ganesh M · Chidanand Gowda · Chirantan

## 1. Introduction

This report analyzes the performance of the five algorithms used in the Cold-Chain Logistics Optimizer, focusing on how they **work together as a pipeline** and the individual complexity/performance characteristics of each.

---

## 2. The Optimization Pipeline

The algorithms are chained to solve the complete cold-chain logistics problem:

```
Step 1: Knapsack    →  Step 2: TSP      →  Step 3: Dijkstra  →  Step 4: A*
(What to load?)        (Which order?)       (Shortest paths?)     (Road blocked?)
```

**Why this order matters:**
- You must decide **what cargo to carry** (Knapsack) before you can plan the route
- You need the **multi-stop route** (TSP) before computing segment-level paths
- Dijkstra gives the **shortest safe path** per segment of the TSP tour
- A* handles **dynamic failures** — only triggered when edges are blocked

---

## 3. Algorithm Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Type |
|-----------|----------------|-----------------|------|
| 0/1 Knapsack | O(n · W) | O(n · W) | Pseudo-polynomial DP |
| Held-Karp TSP | O(n² · 2ⁿ) | O(n · 2ⁿ) | Exponential DP |
| Nearest Neighbour | O(n²) | O(n) | Greedy heuristic |
| Dijkstra | O((V+E) · log V) | O(V) | Greedy (priority queue) |
| A* Search | O(E · log V) | O(V) | Informed search |

---

## 4. Empirical Results (12-City Network)

Pipeline executed with: Start=DEL, Capacity=2000 kg, 1 blocked edge (MUM↔PUN)

### Step 1: 0/1 Knapsack — Cargo Selection

| Metric | Value |
|--------|-------|
| Items available | 12 |
| Items selected | 6 |
| Total value | ₹341,000 |
| Total weight | 1,980 kg |
| Capacity utilization | 99.0% |
| Execution time | < 1 ms |
| DP table size | 12 × 2000 = 24,000 entries |

The knapsack correctly prioritized high-value, low-weight items (Vaccines ₹95K/80kg, Blood Plasma ₹72K/50kg, Biotech Samples ₹58K/30kg).

### Step 2: Held-Karp TSP — Route Planning

| Metric | Value |
|--------|-------|
| Cities | 12 |
| Optimal tour cost | ₹99,900 |
| DP states computed | ~49,152 |
| Execution time | ~40 ms |
| Path | DEL → LKO → KOL → VIZ → CHN → COC → BLR → HYD → PUN → MUM → AHM → JAI → DEL |

### Step 3: Dijkstra — Shortest Safe Paths

| Metric | Value |
|--------|-------|
| Segments computed | 12 |
| Total segment cost | ₹110,285 |
| Execution time | < 1 ms |
| Nodes explored (avg) | 3–5 per segment |

Dijkstra runs once per consecutive pair in the TSP route, finding the cheapest path for each leg of the journey.

### Step 4: A* Search — Dynamic Rerouting

| Metric | Value |
|--------|-------|
| Blocked edges | 1 (MUM ↔ PUN) |
| Segments rerouted | 12 |
| Execution time | < 1 ms |
| Heuristic | Haversine distance × cost factor |

A* successfully rerouted the MUM→PUN segment through an alternate path, demonstrating real-time failure recovery.

### Total Pipeline

| Metric | Value |
|--------|-------|
| **Total execution time** | **43.87 ms** |
| Steps executed | 4 |
| Graph nodes | 12 |
| Graph edges | 23 |

---

## 5. Held-Karp vs Nearest Neighbour (TSP Comparison)

Both solve TSP but with different guarantees:

| Metric | Held-Karp (Exact) | Nearest Neighbour (Heuristic) |
|--------|-------------------|-------------------------------|
| **Guarantee** | Globally optimal | No guarantee |
| **Time** | O(n² · 2ⁿ) | O(n²) |
| **Space** | O(n · 2ⁿ) | O(n) |
| **Practical limit** | n ≤ 20 | Any n |
| **Typical quality** | 100% optimal | ~80% of optimal |

### Scalability

| n (Cities) | Held-Karp Operations | NN Operations | Speedup |
|-----------|---------------------|---------------|---------|
| 5 | 800 | 25 | 32× |
| 10 | 102,400 | 100 | 1,024× |
| 12 | 589,824 | 144 | 4,096× |
| 15 | 7,372,800 | 225 | 32,768× |
| 20 | 419,430,400 | 400 | 1,048,576× |

**Conclusion:** For our 12-city network, Held-Karp runs in ~40ms — perfectly feasible. For networks > 20 cities, switch to Nearest Neighbour.

---

## 6. Dijkstra vs A* (Path-finding Comparison)

Both find shortest paths, but A* is used specifically for rerouting:

| Metric | Dijkstra | A* Search |
|--------|----------|-----------|
| **Purpose in pipeline** | Normal shortest path | Rerouting on failures |
| **Uses heuristic** | No (uninformed) | Yes (Haversine) |
| **Handles blocked edges** | No | Yes |
| **Optimality** | Optimal | Optimal (with admissible heuristic) |
| **Typical nodes explored** | More | Fewer (guided by heuristic) |

A* explores fewer nodes than Dijkstra because the Haversine heuristic guides the search toward the goal.

---

## 7. Conclusion

The pipeline approach demonstrates how classical DAA algorithms solve **real-world problems** when combined:

1. **Knapsack** ensures maximum cargo value within constraints
2. **Held-Karp** produces the mathematically optimal delivery route
3. **Dijkstra** minimizes cost for each route segment with temperature safety
4. **A*** provides resilience against infrastructure failures

All five algorithms execute within **50ms total** for our 12-city network, making the system suitable for real-time logistics planning.

---

*Report prepared as part of the DAA Course Project, RVCE 2025–26.*
