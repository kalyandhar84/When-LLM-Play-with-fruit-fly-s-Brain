import * as api from "./api.js";

const els = {
  journeyGrid: document.getElementById("journey-grid"),
  findForm: document.getElementById("find-form"),
  compareForm: document.getElementById("compare-form"),
  exploreConsole: document.getElementById("explore-console"),
  compareConsole: document.getElementById("compare-console"),
  results: document.getElementById("results"),
  exploreResults: document.getElementById("explore-results"),
  compareResults: document.getElementById("compare-results"),
  status: document.getElementById("status"),
  modeExplore: document.getElementById("mode-explore"),
  modeCompare: document.getElementById("mode-compare"),
  demoBtn: document.getElementById("demo-btn"),
  sourceKind: document.getElementById("source-kind"),
  sourceValue: document.getElementById("source-value"),
  destKind: document.getElementById("dest-kind"),
  destValue: document.getElementById("dest-value"),
  sourceSuggest: document.getElementById("source-suggest"),
  destSuggest: document.getElementById("dest-suggest"),
};

const CATEGORIES = ["Visual", "Olfactory", "Auditory", "Taste", "Motor", "Descending"];

const state = {
  mode: "explore",
  result: null,
  compare: null,
  selectedPath: 0,
  selectedNeuron: null,
  branch: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function setMode(mode) {
  state.mode = mode;
  els.modeExplore.setAttribute("aria-pressed", String(mode === "explore"));
  els.modeCompare.setAttribute("aria-pressed", String(mode === "compare"));
  els.exploreConsole.hidden = mode !== "explore";
  els.compareConsole.hidden = mode !== "compare";
  els.exploreResults.hidden = mode !== "explore";
  els.compareResults.hidden = mode !== "compare";
}

function showBusy(message) {
  els.results.hidden = false;
  els.status.textContent = message;
}

function showError(error) {
  els.results.hidden = false;
  els.status.textContent = error.message || String(error);
}

async function loadJourneys() {
  const journeys = await api.journeys();
  els.journeyGrid.innerHTML = journeys
    .map(
      (j) => `
      <button class="journey-card" type="button" data-id="${escapeHtml(j.id)}">
        <small>${escapeHtml(j.subtitle)}</small>
        <h4>${escapeHtml(j.title)}</h4>
        <p>${escapeHtml(j.blurb)}</p>
      </button>`
    )
    .join("");
  els.journeyGrid.querySelectorAll(".journey-card").forEach((btn) => {
    btn.addEventListener("click", () => runJourney(journeys.find((j) => j.id === btn.dataset.id)));
  });
}

async function runJourney(journey) {
  if (!journey) return;
  setMode("explore");
  els.sourceKind.value = journey.source_query.kind;
  els.sourceValue.value = journey.preferred_source || journey.source_query.value;
  els.destKind.value = journey.destination_query.kind;
  els.destValue.value = journey.preferred_destination || journey.destination_query.value;
  // Use preferred cell IDs so guided journeys match the published examples.
  await runFind(
    api.spec("neuron", journey.preferred_source),
    api.spec("neuron", journey.preferred_destination),
    `Running “${journey.title}”…`
  );
}

async function runFind(source, destination, message = "Tracing structural pathways…") {
  showBusy(message);
  try {
    const result = await api.findPaths(source, destination);
    state.result = result;
    state.selectedPath = 0;
    state.selectedNeuron = result.paths[0]?.neuron_ids[0] || null;
    await refreshBranch();
    renderExplore();
  } catch (error) {
    showError(error);
  }
}

async function refreshBranch() {
  if (!state.selectedNeuron) {
    state.branch = null;
    return;
  }
  try {
    state.branch = await api.branch(state.selectedNeuron);
  } catch {
    state.branch = null;
  }
}

function renderExplore() {
  const result = state.result;
  if (!result) return;
  els.results.hidden = false;
  els.exploreResults.hidden = false;
  if (!result.paths.length) {
    els.status.textContent = "No structural path found in the exploration graph.";
    els.exploreResults.innerHTML = `<p class="empty">${escapeHtml(result.anatomical_summary)}</p>`;
    return;
  }
  const path = result.paths[state.selectedPath] || result.paths[0];
  els.status.textContent = `${result.paths.length} route(s) · ${path.hop_count} hop(s) · claim: structural connectivity`;

  const tabs = result.paths
    .map(
      (p, i) =>
        `<button class="path-tab ${i === state.selectedPath ? "active" : ""}" type="button" data-i="${i}">
          ${escapeHtml(p.label)} · ${p.hop_count} hops · ${p.total_synapses} syn
        </button>`
    )
    .join("");

  const nodes = [];
  path.steps.forEach((step, idx) => {
    if (idx === 0) nodes.push(neuronCard(step.from_neuron));
    nodes.push(edgeLabel(step.synapses));
    nodes.push(neuronCard(step.to_neuron));
  });

  const strength = path.strength_profile
    .map(
      (row) => `
      <div class="bar-row">
        <label><span>${escapeHtml(row.from_name)} → ${escapeHtml(row.to_name)}</span><span>${row.synapses} synapses · ${row.band}</span></label>
        <div class="bar ${escapeHtml(row.band)}"><i style="width:${Math.max(8, row.relative * 100)}%"></i></div>
      </div>`
    )
    .join("");

  const anatomy = path.region_labels
    .map((label) => `<span>${escapeHtml(label)}</span>`)
    .join("");

  const hubs = (result.hubs || [])
    .map(
      (h) => `
      <article class="hub-item">
        <strong>${escapeHtml(h.neuron.name)}</strong>
        <div class="meta">${escapeHtml(h.neuron.cell_type)} · degree ${h.degree} · betweenness ${h.betweenness}</div>
        <p>${escapeHtml(h.interpretation)}</p>
      </article>`
    )
    .join("");

  const branch = renderBranch();

  els.exploreResults.innerHTML = `
    <div class="path-tabs">${tabs}</div>
    <div class="journey-track">${nodes.join("")}</div>
    <div class="metrics">
      <div class="metric"><span>Source</span><strong>${escapeHtml(path.steps[0].from_neuron.name)}</strong></div>
      <div class="metric"><span>Destination</span><strong>${escapeHtml(path.steps.at(-1).to_neuron.name)}</strong></div>
      <div class="metric"><span>Hops</span><strong>${path.hop_count}</strong></div>
      <div class="metric"><span>Total synapses</span><strong>${path.total_synapses}</strong></div>
      <div class="metric"><span>Bottleneck</span><strong>${path.min_synapses}</strong></div>
      <div class="metric"><span>Mean synapses</span><strong>${path.mean_synapses}</strong></div>
    </div>
    <div class="panel">
      <h4>Non-specialist explanation</h4>
      <p>${escapeHtml(path.explanation)}</p>
    </div>
    <div class="grid-2">
      <div class="panel">
        <h4>Why this path?</h4>
        <p>${escapeHtml(path.why_this_path)}</p>
      </div>
      <div class="panel">
        <h4>Pathway strength profile</h4>
        ${strength}
      </div>
    </div>
    <div class="panel" style="margin-top:12px">
      <h4>Anatomical journey</h4>
      <p>${escapeHtml(result.anatomical_summary)}</p>
      <div class="stepper">${anatomy}</div>
    </div>
    <div class="grid-2">
      <div class="panel">
        <h4>Branching view</h4>
        <p>Select a neuron on the path. Upstream / downstream neighbors show where this cell can branch — not a single linear circuit.</p>
        ${branch}
      </div>
      <div class="panel">
        <h4>Neuron importance (structural hubs)</h4>
        <p>Ranks describe connectivity inside this exploration graph, not proven behavioral importance.</p>
        ${hubs}
      </div>
    </div>
  `;

  els.exploreResults.querySelectorAll(".path-tab").forEach((btn) => {
    btn.addEventListener("click", async () => {
      state.selectedPath = Number(btn.dataset.i);
      const next = state.result.paths[state.selectedPath];
      state.selectedNeuron = next?.neuron_ids[0] || null;
      await refreshBranch();
      renderExplore();
    });
  });
  els.exploreResults.querySelectorAll("[data-neuron]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      state.selectedNeuron = btn.dataset.neuron;
      await refreshBranch();
      renderExplore();
    });
  });
}

