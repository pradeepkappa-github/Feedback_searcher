const state = {
  company: "",
  source: "",
  query: "",
  feedback: [],
  overview: null,
  companies: [],
  topics: [],
  sources: [],
  domain: null
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

async function api(path, options) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) throw new Error(`API request failed: ${path}`);
  return response.json();
}

async function init() {
  bindEvents();
  await loadAll();
  render();
  await askQuestion();
}

function bindEvents() {
  $$("nav button").forEach((button) => {
    button.addEventListener("click", () => {
      $$("nav button").forEach((item) => item.classList.remove("active"));
      $$(".view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      $(`#${button.dataset.view}`).classList.add("active");
    });
  });

  $("#companyFilter").addEventListener("change", async (event) => {
    state.company = event.target.value;
    await loadFeedback();
    renderFeedback();
  });

  $("#sourceFilter").addEventListener("change", async (event) => {
    state.source = event.target.value;
    await loadFeedback();
    renderFeedback();
  });

  $("#queryInput").addEventListener("input", async (event) => {
    state.query = event.target.value;
    await loadFeedback();
    renderFeedback();
  });

  $("#askForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await askQuestion();
  });
}

async function loadAll() {
  await Promise.all([
    loadFeedback(),
    api("/api/analytics/overview").then((data) => (state.overview = data)),
    api("/api/analytics/companies").then((data) => (state.companies = data)),
    api("/api/analytics/topics").then((data) => (state.topics = data)),
    api("/api/sources/status").then((data) => (state.sources = data)),
    api("/api/domains/telecom").then((data) => (state.domain = data))
  ]);
}

async function loadFeedback() {
  const params = new URLSearchParams();
  if (state.company) params.set("company", state.company);
  if (state.source) params.set("source", state.source);
  if (state.query) params.set("query", state.query);
  state.feedback = await api(`/api/feedback?${params.toString()}`);
}

function render() {
  populateFilters();
  renderHero();
  renderOverview();
  renderCompanies();
  renderTopics();
  renderFeedback();
  renderSources();
  renderDomain();
}

function populateFilters() {
  const companies = [...new Set(state.companies.map((item) => item.company))];
  const sources = [...new Set(state.sources.map((item) => item.name))];
  fillSelect("#companyFilter", companies, "All companies");
  fillSelect("#sourceFilter", sources, "All sources");
}

function fillSelect(selector, values, label) {
  const select = $(selector);
  const current = select.value;
  select.innerHTML = `<option value="">${label}</option>${values
    .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)
    .join("")}`;
  select.value = current;
}

function renderHero() {
  $("#heroTitle").textContent = "Telecom feedback is clustered around billing, outages, support, and promotions.";
  $("#heroDetail").textContent = `${state.overview.total_feedback} records analyzed from phase-one controlled sources with ${percent(state.overview.average_confidence)} average model confidence.`;
}

function renderOverview() {
  $("#totalFeedback").textContent = state.overview.total_feedback.toLocaleString();
  $("#positiveShare").textContent = percent(state.overview.positive_share);
  $("#negativeShare").textContent = percent(state.overview.negative_share);
  $("#avgConfidence").textContent = percent(state.overview.average_confidence);
  $("#criticalIssues").innerHTML = state.overview.critical_issues.map((record) => issueCard(record)).join("");
}

function renderCompanies() {
  $("#companyBars").innerHTML = state.companies
    .map((item) => barRow(item.company, item.positive_share, item.positive_share < 0.5 ? "var(--danger)" : "var(--accent)"))
    .join("");
}

function renderTopics() {
  $("#topicBars").innerHTML = state.topics
    .map((item) => barRow(item.topic, item.share, item.share > 0.2 ? "var(--danger)" : "var(--blue)"))
    .join("");
}

function barRow(label, share, color) {
  return `
    <div class="bar-row">
      <strong>${escapeHtml(label)}</strong>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round(share * 100)}%; background:${color}"></div></div>
      <span>${percent(share)}</span>
    </div>
  `;
}

