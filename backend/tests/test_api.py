"""API and pathfinder coverage for Neural Path Finder."""

from __future__ import annotations

from app.graph import neighbors, resolve_query
from app.models import QuerySpec
from app.pathfinder import compare_paths, find_paths, quick_find


REQUIRED_JOURNEYS = {
    "visual-to-movement",
    "visual-to-dng13",
    "olfactory-to-descending",
    "taste-to-motor",
    "auditory-to-motor",
}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["product"] == "Neural Path Finder"


def test_journeys_exist(client):
    response = client.get("/api/journeys")
    assert response.status_code == 200
    journeys = response.json()
    ids = {j["id"] for j in journeys}
    assert REQUIRED_JOURNEYS <= ids
    assert len(journeys) >= 5


def test_resolve_visual_to_motor():
    visual = resolve_query(QuerySpec(kind="category", value="Visual"))
    motor = resolve_query(QuerySpec(kind="category", value="Motor"))
    assert visual, "Visual category should resolve to neurons"
    assert motor, "Motor category should resolve to neurons"
    assert any("Visual" in n.categories for n in visual)
    assert any("Motor" in n.categories for n in motor)


def test_resolve_visual_motor_and_find_path():
    from app.models import PathFindRequest

    result = find_paths(
        PathFindRequest(
            source=QuerySpec(kind="category", value="Visual"),
            destination=QuerySpec(kind="category", value="Motor"),
        )
    )
    assert result.source_resolved
    assert result.destination_resolved
    assert result.paths, "Visual → Motor should find at least one structural path"
    assert result.paths[0].hop_count >= 1
    assert result.paths[0].steps
    labels = {p.label for p in result.paths}
    assert any(label.startswith("Most direct") for label in labels)
    assert any("Strongest" in label or "strongest" in label for label in labels) or len(result.paths) == 1


def test_r1_to_dng13_finds_a_path(client):
    result = quick_find("neuron", "R1", "neuron", "DNg13")
    assert result.paths, "R1 → DNg13 must find a path in the exploration graph"
    first = result.paths[0]
    assert first.neuron_ids[0] == "R1"
    assert first.neuron_ids[-1] == "DNg13"
    assert first.hop_count >= 1
    assert first.total_synapses > 0
    assert first.explanation
    assert first.why_this_path
    assert first.strength_profile
    assert first.region_labels

    response = client.post(
        "/api/paths/find",
        json={
            "source": {"kind": "neuron", "value": "R1"},
            "destination": {"kind": "neuron", "value": "DNg13"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["paths"]
    assert body["paths"][0]["neuron_ids"][0] == "R1"
    assert "DNg13" in body["paths"][0]["neuron_ids"]


def test_compare_visual_motor_vs_olfactory_motor(client):
    from app.models import PathFindRequest

    payload = {
        "path_a": {
            "source": {"kind": "category", "value": "Visual"},
            "destination": {"kind": "category", "value": "Motor"},
        },
        "path_b": {
            "source": {"kind": "category", "value": "Olfactory"},
            "destination": {"kind": "category", "value": "Motor"},
        },
    }
    response = client.post("/api/paths/compare", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["path_a"]["paths"]
    assert body["path_b"]["paths"]
    assert body["comparison_explanation"]
    assert "disclaimer" in body

    compared = compare_paths(
        PathFindRequest.model_validate(payload["path_a"]),
        PathFindRequest.model_validate(payload["path_b"]),
    )
    assert compared["path_a"]["paths"]
    assert compared["path_b"]["paths"]


def test_neighbors_branching(client):
    data = neighbors("DNg13")
    assert data["neuron"]["id"] == "DNg13"
    assert data["upstream"]
    assert data["downstream"]

    response = client.get("/api/neurons/DNg13/neighbors")
    assert response.status_code == 200
    body = response.json()
    assert body["upstream_count"] >= 1
    assert body["downstream_count"] >= 1

    branched = client.post("/api/branch", json={"neuron_id": "DNg13", "limit": 8})
    assert branched.status_code == 200
    assert branched.json()["view"] == "branching"


def test_search_and_hubs(client):
    search = client.get("/api/neurons", params={"q": "visual"})
    assert search.status_code == 200
    assert search.json()

    hubs = client.get("/api/hubs")
    assert hubs.status_code == 200
    assert hubs.json()
    assert "structural" in hubs.json()[0]["interpretation"].lower()


def test_unknown_neuron_404(client):
    assert client.get("/api/neurons/not-a-neuron").status_code == 404
    assert client.get("/api/neurons/not-a-neuron/neighbors").status_code == 404
