from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _parse_ts(value: str) -> datetime | None:
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if p <= 0:
        return float(sorted_vals[0])
    if p >= 100:
        return float(sorted_vals[-1])
    k = (p / 100.0) * (len(sorted_vals) - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return float(d0 + d1)


@dataclass(frozen=True)
class DashboardBucket:
    ts: str
    traffic: int
    error_count: int
    error_by_type: dict[str, int]
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    cost_usd: float
    tokens_in: int
    tokens_out: int
    quality_avg: float


def build_dashboard_series(
    log_path: str | Path,
    window_minutes: int = 60,
    bucket_seconds: int = 60,
    now: datetime | None = None,
) -> dict[str, Any]:
    if bucket_seconds <= 0:
        bucket_seconds = 60
    if window_minutes <= 0:
        window_minutes = 60

    log_path = Path(log_path)
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start = now_utc - timedelta(minutes=window_minutes)

    buckets: dict[int, dict[str, Any]] = {}

    if not log_path.exists():
        return {"window_minutes": window_minutes, "bucket_seconds": bucket_seconds, "series": []}

    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {"window_minutes": window_minutes, "bucket_seconds": bucket_seconds, "series": []}

    for line in lines:
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue

        ts = rec.get("ts")
        if not isinstance(ts, str):
            continue
        dt = _parse_ts(ts)
        if dt is None or dt < start or dt > now_utc:
            continue

        event = rec.get("event")
        if event not in ("response_sent", "request_failed"):
            continue

        epoch = int(dt.timestamp())
        key = epoch - (epoch % bucket_seconds)
        b = buckets.setdefault(
            key,
            {
                "ts": datetime.fromtimestamp(key, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                "traffic": 0,
                "error_count": 0,
                "error_by_type": {},
                "latencies": [],
                "cost_usd": 0.0,
                "tokens_in": 0,
                "tokens_out": 0,
                "qualities": [],
            },
        )

        b["traffic"] += 1

        if event == "request_failed":
            b["error_count"] += 1
            et = rec.get("error_type")
            if not isinstance(et, str) or not et:
                et = "UnknownError"
            b["error_by_type"][et] = int(b["error_by_type"].get(et, 0)) + 1
            continue

        latency_ms = rec.get("latency_ms")
        if isinstance(latency_ms, (int, float)):
            b["latencies"].append(float(latency_ms))

        cost_usd = rec.get("cost_usd")
        if isinstance(cost_usd, (int, float)):
            b["cost_usd"] += float(cost_usd)

        tokens_in = rec.get("tokens_in")
        tokens_out = rec.get("tokens_out")
        if isinstance(tokens_in, int):
            b["tokens_in"] += tokens_in
        if isinstance(tokens_out, int):
            b["tokens_out"] += tokens_out

        q = rec.get("quality_score")
        if isinstance(q, (int, float)):
            b["qualities"].append(float(q))

    series: list[DashboardBucket] = []
    for _, b in sorted(buckets.items(), key=lambda kv: kv[0]):
        lat = sorted(b["latencies"])
        qualities = b["qualities"]
        qavg = sum(qualities) / len(qualities) if qualities else 0.0
        series.append(
            DashboardBucket(
                ts=b["ts"],
                traffic=int(b["traffic"]),
                error_count=int(b["error_count"]),
                error_by_type=dict(b["error_by_type"]),
                latency_p50_ms=_percentile(lat, 50),
                latency_p95_ms=_percentile(lat, 95),
                latency_p99_ms=_percentile(lat, 99),
                cost_usd=round(float(b["cost_usd"]), 6),
                tokens_in=int(b["tokens_in"]),
                tokens_out=int(b["tokens_out"]),
                quality_avg=round(float(qavg), 4),
            )
        )

    return {
        "window_minutes": window_minutes,
        "bucket_seconds": bucket_seconds,
        "series": [s.__dict__ for s in series],
    }

