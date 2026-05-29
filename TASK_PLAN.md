# Cold-Chain Logistics Optimizer — Task Plan

## Phase 1: Project Setup & Structure
- [x] Create progress tracking files (TASK_PLAN.md, PROGRESS.md, CONTEXT.md)
- [x] Initialize backend project structure (FastAPI + Python)
- [x] Initialize frontend project (Vanilla JS + Cytoscape.js)
- [x] Create README.md with setup instructions

## Phase 2: Graph Modeling & Data
- [x] Implement `Graph` class (adjacency list representation)
  - [x] `add_node()`, `add_edge()`, `get_neighbors()`, `get_weight()`
  - [x] `to_dict()` serialization for API responses
- [x] Create sample dataset (12 Indian cold-chain cities)
  - [x] Realistic edge weights (distance in km)
  - [x] Temperature zones & cargo capacities per node
  - [x] Cold-chain metadata (max transit time, refrigeration cost)

## Phase 3: Algorithm Implementation
- [x] **Held-Karp (Exact TSP via DP + Bitmask)**
  - [x] Core implementation with memoization
  - [x] Path reconstruction
  - [x] Complexity analysis in docstring: O(n² · 2ⁿ) time, O(n · 2ⁿ) space
- [x] **Dijkstra's Algorithm (Shortest Safe Path)**
  - [x] Min-heap priority queue implementation
  - [x] Temperature-aware edge weighting
  - [x] Complexity: O((V + E) log V)
- [x] **A* Search (Dynamic Rerouting)**
  - [x] Haversine-based heuristic function
  - [x] Edge failure simulation (blocked routes)
  - [x] Complexity: O(E log V) with admissible heuristic
- [x] **0/1 Knapsack (Cargo Load Balancing)**
  - [x] Classic DP table approach
  - [x] Item selection backtracking
  - [x] Complexity: O(n · W) time, O(n · W) space
- [x] **Nearest Neighbour Heuristic (TSP Approximation)**
  - [x] Greedy nearest-city selection
  - [x] Complexity: O(n²)

## Phase 4: Backend API (FastAPI)
- [x] Project configuration & CORS setup
- [x] API Endpoints:
  - [x] `GET /api/graph` — Return full graph data
  - [x] `POST /api/tsp` — Held-Karp exact TSP
  - [x] `POST /api/dijkstra` — Shortest path (source → destination)
  - [x] `POST /api/astar` — A* with optional blocked edges
  - [x] `POST /api/knapsack` — Cargo optimization
  - [x] `POST /api/nearest-neighbour` — TSP heuristic
- [x] Request/response models (Pydantic)
- [x] Error handling & input validation
- [x] Algorithm execution timing

## Phase 5: Frontend (Vanilla JS + Cytoscape.js)
- [x] Project scaffold (HTML/CSS/JS)
- [x] Cytoscape.js graph rendering
  - [x] Node positioning (geographic coordinates)
  - [x] Edge labels (cost)
  - [x] Interactive click events
- [x] Sidebar UI for algorithm selection
  - [x] Algorithm parameter inputs
  - [x] Run button & result display
- [x] Path highlighting with distinct colors per algorithm
- [x] Result panel (path sequence, cost, time, complexity)
- [x] Responsive design & dark theme
- [x] Loading states & error messages

## Phase 6: Documentation & Polish
- [x] README.md (setup, usage, API docs)
- [x] Performance Report (Held-Karp vs Nearest Neighbour)
- [x] Code comments & docstrings audit
- [ ] Final testing & verification
