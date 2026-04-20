# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Lab13-Observability
- [REPO_URL]: https://github.com/dokhiem2k4/Lab13-Observability
- [MEMBERS]:
  - Member A: Sang | Role: Correlation ID
  - Member B: Van | Role: Log Enrichment
  - Member C: Vuong | Role: Logging & PII
  - Member D: Khiem | Role: Tracing, Metrics, and Incident Validation
  - Member E: Dung | Role: Dashboard, SLO/Alerts, Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 15
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: data/logs.jsonl — every API log contains `"correlation_id": "req-<8hex>"` (e.g. `req-bce510a0`)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: evidence\EVIDENCE_VALIDATE_LOGS_PII_PASS.png — validate_logs.py confirmed 0 PII leaks
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Langfuse traces visible when LANGFUSE_PUBLIC_KEY is configured
- [TRACE_WATERFALL_EXPLANATION]: The `LabAgent.run()` span wraps two child operations: `retrieve()` (RAG lookup) and `FakeLLM.generate()` (LLM call). Under normal conditions the RAG span takes ~100ms. Under the `rag_slow` incident the RAG span stretches to 2–5s — visible as the dominant span in the waterfall — proving that retrieval, not the LLM, is the bottleneck.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: config/grafana_dashboard.json — 6-panel Grafana dashboard (import via Grafana UI → Dashboards → Import JSON). Panels: (1) Latency P50/P95/P99, (2) Traffic Request Count, (3) Error Rate gauge, (4) Cost Over Time, (5) Tokens In/Out, (6) Quality Score gauge.
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 156ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0317 (15 requests) |
| Quality Score | ≥ 0.75 | 28d | 0.80 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: config/alert_rules.yaml — 4 rules: high_latency_p95 (P2, 30m window), high_error_rate (P1, 5m window), cost_budget_spike (P2, 15m window), quality_score_degradation (P3, 15m window). Each rule links to runbook and SLO.
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#2-high-error-rate

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency climbs from ~156ms baseline to >2000ms within minutes of `POST /incidents/rag_slow/enable`. `/metrics` shows latency_p95 spike. Quality score may dip if retrieval timeouts return empty docs.
- [ROOT_CAUSE_PROVED_BY]: Langfuse trace shows `retrieve()` span duration jumps from ~100ms to 2000–5000ms. Log line in data/logs.jsonl: `"event":"response_sent", "latency_ms": 4800` confirms the bottleneck is in the RAG span, not the LLM span. `GET /health` shows `"rag_slow": true`.
- [FIX_ACTION]: `POST http://127.0.0.1:8000/incidents/rag_slow/disable` — restores baseline latency immediately. Re-check `/metrics` to confirm latency_p95 returns to <200ms.
- [PREVENTIVE_MEASURE]: Alert `high_latency_p95` in config/alert_rules.yaml fires at >5000ms for 30m so on-call is paged before SLO breach. Add RAG-specific span timeout (3s hard cap) with fallback to empty-docs path to prevent cascading latency impact on the LLM span.

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

### Dung (Nguyễn Hải Văn)
- [TASKS_COMPLETED]: Dashboard spec (docs/dashboard-spec.md) + 6-panel Grafana JSON (config/grafana_dashboard.json). SLO review with current observed values and rationale (config/slo.yaml). Alert rules completed with 4th rule + rationale + SLO links (config/alert_rules.yaml). Full runbook with diagnostic steps for all 4 alerts (docs/alerts.md). Python 3.9 compatibility fix for schemas.py (Optional[str] instead of str|None). validate_logs.py: 100/100 score. Blueprint report (this file). Demo script (docs/demo-script.md).
- [EVIDENCE_LINK]: https://github.com/dokhiem2k4/Lab13-Observability/pull/1 (branch: feature/van-dashboard-slo-alerts-report)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Added `quality_score_degradation` alert rule (P3) to catch LLM answer quality drops early — routes triage toward RAG health and prompt review before users report issues. See config/alert_rules.yaml#quality_score_degradation.
- [BONUS_AUDIT_LOGS]: PII scrubbing extended with Vietnamese address patterns, passport numbers, and recursive `scrub_any()` function that deep-scrubs nested dicts/lists in all log payloads. See app/pii.py.
- [BONUS_CUSTOM_METRIC]: `quality_avg` is tracked as a 4th "golden signal" alongside standard RED metrics (Rate/Error/Duration) and exposed via `/metrics`. Specific to LLM workloads. See app/metrics.py and app/agent.py#_heuristic_quality.
