"""Pathway discovery — shortest, strongest, and alternate structural routes."""

from __future__ import annotations

from itertools import islice
from typing import Iterable

import networkx as nx

from .explain import anatomical_journey, explain_path, why_this_path
from .graph import build_graph, neurons_by_id, resolve_query, structural_hubs
from .models import NeuralPath, Neuron, PathFindRequest, PathFindResponse, PathStep, QuerySpec


def _path_metrics(g: nx.DiGraph, node_path: list[str]) -> dict:
    steps: list[PathStep] = []
    synapses: list[int] = []
    for a, b in zip(node_path, node_path[1:]):
        data = g.edges[a, b]
        syn = int(data["synapses"])
        synapses.append(syn)
        steps.append(
            PathStep(
                from_neuron=neurons_by_id()[a],
                to_neuron=neurons_by_id()[b],
                synapses=syn,
                note=data.get("note", ""),
            )
        )
    regions: list[str] = []
    region_labels: list[str] = []
    for nid in node_path:
        n = neurons_by_id()[nid]
        if not regions or regions[-1] != n.region:
            regions.append(n.region)
            region_labels.append(n.region_label)

    total = sum(synapses)
    minimum = min(synapses) if synapses else 0
    mean = (total / len(synapses)) if synapses else 0.0
    # Strength score favors high min-cut-like bottleneck and high mean
    strength = (minimum * 0.6 + mean * 0.4) if synapses else 0.0
    direct = 1.0 / max(len(node_path) - 1, 1)

    strength_profile = [
        {
            "from_id": s.from_neuron.id,
            "to_id": s.to_neuron.id,
            "from_name": s.from_neuron.name,
            "to_name": s.to_neuron.name,
            "synapses": s.synapses,
            "relative": round(s.synapses / max(max(synapses), 1), 3),
            "band": (
                "strong" if s.synapses >= max(synapses) * 0.66 else
                "moderate" if s.synapses >= max(synapses) * 0.33 else
                "weak"
            ),
        }
        for s in steps
    ]

    return {
        "steps": steps,
        "synapses": synapses,
        "total_synapses": total,
        "min_synapses": minimum,
        "mean_synapses": round(mean, 1),
        "score_direct": round(direct, 4),
        "score_strength": round(strength, 2),
        "regions": regions,
        "region_labels": region_labels,
        "strength_profile": strength_profile,
    }


def _enumerate_simple_paths(
    g: nx.DiGraph,
    sources: Iterable[str],
    targets: Iterable[str],
    max_depth: int,
    limit: int = 40,
) -> list[list[str]]:
    found: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    source_list = list(sources)
    target_set = set(targets)

    # Prefer BFS shortest paths first for diversity seeding
    for s in source_list:
        for t in target_set:
            if s == t:
                continue
            try:
                shortest = nx.shortest_path(g, s, t)
                key = tuple(shortest)
                if key not in seen and len(shortest) - 1 <= max_depth:
                    seen.add(key)
                    found.append(shortest)
            except nx.NetworkXNoPath:
                continue

    for s in source_list:
        for t in target_set:
            if s == t:
                continue
            try:
                for path in islice(
                    nx.all_simple_paths(g, s, t, cutoff=max_depth),
                    limit,
                ):
                    key = tuple(path)
                    if key not in seen:
                        seen.add(key)
                        found.append(path)
                        if len(found) >= limit:
                            return found
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
    return found


def _select_diverse_paths(candidates: list[tuple[list[str], dict]], max_paths: int) -> list[tuple[list[str], dict, str]]:
    """Pick most direct, strongest, and diverse alternatives."""
    if not candidates:
        return []

    by_direct = sorted(candidates, key=lambda x: (len(x[0]), -x[1]["score_strength"]))
    by_strength = sorted(candidates, key=lambda x: (-x[1]["score_strength"], len(x[0])))

    selected: list[tuple[list[str], dict, str]] = []
    used: set[tuple[str, ...]] = set()

    def add(item: tuple[list[str], dict], label: str):
        key = tuple(item[0])
        if key in used:
            return
        used.add(key)
        selected.append((item[0], item[1], label))

    add(by_direct[0], "Most direct")
    strongest_other = next((c for c in by_strength if tuple(c[0]) not in used), None)
    if strongest_other:
        add(strongest_other, "Strongest connectivity")
    elif tuple(by_strength[0][0]) == tuple(by_direct[0][0]):
        # Only one unique top path: it is both shortest and strongest
        selected[0] = (selected[0][0], selected[0][1], "Most direct · strongest")

    # Alternatives: maximize Jaccard distance from already selected node sets
    remaining = [c for c in candidates if tuple(c[0]) not in used]
    while len(selected) < max_paths and remaining:
        best = None
        best_score = -1.0
        selected_sets = [set(p[0]) for p in selected]
        for cand in remaining:
            nodes = set(cand[0])
            diversity = min(1 - (len(nodes & s) / max(len(nodes | s), 1)) for s in selected_sets)
            score = diversity * 2 + cand[1]["score_strength"] / 500 + 1 / len(cand[0])
            if score > best_score:
                best_score = score
                best = cand
        if best is None:
            break
        add(best, "Alternative route")
        remaining = [c for c in remaining if tuple(c[0]) not in used]

    return selected[:max_paths]


def _prefer_endpoints(neurons: list[Neuron], *, as_source: bool) -> list[Neuron]:
    """For category queries, start at sensory cells and end at motor/descending cells."""
    if as_source:
        sensory = [n for n in neurons if n.role == "sensory"]
        return sensory or neurons
    motors = [n for n in neurons if n.role == "motor"]
    if motors:
        return motors
    terminals = [n for n in neurons if n.role in ("motor", "descending")]
    return terminals or neurons


