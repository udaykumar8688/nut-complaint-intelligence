const input = document.querySelector("#complaint-input");
const analyzeButton = document.querySelector("#analyze-button");
const clearButton = document.querySelector("#clear-button");
const characterCount = document.querySelector("#character-count");
const resultStatus = document.querySelector("#result-status");
const resultEmpty = document.querySelector("#result-empty");
const resultContent = document.querySelector("#result-content");
const predictedCategory = document.querySelector("#predicted-category");
const confidenceValue = document.querySelector("#confidence-value");
const confidenceRing = document.querySelector("#confidence-ring");
const confidenceLabel = document.querySelector("#confidence-label");
const decisionSummary = document.querySelector("#decision-summary");
const probabilityBars = document.querySelector("#probability-bars");
const evidenceList = document.querySelector("#evidence-list");
const tokenCount = document.querySelector("#token-count");
const activityList = document.querySelector("#activity-list");
const clearHistoryButton = document.querySelector("#clear-history");
const typingWrap = document.querySelector(".typing-wrap");
const nutLoader = document.querySelector("#nut-loader");
const loaderFill = document.querySelector("#loader-progress-fill");
const loaderPercent = document.querySelector("#loader-percent");
const loaderMessage = document.querySelector("#loader-message");

const state = { history: [], exampleRun: 0 };
const paletteClass = {
  Billing: "billing",
  "Customer Service": "service",
  "Technical Support": "technical",
  "Account Management": "account",
  "Security & Fraud": "security",
  "Orders & Delivery": "orders",
};

function startNutLoader() {
  if (!nutLoader || !loaderFill || !loaderPercent) return;

  const minimumLoaderTime = 10_000;
  const startTime = performance.now();
  const phases = [
    { at: 0, text: "Connecting complaint signals" },
    { at: 2_100, text: "Mapping customer language" },
    { at: 4_250, text: "Learning routing patterns" },
    { at: 6_450, text: "Calibrating confidence" },
    { at: 8_500, text: "NUT intelligence ready" },
  ];
  let progress = 0;
  let isFinished = false;
  let pageReady = document.readyState === "complete";
  let lastPhase = -1;
  const paintProgress = (value) => {
    progress = Math.min(100, value);
    loaderFill.style.transform = `scaleX(${progress / 100})`;
    loaderPercent.textContent = `${Math.round(progress)}%`;
  };
  const finish = () => {
    if (isFinished) return;
    isFinished = true;
    paintProgress(100);
    window.setTimeout(() => {
      nutLoader.classList.add("is-complete");
      window.setTimeout(() => nutLoader.remove(), 600);
    }, 160);
  };
  const update = (now) => {
    if (isFinished) return;
    const elapsed = now - startTime;
    const activePhase = phases.reduce((index, phase, currentIndex) => (elapsed >= phase.at ? currentIndex : index), 0);
    if (activePhase !== lastPhase && loaderMessage) {
      lastPhase = activePhase;
      loaderMessage.style.opacity = "0";
      loaderMessage.style.transform = "translateY(4px)";
      window.setTimeout(() => {
        loaderMessage.textContent = phases[activePhase].text;
        const dots = document.createElement("span");
        dots.className = "loader-dots";
        dots.textContent = "...";
        loaderMessage.appendChild(dots);
        loaderMessage.style.opacity = "1";
        loaderMessage.style.transform = "translateY(0)";
      }, 130);
    }
    paintProgress(Math.min(98, (elapsed / minimumLoaderTime) * 100));
    if (elapsed >= minimumLoaderTime && pageReady) {
      finish();
      return;
    }
    window.requestAnimationFrame(update);
  };

  window.addEventListener("load", () => { pageReady = true; }, { once: true });
  window.requestAnimationFrame(update);
}

function updateCount() {
  characterCount.textContent = `${input.value.length.toLocaleString()} / 3,000`;
}

function setStatus(text, type) {
  resultStatus.textContent = text;
  resultStatus.className = `status-pill ${type}`;
}

function renderBars(probabilities) {
  probabilityBars.replaceChildren();
  probabilities.forEach(({ category, probability }) => {
    const row = document.createElement("div");
    const label = document.createElement("span");
    const track = document.createElement("div");
    const value = document.createElement("div");
    const score = document.createElement("strong");

    row.className = "probability-row";
    label.textContent = category;
    track.className = "bar-track";
    value.className = `bar-value ${paletteClass[category] || "service"}`;
    score.textContent = `${Math.round(probability * 100)}%`;
    track.appendChild(value);
    row.append(label, track, score);
    probabilityBars.appendChild(row);

    requestAnimationFrame(() => {
      value.style.width = `${probability * 100}%`;
    });
  });
}

function renderEvidence(evidence) {
  evidenceList.replaceChildren();
  if (!evidence.length) {
    const note = document.createElement("span");
    note.className = "evidence-muted";
    note.textContent = "No familiar keywords were found. NUT used the overall message pattern.";
    evidenceList.appendChild(note);
    return;
  }

  evidence.forEach((token) => {
    const tag = document.createElement("span");
    tag.className = "evidence-tag";
    tag.textContent = token;
    evidenceList.appendChild(tag);
  });
}

