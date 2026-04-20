from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "docs" / "blueprint-template.md"
RUNBOOK = ROOT / "docs" / "demo-runbook.md"
EVIDENCE_README = ROOT / "docs" / "evidence" / "README.md"


def test_blueprint_template_is_prepopulated_with_verified_values() -> None:
    content = BLUEPRINT.read_text(encoding="utf-8")

    assert "- [VALIDATE_LOGS_FINAL_SCORE]: 100/100" in content
    assert "- [TOTAL_TRACES_COUNT]: 85" in content
    assert "- [PII_LEAKS_FOUND]: 0" in content
    assert "- [SCENARIO_NAME]: rag_slow" in content
    assert "- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95" in content
    assert "Trần Đặng Quang Huy" in content
    assert "Phạm Đan Kha" in content
    assert "Nguyễn Duy Hiếu" in content
    assert "Vũ Đức Kiên" in content
    assert "TBD_" not in content


def test_demo_runbook_exists_and_covers_baseline_and_incident_flow() -> None:
    content = RUNBOOK.read_text(encoding="utf-8")

    assert "python -m pytest -q" in content
    assert "python scripts/validate_logs.py" in content
    assert "uvicorn app.main:app --reload" in content
    assert "python scripts/load_test.py --concurrency 5" in content
    assert "rag_slow" in content
    assert "Langfuse" in content
    assert "/metrics" in content


def test_evidence_readme_lists_required_artifacts() -> None:
    content = EVIDENCE_README.read_text(encoding="utf-8")

    assert "correlation-id-log.png" in content
    assert "pii-redaction-log.png" in content
    assert "trace-waterfall.png" in content
    assert "dashboard-6-panels.png" in content
    assert "alert-rules.png" in content
