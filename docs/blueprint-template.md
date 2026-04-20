# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: Sang | Role: Correlation ID
  - Member B: Van | Role: Log Enrichment
  - Member C: Vuong | Role: Logging & PII
  - Member D: Khiem | Role: Tracing, Metrics, and Incident Validation
  - Member E: Dung | Role: Dashboard, SLO/Alerts, Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: evidence\EVIDENCE_VALIDATE_LOGS_PII_PASS.png
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

### Sang
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### Van
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Vuong
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Khiem
- [TASKS_COMPLETED]: Verified Langfuse tracing, generated request traffic with `python scripts/load_test.py --concurrency 5`, validated `/metrics` output, triggered and observed at least one incident scenario such as `rag_slow`, and captured trace and incident evidence for the report.
- [EVIDENCE_LINK]: (Link to Khiem commit/PR, Langfuse trace screenshot, metrics screenshot, and incident proof)

### Dung
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
