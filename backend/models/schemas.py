"""
Pydantic Request/Response Schemas for Cold-Chain Logistics Optimizer API.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ── Request Schemas ──────────────────────────────────────────────────────

class TSPRequest(BaseModel):
    start: str = Field(..., description="Starting city node ID", examples=["DEL"])


class DijkstraRequest(BaseModel):
    source: str = Field(..., description="Source city node ID", examples=["DEL"])
    destination: str = Field(..., description="Destination city node ID", examples=["BLR"])
    temp_penalty: bool = Field(True, description="Apply temperature-zone cost penalties")


class AStarRequest(BaseModel):
    source: str = Field(..., description="Source city node ID", examples=["DEL"])
    destination: str = Field(..., description="Destination city node ID", examples=["BLR"])
    blocked_edges: Optional[list[list[str]]] = Field(None, description="Blocked edges as [source, target] pairs")


class KnapsackRequest(BaseModel):
    capacity: float = Field(2000, description="Truck capacity in kg", gt=0)
    items: Optional[list[dict]] = Field(None, description="Custom cargo items")


class PipelineRequest(BaseModel):
    """Full pipeline request — runs all algorithms together."""
    start: str = Field(..., description="Starting/depot city node ID", examples=["DEL"])
    capacity: float = Field(2000, description="Truck capacity in kg", gt=0)
    tsp_method: str = Field("held-karp", description="TSP solver: 'held-karp' or 'nearest-neighbour'")
    blocked_edges: Optional[list[list[str]]] = Field(None, description="Blocked edges for A* rerouting")
    items: Optional[list[dict]] = Field(None, description="Custom cargo items (uses defaults if null)")


# ── Response Schemas ─────────────────────────────────────────────────────

class AlgorithmResult(BaseModel):
    algorithm: str
    result: dict
    execution_time_ms: float
    status: str = "success"


class GraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    node_count: int
    edge_count: int


class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"
