# Implementation Plan — Day 13 Observability Lab

**Lab**: Observability End-to-End (Structured Logging, Langfuse Tracing, SLOs, Alerts)  
**App**: FastAPI agent with RAG + LLM pipeline  
**Duration**: 4 hours  
**Team Size**: 5 members  
**Split**: Group (60 pts) + Individual (40 pts)

---

## 1. Project Overview

The lab provides a pre-built FastAPI application (`app/`) that simulates an AI agent with RAG retrieval and an LLM call. The application is **intentionally missing all observability instrumentation**. Every `TODO` block in the codebase must be completed by the team. The final deliverable is a fully observable, traceable, and monitorable system that passes automated validation and a live instructor demo.

---

## 2. Group Work (60 pts)

Group work is organized into **5 work streams**, each assigned to one team member as the primary owner. All members review each other's code before merging.

### Work Stream 1: Structured Logging + PII Scrubbing
**Owner**: *(assign to 1 member)*  
**Weight**: ~12 pts of the 60

**Objective**: All application events are emitted as structured JSON logs with correlation ID propagation and PII redaction.

**Files to modify**:

| File | TODO Description |
|------|-------------------|
| `app/logging_config.py` | Register `scrub_event` PII processor in the structlog pipeline |
| `app/middleware.py` | Generate correlation ID (`req-<8-char-hex>`), clear contextvars between requests, bind correlation ID to structlog contextvars, add `X-Correlation-ID` header to response |
| `app/main.py` | Enrich all log calls with `bind_contextvars` for `user_id_hash`, `session_id`, `feature` |
| `app/pii.py` | Add more PII patterns: passport numbers, Vietnamese address keywords, national ID numbers |

**Deliverables**:
- [ ] `app/logging_config.py` — structlog pipeline outputs JSONL to `data/logs.jsonl`; processor chain includes `scrub_event`
- [ ] `app/middleware.py` — correlation ID generated, stored in contextvars, added to response headers
- [ ] `app/main.py` — all `/health`, `/metrics`, `/chat` endpoints use `bind_contextvars`
- [ ] `app/pii.py` — `scrub_text` redacts emails, phone numbers, credit cards, passport, national ID, Vietnamese addresses
- [ ] Run `python scripts/validate_logs.py` — PII leaks = 0
- [ ] Screenshots: raw JSON log lines showing correlation ID propagation across multiple log events for a single request

---

### Work Stream 2: Langfuse Distributed Tracing
**Owner**: *(assign to 1 member)*  
**Weight**: ~12 pts of the 60

**Objective**: Every agent run is traced in Langfuse with spans for retrieval, LLM call, and response assembly.

**Files to modify**:

| File | TODO Description |
|------|-------------------|
| `app/tracing.py` | Ensure `@observe()` decorator wraps `agent.run()`; verify `tracing_enabled()` checks env keys |
| `app/main.py` | Wrap the agent pipeline call with `@observe()` or call `langfuse.get_instance().trace()` |
| `app/agent.py` | Add child spans for each sub-step (retrieval, prompt assembly, LLM call, response parsing) using `langfuse.get_instance().span()` |
| `app/mock_llm.py` | Tag the Langfuse span with model name, token counts, and cost |
| `app/mock_rag.py` | Tag the Langfuse span with retrieval latency, top-k count, and source document IDs |

**Deliverables**:
- [ ] `app/tracing.py` — `observe` decorator is applied to `agent.run()`
- [ ] `app/agent.py` — at least 3 child spans per request: `rag_retrieval`, `llm_call`, `response_format`
- [ ] Langfuse dashboard shows >= 10 traces after running `python scripts/load_test.py`
- [ ] Each trace has: `correlation_id`, `user_id_hash`, `latency_ms`, `tokens_in`, `tokens_out`, `cost_usd`
- [ ] Screenshots: Langfuse trace waterfall showing all spans for a single `/chat` request

---

### Work Stream 3: Metrics + SLO Definitions + Alert Rules
**Owner**: *(assign to 1 member)*  
**Weight**: ~12 pts of the 60

**Objective**: Prometheus-compatible `/metrics` endpoint with percentile latency, error rate, cost, and quality SLOs backed by alert rules.

**Files to modify**:

| File | TODO Description |
|------|-------------------|
| `app/metrics.py` | Ensure all metric recording calls are present in `agent.py` (latency, tokens, cost, errors) |
| `app/agent.py` | Call `record_request_latency()`, `record_token_usage()`, `record_cost()` at correct points |
| `config/slo.yaml` | Verify SLO targets: P95 latency < 2s, error rate < 5%, cost/token budget, quality > 80% |
| `config/alert_rules.yaml` | Ensure all 3 alert rules are correctly configured (high_latency_p95, high_error_rate, cost_budget_spike) |

