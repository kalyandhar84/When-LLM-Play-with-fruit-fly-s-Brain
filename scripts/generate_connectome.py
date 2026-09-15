#!/usr/bin/env python3
"""Generate a curated Male CNS exploration subgraph for Neural Path Finder.

This is a teaching/demo graph grounded in published Male CNS cell types and
known Drosophila sensory–motor circuit motifs (including the Janelia R1–R6 →
DNg13 visual–motor example). Synapse weights are representative structural
strengths for exploration — not a full dump of MaleCNS v1.0 (~166k neurons /
~125M synapses).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "backend" / "app" / "data" / "connectome.json"

# Regions used for Anatomical Journey summaries
REGIONS = {
    "retina": "Retina / Photoreceptors",
    "lamina": "Lamina (Optic Lobe)",
    "medulla": "Medulla (Optic Lobe)",
    "lobula": "Lobula (Optic Lobe)",
    "lobula_plate": "Lobula Plate (Optic Lobe)",
    "aotu": "Anterior Optic Tubercle",
    "avlp": "Anterior Ventrolateral Protocerebrum",
    "pvlp": "Posterior Ventrolateral Protocerebrum",
    "lal": "Lateral Accessory Lobe",
    "ves": "Vest",
    "gng": "Gnathal Ganglia",
    "al": "Antennal Lobe",
    "mb": "Mushroom Body",
    "lh": "Lateral Horn",
    "sez": "Subesophageal Zone",
    "ammc": "Antennal Mechanosensory and Motor Center",
    "arista": "Antennal Arista (Thermosensors)",
    "pal": "Posterior Antennal Lobe",
    "wed": "Wedge",
    "sps": "Superior Posterior Slope",
    "neck": "Neck Connective",
    "vnc_t1": "Ventral Nerve Cord — T1 Leg Neuropil",
    "vnc_t2": "Ventral Nerve Cord — T2 Leg Neuropil",
    "vnc_t3": "Ventral Nerve Cord — T3 Leg Neuropil",
    "vnc": "Ventral Nerve Cord",
    "central_brain": "Central Brain",
}


def N(
    nid: str,
    name: str,
    cell_type: str,
    region: str,
    *,
    side: str = "right",
    categories: list[str] | None = None,
    role: str = "interneuron",
    description: str = "",
    neurotransmitter: str | None = None,
):
    return {
        "id": nid,
        "name": name,
        "cell_type": cell_type,
        "region": region,
        "region_label": REGIONS[region],
        "side": side,
        "categories": categories or [],
        "role": role,
        "description": description,
        "neurotransmitter": neurotransmitter,
        "source": "MaleCNS v1.0 curated exploration graph (Janelia FlyEM)",
    }


def E(src: str, dst: str, synapses: int, note: str = ""):
    return {
        "source": src,
        "target": dst,
        "synapses": synapses,
        "note": note,
        "claim_level": "structural_connectivity",
    }


def stable_mod(seed: str, modulus: int) -> int:
    """Deterministic alternative to hash() — PYTHONHASHSEED would otherwise change weights."""
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulus


neurons: list[dict] = []
edges: list[dict] = []

# ---------------------------------------------------------------------------
# Visual system (R1–R6 → optic lobe → central brain)
# ---------------------------------------------------------------------------
neurons += [
    N("R1", "R1 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor that detects light and begins visual object detection pathways.", neurotransmitter="Histamine"),
    N("R2", "R2 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor contributing to motion and object vision.", neurotransmitter="Histamine"),
    N("R3", "R3 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor in the R1–R6 group highlighted in Janelia visual–motor examples.", neurotransmitter="Histamine"),
    N("R4", "R4 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor feeding lamina circuitry.", neurotransmitter="Histamine"),
    N("R5", "R5 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor in early visual transduction.", neurotransmitter="Histamine"),
    N("R6", "R6 photoreceptor", "R1-R6", "retina", categories=["Visual", "Sensory"], role="sensory",
      description="Outer photoreceptor completing the R1–R6 visual receptor group.", neurotransmitter="Histamine"),
    N("L1", "L1 lamina neuron", "L1", "lamina", categories=["Visual"], role="interneuron",
      description="Lamina monopolar neuron that relays photoreceptor signals into the medulla.", neurotransmitter="ACh"),
    N("L2", "L2 lamina neuron", "L2", "lamina", categories=["Visual"], role="interneuron",
      description="Lamina monopolar neuron involved in motion-related visual processing.", neurotransmitter="ACh"),
    N("L3", "L3 lamina neuron", "L3", "lamina", categories=["Visual"], role="interneuron",
      description="Lamina neuron contributing to feature pathways beyond elementary motion.", neurotransmitter="ACh"),
    N("Mi1", "Mi1 medulla intrinsic", "Mi1", "medulla", categories=["Visual"],
      description="Medulla intrinsic neuron in ON-pathway visual computation."),
    N("Tm3", "Tm3 transmedullary", "Tm3", "medulla", categories=["Visual"],
      description="Transmedullary neuron carrying medulla signals toward deeper optic lobe layers."),
    N("TmY3", "TmY3 neuron", "TmY3", "medulla", categories=["Visual"],
      description="TmY neuron linking medulla and lobula complex processing."),
    N("T4", "T4 directional neuron", "T4", "medulla", categories=["Visual"],
      description="Direction-selective neuron contributing to motion vision."),
    N("T5", "T5 directional neuron", "T5", "lobula", categories=["Visual"],
      description="Direction-selective neuron in lobula motion pathways."),
    N("LC10", "LC10 lobula columnar", "LC10", "lobula", categories=["Visual"],
      description="Lobula columnar projection neuron associated with object-related visual features."),
    N("LC11", "LC11 lobula columnar", "LC11", "lobula", categories=["Visual"],
      description="Lobula columnar neuron projecting visual information into central brain targets."),
    N("LoVP90b", "LoVP90b", "LoVP90b", "lobula", categories=["Visual"],
      description="Lobula visual projection type listed among Male CNS partners near descending circuits.", neurotransmitter="ACh"),
    N("LoVP92", "LoVP92", "LoVP92", "lobula", categories=["Visual"],
      description="Lobula visual projection neuron type with Male CNS connectivity toward descending circuitry.", neurotransmitter="ACh"),
    N("AOTU002", "AOTU002", "AOTU002", "aotu", categories=["Visual"],
      description="Anterior optic tubercle neuron type; Male CNS lists AOTU002 variants among DNg13 upstream partners.", neurotransmitter="ACh"),
    N("AOTU015", "AOTU015", "AOTU015", "aotu", categories=["Visual"],
      description="AOTU projection neuron linking optic information into central brain sensorimotor areas.", neurotransmitter="ACh"),
    N("AOTU016", "AOTU016_c", "AOTU016", "aotu", categories=["Visual"],
      description="AOTU type with Male CNS connectivity toward DNg13-related circuits.", neurotransmitter="ACh"),
]

# Photoreceptor → lamina
for r in ["R1", "R2", "R3", "R4", "R5", "R6"]:
    edges += [
        E(r, "L1", 85 + stable_mod(r, 40)),
        E(r, "L2", 70 + stable_mod(r[::-1], 35)),
        E(r, "L3", 40 + stable_mod(r, 20)),
    ]

edges += [
    E("L1", "Mi1", 120),
    E("L1", "Tm3", 95),
    E("L2", "Tm3", 110),
    E("L2", "T4", 88),
    E("L3", "TmY3", 76),
    E("Mi1", "Tm3", 64),
    E("Mi1", "T4", 52),
    E("Tm3", "LC10", 140),
    E("Tm3", "LC11", 98),
    E("Tm3", "LoVP92", 72),
    E("TmY3", "LC11", 81),
    E("TmY3", "LoVP90b", 66),
    E("T4", "T5", 55),
    E("T5", "LC10", 48),
    E("LC10", "AOTU002", 156),
    E("LC10", "AOTU015", 92),
    E("LC11", "AOTU015", 118),
    E("LC11", "AOTU016", 87),
    E("LoVP92", "AOTU002", 74),
    E("LoVP90b", "AOTU016", 61),
    E("AOTU002", "LAL073", 47),
    E("AOTU002", "VES200m", 38),
    E("AOTU015", "LAL083", 42),
    E("AOTU015", "AVLP713m", 55),
    E("AOTU016", "LAL073", 39),
    E("AOTU016", "PVLP201m", 44),
]

# ---------------------------------------------------------------------------
# Central brain intermediates feeding DNg13 (from Cell Type Explorer partners)
# ---------------------------------------------------------------------------
neurons += [
    N("LAL073", "LAL073", "LAL073", "lal", categories=["Central"],
      description="Lateral accessory lobe neuron; strong Male CNS upstream partner of DNg13.", neurotransmitter="Glu"),
    N("LAL083", "LAL083", "LAL083", "lal", categories=["Central"],
      description="LAL neuron type contributing to descending-neuron input.", neurotransmitter="Glu"),
    N("LAL015", "LAL015", "LAL015", "lal", categories=["Central"],
      description="LAL intermediate with documented Male CNS connectivity toward DNg13.", neurotransmitter="ACh"),
    N("VES200m", "VES200m", "VES200m", "ves", categories=["Central"],
      description="Vest neuron group; top Male CNS upstream partner type of DNg13 by synapse count.", neurotransmitter="Glu"),
    N("VES045", "VES045", "VES045", "ves", categories=["Central"],
      description="Vest neuron providing structural input toward DNg13.", neurotransmitter="GABA"),
    N("VES005", "VES005", "VES005", "ves", categories=["Central"],
      description="Vest intermediate in descending motor pathways.", neurotransmitter="ACh"),
    N("CB0244", "CB0244", "CB0244", "central_brain", categories=["Central"],
      description="Central brain neuron listed among strong DNg13 upstream partners.", neurotransmitter="ACh"),
    N("GNG532", "GNG532", "GNG532", "gng", categories=["Central"],
      description="Gnathal ganglia neuron contributing inputs toward DNg13.", neurotransmitter="ACh"),
    N("AVLP713m", "AVLP713m", "AVLP713m", "avlp", categories=["Visual", "Central"],
      description="AVLP neuron linking visual-related areas into descending circuits.", neurotransmitter="ACh"),
    N("PVLP201m", "PVLP201m_d", "PVLP201m", "pvlp", categories=["Visual", "Central"],
      description="PVLP neuron near visual projection targets in Male CNS annotations.", neurotransmitter="ACh"),
    N("WED_vis", "WED visual relay", "WED-relay", "wed", categories=["Visual", "Central"],
      description="Wedge relay used here as an alternate visual–descending route."),
]

edges += [
    E("LAL073", "DNg13", 164, "Male CNS Cell Type Explorer lists LAL073 among strong DNg13 inputs"),
    E("LAL083", "DNg13", 101),
    E("LAL015", "DNg13", 69),
    E("VES200m", "DNg13", 181, "Top-ranked upstream partner type for DNg13 in Male CNS explorer"),
    E("VES045", "DNg13", 107),
    E("VES005", "DNg13", 93),
    E("CB0244", "DNg13", 162),
    E("GNG532", "DNg13", 157),
    E("AVLP713m", "DNg13", 63),
    E("AVLP713m", "LAL073", 48),
    E("PVLP201m", "VES200m", 36),
    E("PVLP201m", "DNg13", 20),
    E("AOTU015", "WED_vis", 34),
    E("WED_vis", "VES045", 41),
    E("LC10", "AVLP713m", 58),
    E("LAL073", "CB0244", 28),
    E("VES200m", "CB0244", 22),
]

# ---------------------------------------------------------------------------
# Descending + motor (DNg13 → VNC leg neuropils)
# ---------------------------------------------------------------------------
neurons += [
    N("DNg13", "DNg13 descending neuron", "DNg13", "neck", categories=["Motor", "Descending"], role="descending",
      description="Descending neuron highlighted by Janelia as a visual–motor pathway endpoint from R1–R6. Strong outputs into leg neuropils.",
      neurotransmitter="ACh"),
    N("DNp56", "DNp56 descending neuron", "DNp56", "neck", categories=["Motor", "Descending"], role="descending",
      description="Descending neuron type that also appears among Male CNS partners near DNg13 circuitry.", neurotransmitter="ACh"),
    N("DNg97", "DNg97 descending neuron", "DNg97", "neck", categories=["Motor", "Descending"], role="descending",
      description="Descending neuron participating in brain-to-VNC communication.", neurotransmitter="ACh"),
    N("IN19A015", "IN19A015 VNC interneuron", "IN19A015", "vnc", categories=["Motor"], role="interneuron",
      description="VNC interneuron type listed among DNg13-related Male CNS partners.", neurotransmitter="GABA"),
    N("LegMN_T1", "T1 leg motor neuron", "LegMN-T1", "vnc_t1", categories=["Motor"], role="motor",
      description="Representative front-leg motor-related neuron in T1 neuropil (DNg13 strongly outputs to LegNp(T1))."),
    N("LegMN_T2", "T2 leg motor neuron", "LegMN-T2", "vnc_t2", categories=["Motor"], role="motor",
      description="Representative mid-leg motor-related neuron in T2 neuropil."),
    N("LegMN_T3", "T3 leg motor neuron", "LegMN-T3", "vnc_t3", categories=["Motor"], role="motor",
      description="Representative hind-leg motor-related neuron in T3 neuropil."),
]

edges += [
    E("DNg13", "IN19A015", 80),
    E("DNg13", "LegMN_T1", 420, "DNg13 shows strong Male CNS output into LegNp(T1)"),
    E("DNg13", "LegMN_T2", 290),
    E("DNg13", "LegMN_T3", 250),
    E("IN19A015", "LegMN_T1", 95),
    E("IN19A015", "LegMN_T2", 70),
    E("DNp56", "LegMN_T1", 110),
    E("DNg97", "LegMN_T2", 88),
    E("LAL083", "DNp56", 45),
    E("VES005", "DNg97", 52),
    E("CB0244", "DNp56", 37),
]

# ---------------------------------------------------------------------------
# Olfactory pathway
# ---------------------------------------------------------------------------
neurons += [
    N("ORN_DM1", "ORN DM1", "ORN-DM1", "al", categories=["Olfactory", "Sensory"], role="sensory",
      description="Olfactory receptor neuron tuned to antennal lobe glomerulus DM1.", neurotransmitter="ACh"),
    N("ORN_VA1v", "ORN VA1v", "ORN-VA1v", "al", categories=["Olfactory", "Sensory"], role="sensory",
      description="Olfactory receptor neuron associated with pheromone-related glomerulus VA1v."),
    N("ORN_DL5", "ORN DL5", "ORN-DL5", "al", categories=["Olfactory", "Sensory"], role="sensory",
      description="Olfactory receptor neuron feeding glomerulus DL5."),
    N("PN_DM1", "Projection neuron DM1", "uPN-DM1", "al", categories=["Olfactory"],
      description="Uniglomerular projection neuron carrying DM1 olfactory information to MB and LH."),
    N("PN_VA1v", "Projection neuron VA1v", "uPN-VA1v", "al", categories=["Olfactory"],
      description="Projection neuron for VA1v olfactory channel."),
    N("PN_DL5", "Projection neuron DL5", "uPN-DL5", "al", categories=["Olfactory"],
      description="Projection neuron for DL5 olfactory channel."),
    N("KC_ab", "Kenyon cell αβ", "KC-ab", "mb", categories=["Olfactory"],
      description="Mushroom body Kenyon cell integrating olfactory projection-neuron input."),
    N("MBON35", "MBON35", "MBON35", "mb", categories=["Olfactory", "Central"],
      description="Mushroom body output neuron; Male CNS lists MBON35 among DNg13 upstream partners.", neurotransmitter="ACh"),
    N("LH_ON1", "Lateral horn ON1", "LH-ON1", "lh", categories=["Olfactory"],
      description="Lateral horn neuron participating in innate olfactory routes."),
    N("SMP471", "SMP471", "SMP471", "central_brain", categories=["Olfactory", "Central"],
      description="Superior medial protocerebrum neuron listed among DNg13 partners in Male CNS.", neurotransmitter="ACh"),
]

edges += [
    E("ORN_DM1", "PN_DM1", 210),
    E("ORN_VA1v", "PN_VA1v", 180),
    E("ORN_DL5", "PN_DL5", 160),
    E("PN_DM1", "KC_ab", 95),
    E("PN_DM1", "LH_ON1", 120),
    E("PN_VA1v", "LH_ON1", 110),
    E("PN_VA1v", "KC_ab", 70),
    E("PN_DL5", "KC_ab", 88),
    E("PN_DL5", "LH_ON1", 64),
    E("KC_ab", "MBON35", 145),
    E("LH_ON1", "SMP471", 76),
    E("LH_ON1", "GNG532", 58),
    E("MBON35", "DNg13", 38, "Male CNS explorer lists MBON35 among DNg13 inputs"),
    E("MBON35", "DNp56", 42),
    E("SMP471", "DNg13", 48),
    E("SMP471", "LAL015", 33),
    E("MBON35", "LAL083", 29),
]

# ---------------------------------------------------------------------------
# Auditory pathway
# ---------------------------------------------------------------------------
neurons += [
    N("JO_A", "Johnston's organ A", "JO-A", "ammc", categories=["Auditory", "Mechanosensory", "Sensory"], role="sensory",
      description="Johnston's organ neuron: antennal vibration used for hearing and mechanosensation."),
    N("JO_B", "Johnston's organ B", "JO-B", "ammc", categories=["Auditory", "Mechanosensory", "Sensory"], role="sensory",
      description="Johnston's organ neuron conveying antennal vibration and wind-like mechanical cues."),
    N("AMMC_A1", "AMMC A1", "AMMC-A1", "ammc", categories=["Auditory"],
      description="First-order auditory interneuron in the AMMC."),
    N("AMMC_B1", "AMMC B1", "AMMC-B1", "ammc", categories=["Auditory"],
      description="Auditory interneuron integrating JO input."),
    N("WED_aud", "WED auditory relay", "WED-aud", "wed", categories=["Auditory", "Central"],
      description="Wedge neuron linking auditory pathways into central sensorimotor areas."),
    N("AVLP_aud", "AVLP auditory relay", "AVLP-aud", "avlp", categories=["Auditory", "Central"],
      description="AVLP relay for auditory information approaching descending neurons."),
]

edges += [
    E("JO_A", "AMMC_A1", 150),
    E("JO_B", "AMMC_B1", 132),
    E("JO_A", "AMMC_B1", 48),
    E("AMMC_A1", "WED_aud", 96),
    E("AMMC_B1", "WED_aud", 84),
    E("AMMC_B1", "AVLP_aud", 71),
    E("WED_aud", "VES045", 54),
    E("WED_aud", "GNG532", 47),
    E("AVLP_aud", "LAL015", 40),
    E("AVLP_aud", "DNp56", 35),
    E("WED_aud", "DNg97", 31),
]

# ---------------------------------------------------------------------------
# Taste pathway
# ---------------------------------------------------------------------------
neurons += [
    N("GRN_sweet", "Sweet GRN", "GRN-sweet", "sez", categories=["Taste", "Sensory"], role="sensory",
      description="Gustatory receptor neuron detecting sweet tastants."),
    N("GRN_bitter", "Bitter GRN", "GRN-bitter", "sez", categories=["Taste", "Sensory"], role="sensory",
      description="Gustatory receptor neuron detecting bitter tastants."),
    N("SEZ_IN1", "SEZ interneuron 1", "SEZ-IN1", "sez", categories=["Taste"],
      description="Subesophageal-zone interneuron integrating taste input."),
    N("SEZ_IN2", "SEZ interneuron 2", "SEZ-IN2", "sez", categories=["Taste"],
      description="Taste interneuron linking SEZ circuits toward descending outputs."),
    N("GNG_taste", "GNG taste relay", "GNG-taste", "gng", categories=["Taste", "Central"],
      description="Gnathal relay carrying taste-related signals toward motor-related descending neurons."),
]

edges += [
    E("GRN_sweet", "SEZ_IN1", 175),
    E("GRN_bitter", "SEZ_IN2", 160),
    E("GRN_sweet", "SEZ_IN2", 42),
    E("SEZ_IN1", "GNG_taste", 98),
    E("SEZ_IN2", "GNG_taste", 110),
    E("SEZ_IN1", "GNG532", 66),
    E("GNG_taste", "GNG532", 78),
    E("GNG_taste", "DNg13", 28),
    E("GNG_taste", "IN19A015", 50),
    E("SEZ_IN2", "DNg97", 33),
    E("SEZ_IN1", "MN_proboscis", 88),
    E("GNG_taste", "MN_proboscis", 120),
    E("GRN_sweet", "MN_proboscis", 36),
]

neurons += [
    N("MN_proboscis", "Proboscis motor neuron", "MN-proboscis", "sez", categories=["Taste", "Motor"], role="motor",
      description="Representative feeding-related motor neuron for the proboscis / cibarial pump, a published Drosophila feeding output."),
]

# ---------------------------------------------------------------------------
# Extra hubs / alternate routes for branching & compare views
# ---------------------------------------------------------------------------
neurons += [
    N("SPS_hub", "SPS convergence hub", "SPS-hub", "sps", categories=["Central"],
      description="Superior posterior slope neuron acting as a structural convergence point across modalities in this exploration graph."),
    N("PS018", "PS018", "PS018_b", "central_brain", categories=["Central"],
      description="Posterior slope-related neuron listed among DNg13 partners.", neurotransmitter="ACh"),
]

edges += [
    E("AOTU002", "SPS_hub", 26),
    E("LH_ON1", "SPS_hub", 30),
    E("WED_aud", "SPS_hub", 24),
    E("GNG_taste", "SPS_hub", 22),
    E("SPS_hub", "VES200m", 58),
    E("SPS_hub", "LAL073", 44),
    E("SPS_hub", "DNg13", 19),
    E("AVLP713m", "PS018", 27),
    E("PS018", "DNg13", 55),
    E("LAL015", "PS018", 21),
]

# ---------------------------------------------------------------------------
# Thermosensory (aristal hot / cold cells → PAL → tPNs)
# Grounded in Drosophila antennal-arista thermoreceptors (HC/CC) and
# posterior antennal lobe thermosensory glomeruli (Gallio, Hamada, and related work).
# ---------------------------------------------------------------------------
neurons += [
    N("HC_arista", "Hot-cell thermoreceptor", "HC-arista", "arista",
      categories=["Temperature", "Hot", "Sensory"], role="sensory",
      description="Aristal hot-cell thermoreceptor (HC). Published Drosophila warmth sensor on the antennal arista."),
    N("CC_arista", "Cold-cell thermoreceptor", "CC-arista", "arista",
      categories=["Temperature", "Cold", "Sensory"], role="sensory",
      description="Aristal cold-cell thermoreceptor (CC / Ir21a family). Published Drosophila cool sensor."),
    N("PAL_hot", "PAL hot glomerulus relay", "PAL-hot", "pal", categories=["Temperature", "Hot"],
      description="Posterior antennal lobe relay for hot-cell input."),
    N("PAL_cold", "PAL cold glomerulus relay", "PAL-cold", "pal", categories=["Temperature", "Cold"],
      description="Posterior antennal lobe relay for cold-cell input."),
    N("TPN_hot", "Thermosensory PN (hot)", "tPN-hot", "pal", categories=["Temperature", "Hot", "Central"],
      description="Thermosensory projection neuron carrying warmth-related PAL output toward central brain targets."),
    N("TPN_cold", "Thermosensory PN (cold)", "tPN-cold", "pal", categories=["Temperature", "Cold", "Central"],
      description="Thermosensory projection neuron carrying cool-related PAL output toward central brain targets."),
]

edges += [
    E("HC_arista", "PAL_hot", 190),
    E("CC_arista", "PAL_cold", 185),
    E("PAL_hot", "TPN_hot", 140),
    E("PAL_cold", "TPN_cold", 136),
    E("TPN_hot", "SPS_hub", 52),
    E("TPN_hot", "GNG532", 44),
    E("TPN_hot", "DNg97", 38),
    E("TPN_cold", "SPS_hub", 48),
    E("TPN_cold", "WED_aud", 40),
    E("TPN_cold", "LAL015", 34),
    E("TPN_cold", "DNg97", 36),
    E("TPN_hot", "DNp56", 28),
]

# ---------------------------------------------------------------------------
# Mechanosensory / nociceptive startle (bristle, mdIV, FeCO → Giant Fiber)
# Grounded in adult bristle mechanoreceptors, class IV md nociceptors,
# femoral chordotonal organ, and DNp01 / giant-fiber escape descending neurons.
# ---------------------------------------------------------------------------
neurons += [
    N("BR_mech", "Bristle mechanoreceptor", "bristle-MR", "gng",
      categories=["Mechanosensory", "Sensory"], role="sensory",
      description="External bristle mechanoreceptor — a classic Drosophila touch/wind sensor."),
    N("mdIV", "Class IV md nociceptor", "md-IV", "vnc",
      categories=["Mechanosensory", "Nociception", "Sensory"], role="sensory",
      description="Multidendritic class IV nociceptor type used for noxious touch; adult and larval literature."),
    N("FeCO", "Femoral chordotonal organ", "FeCO", "vnc_t1",
      categories=["Mechanosensory", "Sensory"], role="sensory",
      description="Femoral chordotonal organ neuron: leg mechanosensation / proprioception."),
    N("GNG_mech", "GNG mechanosensory relay", "GNG-mech", "gng", categories=["Mechanosensory", "Central"],
      description="Gnathal relay collecting bristle and nociceptive touch toward descending escape cells."),
    N("AMMC_mech", "AMMC mechanosensory relay", "AMMC-mech", "ammc", categories=["Mechanosensory"],
      description="AMMC interneuron integrating JO and other antennal mechanosensory input."),
    N("DNp01", "DNp01 giant fiber", "DNp01", "neck", categories=["Motor", "Descending", "Mechanosensory"], role="descending",
      description="Giant-fiber-class descending neuron (DNp01) used in published Drosophila startle/escape circuitry."),
]

edges += [
    E("BR_mech", "GNG_mech", 160),
    E("mdIV", "GNG_mech", 148),
    E("mdIV", "IN19A015", 42),
    E("FeCO", "AMMC_mech", 90),
    E("FeCO", "IN19A015", 55),
    E("JO_A", "AMMC_mech", 70),
    E("JO_B", "AMMC_mech", 62),
    E("AMMC_mech", "WED_aud", 80),
    E("AMMC_mech", "DNp01", 95),
    E("GNG_mech", "DNp01", 170),
    E("GNG_mech", "DNg97", 60),
    E("DNp01", "LegMN_T1", 310),
    E("DNp01", "LegMN_T2", 240),
    E("DNp01", "IN19A015", 70),
    E("GNG_mech", "SPS_hub", 26),
]

journeys = [
    {
        "id": "visual-to-movement",
        "title": "Visual to Movement",
        "subtitle": "From photoreceptors toward leg motor circuitry",
        "source_query": {"kind": "category", "value": "Visual"},
        "destination_query": {"kind": "category", "value": "Motor"},
        "preferred_source": "R1",
        "preferred_destination": "LegMN_T1",
        "blurb": "Explore how visual information can structurally reach motor-related neurons, inspired by Janelia’s R1–R6 → DNg13 example.",
    },
    {
        "id": "visual-to-dng13",
        "title": "Visual Input to DNg13",
        "subtitle": "Janelia reference visual–motor scenario",
        "source_query": {"kind": "type", "value": "R1-R6"},
        "destination_query": {"kind": "neuron", "value": "DNg13"},
        "preferred_source": "R1",
        "preferred_destination": "DNg13",
        "blurb": "Follow a structural route from R1–R6 visual neurons to the DNg13 descending neuron highlighted by HHMI Janelia.",
    },
    {
        "id": "olfactory-to-descending",
        "title": "Olfactory to Descending Neuron",
        "subtitle": "Smell pathways approaching brain-to-VNC outputs",
        "source_query": {"kind": "category", "value": "Olfactory"},
        "destination_query": {"kind": "category", "value": "Descending"},
        "preferred_source": "ORN_DM1",
        "preferred_destination": "DNg13",
        "blurb": "Trace how olfactory receptor and projection neurons can reach descending neurons that leave the brain.",
    },
    {
        "id": "taste-to-motor",
        "title": "Taste to Motor Circuit",
        "subtitle": "Gustatory signals toward motor-related outputs",
        "source_query": {"kind": "category", "value": "Taste"},
        "destination_query": {"kind": "category", "value": "Motor"},
        "preferred_source": "GRN_sweet",
        "preferred_destination": "LegMN_T1",
        "blurb": "See how taste neurons in the SEZ/GNG can connect structurally toward motor-related VNC circuitry.",
    },
    {
        "id": "auditory-to-motor",
        "title": "Auditory to Motor",
        "subtitle": "Sound-related routes into descending and leg circuits",
        "source_query": {"kind": "category", "value": "Auditory"},
        "destination_query": {"kind": "category", "value": "Motor"},
        "preferred_source": "JO_A",
        "preferred_destination": "LegMN_T2",
        "blurb": "Explore structural auditory pathways from Johnston’s organ toward motor-related destinations.",
    },
    {
        "id": "hot-to-motor",
        "title": "Hot Sensation to Motor",
        "subtitle": "Aristal hot cells toward avoidance-related outputs",
        "source_query": {"kind": "category", "value": "Hot"},
        "destination_query": {"kind": "category", "value": "Motor"},
        "preferred_source": "HC_arista",
        "preferred_destination": "LegMN_T2",
        "blurb": "Follow aristal hot-cell thermoreceptors through the posterior antennal lobe toward motor-related neurons.",
    },
    {
        "id": "cold-to-motor",
        "title": "Cold Sensation to Motor",
        "subtitle": "Aristal cold cells toward avoidance-related outputs",
        "source_query": {"kind": "category", "value": "Cold"},
        "destination_query": {"kind": "category", "value": "Motor"},
        "preferred_source": "CC_arista",
        "preferred_destination": "LegMN_T2",
        "blurb": "Trace cool-sensing aristal cells toward descending and leg motor-related circuitry.",
    },
    {
        "id": "touch-to-escape",
        "title": "Mechanosensory to Escape",
        "subtitle": "Bristle / nociceptor touch toward the giant fiber",
        "source_query": {"kind": "category", "value": "Mechanosensory"},
        "destination_query": {"kind": "neuron", "value": "DNp01"},
        "preferred_source": "BR_mech",
        "preferred_destination": "DNp01",
        "blurb": "See how touch and noxious mechanosensation can structurally reach DNp01 (giant-fiber class) and leg motor neurons.",
    },
]

scenarios = [
    {
        "id": "taste-food",
        "title": "Taste Food",
        "emoji": "🍯",
        "mood": "food",
        "pose": "eating",
        "play_label": "Tap to taste",
        "hook": "The fly lands on something sweet.",
        "category": "Taste",
        "preferred_source": "GRN_sweet",
        "preferred_destination": "MN_proboscis",
        "source_query": {"kind": "neuron", "value": "GRN_sweet"},
        "destination_query": {"kind": "neuron", "value": "MN_proboscis"},
        "compare_with": "watch-tv",
        "blurb": "Sugar hits the mouthparts. Can that taste wiring reach feeding or walking motors?",
    },
    {
        "id": "watch-tv",
        "title": "Watch TV",
        "emoji": "📺",
        "mood": "tv",
        "pose": "watching",
        "play_label": "Tap to watch",
        "hook": "The fly stares at a glowing, flickering screen.",
        "category": "Visual",
        "preferred_source": "R1",
        "preferred_destination": "DNg13",
        "source_query": {"kind": "neuron", "value": "R1"},
        "destination_query": {"kind": "neuron", "value": "DNg13"},
        "compare_with": "taste-food",
        "blurb": "Light hits the eyes. Follow the official-style R1 → DNg13 visual–motor map.",
    },
    {
        "id": "zapped",
        "title": "Zapped By Human",
        "emoji": "⚡",
        "mood": "zap",
        "pose": "jumping",
        "play_label": "Tap to zap",
        "hook": "A human swats, pokes, or startles the fly.",
        "category": "Mechanosensory",
        "preferred_source": "BR_mech",
        "preferred_destination": "DNp01",
        "source_query": {"kind": "neuron", "value": "BR_mech"},
        "destination_query": {"kind": "neuron", "value": "DNp01"},
        "compare_with": "watch-tv",
        "blurb": "Touch and startle sensors can structurally reach the giant-fiber escape neuron.",
    },
    {
        "id": "hot",
        "title": "Hot Sensation",
        "emoji": "🔥",
        "mood": "hot",
        "pose": "hot",
        "play_label": "Tap the heat",
        "hook": "The air (or the floor) gets too hot.",
        "category": "Hot",
        "preferred_source": "HC_arista",
        "preferred_destination": "LegMN_T2",
        "source_query": {"kind": "neuron", "value": "HC_arista"},
        "destination_query": {"kind": "neuron", "value": "LegMN_T2"},
        "compare_with": "cold",
        "blurb": "Aristal hot cells can connect, hop by hop, toward leg motor circuitry.",
    },
    {
        "id": "cold",
        "title": "Cold Sensation",
        "emoji": "❄️",
        "mood": "cold",
        "pose": "shivering",
        "play_label": "Tap the chill",
        "hook": "A sudden chill hits the antenna.",
        "category": "Cold",
        "preferred_source": "CC_arista",
        "preferred_destination": "LegMN_T2",
        "source_query": {"kind": "neuron", "value": "CC_arista"},
        "destination_query": {"kind": "neuron", "value": "LegMN_T2"},
        "compare_with": "hot",
        "blurb": "Cool-sensing cells in the arista have a structural path toward movement-related neurons.",
    },
    {
        "id": "smell-yummy",
        "title": "Smell Something Yummy",
        "emoji": "🍓",
        "mood": "yummy",
        "pose": "sniffing",
        "play_label": "Tap to sniff",
        "hook": "A tasty smell (like fruit or vinegar) drifts by.",
        "category": "Olfactory",
        "preferred_source": "ORN_DM1",
        "preferred_destination": "DNg13",
        "source_query": {"kind": "neuron", "value": "ORN_DM1"},
        "destination_query": {"kind": "neuron", "value": "DNg13"},
        "compare_with": "smell-bad",
        "blurb": "Food-odor receptor neurons can structurally reach descending motor-related cells.",
    },
    {
        "id": "hear-buzz",
        "title": "Hear a Buzz",
        "emoji": "🎵",
        "mood": "buzz",
        "pose": "listening",
        "play_label": "Tap to listen",
        "hook": "The antennae pick up a buzz or vibration.",
        "category": "Auditory",
        "preferred_source": "JO_A",
        "preferred_destination": "LegMN_T2",
        "source_query": {"kind": "neuron", "value": "JO_A"},
        "destination_query": {"kind": "neuron", "value": "LegMN_T2"},
        "compare_with": "zapped",
        "blurb": "Johnston’s organ is a real fly ear — and a vibration sensor — with paths toward the legs.",
    },
    {
        "id": "smell-bad",
        "title": "Smell Something Bad",
        "emoji": "🤢",
        "mood": "stinky",
        "pose": "recoil",
        "play_label": "Tap the stink",
        "hook": "An unpleasant odor hits the antennae.",
        "category": "Olfactory",
        "preferred_source": "ORN_DL5",
        "preferred_destination": "DNp56",
        "source_query": {"kind": "neuron", "value": "ORN_DL5"},
        "destination_query": {"kind": "neuron", "value": "DNp56"},
        "compare_with": "smell-yummy",
        "blurb": "A different olfactory channel can still reach descending neurons — a separate structural route.",
    },
]

meta = {
    "product": "Neural Path Finder",
    "dataset": "HHMI Janelia FlyEM Male CNS Connectome",
    "dataset_version": "MaleCNS v1.0",
    "dataset_released": "2026-06-08",
    "license": "CC BY",
    "organism": "Drosophila melanogaster (adult male)",
    "full_scale": {
        "neurons": 166000,
        "synapses": 125000000,
        "note": "Full published Male CNS scale; this app uses a curated exploration subgraph.",
    },
    "references": [
        {
            "name": "Janelia Male CNS Connectome",
            "url": "https://www.janelia.org/project-team/flyem/male-cns-connectome",
        },
        {
            "name": "MaleCNS project page",
            "url": "https://male-cns.janelia.org/",
        },
        {
            "name": "NeuPrint",
            "url": "https://neuprint.janelia.org/",
        },
        {
            "name": "Male CNS Cell Type Explorer — DNg13",
            "url": "https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/DNg13.html",
        },
        {
            "name": "Neuroglancer MaleCNS v1.0",
            "url": "https://neuroglancer-demo.appspot.com/#!gs://flyem-male-cns/v1.0/male-cns-v1.0.jso",
        },
    ],
    "disclaimer": (
        "Connectivity here is structural (synaptic anatomy). Structural links do not by themselves "
        "prove causal activity flow during real behavior. This product is for exploration and education, "
        "not medical or biological conclusions."
    ),
    "graph_note": (
        "Neuron types and several synapse strengths are grounded in Male CNS Cell Type Explorer / "
        "published circuit motifs (especially DNg13 partners and the R1–R6 → DNg13 example). "
        "The graph is intentionally compact for interactive path finding."
    ),
}

# Deduplicate neurons by id
seen = {}
for n in neurons:
    seen[n["id"]] = n
neurons = list(seen.values())

payload = {
    "meta": meta,
    "regions": REGIONS,
    "neurons": neurons,
    "connections": edges,
    "journeys": journeys,
    "scenarios": scenarios,
    "categories": [
        "Visual", "Olfactory", "Auditory", "Taste", "Motor", "Descending",
        "Sensory", "Central", "Temperature", "Hot", "Cold", "Mechanosensory", "Nociception",
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=2))
print(f"Wrote {OUT}")
print(f"Neurons: {len(neurons)}  Connections: {len(edges)}")


if __name__ == "__main__":
    # Graph is written at module load so `python scripts/generate_connectome.py` always regenerates.
    pass
