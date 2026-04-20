# Phân Chia Công Việc Lab Observability - 7 Người

> **Ngày cập nhật**: 2026-04-20  
> **Rubric**: 60/40 (60 điểm nhóm + 40 điểm cá nhân)  
> **Passing Criteria**: validate_logs.py ≥80, ≥10 traces, 6-panel dashboard

---

## Tóm Tắt (Executive Summary)

| Member | Role | Task Chính | Rubric Phụ Trách | KPI |
|---|---|---|---|---|
| **A** | Logging Core | middleware.py + main.py enrich | A1-Logging (10đ) | correlation_id + context binding |
| **B** | PII & Security | pii.py regex + logging_config scrubber | A1-PII (5đ từ 10đ Alerts) | 0 PII leaks |
| **C** | Tracing & Instrumentation | tracing.py + @observe decorator | A1-Tracing (10đ) | ≥10 traces waterfall |
| **D** | SLO & Alerts | slo.yaml + alert_rules.yaml + runbook | A1-Alerts (5đ) | ≥3 alert rules chạy |
| **E** | Dashboard & Metrics | metrics.py + 6-panel dashboard | A1-Dashboard (10đ) | screenshot + validate_logs.py ≥80 |
| **F** | Load Test & Incident | load_test.py + inject_incident.py | A2 Incident Debug (10đ) | root cause analysis |
| **G** | Demo Lead & Report | blueprint-template.md + demo script | A3 Live Demo (20đ) | evidence + Q&A prep |

**Dependency Flow**:
```
A → B → [C, D, E, F] → G
```

---

## Chi Tiết Công Việc

### MEMBER A: Logging Core & Correlation ID

**Rubric Score**: A1 - Logging (10 điểm)

**Tasks**:

1. **[CRITICAL]** Fix `app/middleware.py` (3 TODOs)
   - Line 13: Clear contextvars tại đầu request
   - Line 16: Extract hoặc generate `x-request-id` từ header
   - Line 20: Bind correlation_id vào structlog context
   - Line 28: Add correlation_id + processing time vào response headers
   
2. **[CRITICAL]** Enrich logs in `app/main.py:47`
   - Bind `user_id_hash`, `session_id`, `feature`, `model`, `env` vào structlog
   - Đảm bảo mỗi log entry có đầy đủ context

3. **[VERIFY]** Test bằng:
   ```bash
   python scripts/load_test.py --concurrency 1
   tail -f data/logs.jsonl | jq '.request_id' | head -20
   ```
   - Check tất cả logs có `request_id` và context fields

**Deliverables**:
- ✅ Commit: "feat: implement correlation ID in middleware"
- ✅ Commit: "feat: enrich logs with request context"
- ✅ Test output: 20+ logs với correlation_id

**Git Evidence for B2**:
- Commit 1: middleware.py changes
- Commit 2: main.py changes

---

### MEMBER B: PII Scrubbing & Security

**Rubric Score**: A1 - Alerts & PII (5 điểm từ 10đ)

**Tasks**:

1. **[CRITICAL]** Expand PII patterns in `app/pii.py:11`
   - Email: `[\w\.-]+@[\w\.-]+\.\w+`
   - Phone: `(\+84|0)\d{9,10}`
   - CCCD: `\d{12}`
   - Passport: `[A-Z]{1,2}\d{6,8}`
   - Vietnamese address keywords: `Hà Nội|TP\.HCM|Đà Nẵng|...`
   
2. **[CRITICAL]** Implement scrubber in `app/logging_config.py:45`
   - Register PII processor vào structlog pipeline
   - Redact tất cả matches thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, etc.

3. **[VERIFY]** Test bằng:
   ```bash
   python -m pytest tests/test_pii.py -v
   python scripts/validate_logs.py
   ```
   - Đảm bảo `validate_logs.py` report "PII leaks: 0"

4. **[OPTIONAL]** Mở rộng `tests/test_pii.py`
   - Thêm test cases cho các pattern mới

**Deliverables**:
- ✅ Commit: "feat: add comprehensive PII patterns"
- ✅ Commit: "feat: implement PII scrubber processor"
- ✅ Test result: `validate_logs.py` → "PII leaks: 0"

**Git Evidence for B2**:
- Commit 1: pii.py patterns
- Commit 2: logging_config.py scrubber

---

### MEMBER C: Tracing & Enrichment

**Rubric Score**: A1 - Logging & Tracing (10 điểm)

**Tasks**:

1. **[CRITICAL]** Enhance `app/tracing.py`
   - Set up Langfuse client with API key from `.env`
   - Verify `@observe` decorator hoạt động đúng

2. **[CRITICAL]** Instrument `app/agent.py`
   - Wrap main agent flow: `retrieve()` → `generate()` → `rank()`
   - Add `@observe` decorator vào từng function
   - Enrich spans với tags: `model`, `tokens_used`, `cost_estimate`, `latency_ms`

