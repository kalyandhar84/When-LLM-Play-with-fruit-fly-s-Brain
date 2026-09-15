"""Natural-language explanations grounded in annotations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .graph import neurons_by_id

if TYPE_CHECKING:
    from .models import NeuralPath


ROLE_PHRASES = {
    "sensory": "receives sensory information from the environment",
    "interneuron": "participates in intermediate processing within the nervous system",
    "descending": "can carry signals from the brain toward the ventral nerve cord",
    "motor": "is associated with motor-related circuitry",
}


def explain_path(node_path: list[str], metrics: dict[str, Any]) -> str:
    neurons = [neurons_by_id()[nid] for nid in node_path]
    start, end = neurons[0], neurons[-1]

    parts = [
        f"This structural pathway begins at {start.name} ({start.cell_type})",
    ]
    if start.categories:
        parts.append(f"in the {', '.join(start.categories)} category")
    parts.append(f"within the {start.region_label}.")

    mid = neurons[1:-1]
    if mid:
        # Highlight a few biologically meaningful intermediates
        highlights = []
        for n in mid:
            if n.role in ("descending", "motor") or "Visual" in n.categories or n.region in {
                "aotu", "lal", "ves", "mb", "lh", "gng", "neck", "vnc", "vnc_t1"
            }:
                highlights.append(n)
        if not highlights:
            highlights = mid[:3]
        else:
            highlights = highlights[:4]
        names = ", ".join(f"{n.name} ({n.region_label})" for n in highlights)
        parts.append(f"It continues through intermediate neurons such as {names}.")

    if any(n.role == "descending" for n in neurons):
        dn = next(n for n in neurons if n.role == "descending")
        parts.append(
            f"{dn.name} is a descending neuron — anatomically positioned to link central brain circuits with the ventral nerve cord."
        )

    parts.append(
        f"The pathway ends at {end.name} ({end.cell_type}) in the {end.region_label}."
    )
    if end.role in ROLE_PHRASES:
        parts.append(f"This destination {ROLE_PHRASES[end.role]}.")

    parts.append(
        f"Across {metrics['steps'] and len(metrics['steps']) or 0} connections, "
        f"synapse counts range from {metrics['min_synapses']} to "
        f"{max((s.synapses for s in metrics['steps']), default=0)} "
        f"(mean {metrics['mean_synapses']})."
    )
    parts.append(
        "These figures describe structural connectivity in the Male CNS exploration graph, "
        "not proven real-time information flow during behavior."
    )
    return " ".join(parts)


def why_this_path(label: str, metrics: dict[str, Any], rank: int, total: int) -> str:
    hops = len(metrics["steps"])
    reasons = [f"Returned as “{label}” (result {rank} of {total})."]
    if label == "Most direct":
        reasons.append(
            f"It uses {hops} synaptic step(s), among the fewest intermediate hops connecting the selected endpoints."
        )
    elif label == "Strongest connectivity":
        reasons.append(
            f"Its bottleneck synapse count is {metrics['min_synapses']} and mean connection strength is {metrics['mean_synapses']}, "
            "favoring structurally stronger edges in this graph."
        )
    else:
        reasons.append(
            "It provides a distinct alternative route, sharing fewer neurons with the primary results while still linking the same endpoints."
        )

    regions = metrics.get("region_labels") or []
    if regions:
        reasons.append(f"Anatomically it travels through: {' → '.join(regions)}.")

    reasons.append(
        "Path ranking uses hop count, synapse-weighted strength, and route diversity — not behavioral validation."
    )
    return " ".join(reasons)


def anatomical_journey(path: "NeuralPath") -> str:
    labels = path.region_labels
    if not labels:
        return "No anatomical regions available for this path."
    journey = " → ".join(labels)
    return (
        f"Anatomical journey: {journey}. "
        "Because Male CNS includes an intact brain–ventral nerve cord connection, "
        "routes can cross from sensory neuropils through central brain regions and into VNC motor-related areas."
    )
