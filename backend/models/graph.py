"""
Cold-Chain Logistics Optimizer — Graph Model
Adjacency list representation for cold-chain logistics network.

Space Complexity: O(V + E) where V = vertices (cities), E = edges (routes)
"""

from __future__ import annotations
from typing import Optional


class Node:
    """Represents a city/warehouse in the cold-chain network."""

    def __init__(
        self,
        node_id: str,
        name: str,
        latitude: float,
        longitude: float,
        temp_zone: str = "moderate",
        warehouse_capacity_kg: float = 10000.0,
    ):
        self.node_id = node_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.temp_zone = temp_zone  # "cold", "moderate", "hot"
        self.warehouse_capacity_kg = warehouse_capacity_kg

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temp_zone": self.temp_zone,
            "warehouse_capacity_kg": self.warehouse_capacity_kg,
        }


class Edge:
    """Represents a route between two cities with cold-chain metadata."""

    def __init__(
        self,
        source: str,
        target: str,
        distance_km: float,
        cost: float,
        max_transit_hours: float = 24.0,
        road_quality: float = 1.0,  # 1.0 = excellent, 2.0 = poor (multiplier)
    ):
        self.source = source
        self.target = target
        self.distance_km = distance_km
        self.cost = cost
        self.max_transit_hours = max_transit_hours
        self.road_quality = road_quality

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "distance_km": self.distance_km,
            "cost": self.cost,
            "max_transit_hours": self.max_transit_hours,
            "road_quality": self.road_quality,
        }


class Graph:
    """
    Undirected weighted graph using adjacency list representation.

    The graph stores:
      - nodes: dict mapping node_id → Node object
      - adj:   dict mapping node_id → {neighbor_id: Edge, ...}

    Time Complexities:
      - add_node:       O(1)
      - add_edge:       O(1)
      - get_neighbors:  O(1)
      - get_edge:       O(1)
      - get_all_nodes:  O(V)
      - get_all_edges:  O(E)

    Space Complexity: O(V + E)
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.adj: dict[str, dict[str, Edge]] = {}

    def add_node(self, node: Node) -> None:
        """
        Add a node (city) to the graph.

        Time: O(1)
        """
        self.nodes[node.node_id] = node
        if node.node_id not in self.adj:
            self.adj[node.node_id] = {}

    def add_edge(self, edge: Edge, directed: bool = False) -> None:
        """
        Add an edge (route) between two nodes.
        By default, adds in both directions (undirected graph).

        Time: O(1)
        """
        if edge.source not in self.adj:
            self.adj[edge.source] = {}
        if edge.target not in self.adj:
            self.adj[edge.target] = {}

        self.adj[edge.source][edge.target] = edge

        if not directed:
            # Create reverse edge with same properties
            reverse = Edge(
                source=edge.target,
                target=edge.source,
                distance_km=edge.distance_km,
                cost=edge.cost,
                max_transit_hours=edge.max_transit_hours,
                road_quality=edge.road_quality,
            )
            self.adj[edge.target][edge.source] = reverse

    def get_neighbors(self, node_id: str) -> dict[str, Edge]:
        """
        Return all neighbors of a given node.

        Time: O(1)
        Returns: dict mapping neighbor_id → Edge
        """
        return self.adj.get(node_id, {})

    def get_edge(self, source: str, target: str) -> Optional[Edge]:
        """
        Get the edge between two nodes, or None if not connected.

        Time: O(1)
        """
        return self.adj.get(source, {}).get(target, None)

    def get_weight(self, source: str, target: str) -> float:
        """
        Get the cost (weight) of the edge between two nodes.
        Returns float('inf') if no edge exists.

        Time: O(1)
        """
        edge = self.get_edge(source, target)
        return edge.cost if edge else float("inf")

    def get_all_nodes(self) -> list[Node]:
        """Return all nodes. Time: O(V)"""
        return list(self.nodes.values())

    def get_all_edges(self) -> list[Edge]:
        """
        Return all unique edges (avoids duplicates for undirected graphs).

        Time: O(V + E)
        """
        seen = set()
        edges = []
        for src, neighbors in self.adj.items():
            for tgt, edge in neighbors.items():
                edge_key = tuple(sorted([src, tgt]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append(edge)
        return edges

    def get_node_ids(self) -> list[str]:
        """Return sorted list of all node IDs. Time: O(V log V)"""
        return sorted(self.nodes.keys())

    def to_dict(self) -> dict:
        """
        Serialize the entire graph for API response / frontend rendering.

        Returns dict with 'nodes' and 'edges' lists.
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.get_all_edges()],
        }

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.get_all_edges())})"
