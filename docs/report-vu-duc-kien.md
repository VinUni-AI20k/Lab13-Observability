# Day 13 Observability Lab Report - Vu Duc Kien

> Individual split report generated from `docs/blueprint-template.md` for Vũ Đức Kiên.

## 1. Team Metadata
- **GROUP_NAME**: Huy-Kha-Hieu-Kien
- **REPO_URL**: https://github.com/khadpham/Lab13-Observability
- **MEMBERS**:
  - Member A: Trần Đặng Quang Huy | Role: Logging, PII, final integration
  - Member B: Phạm Đan Kha | Role: Tracing, enrichment, trace walkthrough
  - Member C: Nguyễn Duy Hiếu | Role: SLOs, alerts, incident reasoning
  - Member D: Vũ Đức Kiên | Role: Load test, dashboard, evidence capture

---

## 2. Group Performance (Auto-Verified)
- **VALIDATE_LOGS_FINAL_SCORE**: 100/100
- **TOTAL_TRACES_COUNT**: 85
- **PII_LEAKS_FOUND**: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- **EVIDENCE_CORRELATION_ID_SCREENSHOT**: docs/evidence/correlation-id-log.png
- **EVIDENCE_PII_REDACTION_SCREENSHOT**: docs/evidence/pii-redaction-log.png
- **EVIDENCE_TRACE_WATERFALL_SCREENSHOT**: docs/evidence/trace-waterfall.png
- **TRACE_WATERFALL_EXPLANATION**: The slowest span should be the retrieval path during `rag_slow`, proving the incident affects tail latency before the answer is returned.

### 3.2 Dashboard & SLOs
- **DASHBOARD_6_PANELS_SCREENSHOT**: docs/evidence/dashboard-6-panels.png
**SLO_TABLE**:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | &lt; 3000ms | 28d | 150ms |
| Error Rate | &lt; 2% | 28d | 0.0% |
| Cost Budget | &lt; $2.5/day | 1d | $0.0018 avg/request |

### 3.3 Alerts & Runbook
- **ALERT_RULES_SCREENSHOT**: docs/evidence/alert-rules.png
- **SAMPLE_RUNBOOK_LINK**: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- **SCENARIO_NAME**: rag_slow
- **SYMPTOMS_OBSERVED**: Latency P95 rises, the dashboard tail-latency panel spikes, and slow requests become obvious in Langfuse.
- **ROOT_CAUSE_PROVED_BY**: Langfuse Trace ID `473e676cb3070b357fbb120c294b5edc` plus correlated log lines for `correlation_id=req-2f38c0a0`.
- **FIX_ACTION**: Disable the injected incident after the demo and rerun clean traffic to show latency recovery.
- **PREVENTIVE_MEASURE**: Add alerting on tail latency and review retrieval latency in traces before shipping retrieval changes.

---

## 5. Individual Contribution & Evidence

### Vũ Đức Kiên
- **TASKS_COMPLETED**: Ran load tests, prepared the dashboard view, captured evidence requirements, and supported incident rehearsal for `rag_slow`.
- **EVIDENCE_LINK**: Member-specific commit or PR link should be attached after the team push; no separate link was present in the local repository history.

---

## 6. Bonus Items (Optional)
- **BONUS_COST_OPTIMIZATION**: Not claimed in this submission. The team did not run a before/after cost-optimization experiment, so no savings figure is reported.
- **BONUS_AUDIT_LOGS**: Not claimed in this submission. `audit.jsonl` is listed as an optional output in the template repo, but a separate audit-log pipeline is not currently implemented.
- **BONUS_CUSTOM_METRIC**: Claimed. The app exposes `quality_avg` from `app/metrics.py` as a custom heuristic quality metric, and this metric is visualized on the dashboard as the "Quality Proxy" panel.
