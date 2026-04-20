"use strict";

// ── Session ──
let sessionId = `s-${Math.random().toString(36).slice(2, 10)}`;
const userId  = `u-${Math.random().toString(36).slice(2, 10)}`;

// ── Charts registry ──
const charts = {};

// ── Issue-type display config ──
const ISSUE_CONFIG = {
  BUG:             { label: "🐛 Bug",          cls: "issue-bug" },
  FEATURE_REQUEST: { label: "💡 Feature",       cls: "issue-feature" },
  QUESTION:        { label: "❓ Question",      cls: "issue-question" },
  UNKNOWN:         { label: "·",               cls: "issue-unknown" },
};

// ── Log column config — priority order, auto-detect extras ──
const PRIORITY_COLS = ["ts", "level", "service", "event", "issue_type", "correlation_id"];
const SECONDARY_COLS = ["latency_ms", "model_used", "feature", "user_id_hash"];

// ── Init ──
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  setInterval(checkHealth, 15_000);
});

// ══════════════════════════════════════════
//  Navigation
// ══════════════════════════════════════════
function switchTab(name) {
  document.querySelectorAll(".nav-item").forEach(el =>
    el.classList.toggle("active", el.dataset.tab === name)
  );
  document.querySelectorAll(".tab-panel").forEach(el =>
    el.classList.toggle("active", el.id === `tab-${name}`)
  );
  if (name === "dashboard") refreshDashboard();
  if (name === "logs")      refreshLogs();
  if (name === "incidents") loadIncidents();
}

// ══════════════════════════════════════════
//  Health
// ══════════════════════════════════════════
async function checkHealth() {
  const dot        = document.getElementById("health-dot");
  const txt        = document.getElementById("health-text");
  const modelBadge = document.getElementById("model-badge");
  const modeBadge  = document.getElementById("mode-badge");
  try {
    const r = await fetch("/health");
    const d = await r.json();
    dot.className   = "status-dot ok";
    txt.textContent = d.mode === "live" ? "Online · OpenAI" : "Online · Mock";

    if (modelBadge) {
      modelBadge.textContent  = d.model ?? "";
      modelBadge.style.display = d.model ? "block" : "none";
    }
    if (modeBadge) {
      const isLive = d.mode === "live";
      modeBadge.textContent  = isLive ? "🟢 Live" : "🟡 Demo";
      modeBadge.className    = `mode-badge mode-${d.mode ?? "demo"}`;
      modeBadge.title        = isLive
        ? `Using real OpenAI API (${d.model})`
        : "Using Smart Mock — add OPENAI_API_KEY to .env for Live mode";
    }
  } catch {
    dot.className = "status-dot error";
    txt.textContent = "Offline";
    if (modeBadge) { modeBadge.textContent = "⚫ Offline"; modeBadge.className = "mode-badge mode-offline"; }
  }
}

// ══════════════════════════════════════════
//  Chat
// ══════════════════════════════════════════
function handleChatKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function onPersonaChange() {
  const persona = document.getElementById("chat-persona").value;
  const sub = document.getElementById("chat-subtitle");
  const labels = {
    default: "IP Tech Support",
    brief:   "IP Tech Support · Brief",
    verbose: "IP Tech Support · Verbose",
    english: "IP Tech Support · EN",
  };
  if (sub) sub.textContent = labels[persona] ?? "IP Tech Support";
}

