# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Nhóm 9 — Day 13 Observability

- [REPO_URL]: [Link GitHub](https://github.com/DangMinh21/Lab13-Observability)

- [MEMBERS]:
  - Member A: Nguyễn Quang Tùng | Role: Correlation ID & Incident Debug
  - Member B: Nguyễn Thị Quỳnh Trang | Role: Logging & PII Scrubbing
  - Member C: Đặng Văn Minh | Role: Tracing (Langfuse) + SLO + Alerts
  - Member D: Đồng Văn Thịnh | Role: Dashboard + Docs + Report .

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- TOTAL_TRACES_COUNT: 10
- PII_LEAKS_FOUND: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- EVIDENCE_CORRELATION_ID_SCREENSHOT: docs/screenshots/correlation-id-log.png
- EVIDENCE_PII_REDACTION_SCREENSHOT: docs/screenshots/pii-redaction-log.png
- EVIDENCE_TRACE_WATERFALL_SCREENSHOT: docs/screenshots/langfuse-trace-waterfall.png
- TRACE_WATERFALL_EXPLANATION: Span 'retrieve' thể hiện quá trình truy xuất dữ liệu từ vector database; là chìa khóa để chẩn đoán sự cố rag_slow.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- SLO_TABLE:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 165ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0185 |

### 3.3
- DASHBOARD_6_PANELS_SCREENSHOT: docs/screenshots/dashboard-6-panels.png
- ALERT_RULES_SCREENSHOT: docs/screenshots/alert-rules.png
- SAMPLE_RUNBOOK_LINK: docs/alerts.md#4-quality-degradation

---

## 4. Incident Response (Group)
- SCENARIO_NAME: rag_slow
- SYMPTOMS_OBSERVED: Latency P95 tăng vọt từ ~165ms lên > 3000ms, vi phạm SLO.
- ROOT_CAUSE_PROVED_BY: Langfuse trace waterfall cho thấy span 'retrieve' chiếm 85% tổng latency.
- FIX_ACTION: POST /incidents/rag_slow/disable để đưa hệ thống về trạng thái bình thường.
- PREVENTIVE_MEASURE: Thiết lập alert rule 'high_latency_p95' trong alert_rules.yaml để cảnh báo sớm.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Đồng Văn Thịnh
- [TASKS_COMPLETED]: Xây dựng terminal dashboard 6 panels kết nối với endpoint /metrics. Điều phối file blueprint-template.md và quản lý evidence. Thiết lập thư mục docs/screenshots và checklist pass demo.
- [EVIDENCE_LINK]: https://github.com/DangMinh21/Lab13-Observability/pull/4

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