function neuronCard(neuron) {
  const selected = neuron.id === state.selectedNeuron ? "selected" : "";
  return `
    <button class="node ${selected}" type="button" data-neuron="${escapeHtml(neuron.id)}">
      <div class="nid">${escapeHtml(neuron.id)}</div>
      <h4>${escapeHtml(neuron.name)}</h4>
      <div class="meta">${escapeHtml(neuron.cell_type)} · ${escapeHtml(neuron.region_label)}</div>
    </button>`;
}

function edgeLabel(synapses) {
  return `<div class="edge">${synapses}<small>synapses</small></div>`;
}

function renderBranch() {
  const data = state.branch;
  if (!data) return `<p class="empty">Click a neuron to inspect neighbors.</p>`;
  const col = (rows, title) => `
    <div>
      <strong>${title} (${rows.length})</strong>
      ${rows
        .map(
          (row) => `
        <div class="neighbor" data-neuron="${escapeHtml(row.neuron.id)}">
          <span>${escapeHtml(row.neuron.name)}</span>
          <span>${row.synapses}</span>
        </div>`
        )
        .join("")}
    </div>`;
  return `
    <p><strong>${escapeHtml(data.neuron.name)}</strong> — ${escapeHtml(data.neuron.description || data.neuron.cell_type)}</p>
    <div class="branch-cols">
      ${col(data.upstream, "Upstream")}
      ${col(data.downstream, "Downstream")}
    </div>`;
}