3. **[CRITICAL]** Verify traces in Langfuse
   - Chạy ≥10 requests để tạo traces
   - Confirm ≥10 traces xuất hiện trong Langfuse dashboard
   - Screenshot trace waterfall (span tree) với metadata

4. **[VERIFY]** Check bằng:
   ```bash
   python scripts/load_test.py --concurrency 1 --requests 10
   # Vào Langfuse → verify 10+ traces
   ```

**Deliverables**:
- ✅ Commit: "feat: enhance Langfuse tracing in agent pipeline"
- ✅ Commit: "feat: add instrumentation tags to spans"
- ✅ Langfuse screenshot: 10+ traces với waterfall view
- ✅ Trace explanation: 1 trace waterfall giải thích (cho blueprint section 3.1)

**Git Evidence for B2**:
- Commit 1: tracing.py enhancements
- Commit 2: agent.py instrumentation

---

### MEMBER D: SLO & Alerting

**Rubric Score**: A1 - Alerts & PII (5 điểm từ 10đ)

**Tasks**:

1. **[CRITICAL]** Complete `config/slo.yaml`
   - Define SLIs (Service Level Indicators):
     - `latency_p95`: < 3000ms (28-day window)
     - `error_rate`: < 2% (28-day window)
     - `cost_per_day`: < $2.5 (1-day window)
   - Set error budgets: `1 - target = budget`
   - Example:
     ```yaml
     slos:
       - name: latency_p95
         target: 0.95
         window: 28d
         threshold_ms: 3000
       - name: error_rate
         target: 0.98
         window: 28d
         threshold: 0.02
       - name: cost_budget
         target: 1.0
         window: 1d
         budget_usd: 2.5
     ```

2. **[CRITICAL]** Implement ≥3 alert rules in `config/alert_rules.yaml`
   - Rule 1: `latency_p95_breach` (P95 > 3000ms)
   - Rule 2: `error_rate_high` (Error > 2%)
   - Rule 3: `cost_overrun` (Daily cost > $2.5)
   - Each rule must have: condition, threshold, runbook_link, severity
   
   Example:
   ```yaml
   alert_rules:
     - name: latency_p95_breach
       metric: latency_p95
       operator: ">"
       threshold: 3000
       severity: high
       runbook: "docs/alerts.md#latency-p95-breach"
   ```

3. **[CRITICAL]** Write runbook in `docs/alerts.md`
   - For each alert: symptoms, debugging steps, mitigation, escalation
   - Template:
     ```markdown
     ## Alert: latency_p95_breach
     
     **Symptoms**: P95 latency > 3000ms for 5+ minutes
     
     **Debug Steps**:
     1. Check Langfuse traces → identify slow span
     2. Check metrics dashboard → CPU/memory usage
     3. Check logs → filter by high latency requests
     
     **Mitigation**:
     - Scale up RAG service
     - Check LLM rate limits
     
     **Escalation**: Alert oncall → page SRE
     ```

4. **[VERIFY]** Test alerts by:
   ```bash
   python scripts/inject_incident.py --scenario rag_slow
   # Check alert rule triggers
   ```

**Deliverables**:
- ✅ Commit: "feat: define SLOs in slo.yaml"
- ✅ Commit: "feat: implement alert rules in alert_rules.yaml"
- ✅ Commit: "docs: write alert runbooks"
- ✅ Screenshot: alert_rules.yaml with ≥3 rules
- ✅ Runbook: at least one fully documented in docs/alerts.md

**Git Evidence for B2**:
- Commit 1: slo.yaml
- Commit 2: alert_rules.yaml + docs/alerts.md

---

### MEMBER E: Dashboard & Metrics

**Rubric Score**: A1 - Dashboard & SLO (10 điểm) + Bonus Dashboard Design (+3đ)

**Tasks**:

1. **[CRITICAL]** Complete `app/metrics.py`
   - Implement metrics collectors:
     - `latency_histogram` (per endpoint, per model)
     - `error_counter` (by error type)
     - `cost_gauge` (current estimated cost)
     - `token_counter` (input + output tokens)
   - Ensure metrics are in Prometheus format

2. **[CRITICAL]** Create 6-panel dashboard (Grafana or similar)
   - **Panel 1**: Latency P95 (time series)
   - **Panel 2**: Error Rate % (time series with threshold line)
   - **Panel 3**: Request Volume (bar chart, by endpoint)
   - **Panel 4**: Token Usage (stacked bar: input vs output)
   - **Panel 5**: Cost Estimate (gauge showing $/day vs $2.5 budget)
   - **Panel 6**: Top Slow Endpoints (table with P95 latency)
   
   Each panel must have:
   - ✅ Title
   - ✅ Units (ms, %, $, tokens)
   - ✅ Threshold/SLO line if applicable

