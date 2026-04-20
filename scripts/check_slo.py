"""
SLO Compliance Checker — Member C
===================================
Script này đọc metrics từ app đang chạy, so sánh với SLO config,
và đưa ra bảng compliance (đạt/không đạt).

CÁCH HOẠT ĐỘNG:
  1. Đọc SLO definitions từ config/slo.yaml
  2. Gọi GET /metrics để lấy số liệu thực tế
  3. So sánh actual vs objective
  4. In bảng kết quả + tính error budget còn lại

CÁCH DÙNG:
  # App phải đang chạy (uvicorn app.main:app --reload)
  python scripts/check_slo.py

  # Chỉ kiểm tra offline (không cần app chạy, dùng mock data)
  python scripts/check_slo.py --offline
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import yaml

# Fix Unicode output trên Windows (PowerShell dùng cp1252 mặc định)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Hằng số
# ---------------------------------------------------------------------------
SLO_PATH = Path("config/slo.yaml")
BASE_URL = "http://127.0.0.1:8000"

# Mapping: SLI name trong slo.yaml → field name trong /metrics response
# Tại sao cần mapping này?
#   → slo.yaml dùng tên mô tả ("latency_p95_ms")
#   → /metrics trả về tên kỹ thuật ("latency_p95")
#   → Cần bảng ánh xạ giữa hai hệ thống
SLI_TO_METRIC = {
    "latency_p95_ms": "latency_p95",
    "error_rate_pct": "__computed_error_rate__",   # Tự tính từ errors/traffic
    "daily_cost_usd": "total_cost_usd",
    "quality_score_avg": "quality_avg",
}


# ---------------------------------------------------------------------------
# Hàm đọc SLO config
# ---------------------------------------------------------------------------
def load_slo_config() -> dict:
    """
    Đọc file slo.yaml và trả về dict.

    Tại sao dùng YAML mà không phải JSON?
      → YAML hỗ trợ comment (giải thích ngay trong file)
      → Dễ đọc hơn JSON cho config files
      → Chuẩn công nghiệp cho Kubernetes, Prometheus, Grafana
    """
    if not SLO_PATH.exists():
        print(f"Error: {SLO_PATH} not found")
        sys.exit(1)
    with SLO_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Hàm lấy metrics từ app
# ---------------------------------------------------------------------------
def fetch_metrics() -> dict:
    """
    Gọi GET /metrics và trả về dict metrics.

    Endpoint /metrics trả về:
    {
        "traffic": 45,
        "latency_p50": 820, "latency_p95": 1950, "latency_p99": 2800,
        "avg_cost_usd": 0.0012, "total_cost_usd": 0.054,
        "tokens_in_total": 12500, "tokens_out_total": 8300,
        "error_breakdown": {"TimeoutError": 2},
        "quality_avg": 0.78
    }
    """
    import httpx
    try:
        r = httpx.get(f"{BASE_URL}/metrics", timeout=5.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        print("Hint: Is the app running? (uvicorn app.main:app --reload)")
        sys.exit(1)


def get_mock_metrics() -> dict:
    """
    Metrics giả lập để test offline (không cần app chạy).
    Giá trị được thiết kế để một số SLO pass, một số fail.
    """
    return {
        "traffic": 25,
        "latency_p50": 400,
        "latency_p95": 1800,
        "latency_p99": 2500,
        "avg_cost_usd": 0.0008,
        "total_cost_usd": 0.02,
        "tokens_in_total": 5000,
        "tokens_out_total": 3200,
        "error_breakdown": {"RuntimeError": 1},
        "quality_avg": 0.82,
    }


# ---------------------------------------------------------------------------
# Hàm tính error rate
# ---------------------------------------------------------------------------
def compute_error_rate(metrics_data: dict) -> float:
    """
    Tính tỉ lệ lỗi = tổng errors / tổng traffic * 100

    Ví dụ: 2 errors / 25 traffic = 8%

    Tại sao tính thủ công?
      → /metrics không trả về error_rate trực tiếp
      → Chỉ trả về error_breakdown (đếm theo loại) và traffic (đếm tổng)
      → Ta phải tự tính ratio
    """
    traffic = metrics_data.get("traffic", 0)
    if traffic == 0:
        return 0.0
    total_errors = sum(metrics_data.get("error_breakdown", {}).values())
    return round((total_errors / traffic) * 100, 2)


# ---------------------------------------------------------------------------
# Hàm đánh giá 1 SLI
# ---------------------------------------------------------------------------
def evaluate_sli(sli_name: str, sli_config: dict, metrics_data: dict) -> dict:
    """
    So sánh giá trị thực tế với objective.

    Logic đánh giá:
      - latency, error_rate, cost: "actual < objective" → PASS
      - quality: "actual >= objective" → PASS (quality càng CAO càng tốt)

    Returns dict:
      {
        "sli_name": "latency_p95_ms",
        "objective": 3000,
        "actual": 1800,
        "passed": True,
        "margin": 1200,      # khoảng cách đến ngưỡng (dương = an toàn)
        "margin_pct": 40.0    # % margin so với objective
      }
    """
    objective = sli_config["objective"]

    # Lấy giá trị thực tế từ metrics
    metric_key = SLI_TO_METRIC.get(sli_name)
    if metric_key == "__computed_error_rate__":
        actual = compute_error_rate(metrics_data)
    else:
        actual = metrics_data.get(metric_key, 0)

    # Quality là SLI "higher is better" (càng cao càng tốt)
    # Còn lại là "lower is better" (càng thấp càng tốt)
    if sli_name == "quality_score_avg":
        passed = actual >= objective
        margin = actual - objective
    else:
        passed = actual <= objective
        margin = objective - actual

    margin_pct = round((margin / objective) * 100, 1) if objective else 0

    return {
        "sli_name": sli_name,
        "description": sli_config.get("description", ""),
        "objective": objective,
        "target_pct": sli_config.get("target", 0),
        "actual": actual,
        "unit": sli_config.get("unit", ""),
        "passed": passed,
        "margin": round(margin, 4),
        "margin_pct": margin_pct,
        "error_budget_minutes": sli_config.get("error_budget_minutes", 0),
    }


# ---------------------------------------------------------------------------
# Hàm in kết quả
# ---------------------------------------------------------------------------
def print_report(results: list[dict], config: dict) -> None:
    """In bảng compliance đẹp, dễ đọc."""

    window = config.get("window", "28d")
    service = config.get("service", "unknown")

    print("=" * 78)
    print(f"  SLO COMPLIANCE REPORT -- {service}")
    print(f"  Window: {window}")
    print("=" * 78)
    print()

    # Header
    print(f"{'SLI':<22} {'Objective':>10} {'Actual':>10} {'Status':>8} {'Margin':>10}")
    print("-" * 66)

    passed_count = 0
    for r in results:
        status = "[PASS]" if r["passed"] else "[FAIL]"
        if r["passed"]:
            passed_count += 1

        # Format theo unit
        if r["unit"] == "milliseconds":
            obj_str = f"{r['objective']}ms"
            act_str = f"{r['actual']:.0f}ms"
            margin_str = f"{r['margin']:.0f}ms"
        elif r["unit"] == "percent":
            obj_str = f"<{r['objective']}%"
            act_str = f"{r['actual']:.2f}%"
            margin_str = f"{r['margin']:.2f}%"
        elif r["unit"] == "usd":
            obj_str = f"${r['objective']}"
            act_str = f"${r['actual']:.4f}"
            margin_str = f"${r['margin']:.4f}"
        elif r["unit"] == "score_0_to_1":
            obj_str = f">={r['objective']}"
            act_str = f"{r['actual']:.2f}"
            margin_str = f"{r['margin']:.2f}"
        else:
            obj_str = str(r["objective"])
            act_str = str(r["actual"])
            margin_str = str(r["margin"])

        print(f"{r['sli_name']:<22} {obj_str:>10} {act_str:>10} {status:>8} {margin_str:>10}")

    print("-" * 66)
    total = len(results)
    print(f"\nResult: {passed_count}/{total} SLOs passing")

    if passed_count == total:
        print("[OK] All SLOs are within budget! Safe to deploy new features.")
    elif passed_count >= total - 1:
        print("[WARN] One SLO breached. Consider pausing feature work to investigate.")
    else:
        print("[CRITICAL] Multiple SLOs breached! Freeze deploys and focus on reliability.")

    # Error budget section
    print(f"\n{'-' * 40}")
    print("Error Budget Status:")
    for r in results:
        budget = r.get("error_budget_minutes", 0)
        if budget > 0:
            print(f"  {r['sli_name']}: {budget:.0f} min allowed in {window}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Check SLO compliance against live metrics")
    parser.add_argument("--offline", action="store_true", help="Use mock data (no app required)")
    args = parser.parse_args()

    config = load_slo_config()
    slis = config.get("slis", {})

    if not slis:
        print("No SLIs defined in config/slo.yaml")
        sys.exit(1)

    if args.offline:
        print("[OFFLINE MODE] Using mock metrics data\n")
        metrics_data = get_mock_metrics()
    else:
        metrics_data = fetch_metrics()

    results = []
    for sli_name, sli_config in slis.items():
        result = evaluate_sli(sli_name, sli_config, metrics_data)
        results.append(result)

    print_report(results, config)


if __name__ == "__main__":
    main()
