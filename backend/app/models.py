"""Pydantic models for Neural Path Finder."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Neuron(BaseModel):
    id: str
    name: str
    cell_type: str
    region: str
    region_label: str
    side: str = "right"
    categories: list[str] = Field(default_factory=list)
    role: str = "interneuron"
    description: str = ""
    neurotransmitter: str | None = None
    source: str = ""


class Connection(BaseModel):
    source: str
    target: str
    synapses: int
    note: str = ""
    claim_level: str = "structural_connectivity"


class QuerySpec(BaseModel):
    kind: Literal["neuron", "type", "region", "category", "name"]
    value: str


class PathFindRequest(BaseModel):
    source: QuerySpec
    destination: QuerySpec
    max_paths: int = 5
    max_depth: int = 10


class PathStep(BaseModel):
    from_neuron: Neuron
    to_neuron: Neuron
    synapses: int
    note: str = ""


class NeuralPath(BaseModel):
    id: str
    rank: int
    label: str
    steps: list[PathStep]
    neuron_ids: list[str]
    hop_count: int
    total_synapses: int
    min_synapses: int
    mean_synapses: float
    score_direct: float
    score_strength: float
    regions: list[str]
    region_labels: list[str]
    explanation: str
    why_this_path: str
    strength_profile: list[dict[str, Any]]
    claim_level: str = "structural_connectivity"


class PathFindResponse(BaseModel):
    source_resolved: list[Neuron]
    destination_resolved: list[Neuron]
    paths: list[NeuralPath]
    hubs: list[dict[str, Any]]
    anatomical_summary: str
    disclaimer: str
    query: PathFindRequest


class CompareRequest(BaseModel):
    path_a: PathFindRequest
    path_b: PathFindRequest


class BranchRequest(BaseModel):
    neuron_id: str
    limit: int = 12
