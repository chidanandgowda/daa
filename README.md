# 🧊 Cold-Chain Logistics Optimizer

> **Design and Analysis of Algorithms (DAA) Project**
> RV College of Engineering, Bengaluru
> *Ganesh M · Chidanand Gowda · Chirantan*

A full-stack web application that models cold-chain logistics as a graph problem. All five algorithms work together in a **unified optimization pipeline** to solve routing, scheduling, and cargo-loading problems for temperature-sensitive goods.

---

## 🔗 How the Algorithms Work Together

The core idea: **each algorithm solves one piece of the logistics puzzle, and they chain together as a pipeline.**

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────┐
│  0/1 Knapsack│ ──→ │  Held-Karp /  │ ──→ │   Dijkstra   │ ──→ │  A* Search │
│  Cargo Load  │     │  NN (TSP)     │     │  Safe Paths  │     │  Rerouting │
│  Balancing   │     │  Route Plan   │     │  per Segment │     │  on Failure│
└─────────────┘     └───────────────┘     └──────────────┘     └────────────┘
  What to load?       Which order?         Shortest route?      Road blocked?
```

| Step | Algorithm | Problem | Complexity |
|------|-----------|---------|------------|
| 1 | **0/1 Knapsack DP** | Select optimal cargo for the truck | O(n·W) |
| 2 | **Held-Karp TSP** (or Nearest Neighbour) | Plan multi-stop delivery route | O(n²·2ⁿ) / O(n²) |
| 3 | **Dijkstra's Algorithm** | Find shortest safe path between consecutive stops | O((V+E) log V) |
| 4 | **A* Search** | Dynamically reroute if roads are blocked | O(E log V) |

---

## 📁 Project Structure

```
cold-chain-optimizer/
├── backend/
│   ├── app/main.py              # FastAPI entry point
│   ├── algorithms/
│   │   ├── held_karp.py         # Exact TSP (DP + bitmask)
│   │   ├── dijkstra.py          # Shortest safe path
│   │   ├── astar.py             # A* with Haversine heuristic
│   │   ├── knapsack.py          # 0/1 Knapsack DP
│   │   └── nearest_neighbour.py # TSP greedy heuristic
│   ├── models/
│   │   ├── graph.py             # Graph class (adjacency list)
│   │   └── schemas.py           # Pydantic request/response models
│   ├── api/routes.py            # REST API + pipeline endpoint
│   ├── data/sample_data.py      # 12 cities + 12 cargo items
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css            # Light professional theme
│   └── js/
│       ├── app.js               # Pipeline controller
│       ├── graph.js             # Cytoscape.js renderer
│       ├── api.js               # API client
│       └── ui.js                # UI & result display
├── README.md
├── PERFORMANCE_REPORT.md
└── DAA_Abstract.pdf
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- A modern web browser

### 1. Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000` — Swagger docs at `/docs`

### 2. Frontend

```bash
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/graph` | Full graph data (nodes + edges) |
| GET | `/api/cargo` | Cargo items list |
| **POST** | **`/api/optimize`** | **Full pipeline (Knapsack → TSP → Dijkstra → A*)** |
| POST | `/api/tsp` | Held-Karp TSP (standalone) |
| POST | `/api/nearest-neighbour` | NN TSP heuristic (standalone) |
| POST | `/api/dijkstra` | Dijkstra shortest path (standalone) |
| POST | `/api/astar` | A* search (standalone) |
| POST | `/api/knapsack` | Knapsack optimization (standalone) |

### Pipeline Example

```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "start": "DEL",
    "capacity": 2000,
    "tsp_method": "held-karp",
    "blocked_edges": [["MUM", "PUN"]]
  }'
```

---

## 📊 Sample Dataset

- **12 Indian cities**: Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad, Ahmedabad, Pune, Jaipur, Lucknow, Kochi, Visakhapatnam
- **23 weighted routes** with distance, cost, transit time, and road quality
- **12 cargo items**: Insulin, Vaccines, Blood Plasma, Frozen Seafood, Dairy, etc.

---

## ✅ Verified Pipeline Output

```
Step 1 - Knapsack:  6 items selected, ₹341,000 value, 1980 kg (99% utilization)
Step 2 - Held-Karp: Optimal 12-city tour, cost ₹99,900
Step 3 - Dijkstra:  12 shortest-path segments, total ₹110,285
Step 4 - A*:        12 segments rerouted around blocked edge MUM↔PUN
Total pipeline:     43.87 ms
```

---

## 📄 License

Academic project — RV College of Engineering, 2025–26.
