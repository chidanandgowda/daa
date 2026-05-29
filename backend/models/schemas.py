"""
Pydantic Request/Response Schemas for Cold-Chain Logistics Optimizer API.

Provides input validation, serialization, and automatic OpenAPI documentation.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ── Request Schemas ──────────────────────────────────────────────────────

class TSPRequest(BaseModel):
    """Request body for TSP algorithms (Held-Karp and Nearest Neighbour)."""
    start: str = Field(
        ...,
        description="Starting city node ID (e.g., 'DEL')",
        examples=["DEL"],
    )


class DijkstraRequest(BaseModel):
    """Request body for Dijkstra's shortest path."""
    source: str = Field(..., description="Source city node ID", examples=["DEL"])
    destination: str = Field(..., description="Destination city node ID", examples=["BLR"])
    temp_penalty: bool = Field(
        True,
        description="Apply temperature-zone cost penalties",
    )


class AStarRequest(BaseModel):
    """Request body for A* search with optional blocked edges."""
    source: str = Field(..., description="Source city node ID", examples=["DEL"])
    destination: str = Field(..., description="Destination city node ID", examples=["BLR"])
    blocked_edges: Optional[list[list[str]]] = Field(
        None,
        description="List of blocked edges as [source, target] pairs",
        examples=[[["MUM", "PUN"], ["DEL", "JAI"]]],
    )


class KnapsackRequest(BaseModel):
    """Request body for 0/1 Knapsack cargo optimization."""
    capacity: float = Field(
        2000,
        description="Truck capacity in kg",
        gt=0,
        examples=[2000],
    )
    items: Optional[list[dict]] = Field(
        None,
        description="Custom cargo items (uses sample data if not provided)",
    )


# ── Response Schemas ─────────────────────────────────────────────────────

class AlgorithmResult(BaseModel):
    """Standard response for all algorithm endpoints."""
    algorithm: str = Field(..., description="Algorithm name")
    result: dict = Field(..., description="Algorithm output data")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    status: str = Field("success", description="Execution status")


class GraphResponse(BaseModel):
    """Response for the graph data endpoint."""
    nodes: list[dict]
    edges: list[dict]
    node_count: int
    edge_count: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    status: str = "error"
