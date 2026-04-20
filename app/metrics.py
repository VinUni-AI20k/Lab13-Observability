from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
METRIC_HISTORY: list[dict[str, float | int | str]] = []


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    _append_history_point()


def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1
    _append_history_point()


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def error_rate_pct() -> float:
    total_events = TRAFFIC + sum(ERRORS.values())
    if total_events == 0:
        return 0.0
    return round((sum(ERRORS.values()) / total_events) * 100, 2)


def _append_history_point() -> None:
    point = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "traffic": TRAFFIC,
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "error_rate_pct": error_rate_pct(),
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }
    METRIC_HISTORY.append(point)
    if len(METRIC_HISTORY) > 120:
        del METRIC_HISTORY[:-120]


def history() -> list[dict[str, float | int | str]]:
    return METRIC_HISTORY[-60:]


def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "error_rate_pct": error_rate_pct(),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }
