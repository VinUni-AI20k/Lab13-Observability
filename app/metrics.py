from __future__ import annotations

import time
from collections import Counter, defaultdict
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []

# Time-series data for dashboard (last hour)
TIMESERIES_DATA: defaultdict[int, dict] = defaultdict(lambda: {
    "timestamp": 0,
    "requests": 0,
    "errors": 0,
    "latencies": [],
    "costs": [],
    "tokens_in": 0,
    "tokens_out": 0,
    "quality_scores": []
})


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    
    # Record time-series data (1-minute buckets)
    minute_bucket = int(time.time()) // 60
    bucket = TIMESERIES_DATA[minute_bucket]
    bucket["timestamp"] = minute_bucket * 60
    bucket["requests"] += 1
    bucket["latencies"].append(latency_ms)
    bucket["costs"].append(cost_usd)
    bucket["tokens_in"] += tokens_in
    bucket["tokens_out"] += tokens_out
    bucket["quality_scores"].append(quality_score)


def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1
    
    # Record error in time-series
    minute_bucket = int(time.time()) // 60
    bucket = TIMESERIES_DATA[minute_bucket]
    bucket["errors"] += 1


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def calculate_error_rate() -> float:
    total_requests = TRAFFIC
    total_errors = sum(ERRORS.values())
    if total_requests == 0:
        return 0.0
    return round((total_errors / total_requests) * 100, 2)


def get_timeseries_data() -> list[dict]:
    """Get time-series data for the last hour"""
    current_time = int(time.time())
    one_hour_ago = current_time - 3600
    
    result = []
    for minute_bucket, data in TIMESERIES_DATA.items():
        if data["timestamp"] >= one_hour_ago:
            bucket_data = {
                "timestamp": data["timestamp"],
                "requests": data["requests"],
                "errors": data["errors"],
                "error_rate": round((data["errors"] / data["requests"]) * 100, 2) if data["requests"] > 0 else 0,
                "latency_p50": percentile(data["latencies"], 50) if data["latencies"] else 0,
                "latency_p95": percentile(data["latencies"], 95) if data["latencies"] else 0,
                "latency_p99": percentile(data["latencies"], 99) if data["latencies"] else 0,
                "avg_cost": round(mean(data["costs"]), 4) if data["costs"] else 0,
                "tokens_in": data["tokens_in"],
                "tokens_out": data["tokens_out"],
                "quality_avg": round(mean(data["quality_scores"]), 4) if data["quality_scores"] else 0
            }
            result.append(bucket_data)
    
    return sorted(result, key=lambda x: x["timestamp"])


def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "error_rate_pct": calculate_error_rate(),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
        "timeseries": get_timeseries_data()
    }
