from __future__ import annotations

import time
from collections import Counter
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
SEVERITY_COUNTS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
HISTORY: list[dict] = []
LAST_SNAPSHOT_TIME: float = 0


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float, severity: str = "Normal") -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    SEVERITY_COUNTS[severity] += 1
    
    # Keep bounded
    if len(REQUEST_LATENCIES) > 1000:
        REQUEST_LATENCIES.pop(0)
        REQUEST_COSTS.pop(0)
        REQUEST_TOKENS_IN.pop(0)
        REQUEST_TOKENS_OUT.pop(0)
        QUALITY_SCORES.pop(0)


def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def snapshot() -> dict:
    global LAST_SNAPSHOT_TIME
    now = time.time()
    
    # Calculate current state
    current_state = {
        "timestamp": int(now * 1000),
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "severity_counts": dict(SEVERITY_COUNTS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
        "error_rate": (sum(ERRORS.values()) / max(1, TRAFFIC)) * 100
    }
    
    # Append to history every 2 seconds roughly
    if now - LAST_SNAPSHOT_TIME >= 2.0:
        HISTORY.append(current_state.copy())
        LAST_SNAPSHOT_TIME = now
        if len(HISTORY) > 30: # keep last 60 seconds (30 * 2s)
            HISTORY.pop(0)
            
    current_state["history"] = HISTORY
    return current_state
