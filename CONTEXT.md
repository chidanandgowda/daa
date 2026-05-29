# Cold-Chain Logistics Optimizer — Project Context

## Project Overview
A full-stack web application for RV College of Engineering's DAA course. Models cold-chain logistics as a graph problem where **all five algorithms work together in a pipeline** to solve routing, scheduling, and cargo-loading problems.

## Architecture

```
cold-chain-optimizer/
├── backend/                    # Python FastAPI server
│   ├── app/main.py             # FastAPI entry point + CORS
│   ├── algorithms/             # All 5 algorithm implementations
│   ├── models/                 # Graph class + Pydantic schemas
│   ├── api/routes.py           # REST endpoints + pipeline
│   └── data/sample_data.py     # 12 cities, 23 routes, 12 cargo items
└── frontend/                   # Vanilla JS + Cytoscape.js
    ├── index.html              # 3-column layout
    ├── css/style.css           # Light professional theme
    └── js/                     # app.js, graph.js, api.js, ui.js
```

## Algorithm Pipeline (How They Work Together)

The key design decision: algorithms are **not independent tools** — they form a **unified cold-chain optimization pipeline**:

```
Knapsack → TSP → Dijkstra → A*
```

1. **0/1 Knapsack** — decides WHAT cargo to load on the truck (maximizing value within capacity)
2. **Held-Karp / Nearest Neighbour TSP** — decides WHICH ORDER to visit all delivery cities
3. **Dijkstra** — finds the SHORTEST SAFE PATH between each consecutive pair of TSP stops
4. **A* Search** — REROUTES dynamically if any road segment is blocked (failure simulation)

This is implemented as `POST /api/optimize` — a single endpoint that runs all steps.

## Technology Decisions

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | FastAPI + Python | Async, auto OpenAPI docs, Pydantic validation |
| Frontend | Vanilla JS + Cytoscape.js | No build step, Cytoscape is the gold standard for graphs |
| Theme | Light (white/indigo) | Professional, clean, per user preference |
| Graph | Adjacency list (dict of dicts) | O(V+E) space, ideal for sparse city networks |

## Important Notes
- All algorithms include complexity analysis in docstrings
- The graph uses **undirected edges** (roads go both ways)
- Haversine heuristic in A* is admissible → guarantees optimal rerouting
- Frontend highlights TSP route (indigo), Dijkstra paths (green), A* reroutes (amber)
- Edge blocking: click any edge on the graph to simulate a road failure
