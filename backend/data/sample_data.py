"""
Sample Dataset — Indian Cold-Chain Logistics Network
12 cities with realistic distances, costs, and cold-chain metadata.

Cities chosen from major cold-chain hubs across India covering
diverse temperature zones and warehouse capacities.
"""

from models.graph import Graph, Node, Edge


def build_sample_graph() -> Graph:
    """
    Build and return a sample cold-chain logistics graph with 12 Indian cities.

    The graph represents a realistic cold-chain distribution network with:
    - 12 city nodes with geographic coordinates and temperature zones
    - ~25 weighted edges with distance, cost, and transit metadata
    - Weights are composite: base_cost influenced by distance and road quality

    Returns:
        Graph: Populated graph ready for algorithm execution
    """
    g = Graph()

    # ── Nodes (Cities / Cold-Chain Hubs) ─────────────────────────────────
    cities = [
        Node("DEL", "New Delhi",     28.6139,  77.2090, "hot",      15000),
        Node("MUM", "Mumbai",        19.0760,  72.8777, "hot",      18000),
        Node("BLR", "Bengaluru",     12.9716,  77.5946, "moderate", 16000),
        Node("CHN", "Chennai",       13.0827,  80.2707, "hot",      14000),
        Node("KOL", "Kolkata",       22.5726,  88.3639, "hot",      12000),
        Node("HYD", "Hyderabad",     17.3850,  78.4867, "hot",      13000),
        Node("AHM", "Ahmedabad",     23.0225,  72.5714, "hot",      11000),
        Node("PUN", "Pune",          18.5204,  73.8567, "moderate", 10000),
        Node("JAI", "Jaipur",        26.9124,  75.7873, "hot",       9000),
        Node("LKO", "Lucknow",       26.8467,  80.9462, "moderate", 10000),
        Node("COC", "Kochi",          9.9312,  76.2673, "moderate", 11000),
        Node("VIZ", "Visakhapatnam", 17.6868,  83.2185, "hot",       8000),
    ]

    for city in cities:
        g.add_node(city)

    # ── Edges (Routes) ───────────────────────────────────────────────────
    # Format: (source, target, distance_km, cost, max_transit_hrs, road_quality)
    # Cost is a composite metric: roughly distance * fuel_factor * road_quality
    routes = [
        # Northern corridor
        ("DEL", "JAI",  281,  4200, 5.0, 1.0),
        ("DEL", "LKO",  556,  7800, 9.0, 1.1),
        ("DEL", "AHM",  947, 13500, 15.0, 1.2),

        # Western corridor
        ("AHM", "MUM",  524,  7400, 8.0, 1.0),
        ("MUM", "PUN",  149,  2100, 2.5, 1.0),
        ("AHM", "JAI",  660,  9200, 10.0, 1.3),

        # Southern corridor
        ("PUN", "BLR",  840, 11800, 13.0, 1.1),
        ("BLR", "CHN",  346,  4900, 5.5, 1.0),
        ("BLR", "HYD",  570,  8000, 9.0, 1.1),
        ("BLR", "COC",  557,  7800, 9.0, 1.2),
        ("CHN", "COC",  680,  9500, 11.0, 1.3),

        # Eastern corridor
        ("DEL", "KOL", 1472, 20600, 22.0, 1.4),
        ("KOL", "VIZ",  800, 11200, 13.0, 1.3),
        ("HYD", "VIZ",  623,  8700, 10.0, 1.2),
        ("CHN", "VIZ",  792, 11100, 13.0, 1.2),

        # Cross-country connections
        ("MUM", "HYD",  711, 10000, 11.0, 1.1),
        ("LKO", "KOL",  986, 13800, 16.0, 1.4),
        ("JAI", "LKO",  604,  8500, 10.0, 1.2),
        ("MUM", "BLR",  984, 13800, 15.0, 1.2),
        ("HYD", "CHN",  625,  8800, 10.0, 1.1),
        ("PUN", "HYD",  560,  7800, 9.0, 1.1),
        ("DEL", "MUM", 1400, 19600, 20.0, 1.3),
        ("KOL", "CHN", 1659, 23200, 24.0, 1.5),
    ]

    for src, tgt, dist, cost, transit, quality in routes:
        g.add_edge(Edge(src, tgt, dist, cost, transit, quality))

    return g


# ── Cargo Items for Knapsack ────────────────────────────────────────────

CARGO_ITEMS = [
    {"id": "C01", "name": "Insulin Vials",          "weight_kg":  120, "value": 48000, "temp_req": "cold",     "priority": "critical"},
    {"id": "C02", "name": "Frozen Seafood",          "weight_kg":  800, "value": 32000, "temp_req": "frozen",   "priority": "high"},
    {"id": "C03", "name": "Dairy Products",          "weight_kg":  500, "value": 18000, "temp_req": "cold",     "priority": "medium"},
    {"id": "C04", "name": "Fresh Vegetables",        "weight_kg":  600, "value": 12000, "temp_req": "cool",     "priority": "medium"},
    {"id": "C05", "name": "Vaccine Shipment",        "weight_kg":   80, "value": 95000, "temp_req": "cold",     "priority": "critical"},
    {"id": "C06", "name": "Frozen Meat",             "weight_kg":  900, "value": 36000, "temp_req": "frozen",   "priority": "high"},
    {"id": "C07", "name": "Fruit Pulp Concentrate",  "weight_kg":  400, "value": 15000, "temp_req": "cool",     "priority": "low"},
    {"id": "C08", "name": "Blood Plasma Units",      "weight_kg":   50, "value": 72000, "temp_req": "cold",     "priority": "critical"},
    {"id": "C09", "name": "Ice Cream (Bulk)",        "weight_kg":  700, "value": 21000, "temp_req": "frozen",   "priority": "medium"},
    {"id": "C10", "name": "Biotech Samples",         "weight_kg":   30, "value": 58000, "temp_req": "cold",     "priority": "critical"},
    {"id": "C11", "name": "Fresh Flowers",           "weight_kg":  200, "value":  8000, "temp_req": "cool",     "priority": "low"},
    {"id": "C12", "name": "Cheese Blocks",           "weight_kg":  350, "value": 14000, "temp_req": "cold",     "priority": "medium"},
]
