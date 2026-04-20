# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: [Name] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: [Name] | Role: Load Test & Dashboard
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: ⏳ _Chờ load test chạy xong để chụp screenshot_
- Dashboard gồm 6 panels: Latency (P50/P95/P99), Traffic (QPS), Error Rate, Cost over time, Tokens in/out, Quality score
- [SLO_TABLE]:
| SLI | Objective | Target | Window | Unit | Current Value |
|---|---:|---:|---|---|---:|
| Latency P95 | < 3000ms | 99.5% requests đạt | 28d | ms | **151.0** |
| Error Rate | < 2% | 99.0% thời gian đạt | 28d | % | **0.0** |
| Cost Budget | < $2.50/day | 100% thời gian đạt | 1d | USD/day | **~$0.02** |
| Quality Score | ≥ 0.75 | 95% thời gian đạt | 28d | score | **0.88** |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: ⏳ _Chờ app chạy để chụp screenshot_
- Tổng cộng **5 alert rules** đã cấu hình trong `config/alert_rules.yaml`:
  1. `high_latency_p95` (P2) — Runbook: [docs/alerts.md#1-high-latency-p95](docs/alerts.md#1-high-latency-p95)
  2. `high_error_rate` (P1) — Runbook: [docs/alerts.md#2-high-error-rate](docs/alerts.md#2-high-error-rate)
  3. `cost_budget_spike` (P2) — Runbook: [docs/alerts.md#3-cost-budget-spike](docs/alerts.md#3-cost-budget-spike)
  4. `quality_degradation` (P2) — Runbook: [docs/alerts.md#4-quality-degradation](docs/alerts.md#4-quality-degradation)
  5. `token_anomaly` (P3) — Runbook: [docs/alerts.md#5-token-anomaly](docs/alerts.md#5-token-anomaly)
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md](docs/alerts.md)

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
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

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