3. **[OPTIONAL]** Bonus: Make dashboard visually polished
   - Good color scheme (avoid red-green colorblind issues)
   - Consistent formatting
   - Clear legends and labels

4. **[VERIFY]** Export dashboard:
   ```bash
   python scripts/validate_logs.py
   # Capture screenshot of all 6 panels
   ```

**Deliverables**:
- ✅ Commit: "feat: implement metrics collectors"
- ✅ Commit: "feat: build 6-panel dashboard"
- ✅ Dashboard screenshot: all 6 panels visible
- ✅ validate_logs.py output: ≥80/100 score

**Git Evidence for B2**:
- Commit 1: metrics.py
- Commit 2: dashboard config/setup

---

### MEMBER F: Load Testing & Incident Injection

**Rubric Score**: A2 - Incident Response & Debugging (10 điểm) + Bonus (+2đ)

**Tasks**:

1. **[CRITICAL]** Run load test to generate traces
   ```bash
   python scripts/load_test.py --concurrency 5 --requests 50
   # Should generate ≥10 traces in Langfuse
   ```
   - Verify logs.jsonl has ≥100 entries
   - Monitor dashboard for metrics

2. **[CRITICAL]** Inject incident scenarios
   - Use `scripts/inject_incident.py` to trigger failures:
     ```bash
     python scripts/inject_incident.py --scenario rag_slow
     python scripts/inject_incident.py --scenario llm_fail
     python scripts/inject_incident.py --scenario cost_spike
     ```
   - Observe how metrics/traces/logs respond

3. **[CRITICAL]** Root cause analysis for ≥1 incident
   - Pick one scenario (e.g., `rag_slow`)
   - Follow debugging flow: **Metrics → Traces → Logs**
   
   **Example Analysis**:
   - **Symptoms**: P95 latency spike from 500ms to 4500ms
   - **Metrics Evidence**: latency_p95 graph shows spike at 14:32:15
   - **Trace Evidence**: Langfuse trace [ID: xyz123] shows `retrieve()` span took 4000ms (vs normal 100ms)
   - **Log Evidence**: logs.jsonl shows "RAG service slow: 4000ms" at timestamp
   - **Root Cause**: RAG service overloaded (injected scenario)
   - **Fix**: Scale up RAG replicas from 2→5
   - **Preventive**: Set alert on RAG latency + auto-scaling policy

4. **[OPTIONAL]** Bonus: Automate incident injection
   - Write bash script to cycle through scenarios
   - Capture metrics before/after each injection

**Deliverables**:
- ✅ Commit: "test: run load test and generate traces"
- ✅ Commit: "test: inject incident scenarios and analyze"
- ✅ Incident analysis document (for blueprint section 4):
  - Scenario name, symptoms, trace ID, root cause, fix, prevention
- ✅ Screenshots: metrics/traces/logs showing incident

**Git Evidence for B2**:
- Commit 1: load_test.py execution
- Commit 2: incident analysis write-up

---

### MEMBER G: Demo Lead & Final Report

**Rubric Score**: A3 - Live Demo & Communication (20 điểm) + Bonus Audit Logs (+2đ)

**Tasks**:

1. **[CRITICAL]** Coordinate & complete `docs/blueprint-template.md`
   
   **Section 1: Team Metadata**
   - Fill in GROUP_NAME, REPO_URL, all 7 MEMBERS with names + roles
   
   **Section 2: Auto-Verified Metrics** (collect from others)
   - VALIDATE_LOGS_FINAL_SCORE: Ask Member E for validate_logs.py score
   - TOTAL_TRACES_COUNT: Ask Member C for Langfuse count
   - PII_LEAKS_FOUND: Ask Member B for test result
   
   **Section 3: Technical Evidence** (collect screenshots from all)
   - 3.1: correlation_id log (from A), PII redaction (from B), trace waterfall (from C)
   - 3.2: 6-panel dashboard (from E), fill SLO table with current values
   - 3.3: alert_rules (from D), runbook links
   
   **Section 4: Incident Response** (from F)
   - Fill in scenario name, symptoms, root cause, fix, prevention
   
   **Section 5: Individual Contributions** (each member fills their own)
   - Each member writes their TASKS_COMPLETED + EVIDENCE_LINK (commit/PR)
   
   **Section 6: Bonus Items** (optional)
   - Cost optimization (if done)
   - Audit logs (if done)