**Deliverables**:
- [ ] `GET /metrics` returns Prometheus-format metrics (latency histogram, counters for requests/errors/tokens/cost)
- [ ] `config/slo.yaml` — 4 SLOs defined with clear targets and measurement windows
- [ ] `config/alert_rules.yaml` — 3 alert rules with correct thresholds, severity levels, and runbook links
- [ ] After `python scripts/load_test.py`, metrics show non-zero values for all metric types
- [ ] Screenshots: `/metrics` output snippet, SLO table showing current status vs. targets

---

### Work Stream 4: Incident Response + Runbooks + Alerts
**Owner**: *(assign to 1 member)*  
**Weight**: ~12 pts of the 60

**Objective**: The team must be able to detect, diagnose, and resolve 3 simulated incidents using the observability stack.

**Incident Scenarios** (from `data/incidents.json`):

| Incident | Toggle Name | Symptoms | Detection |
|----------|------------|----------|-----------|
| Slow RAG | `rag_slow` | P95 latency > 5s | Alert on `app_latency_p95_seconds > 5` |
| Tool Failure | `tool_fail` | Error rate > 5% | Alert on `app_error_rate > 0.05` |
| Cost Spike | `cost_spike` | Hourly cost 4x baseline | Alert on `app_cost_per_hour > 2 * baseline` |

**Tasks**:

| Step | Task |
|------|------|
| 1 | Enable `rag_slow` via `python scripts/inject_incident.py --incident rag_slow --enable` |
| 2 | Verify alert fires (or would fire) in the alert rules |
| 3 | Open Langfuse trace for a failing request — identify slow span (`rag_retrieval`) |
| 4 | Open logs — find correlation ID chain from request to error |
| 5 | Diagnose root cause: vector store timeout in `mock_rag.py` |
| 6 | Apply fix (document the manual fix or script it in `scripts/`) |
| 7 | Disable toggle, verify metrics return to normal |
| 8 | Repeat for `tool_fail` and `cost_spike` |
| 9 | Write runbook for each incident in `docs/alerts.md` |

**Deliverables**:
- [ ] `docs/alerts.md` — 3 runbooks, each with: symptoms, detection (alert rule), diagnosis steps, fix action, preventive measure
- [ ] Screenshots: alert firing in dashboard, Langfuse trace showing slow/failed span, log correlation chain
- [ ] All 3 incident scenarios successfully diagnosed and resolved within the session

---

### Work Stream 5: Dashboard + Load Testing + Validation
**Owner**: *(assign to 1 member)*  
**Weight**: ~12 pts of the 60

**Objective**: Build a 6-panel Grafana dashboard and run the full validation suite.

**Dashboard Panels** (from `docs/dashboard-spec.md`):

| Panel # | Title | Metric / Query | Type |
|---------|-------|----------------|------|
| 1 | Request Volume | `sum(rate(app_requests_total[5m]))` | Time series |
| 2 | P95 Latency | `histogram_quantile(0.95, app_request_latency_seconds)` | Time series |
| 3 | Error Rate | `sum(rate(app_errors_total[5m])) / sum(rate(app_requests_total[5m]))` | Gauge |
| 4 | Token Usage (in/out) | `app_tokens_in_total`, `app_tokens_out_total` | Stacked time series |
| 5 | Cost per Hour | `app_cost_total * 3600 / elapsed_seconds` | Single stat |
| 6 | SLO Health | Composite: latency SLO %, error SLO %, cost SLO % | Traffic light gauge |

**Tasks**:

| Step | Task |
|------|------|
| 1 | Run `python scripts/load_test.py` with concurrency=5, count=50 |
| 2 | Verify `data/logs.jsonl` contains >= 50 entries |
| 3 | Run `python scripts/validate_logs.py` — score >= 80/100 |
| 4 | Build Grafana dashboard with all 6 panels |
| 5 | Import `config/slo.yaml` and `config/alert_rules.yaml` into alert management system |
| 6 | Collect all screenshots for the blueprint report |

**Deliverables**:
- [ ] `python scripts/load_test.py` completes successfully (>= 50 requests)
- [ ] `python scripts/validate_logs.py` score >= 80/100, PII leaks = 0, correlation ID gaps = 0
- [ ] Grafana dashboard with 6 panels, all showing data
- [ ] Screenshots: dashboard with all 6 panels populated, validation script output

---

## 3. Individual Work (40 pts)

Each team member writes their own individual report and demonstrates Git evidence.

### Individual Report (20 pts)

Each member writes a report covering:

1. **Role in the team** — which work stream you owned, what you implemented
2. **Technical contribution** — code changes you made, key design decisions
3. **Challenges faced** — and how you resolved them
4. **Evidence** — links to your Git commits, screenshots of your component working
5. **Reflection** — what you learned about observability from this lab

**Format**: Markdown file per member (e.g., `docs/individual-report-<name>.md`)

**Deliverables**:
- [ ] One markdown report per member saved in `docs/`
- [ ] All TODO items owned by that member are committed to Git with descriptive messages
- [ ] Screenshots of the owned component working (embedded or linked)
- [ ] Minimum 3 commits with substantive change descriptions

