# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Lab13-Observability-Team
- [REPO_URL]: [Insert Repo URL here]
- [MEMBERS]:
  - Member A: Nguyễn Bằng Anh - 2A202600136 | Role: dashboard + evidence + blueprint + demo lead
  - Member B: Đỗ Thị Thùy Trang - 2A202600041 | Role: SLO + alerts
  - Member C: Nguyễn Thị Thanh Huyền - 2A202600211 | Role: tracing + tags
  - Member D: Nguyễn Quốc Nam - 2A202600201 | Role: logging + PII
  - Member E: Bùi Trọng Anh - 2A202600010 | Role: load test + incident injection

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 20
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
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
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency spikes heavily from ~1000ms to > 10000ms. End-users experience long waits for responses.
- [ROOT_CAUSE_PROVED_BY]: In Langfuse traces, the `rag_retrieval` span takes > 10000ms compared to the baseline < 500ms. Alert rules trigger for `HighLatency`.
- [FIX_ACTION]: Investigate the RAG retrieval service, ensure database indexes are optimized, and increase timeout constraints or implement a circuit breaker. Disable the incident using `scripts/inject_incident.py --scenario rag_slow --disable`.
- [PREVENTIVE_MEASURE]: Implement stricter timeouts for downstream services and provide fallback caching mechanisms.

---

## 5. Individual Contributions & Evidence

### Nguyễn Bằng Anh - 2A202600136
- [TASKS_COMPLETED]: Created the blueprint report, set up the initial repository, generated dashboard specification, and orchestrated demo.
- [EVIDENCE_LINK]: [Link to commit or PR]

### Đỗ Thị Thùy Trang - 2A202600041
- [TASKS_COMPLETED]: Configured `alert_rules.yaml` and documented the alert runbooks in `alerts.md`.
- [EVIDENCE_LINK]: [Link to commit or PR]

### Nguyễn Thị Thanh Huyền - 2A202600211
- [TASKS_COMPLETED]: Added log enrichment in `main.py` and validated traces in Langfuse.
- [EVIDENCE_LINK]: [Link to commit or PR]

### Nguyễn Quốc Nam - 2A202600201
- [TASKS_COMPLETED]: Implemented Correlation ID Middleware and added regex patterns for PII scrubbing.
- [EVIDENCE_LINK]: [Link to commit or PR]

### Bùi Trọng Anh - 2A202600010
- [TASKS_COMPLETED]: Executed load testing scripts and managed incident injection to test alerts.
- [EVIDENCE_LINK]: [Link to commit or PR]

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
