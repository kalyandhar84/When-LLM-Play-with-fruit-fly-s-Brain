"""Neural Path Finder API — Google Maps for the male fruit fly connectome."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .explain import playful_story
from .graph import (
    get_categories,
    get_journeys,
    get_meta,
    get_regions,
    get_scenarios,
    neighbors,
    neurons_by_id,
    search_neurons,
    structural_hubs,
)
from .models import BranchRequest, CompareRequest, PathFindRequest
from .pathfinder import compare_paths, find_paths

APP_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = APP_DIR.parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Neural Path Finder",
    description=(
        "Interactive pathway discovery over a curated HHMI Janelia Male CNS "
        "Connectome exploration graph (MaleCNS v1.0)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "product": "Neural Path Finder"}


@app.get("/api/meta")
def meta():
    raw = get_meta()
    return {
        **raw,
        "categories": get_categories(),
        "regions": get_regions(),
        "neuron_count_graph": len(neurons_by_id()),
    }


@app.get("/api/neurons")
def list_neurons(q: str = Query(""), limit: int = Query(40, ge=1, le=200)):
    return [n.model_dump() for n in search_neurons(q, limit=limit)]


@app.get("/api/neurons/{neuron_id}")
def get_neuron(neuron_id: str):
    n = neurons_by_id().get(neuron_id)
    if not n:
        raise HTTPException(404, f"Neuron '{neuron_id}' not found")
    return n.model_dump()


@app.get("/api/neurons/{neuron_id}/neighbors")
def neuron_neighbors(neuron_id: str, limit: int = Query(12, ge=1, le=50)):
    try:
        return neighbors(neuron_id, limit=limit)
    except KeyError:
        raise HTTPException(404, f"Neuron '{neuron_id}' not found") from None


@app.post("/api/branch")
def branch_view(body: BranchRequest):
    try:
        data = neighbors(body.neuron_id, limit=body.limit)
    except KeyError:
        raise HTTPException(404, f"Neuron '{body.neuron_id}' not found") from None
    data["view"] = "branching"
    data["note"] = (
        "A neuron typically participates in a network rather than belonging to a single path. "
        "Upstream and downstream neighbors show where structural connectivity could branch."
    )
    return data


@app.post("/api/paths/find")
def paths_find(body: PathFindRequest):
    return find_paths(body).model_dump()


@app.post("/api/paths/compare")
def paths_compare(body: CompareRequest):
    return compare_paths(body.path_a, body.path_b)


@app.get("/api/journeys")
def journeys():
    return get_journeys()


@app.get("/api/scenarios")
def scenarios():
    return get_scenarios()


@app.get("/api/scenarios/{scenario_id}/run")
def run_scenario(scenario_id: str):
    match = next((s for s in get_scenarios() if s["id"] == scenario_id), None)
    if not match:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    req = PathFindRequest(
        source={"kind": "neuron", "value": match["preferred_source"]},
        destination={"kind": "neuron", "value": match["preferred_destination"]},
        max_paths=5,
    )
    result = find_paths(req)
    top = result.paths[0] if result.paths else None
    return {
        "scenario": match,
        "result": result.model_dump(),
        "story": playful_story(match, top),
    }


@app.get("/api/journeys/{journey_id}/run")
def run_journey(journey_id: str):
    match = next((j for j in get_journeys() if j["id"] == journey_id), None)
    if not match:
        raise HTTPException(404, f"Journey '{journey_id}' not found")
    req = PathFindRequest(
        source={
            "kind": "neuron",
            "value": match["preferred_source"],
        },
        destination={
            "kind": "neuron",
            "value": match["preferred_destination"],
        },
        max_paths=5,
    )
    result = find_paths(req)
    return {"journey": match, "result": result.model_dump()}


@app.get("/api/hubs")
def hubs(limit: int = Query(8, ge=1, le=30)):
    return structural_hubs(limit=limit)


def _frontend_index() -> Path | None:
    index = FRONTEND_DIST / "index.html"
    return index if index.is_file() else None


if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/")
def index():
    index_file = _frontend_index()
    if index_file:
        return FileResponse(index_file)
    return {
        "product": "Neural Path Finder",
        "docs": "/docs",
        "hint": "Build the frontend with `cd frontend && npm install && npm run build`.",
    }


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path in {"docs", "redoc", "openapi.json"}:
        raise HTTPException(status_code=404, detail="Not found")
    index_file = _frontend_index()
    if not index_file:
        raise HTTPException(404, "Frontend is not built yet")
    candidate = FRONTEND_DIST / full_path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(index_file)
