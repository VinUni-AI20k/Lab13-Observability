# Git Commit Guide — Day 13 Observability Lab

## Team Members & Branch Assignments

| Member | MSSV | Branch | Primary Files |
|--------|------|--------|---------------|
| Võ Thiên Phú | 2A202600336 | `feature/logging-pii-scrubbing` | `app/middleware.py`, `app/logging_config.py`, `app/pii.py`, `app/main.py` |
| Đào Hồng Sơn | 2A202600462 | `feature/langfuse-tracing` | `app/agent.py`, `app/mock_llm.py`, `app/mock_rag.py`, `app/tracing.py` |
| Phan Dương Định | 2A202600277 | `feature/metrics-slo-alerts` | `app/metrics.py`, `config/slo.yaml`, `config/alert_rules.yaml` |
| Phạm Minh Khang | 2A202600417 | `feature/incident-runbooks` | `docs/alerts.md`, `scripts/inject_incident.py` |
| Nguyễn Anh Quân | 2A202600132 | `feature/dashboard-validation-bonus` | `docs/dashboard-spec.md`, `scripts/run_full_validation.py`, `app/audit.py`, `scripts/load_test.py` |

---

## Commit Message Convention

We follow **Conventional Commits** format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature (e.g., correlation ID middleware)
- `fix`: Bug fix (e.g., fixed missing correlation ID in logs)
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation only changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (deps, scripts, configs)

### Examples
```
feat(logging): add correlation ID middleware
feat(logging): register scrub_event PII processor in structlog pipeline
feat(logging): enrich /chat endpoint logs with user contextvars
feat(tracing): add child spans for agent pipeline stages
feat(metrics): expose Prometheus-compatible /metrics endpoint
feat(audit): implement audit logging to data/audit.jsonl
docs(runbook): document rag_slow incident response
```

---

## Workflow

### 1. Create Feature Branches

Each member creates their own branch from `main`:

```bash
# Võ Thiên Phú
git checkout main
git pull origin main
git checkout -b feature/logging-pii-scrubbing

# Đào Hồng Sơn
git checkout main
git pull origin main
git checkout -b feature/langfuse-tracing

# Phan Dương Định
git checkout main
git pull origin main
git checkout -b feature/metrics-slo-alerts

# Phạm Minh Khang
git checkout main
git pull origin main
git checkout -b feature/incident-runbooks

# Nguyễn Anh Quân
git checkout main
git pull origin main
git checkout -b feature/dashboard-validation-bonus
```

### 2. Make Commits

Each member commits their work with descriptive messages:

#### Võ Thiên Phú — 3 commits

```bash
# Commit 1: Correlation ID Middleware
git add app/middleware.py
git commit -m "feat(logging): implement correlation ID middleware

- Generate req-<8-char-hex> IDs for each request
- Clear contextvars between requests to prevent leakage
- Add X-Request-ID and X-Response-Time-Ms to response headers
- Bind correlation_id to structlog contextvars

Closes #WS1"

# Commit 2: PII Scrubbing Pipeline
git add app/logging_config.py app/pii.py
git commit -m "feat(logging): register PII scrubber in structlog pipeline

- Added scrub_event processor to structlog chain
- Extended PII patterns: email, phone_vn, cccd, credit_card, passport,
  national_id_vn, vietnamese_address
- scrub_text() replaces matches with [REDACTED_<PATTERN>]

Closes #WS1"

# Commit 3: Log Enrichment in main.py
git add app/main.py
git commit -m "feat(logging): enrich all endpoint logs with context variables

- Bind user_id_hash, session_id, feature in /chat handler
- Bind service and env in startup event
- Bind service=control in incident toggle handlers

Closes #WS1"
```

#### Đào Hồng Sơn — 3 commits

