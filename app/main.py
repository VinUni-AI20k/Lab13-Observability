from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars

load_dotenv()

from .agent import LabAgent
from .incidents import disable, enable, status
from .logging_config import LOG_PATH, configure_logging, get_logger
from .metrics import history, record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()
SLO_TARGETS = {
    "latency_p95_ms": 3000,
    "error_rate_pct": 2.0,
    "daily_cost_usd": 2.5,
    "quality_score_avg": 0.75,
}


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _load_log_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records.sort(key=lambda item: item.get("ts", ""))
    return records


def _percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def _dashboard_payload(window_seconds: int = 3600, raw_limit: int = 25) -> dict:
    now = datetime.now(timezone.utc)
    cutoff = None if window_seconds <= 0 else now - timedelta(seconds=window_seconds)
    records = []
    for record in _load_log_records():
        ts = _parse_ts(record.get("ts"))
        if cutoff and ts and ts < cutoff:
            continue
        records.append(record)

    response_events = [
        rec
        for rec in records
        if rec.get("service") == "api" and rec.get("event") == "response_sent"
    ]
    error_events = [rec for rec in records if rec.get("event") == "request_failed"]

    latencies = [int(rec.get("latency_ms", 0)) for rec in response_events if rec.get("latency_ms") is not None]
    costs = [float(rec.get("cost_usd", 0.0)) for rec in response_events if rec.get("cost_usd") is not None]
    tokens_in = [int(rec.get("tokens_in", 0)) for rec in response_events if rec.get("tokens_in") is not None]
    tokens_out = [int(rec.get("tokens_out", 0)) for rec in response_events if rec.get("tokens_out") is not None]
    quality_scores = [
        float(rec.get("quality_score", 0.0))
        for rec in response_events
        if rec.get("quality_score") is not None
    ]
    error_breakdown = Counter(
        str(rec.get("error_type", "unknown"))
        for rec in error_events
    )

    traffic = len(response_events)
    error_total = len(error_events)
    total_events = traffic + error_total
    error_rate_pct = round((error_total / total_events) * 100, 2) if total_events else 0.0

    cumulative_latencies: list[int] = []
    cumulative_cost = 0.0
    cumulative_tokens_in = 0
    cumulative_tokens_out = 0
    cumulative_quality: list[float] = []
    cumulative_responses = 0
    cumulative_errors = 0
    history_points: list[dict[str, float | int | str]] = []

    for rec in records:
        event = rec.get("event")
        if event == "response_sent" and rec.get("service") == "api":
            cumulative_responses += 1
            latency = int(rec.get("latency_ms", 0))
            cumulative_latencies.append(latency)
            cumulative_cost += float(rec.get("cost_usd", 0.0))
            cumulative_tokens_in += int(rec.get("tokens_in", 0))
            cumulative_tokens_out += int(rec.get("tokens_out", 0))
            quality_value = rec.get("quality_score")
            if quality_value is not None:
                cumulative_quality.append(float(quality_value))
        elif event == "request_failed":
            cumulative_errors += 1

        if event not in {"response_sent", "request_failed"}:
            continue

        total_so_far = cumulative_responses + cumulative_errors
        history_points.append(
            {
                "ts": rec.get("ts", ""),
                "traffic": cumulative_responses,
                "latency_p95": _percentile(cumulative_latencies, 95),
                "error_rate_pct": round((cumulative_errors / total_so_far) * 100, 2) if total_so_far else 0.0,
                "total_cost_usd": round(cumulative_cost, 4),
                "tokens_in_total": cumulative_tokens_in,
                "tokens_out_total": cumulative_tokens_out,
                "quality_avg": round(sum(cumulative_quality) / len(cumulative_quality), 4) if cumulative_quality else 0.0,
            }
        )

    raw_logs = records[-max(1, min(raw_limit, 200)):]

    snapshot_from_logs = {
        "traffic": traffic,
        "latency_p50": _percentile(latencies, 50),
        "latency_p95": _percentile(latencies, 95),
        "latency_p99": _percentile(latencies, 99),
        "error_rate_pct": error_rate_pct,
        "avg_cost_usd": round(sum(costs) / len(costs), 4) if costs else 0.0,
        "total_cost_usd": round(sum(costs), 4),
        "tokens_in_total": sum(tokens_in),
        "tokens_out_total": sum(tokens_out),
        "error_breakdown": dict(error_breakdown),
        "quality_avg": round(sum(quality_scores) / len(quality_scores), 4) if quality_scores else 0.0,
        "records_in_window": len(records),
        "window_seconds": window_seconds,
        "last_event_ts": records[-1].get("ts") if records else None,
    }

    return {
        "snapshot": snapshot_from_logs,
        "history": history_points[-60:],
        "slo_targets": SLO_TARGETS,
        "raw_logs": raw_logs,
        "window_seconds": window_seconds,
        "generated_at": now.isoformat(),
        "incidents": status(),
        "live_metrics": {"snapshot": snapshot(), "history": history()},
    }


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/dashboard-data")
async def dashboard_data(window_seconds: int = 3600, raw_limit: int = 25) -> dict:
    return _dashboard_payload(window_seconds=window_seconds, raw_limit=raw_limit)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    return HTMLResponse(
        """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Observability Dashboard</title>
  <style>
    :root {
      --bg-light: #f8f9fa;
      --bg-surface: #ffffff;
      --bg-secondary: #f0f2f5;
      --text-primary: #1a1a2e;
      --text-secondary: #6b7280;
      --text-muted: #9ca3af;
      --border-color: #e5e7eb;
      --accent-blue: #3b82f6;
      --accent-teal: #14b8a6;
      --accent-red: #ef4444;
      --accent-amber: #f59e0b;
      --accent-green: #10b981;
      --status-ok: #22c55e;
      --status-warn: #f97316;
      --status-error: #dc2626;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--text-primary);
      background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
      min-height: 100vh;
      padding: 0;
      margin: 0;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 32px 20px;
    }

    .header {
      margin-bottom: 40px;
      padding-bottom: 32px;
      border-bottom: 2px solid var(--border-color);
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      flex-wrap: wrap;
    }

    .header-title {
      flex: 1;
    }

    h1 {
      font-size: 32px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }

    .header-subtitle {
      color: var(--text-secondary);
      font-size: 15px;
      line-height: 1.6;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: rgba(34, 197, 94, 0.1);
      color: var(--status-ok);
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
    }

    .status-badge.warning {
      background: rgba(249, 115, 22, 0.1);
      color: var(--status-warn);
    }

    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      justify-content: flex-end;
    }

    .control {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 140px;
    }

    .control label {
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    .control select,
    .control button {
      appearance: none;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
      color: var(--text-primary);
    }

    .control button {
      background: var(--accent-blue);
      color: white;
      font-weight: 600;
      cursor: pointer;
    }

    .control button:hover {
      filter: brightness(0.96);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }

    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
    }

    .card:hover {
      border-color: var(--accent-blue);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--bg-secondary);
    }

    .card-label {
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      flex: 1;
    }

    .card-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--bg-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      margin-left: 8px;
    }

    .value-primary {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
      letter-spacing: -0.5px;
    }

    .value-secondary {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 16px;
    }

    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
      padding: 12px 0;
    }

    .metric-item {
      background: var(--bg-secondary);
      border-radius: 8px;
      padding: 12px;
      text-align: center;
    }

    .metric-label {
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 6px;
      text-transform: uppercase;
      font-weight: 500;
      letter-spacing: 0.3px;
    }

    .metric-value {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .metric-value.ok {
      color: var(--status-ok);
    }

    .metric-value.warn {
      color: var(--status-warn);
    }

    .metric-value.error {
      color: var(--status-error);
    }

    .spark-container {
      position: relative;
      margin: 18px 0;
      padding: 16px;
      background: var(--bg-secondary);
      border-radius: 8px;
      overflow: hidden;
    }

    .spark-label {
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 8px;
      text-transform: uppercase;
      font-weight: 500;
      letter-spacing: 0.3px;
    }

    .spark {
      width: 100%;
      height: 80px;
      display: block;
      border-radius: 6px;
    }

    .legend {
      margin-top: 12px;
      font-size: 13px;
      color: var(--text-secondary);
      padding-top: 12px;
      border-top: 1px solid var(--border-color);
      line-height: 1.6;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
    }

    .legend-color {
      width: 12px;
      height: 12px;
      border-radius: 3px;
      flex-shrink: 0;
    }

    .legend-color.line {
      width: 16px;
      height: 2px;
    }

    pre {
      margin: 12px 0 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 12px;
      color: var(--text-primary);
      background: var(--bg-secondary);
      border-radius: 8px;
      padding: 12px;
      border-left: 3px solid var(--accent-blue);
      line-height: 1.5;
      max-height: 200px;
      overflow-y: auto;
    }

    .no-data {
      padding: 16px;
      text-align: center;
      color: var(--text-secondary);
      font-size: 14px;
    }

    .section-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 24px;
      margin-top: 32px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--border-color);
      letter-spacing: -0.3px;
    }

    .full-width {
      grid-column: 1 / -1;
    }

    .stack {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 24px;
      margin-top: 24px;
    }

    .toolbar-meta {
      margin-top: 12px;
      color: var(--text-secondary);
      font-size: 13px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--bg-secondary);
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 600;
    }

    .incident-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }

    .incident-pill {
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(239, 68, 68, 0.1);
      color: var(--status-error);
      font-size: 12px;
      font-weight: 600;
    }

    .incident-pill.off {
      background: rgba(107, 114, 128, 0.12);
      color: var(--text-secondary);
    }

    .raw-table-wrap {
      margin-top: 16px;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: auto;
      background: linear-gradient(180deg, rgba(59,130,246,0.03), rgba(59,130,246,0.01));
      max-height: 420px;
    }

    .raw-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      min-width: 980px;
    }

    .raw-table thead th {
      position: sticky;
      top: 0;
      background: #eef4ff;
      color: var(--text-primary);
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--border-color);
      text-transform: uppercase;
      letter-spacing: 0.3px;
      font-size: 11px;
      z-index: 1;
    }

    .raw-table tbody td {
      padding: 10px;
      border-bottom: 1px solid rgba(229, 231, 235, 0.9);
      vertical-align: top;
      color: var(--text-primary);
      background: rgba(255,255,255,0.85);
    }

    .raw-table tbody tr:nth-child(even) td {
      background: rgba(248, 250, 252, 0.92);
    }

    .raw-table tbody tr:hover td {
      background: rgba(219, 234, 254, 0.6);
    }

    .raw-pill {
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      line-height: 1;
      white-space: nowrap;
    }

    .raw-pill.event-response_sent {
      background: rgba(16, 185, 129, 0.14);
      color: #047857;
    }

    .raw-pill.event-request_received {
      background: rgba(59, 130, 246, 0.14);
      color: #1d4ed8;
    }

    .raw-pill.event-request_failed {
      background: rgba(239, 68, 68, 0.14);
      color: #b91c1c;
    }

    .raw-pill.event-app_started {
      background: rgba(168, 85, 247, 0.14);
      color: #7e22ce;
    }

    .truncate-cell {
      max-width: 280px;
      white-space: normal;
      line-height: 1.45;
      color: var(--text-secondary);
    }

    .muted-cell {
      color: var(--text-secondary);
    }

    .context-card {
      background:
        linear-gradient(140deg, rgba(59,130,246,0.10), rgba(20,184,166,0.12)),
        var(--bg-surface);
      border: 1px solid rgba(59,130,246,0.18);
      box-shadow: 0 10px 24px rgba(20, 184, 166, 0.08);
    }

    .context-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }

    .context-stat {
      border-radius: 12px;
      padding: 14px;
      color: white;
      min-height: 86px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.18);
    }

    .context-stat.blue {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }

    .context-stat.teal {
      background: linear-gradient(135deg, #0f766e, #14b8a6);
    }

    .context-stat.amber {
      background: linear-gradient(135deg, #d97706, #f59e0b);
    }

    .context-stat.slate {
      background: linear-gradient(135deg, #475569, #334155);
    }

    .context-stat-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.35px;
      opacity: 0.9;
    }

    .context-stat-value {
      font-size: 20px;
      font-weight: 700;
      line-height: 1.1;
    }

    .context-stat-sub {
      font-size: 12px;
      opacity: 0.9;
    }

    @media (max-width: 768px) {
      .grid {
        grid-template-columns: 1fr;
      }

      .header-content {
        flex-direction: column;
      }

      h1 {
        font-size: 24px;
      }

      .metrics-row {
        grid-template-columns: repeat(2, 1fr);
      }

      .stack {
        grid-template-columns: 1fr;
      }

      .context-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <section class="header">
      <div class="header-content">
        <div class="header-title">
          <h1>&#128202; Observability Dashboard</h1>
          <div class="header-subtitle">
            <span class="status-dot"></span>
            Log-driven observability view for metrics, incidents, and raw JSONL evidence
          </div>
          <div class="toolbar-meta">
            <span class="pill" id="windowMeta">Window: 1 hour</span>
            <span class="pill" id="refreshMeta">Auto-refresh: 15s</span>
            <span class="pill" id="generatedMeta">Last refresh: --</span>
          </div>
        </div>
        <div class="controls">
          <div class="control">
            <label for="windowSelect">Time Window</label>
            <select id="windowSelect">
              <option value="300">Last 5 minutes</option>
              <option value="900">Last 15 minutes</option>
              <option value="3600" selected>Last 1 hour</option>
              <option value="21600">Last 6 hours</option>
              <option value="0">All data</option>
            </select>
          </div>
          <div class="control">
            <label for="refreshSelect">Auto Refresh</label>
            <select id="refreshSelect">
              <option value="0">Off</option>
              <option value="5000">5 seconds</option>
              <option value="15000" selected>15 seconds</option>
              <option value="30000">30 seconds</option>
              <option value="60000">60 seconds</option>
            </select>
          </div>
          <div class="control">
            <label for="rawLimitSelect">Raw Log Lines</label>
            <select id="rawLimitSelect">
              <option value="10">10</option>
              <option value="25" selected>25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
          <div class="control">
            <label for="refreshButton">Manual Refresh</label>
            <button id="refreshButton" type="button">Refresh now</button>
          </div>
          <div class="status-badge" id="statusBadge">
            <span class="status-dot"></span>
            System Healthy
          </div>
        </div>
      </div>
    </section>

    <div class="section-title">Key Metrics</div>

    <div class="grid">
      <article class="card">
        <div class="card-header">
          <span class="card-label">Latency Performance</span>
          <div class="card-icon">&#9889;</div>
        </div>
        <div class="value-primary" id="latencyValue">-- ms</div>
        <div class="value-secondary">P95 Latency</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">P50</div>
            <div class="metric-value" id="latencyP50">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">P99</div>
            <div class="metric-value" id="latencyP99">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">SLO</div>
            <div class="metric-value" id="latencySLO">--</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Trend (95th percentile)</div>
          <svg class="spark" id="latencyChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="legend">
          <div class="legend-item">
            <div class="legend-color" style="background: #3b82f6;"></div>
            <span>Response time in milliseconds</span>
          </div>
          <div class="legend-item">
            <div class="legend-color line" style="background: #f59e0b;"></div>
            <span>Target SLO threshold</span>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="card-header">
          <span class="card-label">Traffic Volume</span>
          <div class="card-icon">&#128200;</div>
        </div>
        <div class="value-primary" id="trafficValue">--</div>
        <div class="value-secondary">Total Requests</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">Status</div>
            <div class="metric-value ok">Active</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Range</div>
            <div class="metric-value">Latest</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Request count over time</div>
          <svg class="spark" id="trafficChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="legend">
          <span>Measures total requests processed in the current session</span>
        </div>
      </article>

      <article class="card">
        <div class="card-header">
          <span class="card-label">Error Rate Analysis</span>
          <div class="card-icon">&#9888;&#65039;</div>
        </div>
        <div class="value-primary" id="errorValue">--%</div>
        <div class="value-secondary">Current Error Rate</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">SLO Target</div>
            <div class="metric-value" id="errorSLO">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Total Errors</div>
            <div class="metric-value" id="errorCount">0</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Error rate trend</div>
          <svg class="spark" id="errorChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="section-title" style="font-size: 14px; margin: 16px 0 8px; border: none; padding: 0;">Error Breakdown</div>
        <pre id="errorBreakdown">No errors recorded.</pre>
      </article>

      <article class="card">
        <div class="card-header">
          <span class="card-label">Cost Management</span>
          <div class="card-icon">&#128176;</div>
        </div>
        <div class="value-primary" id="costValue">$--</div>
        <div class="value-secondary">Total Cost</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">Avg/Request</div>
            <div class="metric-value" id="costAvg">$--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Daily Budget</div>
            <div class="metric-value" id="costBudget">$--</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Cost over time</div>
          <svg class="spark" id="costChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="legend">
          <div class="legend-item">
            <div class="legend-color" style="background: #3b82f6;"></div>
            <span>Cumulative cost in USD</span>
          </div>
          <div class="legend-item">
            <div class="legend-color line" style="background: #f59e0b;"></div>
            <span>Daily budget threshold</span>
          </div>
        </div>
      </article>

      <article class="card">
        <div class="card-header">
          <span class="card-label">Token Usage</span>
          <div class="card-icon">&#128164;</div>
        </div>
        <div class="value-primary" id="tokensValue">-- / --</div>
        <div class="value-secondary">Input / Output</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">Input</div>
            <div class="metric-value" id="tokensIn">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Output</div>
            <div class="metric-value" id="tokensOut">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Total</div>
            <div class="metric-value" id="tokensTotal">--</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Total token consumption</div>
          <svg class="spark" id="tokensChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="legend">
          <span>Monitors token usage to detect prompt inflation or verbose responses</span>
        </div>
      </article>

      <article class="card">
        <div class="card-header">
          <span class="card-label">Quality Score</span>
          <div class="card-icon">&#11088;</div>
        </div>
        <div class="value-primary" id="qualityValue">--</div>
        <div class="value-secondary">Average Quality</div>

        <div class="metrics-row">
          <div class="metric-item">
            <div class="metric-label">Target</div>
            <div class="metric-value" id="qualityTarget">--</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Status</div>
            <div class="metric-value ok" id="qualityStatus">Good</div>
          </div>
        </div>

        <div class="spark-container">
          <div class="spark-label">Quality proxy score</div>
          <svg class="spark" id="qualityChart" viewBox="0 0 320 80" preserveAspectRatio="none"></svg>
        </div>

        <div class="legend">
          <div class="legend-item">
            <div class="legend-color" style="background: #3b82f6;"></div>
            <span>Quality heuristic proxy</span>
          </div>
          <div class="legend-item">
            <div class="legend-color line" style="background: #f59e0b;"></div>
            <span>Minimum acceptable quality</span>
          </div>
        </div>
      </article>
    </div>

    <div class="section-title">Investigation View</div>
    <div class="stack">
      <article class="card">
        <div class="card-header">
          <span class="card-label">Raw JSONL Logs</span>
          <div class="card-icon">&#129534;</div>
        </div>
        <div class="value-secondary">Latest filtered records from <code>data/logs.jsonl</code></div>
        <div class="raw-table-wrap">
          <table class="raw-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>Service</th>
                <th>Correlation ID</th>
                <th>Feature</th>
                <th>Latency</th>
                <th>Cost</th>
                <th>Preview / Detail</th>
              </tr>
            </thead>
            <tbody id="rawLogsTable">
              <tr><td colspan="8" class="no-data">No log records available for the selected time window.</td></tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="card context-card">
        <div class="card-header">
          <span class="card-label">Context &amp; Controls</span>
          <div class="card-icon">&#127899;&#65039;</div>
        </div>
        <div class="context-grid">
          <div class="context-stat blue">
            <div class="context-stat-label">Records In Window</div>
            <div class="context-stat-value" id="recordCount">0</div>
            <div class="context-stat-sub">Filtered from logs.jsonl</div>
          </div>
          <div class="context-stat teal">
            <div class="context-stat-label">Last Event</div>
            <div class="context-stat-value" id="lastEvent">--</div>
            <div class="context-stat-sub">Most recent log timestamp</div>
          </div>
          <div class="context-stat amber">
            <div class="context-stat-label">Live Traffic</div>
            <div class="context-stat-value" id="liveTraffic">0</div>
            <div class="context-stat-sub">In-memory request count</div>
          </div>
          <div class="context-stat slate">
            <div class="context-stat-label">Current Window</div>
            <div class="context-stat-value" id="windowContext">1h</div>
            <div class="context-stat-sub">Auto-refresh aware view</div>
          </div>
        </div>
        <div class="legend">
          Use the time window control to focus on a recent incident, then inspect the raw JSONL lines to correlate the exact request, correlation_id, and error_type with the charts above.
        </div>
        <div class="section-title" style="font-size: 14px; margin: 16px 0 8px; border: none; padding: 0;">Incident Toggles</div>
        <div class="incident-list" id="incidentList"></div>
      </article>
    </div>
  </div>

  <script>
    function money(v) { return "$" + Number(v || 0).toFixed(4); }
    function pct(v) { return Number(v || 0).toFixed(2) + "%"; }
    function fixed(v, n = 0) { return Number(v || 0).toFixed(n); }
    function statusClass(ok) { return ok ? "ok" : "warn"; }
    function humanWindow(seconds) {
      if (seconds === 0) return "All data";
      if (seconds < 3600) return `Last ${Math.round(seconds / 60)} minutes`;
      if (seconds < 86400) return `Last ${Math.round(seconds / 3600)} hours`;
      return `Last ${Math.round(seconds / 86400)} days`;
    }
    function formatLocal(ts) {
      if (!ts) return "--";
      return new Date(ts).toLocaleTimeString();
    }

    function shortWindow(seconds) {
      if (seconds === 0) return "All";
      if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
      if (seconds < 86400) return `${Math.round(seconds / 3600)}h`;
      return `${Math.round(seconds / 86400)}d`;
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function summarizeLog(record) {
      if (record.payload && record.payload.message_preview) return record.payload.message_preview;
      if (record.payload && record.payload.answer_preview) return record.payload.answer_preview;
      if (record.payload && record.payload.detail) return record.payload.detail;
      return JSON.stringify(record.payload || {});
    }

    function renderRawLogTable(records) {
      const tbody = document.getElementById("rawLogsTable");
      if (!records.length) {
        tbody.innerHTML = `<tr><td colspan="8" class="no-data">No log records available for the selected time window.</td></tr>`;
        return;
      }
      tbody.innerHTML = records.map((record) => {
        const event = escapeHtml(record.event || "unknown");
        const eventClass = `event-${event.replace(/[^a-zA-Z0-9_-]/g, "-")}`;
        return `
          <tr>
            <td class="muted-cell">${escapeHtml(formatLocal(record.ts))}</td>
            <td><span class="raw-pill ${eventClass}">${event}</span></td>
            <td>${escapeHtml(record.service || "--")}</td>
            <td>${escapeHtml(record.correlation_id || "--")}</td>
            <td>${escapeHtml(record.feature || "--")}</td>
            <td>${record.latency_ms != null ? `${escapeHtml(record.latency_ms)} ms` : "--"}</td>
            <td>${record.cost_usd != null ? money(record.cost_usd) : "--"}</td>
            <td class="truncate-cell">${escapeHtml(summarizeLog(record))}</td>
          </tr>
        `;
      }).join("");
    }

    let refreshHandle = null;

    function currentParams() {
      return {
        window_seconds: Number(document.getElementById("windowSelect").value),
        raw_limit: Number(document.getElementById("rawLimitSelect").value),
      };
    }

    function installRefreshTimer() {
      if (refreshHandle) {
        clearInterval(refreshHandle);
        refreshHandle = null;
      }
      const interval = Number(document.getElementById("refreshSelect").value);
      document.getElementById("refreshMeta").textContent =
        "Auto-refresh: " + (interval === 0 ? "Off" : `${interval / 1000}s`);
      if (interval > 0) {
        refreshHandle = setInterval(refreshDashboard, interval);
      }
    }

    function renderSparkline(id, values, threshold) {
      const svg = document.getElementById(id);
      const width = 320;
      const height = 80;
      const usable = values.length ? values : [0];
      const maxData = Math.max(...usable, threshold || 0, 1);
      const minData = Math.min(...usable, 0);
      const range = maxData - minData || 1;

      const points = usable.map((value, index) => {
        const x = usable.length === 1 ? width / 2 : (index / (usable.length - 1)) * width;
        const y = height - ((value - minData) / range) * (height - 12) - 6;
        return `${x},${y}`;
      }).join(" ");

      const thresholdY = threshold == null ? null : height - ((threshold - minData) / range) * (height - 12) - 6;

      const gradient = `
        <defs>
          <linearGradient id="grad-${id}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.15" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.01" />
          </linearGradient>
        </defs>
      `;

      svg.innerHTML = `
        ${gradient}
        <polygon points="0,${height} ${points} ${width},${height}" fill="url(#grad-${id})"></polygon>
        <polyline points="${points}" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"></polyline>
        ${thresholdY == null ? "" : `<line x1="0" y1="${thresholdY}" x2="${width}" y2="${thresholdY}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="5 3"></line>`}
      `;
    }

    async function refreshDashboard() {
      try {
        const params = new URLSearchParams(currentParams());
        const response = await fetch(`/dashboard-data?${params.toString()}`);
        const data = await response.json();
        const snap = data.snapshot;
        const hist = data.history;
        const slo = data.slo_targets;
        const live = data.live_metrics.snapshot;

        const latencyOk = snap.latency_p95 <= slo.latency_p95_ms;
        const errorOk = snap.error_rate_pct <= slo.error_rate_pct;
        const costOk = snap.total_cost_usd <= slo.daily_cost_usd;
        const qualityOk = snap.quality_avg >= slo.quality_score_avg;

        document.getElementById("statusBadge").className =
          (latencyOk && errorOk && costOk && qualityOk) ? "status-badge" : "status-badge warning";
        document.getElementById("statusBadge").innerHTML =
          `<span class="status-dot"></span>${(latencyOk && errorOk && costOk && qualityOk) ? "System Healthy" : "Attention Required"}`;
        document.getElementById("windowMeta").textContent =
          `Window: ${humanWindow(data.window_seconds)}`;
        document.getElementById("generatedMeta").textContent =
          `Last refresh: ${formatLocal(data.generated_at)}`;

        document.getElementById("latencyValue").textContent = `${fixed(snap.latency_p95)} ms`;
        document.getElementById("latencyP50").textContent = `${fixed(snap.latency_p50)} ms`;
        document.getElementById("latencyP99").textContent = `${fixed(snap.latency_p99)} ms`;
        document.getElementById("latencySLO").className = `metric-value ${statusClass(latencyOk)}`;
        document.getElementById("latencySLO").textContent = slo.latency_p95_ms + " ms";
        renderSparkline("latencyChart", hist.map(x => x.latency_p95), slo.latency_p95_ms);

        document.getElementById("trafficValue").textContent = fixed(snap.traffic);
        renderSparkline("trafficChart", hist.map(x => x.traffic));

        const errorCount = Object.values(snap.error_breakdown).reduce((a, b) => a + b, 0);
        document.getElementById("errorValue").textContent = pct(snap.error_rate_pct);
        document.getElementById("errorSLO").className = `metric-value ${statusClass(errorOk)}`;
        document.getElementById("errorSLO").textContent = slo.error_rate_pct + "%";
        document.getElementById("errorCount").textContent = errorCount;
        document.getElementById("errorBreakdown").textContent =
          Object.keys(snap.error_breakdown).length ? JSON.stringify(snap.error_breakdown, null, 2) : "No errors recorded.";
        renderSparkline("errorChart", hist.map(x => x.error_rate_pct), slo.error_rate_pct);

        document.getElementById("costValue").textContent = money(snap.total_cost_usd);
        document.getElementById("costAvg").textContent = money(snap.avg_cost_usd);
        document.getElementById("costBudget").className = `metric-value ${statusClass(costOk)}`;
        document.getElementById("costBudget").textContent = money(slo.daily_cost_usd);
        renderSparkline("costChart", hist.map(x => x.total_cost_usd), slo.daily_cost_usd);

        document.getElementById("tokensValue").textContent =
          `${fixed(snap.tokens_in_total)} / ${fixed(snap.tokens_out_total)}`;
        document.getElementById("tokensIn").textContent = fixed(snap.tokens_in_total);
        document.getElementById("tokensOut").textContent = fixed(snap.tokens_out_total);
        document.getElementById("tokensTotal").textContent =
          fixed(snap.tokens_in_total + snap.tokens_out_total);
        renderSparkline("tokensChart", hist.map(x => (x.tokens_in_total || 0) + (x.tokens_out_total || 0)));

        document.getElementById("qualityValue").textContent = fixed(snap.quality_avg, 2);
        document.getElementById("qualityTarget").textContent = fixed(slo.quality_score_avg, 2);
        document.getElementById("qualityStatus").className = `metric-value ${statusClass(qualityOk)}`;
        document.getElementById("qualityStatus").textContent = qualityOk ? "Good" : "Low";
        renderSparkline("qualityChart", hist.map(x => x.quality_avg), slo.quality_score_avg);

        document.getElementById("recordCount").textContent = fixed(snap.records_in_window);
        document.getElementById("lastEvent").textContent = formatLocal(snap.last_event_ts);
        document.getElementById("liveTraffic").textContent = fixed(live.traffic);
        document.getElementById("windowContext").textContent = shortWindow(data.window_seconds);
        renderRawLogTable(data.raw_logs);

        const incidentEntries = Object.entries(data.incidents || {});
        document.getElementById("incidentList").innerHTML = incidentEntries.length
          ? incidentEntries
              .map(([name, enabled]) => `<span class="incident-pill ${enabled ? "" : "off"}">${name}: ${enabled ? "on" : "off"}</span>`)
              .join("")
          : `<span class="incident-pill off">No incidents configured</span>`;
      } catch (err) {
        console.error("Dashboard refresh error:", err);
      }
    }

    document.getElementById("windowSelect").addEventListener("change", refreshDashboard);
    document.getElementById("rawLimitSelect").addEventListener("change", refreshDashboard);
    document.getElementById("refreshSelect").addEventListener("change", () => {
      installRefreshTimer();
      refreshDashboard();
    });
    document.getElementById("refreshButton").addEventListener("click", refreshDashboard);

    installRefreshTimer();
    refreshDashboard();
  </script>
</body>
</html>
        """
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )

    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
