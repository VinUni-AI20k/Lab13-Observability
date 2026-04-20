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
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/screenshot_correlation_id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/screenshot_pii_redaction.png
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
- [ALERT_RULES_SCREENSHOT]: config/alert_rules.yaml
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: (e.g., rag_slow)
- [SYMPTOMS_OBSERVED]: 
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: 
- [PREVENTIVE_MEASURE]: 

---

## 5. Individual Contributions & Evidence

### 2A202600080 - Hồ Trần Đình Nguyên
- [TASKS_COMPLETED]: Implement Correlation ID middleware, PII scrubbing processor, bổ sung PII patterns (passport, địa chỉ VN)
- [EVIDENCE_LINK]: https://github.com/Wan1302/Nhom70-403-Day13/commit/0ffe61a

### 2A202600081 - Hồ Trọng Duy Quang
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### 2A202600057 - Hồ Đắc Toàn
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
