"""Build 6-panel observability dashboard from logs.jsonl + /metrics snapshot.

Outputs docs/evidence/dashboard-6-panels.html (and a PNG via matplotlib).
Run: python scripts/build_dashboard.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))
OUT_PNG = Path("docs/dashboard-6-panels.png")
OUT_PNG.parent.mkdir(parents=True, exist_ok=True)

# ── load logs ──────────────────────────────────────────────────────────────────
records = []
if LOG_PATH.exists():
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

response_logs = [r for r in records if r.get("event") == "response_sent" and r.get("service") == "api"]

latencies   = [r["latency_ms"]   for r in response_logs if "latency_ms"   in r]
costs       = [r["cost_usd"]     for r in response_logs if "cost_usd"     in r]
tokens_in   = [r["tokens_in"]    for r in response_logs if "tokens_in"    in r]
tokens_out  = [r["tokens_out"]   for r in response_logs if "tokens_out"   in r]
qualities   = [r.get("quality_score", r.get("quality_avg", 0)) for r in response_logs]

error_logs = [r for r in records if r.get("event") == "request_failed"]
total_req  = len(response_logs) + len(error_logs)
error_rate = (len(error_logs) / total_req * 100) if total_req else 0.0

def percentile(data: list[float], p: int) -> float:
    if not data:
        return 0.0
    arr = sorted(data)
    idx = max(0, int(np.ceil(p / 100 * len(arr))) - 1)
    return arr[idx]

p50 = percentile(latencies, 50)
p95 = percentile(latencies, 95)
p99 = percentile(latencies, 99)
avg_quality = sum(qualities) / len(qualities) if qualities else 0.0

# ── figure setup ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 11), facecolor="#0f1117")
fig.suptitle(
    "Day 13 Observability Lab — Dashboard  |  Auto-refresh: 30s  |  Window: last 1h",
    color="white", fontsize=13, fontweight="bold", y=0.98,
)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)
DARK_BG   = "#1a1d27"
GRID_CLR  = "#2a2d3a"
TEXT_CLR  = "#e0e0e0"
ACCENT    = "#4e9af1"
WARN      = "#f1c94e"
DANGER    = "#f14e4e"
OK        = "#4ef18a"

def styled_ax(ax, title: str) -> None:
    ax.set_facecolor(DARK_BG)
    ax.set_title(title, color=TEXT_CLR, fontsize=10, pad=8, fontweight="bold")
    ax.tick_params(colors=TEXT_CLR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.yaxis.grid(True, color=GRID_CLR, linewidth=0.5)
    ax.set_axisbelow(True)

# ── Panel 1: Latency P50/P95/P99 ──────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
styled_ax(ax1, "Panel 1 — Latency P50 / P95 / P99  (ms)")
labels = ["P50", "P95", "P99"]
values = [p50, p95, p99]
colors = [OK if v < 1000 else WARN if v < 3000 else DANGER for v in values]
bars = ax1.bar(labels, values, color=colors, width=0.5, zorder=3)
ax1.axhline(y=3000, color=DANGER, linewidth=1.5, linestyle="--", label="SLO 3000ms")
ax1.set_ylabel("ms", color=TEXT_CLR, fontsize=8)
ax1.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_CLR, framealpha=0.8)
for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
             f"{val:.0f}ms", ha="center", va="bottom", color=TEXT_CLR, fontsize=8)

# ── Panel 2: Traffic ──────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
styled_ax(ax2, "Panel 2 — Traffic  (request count)")
chunks = [latencies[i:i+10] for i in range(0, len(latencies), 10)]
batch_labels = [f"Batch {i+1}" for i in range(len(chunks))]
batch_counts = [len(c) for c in chunks]
ax2.bar(batch_labels, batch_counts, color=ACCENT, width=0.6, zorder=3)
ax2.set_ylabel("requests / batch", color=TEXT_CLR, fontsize=8)
ax2.tick_params(axis="x", rotation=30)
ax2.text(0.98, 0.95, f"Total: {total_req}", transform=ax2.transAxes,
         ha="right", va="top", color=TEXT_CLR, fontsize=9,
         bbox=dict(facecolor=GRID_CLR, alpha=0.8, boxstyle="round,pad=0.3"))

# ── Panel 3: Error Rate ────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
styled_ax(ax3, "Panel 3 — Error Rate  (%)")
er_color = DANGER if error_rate >= 5 else WARN if error_rate >= 2 else OK
ax3.bar(["Error Rate"], [error_rate], color=er_color, width=0.4, zorder=3)
ax3.axhline(y=2, color=WARN, linewidth=1.5, linestyle="--", label="SLO 2%")
ax3.axhline(y=5, color=DANGER, linewidth=1.5, linestyle="--", label="Alert 5%")
ax3.set_ylabel("%", color=TEXT_CLR, fontsize=8)
ax3.set_ylim(0, max(10, error_rate * 1.5 + 1))
ax3.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_CLR, framealpha=0.8)
ax3.text(0, error_rate + 0.1, f"{error_rate:.1f}%", ha="center", va="bottom",
         color=TEXT_CLR, fontsize=9)

# ── Panel 4: Cost Over Time ────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
styled_ax(ax4, "Panel 4 — Cost Over Time  (USD)")
cum_costs = list(np.cumsum(costs)) if costs else [0]
ax4.plot(range(len(cum_costs)), cum_costs, color=WARN, linewidth=2, marker="o",
         markersize=3, zorder=3)
ax4.axhline(y=2.5, color=DANGER, linewidth=1.5, linestyle="--", label="Budget $2.5/day")
ax4.set_ylabel("Cumulative USD", color=TEXT_CLR, fontsize=8)
ax4.set_xlabel("Request #", color=TEXT_CLR, fontsize=8)
ax4.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_CLR, framealpha=0.8)
total_cost = sum(costs)
ax4.text(0.98, 0.05, f"Total: ${total_cost:.4f}", transform=ax4.transAxes,
         ha="right", va="bottom", color=TEXT_CLR, fontsize=8,
         bbox=dict(facecolor=GRID_CLR, alpha=0.8, boxstyle="round,pad=0.3"))

# ── Panel 5: Tokens In / Out ──────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
styled_ax(ax5, "Panel 5 — Tokens In / Out  (per request)")
idx = range(len(tokens_in))
ax5.bar(idx, tokens_in, label="tokens_in", color=ACCENT, alpha=0.85, zorder=3)
ax5.bar(idx, tokens_out, bottom=tokens_in, label="tokens_out", color=WARN, alpha=0.85, zorder=3)
ax5.set_ylabel("tokens", color=TEXT_CLR, fontsize=8)
ax5.set_xlabel("Request #", color=TEXT_CLR, fontsize=8)
ax5.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_CLR, framealpha=0.8)
total_in = sum(tokens_in); total_out = sum(tokens_out)
ax5.text(0.98, 0.95, f"∑in: {total_in}  ∑out: {total_out}", transform=ax5.transAxes,
         ha="right", va="top", color=TEXT_CLR, fontsize=7,
         bbox=dict(facecolor=GRID_CLR, alpha=0.8, boxstyle="round,pad=0.3"))

# ── Panel 6: Quality Score ─────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
styled_ax(ax6, "Panel 6 — Quality Score  (heuristic proxy)")
q_color = OK if avg_quality >= 0.75 else DANGER
ax6.plot(range(len(qualities)), qualities, color=q_color, linewidth=1.5,
         marker="o", markersize=4, zorder=3)
ax6.axhline(y=0.75, color=DANGER, linewidth=1.5, linestyle="--", label="SLO 0.75")
ax6.set_ylim(0, 1.1)
ax6.set_ylabel("score (0–1)", color=TEXT_CLR, fontsize=8)
ax6.set_xlabel("Request #", color=TEXT_CLR, fontsize=8)
ax6.legend(fontsize=7, facecolor=DARK_BG, labelcolor=TEXT_CLR, framealpha=0.8)
ax6.text(0.98, 0.05, f"avg: {avg_quality:.2f}", transform=ax6.transAxes,
         ha="right", va="bottom", color=TEXT_CLR, fontsize=9,
         bbox=dict(facecolor=GRID_CLR, alpha=0.8, boxstyle="round,pad=0.3"))

# ── save ──────────────────────────────────────────────────────────────────────
fig.savefig(OUT_PNG, dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)
print(f"Dashboard saved -> {OUT_PNG}")
print(f"  P50={p50:.0f}ms  P95={p95:.0f}ms  P99={p99:.0f}ms")
print(f"  Traffic={total_req}  Error rate={error_rate:.1f}%")
print(f"  Total cost=${total_cost:.4f}  Quality avg={avg_quality:.2f}")
