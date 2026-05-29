"""Test the /api/optimize pipeline endpoint."""
import urllib.request
import json

def post(path, data):
    req = urllib.request.Request(
        "http://localhost:8000" + path,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

print("=== Testing Full Pipeline ===\n")

result = post("/api/optimize", {
    "start": "DEL",
    "capacity": 2000,
    "tsp_method": "held-karp",
    "blocked_edges": [["MUM", "PUN"]]
})

p = result["pipeline"]

# Knapsack
ks = p["knapsack"]["result"]
print(f"Step 1 - Knapsack: {len(ks['selected_items'])} items, "
      f"value=Rs.{ks['total_value']}, weight={ks['total_weight']}kg, "
      f"util={ks['utilization_pct']}%")

# TSP
tsp = p["tsp"]["result"]
print(f"Step 2 - Held-Karp TSP: cost={tsp['total_cost']}, "
      f"path={' -> '.join(tsp['path'])}")

# Dijkstra
dj = p["dijkstra"]
print(f"Step 3 - Dijkstra: {len(dj['segments'])} segments, "
      f"total_cost={dj['total_segment_cost']}")

# A*
if "astar" in p:
    astar = p["astar"]
    print(f"Step 4 - A*: {len(astar['segments'])} segments rerouted "
          f"around {len(astar['blocked_edges'])} blocked edges")

print(f"\nTotal pipeline time: {result['total_execution_time_ms']:.2f} ms")
print("\nAll algorithms worked together successfully!")
