# Neural Path Finder

Interactive “Google Maps for a nervous system” over a curated exploration subgraph of the
**HHMI Janelia FlyEM Male CNS Connectome** (MaleCNS v1.0, released 2026-06-08, CC BY).

Ask questions such as *how can visual information eventually reach a motor neuron?* and
inspect structural routes: hops, synapse counts, anatomy, alternatives, branching, and hubs.

The full published Male CNS scale is about **166,000 neurons** and **125 million synapses**.
This app does **not** load that entire volume. It uses a compact, curated graph grounded in
published cell types and the official **R1–R6 → DNg13** visual–motor example so pathways
can be explored in a browser.

## What you can do

- **Neural path result** — source, intermediates, destination, hop count, synapse totals, anatomy
- **Multiple paths** — most direct, strongest connectivity, and diverse alternatives
- **Non-specialist explanation** for each path
- **Pathway strength profile** — relative synapse weight along each hop
- **Branching view** — upstream and downstream neighbors when a neuron is selected
- **Anatomical journey** — region-to-region stepper (optic lobe → central brain → VNC)
- **Neuron importance / structural hubs** — degree and betweenness *inside this graph only*
- **Compare two paths** — e.g. Visual → Motor vs Olfactory → Motor
- **Guided journeys** — Visual to Movement, Olfactory to Descending Neuron, Taste to Motor Circuit, Visual Input to DNg13, Auditory to Motor
- **Why this path?** — ranking rationale (hops, bottleneck strength, diversity)
- **Search** — neuron ID, name, type, region, or category (Visual, Olfactory, Auditory, Taste, Motor, Descending)
- **Demo path** — visual sensory (R1) → DNg13 / motor circuitry

## Disclaimer

Connectivity here is **structural** (synaptic anatomy). A structural path does **not** prove
causal activity flow during real behavior, does not establish that these cells fire together,
and supports **no medical conclusions**. Ranked “hubs” describe network structure in the
exploration graph, not proven behavioral importance.

## Dataset attribution

- Organism: *Drosophila melanogaster* (adult male)
- Source: [Janelia Male CNS Connectome](https://www.janelia.org/project-team/flyem/male-cns-connectome)
- Project: [male-cns.janelia.org](https://male-cns.janelia.org/)
- [NeuPrint](https://neuprint.janelia.org/)
- [Male CNS Cell Type Explorer — DNg13](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/DNg13.html)
- [Neuroglancer MaleCNS v1.0](https://neuroglancer-demo.appspot.com/#!gs://flyem-male-cns/v1.0/male-cns-v1.0.jso)
- License: CC BY

Neuron types and several synapse-strength annotations are grounded in public Male CNS
resources (especially DNg13 partners). Remaining edge weights are representative structural
strengths for exploration, not a dump of the full connectome.

## Setup

Python 3.12+ and Node.js 20+ are expected. The virtual environment **must be named `fly`**.

```
python3 -m venv fly
source fly/bin/activate
pip install -r requirements.txt
python scripts/generate_connectome.py
cd frontend && npm install && npm run build && cd ..
PYTHONPATH=backend fly/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Equivalent using the run script (after the same venv, data, and frontend build steps):

```
source fly/bin/activate
PYTHONPATH=backend python backend/run.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). FastAPI serves the built
`frontend/dist` SPA and the `/api` routes from the same origin.

### Frontend development

With the API already running on port 8000:

```
source fly/bin/activate
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

### Tests

```
source fly/bin/activate
PYTHONPATH=backend pytest backend/tests -q
```

## Project layout

```
backend/app/           FastAPI app, pathfinder, graph loader
backend/app/data/      Generated connectome.json
backend/run.py         Uvicorn entrypoint (0.0.0.0:8000)
backend/tests/         pytest coverage for health, journeys, paths, compare, neighbors
frontend/              Vite + vanilla HTML/CSS/JS discovery UI
scripts/generate_connectome.py
```

## API (same origin `/api`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness |
| GET | `/api/meta` | Dataset metadata, categories, regions |
| GET | `/api/neurons?q=` | Search neurons |
| GET | `/api/neurons/{id}/neighbors` | Upstream / downstream |
| POST | `/api/branch` | Branching view |
| POST | `/api/paths/find` | Multiple structural paths |
| POST | `/api/paths/compare` | Compare two queries |
| GET | `/api/journeys` | Guided journeys |
| GET | `/api/hubs` | Structural hubs |

Example body for `POST /api/paths/find`:

```json
{
  "source": { "kind": "neuron", "value": "R1" },
  "destination": { "kind": "neuron", "value": "DNg13" }
}
```

`kind` may be `neuron`, `name`, `type`, `region`, or `category`.

## Known limitations

- The live graph is a **curated subgraph** (dozens of typed neurons and representative edges),
  not the full ~166k / ~125M Male CNS volume.
- Paths are computed on directed structural edges. They are hypotheses about anatomy, not
  recordings of activity.
- Synapse numbers mix published partner-scale annotations with representative weights so
  ranking stays informative at exploration scale.
- Betweenness / degree “importance” is local to this subgraph.

## License

Application code in this repository is provided for research and education. Underlying
connectome data remain under Janelia’s CC BY terms.
