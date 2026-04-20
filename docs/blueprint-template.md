# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: A20-Observability-Lab
- [REPO_URL]: https://github.com/VinUni-AI20k/Lab13-Observability.git
- [MEMBERS]:
  - Member A: AI20k-Team | Role: Logging & PII
  - Member B: AI20k-Team | Role: Tracing & Enrichment
  - Member C: AI20k-Team | Role: SLO & Alerts
  - Member D: AI20k-Team | Role: Load Test & Dashboard
  - Member E: AI20k-Team | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 30 (local, Langfuse pending key config)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: All logs contain unique `req-<8hex>` correlation IDs
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: Verified in logs:
  - `student@vinuni.edu.vn` → `[REDACTED_EMAIL]`
  - `0987654321` → `[REDACTED_PHONE_VN]`  
  - `4111 1111 1111 1111` → `[REDACTED_CREDIT_CARD]`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Pending Langfuse key configuration
- [TRACE_WATERFALL_EXPLANATION]: Each trace captures the full agent pipeline: request → RAG retrieval → LLM generation → response. The `observe()` decorator on `LabAgent.run()` creates a parent span, with metadata including doc_count, query_preview, and token usage.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: `dashboard.html` — 6 panels with Chart.js:
  1. Latency P50/P95/P99 (line chart, SLO threshold at 3000ms)
  2. Traffic count (line chart)
  3. Error rate with breakdown (doughnut chart)
  4. Cost over time (line chart, budget line at $2.50)
  5. Tokens In/Out (bar chart)
  6. Quality proxy score (line chart, SLO at 0.75)
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2651ms ✅ |
| Error Rate | < 2% | 28d | 0.0% ✅ |
| Cost Budget | < $2.5/day | 1d | $0.0605 ✅ |
| Quality Avg | ≥ 0.75 | 28d | 0.88 ✅ |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: 5 alert rules in `config/alert_rules.yaml`
  1. `high_latency_p95` (P2) — docs/alerts.md#1
  2. `high_error_rate` (P1) — docs/alerts.md#2
  3. `cost_budget_spike` (P2) — docs/alerts.md#3
  4. `quality_score_drop` (P2) — docs/alerts.md#4
  5. `token_budget_exceeded` (P3) — docs/alerts.md#5
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#1-high-latency-p95](docs/alerts.md#1-high-latency-p95)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: 
  - Latency jumped from ~460ms baseline to ~2654ms (5.8x increase)
  - P95 latency breached SLO threshold (3000ms) on dashboard
  - All requests still returned 200 OK (no errors), but tail latency degraded UX
- [ROOT_CAUSE_PROVED_BY]: 
  - Metrics endpoint showed `latency_p95: 2651ms` (vs ~150ms baseline)
  - Log timestamps show each request taking ~2654ms during incident
  - Correlation IDs `req-fb066141` through `req-372927ab` all show elevated latency
  - Incident toggle `rag_slow` was confirmed enabled via `/health` endpoint
- [FIX_ACTION]: 
  - Disabled incident toggle via `POST /incidents/rag_slow/disable`
  - RAG retrieval latency returned to normal (~0ms simulated)
  - Post-fix verification: new requests returned to ~460ms latency
- [PREVENTIVE_MEASURE]: 
  - Alert rule `high_latency_p95` (P2) triggers when P95 > 5000ms for 30m
  - Runbook instructs: check RAG span vs LLM span, verify incident toggles
  - Long-term: add circuit breaker for RAG retrieval, fallback to cached results

---

## 5. Individual Contributions & Evidence

### AI20k-Team (All Roles)
- [TASKS_COMPLETED]: 
  - ✅ Implemented correlation ID middleware (`app/middleware.py`) — `req-<8hex>` format
  - ✅ Enriched logs with user context (`app/main.py`) — user_id_hash, session_id, feature, model, env
  - ✅ Enabled PII scrubbing processor (`app/logging_config.py`)
  - ✅ Extended PII patterns (`app/pii.py`) — added passport, Vietnamese address keywords
  - ✅ Fixed PII regex ordering to prevent CCCD/phone collision
  - ✅ Built 6-panel dashboard (`dashboard.html`) — Chart.js, auto-refresh 15s, SLO lines
  - ✅ Expanded alert rules from 3→5 (`config/alert_rules.yaml`)
  - ✅ Added runbooks for new alerts (`docs/alerts.md`)
  - ✅ Updated SLO targets with descriptive notes (`config/slo.yaml`)
  - ✅ Wrote 15 unit tests (all passing) — PII, middleware, metrics
  - ✅ Conducted incident response exercise (rag_slow scenario)
- [EVIDENCE_LINK]: All commits in local repository

---

## 6. Bonus Items (Optional)
- [BONUS_AUDIT_LOGS]: Audit log path configured in `.env` at `data/audit.jsonl`
- [BONUS_CUSTOM_METRIC]: Quality score proxy metric with heuristic scoring (doc relevance, response length, keyword overlap) — visible in `/metrics` endpoint and dashboard Panel 6
