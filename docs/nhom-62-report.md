# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 62
- [REPO_URL]: https://github.com/dokhiem2k4/Lab13-Observability
- [MEM  - Mem  
  - Member A: [Phan Thanh Sang] | Role: Correlation ID
  - Member B: [Trần Tiến Dũng] | Role: Log Enrichment
  - Member C: [Trần Đình Minh Vương] | Role: Logging & PII
  - Member D: [Đỗ Minh Khiêm] | Role: Tracing + Incident + Metrics
  - Member E: [Ngô Hải Văn] | Role: Dashboard + SLO/Alerts + Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Correlation ID in Logs](./EVIDENCE_CORRELATION_ID_SCREENSHOT.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [PII Redaction in Logs](./EVIDENCE_PII_REDACTION_SCREENSHOT.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $2.5/day | 1d | |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: (e.g., rag_slow)
- [SYMPTOMS_OBSERVED]: 
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: 
- [PREVENTIVE_MEASURE]: 

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: Phụ trách phần Logging, đảm bảo correlation_id được gắn vào logs và thực hiện redaction các thông tin nhạy cảm.
- [EVIDENCE_LINK]: [PR #1](https://github.com/dokhiem2k4/Lab13-Observability/pull/1)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
### Trần Đình Minh Vương
- [TASKS_COMPLETED]: |
  1. Bật `scrub_event` trong structlog pipeline (`app/logging_config.py`), đảm bảo mọi log record đi qua PII redaction trước khi ghi ra file.
  2. Bổ sung pattern PII còn thiếu trong `app/pii.py`: `passport` (hộ chiếu dạng B1234567, AB1234567) và `address_vn` (từ khóa địa chỉ Việt Nam: đường, phường, xã, quận, thôn, ấp, hẻm, ngõ…).
  3. Fix thứ tự pattern `PII_PATTERNS` để tránh `phone_vn` nhận nhầm CCCD 12 chữ số (commit `eb88b78`).
  4. Kiểm tra `data/logs.jsonl` — log đã sạch, không còn lộ email, phone, CCCD, credit card; các giá trị nhạy cảm được thay bằng `[REDACTED_...]`.
  5. Chạy `python scripts/validate_logs.py` — phần PII scrubbing PASS (0 leak phát hiện).
- [EVIDENCE_LINK]: [PR #7](https://github.com/dokhiem2k4/Lab13-Observability/pull/7)

### [MEMBER_D_NAME]
### Đỗ Minh Khiêm
- [TASKS_COMPLETED]: |
  1. Tích hợp Langfuse tracing cho endpoint `/chat` ([app/tracing.py](../app/tracing.py), [app/agent.py](../app/agent.py)): tạo span cho request chính, RAG retrieval và LLM generation; xác thực trace hiển thị đầy đủ trên Langfuse UI.
  2. Xây dựng metrics pipeline ([app/metrics.py](../app/metrics.py)): đếm traffic, tính latency P50/P95/P99, tổng hợp cost/tokens, error_breakdown, quality_avg; expose qua `GET /metrics`.
  3. Hiện thực 3 kịch bản incident injection ([app/incidents.py](../app/incidents.py)): `rag_slow`, `tool_fail`, `cost_spike` kèm endpoint `POST /incidents/{name}/enable|disable`.
  4. Chạy thử các incident, thu thập bằng chứng trace waterfall + /metrics trước/sau để chứng minh tác động lên P95 latency, error rate và cost.
  5. Viết phần Incident Response (Section 4) và Trace Waterfall Explanation trong report.
- [EVIDENCE_LINK]: [PR tracing + metrics + incidents](https://github.com/dokhiem2k4/Lab13-Observability/pull/2)

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

NK]: 
Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
