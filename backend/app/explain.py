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
    if label.startswith("Most direct"):
        reasons.append(
            f"It uses {hops} synaptic step(s), among the fewest intermediate hops connecting the selected endpoints."
        )
    if label == "Most direct · strongest":
        reasons.append(
            f"The same route is also the strongest in this result set (bottleneck {metrics['min_synapses']}, mean {metrics['mean_synapses']})."
        )
    elif label == "Strongest connectivity":
        reasons.append(
            f"Its bottleneck synapse count is {metrics['min_synapses']} and mean connection strength is {metrics['mean_synapses']}, "
            "favoring structurally stronger edges in this graph."
        )
    elif not label.startswith("Most direct"):
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


def playful_story(scenario: dict, path: "NeuralPath | None") -> dict:
    """Plain-language story beats for the tap-to-play exhibit. Structural, not causal."""
    hook = scenario.get("hook") or scenario.get("title", "A fly has an experience.")
    if not path or not path.steps:
        return {
            "headline": hook,
            "beats": [
                hook,
                "No structural path showed up in this small exploration map.",
                "That does not mean the fly cannot sense it — only that this toy graph did not connect those cells.",
            ],
        }

    start = path.steps[0].from_neuron
    end = path.steps[-1].to_neuron
    mids = []
    for step in path.steps[:-1]:
        n = step.to_neuron
        if n.id != end.id:
            mids.append(n)
    mid_names = ", ".join(n.name for n in mids[:3]) if mids else "a few relay cells"
    regions = " → ".join(path.region_labels)
    beats = [
        hook,
        f"Sensors like {start.name} in the {start.region_label} can pick that kind of cue up.",
        f"On this wiring map the signal can hop {path.hop_count} times, visiting {mid_names}.",
        f"It can reach {end.name} in the {end.region_label} — a {end.role} cell that belongs to movement-related circuitry.",
        f"The anatomical trip is: {regions}.",
        "This is a map of physical connections, not a video of the fly deciding or feeling something. Wiring is not the same as behavior.",
    ]
    brain = list(scenario.get("brain_story") or [])
    if path and path.region_labels and not brain:
        brain = [
            f"This wiring map travels { ' → '.join(path.region_labels) }.",
            "Sensory cells can connect through intermediate regions toward descending or motor cells.",
        ]
    actions = list(scenario.get("possible_actions") or [
        "Reach movement-related circuitry — walking, turning, or feeding motors may sit downstream.",
        "That is a possible use of the wires, not a prediction of what the fly will do.",
    ])
    return {
        "headline": hook,
        "beats": beats,
        "brain_story": brain,
        "possible_actions": actions,
    }


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
