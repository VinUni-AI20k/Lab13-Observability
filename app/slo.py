"""
SLO management: load config, evaluate against live metrics, send Discord alerts.
Deduplication: one alert per SLO per COOLDOWN_SECONDS (default 600s / 10min).
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

from . import metrics as _metrics

CONFIG_PATH = Path(__file__).parent.parent / "config" / "slo.yaml"
COOLDOWN_SECONDS = int(os.getenv("SLO_ALERT_COOLDOWN", "600"))

# Dedup state: slo_name → unix timestamp of last sent alert
_last_notified: dict[str, float] = {}


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class SLOConfig:
    name: str
    display_name: str
    description: str
    objective: float   # threshold value
    target_pct: float  # availability target e.g. 99.5%
    unit: str          # ms | % | USD | score
    direction: str     # lower_is_better | higher_is_better


@dataclass
class SLOResult:
    config: SLOConfig
    current_value: float
    status: str         # "ok" | "violated" | "no_data"
    last_checked: str   # ISO timestamp
    notified: bool = False


# ── Static schema for yaml keys ───────────────────────────────────────────────

_META: dict[str, dict] = {
    "latency_p95_ms": {
        "display_name": "P95 Latency",
        "unit": "ms",
        "direction": "lower_is_better",
        "description": "95th-percentile response time must stay under threshold",
    },
    "error_rate_pct": {
        "display_name": "Error Rate",
        "unit": "%",
        "direction": "lower_is_better",
        "description": "% of requests that resulted in errors",
    },
    "daily_cost_usd": {
        "display_name": "Daily Cost",
        "unit": "USD",
        "direction": "lower_is_better",
        "description": "Accumulated LLM API cost since server start",
    },
    "quality_score_avg": {
        "display_name": "Quality Score",
        "unit": "score",
        "direction": "higher_is_better",
        "description": "Average response quality (0–1 scale)",
    },
}


# ── Loader ────────────────────────────────────────────────────────────────────

def load_slos() -> list[SLOConfig]:
    """Read config/slo.yaml → list of SLOConfig."""
    try:
        raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    slos: list[SLOConfig] = []
    for name, cfg in raw.get("slis", {}).items():
        meta = _META.get(name, {})
        slos.append(SLOConfig(
            name=name,
            display_name=meta.get("display_name", name),
            description=meta.get("description", ""),
            objective=float(cfg.get("objective", 0)),
            target_pct=float(cfg.get("target", 99.0)),
            unit=meta.get("unit", ""),
            direction=meta.get("direction", "lower_is_better"),
        ))
    return slos


# ── Metric extractor ──────────────────────────────────────────────────────────

def _current(slo: SLOConfig, snap: dict) -> float | None:
    if slo.name == "latency_p95_ms":
        return snap.get("latency_p95")
    if slo.name == "error_rate_pct":
        traffic = snap.get("traffic", 0)
        errors  = sum(snap.get("error_breakdown", {}).values())
        return round(errors / traffic * 100, 2) if traffic > 0 else None
    if slo.name == "daily_cost_usd":
        return snap.get("total_cost_usd")
    if slo.name == "quality_score_avg":
        v = snap.get("quality_avg", 0.0)
        return v if snap.get("traffic", 0) > 0 else None
    return None


# ── Evaluator ─────────────────────────────────────────────────────────────────

def evaluate(slos: list[SLOConfig] | None = None) -> list[SLOResult]:
    """Compare current live metrics to each SLO. Returns evaluation list."""
    if slos is None:
        slos = load_slos()

    snap = _metrics.snapshot()
    now  = datetime.now(timezone.utc).isoformat()

    results: list[SLOResult] = []
    for slo in slos:
        value = _current(slo, snap)
        if value is None:
            results.append(SLOResult(config=slo, current_value=0.0, status="no_data", last_checked=now))
            continue

        if slo.direction == "lower_is_better":
            violated = value > slo.objective
        else:
            violated = value < slo.objective

        results.append(SLOResult(
            config=slo,
            current_value=round(value, 4),
            status="violated" if violated else "ok",
            last_checked=now,
        ))
    return results


# ── Discord ───────────────────────────────────────────────────────────────────

def _can_notify(name: str) -> bool:
    return (time.time() - _last_notified.get(name, 0)) > COOLDOWN_SECONDS


def notify_discord(result: SLOResult, force: bool = False) -> bool:
    """
    POST a rich Discord embed for a violated SLO.
    Returns True if the message was actually sent.
    Silently skips if: webhook not configured, cooldown active (unless force=True).
    """
    url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        return False
    if not force and not _can_notify(result.config.name):
        return False

    slo   = result.config
    val   = result.current_value
    limit = slo.objective
    unit  = slo.unit
    ts    = result.last_checked

    # Choose emoji based on direction
    over_or_under = "↑ too high" if slo.direction == "lower_is_better" else "↓ too low"

    payload = {
        "username": "SLO Monitor",
        "embeds": [{
            "title": "🚨 SLO Violation",
            "description": (
                f"**{slo.display_name}** has breached its objective.\n"
                f"*{slo.description}*"
            ),
            "color": 0xE74C3C,
            "fields": [
                {
                    "name": "SLO",
                    "value": f"`{slo.name}`",
                    "inline": True,
                },
                {
                    "name": "Current Value",
                    "value": f"**{val} {unit}** {over_or_under}",
                    "inline": True,
                },
                {
                    "name": "Objective",
                    "value": f"{limit} {unit}",
                    "inline": True,
                },
                {
                    "name": "Availability Target",
                    "value": f"{slo.target_pct}%",
                    "inline": True,
                },
                {
                    "name": "Detected at (UTC)",
                    "value": ts,
                    "inline": False,
                },
            ],
            "footer": {
                "text": "Day 13 Observability Lab • SLO Monitor",
            },
        }],
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
        _last_notified[slo.name] = time.time()
        return True
    except Exception:
        return False


# ── Combined check + notify ───────────────────────────────────────────────────

def check_and_notify(slos: list[SLOConfig] | None = None) -> list[SLOResult]:
    """Evaluate all SLOs and send Discord alerts for violations (with dedup)."""
    results = evaluate(slos)
    for r in results:
        if r.status == "violated":
            r.notified = notify_discord(r)
    return results


# ── Serialiser for API responses ──────────────────────────────────────────────

def result_to_dict(r: SLOResult) -> dict:
    return {
        "name":          r.config.name,
        "display_name":  r.config.display_name,
        "description":   r.config.description,
        "objective":     r.config.objective,
        "unit":          r.config.unit,
        "target_pct":    r.config.target_pct,
        "direction":     r.config.direction,
        "current_value": r.current_value,
        "status":        r.status,
        "last_checked":  r.last_checked,
        "notified":      r.notified,
    }
