import random
from models.graph import Graph, Node, Edge
from data.indian_cities import INDIAN_CITIES
from algorithms.astar import haversine_distance

def generate_random_graph(num_cities: int = 12) -> Graph:
    """
    Generates a dynamic random graph using real Indian cities.
    Ensures connectivity by first building a minimum spanning tree,
    then randomly adding additional edges for realistic network density.
    """
    g = Graph()
    
    # 1. Randomly select N cities
    num_cities = min(max(3, num_cities), len(INDIAN_CITIES))
    selected_cities_data = random.sample(INDIAN_CITIES, num_cities)
    
    # Add nodes to graph
    selected_nodes = []
    for city_data in selected_cities_data:
        node = Node(
            node_id=city_data["id"],
            name=city_data["name"],
            latitude=city_data["lat"],
            longitude=city_data["lon"],
            temp_zone=city_data["zone"],
            warehouse_capacity_kg=city_data["capacity"]
        )
        g.add_node(node)
        selected_nodes.append(node)
        
    # 2. Build a connected base (spanning tree) to ensure the graph is fully connected
    connected_ids = [selected_nodes[0].node_id]
    unconnected = selected_nodes[1:]
    
    def calculate_edge_attributes(src: Node, tgt: Node):
        # Straight-line distance
        dist_km = haversine_distance(src.latitude, src.longitude, tgt.latitude, tgt.longitude)
        # Apply winding factor for realistic road distance
        road_dist = dist_km * random.uniform(1.1, 1.3)
        
        # Road quality factor (1.0 = excellent, 1.5 = poor)
        # Forward edge
        quality_fwd = round(random.uniform(1.0, 1.5), 1)
        cost_fwd = int(road_dist * 15.0 * quality_fwd)
        transit_fwd = round(road_dist / 50.0, 1)

        # Reverse edge (asymmetric road conditions, e.g. uphill/downhill or traffic)
        quality_rev = round(quality_fwd * random.uniform(0.9, 1.1), 1)
        cost_rev = int(road_dist * 15.0 * quality_rev)
        transit_rev = round(road_dist / 50.0, 1)
        
        return int(road_dist), cost_fwd, transit_fwd, quality_fwd, cost_rev, transit_rev, quality_rev

    edges_to_add = []
    
    # Connect all nodes to form a tree
    while unconnected:
        # Pick a random connected node and a random unconnected node
        src_id = random.choice(connected_ids)
        tgt_node = random.choice(unconnected)
        
        src_node = g.nodes[src_id]
        
        dist, c_fwd, t_fwd, q_fwd, c_rev, t_rev, q_rev = calculate_edge_attributes(src_node, tgt_node)
        edges_to_add.append((Edge(src_id, tgt_node.node_id, dist, c_fwd, t_fwd, q_fwd), True))
        edges_to_add.append((Edge(tgt_node.node_id, src_id, dist, c_rev, t_rev, q_rev), True))
        
        connected_ids.append(tgt_node.node_id)
        unconnected.remove(tgt_node)
        
    # 3. Add additional random edges to create multiple routes/cycles
    # A realistic road network usually has roughly 1.5x to 2.5x as many edges as nodes
    num_extra_edges = int(num_cities * random.uniform(0.5, 1.5))
    
    for _ in range(num_extra_edges):
        src_node = random.choice(selected_nodes)
        tgt_node = random.choice(selected_nodes)
        
        if src_node.node_id != tgt_node.node_id:
            # Check if edge already exists
            if tgt_node.node_id not in g.get_neighbors(src_node.node_id):
                dist, c_fwd, t_fwd, q_fwd, c_rev, t_rev, q_rev = calculate_edge_attributes(src_node, tgt_node)
                edges_to_add.append((Edge(src_node.node_id, tgt_node.node_id, dist, c_fwd, t_fwd, q_fwd), True))
                edges_to_add.append((Edge(tgt_node.node_id, src_node.node_id, dist, c_rev, t_rev, q_rev), True))
                
    # Add all generated edges to the graph
    for edge, directed in edges_to_add:
        g.add_edge(edge, directed=directed)
        
    return g
