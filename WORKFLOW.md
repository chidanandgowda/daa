# Cold-Chain Logistics Optimizer: Step-by-Step Workflow

This document explains exactly how the Cold-Chain Logistics Optimizer works under the hood. The core philosophy of this project is that algorithms are not used in isolation; instead, they are chained together into a **unified optimization pipeline** that solves a realistic logistics problem from start to finish.

The entire process is orchestrated by the `/api/optimize` endpoint in the backend and visualised in the frontend.

---

## The Big Picture: The Optimization Pipeline

When you click **"Run Full Pipeline"** in the UI, the system executes four distinct steps in a specific order. Each step solves a different piece of the logistics puzzle, passing its results to the next step.

```text
Step 1: Knapsack (What to load?)
       ↓
Step 2: TSP (In what order do we deliver?)
       ↓
Step 3: Dijkstra (What is the exact route between stops?)
       ↓
Step 4: A* Search (What if a road is blocked?)
```

Here is a detailed breakdown of each step.

---

## Step 1: Cargo Load Balancing (0/1 Knapsack)

**The Problem:** A refrigerated truck has a strict weight capacity (e.g., 2000 kg). We have a list of available cargo items (Vaccines, Insulin, Seafood, Dairy, etc.), each with a specific weight and a priority/monetary value. We cannot take everything. 
**The Goal:** Maximize the total value of the loaded cargo without exceeding the truck's weight capacity.

**How it works:**
1. The backend receives the truck capacity from the frontend.
2. The **0/1 Knapsack algorithm** (using Dynamic Programming) builds a 2D table where `dp[i][w]` represents the maximum value achievable using the first `i` items with a weight limit of `w`.
3. It iterates through all available items, deciding at each step whether including the item yields a higher total value than excluding it.
4. Finally, it backtracks through the DP table to identify exactly which items were selected.

**Result:** A list of optimal items to load onto the truck, ensuring we transport the most critical/valuable goods possible.

---

## Step 2: Multi-Stop Route Planning (TSP)

**The Problem:** The truck needs to visit all 12 cold-chain hubs (cities) in the network exactly once and return to the starting depot.
**The Goal:** Find the order of cities that minimizes the total travel cost.

**How it works:**
1. The system needs to know the shortest distance between every pair of cities. It runs Dijkstra's algorithm in the background (Phase 0 of TSP) to pre-calculate an All-Pairs Shortest Path distance matrix.
2. Depending on the user's choice, it runs one of two algorithms:
   - **Held-Karp (Exact):** Uses Dynamic Programming with Bitmasking. It calculates the absolute optimal route by breaking the problem down into smaller sub-tours. It is mathematically guaranteed to find the best route but is computationally heavy (O(n² · 2ⁿ)).
   - **Nearest Neighbour (Heuristic):** A greedy approach that simply goes to the closest unvisited city next. It is incredibly fast but does not guarantee the optimal route.
   
**Result:** An ordered sequence of cities to visit (e.g., DEL → LKO → KOL → ... → DEL).

---

## Step 3: Shortest Safe Path (Dijkstra)

**The Problem:** The TSP algorithm told us the *order* of cities to visit (e.g., we must go from Delhi to Lucknow). However, TSP only knows the theoretical shortest distance between them. In the real world, we need to know the exact road segments to take through the graph to get from Delhi to Lucknow safely.
**The Goal:** Find the cheapest path between each consecutive pair of stops in the TSP route, factoring in temperature penalties.

**How it works:**
1. The backend looks at the TSP route and breaks it into consecutive segments (Segment 1: DEL → LKO, Segment 2: LKO → KOL, etc.).
2. For each segment, it runs **Dijkstra's Algorithm**.
3. Dijkstra explores the road network using a priority queue (min-heap). 
4. **Temperature Penalty:** As Dijkstra calculates edge weights, it checks the temperature zones of the connected cities. If a road passes through a "hot" zone, the algorithm artificially inflates the cost (penalty) of that road, encouraging the truck to route through cooler, safer regions if a viable alternative exists.

**Result:** The exact, node-by-node path the truck will take for the entire journey, visualised in green on the graph.

---

## Step 4: Dynamic Rerouting (A* Search)

**The Problem:** What happens if a road is closed due to an accident, or a warehouse fails while the truck is en route? The pre-planned Dijkstra paths are no longer valid.
**The Goal:** Find a new optimal route around the blocked infrastructure as quickly as possible.

**How it works:**
1. In the frontend, the user can click on edges (roads) to mark them as "blocked" (simulating a failure).
2. The backend receives the list of blocked edges. Before running, it does a quick BFS connectivity check to ensure the graph hasn't been completely split apart.
3. For every segment in the TSP route, it runs **A* Search**, passing in the blocked edges so the algorithm knows to ignore them.
4. **The Heuristic:** A* uses the **Haversine formula** (which calculates the straight-line geographic distance between two lat/long coordinates on Earth) as its heuristic. 
5. Because A* knows roughly what direction the destination is in (thanks to the Haversine heuristic), it explores far fewer nodes than Dijkstra, making it incredibly fast for real-time rerouting.

**Result:** Updated routes that actively avoid the blocked edges, visualised in amber/orange on the graph.

---

## Summary of the Request Flow

1. User configures parameters (Capacity, Start City, TSP Method, Blocked Edges) in the UI.
2. User clicks **Run Full Pipeline**.
3. Frontend sends a `POST` request to `/api/optimize` with the parameters.
4. Backend executes `knapsack_01()` to get cargo.
5. Backend executes `held_karp_tsp()` or `nearest_neighbour_tsp()` to get the stop order.
6. Backend loops through the TSP stops, executing `dijkstra()` for every pair.
7. If there are blocked edges, Backend loops through the TSP stops again, executing `astar_search()` to find alternate routes.
8. Backend packages all results, execution times, and complexity metrics into a JSON response.
9. Frontend receives the JSON, updates the UI cards, and animates the Cytoscape.js graph to show the final plan.