```bash
# Commit 1: Agent Pipeline Spans
git add app/agent.py
git commit -m "feat(tracing): add child spans for agent pipeline stages

- rag_retrieval span captures doc_count and query_preview
- prompt_assembly span captures prompt_length and feature
- llm_call span captures model, tokens_in, tokens_out
- response_format span captures answer_length and quality_score

Closes #WS2"

# Commit 2: LLM Span Tagging
git add app/mock_llm.py
git commit -m "feat(tracing): tag llm_generate span with model and cost metadata

- Add llm_generate span in FakeLLM.generate()
- Capture model name, prompt_length in span metadata
- Tag cost_spike incident in span when active

Closes #WS2"

# Commit 3: RAG Span Tagging
git add app/mock_rag.py
git commit -m "feat(tracing): tag vector_store_lookup span with incident metadata

- Wrap retrieve() in langfuse span
- Add incident=rag_slow/tool_fail to span metadata
- Record slowdown_ms for rag_slow incidents

Closes #WS2"
```

#### Phan Dương Định — 3 commits

```bash
# Commit 1: Enhanced Metrics Module
git add app/metrics.py
git commit -m "feat(metrics): add Prometheus-compatible metrics and SLO support

- Add RETRIEVAL_LATENCIES for app_retrieval_latency_p95_seconds
- Add START_TIME and BASELINE_COST_PER_HOUR for adaptive cost baseline
- Add record_retrieval_latency() function
- Update snapshot() with Prometheus-formatted keys (app_* prefix)

Closes #WS3"

# Commit 2: SLO Configuration
git add config/slo.yaml
git commit -m "feat(slo): define 4 SLIs with objectives and targets

- latency_p95_ms: < 3000ms, target 99.5%
- error_rate_pct: < 2%, target 99.0%
- daily_cost_usd: < $2.50/day, target 100%
- quality_score_avg: > 0.75, target 95%

Closes #WS3"

# Commit 3: Alert Rules
git add config/alert_rules.yaml
git commit -m "feat(alerts): configure 3 alert rules with severity and runbooks

- high_latency_p95: P2, > 5s for 30m
- high_error_rate: P1, > 5% for 5m
- cost_budget_spike: P2, > 2x baseline for 15m

Each rule includes owner, runbook link, and dashboard panel reference.

Closes #WS3"
```

#### Phạm Minh Khang — 2 commits

```bash
# Commit 1: Complete Runbook Documentation
git add docs/alerts.md
git commit -m "docs(runbook): document all 3 incident scenarios with full workflow

- rag_slow: symptoms, detection, diagnosis, fix, prevention
- tool_fail: symptoms, detection, diagnosis, fix, prevention
- cost_spike: symptoms, detection, diagnosis, fix, prevention
- Add standard incident response workflow (DETECT->TRIAGE->DIAGNOSE->FIX)
- Add quick reference commands for all incident toggles

Closes #WS4"

# Commit 2: Enhanced Incident Injection Script
git add scripts/inject_incident.py
git commit -m "feat(incident): enhance inject_incident.py with aliases and module support

- Add --incident as alias for --scenario
- Support python -m scripts.inject_incident invocation
- Add descriptive argparse help text

Closes #WS4"
```

#### Nguyễn Anh Quân — 3 commits

```bash
# Commit 1: Grafana Dashboard Specification
git add docs/dashboard-spec.md
git commit -m "feat(dashboard): create 6-panel Grafana dashboard JSON

- Panel 1: Request Volume (QPS) time series
- Panel 2: P95 Latency with SLO line at 3000ms
- Panel 3: Error Rate gauge with thresholds
- Panel 4: Token Usage (in/out) stacked time series
- Panel 5: Cost per Hour stat
- Panel 6: SLO Health overview table
- Dark theme, 15s auto-refresh, 1h default range

Closes #WS5"

# Commit 2: Full Validation Automation Script
git add scripts/run_full_validation.py
git commit -m "feat(validation): add run_full_validation.py automation script

- Clears logs, runs load test, validates output
- Supports --concurrency and --count parameters
- Prints PASS/FAIL verdict with score summary
- Idempotent: safe to run multiple times

Bonus item: +2 automation pts

Closes #WS5"

# Commit 3: Audit Logging and Enhanced Load Test
git add app/audit.py scripts/load_test.py
git commit -m "feat(audit): implement audit logging to data/audit.jsonl

- audit_chat_request for every successful /chat request
- audit_chat_error for every failed /chat request
- audit_incident_toggle for incident enable/disable
- Integrated into app/main.py for all /chat and incident endpoints

feat(load): enhance load_test.py with --count and module support

Bonus items: +2 audit logs pts

Closes #WS5"
```

