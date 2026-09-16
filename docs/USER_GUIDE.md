# Neural Path Finder — User Guide

A click-by-click walkthrough of the exhibit. Every screenshot below is a real capture of the running app (warm daylight theme) at [http://127.0.0.1:8000](http://127.0.0.1:8000).

This is a **wiring map** of a small teaching graph, not a movie of the fly’s feelings. Paths do not prove the fly thought, decided, or felt that way, and this is not medical advice.

**Need the short version?** See the [README](../README.md). **Want the internals?** See [Architecture](ARCHITECTURE.md).

---

## Before you start

1. Create a Python 3.12+ virtualenv named **`fly`**, install `requirements.txt`, and generate the connectome JSON.
2. Build the frontend: `cd frontend && npm install && npm run build`.
3. Run the API from the repo root:

```powershell
$env:PYTHONPATH = "backend"
.\fly\Scripts\python.exe backend\run.py
```

4. Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in a browser. You should see a lemon-cream page, a cartoon fly, and eight scene cards.

If the page is missing or looks like raw JSON, the frontend was not built. Run `npm run build` again, then refresh.

---

## 1. Open the app (home)

You land in **Play mode**. Look for:

- The **Neural Path Finder** title and a round brand mark in the top left.
- A **Scientist mode** button in the top right (leave it closed for now).
- The cartoon fly and the headline *What happens inside a fly when it tastes, watches, or gets zapped?*
- A disclaimer: *Just a wiring map.*
- A **Pick a scene** board with eight cards.

<img src="screenshots/01-home.png" alt="Home screen: cartoon fly, headline, disclaimer, and eight scene cards on a daylight background" width="900">

*What you should see: a warm, light page — not a dark dashboard. The fly is idle and waiting for a tap.*

---

## 2. Pick a scene

The eight cards are tap-to-play shortcuts. Each one is a preferred start cell and end cell in the same `connectome.json` the API loads:

| Card | What it traces |
| --- | --- |
| Taste Food | Sweet taste cell `GRN_sweet` toward front-leg motor `LegMN_T1` |
| Watch TV | Photoreceptor `R1` toward descending neuron `DNg13` |
| Zapped By Human | Bristle mechanoreceptor `BR_mech` toward giant-fiber-class `DNp01` |
| Hot Sensation | Aristal hot cell `HC_arista` toward `LegMN_T2` |
| Cold Sensation | Aristal cold cell `CC_arista` toward `LegMN_T2` |
| Smell Something Yummy | Olfactory `ORN_DM1` toward `DNg13` |
| Hear a Buzz | Johnston’s organ `JO_A` toward `LegMN_T2` |
| Smell Something Bad | Olfactory `ORN_DL5` toward `DNp56` |

**Click Watch TV** (the TV-set card). The card highlights with a blue border. The fly’s line changes to a watching pose. Status text under the cards becomes *Following the wires…*

<img src="screenshots/02-scenarios.png" alt="Eight scene cards with Watch TV selected" width="900">

*Watch TV is selected. That scene follows the official-style R1 → DNg13 visual–motor map.*

You can tap any other card the same way. One tap runs `GET /api/scenarios/{id}/run` and returns a story plus ranked paths.

---

## 3. Follow the wires (a Watch TV run)

The page scrolls to **Results**. You should see, in order:

1. **Story beats** — a short exhibit narrative (hook, sensors, hop count, destination). Flavor text; the hops underneath are still structural.
2. **Route tabs** — *Most direct*, *Strongest connectivity*, and alternative walks. The first tab is selected.
3. **Hop strip** — neurons as station cards, synapse counts as the tracks between them.
4. **Metrics** — start cell, end cell, hop count, synapse total.
5. **In plain words** and **Why this path?** — what the ranker did.
6. **Neighborhoods along the way** — region stepper (Retina → Lamina → Medulla → …).
7. **Tap a cell to see branches** and **Busy crossroads** — neighbors and hubs *in this 75-node graph only*.

<img src="screenshots/03-connectome-path.png" alt="Watch TV result: story beats, route tabs, hop strip, metrics, and explanations" width="900">

*A Watch TV run. Story at the top, then the anatomical walk from retina toward descending motor cells.*

### Read the hop strip

Each rounded card is one neuron (`id`, name, type, region). The small labels between cards are **synapse weights** on that hop — useful for ranking this toy graph, not a NeuPrint export you can cite as MaleCNS v1.0 connectivity.

<img src="screenshots/04-journey-track.png" alt="Close-up of the neuron hop strip from R1 through L1, Tm3, LC10, AVLP713m to DNg13" width="900">

*Example walk: `R1` → `L1` → `Tm3` → `LC10` → `AVLP713m` → `DNg13`. Click any station to load upstream and downstream neighbors.*

**Try this:** click **R1 photoreceptor** on the strip. The *Tap a cell to see branches* panel lists cells before (upstream) and after (downstream) that neuron.

Switch tabs to compare a shorter walk with a stronger-synapse walk. Alternative tabs are other simple paths that share fewer nodes — not proven backup circuits in the fly.

---

## 4. Zap the fly

Go back to **Pick a scene** and click **Zapped By Human**.

The background flashes briefly (the zap mood), the mascot jumps, and a new path runs: mechanosensory bristle cells toward giant-fiber-class **DNp01**. Same engine, different endpoints.

<img src="screenshots/05-zapped-run.png" alt="Zapped By Human result on a lemon daylight background with a short escape-style hop strip" width="900">

*Zapped By Human: a short structural escape-style walk, still labeled as a wiring map. Typical result is a handful of hops (for example bristle → GNG relay → DNp01).*

---

## 5. Compare two scenes (do they meet?)

Under the scene board, click the wide gradient button:

**Taste food vs watch TV — do they meet?**

That posts two path queries at once (`GRN_sweet` → `LegMN_T1` versus `R1` → `DNg13`) and opens a split panel.

<img src="screenshots/06-compare-taste-tv.png" alt="Side-by-side comparison of taste-food and watch-TV paths with shared cells called out" width="900">

*What you should look for:*

- A headline **Taste food vs watch TV** and a paragraph about shared anatomical territories.
- **Shared cells** on the top routes (often `DNg13` in this teaching graph).
- Left column: taste-food hops through SEZ / GNG / neck / VNC.
- Right column: watch-TV hops through retina / optic lobe / central brain / neck.

Shared nodes are **meeting points in the graph**, not proof the behaviors happen together.

---

## 6. Scientist mode

Click **Scientist mode** in the header, or open the **Scientist mode — search neurons yourself** panel at the bottom of the page.

<img src="screenshots/07-scientist-mode.png" alt="Scientist mode origin and destination pickers with R1 and DNg13 filled in" width="900">

*Same toy graph, same structural-only rules — you pick the endpoints.*

**Classic demo (fastest):**

1. Leave Kind as **Neuron ID** on both sides.
2. Origin value `R1`, destination value `DNg13` (the defaults).
3. Click **Classic demo: R1 → DNg13**, or **Trace pathway**.

You get the same hop strip, tabs, explanations, and hubs as a Watch TV scene, labeled as a custom search.

**Search by something other than an ID:**

1. Change Kind to **Category**, **Name**, **Cell type**, or **Region**.
2. Start typing in Value. A suggest list appears (for example category `Visual`, region `retina`).
3. Pick a hit, then **Trace pathway**.

Category searches prefer sensory cells as origins and motor (then descending) cells as destinations, then cap each side so the UI stays interactive.

---

## 7. How to read a result without overclaiming

When the UI says **Most direct · 5 hops · R1 → … → DNg13**:

1. In this 75-node teaching graph, a hop-minimizing directed walk exists.
2. Synapse integers mix a few published-scale DNg13 partner weights with representative teaching weights.
3. Alternative tabs are other simple paths, not proven backup circuits.
4. The anatomical stepper collapses `region_label`s along that walk.
5. A playful hook (“The fly stares at a glowing, flickering screen”) is flavor.

If you need a number you can cite in a paper, leave this app and go to [NeuPrint](https://neuprint.janelia.org/) or the [DNg13 Cell Type Explorer](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/DNg13.html).

---

## Troubleshooting

| Symptom | What to try |
| --- | --- |
| Blank page or “frontend/dist missing” | `cd frontend && npm run build`, restart `backend\run.py` |
| Cards never appear | Check `GET /api/health` and `GET /api/scenarios` in the browser |
| Theme looks dark | Hard-refresh; you should see lemon cream, not a navy dashboard |
| Path says “No path in this toy map” | Those two cells are not connected in the 75-node graph — pick a scene card or the classic R1 → DNg13 demo |
| Stale UI after a code change | Rebuild the frontend; FastAPI only serves `frontend/dist` |
