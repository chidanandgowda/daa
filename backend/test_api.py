"""Quick API test script."""
import urllib.request
import json

BASE = "http://localhost:8000"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

def post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read())

# Test 1: Health check
print("=== Health Check ===")
h = get("/")
print(f"  Status: {h['status']}, Project: {h['project']}")

# Test 2: Graph
print("\n=== Graph Data ===")
g = get("/api/graph")
print(f"  Nodes: {g['node_count']}, Edges: {g['edge_count']}")

# Test 3: Held-Karp TSP
print("\n=== Held-Karp TSP (start=DEL) ===")
t = post("/api/tsp", {"start": "DEL"})
r = t["result"]
print(f"  Cost: {r['total_cost']}")
print(f"  Path: {' -> '.join(r['path'])}")
print(f"  Time: {t['execution_time_ms']:.2f} ms")

# Test 4: Nearest Neighbour
print("\n=== Nearest Neighbour TSP (start=DEL) ===")
nn = post("/api/nearest-neighbour", {"start": "DEL"})
r2 = nn["result"]
print(f"  Cost: {r2['total_cost']}")
print(f"  Path: {' -> '.join(r2['path'])}")
print(f"  Time: {nn['execution_time_ms']:.2f} ms")

# Test 5: Dijkstra
print("\n=== Dijkstra (DEL -> BLR) ===")
dj = post("/api/dijkstra", {"source": "DEL", "destination": "BLR", "temp_penalty": True})
r3 = dj["result"]
print(f"  Cost: {r3['total_cost']}")
print(f"  Path: {' -> '.join(r3['path'])}")
print(f"  Nodes explored: {r3['nodes_explored']}")

# Test 6: A* Search
print("\n=== A* Search (DEL -> BLR, blocked MUM-PUN) ===")
a = post("/api/astar", {"source": "DEL", "destination": "BLR", "blocked_edges": [["MUM", "PUN"]]})
r4 = a["result"]
print(f"  Cost: {r4['total_cost']}")
print(f"  Path: {' -> '.join(r4['path'])}")

# Test 7: Knapsack
print("\n=== 0/1 Knapsack (capacity=2000kg) ===")
k = post("/api/knapsack", {"capacity": 2000})
r5 = k["result"]
print(f"  Value: {r5['total_value']}")
print(f"  Weight: {r5['total_weight']} kg")
print(f"  Utilization: {r5['utilization_pct']}%")
print(f"  Items: {', '.join(i['name'] for i in r5['selected_items'])}")

print("\n✅ All tests passed!")
