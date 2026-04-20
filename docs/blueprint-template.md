# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: C401-Group
- [REPO_URL]: https://github.com/TBNRGarret/Lab13-A1-C401
- [MEMBERS]:
  - Member A: [Name] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C:  | Role: SLO & Alerts
  - Member D: [Name] | Role: Load Test & Dashboard
  - Member E: Phạm Tuấn Anh | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
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
| Latency P95 | < 3000ms | 28d | _(run load test)_ |
| Error Rate | < 2% | 28d | _(run load test)_ |
| Cost Budget | < $2.50/day | 1d | _(run load test)_ |
| Quality Score | ≥ 0.75 avg | 28d | _(run load test)_ |
| Throughput | ≥ 1 RPS | 28d | _(run load test)_ |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#1-high-latency-p95](docs/alerts.md#1-high-latency-p95)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: (e.g., P95 latency spike to >8000ms, alert `high_latency_p95` fired)
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: Disabled `rag_slow` incident toggle via `/admin/incidents`
- [PREVENTIVE_MEASURE]: Added SLO burn rate alert to detect this scenario faster. Set `rag_slow` as a known incident in runbook.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Member C - SLO & Alerts

**[TASKS_COMPLETED]**:
1. Defined 5 SLIs with quantified objectives in `config/slo.yaml`:
   - `latency_p95_ms` < 3000ms (99.5% target over 28d)
   - `error_rate_pct` < 2% (99.0% target over 28d)
   - `daily_cost_usd` < $2.50/day (hard cap)
   - `quality_score_avg` ≥ 0.75 (95.0% target over 28d)
   - `throughput_rps` ≥ 1.0 (99.0% target over 28d)
2. Added `error_budget` section to `slo.yaml` providing concrete budget minutes per SLI.
3. Configured 6 alert rules in `config/alert_rules.yaml` with P1/P2/P3 severity tiers:
   - P1: `high_error_rate` — triggers on >5% error rate for 5m (critical, PagerDuty)
   - P2: `high_latency_p95`, `cost_budget_spike`, `quality_score_degraded` (Slack)
   - P3: `slo_error_budget_warning`, `low_throughput` (informational)
4. Authored full runbooks in `docs/alerts.md` for all 6 alerts with:
   - Exact trigger conditions and business impact
   - Step-by-step investigation commands (with `jq` log queries)
   - Specific mitigation actions and escalation criteria

**Key Design Decisions**:
- Used **symptom-based alerts** (not cause-based) for P1/P2 to alert on user impact, not internal metrics
- Added **SLO burn-rate awareness**: `slo_error_budget_warning` fires when <20% budget remains, giving time to act before SLO is breached
- Runbooks include **concrete log query commands** so on-call engineers can debug immediately without context

**[EVIDENCE_LINK]**: _(Link to your commit after pushing)_

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
- [BONUS_CUSTOM_METRIC]: Added `throughput_rps` as a 5th SLI beyond the starter template, with a corresponding `low_throughput` P3 alert and runbook.
