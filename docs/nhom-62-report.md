# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 62
- [REPO_URL]: https://github.com/dokhiem2k4/Lab13-Observability
- [MEMBERS]:
  - Member A: [Phan Thanh Sang] | Role: Logging & PII
  - Member B: [Trần Tiến Dũng] | Role: Tracing & Enrichment
  - Member C: [Trần Đình Minh Vương] | Role: SLO & Alerts
  - Member D: [Đỗ Minh Khiêm] | Role: Load Test & Dashboard
  - Member E: [Ngô Hải Văn] | Role: Demo & Report

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
#### Enrichment & Trace Waterfall
- [Kết quả validate log của enrichment pass]: [Log Enrichment Pass](./LOG_ENRICHMENT_PASS.jpg)
- [Log có ngữ cảnh để truy vết user]: [Log Context](./LOG_CONTEXT.jpg)

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
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
