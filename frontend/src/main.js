import * as api from "./api.js";

const HARDCODED_SCENES = [
  { id: "taste-food", title: "Taste Food", emoji: "🍯", mood: "food", pose: "eating", play_label: "Tap to taste", hook: "The fly lands on something sweet.", blurb: "Sugar hits the mouthparts.", preferred_source: "GRN_sweet", preferred_destination: "LegMN_T1" },
  { id: "watch-tv", title: "Watch TV", emoji: "📺", mood: "tv", pose: "watching", play_label: "Tap to watch", hook: "The fly stares at a glowing screen.", blurb: "Light hits the eyes.", preferred_source: "R1", preferred_destination: "DNg13" },
  { id: "zapped", title: "Zapped By Human", emoji: "⚡", mood: "zap", pose: "jumping", play_label: "Tap to zap", hook: "A human swats or pokes the fly.", blurb: "Touch can reach the giant fiber.", preferred_source: "BR_mech", preferred_destination: "DNp01" },
  { id: "hot", title: "Hot Sensation", emoji: "🔥", mood: "hot", pose: "hot", play_label: "Tap the heat", hook: "It gets too hot.", blurb: "Aristal hot cells toward the legs.", preferred_source: "HC_arista", preferred_destination: "LegMN_T2" },
  { id: "cold", title: "Cold Sensation", emoji: "❄️", mood: "cold", pose: "shivering", play_label: "Tap the chill", hook: "A chill hits the antenna.", blurb: "Aristal cold cells toward the legs.", preferred_source: "CC_arista", preferred_destination: "LegMN_T2" },
  { id: "smell-yummy", title: "Smell Something Yummy", emoji: "🍓", mood: "yummy", pose: "sniffing", play_label: "Tap to sniff", hook: "A tasty smell drifts by.", blurb: "Food odor toward DNg13.", preferred_source: "ORN_DM1", preferred_destination: "DNg13" },
  { id: "hear-buzz", title: "Hear a Buzz", emoji: "🎵", mood: "buzz", pose: "listening", play_label: "Tap to listen", hook: "The antennae pick up a buzz.", blurb: "Johnston’s organ toward the legs.", preferred_source: "JO_A", preferred_destination: "LegMN_T2" },
  { id: "smell-bad", title: "Smell Something Bad", emoji: "🤢", mood: "stinky", pose: "recoil", play_label: "Tap the stink", hook: "An unpleasant odor hits.", blurb: "A second smell channel toward DNp56.", preferred_source: "ORN_DL5", preferred_destination: "DNp56" },
];

const els = {
  board: document.getElementById("scenario-board"),
  results: document.getElementById("results"),
  exploreResults: document.getElementById("explore-results"),
  compareResults: document.getElementById("compare-results"),
  status: document.getElementById("status"),
  mascotLine: document.getElementById("mascot-line"),
  findForm: document.getElementById("find-form"),
  compareTasteTv: document.getElementById("compare-taste-tv"),
  demoBtn: document.getElementById("demo-btn"),
  sourceKind: document.getElementById("source-kind"),
  sourceValue: document.getElementById("source-value"),
  destKind: document.getElementById("dest-kind"),
  destValue: document.getElementById("dest-value"),
  sourceSuggest: document.getElementById("source-suggest"),
  destSuggest: document.getElementById("dest-suggest"),
  brainCard: document.getElementById("brain-card"),
  actionCard: document.getElementById("action-card"),
  scientistHint: document.getElementById("scientist-hint"),
};