function renderResult(data) {
  const percentage = Math.round(data.confidence * 100);
  resultEmpty.classList.add("hidden");
  resultContent.classList.remove("hidden");
  predictedCategory.textContent = data.category;
  confidenceValue.textContent = `${percentage}%`;
  confidenceLabel.textContent = data.confidence_label;
  tokenCount.textContent = `${data.tokens_analyzed} signals`;
  decisionSummary.textContent = `${data.category} is the strongest match, ahead of the next route by ${Math.round(data.margin * 100)} percentage points.`;
  confidenceRing.style.strokeDashoffset = String(194.78 * (1 - data.confidence));
  renderBars(data.probabilities);
  renderEvidence(data.evidence);
  setStatus("Route found", "ready");
}

function renderHistory() {
  activityList.replaceChildren();
  if (!state.history.length) {
    const placeholder = document.createElement("div");
    const dot = document.createElement("span");
    dot.className = "pulse-dot";
    placeholder.className = "activity-placeholder";
    placeholder.append(dot, " Your recent NUT routes will appear here during this demo.");
    activityList.appendChild(placeholder);
    return;
  }

  state.history.slice(0, 4).forEach((record) => {
    const item = document.createElement("div");
    const accent = document.createElement("span");
    const copy = document.createElement("div");
    const complaint = document.createElement("strong");
    const meta = document.createElement("span");
    const confidence = document.createElement("span");

    item.className = "activity-item";
    accent.className = `activity-color ${paletteClass[record.category] || "service"}`;
    copy.className = "activity-copy";
    complaint.textContent = record.complaint;
    meta.textContent = `${record.category} / just now`;
    confidence.className = "activity-confidence";
    confidence.textContent = `${Math.round(record.confidence * 100)}%`;
    copy.append(complaint, meta);
    item.append(accent, copy, confidence);
    activityList.appendChild(item);
  });
}

function showResultError(message) {
  resultContent.classList.add("hidden");
  resultEmpty.classList.remove("hidden");
  resultEmpty.replaceChildren();
  const orbit = document.createElement("div");
  const marker = document.createElement("i");
  const title = document.createElement("strong");
  const copy = document.createElement("p");
  orbit.className = "empty-orbit";
  marker.textContent = "!";
  title.textContent = "NUT could not read that message";
  copy.textContent = message;
  orbit.appendChild(marker);
  resultEmpty.append(orbit, title, copy);
}

async function analyzeComplaint() {
  const complaint = input.value.trim();
  if (!complaint) {
    input.focus();
    setStatus("Write a message first", "error");
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.classList.add("loading");
  analyzeButton.querySelector("span").textContent = "NUT is reading";
  setStatus("Finding a route", "analyzing");

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ complaint }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The model could not analyse this complaint.");
    renderResult(data);
    state.history.unshift({ complaint, category: data.category, confidence: data.confidence });
    renderHistory();
  } catch (error) {
    setStatus("Analysis unavailable", "error");
    showResultError(error.message);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.classList.remove("loading");
    analyzeButton.querySelector("span").textContent = "Find the route";
  }
}

async function typeExample(text) {
  const run = ++state.exampleRun;
  input.value = "";
  input.focus();
  typingWrap.classList.add("is-typing");
  updateCount();

  for (const character of text) {
    if (run !== state.exampleRun) return;
    input.value += character;
    updateCount();
    await new Promise((resolve) => window.setTimeout(resolve, 9));
  }

  if (run === state.exampleRun) typingWrap.classList.remove("is-typing");
}

async function loadModelInformation() {
  try {
    const response = await fetch("/api/model-info");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    document.querySelector("#stat-algorithm").textContent = "Naive Bayes + cues";
    document.querySelector("#stat-training").textContent = data.training_examples;
    document.querySelector("#stat-vocabulary").textContent = data.vocabulary_size;
    document.querySelector("#stat-categories").textContent = data.categories.length;
  } catch (error) {
    document.querySelector("#stat-training").textContent = "Offline";
  }
}

function enableScrollReveals() {
  const elements = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("visible"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  elements.forEach((element) => observer.observe(element));
}

input.addEventListener("input", () => {
  state.exampleRun += 1;
  typingWrap.classList.remove("is-typing");
  updateCount();
});
input.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") analyzeComplaint();
});
analyzeButton.addEventListener("click", analyzeComplaint);
clearButton.addEventListener("click", () => {
  state.exampleRun += 1;
  input.value = "";
  typingWrap.classList.remove("is-typing");
  updateCount();
  input.focus();
});
document.querySelectorAll(".example-chip").forEach((button) => {
  button.addEventListener("click", () => typeExample(button.dataset.example));
});
clearHistoryButton.addEventListener("click", () => {
  state.history = [];
  renderHistory();
});

updateCount();
renderHistory();
loadModelInformation();
enableScrollReveals();
startNutLoader();