### 3. Push Branches

```bash
# Each member pushes their branch
git push -u origin feature/logging-pii-scrubbing
git push -u origin feature/langfuse-tracing
git push -u origin feature/metrics-slo-alerts
git push -u origin feature/incident-runbooks
git push -u origin feature/dashboard-validation-bonus
```

### 4. Create Pull Requests

Each member creates a PR targeting `main`. At least **1 other member must review and approve** each PR before merging.

```bash
# Example: Võ Thiên Phú creates PR
gh pr create \
  --title "feat(logging): implement correlation ID and PII scrubbing" \
  --body "$(cat <<'EOF'
## Summary
- Implement CorrelationIdMiddleware with req-<8-char-hex> ID generation
- Register scrub_event PII processor in structlog pipeline
- Enrich all /chat logs with user_id_hash, session_id, feature
- Extend PII patterns: passport, national_id_vn, vietnamese_address

## Test plan
- [ ] Run validate_logs.py — score >= 80/100
- [ ] PII leaks = 0 (no email/phone/CC in logs)
- [ ] Correlation ID present in every log entry
EOF
)"
```

### 5. Merge Branches

After approval, merge each PR. Merge order does not matter (all target `main`).

```bash
# Merge via GitHub PR or:
git checkout main
git merge feature/logging-pii-scrubbing
git merge feature/langfuse-tracing
git merge feature/metrics-slo-alerts
git merge feature/incident-runbooks
git merge feature/dashboard-validation-bonus
git push origin main
```

---

## Git Commands Quick Reference

```bash
# Check current status
git status

# See what changed
git diff

# See commit history
git log --oneline --graph --all

# Stage files
git add <file>

# Commit with message
git commit -m "feat(scope): description"

# Push branch
git push -u origin <branch-name>

# Create PR (requires GitHub CLI)
gh pr create --title "Title" --body "Description"

# Check PR status
gh pr status

# Merge PR (after approval)
gh pr merge <pr-number>

# Pull latest main
git pull origin main
```

---

## GitHub Setup Requirements

Each team member needs:
1. **Git configured** with their name and email:
   ```bash
   git config --global user.name "Full Name"
   git config --global user.email "student@vinuni.edu.vn"
   ```
2. **GitHub CLI authenticated**:
   ```bash
   gh auth login
   ```
3. **Repository access** — ask the repo owner to add you as a collaborator if needed

---

## Evidence Checklist

For each member, the final `git log` must show:

| Member | Min Commits | Branch | PR Approved |
|--------|:-----------:|--------|:-----------:|
| Võ Thiên Phú | 3 | `feature/logging-pii-scrubbing` | Yes |
| Đào Hồng Sơn | 3 | `feature/langfuse-tracing` | Yes |
| Phan Dương Định | 3 | `feature/metrics-slo-alerts` | Yes |
| Phạm Minh Khang | 2 | `feature/incident-runbooks` | Yes |
| Nguyễn Anh Quân | 3 | `feature/dashboard-validation-bonus` | Yes |

Screenshots needed:
- [ ] `git log --oneline` showing all team members' commits
- [ ] At least one PR with approval (for grading)
- [ ] `git diff` for the most important commit in each branch