async function sendMessage() {
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const msg     = input.value.trim();
  if (!msg) return;

  const feature = document.getElementById("chat-feature").value;
  const persona = document.getElementById("chat-persona").value;

  input.value      = "";
  input.disabled   = true;
  sendBtn.disabled = true;

  const welcome = document.querySelector(".chat-welcome");
  if (welcome) welcome.remove();

  appendMessage("user", msg, null);
  const loader = appendLoading();

  try {
    const r = await fetch("/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, session_id: sessionId, feature, message: msg, persona }),
    });
    const d = await r.json();
    loader.remove();

    if (!r.ok) {
      appendMessage("assistant", `Error ${r.status}: ${d.detail ?? "Unknown error"}`, null);
    } else {
      appendMessage("assistant", d.answer, {
        issue_type:     d.issue_type,
        latency_ms:     d.latency_ms,
        tokens_in:      d.tokens_in,
        tokens_out:     d.tokens_out,
        cost_usd:       d.cost_usd,
        quality_score:  d.quality_score,
        correlation_id: d.correlation_id,
        model_used:     d.model_used,
      });
    }
  } catch (err) {
    loader.remove();
    appendMessage("assistant", `Network error: ${err.message}`, null);
  } finally {
    input.disabled   = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

function appendMessage(role, content, meta) {
  const wrap   = document.getElementById("chat-messages");
  const el     = document.createElement("div");
  el.className = `message ${role}`;

  const bubble     = document.createElement("div");
  bubble.className = "message-bubble";

  // Issue type badge inside bubble (assistant only)
  if (meta?.issue_type && meta.issue_type !== "UNKNOWN" && role === "assistant") {
    const cfg  = ISSUE_CONFIG[meta.issue_type] ?? ISSUE_CONFIG.UNKNOWN;
    const tag  = document.createElement("span");
    tag.className   = `issue-badge ${cfg.cls}`;
    tag.textContent = cfg.label;
    bubble.appendChild(tag);
    bubble.appendChild(document.createElement("br"));
  }

  const txt = document.createTextNode(content);
  bubble.appendChild(txt);
  el.appendChild(bubble);

  if (meta) {
    const metaEl     = document.createElement("div");
    metaEl.className = "message-meta";
    const parts = [
      meta.latency_ms    != null ? `⏱ ${meta.latency_ms} ms`                    : null,
      meta.tokens_in     != null ? `↑${meta.tokens_in} ↓${meta.tokens_out} tok` : null,
      meta.cost_usd      != null ? `$${meta.cost_usd.toFixed(5)}`                : null,
      meta.quality_score != null ? `Q ${meta.quality_score.toFixed(2)}`          : null,
      meta.model_used               ? `[${meta.model_used}]`                     : null,
      meta.correlation_id           ? `#${meta.correlation_id}`                  : null,
    ].filter(Boolean);
    metaEl.textContent = parts.join("  ·  ");
    el.appendChild(metaEl);
  }

  wrap.appendChild(el);
  wrap.scrollTop = wrap.scrollHeight;
  return el;
}

function appendLoading() {
  const wrap   = document.getElementById("chat-messages");
  const el     = document.createElement("div");
  el.className = "message assistant message-loading";
  el.innerHTML = `<div class="message-bubble">
    <div class="thinking-label">AI đang suy nghĩ…</div>
    <div class="dots-row">
      <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    </div>
  </div>`;
  wrap.appendChild(el);
  wrap.scrollTop = wrap.scrollHeight;
  return el;
}

async function clearChat() {
  // Reset session → clear server-side conversation history
  await fetch(`/session/${sessionId}`, { method: "DELETE" }).catch(() => {});
  sessionId = `s-${Math.random().toString(36).slice(2, 10)}`;
  document.getElementById("chat-messages").innerHTML =
    `<div class="chat-welcome">
      <p>Xin chào! Tôi là <strong>AI Tech Support</strong> của cửa hàng thiết bị IP.</p>
      <p>Thử hỏi: <em>"Camera của tôi mất kết nối WiFi"</em> hoặc <em>"Giá NVR 16 kênh là bao nhiêu?"</em></p>
    </div>`;
}

// ══════════════════════════════════════════
//  Toast
// ══════════════════════════════════════════
function showToast(msg, type = "ok") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className   = `toast toast-${type}`;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 3500);
}

