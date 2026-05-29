# Cold-Chain Logistics Optimizer — Project Context

## Project Overview
A full-stack web application for RV College of Engineering's Design and Analysis of Algorithms (DAA) course. Models cold-chain logistics as a graph problem, providing optimal routing and cargo decisions with interactive visualization.

## Architecture

```
cold-chain-optimizer/
├── backend/                    # Python FastAPI server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   └── config.py           # App configuration
│   ├── algorithms/             # All algorithm implementations
│   │   ├── __init__.py
│   │   ├── held_karp.py        # Exact TSP (DP + bitmask)
│   │   ├── dijkstra.py         # Shortest safe path
│   │   ├── astar.py            # Dynamic rerouting with A*
│   │   ├── knapsack.py         # 0/1 Knapsack cargo balancing
│   │   └── nearest_neighbour.py # TSP heuristic
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── graph.py            # Graph class (adjacency list)
│   │   └── schemas.py          # Pydantic request/response models
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   └── routes.py           # All REST endpoints
│   ├── data/
│   │   └── sample_data.py      # Sample city dataset
│   └── requirements.txt
├── frontend/                   # Vanilla JS + Cytoscape.js
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js              # Main application logic
│   │   ├── graph.js            # Cytoscape.js graph rendering
│   │   ├── api.js              # Backend API client
│   │   └── ui.js               # UI interactions & result display
│   └── assets/
├── TASK_PLAN.md
├── PROGRESS.md
├── CONTEXT.md
├── README.md
└── PERFORMANCE_REPORT.md
```

## Technology Decisions

### Backend: FastAPI (Python)
- **Why:** Automatic OpenAPI docs, async support, Pydantic validation, ideal for academic projects
- **Python version:** 3.10+
- **Key dependencies:** fastapi, uvicorn, pydantic

### Frontend: Vanilla JS + Cytoscape.js
- **Why:** No build step needed, lightweight, Cytoscape.js is the gold standard for graph visualization
- **Cytoscape.js:** Loaded via CDN — powerful graph rendering with built-in layouts, styling, and event handling
- **Design:** Dark theme, glassmorphism cards, smooth animations

### Graph Representation: Adjacency List
- **Why:** Sparse graphs (cities aren't all connected) → adjacency list is O(V + E) space vs O(V²) for matrix
- **Implementation:** Python dict of dicts: `{node_id: {neighbor_id: weight, ...}, ...}`

## Sample Dataset Design
- **12–15 Indian cities** on major cold-chain routes
- **Edge weights:** Composite cost = f(distance_km, fuel_cost, refrigeration_cost, road_quality)
- **Node metadata:** City name, latitude, longitude, temperature zone, warehouse capacity
- **Cargo items:** Pharmaceutical products, frozen food, dairy — each with weight, value, temperature requirement

## Algorithm Design Notes

### Held-Karp (Exact TSP)
- Suitable for n ≤ 20 cities (2ⁿ bitmask)
- Returns guaranteed optimal tour
- Compare with Nearest Neighbour for performance report

### Dijkstra (Shortest Safe Path)
- Modified weights: base_cost × temperature_penalty
- Priority queue via `heapq`

### A* (Dynamic Rerouting)
- Heuristic: Haversine distance (admissible for geographic graphs)
- Supports blocked edges to simulate route failures

### 0/1 Knapsack (Cargo Balancing)
- Items = cargo packages, weight = physical weight, value = priority/revenue
- Capacity = truck capacity in kg

### Nearest Neighbour (TSP Heuristic)
- Greedy baseline for comparison with Held-Karp
- Fast but suboptimal

## API Design
- All algorithm endpoints accept POST with JSON body
- Responses include: result data, execution_time_ms, complexity info
- CORS enabled for frontend-backend communication
- Base URL: `http://localhost:8000/api`

## Important Notes
- All algorithms include complexity analysis in docstrings
- Frontend uses color-coded path highlighting per algorithm
- Error handling returns meaningful messages with HTTP status codes