function issueCard(record) {
  return `
    <article class="issue">
      <div>
        <strong>${escapeHtml(record.analysis.company)} · ${escapeHtml(record.analysis.topics.slice(0, 2).join(", "))}</strong>
        <p>${escapeHtml(record.analysis.summary)}</p>
      </div>
      <span class="score">${Math.round(record.analysis.urgency_score * 100)}</span>
    </article>
  `;
}

function renderFeedback() {
  $("#feedbackList").innerHTML = state.feedback.map((record) => {
    const sentimentClass = record.analysis.sentiment_score > 0.2 ? "good" : record.analysis.sentiment_score < -0.2 ? "bad" : "";
    return `
      <article class="feedback-card">
        <div class="tags">
          <span class="tag">${escapeHtml(record.analysis.company)}</span>
          <span class="tag">${escapeHtml(record.analysis.product || "Unknown product")}</span>
          <span class="tag ${sentimentClass}">${escapeHtml(record.analysis.sentiment_label)}</span>
          <span class="tag">${escapeHtml(record.analysis.emotion)}</span>
          ${record.analysis.topics.map((topic) => `<span class="tag">${escapeHtml(topic)}</span>`).join("")}
        </div>
        <p>${escapeHtml(record.cleaned_text)}</p>
        <div class="meta">${escapeHtml(record.source)} · ${escapeHtml(record.location || "Unknown location")} · confidence ${percent(record.analysis.confidence)} · <a href="${record.source_url}">source</a></div>
      </article>
    `;
  }).join("") || "<p>No matching feedback records.</p>";
}

async function askQuestion() {
  const question = $("#question").value.trim();
  const askButton = $("#askButton");
  const answer = $("#answer");
  if (!question) {
    answer.textContent = "Enter a question first.";
    return;
  }

  askButton.disabled = true;
  askButton.textContent = "Thinking...";
  answer.textContent = `Thinking about: ${question}`;

  const payload = {
    question,
    company: state.company || undefined,
    days: 7
  };

  try {
    const response = await api("/api/assistant/ask", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    const answeredAt = new Date().toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit"
    });
    answer.textContent = [
      `Answered ${answeredAt}: ${response.answer}`,
      `Confidence ${percent(response.confidence)} from ${response.records_analyzed} records.`
    ].join(" ");
    $("#storyConfidence").textContent = `${percent(response.confidence)} confidence`;
    $("#storyBody").innerHTML = `
      <h4>Question</h4>
      <p>${escapeHtml(question)}</p>
      <h4>What happened?</h4>
      <p>${escapeHtml(response.answer)}</p>
      <h4>Evidence</h4>
      <p>Supporting records: ${response.supporting_record_ids.map(escapeHtml).join(", ") || "none"}</p>
      <h4>Grounding</h4>
      <p>Every story response returns source URLs, record IDs, confidence, and the number of records analyzed.</p>
    `;
  } catch (error) {
    console.error(error);
    answer.textContent = `Ask AI failed: ${error.message}`;
  } finally {
    askButton.disabled = false;
    askButton.textContent = "Ask AI";
  }
}

function renderSources() {
  $("#sourceStatus").innerHTML = state.sources.map((source) => `
    <article class="source-card">
      <strong>${escapeHtml(source.name)} · ${escapeHtml(source.status)}</strong>
      <div class="meta">${source.records_collected} records · ${source.average_latency_ms}ms · ${escapeHtml(source.policy_note)}</div>
    </article>
  `).join("");
}

function renderDomain() {
  $("#domainPack").textContent = JSON.stringify(state.domain, null, 2);
}

function percent(value) {
  return `${Math.round(value * 100)}%`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

init().catch((error) => {
  console.error(error);
  $("#heroTitle").textContent = "Unable to load feedback intelligence.";
  $("#heroDetail").textContent = error.message;
});