### Git Evidence (20 pts)

| Criterion | Requirement |
|-----------|-------------|
| Commit count | At least 3 commits per person |
| Commit quality | Descriptive messages: `feat: add correlation ID middleware`, not `fix stuff` |
| Branching | Use feature branches (`feature/logging`, `feature/tracing`, etc.) |
| Merge strategy | Pull requests reviewed by at least 1 other team member |
| `git log` | Shows meaningful incremental progress |

**Deliverables**:
- [ ] Feature branch per work stream
- [ ] Pull requests with at least 1 approval
- [ ] `git log --oneline` screenshot showing all commits
- [ ] `git diff` screenshot for at least one key change

---

## 4. Bonus Work (up to +10 pts)

| Bonus Item | Points | Owner |
|-----------|--------|-------|
| Cost optimization — add token budget per user/session with graceful degradation | +2 | Anyone |
| Audit logging — write structured audit events to `data/audit.jsonl` for compliance | +2 | Anyone |
| Custom metrics — add `app_retrieval_latency_seconds` histogram broken down by top-k | +2 | Anyone |
| Dashboard aesthetics — custom color scheme, annotations, variable filters | +2 | Anyone |
| Automation script — single `python scripts/run_full_validation.py` that does load test + validation | +2 | Anyone |

---

## 5. Submission Checklist

### Group Submission
- [ ] `docs/blueprint-template.md` — filled with all team info, scores, screenshots, incident reports
- [ ] `python scripts/validate_logs.py` score >= 80/100
- [ ] Langfuse dashboard shows >= 10 traces
- [ ] Grafana dashboard has 6 panels with live data
- [ ] All 3 incident scenarios diagnosed and resolved
- [ ] `requirements.txt` pinned with exact versions

### Individual Submission
- [ ] `docs/individual-report-<name>.md` per member
- [ ] Git history shows >= 3 commits per person with descriptive messages
- [ ] Feature branches merged into main via PR

### Live Demo (20 pts)
- [ ] Start the app with `uvicorn app.main:app --reload`
- [ ] Show `/health` and `/metrics`
- [ ] Send 1 request to `/chat` — show structured log output
- [ ] Show Langfuse trace for that request (waterfall view)
- [ ] Trigger one incident toggle and show the alert firing
- [ ] Disable the toggle and show metrics return to normal

---

## 6. Suggested Timeline (4 hours)

| Time | Activity |
|------|----------|
| 0:00 – 0:15 | Kickoff: assign roles, clone repo, install deps (`pip install -r requirements.txt`) |
| 0:15 – 0:45 | Work Stream 1 + 2 in parallel (logging & tracing) |
| 0:45 – 1:15 | Work Stream 3 + 4 in parallel (metrics/alerts & incidents) |
| 1:15 – 2:00 | Work Stream 5 (dashboard, load test, validation) — all members contribute |
| 2:00 – 2:30 | Incident response walk-through (all members) |
| 2:30 – 3:15 | Write individual reports + finalize Git history |
| 3:15 – 3:45 | Fill `docs/blueprint-template.md`, collect screenshots |
| 3:45 – 4:00 | Live demo rehearsal + final submission |

---

## 7. Team Assignment Template

| Work Stream | Assigned To | Primary File(s) |
|-------------|-----------|-----------------|
| 1: Logging + PII Scrubbing | Võ Thiên Phú (2A202600336) | `app/logging_config.py`, `app/middleware.py`, `app/pii.py` |
| 2: Langfuse Tracing | Đào Hồng Sơn (2A202600462) | `app/tracing.py`, `app/agent.py`, `app/mock_llm.py`, `app/mock_rag.py` |
| 3: Metrics + SLO + Alerts | Phan Dương Định (2A202600277) | `app/metrics.py`, `app/agent.py`, `config/slo.yaml`, `config/alert_rules.yaml` |
| 4: Incident Response | Phạm Minh Khang (2A202600417) | `app/incidents.py`, `docs/alerts.md`, `scripts/inject_incident.py` |
| 5: Dashboard + Load Test | Nguyễn Anh Quân (2A202600132) | `docs/dashboard-spec.md`, `scripts/load_test.py`, `scripts/validate_logs.py`, `scripts/run_full_validation.py` |

---

## 8. Final Validation Results

After running `python scripts/load_test.py --concurrency 5 --count 5` and `python scripts/validate_logs.py`:

| Check | Result |
|-------|--------|
| Total log records | 101 (from 50 requests + startup/health/metrics logs) |
| Missing required fields | 0 |
| Missing enrichment | 0 |
| Unique correlation IDs | 50 |
| PII leaks | 0 |
| **Validation Score** | **100/100** |
| Pytest | 2/2 passed |

---

*Generated for Day 13 Observability Lab — Vo Thien Phu — 2A202600336*
