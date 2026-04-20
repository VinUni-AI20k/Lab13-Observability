from __future__ import annotations

from fastapi.responses import HTMLResponse


def dashboard_response() -> HTMLResponse:
    return HTMLResponse(_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Observability Dashboard</title>
    <style>
      :root {
        --bg: #f4efe4;
        --surface: rgba(255, 252, 245, 0.86);
        --surface-strong: #fffdf7;
        --ink: #1d1b19;
        --muted: #675f57;
        --line: rgba(36, 30, 26, 0.12);
        --accent: #0e7490;
        --accent-2: #b45309;
        --accent-3: #7c3aed;
        --danger: #b42318;
        --ok: #15803d;
        --shadow: 0 24px 60px rgba(62, 47, 33, 0.12);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(14, 116, 144, 0.12), transparent 30%),
          radial-gradient(circle at top right, rgba(180, 83, 9, 0.16), transparent 28%),
          linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
      }

      .shell {
        max-width: 1400px;
        margin: 0 auto;
        padding: 28px;
      }

      .hero {
        display: grid;
        grid-template-columns: 1.5fr 1fr;
        gap: 18px;
        margin-bottom: 20px;
      }

      .hero-card,
      .panel {
        border: 1px solid var(--line);
        background: var(--surface);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        box-shadow: var(--shadow);
      }

      .hero-card {
        padding: 24px;
      }

      .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 10px;
      }

      h1 {
        font-size: clamp(32px, 4vw, 54px);
        margin: 0 0 12px;
        line-height: 1;
      }

      .hero-copy {
        margin: 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.6;
      }

      .hero-stats {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .stat {
        padding: 16px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(36, 30, 26, 0.08);
      }

      .stat-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
      }

      .stat-value {
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
      }

      .panels {
        display: grid;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: 18px;
      }

      .panel {
        padding: 20px;
        min-height: 280px;
      }

      .panel.wide {
        grid-column: span 6;
      }

      .panel.half {
        grid-column: span 4;
      }

      .panel-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: baseline;
        margin-bottom: 12px;
      }

      .panel h2 {
        font-size: 19px;
        margin: 0;
      }

      .subtle {
        color: var(--muted);
        font-size: 13px;
      }

      .metric-strip {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 12px;
      }

      .pill {
        background: rgba(14, 116, 144, 0.08);
        color: var(--accent);
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 600;
      }

      .chart {
        width: 100%;
        height: 164px;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(255,255,255,0.7), rgba(250,246,237,0.95));
        border: 1px solid rgba(36, 30, 26, 0.07);
      }

      .table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 14px;
      }

      .table th,
      .table td {
        padding: 10px 0;
        border-bottom: 1px solid rgba(36, 30, 26, 0.08);
        text-align: left;
      }

      .table th:last-child,
      .table td:last-child {
        text-align: right;
      }

      .ok {
        color: var(--ok);
      }

      .warn {
        color: var(--accent-2);
      }

      .danger {
        color: var(--danger);
      }

      .stack {
        display: grid;
        gap: 12px;
      }

      .legend {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        font-size: 12px;
        color: var(--muted);
        margin-top: 10px;
      }

      .legend span::before {
        content: "";
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 999px;
        margin-right: 6px;
      }

      .legend .lat50::before {
        background: var(--accent);
      }

      .legend .lat95::before {
        background: var(--accent-2);
      }

      .legend .lat99::before {
        background: var(--accent-3);
      }

      .legend .token-in::before {
        background: var(--accent);
      }

      .legend .token-out::before {
        background: var(--accent-2);
      }

      .foot {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 18px;
        color: var(--muted);
        font-size: 13px;
      }

      @media (max-width: 1080px) {
        .hero,
        .hero-stats {
          grid-template-columns: 1fr;
        }

        .panel.wide,
        .panel.half {
          grid-column: span 12;
        }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <article class="hero-card">
          <div class="eyebrow">Layer 2 Dashboard</div>
          <h1>Observability Control Deck</h1>
          <p class="hero-copy">
            Default range: last 1 hour. Auto-refresh: every 15 seconds. Use this
            page while running <code>scripts/load_test.py</code> so the six required
            panels populate with live metrics and become screenshot-ready.
          </p>
        </article>
        <article class="hero-card hero-stats">
          <div class="stat">
            <div class="stat-label">Traffic</div>
            <div class="stat-value" id="hero-traffic">0 req</div>
          </div>
          <div class="stat">
            <div class="stat-label">Error Rate</div>
            <div class="stat-value" id="hero-error-rate">0.00%</div>
          </div>
          <div class="stat">
            <div class="stat-label">P95 Latency</div>
            <div class="stat-value" id="hero-p95">0 ms</div>
          </div>
          <div class="stat">
            <div class="stat-label">Total Cost</div>
            <div class="stat-value" id="hero-cost">$0.0000</div>
          </div>
        </article>
      </section>

      <section class="panels">
        <article class="panel wide">
          <div class="panel-head">
            <h2>Latency P50 / P95 / P99</h2>
            <div class="subtle">SLO line at 3000 ms</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="latency-p50-label">P50: 0 ms</span>
            <span class="pill" id="latency-p95-label">P95: 0 ms</span>
            <span class="pill" id="latency-p99-label">P99: 0 ms</span>
          </div>
          <svg class="chart" id="latency-chart" viewBox="0 0 600 164" preserveAspectRatio="none"></svg>
          <div class="legend">
            <span class="lat50">P50</span>
            <span class="lat95">P95</span>
            <span class="lat99">P99</span>
          </div>
        </article>

        <article class="panel half">
          <div class="panel-head">
            <h2>Traffic</h2>
            <div class="subtle">Request count over time</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="traffic-label">Current: 0 req</span>
          </div>
          <svg class="chart" id="traffic-chart" viewBox="0 0 400 164" preserveAspectRatio="none"></svg>
        </article>

        <article class="panel half">
          <div class="panel-head">
            <h2>Error Rate With Breakdown</h2>
            <div class="subtle">SLO line at 2%</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="error-rate-label">Error rate: 0.00%</span>
          </div>
          <div class="stack">
            <svg class="chart" id="error-chart" viewBox="0 0 400 120" preserveAspectRatio="none"></svg>
            <table class="table" id="error-table">
              <thead>
                <tr><th>Error Type</th><th>Count</th></tr>
              </thead>
              <tbody><tr><td>No errors</td><td>0</td></tr></tbody>
            </table>
          </div>
        </article>

        <article class="panel half">
          <div class="panel-head">
            <h2>Cost Over Time</h2>
            <div class="subtle">Daily budget reference: $2.50</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="cost-label">Total: $0.0000</span>
            <span class="pill" id="avg-cost-label">Avg: $0.0000</span>
          </div>
          <svg class="chart" id="cost-chart" viewBox="0 0 400 164" preserveAspectRatio="none"></svg>
        </article>

        <article class="panel half">
          <div class="panel-head">
            <h2>Tokens In / Out</h2>
            <div class="subtle">Token volume accumulation</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="tokens-in-label">In: 0</span>
            <span class="pill" id="tokens-out-label">Out: 0</span>
          </div>
          <svg class="chart" id="tokens-chart" viewBox="0 0 400 164" preserveAspectRatio="none"></svg>
          <div class="legend">
            <span class="token-in">Tokens in</span>
            <span class="token-out">Tokens out</span>
          </div>
        </article>

        <article class="panel half">
          <div class="panel-head">
            <h2>Quality Proxy</h2>
            <div class="subtle">Target floor: 0.75</div>
          </div>
          <div class="metric-strip">
            <span class="pill" id="quality-label">Average quality: 0.00</span>
          </div>
          <svg class="chart" id="quality-chart" viewBox="0 0 400 164" preserveAspectRatio="none"></svg>
        </article>
      </section>

      <footer class="foot">
        <span id="last-updated">Waiting for first metrics refresh...</span>
        <span>Refresh the page only after you have captured the screenshot you want.</span>
      </footer>
    </main>

    <script>
      const state = {
        labels: [],
        latencyP50: [],
        latencyP95: [],
        latencyP99: [],
        traffic: [],
        errorRate: [],
        totalCost: [],
        avgCost: [],
        tokensIn: [],
        tokensOut: [],
        quality: []
      };

      const MAX_POINTS = 24;
      const REFRESH_MS = 15000;
      const LATENCY_SLO = 3000;
      const ERROR_SLO = 2;
      const COST_BUDGET = 2.5;
      const QUALITY_TARGET = 0.75;

      function pushPoint(key, value) {
        state[key].push(value);
        if (state[key].length > MAX_POINTS) {
          state[key].shift();
        }
      }

      function pushLabel(label) {
        state.labels.push(label);
        if (state.labels.length > MAX_POINTS) {
          state.labels.shift();
        }
      }

      function currency(value) {
        return `$${Number(value || 0).toFixed(4)}`;
      }

      function fixed(value, digits = 2) {
        return Number(value || 0).toFixed(digits);
      }

      function linePath(values, width, height, maxValue) {
        if (!values.length) {
          return "";
        }
        const usableMax = maxValue > 0 ? maxValue : 1;
        return values.map((value, index) => {
          const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width;
          const y = height - (Math.max(0, value) / usableMax) * (height - 16) - 8;
          return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
        }).join(" ");
      }

      function thresholdY(threshold, height, maxValue) {
        const usableMax = maxValue > 0 ? maxValue : 1;
        return height - (Math.max(0, threshold) / usableMax) * (height - 16) - 8;
      }

      function renderLineChart(targetId, series, options) {
        const svg = document.getElementById(targetId);
        const width = Number(svg.getAttribute("viewBox").split(" ")[2]);
        const height = Number(svg.getAttribute("viewBox").split(" ")[3]);
        const allValues = options.series.flatMap(item => item.values);
        const referenceValues = options.thresholds ? options.thresholds.map(item => item.value) : [];
        const maxValue = Math.max(1, ...allValues, ...referenceValues);
        const grid = [0.25, 0.5, 0.75].map(step => {
          const y = (height - 16) * step + 8;
          return `<line x1="0" y1="${y}" x2="${width}" y2="${y}" stroke="rgba(36, 30, 26, 0.08)" stroke-dasharray="4 4" />`;
        }).join("");
        const thresholds = (options.thresholds || []).map(item => {
          const y = thresholdY(item.value, height, maxValue);
          return `<line x1="0" y1="${y}" x2="${width}" y2="${y}" stroke="${item.color}" stroke-width="2" stroke-dasharray="7 7" />`;
        }).join("");
        const lines = options.series.map(item => {
          const d = linePath(item.values, width, height, maxValue);
          return d
            ? `<path d="${d}" fill="none" stroke="${item.color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />`
            : "";
        }).join("");
        svg.innerHTML = `<rect x="0" y="0" width="${width}" height="${height}" fill="transparent" rx="18" />${grid}${thresholds}${lines}`;
      }

      function renderBarChart(targetId, entries, threshold) {
        const svg = document.getElementById(targetId);
        const width = Number(svg.getAttribute("viewBox").split(" ")[2]);
        const height = Number(svg.getAttribute("viewBox").split(" ")[3]);
        const values = entries.map(([, value]) => value);
        const maxValue = Math.max(1, threshold || 0, ...values);
        const barWidth = width / Math.max(entries.length, 1);
        const bars = entries.map(([label, value], index) => {
          const x = index * barWidth + 18;
          const usableWidth = Math.max(24, barWidth - 36);
          const barHeight = ((Math.max(0, value) / maxValue) * (height - 42));
          const y = height - barHeight - 22;
          const fill = value > 0 ? "rgba(180, 35, 24, 0.8)" : "rgba(21, 128, 61, 0.65)";
          return `
            <rect x="${x}" y="${y}" width="${usableWidth}" height="${barHeight}" rx="10" fill="${fill}" />
            <text x="${x + usableWidth / 2}" y="${height - 8}" text-anchor="middle" font-size="11" fill="#675f57">${label}</text>
          `;
        }).join("");
        const thresholdLine = threshold != null
          ? `<line x1="0" y1="${thresholdY(threshold, height, maxValue)}" x2="${width}" y2="${thresholdY(threshold, height, maxValue)}" stroke="#b45309" stroke-width="2" stroke-dasharray="7 7" />`
          : "";
        svg.innerHTML = `${thresholdLine}${bars}`;
      }

      function renderErrorTable(errorBreakdown) {
        const tbody = document.querySelector("#error-table tbody");
        const entries = Object.entries(errorBreakdown || {});
        if (!entries.length) {
          tbody.innerHTML = "<tr><td>No errors</td><td>0</td></tr>";
          return;
        }
        tbody.innerHTML = entries.map(([label, value]) => `<tr><td>${label}</td><td>${value}</td></tr>`).join("");
      }

      function updateSummary(metrics) {
        const totalErrors = Object.values(metrics.error_breakdown || {}).reduce((sum, value) => sum + value, 0);
        const totalRequests = (metrics.traffic || 0) + totalErrors;
        const errorRate = totalRequests ? (totalErrors / totalRequests) * 100 : 0;

        document.getElementById("hero-traffic").textContent = `${metrics.traffic || 0} req`;
        document.getElementById("hero-error-rate").textContent = `${fixed(errorRate)}%`;
        document.getElementById("hero-p95").textContent = `${fixed(metrics.latency_p95, 0)} ms`;
        document.getElementById("hero-cost").textContent = currency(metrics.total_cost_usd);

        document.getElementById("latency-p50-label").textContent = `P50: ${fixed(metrics.latency_p50, 0)} ms`;
        document.getElementById("latency-p95-label").textContent = `P95: ${fixed(metrics.latency_p95, 0)} ms`;
        document.getElementById("latency-p99-label").textContent = `P99: ${fixed(metrics.latency_p99, 0)} ms`;
        document.getElementById("traffic-label").textContent = `Current: ${metrics.traffic || 0} req`;
        document.getElementById("error-rate-label").textContent = `Error rate: ${fixed(errorRate)}%`;
        document.getElementById("cost-label").textContent = `Total: ${currency(metrics.total_cost_usd)}`;
        document.getElementById("avg-cost-label").textContent = `Avg: ${currency(metrics.avg_cost_usd)}`;
        document.getElementById("tokens-in-label").textContent = `In: ${metrics.tokens_in_total || 0}`;
        document.getElementById("tokens-out-label").textContent = `Out: ${metrics.tokens_out_total || 0}`;
        document.getElementById("quality-label").textContent = `Average quality: ${fixed(metrics.quality_avg)}`;

        pushLabel(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
        pushPoint("latencyP50", Number(metrics.latency_p50 || 0));
        pushPoint("latencyP95", Number(metrics.latency_p95 || 0));
        pushPoint("latencyP99", Number(metrics.latency_p99 || 0));
        pushPoint("traffic", Number(metrics.traffic || 0));
        pushPoint("errorRate", Number(errorRate));
        pushPoint("totalCost", Number(metrics.total_cost_usd || 0));
        pushPoint("avgCost", Number(metrics.avg_cost_usd || 0));
        pushPoint("tokensIn", Number(metrics.tokens_in_total || 0));
        pushPoint("tokensOut", Number(metrics.tokens_out_total || 0));
        pushPoint("quality", Number(metrics.quality_avg || 0));

        renderLineChart("latency-chart", state.latencyP50, {
          series: [
            { values: state.latencyP50, color: "#0e7490" },
            { values: state.latencyP95, color: "#b45309" },
            { values: state.latencyP99, color: "#7c3aed" }
          ],
          thresholds: [{ value: LATENCY_SLO, color: "#b42318" }]
        });
        renderLineChart("traffic-chart", state.traffic, {
          series: [{ values: state.traffic, color: "#0e7490" }]
        });
        renderLineChart("cost-chart", state.totalCost, {
          series: [
            { values: state.totalCost, color: "#b45309" },
            { values: state.avgCost, color: "#0e7490" }
          ],
          thresholds: [{ value: COST_BUDGET, color: "#7c3aed" }]
        });
        renderLineChart("tokens-chart", state.tokensIn, {
          series: [
            { values: state.tokensIn, color: "#0e7490" },
            { values: state.tokensOut, color: "#b45309" }
          ]
        });
        renderLineChart("quality-chart", state.quality, {
          series: [{ values: state.quality, color: "#15803d" }],
          thresholds: [{ value: QUALITY_TARGET, color: "#7c3aed" }]
        });

        const errorEntries = Object.entries(metrics.error_breakdown || {});
        const barEntries = errorEntries.length ? errorEntries : [["No errors", 0]];
        renderBarChart("error-chart", barEntries, ERROR_SLO);
        renderErrorTable(metrics.error_breakdown || {});

        const ts = new Date().toLocaleString();
        document.getElementById("last-updated").textContent = `Last updated: ${ts}`;
      }

      async function refreshMetrics() {
        try {
          const response = await fetch("/metrics", { cache: "no-store" });
          const metrics = await response.json();
          updateSummary(metrics);
        } catch (error) {
          document.getElementById("last-updated").textContent = `Dashboard refresh failed: ${error}`;
        }
      }

      refreshMetrics();
      setInterval(refreshMetrics, REFRESH_MS);
    </script>
  </body>
</html>
"""
