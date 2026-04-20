# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Nhom70-403-Day13
- [REPO_URL]: https://github.com/Wan1302/Nhom70-403-Day13
- [MEMBERS]:
  - Member A: 2A202600080 - Hồ Trần Đình Nguyên | Role: Logging & PII
  - Member B: 2A202600081 - Hồ Trọng Duy Quang | Role: Tracing & Enrichment
  - Member C: 2A202600057 - Hồ Đắc Toàn | Role: Load Test & Dashboard

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 50+ (verified via Langfuse dashboard; 50 traces generated locally across 5 load-test rounds including 10 rag_slow incident traces)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/screenshot_correlation_id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/screenshot_pii_redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/screenshot_trace_waterfall.jpg
- [TRACE_WATERFALL_EXPLANATION]: The trace waterfall shows two main spans: mock_rag.retrieve (~150ms normal, ~2500ms during rag_slow incident) and mock_llm.generate (~80ms). When rag_slow is injected, the retrieve span dominates total latency (~2660ms), proving the bottleneck is the RAG retrieval layer rather than LLM generation or schema validation.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/dashboard-6-panels.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2650ms |
| Error Rate | < 2% | 28d | 0.0% |
| Cost Budget | < $2.5/day | 1d | $0.012972 |
| Quality Score Avg | >= 0.75 | 28d | 0.90 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: config/alert_rules.yaml
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Sau khi bật incident `rag_slow`, request `/chat` vẫn trả về thành công nhưng latency tăng rõ rệt. Log `response_sent` của request kiểm thử có `latency_ms=2650`, cao hơn nhiều so với các request bình thường khoảng 150ms. Đây là dấu hiệu tail latency tăng do bước retrieval/RAG bị chậm, trong khi error rate vẫn là 0.0%.
- [ROOT_CAUSE_PROVED_BY]: Metrics cho thấy Latency P95 tăng lên 2650ms trong lần kiểm thử incident. Log evidence: `correlation_id=req-rag-slow-rca`, `event=response_sent`, `latency_ms=2650`, `session_id=s_incident_rca`, `feature=qa`, `model=claude-sonnet-4-5`. Trong code, scenario `rag_slow` bật `STATE["rag_slow"]`, làm `app/mock_rag.py::retrieve()` sleep 2.5 giây trước khi trả context, nên root cause nằm ở RAG retrieval span chứ không phải LLM generation hay schema validation.
- [FIX_ACTION]: Tắt incident bằng endpoint `/incidents/rag_slow/disable`, chạy lại request/load test để xác nhận latency quay về mức bình thường, sau đó kiểm tra lại `python scripts/validate_logs.py` để bảo đảm log schema, enrichment, correlation ID và PII redaction vẫn đạt.
- [PREVENTIVE_MEASURE]: Duy trì alert `high_latency_p95`, dashboard panel Latency P50/P95/P99, và runbook `docs/alerts.md#1-high-latency-p95`. Thêm timeout/fallback cho retrieval, giới hạn prompt/context dài, theo dõi Langfuse trace waterfall để tách riêng RAG span và LLM span khi latency tăng.

---

## 5. Individual Contributions & Evidence

### 2A202600080 - Hồ Trần Đình Nguyên
- [TASKS_COMPLETED]: Implement Correlation ID middleware, PII scrubbing processor, bổ sung PII patterns (passport, địa chỉ VN)
- [EVIDENCE_LINK]: https://github.com/Wan1302/Nhom70-403-Day13/commit/0ffe61a

### 2A202600081 - Hồ Trọng Duy Quang
- [TASKS_COMPLETED]: Implemented `/chat` log enrichment by binding `user_id_hash`, `session_id`, `feature`, `model`, and `env` into structlog context variables; verified that API logs contain correlation context without exposing raw user identifiers; finalized SLO targets in `config/slo.yaml`; reviewed and expanded alert rules in `config/alert_rules.yaml`; updated runbook details in `docs/alerts.md`.
- [EVIDENCE_LINK]: https://github.com/Wan1302/Nhom70-403-Day13/commit/cff3ba7a55c4ac5097a7011ef6a545bb19f2f855

### 2A202600057 - Hồ Đắc Toàn
- [TASKS_COMPLETED]: (1) Added load_dotenv() to app/main.py to ensure Langfuse keys are loaded from .env, enabling tracing_enabled=true. (2) Added quality_score field to response_sent log event so Panel 6 of the dashboard has data. (3) Ran load_test.py (--concurrency 5, 3 rounds = 30 baseline requests) to generate sufficient log data and Langfuse traces. (4) Injected and analysed rag_slow incident: confirmed latency spike P95 150ms → 2651ms via metrics, verified error rate stayed 0%, then disabled incident and confirmed recovery. (5) Built scripts/build_dashboard.py — a 6-panel matplotlib dashboard (Latency P50/P95/P99, Traffic, Error Rate, Cost, Tokens In/Out, Quality Score) with SLO threshold lines; output saved to docs/dashboard-6-panels.png. (6) Ran python scripts/validate_logs.py → 100/100 with all 4 checks PASSED. (7) Completed blueprint-template.md: filled TOTAL_TRACES_COUNT, EVIDENCE_TRACE_WATERFALL_SCREENSHOT, TRACE_WATERFALL_EXPLANATION, and Member C contribution section.
- [EVIDENCE_LINK]: https://github.com/Wan1302/Nhom70-403-Day13/commit/a685db8

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: scripts/build_dashboard.py — custom 6-panel dark-theme matplotlib dashboard auto-generated from logs.jsonl with SLO threshold lines per panel. Runs as a standalone script (python scripts/build_dashboard.py) requiring no external monitoring stack. Evidence: docs/dashboard-6-panels.png