// ══════════════════════════════════════════
//  Dashboard
// ══════════════════════════════════════════
async function seedDemoData() {
  const btn = document.getElementById("seed-btn");
  if (btn) { btn.disabled = true; btn.textContent = "Seeding…"; }
  try {
    const r = await fetch("/seed?n=20", { method: "POST" });
    const d = await r.json();
    showToast(`✅ Seeded ${d.seeded} sample logs — refresh logs tab to view.`, "ok");
    await refreshDashboard();
  } catch (err) {
    showToast(`❌ Seed failed: ${err.message}`, "error");
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/></svg> Seed Data`; }
  }
}

async function refreshDashboard() {
  try {
    const [metricsRes, logsRes] = await Promise.all([
      fetch("/metrics").then(r => r.json()),
      fetch("/logs?n=200").then(r => r.json()),
    ]);
    updateCards(metricsRes);
    buildLatencyChart(metricsRes);
    buildTokenChart(metricsRes);
    buildIssueChart(logsRes);
    buildSLO(metricsRes);
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

function updateCards(d) {
  document.getElementById("m-traffic").textContent = d.traffic ?? 0;
  document.getElementById("m-p95").textContent =
    d.latency_p95 != null ? d.latency_p95.toFixed(0) : "—";
  document.getElementById("m-quality").textContent =
    d.quality_avg != null ? d.quality_avg.toFixed(2) : "—";
  document.getElementById("m-cost").textContent =
    d.total_cost_usd != null ? `$${d.total_cost_usd.toFixed(4)}` : "$0.0000";
}

function destroyChart(key) {
  if (charts[key]) { charts[key].destroy(); delete charts[key]; }
}

function buildLatencyChart(d) {
  destroyChart("latency");
  const ctx = document.getElementById("chart-latency").getContext("2d");
  charts.latency = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["P50", "P95", "P99"],
      datasets: [{
        data: [d.latency_p50 ?? 0, d.latency_p95 ?? 0, d.latency_p99 ?? 0],
        backgroundColor: ["rgba(88,166,255,.55)", "rgba(210,153,34,.55)", "rgba(248,81,73,.55)"],
        borderColor:     ["#58a6ff", "#d29922", "#f85149"],
        borderWidth: 1, borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { color: "#8b949e" }, grid: { color: "#21262d" } },
        x: { ticks: { color: "#8b949e" }, grid: { display: false } },
      },
    },
  });
}

function buildTokenChart(d) {
  destroyChart("tokens");
  const ctx = document.getElementById("chart-tokens").getContext("2d");
  charts.tokens = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Tokens In", "Tokens Out"],
      datasets: [{
        data: [d.tokens_in_total ?? 0, d.tokens_out_total ?? 0],
        backgroundColor: ["rgba(88,166,255,.65)", "rgba(124,58,237,.65)"],
        borderColor:     ["#58a6ff", "#7c3aed"],
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom", labels: { color: "#8b949e", font: { size: 11 } } } },
    },
  });
}

function buildIssueChart(logs) {
  destroyChart("issues");
  const ctx    = document.getElementById("chart-issues").getContext("2d");
  const counts = { BUG: 0, FEATURE_REQUEST: 0, QUESTION: 0 };
  for (const l of logs) {
    if (l.issue_type && l.issue_type in counts) counts[l.issue_type]++;
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  charts.issues = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["🐛 Bug", "💡 Feature Request", "❓ Question"],
      datasets: [{
        data: [counts.BUG, counts.FEATURE_REQUEST, counts.QUESTION],
        backgroundColor: ["rgba(248,81,73,.65)", "rgba(124,58,237,.65)", "rgba(88,166,255,.65)"],
        borderColor:     ["#f85149", "#7c3aed", "#58a6ff"],
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { color: "#8b949e", font: { size: 11 } } },
        subtitle: {
          display: total === 0,
          text: "No conversations yet",
          color: "#484f58",
          font: { size: 13 },
          padding: { top: 40 },
        },
      },
    },
  });
}

function buildSLO(d) {
  const slos = [
    { name: "P95 Latency", value: d.latency_p95 ?? 0,    fmt: v => `${v.toFixed(0)} ms`, ok: v => v <= 3000 },
    { name: "Quality Avg", value: d.quality_avg ?? 0,    fmt: v => v.toFixed(2),          ok: v => v >= 0.75 },
    { name: "Avg Cost/req", value: d.avg_cost_usd ?? 0,  fmt: v => `$${v.toFixed(5)}`,    ok: v => v <= 0.005 },
    { name: "Total Cost",  value: d.total_cost_usd ?? 0, fmt: v => `$${v.toFixed(4)}`,    ok: v => v <= 2.5 },
  ];
  document.getElementById("slo-list").innerHTML = slos.map(s => {
    const pass = s.ok(s.value);
    return `<div class="slo-item">
      <span class="slo-name">${s.name}</span>
      <span class="slo-value ${pass ? "slo-ok" : "slo-bad"}">${s.fmt(s.value)} ${pass ? "✓" : "✗"}</span>
    </div>`;
  }).join("");
}

// ══════════════════════════════════════════
//  Logs — dynamic columns
// ══════════════════════════════════════════
let allLogs = [];

async function refreshLogs() {
  try {
    const r = await fetch("/logs?n=200");
    allLogs  = await r.json();
    renderLogTable();
    const note = document.getElementById("log-schema-note");
    if (note) note.textContent = `${allLogs.length} records`;
  } catch (err) {
    console.error("Logs error:", err);
  }
}

function getActiveCols(logs) {
  // Always show priority cols; append secondary cols that have at least one non-null value
  const present = new Set(
    SECONDARY_COLS.filter(c => logs.some(l => l[c] != null && l[c] !== ""))
  );
  return [...PRIORITY_COLS, ...SECONDARY_COLS.filter(c => present.has(c))];
}

function renderLogTable() {
  filterLogs();
}

function filterLogs() {
  const search     = document.getElementById("log-search").value.toLowerCase();
  const levelF     = document.getElementById("log-level-filter").value;
  const issueF     = document.getElementById("log-issue-filter").value;

  const filtered = allLogs.filter(l => {
    if (levelF && l.level !== levelF) return false;
    if (issueF && l.issue_type !== issueF) return false;
    if (search && !JSON.stringify(l).toLowerCase().includes(search)) return false;
    return true;
  });

  const thead = document.getElementById("log-thead");
  const tbody = document.getElementById("log-tbody");
  const empty = document.getElementById("log-empty");

  if (filtered.length === 0) {
    thead.innerHTML = "";
    tbody.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";

  // Dynamic columns based on what's in the data
  const cols = getActiveCols(filtered);

  thead.innerHTML = `<tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr>`;
  tbody.innerHTML = filtered.map(l => {
    const idx = allLogs.indexOf(l);
    const cells = cols.map(c => {
      const val = l[c];
      if (c === "ts" && val) return `<td>${new Date(val).toLocaleTimeString()}</td>`;
      if (c === "level")     return `<td class="lvl-${val ?? ""}">${val ?? "—"}</td>`;
      if (c === "issue_type" && val && val !== "UNKNOWN") {
        const cfg = ISSUE_CONFIG[val] ?? ISSUE_CONFIG.UNKNOWN;
        return `<td><span class="issue-badge-sm ${cfg.cls}">${cfg.label}</span></td>`;
      }
      if (c === "latency_ms" && val != null) return `<td>${val} ms</td>`;
      if (c === "correlation_id") return `<td style="font-family:monospace;font-size:11px">${val ?? "—"}</td>`;
      return `<td>${val ?? "—"}</td>`;
    }).join("");
    return `<tr onclick="showLogDetail(${idx})">${cells}</tr>`;
  }).join("");
}

function showLogDetail(idx) {
  const panel = document.getElementById("log-detail");
  document.getElementById("log-detail-content").textContent =
    JSON.stringify(allLogs[idx], null, 2);
  panel.style.display = "block";
}

function closeLogDetail() {
  document.getElementById("log-detail").style.display = "none";
}

// ══════════════════════════════════════════
//  Incidents
// ══════════════════════════════════════════
async function loadIncidents() {
  try {
    const r = await fetch("/health");
    const d = await r.json();
    for (const [name, active] of Object.entries(d.incidents ?? {})) {
      const badge = document.getElementById(`badge-${name}`);
      const card  = document.getElementById(`inc-${name}`);
      if (badge) {
        badge.textContent = active ? "ON" : "OFF";
        badge.className   = `incident-badge ${active ? "on" : "off"}`;
      }
      if (card) card.classList.toggle("on", !!active);
    }
  } catch (err) {
    console.error("Incidents error:", err);
  }
}

async function toggleIncident(name, action) {
  try {
    await fetch(`/incidents/${name}/${action}`, { method: "POST" });
    await loadIncidents();
  } catch (err) {
    console.error(`Toggle ${name}/${action} failed:`, err);
  }
}
