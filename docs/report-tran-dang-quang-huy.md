# Day 13 Observability Lab Report - Trần Đặng Quang Huy

> Individual split report generated from `docs/blueprint-template.md` for Trần Đặng Quang Huy.

## 1. Team Metadata

- Group Name: 72
- Repository: https://github.com/khadpham/Lab13-Observability
- Members:
  - Member A: Trần Đặng Quang Huy | Role: Logging, PII, final integration
  - Member B: Phạm Đan Kha | Role: Tracing, enrichment, trace walkthrough
  - Member C: Nguyễn Duy Hiếu | Role: SLOs, alerts, incident reasoning
  - Member D: Vũ Đức Kiên | Role: Load test, dashboard, evidence capture

---

## 2. Group Performance (Auto-Verified)

- Validate Logs Final Score: 100/100
- Total Traces Count: 85
- PII Leaks Found: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing

- Correlation ID Screenshot: `docs/evidence/correlation-id-log.png`
- PII Redaction Screenshot: `docs/evidence/pii-redaction-log.png`
- Trace Waterfall Screenshot: `docs/evidence/trace-waterfall.png`
- Trace Waterfall Explanation: The slowest span should be the retrieval path during `rag_slow`, proving the incident affects tail latency before the answer is returned.

### 3.2 Dashboard & SLOs

- Dashboard Screenshot: `docs/evidence/dashboard-6-panels.png`
- SLO Table:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0.0% |
| Cost Budget | < $2.5/day | 1d | $0.0018 avg/request |

### 3.3 Alerts & Runbook

- Alert Rules Screenshot: `docs/evidence/alert-rules.png`
- Sample Runbook Link: `docs/alerts.md#1-high-latency-p95`

---

## 4. Incident Response (Group)

- Scenario Name: `rag_slow`
- Symptoms Observed: Latency P95 rises, the dashboard tail-latency panel spikes, and slow requests become obvious in Langfuse.
- Root Cause Proved By: Langfuse Trace ID `473e676cb3070b357fbb120c294b5edc` plus correlated log lines for `correlation_id=req-2f38c0a0`.
- Fix Action: Disable the injected incident after the demo and rerun clean traffic to show latency recovery.
- Preventive Measure: Add alerting on tail latency and review retrieval latency in traces before shipping retrieval changes.

---

## 5. Individual Contribution & Evidence

### Trần Đặng Quang Huy

- Tasks Completed: Completed the logging pipeline, correlation ID propagation, PII scrubbing, dashboard route integration, and final document consolidation.
- Evidence Link: https://github.com/khadpham/Lab13-Observability/tree/huy

---

## 6. Bonus Items (Optional)

- Bonus Cost Optimization: Not claimed in this submission. The team did not run a before/after cost-optimization experiment, so no savings figure is reported.
- Bonus Audit Logs: Not claimed in this submission. `audit.jsonl` is listed as an optional output in the template repo, but a separate audit-log pipeline is not currently implemented.
- Bonus Custom Metric: Claimed. The app exposes `quality_avg` from `app/metrics.py` as a custom heuristic quality metric, and this metric is visualized on the dashboard as the "Quality Proxy" panel.
