"""
Alert Evaluator — Member C
============================
Script này đọc alert rules từ config/alert_rules.yaml,
lấy metrics từ app, và đánh giá alert nào đang FIRING (kích hoạt).

CÁCH HOẠT ĐỘNG:
  1. Parse alert rules từ YAML
  2. Gọi GET /metrics để lấy số liệu thực tế
  3. Evaluate từng rule condition
  4. In trạng thái: FIRING (đang cháy) hoặc OK (bình thường)

CÁCH DÙNG:
  # App phải đang chạy
  python scripts/evaluate_alerts.py

  # Offline mode (mock data)
  python scripts/evaluate_alerts.py --offline

  # Simulate incident (giả lập sự cố)
  python scripts/evaluate_alerts.py --offline --simulate cost_spike
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

import yaml

ALERT_PATH = Path("config/alert_rules.yaml")
BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------------------------
# Load alert config
# ---------------------------------------------------------------------------
def load_alert_config() -> list[dict]:
    if not ALERT_PATH.exists():
        print(f"Error: {ALERT_PATH} not found")
        sys.exit(1)
    with ALERT_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("alerts", [])


# ---------------------------------------------------------------------------
# Fetch metrics (giống check_slo.py)
# ---------------------------------------------------------------------------
def fetch_metrics() -> dict:
    import httpx
    try:
        r = httpx.get(f"{BASE_URL}/metrics", timeout=5.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        sys.exit(1)


def get_mock_metrics(simulate: str | None = None) -> dict:
    """
    Mock metrics. Dùng --simulate để giả lập incident cụ thể.

    Các scenario:
      - rag_slow:   latency P95 = 6500ms (vượt ngưỡng 5000ms)
      - tool_fail:  error rate = 12% (vượt ngưỡng 5%)
      - cost_spike: cost gấp 4x bình thường
    """
    base = {
        "traffic": 30,
        "latency_p50": 400,
        "latency_p95": 1800,
        "latency_p99": 2500,
        "avg_cost_usd": 0.0008,
        "total_cost_usd": 0.024,
        "tokens_in_total": 6000,
        "tokens_out_total": 4000,
        "error_breakdown": {},
        "quality_avg": 0.82,
    }

    if simulate == "rag_slow":
        base["latency_p95"] = 6500      # Vượt ngưỡng 5000ms
        base["latency_p99"] = 8200
        base["quality_avg"] = 0.55       # Quality cũng giảm khi RAG chậm
    elif simulate == "tool_fail":
        base["error_breakdown"] = {"RuntimeError": 4}  # 4/30 = 13.3%
        base["quality_avg"] = 0.45
    elif simulate == "cost_spike":
        base["avg_cost_usd"] = 0.004     # 4x bình thường
        base["total_cost_usd"] = 0.12
        base["tokens_in_total"] = 6000
        base["tokens_out_total"] = 16000  # 4x output tokens
    return base


# ---------------------------------------------------------------------------
# Parse và evaluate condition
# ---------------------------------------------------------------------------
def parse_and_evaluate(condition: str, metrics_data: dict) -> tuple[bool, str]:
    """
    Parse condition string từ YAML và evaluate.

    Hỗ trợ formats:
      "latency_p95_ms > 5000 for 30m"
      "error_rate_pct > 5 for 5m"
      "quality_score_avg < 0.6 for 15m"
      "hourly_cost_usd > 2x_baseline for 15m"
      "tokens_in_total > 50000 per hour"

    Tại sao phải parse thủ công?
      → Trong thực tế, alert engine (Prometheus/Grafana) parse điều kiện này
      → Trong lab, ta mô phỏng bằng Python để hiểu cách hoạt động
      → Phần "for 30m" chỉ là metadata (cần data lịch sử để đánh giá đúng)

    Returns: (is_firing, explanation)
    """
    traffic = metrics_data.get("traffic", 0)
    total_errors = sum(metrics_data.get("error_breakdown", {}).values())
    error_rate = (total_errors / traffic * 100) if traffic > 0 else 0

    # Map metric names tới actual values
    value_map = {
        "latency_p95_ms": metrics_data.get("latency_p95", 0),
        "error_rate_pct": error_rate,
        "quality_score_avg": metrics_data.get("quality_avg", 0),
        "hourly_cost_usd": metrics_data.get("total_cost_usd", 0),
        "tokens_in_total": metrics_data.get("tokens_in_total", 0),
    }

    # Baseline cho cost (ước tính): 30 requests * $0.001 = $0.03/h
    cost_baseline = max(0.001, metrics_data.get("avg_cost_usd", 0.001)) * 30

    # Parse condition: "metric_name > threshold for/per ..."
    # Regex giải thích:
    #   (\w+)           → tên metric (vd: latency_p95_ms)
    #   \s*([<>]=?)\s*  → operator (>, <, >=, <=)
    #   (.+?)           → threshold value (có thể là "5000" hoặc "2x_baseline")
    #   (?:\s+(?:for|per)\s+.+)?  → optional "for 30m" hoặc "per hour"
    match = re.match(r"(\w+)\s*([<>]=?)\s*(.+?)(?:\s+(?:for|per)\s+.+)?$", condition.strip())

    if not match:
        return False, f"Cannot parse condition: {condition}"

    metric_name = match.group(1)
    operator = match.group(2)
    threshold_raw = match.group(3).strip()

    # Resolve threshold
    if "x_baseline" in threshold_raw:
        multiplier = float(threshold_raw.replace("x_baseline", ""))
        threshold = cost_baseline * multiplier
    else:
        threshold = float(threshold_raw)

    actual = value_map.get(metric_name, 0)

    # Evaluate
    if operator == ">":
        firing = actual > threshold
    elif operator == ">=":
        firing = actual >= threshold
    elif operator == "<":
        firing = actual < threshold
    elif operator == "<=":
        firing = actual <= threshold
    else:
        return False, f"Unknown operator: {operator}"

    explanation = f"{metric_name} = {actual:.2f} (threshold: {operator} {threshold:.2f})"
    return firing, explanation


# ---------------------------------------------------------------------------
# Print results
# ---------------------------------------------------------------------------
def print_alert_status(alerts: list[dict], metrics_data: dict) -> None:
    print("=" * 78)
    print("  ALERT EVALUATION REPORT")
    print("=" * 78)
    print()

    firing_count = 0

    for alert in alerts:
        name = alert["name"]
        severity = alert.get("severity", "?")
        condition = alert.get("condition", "")
        runbook = alert.get("runbook", "N/A")

        is_firing, explanation = parse_and_evaluate(condition, metrics_data)

        if is_firing:
            firing_count += 1
            icon = ">>>"
            status = "FIRING"
        else:
            icon = "[OK]"
            status = "OK"

        print(f"  {icon} [{severity}] {name}: {status}")
        print(f"     Condition: {condition}")
        print(f"     Current:   {explanation}")
        if is_firing:
            print(f"     Runbook:   {runbook}")
        print()

    print("-" * 78)
    if firing_count > 0:
        print(f"[ALERT] {firing_count} alert(s) FIRING! Check runbooks above.")
    else:
        print("[OK] All alerts OK. System healthy.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # Fix Unicode output on Windows
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Evaluate alert rules against live metrics")
    parser.add_argument("--offline", action="store_true", help="Use mock data")
    parser.add_argument(
        "--simulate", choices=["rag_slow", "tool_fail", "cost_spike"],
        help="Simulate an incident scenario (requires --offline)"
    )
    args = parser.parse_args()

    alerts = load_alert_config()

    if args.offline:
        scenario = args.simulate
        if scenario:
            print(f"[OFFLINE] Simulating incident: {scenario}\n")
        else:
            print("[OFFLINE] Using healthy mock data\n")
        metrics_data = get_mock_metrics(simulate=scenario)
    else:
        metrics_data = fetch_metrics()

    print_alert_status(alerts, metrics_data)


if __name__ == "__main__":
    main()
