import * as api from "./api.js";

const els = {
  board: document.getElementById("scenario-board"),
  results: document.getElementById("results"),
  exploreResults: document.getElementById("explore-results"),
  compareResults: document.getElementById("compare-results"),
  storyCard: document.getElementById("story-card"),
  status: document.getElementById("status"),
  mascotLine: document.getElementById("mascot-line"),
  findForm: document.getElementById("find-form"),
  scientistToggle: document.getElementById("scientist-toggle"),
  scientistPanel: document.getElementById("scientist-panel"),
  compareTasteTv: document.getElementById("compare-taste-tv"),
  demoBtn: document.getElementById("demo-btn"),
  sourceKind: document.getElementById("source-kind"),
  sourceValue: document.getElementById("source-value"),
  destKind: document.getElementById("dest-kind"),
  destValue: document.getElementById("dest-value"),
  sourceSuggest: document.getElementById("source-suggest"),
  destSuggest: document.getElementById("dest-suggest"),
};

const CATEGORIES = [
  "Visual", "Olfactory", "Auditory", "Taste", "Motor", "Descending",
  "Temperature", "Hot", "Cold", "Mechanosensory",
];

const state = {
  scenarios: [],
  activeId: null,
  result: null,
  compare: null,
  selectedPath: 0,
  selectedNeuron: null,
  branch: null,
  story: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function setMood(mood, pose, line) {
  document.body.dataset.mood = mood || "idle";
  document.body.dataset.pose = pose || "idle";
  document.body.classList.toggle("flash", mood === "zap");
  if (line) els.mascotLine.textContent = line;
  if (mood === "zap") {
    window.setTimeout(() => document.body.classList.remove("flash"), 600);
  }
}

function showBusy(message) {
  els.results.hidden = false;
  els.compareResults.hidden = true;
  els.exploreResults.hidden = false;
  els.status.textContent = message;
}

function showError(error) {
  els.results.hidden = false;
  els.status.textContent = error.message || String(error);
}

function renderBoard() {
  els.board.innerHTML = state.scenarios
    .map(
      (s) => `
      <button class="scene-card mood-${escapeHtml(s.mood)} ${state.activeId === s.id ? "active" : ""}" type="button" data-id="${escapeHtml(s.id)}">
        <div class="art" aria-hidden="true">${s.emoji}</div>
        <h4>${escapeHtml(s.title)}</h4>
        <p>${escapeHtml(s.blurb)}</p>
        <small>${escapeHtml(s.play_label)}</small>
      </button>`
    )
    .join("");
  els.board.querySelectorAll(".scene-card").forEach((btn) => {
    btn.addEventListener("click", () => playScenario(btn.dataset.id));
  });
}

async function playScenario(id) {
  const scenario = state.scenarios.find((s) => s.id === id);
  if (!scenario) return;
  state.activeId = id;
  renderBoard();
  setMood(scenario.mood, scenario.pose, scenario.hook);
  showBusy("Following the wires…");
  els.storyCard.innerHTML = `<p>${escapeHtml(scenario.hook)}</p>`;
  try {
    const packed = await api.runScenario(id);
    state.result = packed.result;
    state.story = packed.story;
    state.selectedPath = 0;
    state.selectedNeuron = packed.result.paths[0]?.neuron_ids[0] || null;
    await refreshBranch();
    renderStory();
    renderExplore();
    els.results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showError(error);
  }
}

function renderStory() {
  if (!state.story) {
    els.storyCard.innerHTML = "";
    return;
  }
  const beats = state.story.beats
    .map((beat, i) => `<li style="animation-delay:${i * 90}ms">${escapeHtml(beat)}</li>`)
    .join("");
  els.storyCard.innerHTML = `
    <h3>${escapeHtml(state.story.headline)}</h3>
    <ol>${beats}</ol>
  `;
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
  els.compareResults.hidden = true;
  if (!result.paths.length) {
    els.status.textContent = "No path in this toy map.";
    els.exploreResults.innerHTML = `<p>${escapeHtml(result.anatomical_summary)}</p>`;
    return;
  }
  const path = result.paths[state.selectedPath] || result.paths[0];
  els.status.textContent = `${result.paths.length} routes · ${path.hop_count} hops · still just a wiring map`;

  const tabs = result.paths
    .map(
      (p, i) =>
        `<button class="path-tab ${i === state.selectedPath ? "active" : ""}" type="button" data-i="${i}">
          ${escapeHtml(p.label)} · ${p.hop_count} hops
        </button>`
    )
    .join("");

  const pieces = [];
  let i = 0;
  path.steps.forEach((step, idx) => {
    if (idx === 0) pieces.push(neuronCard(step.from_neuron, i++));
    pieces.push(edgeLabel(step.synapses, i++));
    pieces.push(neuronCard(step.to_neuron, i++));
  });

  const strength = path.strength_profile
    .map(
      (row) => `
      <div class="bar-row">
        <label><span>${escapeHtml(row.from_name)} → ${escapeHtml(row.to_name)}</span><span>${row.synapses} synapses</span></label>
        <div class="bar ${escapeHtml(row.band)}"><i style="--w:${Math.max(10, row.relative * 100)}%"></i></div>
      </div>`
    )
    .join("");

  const anatomy = path.region_labels.map((label) => `<span>${escapeHtml(label)}</span>`).join("");
  const hubs = (result.hubs || [])
    .map(
      (h) => `
      <article class="hub-item">
        <strong>${escapeHtml(h.neuron.name)}</strong>
        <div class="meta">${escapeHtml(h.neuron.cell_type)} · ${h.degree} neighbors</div>
        <p>${escapeHtml(h.interpretation)}</p>
      </article>`
    )
    .join("");

  els.exploreResults.innerHTML = `
    <div class="path-tabs">${tabs}</div>
    <div class="journey-track">${pieces.join("")}</div>
    <div class="metrics">
      <div class="metric"><span>Start</span><strong>${escapeHtml(path.steps[0].from_neuron.name)}</strong></div>
      <div class="metric"><span>End</span><strong>${escapeHtml(path.steps.at(-1).to_neuron.name)}</strong></div>
      <div class="metric"><span>Hops</span><strong>${path.hop_count}</strong></div>
      <div class="metric"><span>Synapse total</span><strong>${path.total_synapses}</strong></div>
    </div>
    <div class="panel">
      <h4>In plain words</h4>
      <p>${escapeHtml(path.explanation)}</p>
    </div>
    <div class="grid-2" style="margin-top:12px">
      <div class="panel">
        <h4>Why this path?</h4>
        <p>${escapeHtml(path.why_this_path)}</p>
      </div>
      <div class="panel">
        <h4>How strong are the links?</h4>
        ${strength}
      </div>
    </div>
    <div class="panel" style="margin-top:12px">
      <h4>Neighborhoods along the way</h4>
      <p>${escapeHtml(result.anatomical_summary)}</p>
      <div class="stepper">${anatomy}</div>
    </div>
    <div class="grid-2" style="margin-top:12px">
      <div class="panel">
        <h4>Tap a cell to see branches</h4>
        <p>A neuron is a crossroads, not a one-way street.</p>
        ${renderBranch()}
      </div>
      <div class="panel">
        <h4>Busy crossroads (not “important” in real life)</h4>
        <p>These ranks are only inside this tiny map.</p>
        ${hubs}
      </div>
    </div>
  `;

  els.exploreResults.querySelectorAll(".path-tab").forEach((btn) => {
    btn.addEventListener("click", async () => {
      state.selectedPath = Number(btn.dataset.i);
      state.selectedNeuron = state.result.paths[state.selectedPath]?.neuron_ids[0] || null;
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

function neuronCard(neuron, index) {
  const selected = neuron.id === state.selectedNeuron ? "selected" : "";
  return `
    <button class="node ${selected}" type="button" data-neuron="${escapeHtml(neuron.id)}" style="--i:${index}">
      <div class="nid">${escapeHtml(neuron.id)}</div>
      <h4>${escapeHtml(neuron.name)}</h4>
      <div class="meta">${escapeHtml(neuron.cell_type)} · ${escapeHtml(neuron.region_label)}</div>
    </button>`;
}

function edgeLabel(synapses, index) {
  return `<div class="edge" style="--i:${index}"><span class="pulse"></span>${synapses}<small>synapses</small></div>`;
}

function renderBranch() {
  const data = state.branch;
  if (!data) return `<p>Tap a glowing cell on the path.</p>`;
  const col = (rows, title) => `
    <div>
      <strong>${title}</strong>
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
    <p><strong>${escapeHtml(data.neuron.name)}</strong> — ${escapeHtml(data.neuron.description || "")}</p>
    <div class="branch-cols">
      ${col(data.upstream, "Before")}
      ${col(data.downstream, "After")}
    </div>`;
}

function renderCompare() {
  const cmp = state.compare;
  if (!cmp) return;
  els.results.hidden = false;
  els.exploreResults.hidden = true;
  els.compareResults.hidden = false;
  els.status.textContent = "Do the two scenes share any cells?";
  setMood("idle", "idle", "Two scenes, one map. Shared cells are meeting points in the wiring — not proof they happen together.");
  const side = (label, result) => {
    const path = result.paths?.[0];
    if (!path) return `<div class="panel"><h4>${label}</h4><p>No path.</p></div>`;
    return `
      <div class="panel">
        <h4>${label}</h4>
        <p>${path.hop_count} hops · ${escapeHtml(path.region_labels.join(" → "))}</p>
        <p>${escapeHtml(path.explanation)}</p>
      </div>`;
  };
  const shared = (cmp.shared_neuron_ids || []).join(", ") || "none on the top routes";
  els.storyCard.innerHTML = `
    <h3>Taste food vs watch TV</h3>
    <p>${escapeHtml(cmp.comparison_explanation)}</p>
    <p>Shared cells: ${escapeHtml(shared)}.</p>
  `;
  els.compareResults.innerHTML = `
    <div class="compare-split">
      ${side("Taste food", cmp.path_a)}
      ${side("Watch TV", cmp.path_b)}
    </div>
  `;
}

function bindSearch(input, suggestBox, kindSelect) {
  let timer = 0;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = window.setTimeout(async () => {
      const q = input.value.trim();
      if (kindSelect.value === "category") {
        const hits = CATEGORIES.filter((c) => c.toLowerCase().includes(q.toLowerCase() || ""));
        renderSuggest(suggestBox, hits.map((c) => ({ id: c, name: c, cell_type: "category" })), input, kindSelect);
        return;
      }
      if (q.length < 1) {
        suggestBox.hidden = true;
        return;
      }
      try {
        renderSuggest(suggestBox, await api.searchNeurons(q, 8), input, kindSelect);
      } catch {
        suggestBox.hidden = true;
      }
    }, 160);
  });
  document.addEventListener("click", (event) => {
    if (!suggestBox.contains(event.target) && event.target !== input) suggestBox.hidden = true;
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
        `<button type="button" data-id="${escapeHtml(n.id)}"><strong>${escapeHtml(n.id)}</strong> · ${escapeHtml(n.name)}</button>`
    )
    .join("");
  box.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (kindSelect.value !== "category") kindSelect.value = "neuron";
      input.value = btn.dataset.id;
      box.hidden = true;
    });
  });
}

els.findForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  state.activeId = null;
  renderBoard();
  setMood("idle", "idle", "Scientist mode is tracing a custom path.");
  showBusy("Tracing…");
  try {
    state.result = await api.findPaths(
      api.spec(els.sourceKind.value, els.sourceValue.value),
      api.spec(els.destKind.value, els.destValue.value)
    );
    state.story = {
      headline: "Custom search",
      beats: ["You picked the start and end.", "Same rules: this is a wiring map, not a behavior recording."],
    };
    state.selectedPath = 0;
    state.selectedNeuron = state.result.paths[0]?.neuron_ids[0] || null;
    await refreshBranch();
    renderStory();
    renderExplore();
  } catch (error) {
    showError(error);
  }
});

els.demoBtn.addEventListener("click", () => playScenario("watch-tv"));

els.compareTasteTv.addEventListener("click", async () => {
  state.activeId = null;
  renderBoard();
  showBusy("Comparing taste and TV wiring…");
  try {
    state.compare = await api.comparePaths(
      { source: api.spec("neuron", "GRN_sweet"), destination: api.spec("neuron", "MN_proboscis") },
      { source: api.spec("neuron", "R1"), destination: api.spec("neuron", "DNg13") }
    );
    renderCompare();
    els.results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showError(error);
  }
});

els.scientistToggle.addEventListener("click", () => {
  const open = !els.scientistPanel.open;
  els.scientistPanel.open = open;
  els.scientistToggle.setAttribute("aria-expanded", String(open));
  if (open) els.scientistPanel.scrollIntoView({ behavior: "smooth" });
});

bindSearch(els.sourceValue, els.sourceSuggest, els.sourceKind);
bindSearch(els.destValue, els.destSuggest, els.destKind);

(async function boot() {
  try {
    state.scenarios = await api.scenarios();
    renderBoard();
  } catch (error) {
    showError(error);
  }
})();
