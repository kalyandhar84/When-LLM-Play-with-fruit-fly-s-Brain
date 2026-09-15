"""Load and index the curated Male CNS exploration graph."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import networkx as nx

from .models import Connection, Neuron, QuerySpec

DATA_PATH = Path(__file__).parent / "data" / "connectome.json"


@lru_cache(maxsize=1)
def load_raw() -> dict:
    with DATA_PATH.open() as f:
        return json.load(f)


def get_meta() -> dict:
    return load_raw()["meta"]


def get_journeys() -> list[dict]:
    return load_raw()["journeys"]


def get_scenarios() -> list[dict]:
    return load_raw().get("scenarios") or []


def get_categories() -> list[str]:
    return load_raw()["categories"]


def get_regions() -> dict[str, str]:
    return load_raw()["regions"]


@lru_cache(maxsize=1)
def neurons_by_id() -> dict[str, Neuron]:
    return {n["id"]: Neuron.model_validate(n) for n in load_raw()["neurons"]}


@lru_cache(maxsize=1)
def connections() -> list[Connection]:
    return [Connection.model_validate(c) for c in load_raw()["connections"]]


@lru_cache(maxsize=1)
def build_graph() -> nx.DiGraph:
    g = nx.DiGraph()
    for neuron in neurons_by_id().values():
        g.add_node(neuron.id, **neuron.model_dump())
    for edge in connections():
        g.add_edge(
            edge.source,
            edge.target,
            synapses=edge.synapses,
            note=edge.note,
            weight=1.0 / max(edge.synapses, 1),
            claim_level=edge.claim_level,
        )
    return g


VALUE_ALIASES = {
    "movement": "motor",
    "moving": "motor",
    "walk": "motor",
    "walking": "motor",
    "motion": "motor",
    "vision": "visual",
    "sight": "visual",
    "seeing": "visual",
    "eye": "visual",
    "eyes": "visual",
    "tv": "visual",
    "smell": "olfactory",
    "odor": "olfactory",
    "odour": "olfactory",
    "hear": "auditory",
    "hearing": "auditory",
    "sound": "auditory",
    "buzz": "auditory",
    "touch": "mechanosensory",
    "zap": "mechanosensory",
    "zapped": "mechanosensory",
    "shock": "mechanosensory",
    "poke": "mechanosensory",
    "heat": "hot",
    "warm": "hot",
    "warmth": "hot",
    "cool": "cold",
    "chill": "cold",
    "food": "taste",
    "sugar": "taste",
    "sweet": "taste",
    "eat": "taste",
}


def _normalize_value(value: str) -> str:
    raw = value.strip().lower()
    return VALUE_ALIASES.get(raw, raw)


def _resolve_kind(kind: str, value: str) -> list[Neuron]:
    neurons = list(neurons_by_id().values())
    value_l = _normalize_value(value)
    if not value_l:
        return []

    if kind == "neuron":
        exact = neurons_by_id().get(value) or neurons_by_id().get(value.strip())
        if exact:
            return [exact]
        lower_ids = {n.id.lower(): n for n in neurons}
        if value_l in lower_ids:
            return [lower_ids[value_l]]
        return [n for n in neurons if n.name.lower() == value_l or n.name.lower() == value.strip().lower()]

    if kind == "name":
        return [n for n in neurons if value_l in n.name.lower() or value_l in n.id.lower()]

    if kind == "type":
        return [n for n in neurons if value_l == n.cell_type.lower() or value_l in n.cell_type.lower()]

    if kind == "region":
        return [
            n
            for n in neurons
            if n.region.lower() == value_l
            or value_l in n.region_label.lower()
            or n.region_label.lower() == value_l
        ]

    if kind == "category":
        hits = [n for n in neurons if any(c.lower() == value_l for c in n.categories)]
        if hits:
            return hits
        return [n for n in neurons if any(value_l in c.lower() for c in n.categories)]

    return []


def resolve_query(spec: QuerySpec) -> list[Neuron]:
    """Resolve a user query; fall back across kinds so 'Visual' still works as a neuron-kind typo."""
    value = spec.value.strip()
    if not value:
        return []

    kind = spec.kind if spec.kind != "auto" else "auto"
    order = [kind] if kind != "auto" else []
    order += [k for k in ("category", "neuron", "type", "name", "region") if k not in order]

    for candidate_kind in order:
        hits = _resolve_kind(candidate_kind, value)
        if hits:
            return hits

    return search_neurons(value, limit=16)


def suggest_queries(value: str) -> list[str]:
    hints = ["R1", "DNg13", "Taste Food", "Visual", "Motor", "GRN_sweet", "LegMN_T1"]
    if not value.strip():
        return hints
    hits = search_neurons(value, limit=6)
    names = [f"{n.id} ({n.name})" for n in hits]
    extras = [h for h in hints if value.strip().lower() not in h.lower()]
    return (names + extras)[:8]


def search_neurons(q: str, limit: int = 25) -> list[Neuron]:
    q = q.strip().lower()
    if not q:
        return list(neurons_by_id().values())[:limit]
    scored: list[tuple[int, Neuron]] = []
    for n in neurons_by_id().values():
        hay = " ".join(
            [
                n.id,
                n.name,
                n.cell_type,
                n.region,
                n.region_label,
                " ".join(n.categories),
                n.role,
            ]
        ).lower()
        if q not in hay:
            continue
        score = 0
        if n.id.lower() == q:
            score += 100
        if n.name.lower().startswith(q):
            score += 50
        if q in n.cell_type.lower():
            score += 30
        if any(q == c.lower() for c in n.categories):
            score += 40
        score += hay.count(q)
        scored.append((score, n))
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return [n for _, n in scored[:limit]]


def neuron_or_raise(neuron_id: str) -> Neuron:
    n = neurons_by_id().get(neuron_id)
    if not n:
        raise KeyError(neuron_id)
    return n


def neighbors(neuron_id: str, direction: str = "both", limit: int = 12) -> dict:
    g = build_graph()
    if neuron_id not in g:
        raise KeyError(neuron_id)

    upstream = []
    downstream = []
    if direction in ("upstream", "both"):
        for pred in g.predecessors(neuron_id):
            data = g.edges[pred, neuron_id]
            upstream.append(
                {
                    "neuron": neurons_by_id()[pred].model_dump(),
                    "synapses": data["synapses"],
                    "note": data.get("note", ""),
                }
            )
        upstream.sort(key=lambda x: -x["synapses"])
        upstream = upstream[:limit]

    if direction in ("downstream", "both"):
        for succ in g.successors(neuron_id):
            data = g.edges[neuron_id, succ]
            downstream.append(
                {
                    "neuron": neurons_by_id()[succ].model_dump(),
                    "synapses": data["synapses"],
                    "note": data.get("note", ""),
                }
            )
        downstream.sort(key=lambda x: -x["synapses"])
        downstream = downstream[:limit]

    return {
        "neuron": neurons_by_id()[neuron_id].model_dump(),
        "upstream": upstream,
        "downstream": downstream,
        "upstream_count": g.in_degree(neuron_id),
        "downstream_count": g.out_degree(neuron_id),
    }


def structural_hubs(limit: int = 8, focus_ids: Iterable[str] | None = None) -> list[dict]:
    """Rank neurons by structural degree / betweenness within the exploration graph."""
    g = build_graph()
    focus = set(focus_ids or [])
    degree = dict(g.degree())
    try:
        betweenness = nx.betweenness_centrality(g, weight=None)
    except Exception:
        betweenness = {n: 0.0 for n in g.nodes}

    ranked = []
    for nid, deg in degree.items():
        n = neurons_by_id()[nid]
        score = deg + 10 * betweenness.get(nid, 0.0)
        if focus and nid in focus:
            score += 5
        ranked.append(
            {
                "neuron": n.model_dump(),
                "degree": deg,
                "in_degree": g.in_degree(nid),
                "out_degree": g.out_degree(nid),
                "betweenness": round(betweenness.get(nid, 0.0), 4),
                "structural_score": round(score, 3),
                "interpretation": (
                    f"{n.name} sits at a high-connectivity position in this exploration graph "
                    f"({deg} structural neighbors). This describes network structure, not proven behavioral importance."
                ),
            }
        )
    ranked.sort(key=lambda x: (-x["structural_score"], -x["degree"], x["neuron"]["name"]))
    if focus:
        # Bring path-participating hubs forward
        in_focus = [h for h in ranked if h["neuron"]["id"] in focus]
        others = [h for h in ranked if h["neuron"]["id"] not in focus]
        ranked = in_focus + others
    return ranked[:limit]