2. **[CRITICAL]** Prepare live demo script
   - Demo flow (5-10 minutes):
     1. Show app running: `uvicorn app.main:app --reload`
     2. Send test request: `curl -X POST http://localhost:8000/query -H "x-request-id: demo123"`
     3. Show logs.jsonl: `tail -f data/logs.jsonl | jq '.'`
     4. Show Langfuse trace waterfall
     5. Show 6-panel dashboard with metrics
     6. Trigger alert: `python scripts/inject_incident.py --scenario rag_slow`
     7. Show alert rule triggered + metrics spiked
     8. Explain incident → traces → logs debugging flow

3. **[CRITICAL]** Prepare Q&A for giảng viên
   - Study `docs/mock-debug-qa.md` if available
   - Assign Q&A responsibility:
     - A answers about correlation IDs
     - B answers about PII redaction
     - C answers about tracing
     - D answers about SLOs & alerts
     - E answers about dashboard & metrics
     - F answers about incident debugging
   - Practice explaining regex, JSON schema, middleware flow

4. **[OPTIONAL]** Bonus: Set up audit logs
   - Implement separate `data/audit.jsonl` for sensitive operations
   - Log: config changes, alert triggers, incident injection/resolution
   - Show separation in blueprint bonus section

5. **[VERIFY]** Final checklist before demo:
   - [ ] All TODO comments resolved
   - [ ] `validate_logs.py` runs without errors
   - [ ] ≥10 traces visible in Langfuse
   - [ ] 6-panel dashboard shows real data
   - [ ] ≥3 alert rules configured
   - [ ] blueprint-template.md filled 100%
   - [ ] Each member has ≥2 commits
   - [ ] Demo script tested end-to-end

**Deliverables**:
- ✅ Commit: "docs: complete blueprint-template.md"
- ✅ Commit: "docs: prepare demo script and Q&A"
- ✅ Final blueprint-template.md with all sections filled
- ✅ docs/grading-evidence.md with evidence checklist
- ✅ Demo runs smoothly with no errors

**Git Evidence for B2**:
- Commit 1: blueprint-template.md
- Commit 2: demo preparation & Q&A notes

---

## Execution Timeline

| Phase | Duration | Members | Deliverable |
|---|---|---|---|
| **Phase 1: Logging** | 30 min | A | logs.jsonl with correlation_id |
| **Phase 2: PII** | 20 min | B | 0 PII leaks (validate_logs.py) |
| **Phase 3: Parallel** | 45 min | C, D, E, F | traces, SLOs, alerts, dashboard, incident analysis |
| **Phase 4: Integration** | 30 min | G (all support) | blueprint-template.md + demo test |
| **Phase 5: Final Polish** | 15 min | All | commit cleanup, final checklist |
| **DEMO** | 10 min | G (all present) | live presentation |

**Total**: ~2.5 hours hands-on + 30 min demo

---

## Success Criteria (Passing)

- ✅ validate_logs.py ≥ 80/100
- ✅ ≥ 10 traces in Langfuse
- ✅ 6-panel dashboard complete
- ✅ ≥ 3 alert rules working
- ✅ blueprint-template.md 100% filled
- ✅ Each member has ≥ 2 commits
- ✅ Demo runs without crashes

## Bonus Opportunities

| Bonus | Points | Owner | Task |
|---|---|---|---|
| Cost Optimization | +3 | F | Calculate before/after cost savings |
| Dashboard Design | +3 | E | Polished, professional looking |
| Auto-instrumentation | +2 | F | Script to auto-inject scenarios |
| Audit Logs | +2 | G | Separate audit.jsonl tracking |

---

## Git Workflow

**Each member should**:
1. Create feature branch: `git checkout -b feat/ROLE_NAME`
2. Make 2-3 meaningful commits with clear messages
3. Push: `git push origin feat/ROLE_NAME`
4. Open PR with description of changes
5. Merge after code review

**Commit naming convention**:
```
feat: [MEMBER_INITIAL]_[TASK] - brief description
e.g., "feat: A_correlation-id - implement x-request-id header"
```

---

## Communication & Checkpoints

**Slack/Discord Check-ins**:
- 00:00-00:30 → A completes logging (critical path)
- 00:30-00:45 → B completes PII (blocks A)
- 00:45-01:30 → C, D, E, F work in parallel
- 01:30-02:00 → G coordinates blueprint + final merge
- 02:00-02:30 → All polish + demo rehearsal

**Red flags** (escalate immediately):
- validate_logs.py score < 70
- 0 traces in Langfuse after load test
- PII leaks detected in logs
- Dashboard missing panels
- Any member stuck > 15 min without progress

---

## References

- Rubric: [day13-rubric-for-instructor.md](day13-rubric-for-instructor.md)
- Blueprint: [docs/blueprint-template.md](docs/blueprint-template.md)
- Alert spec: [docs/alerts.md](docs/alerts.md)
- Dashboard spec: [docs/dashboard-spec.md](docs/dashboard-spec.md)
- Grading evidence: [docs/grading-evidence.md](docs/grading-evidence.md)
