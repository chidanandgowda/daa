# 🧊 Cold-Chain Logistics Optimizer

> **Design and Analysis of Algorithms (DAA) Project**
> RV College of Engineering, Bengaluru

A full-stack web application that models cold-chain logistics as a graph problem, providing optimal routing and cargo decisions with interactive visualization using **Cytoscape.js**.

---

## 📸 Features

- **Interactive Graph Visualization** — 12 Indian cold-chain cities rendered geographically with Cytoscape.js
- **5 Algorithm Implementations** with full complexity analysis:
  | Algorithm | Type | Complexity | Purpose |
  |-----------|------|------------|---------|
  | Held-Karp | Exact TSP | O(n²·2ⁿ) | Optimal multi-stop route |
  | Nearest Neighbour | TSP Heuristic | O(n²) | Fast approximate route |
  | Dijkstra | Shortest Path | O((V+E)·log V) | Temperature-safe routing |
  | A* Search | Informed Search | O(E·log V) | Dynamic rerouting with blocked roads |
  | 0/1 Knapsack | DP | O(n·W) | Cargo load balancing |

- **Color-Coded Path Highlighting** — Each algorithm uses a distinct color
- **Edge Blocking** — Click edges to simulate route failures (A* mode)
- **Temperature Penalties** — Cold-chain safety-aware edge weighting
- **Real-Time Results** — Execution time, cost, path, and complexity displayed instantly
- **Premium Dark Theme** with glassmorphism and smooth animations

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, Pydantic, Uvicorn |
| Frontend | Vanilla JS, Cytoscape.js, CSS3 |
| Graph | Adjacency List (dict of dicts) |
| API | REST (JSON), auto-generated OpenAPI docs |

---

## 📁 Project Structure

```
cold-chain-optimizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   └── config.py            # Configuration
│   ├── algorithms/
│   │   ├── held_karp.py         # Exact TSP (DP + bitmask)
│   │   ├── dijkstra.py          # Shortest safe path
│   │   ├── astar.py             # A* with Haversine heuristic
│   │   ├── knapsack.py          # 0/1 Knapsack DP
│   │   └── nearest_neighbour.py # TSP greedy heuristic
│   ├── models/
│   │   ├── graph.py             # Graph class (adjacency list)
│   │   └── schemas.py           # Pydantic models
│   ├── api/
│   │   └── routes.py            # REST API endpoints
│   ├── data/
│   │   └── sample_data.py       # 12 cities + 12 cargo items
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js               # Main controller
│       ├── graph.js             # Cytoscape.js renderer
│       ├── api.js               # API client
│       └── ui.js                # UI interactions
├── README.md
├── PERFORMANCE_REPORT.md
├── TASK_PLAN.md
├── PROGRESS.md
└── CONTEXT.md
```

---

## 🚀 Setup & Run

### Prerequisites
- **Python 3.10+** installed
- **pip** package manager
- A modern web browser (Chrome, Firefox, Edge)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend Setup

Open `frontend/index.html` directly in a browser, or serve it:

```bash
# Option A: Python HTTP server
cd frontend
python -m http.server 5500

# Option B: VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

Frontend will be at: `http://localhost:5500`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/graph` | Get full graph (nodes + edges) |
| GET | `/api/cargo` | Get cargo items list |
| POST | `/api/tsp` | Run Held-Karp exact TSP |
| POST | `/api/dijkstra` | Shortest path (Dijkstra) |
| POST | `/api/astar` | A* search with blocked edges |
| POST | `/api/knapsack` | 0/1 Knapsack optimization |
| POST | `/api/nearest-neighbour` | Nearest Neighbour TSP |

### Example: Run Held-Karp TSP
```bash
curl -X POST http://localhost:8000/api/tsp \
  -H "Content-Type: application/json" \
  -d '{"start": "DEL"}'
```

---

## 📊 Sample Dataset

**12 Indian Cities** on major cold-chain corridors:
Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad, Ahmedabad, Pune, Jaipur, Lucknow, Kochi, Visakhapatnam

**12 Cargo Items** including:
Insulin Vials, Frozen Seafood, Vaccine Shipments, Blood Plasma, Biotech Samples, and more.

---

## 👤 Author

DAA Course Project — RV College of Engineering

---

## 📄 License

This project is for academic purposes.