const state = {
  scenarios: [],
  activeId: null,
  result: null,
  compare: null,
  selectedPath: 0,
  selectedNeuron: null,
  branch: null,
  story: null,
  scenario: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function setTab(tab) {
  document.body.dataset.tab = tab;
  document.querySelectorAll(".exhibit-tabs [role='tab']").forEach((btn) => {
    btn.setAttribute("aria-selected", String(btn.dataset.tab === tab));
  });
  ["play", "brain", "action", "scientist"].forEach((name) => {
    const panel = document.getElementById(`panel-${name}`);
    if (panel) panel.hidden = name !== tab;
  });
}

function setMood(mood, pose, line) {
  document.body.dataset.mood = mood || "idle";
  document.body.dataset.pose = pose || "idle";
  document.body.classList.toggle("flash", mood === "zap");
  if (line) els.mascotLine.textContent = line;
  if (mood === "zap") window.setTimeout(() => document.body.classList.remove("flash"), 600);
}

function showBusy(message) {
  els.results.hidden = false;
  els.compareResults.hidden = true;
  els.exploreResults.hidden = false;
  els.status.textContent = message;
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

function fillSideTabs(scenario, story, path) {
  const brain = story?.brain_story?.length ? story.brain_story : [
    path ? `This map travels ${path.region_labels.join(" → ")}.` : "Play a scene to fill this tab.",
  ];
  const actions = story?.possible_actions?.length ? story.possible_actions : [
    "Movement-related cells sit downstream on some maps.",
    "That could support walking, turning, feeding, or startle — it does not prove the fly will do those things.",
  ];
  els.brainCard.innerHTML = `
    <h3>${escapeHtml(scenario?.title || "What happens in the brain")}</h3>
    <ol>${brain.map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ol>
  `;
  els.actionCard.innerHTML = `
    <h3>What the fly might do</h3>
    <p>These are possible uses of structurally connected motor or descending cells — not predictions.</p>
    <ol>${actions.map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ol>
  `;
}

async function playScenario(id) {
  const scenario = state.scenarios.find((s) => s.id === id) || HARDCODED_SCENES.find((s) => s.id === id);
  if (!scenario) return;
  state.activeId = id;
  state.scenario = scenario;
  renderBoard();
  setMood(scenario.mood, scenario.pose, scenario.hook);
  setTab("play");
  showBusy("Following the wires…");
  try {
    let packed;
    try {
      packed = await api.runScenario(id);
    } catch {
      const result = await api.findPaths(
        api.spec("neuron", scenario.preferred_source),
        api.spec("neuron", scenario.preferred_destination)
      );
      packed = { scenario, result, story: { headline: scenario.hook, beats: [scenario.hook], brain_story: [], possible_actions: [] } };
    }
    state.result = packed.result;
    state.story = packed.story;
    state.scenario = packed.scenario || scenario;
    state.selectedPath = 0;
    state.selectedNeuron = packed.result.paths[0]?.neuron_ids[0] || null;
    await refreshBranch();
    fillSideTabs(state.scenario, state.story, packed.result.paths[0]);
    renderExplore();
    els.results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    els.status.textContent = error.message || String(error);
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
  els.compareResults.hidden = true;
  if (!result.paths.length) {
    const hint = (result.suggestions || []).join(", ");
    els.status.textContent = "We could not wire that pair — try a suggestion.";
    els.exploreResults.innerHTML = `<p>${escapeHtml(result.anatomical_summary)}</p>${hint ? `<p class="hint">Did you mean ${escapeHtml(hint)}?</p>` : ""}`;
    return;
  }
  const path = result.paths[state.selectedPath] || result.paths[0];
  els.status.textContent = `${result.paths.length} routes · ${path.hop_count} hops · wiring map only`;

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
        <div class="bar"><i style="--w:${Math.max(10, row.relative * 100)}%"></i></div>
      </div>`
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
    <div class="panel"><h4>In plain words</h4><p>${escapeHtml(path.explanation)}</p></div>
    <div class="grid-2" style="margin-top:12px">
      <div class="panel"><h4>Why this path?</h4><p>${escapeHtml(path.why_this_path)}</p></div>
      <div class="panel"><h4>How strong are the links?</h4>${strength}</div>
    </div>
    <div class="panel" style="margin-top:12px">
      <h4>Neighborhoods along the way</h4>
      <p>${escapeHtml(result.anatomical_summary)}</p>
      <div class="stepper">${path.region_labels.map((label) => `<span>${escapeHtml(label)}</span>`).join("")}</div>
    </div>
    <div class="grid-2" style="margin-top:12px">
      <div class="panel"><h4>Tap a cell to see branches</h4>${renderBranch()}</div>
      <div class="panel"><h4>Busy crossroads (only on this tiny map)</h4>${(result.hubs || []).map((h) => `<article class="hub-item"><strong>${escapeHtml(h.neuron.name)}</strong><p>${escapeHtml(h.interpretation)}</p></article>`).join("")}</div>
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
  if (!data) return `<p>Tap a cell on the path.</p>`;
  const col = (rows, title) => `
    <div><strong>${title}</strong>${rows.map((row) => `<div class="neighbor" data-neuron="${escapeHtml(row.neuron.id)}"><span>${escapeHtml(row.neuron.name)}</span><span>${row.synapses}</span></div>`).join("")}</div>`;
  return `<p><strong>${escapeHtml(data.neuron.name)}</strong></p><div class="branch-cols">${col(data.upstream, "Before")}${col(data.downstream, "After")}</div>`;
}

function renderCompare() {
  const cmp = state.compare;
  if (!cmp) return;
  els.results.hidden = false;
  els.exploreResults.hidden = true;
  els.compareResults.hidden = false;
  els.status.textContent = "Do the two scenes share any cells?";
  setMood("idle", "idle", "Shared cells are meeting points in the wiring — not proof they happen together.");
  const side = (label, result) => {
    const path = result.paths?.[0];
    if (!path) return `<div class="panel"><h4>${label}</h4><p>No path.</p></div>`;
    return `<div class="panel"><h4>${label}</h4><p>${path.hop_count} hops · ${escapeHtml(path.region_labels.join(" → "))}</p><p>${escapeHtml(path.explanation)}</p></div>`;
  };
  els.compareResults.innerHTML = `
    <p>${escapeHtml(cmp.comparison_explanation)}</p>
    <p>Shared cells: ${escapeHtml((cmp.shared_neuron_ids || []).join(", ") || "none on the top routes")}.</p>
    <div class="compare-split">${side("Taste food", cmp.path_a)}${side("Watch TV", cmp.path_b)}</div>
  `;
}

function bindSearch(input, suggestBox, kindSelect) {
  let timer = 0;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = window.setTimeout(async () => {
      const q = input.value.trim();
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
    .map((n) => `<button type="button" data-id="${escapeHtml(n.id)}"><strong>${escapeHtml(n.id)}</strong> · ${escapeHtml(n.name)}</button>`)
    .join("");
  box.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      kindSelect.value = "neuron";
      input.value = btn.dataset.id;
      box.hidden = true;
    });
  });
}

document.querySelectorAll(".exhibit-tabs [role='tab']").forEach((btn) => {
  btn.addEventListener("click", () => setTab(btn.dataset.tab));
});

els.findForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setTab("play");
  showBusy("Tracing…");
  try {
    const result = await api.findPaths(
      api.spec(els.sourceKind.value, els.sourceValue.value),
      api.spec(els.destKind.value, els.destValue.value)
    );
    state.result = result;
    state.story = {
      headline: "Custom search",
      beats: [result.resolve_note || "You picked the start and end."],
      brain_story: result.paths[0] ? [`This custom map travels ${result.paths[0].region_labels.join(" → ")}.`] : [],
      possible_actions: ["Custom searches still only show wiring, not what the fly will do."],
    };
    state.selectedPath = 0;
    state.selectedNeuron = result.paths[0]?.neuron_ids[0] || null;
    els.scientistHint.textContent = result.fallback_used
      ? result.resolve_note
      : result.suggestions?.length
        ? `Did you mean ${result.suggestions.join(", ")}?`
        : "";
    await refreshBranch();
    fillSideTabs({ title: "Scientist search" }, state.story, result.paths[0]);
    renderExplore();
  } catch (error) {
    els.status.textContent = error.message || String(error);
    els.scientistHint.textContent = "Try Visual → Motor, or R1 → DNg13, or a Play scene.";
  }
});

els.demoBtn.addEventListener("click", () => playScenario("watch-tv"));

els.compareTasteTv.addEventListener("click", async () => {
  setTab("play");
  showBusy("Comparing taste and TV wiring…");
  try {
    state.compare = await api.comparePaths(
      { source: api.spec("neuron", "GRN_sweet"), destination: api.spec("neuron", "LegMN_T1") },
      { source: api.spec("neuron", "R1"), destination: api.spec("neuron", "DNg13") }
    );
    renderCompare();
    els.results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    els.status.textContent = error.message || String(error);
  }
});

bindSearch(els.sourceValue, els.sourceSuggest, els.sourceKind);
bindSearch(els.destValue, els.destSuggest, els.destKind);

(async function boot() {
  try {
    state.scenarios = await api.scenarios();
    if (!state.scenarios?.length) state.scenarios = HARDCODED_SCENES;
  } catch {
    state.scenarios = HARDCODED_SCENES;
  }
  renderBoard();
  setTab("play");
})();
