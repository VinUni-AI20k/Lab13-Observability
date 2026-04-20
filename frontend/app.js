"use strict";

// ── Session ──
const sessionId = `s-${Math.random().toString(36).slice(2, 10)}`;
const userId    = `u-${Math.random().toString(36).slice(2, 10)}`;

// ── Charts registry ──
const charts = {};

// ── Init ──
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  setInterval(checkHealth, 15_000);
});

// ── Tab Switching ──
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

// ── Health ──
async function checkHealth() {
  const dot = document.getElementById("health-dot");
  const txt = document.getElementById("health-text");
  try {
    const r = await fetch("/health");
    const d = await r.json();
    dot.className = "status-dot ok";
    txt.textContent = d.tracing_enabled ? "Online · Tracing" : "Online";
  } catch {
    dot.className = "status-dot error";
    txt.textContent = "Offline";
  }
}

// ══════════════════════
//  CHAT
// ══════════════════════
function handleChatKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

async function sendMessage() {
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const msg     = input.value.trim();
  if (!msg) return;

  const feature = document.getElementById("chat-feature").value;

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
      body: JSON.stringify({
        user_id:    userId,
        session_id: sessionId,
        feature,
        message:    msg,
      }),
    });
    const d = await r.json();
    loader.remove();

    if (!r.ok) {
      appendMessage("assistant", `Error ${r.status}: ${d.detail ?? "Unknown error"}`, null);
    } else {
      appendMessage("assistant", d.answer, {
        latency_ms:    d.latency_ms,
        tokens_in:     d.tokens_in,
        tokens_out:    d.tokens_out,
        cost_usd:      d.cost_usd,
        quality_score: d.quality_score,
        correlation_id: d.correlation_id,
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
  bubble.textContent = content;
  el.appendChild(bubble);

  if (meta) {
    const parts = [
      meta.latency_ms     != null ? `⏱ ${meta.latency_ms} ms`                     : null,
      meta.tokens_in      != null ? `↑${meta.tokens_in} ↓${meta.tokens_out} tok`  : null,
      meta.cost_usd       != null ? `$${meta.cost_usd.toFixed(5)}`                 : null,
      meta.quality_score  != null ? `Q ${meta.quality_score.toFixed(2)}`           : null,
      meta.correlation_id           ? `#${meta.correlation_id}`                    : null,
    ].filter(Boolean);

    const metaEl     = document.createElement("div");
    metaEl.className = "message-meta";
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
    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
  </div>`;
  wrap.appendChild(el);
  wrap.scrollTop = wrap.scrollHeight;
  return el;
}

function clearChat() {
  document.getElementById("chat-messages").innerHTML =
    `<div class="chat-welcome"><p>Ask the lab agent anything — try <em>"What is your refund policy?"</em></p></div>`;
}

// ══════════════════════
//  DASHBOARD
// ══════════════════════
async function refreshDashboard() {
  try {
    const r = await fetch("/metrics");
    const d = await r.json();
    updateCards(d);
    buildLatencyChart(d);
    buildTokenChart(d);
    buildErrorChart(d);
    buildSLO(d);
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

function updateCards(d) {
  document.getElementById("m-traffic").textContent = d.traffic ?? 0;
  document.getElementById("m-p95").textContent     = d.latency_p95  != null ? d.latency_p95.toFixed(0)  : "—";
  document.getElementById("m-quality").textContent = d.quality_avg  != null ? d.quality_avg.toFixed(2)  : "—";
  document.getElementById("m-cost").textContent    = d.total_cost_usd != null ? `$${d.total_cost_usd.toFixed(4)}` : "$0.0000";
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
        borderWidth: 1,
        borderRadius: 4,
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

function buildErrorChart(d) {
  destroyChart("errors");
  const ctx    = document.getElementById("chart-errors").getContext("2d");
  const errors = d.error_breakdown ?? {};
  let labels   = Object.keys(errors);
  let values   = Object.values(errors);
  const noErrors = labels.length === 0;
  if (noErrors) { labels = ["No Errors"]; values = [1]; }

  charts.errors = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: noErrors
          ? ["rgba(63,185,80,.35)"]
          : ["rgba(248,81,73,.65)", "rgba(210,153,34,.65)", "rgba(88,166,255,.65)"],
        borderColor: noErrors
          ? ["#3fb950"]
          : ["#f85149", "#d29922", "#58a6ff"],
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom", labels: { color: "#8b949e", font: { size: 11 } } } },
    },
  });
}

function buildSLO(d) {
  const slos = [
    {
      name: "P95 Latency",
      value: d.latency_p95 ?? 0,
      threshold: 3000,
      fmt: v => `${v.toFixed(0)} ms`,
      ok: v => v <= 3000,
    },
    {
      name: "Quality Avg",
      value: d.quality_avg ?? 0,
      threshold: 0.75,
      fmt: v => v.toFixed(2),
      ok: v => v >= 0.75,
    },
    {
      name: "Avg Cost / req",
      value: d.avg_cost_usd ?? 0,
      threshold: 0.005,
      fmt: v => `$${v.toFixed(5)}`,
      ok: v => v <= 0.005,
    },
    {
      name: "Total Cost",
      value: d.total_cost_usd ?? 0,
      threshold: 2.5,
      fmt: v => `$${v.toFixed(4)}`,
      ok: v => v <= 2.5,
    },
  ];

  document.getElementById("slo-list").innerHTML = slos.map(s => {
    const pass = s.ok(s.value);
    const cls  = pass ? "slo-ok" : "slo-bad";
    return `<div class="slo-item">
      <span class="slo-name">${s.name}</span>
      <span class="slo-value ${cls}">${s.fmt(s.value)} ${pass ? "✓" : "✗"}</span>
    </div>`;
  }).join("");
}

// ══════════════════════
//  LOGS
// ══════════════════════
let allLogs = [];

async function refreshLogs() {
  try {
    const r = await fetch("/logs?n=200");
    allLogs  = await r.json();
    filterLogs();
  } catch (err) {
    console.error("Logs error:", err);
  }
}

function filterLogs() {
  const search = document.getElementById("log-search").value.toLowerCase();
  const level  = document.getElementById("log-level-filter").value;

  const filtered = allLogs.filter(l => {
    if (level && l.level !== level) return false;
    if (search && !JSON.stringify(l).toLowerCase().includes(search)) return false;
    return true;
  });

  const tbody = document.getElementById("log-tbody");
  const empty = document.getElementById("log-empty");

  if (filtered.length === 0) {
    tbody.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";

  tbody.innerHTML = filtered.map(l => {
    const ts  = l.ts ? new Date(l.ts).toLocaleTimeString() : "—";
    const idx = allLogs.indexOf(l);
    const lvlClass = `lvl-${l.level ?? ""}`;
    return `<tr onclick="showLogDetail(${idx})">
      <td>${ts}</td>
      <td class="${lvlClass}">${l.level ?? "—"}</td>
      <td>${l.service ?? "—"}</td>
      <td>${l.event ?? "—"}</td>
      <td style="font-family:monospace;font-size:11px">${l.correlation_id ?? "—"}</td>
      <td>${l.latency_ms != null ? l.latency_ms + " ms" : "—"}</td>
    </tr>`;
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

// ══════════════════════
//  INCIDENTS
// ══════════════════════
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