function renderCompare() {
  const cmp = state.compare;
  if (!cmp) return;
  els.results.hidden = false;
  els.compareResults.hidden = false;
  els.status.textContent = "Comparison uses the top-ranked structural route on each side.";

  const side = (label, result) => {
    const path = result.paths?.[0];
    if (!path) return `<div class="panel"><h4>${label}</h4><p>No path found.</p></div>`;
    return `
      <div class="panel">
        <h4>${label}: ${escapeHtml(path.label)}</h4>
        <p>${path.hop_count} hops · ${path.total_synapses} synapses · ${escapeHtml(path.region_labels.join(" → "))}</p>
        <p>${escapeHtml(path.explanation)}</p>
      </div>`;
  };

  const shared = (cmp.shared_neuron_ids || []).join(", ") || "none in the top routes";
  els.compareResults.innerHTML = `
    <div class="panel">
      <h4>What the comparison shows</h4>
      <p>${escapeHtml(cmp.comparison_explanation)}</p>
      <p>Shared neurons: ${escapeHtml(shared)}. Shared regions: ${escapeHtml((cmp.shared_regions || []).join(", ") || "none")}.</p>
    </div>
    <div class="compare-split">
      ${side("Path A", cmp.path_a)}
      ${side("Path B", cmp.path_b)}
    </div>
  `;
}

function bindSearch(input, suggestBox, kindSelect) {
  let timer = 0;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const q = input.value.trim();
      if (q.length < 1 || kindSelect.value === "category") {
        if (kindSelect.value === "category") {
          const hits = CATEGORIES.filter((c) => c.toLowerCase().includes(q.toLowerCase()));
          renderSuggest(suggestBox, hits.map((c) => ({ id: c, name: c, cell_type: "category" })), input, kindSelect);
          return;
        }
        suggestBox.hidden = true;
        return;
      }
      try {
        const hits = await api.searchNeurons(q, 8);
        renderSuggest(suggestBox, hits, input, kindSelect);
      } catch {
        suggestBox.hidden = true;
      }
    }, 160);
  });
  document.addEventListener("click", (event) => {
    if (!suggestBox.contains(event.target) && event.target !== input) {
      suggestBox.hidden = true;
    }
  });
}

function renderSuggest(box, hits, input, kindSelect) {
  if (!hits.length) {
    box.hidden = true;
    return;
  }
  box.hidden = false;
  box.innerHTML = hits
    .map(
      (n) =>
        `<button type="button" data-id="${escapeHtml(n.id)}" data-name="${escapeHtml(n.name)}">
          <strong>${escapeHtml(n.id)}</strong> · ${escapeHtml(n.name)} · ${escapeHtml(n.cell_type)}
        </button>`
    )
    .join("");
  box.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (kindSelect.value === "category") {
        input.value = btn.dataset.id;
      } else {
        kindSelect.value = "neuron";
        input.value = btn.dataset.id;
      }
      box.hidden = true;
    });
  });
}

els.findForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runFind(
    api.spec(els.sourceKind.value, els.sourceValue.value),
    api.spec(els.destKind.value, els.destValue.value)
  );
});

els.demoBtn.addEventListener("click", () => {
  els.sourceKind.value = "neuron";
  els.sourceValue.value = "R1";
  els.destKind.value = "neuron";
  els.destValue.value = "DNg13";
  runFind(api.spec("neuron", "R1"), api.spec("neuron", "DNg13"), "Demo path: visual sensory → DNg13…");
});

els.compareForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showBusy("Comparing Visual→Motor-style routes…");
  try {
    state.compare = await api.comparePaths(
      {
        source: api.spec(document.getElementById("ca-kind").value, document.getElementById("ca-value").value),
        destination: api.spec(document.getElementById("ca-dk").value, document.getElementById("ca-dv").value),
      },
      {
        source: api.spec(document.getElementById("cb-kind").value, document.getElementById("cb-value").value),
        destination: api.spec(document.getElementById("cb-dk").value, document.getElementById("cb-dv").value),
      }
    );
    renderCompare();
  } catch (error) {
    showError(error);
  }
});

els.modeExplore.addEventListener("click", () => setMode("explore"));
els.modeCompare.addEventListener("click", () => setMode("compare"));

bindSearch(els.sourceValue, els.sourceSuggest, els.sourceKind);
bindSearch(els.destValue, els.destSuggest, els.destKind);

(async function boot() {
  try {
    await loadJourneys();
    await runFind(api.spec("neuron", "R1"), api.spec("neuron", "DNg13"), "Loading demo path: visual sensory → DNg13…");
  } catch (error) {
    showError(error);
  }
})();