def find_paths(req: PathFindRequest) -> PathFindResponse:
    g = build_graph()
    sources = resolve_query(req.source)
    destinations = resolve_query(req.destination)

    if req.source.kind == "category":
        sources = _prefer_endpoints(sources, as_source=True)
    if req.destination.kind == "category":
        destinations = _prefer_endpoints(destinations, as_source=False)

    # Cap pair-wise enumeration so category-wide searches stay interactive
    sources = sources[:8]
    destinations = destinations[:8]

    if not sources or not destinations:
        return PathFindResponse(
            source_resolved=sources,
            destination_resolved=destinations,
            paths=[],
            hubs=[],
            anatomical_summary="No matching source or destination neurons were found for this query.",
            disclaimer=get_disclaimer(),
            query=req,
        )

    source_ids = [n.id for n in sources]
    dest_ids = [n.id for n in destinations]
    raw_paths = _enumerate_simple_paths(g, source_ids, dest_ids, req.max_depth)

    measured: list[tuple[list[str], dict]] = []
    for path in raw_paths:
        measured.append((path, _path_metrics(g, path)))

    chosen = _select_diverse_paths(measured, req.max_paths)
    neural_paths: list[NeuralPath] = []
    all_nodes: set[str] = set()

    for rank, (node_path, metrics, label) in enumerate(chosen, start=1):
        all_nodes.update(node_path)
        explanation = explain_path(node_path, metrics)
        why = why_this_path(label, metrics, rank, len(chosen))
        neural_paths.append(
            NeuralPath(
                id=f"path-{rank}-{'/'.join(node_path)}",
                rank=rank,
                label=label,
                steps=metrics["steps"],
                neuron_ids=node_path,
                hop_count=len(node_path) - 1,
                total_synapses=metrics["total_synapses"],
                min_synapses=metrics["min_synapses"],
                mean_synapses=metrics["mean_synapses"],
                score_direct=metrics["score_direct"],
                score_strength=metrics["score_strength"],
                regions=metrics["regions"],
                region_labels=metrics["region_labels"],
                explanation=explanation,
                why_this_path=why,
                strength_profile=metrics["strength_profile"],
            )
        )

    hubs = structural_hubs(limit=6, focus_ids=all_nodes)
    summary = anatomical_journey(neural_paths[0]) if neural_paths else "No structural path found in the exploration graph."

    return PathFindResponse(
        source_resolved=sources,
        destination_resolved=destinations,
        paths=neural_paths,
        hubs=hubs,
        anatomical_summary=summary,
        disclaimer=get_disclaimer(),
        query=req,
    )


def get_disclaimer() -> str:
    from .graph import get_meta

    return get_meta()["disclaimer"]


def compare_paths(path_a: PathFindRequest, path_b: PathFindRequest) -> dict:
    a = find_paths(path_a)
    b = find_paths(path_b)
    best_a = a.paths[0] if a.paths else None
    best_b = b.paths[0] if b.paths else None

    shared_neurons: list[str] = []
    shared_regions: list[str] = []
    only_a: list[str] = []
    only_b: list[str] = []

    if best_a and best_b:
        set_a = set(best_a.neuron_ids)
        set_b = set(best_b.neuron_ids)
        shared_neurons = sorted(set_a & set_b)
        only_a = sorted(set_a - set_b)
        only_b = sorted(set_b - set_a)
        shared_regions = sorted(set(best_a.region_labels) & set(best_b.region_labels))

    convergence = None
    if best_a and best_b:
        for nid in best_a.neuron_ids:
            if nid in best_b.neuron_ids and nid not in (best_a.neuron_ids[0],):
                convergence = neurons_by_id()[nid].model_dump()
                # prefer late shared neuron
        for nid in reversed(best_a.neuron_ids):
            if nid in set(best_b.neuron_ids):
                convergence = neurons_by_id()[nid].model_dump()
                break

    narrative_parts = []
    if best_a and best_b:
        narrative_parts.append(
            f"Path A travels {best_a.hop_count} steps through {', '.join(best_a.region_labels)}."
        )
        narrative_parts.append(
            f"Path B travels {best_b.hop_count} steps through {', '.join(best_b.region_labels)}."
        )
        if shared_regions:
            narrative_parts.append(
                f"They share anatomical territories: {', '.join(shared_regions)}."
            )
        if shared_neurons:
            names = [neurons_by_id()[i].name for i in shared_neurons]
            narrative_parts.append(
                f"Shared neurons include {', '.join(names)}. Shared nodes suggest structural convergence opportunities, not identical real-time activity."
            )
        else:
            narrative_parts.append(
                "These top routes do not share individual neurons in the exploration graph, though they may still meet in broader Male CNS circuitry."
            )
        if convergence:
            narrative_parts.append(
                f"A notable convergence candidate is {convergence['name']} ({convergence['cell_type']})."
            )
    else:
        narrative_parts.append("One or both queries did not yield a structural path in the curated graph.")

    return {
        "path_a": a.model_dump(),
        "path_b": b.model_dump(),
        "shared_neuron_ids": shared_neurons,
        "shared_regions": shared_regions,
        "only_in_a": only_a,
        "only_in_b": only_b,
        "convergence_neuron": convergence,
        "comparison_explanation": " ".join(narrative_parts),
        "disclaimer": get_disclaimer(),
    }


def quick_find(
    source_kind: str,
    source_value: str,
    dest_kind: str,
    dest_value: str,
    max_paths: int = 5,
) -> PathFindResponse:
    return find_paths(
        PathFindRequest(
            source=QuerySpec(kind=source_kind, value=source_value),  # type: ignore[arg-type]
            destination=QuerySpec(kind=dest_kind, value=dest_value),  # type: ignore[arg-type]
            max_paths=max_paths,
        )
    )
