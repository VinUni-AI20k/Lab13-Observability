# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Group [TODO: Fill group number]
- [REPO_URL]: https://github.com/PhamXuanKhang/Lab13-Observability
- [MEMBERS]:
  - Member A: Khang | Role: Logging & PII + Blueprint Lead
  - Member B: Duy | Role: Tracing & Tags + SLO & Alerts
  - Member C: Thức | Role: Load Test & Incident Injection
  - Member D: Thư | Role: Dashboard & Evidence

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/screenshots/logs-correlation-id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/screenshots/pii-redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/screenshots/trace-waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: The LabAgent.run span shows the full request lifecycle: starts with retrieve() for RAG docs (~100-200ms), followed by FakeLLM.generate() for response generation (~50-100ms). The trace captures model name, user_id hash, session_id, and feature tag for filtering.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/screenshots/dashboard-6-panels.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 2000ms | 28d | [TODO: measure] |
| Error Rate | < 5% | 28d | [TODO: measure] |
| Cost per 1k | < $0.50 | 28d | [TODO: measure] |
| Cost Budget | < $2.5/day | 1d | [TODO: measure] |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/screenshots/alert-rules.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#4-rag-slow

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency exceeded 2000ms SLO threshold; Langfuse traces show retrieval span consistently > 2500ms
- [ROOT_CAUSE_PROVED_BY]: Langfuse trace waterfall shows mock_rag.retrieve() has a 2.5s sleep injected by `inject_incident.py --scenario rag_slow` (Trace ID: [TODO: fill actual trace ID from Langfuse])
- [FIX_ACTION]: Identify and remove the injected sleep; add timeout wrapper around RAG retrieval calls
- [PREVENTIVE_MEASURE]: The rag_slow alert rule in config/alert_rules.yaml fires when P95 > 2000ms; runbook at docs/alerts.md#4-rag-slow guides on-call response 

---

## 5. Individual Contributions & Evidence

### Khang
- [TASKS_COMPLETED]: Implemented correlation ID in middleware.py (clear_contextvars, generate req-hex ID, bind to structlog, add response headers), activated PII scrubbing in logging_config.py, added passport and Vietnamese address PII patterns in pii.py, led blueprint report
- [EVIDENCE_LINK]: https://github.com/PhamXuanKhang/Lab13-Observability/commit/57d245c, https://github.com/PhamXuanKhang/Lab13-Observability/commit/3445fd8

### Duy
- [TASKS_COMPLETED]: Verified Langfuse tracing setup in tracing.py, confirmed @observe() decorator with trace metadata in agent.py, set SLO targets (latency 2000ms, error rate 5%, cost $0.50/1k) in slo.yaml, expanded alert rules to 4 rules (added rag_slow), updated runbook in alerts.md
- [EVIDENCE_LINK]: https://github.com/PhamXuanKhang/Lab13-Observability/commit/ae2dee7, https://github.com/PhamXuanKhang/Lab13-Observability/commit/1fe01d9 

### Thức
- [TASKS_COMPLETED]: Enhanced load_test.py with --requests and --concurrency arguments plus summary output (total, success, errors, avg latency), verified inject_incident.py supports all 3 scenarios (rag_slow, tool_fail, cost_spike)
- [EVIDENCE_LINK]: https://github.com/PhamXuanKhang/Lab13-Observability/commit/458a44c, https://github.com/PhamXuanKhang/Lab13-Observability/commit/2d3121e 

### Thư
- [TASKS_COMPLETED]: Completed dashboard-spec.md with all 6 panels (Latency P95, Error Rate, Token Usage/Cost, Active Requests, Trace Count, Quality Score) and SLO thresholds, filled grading-evidence.md with validation structure and screenshot paths, led incident response documentation
- [EVIDENCE_LINK]: https://github.com/PhamXuanKhang/Lab13-Observability/commit/b969a1b, https://github.com/PhamXuanKhang/Lab13-Observability/commit/c53f1de 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
