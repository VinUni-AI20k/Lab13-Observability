"""
Unit Tests for SLO & Alert Logic — Member C
=============================================
Tests này kiểm tra logic đánh giá SLO và alert mà không cần chạy app.

CÁCH CHẠY:
  python -m pytest tests/test_slo_alerts.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

# Thêm project root vào path để import scripts
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.check_slo import compute_error_rate, evaluate_sli, load_slo_config
from scripts.evaluate_alerts import parse_and_evaluate


# ==========================================================================
# Test fixtures (dữ liệu test dùng chung)
# ==========================================================================

@pytest.fixture
def healthy_metrics() -> dict:
    """Metrics khi hệ thống khỏe mạnh — mọi SLO nên PASS."""
    return {
        "traffic": 50,
        "latency_p50": 400,
        "latency_p95": 1800,
        "latency_p99": 2500,
        "avg_cost_usd": 0.0008,
        "total_cost_usd": 0.04,
        "tokens_in_total": 6000,
        "tokens_out_total": 4000,
        "error_breakdown": {},
        "quality_avg": 0.82,
    }


@pytest.fixture
def degraded_metrics() -> dict:
    """Metrics khi hệ thống có vấn đề — một số SLO sẽ FAIL."""
    return {
        "traffic": 50,
        "latency_p50": 2000,
        "latency_p95": 6500,       # Vượt SLO 3000ms
        "latency_p99": 9000,
        "avg_cost_usd": 0.005,
        "total_cost_usd": 0.25,
        "tokens_in_total": 60000,   # Token rất cao
        "tokens_out_total": 40000,
        "error_breakdown": {"RuntimeError": 5},  # 10% error rate
        "quality_avg": 0.45,        # Quality thấp
    }


# ==========================================================================
# Tests cho compute_error_rate
# ==========================================================================

class TestComputeErrorRate:
    """
    Test tính error rate.
    Error rate = tổng errors / traffic * 100
    """

    def test_no_traffic(self) -> None:
        """Traffic = 0 → error rate = 0 (tránh chia cho 0)."""
        result = compute_error_rate({"traffic": 0, "error_breakdown": {}})
        assert result == 0.0

    def test_no_errors(self, healthy_metrics: dict) -> None:
        """Không có lỗi → error rate = 0%."""
        result = compute_error_rate(healthy_metrics)
        assert result == 0.0

    def test_some_errors(self) -> None:
        """2 errors / 50 traffic = 4%."""
        metrics = {"traffic": 50, "error_breakdown": {"TimeoutError": 2}}
        result = compute_error_rate(metrics)
        assert result == 4.0

    def test_mixed_errors(self) -> None:
        """Nhiều loại lỗi: 3 + 2 = 5 / 100 = 5%."""
        metrics = {
            "traffic": 100,
            "error_breakdown": {"RuntimeError": 3, "TimeoutError": 2},
        }
        result = compute_error_rate(metrics)
        assert result == 5.0


# ==========================================================================
# Tests cho evaluate_sli (SLO compliance check)
# ==========================================================================

class TestEvaluateSli:
    """
    Test đánh giá SLI vs SLO objective.
    """

    def test_latency_passing(self, healthy_metrics: dict) -> None:
        """P95 = 1800ms < objective 3000ms → PASS."""
        sli_config = {"objective": 3000, "target": 99.5, "unit": "milliseconds"}
        result = evaluate_sli("latency_p95_ms", sli_config, healthy_metrics)
        assert result["passed"] is True
        assert result["actual"] == 1800
        assert result["margin"] == 1200  # 3000 - 1800

    def test_latency_failing(self, degraded_metrics: dict) -> None:
        """P95 = 6500ms > objective 3000ms → FAIL."""
        sli_config = {"objective": 3000, "target": 99.5, "unit": "milliseconds"}
        result = evaluate_sli("latency_p95_ms", sli_config, degraded_metrics)
        assert result["passed"] is False
        assert result["actual"] == 6500

    def test_error_rate_passing(self, healthy_metrics: dict) -> None:
        """Error rate = 0% < objective 2% → PASS."""
        sli_config = {"objective": 2, "target": 99.0, "unit": "percent"}
        result = evaluate_sli("error_rate_pct", sli_config, healthy_metrics)
        assert result["passed"] is True

    def test_error_rate_failing(self, degraded_metrics: dict) -> None:
        """Error rate = 10% > objective 2% → FAIL."""
        sli_config = {"objective": 2, "target": 99.0, "unit": "percent"}
        result = evaluate_sli("error_rate_pct", sli_config, degraded_metrics)
        assert result["passed"] is False
        assert result["actual"] == 10.0

    def test_quality_passing(self, healthy_metrics: dict) -> None:
        """Quality = 0.82 >= objective 0.75 → PASS (higher is better)."""
        sli_config = {"objective": 0.75, "target": 95.0, "unit": "score_0_to_1"}
        result = evaluate_sli("quality_score_avg", sli_config, healthy_metrics)
        assert result["passed"] is True
        assert result["margin"] == pytest.approx(0.07, abs=0.01)

    def test_quality_failing(self, degraded_metrics: dict) -> None:
        """Quality = 0.45 < objective 0.75 → FAIL."""
        sli_config = {"objective": 0.75, "target": 95.0, "unit": "score_0_to_1"}
        result = evaluate_sli("quality_score_avg", sli_config, degraded_metrics)
        assert result["passed"] is False

    def test_cost_passing(self, healthy_metrics: dict) -> None:
        """Cost = $0.04 < objective $2.5 → PASS."""
        sli_config = {"objective": 2.5, "target": 100.0, "unit": "usd"}
        result = evaluate_sli("daily_cost_usd", sli_config, healthy_metrics)
        assert result["passed"] is True


# ==========================================================================
# Tests cho parse_and_evaluate (alert rules)
# ==========================================================================

class TestParseAndEvaluateAlerts:
    """
    Test parse alert condition string và evaluate.
    """

    def test_latency_ok(self, healthy_metrics: dict) -> None:
        """P95 = 1800 < 5000 → OK (không firing)."""
        firing, _ = parse_and_evaluate("latency_p95_ms > 5000 for 30m", healthy_metrics)
        assert firing is False

    def test_latency_firing(self, degraded_metrics: dict) -> None:
        """P95 = 6500 > 5000 → FIRING."""
        firing, _ = parse_and_evaluate("latency_p95_ms > 5000 for 30m", degraded_metrics)
        assert firing is True

    def test_error_rate_ok(self, healthy_metrics: dict) -> None:
        """Error rate = 0% < 5% → OK."""
        firing, _ = parse_and_evaluate("error_rate_pct > 5 for 5m", healthy_metrics)
        assert firing is False

    def test_error_rate_firing(self, degraded_metrics: dict) -> None:
        """Error rate = 10% > 5% → FIRING."""
        firing, _ = parse_and_evaluate("error_rate_pct > 5 for 5m", degraded_metrics)
        assert firing is True

    def test_quality_ok(self, healthy_metrics: dict) -> None:
        """Quality = 0.82 > 0.6 → OK (not below threshold)."""
        firing, _ = parse_and_evaluate("quality_score_avg < 0.6 for 15m", healthy_metrics)
        assert firing is False

    def test_quality_firing(self, degraded_metrics: dict) -> None:
        """Quality = 0.45 < 0.6 → FIRING."""
        firing, _ = parse_and_evaluate("quality_score_avg < 0.6 for 15m", degraded_metrics)
        assert firing is True

    def test_token_budget_ok(self, healthy_metrics: dict) -> None:
        """Tokens = 6000 < 50000 → OK."""
        firing, _ = parse_and_evaluate("tokens_in_total > 50000 per hour", healthy_metrics)
        assert firing is False

    def test_token_budget_firing(self, degraded_metrics: dict) -> None:
        """Tokens = 60000 > 50000 → FIRING."""
        firing, _ = parse_and_evaluate("tokens_in_total > 50000 per hour", degraded_metrics)
        assert firing is True

    def test_invalid_condition(self, healthy_metrics: dict) -> None:
        """Condition không hợp lệ → không firing, trả lời lỗi."""
        firing, explanation = parse_and_evaluate("???invalid", healthy_metrics)
        assert firing is False
        assert "Cannot parse" in explanation


# ==========================================================================
# Tests cho SLO config file integrity
# ==========================================================================

class TestSloConfigIntegrity:
    """Test file config/slo.yaml có đúng format không."""

    def test_slo_file_exists(self) -> None:
        assert Path("config/slo.yaml").exists(), "config/slo.yaml must exist"

    def test_slo_has_required_fields(self) -> None:
        config = load_slo_config()
        assert "service" in config
        assert "window" in config
        assert "slis" in config

    def test_each_sli_has_objective_and_target(self) -> None:
        config = load_slo_config()
        for name, sli in config["slis"].items():
            assert "objective" in sli, f"{name} missing 'objective'"
            assert "target" in sli, f"{name} missing 'target'"

    def test_alert_file_exists(self) -> None:
        assert Path("config/alert_rules.yaml").exists()

    def test_at_least_3_alerts_with_runbook(self) -> None:
        """Rubric yêu cầu ít nhất 3 alert rules có runbook link."""
        with Path("config/alert_rules.yaml").open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        alerts = data.get("alerts", [])
        alerts_with_runbook = [a for a in alerts if a.get("runbook")]
        assert len(alerts_with_runbook) >= 3, f"Need >= 3 alerts with runbook, got {len(alerts_with_runbook)}"
