# Alert Rules and Runbooks

> Each runbook follows the **Detect → Triage → Mitigate → Prevent** pattern.
> Incident toggles: `rag_slow`, `tool_fail`, `cost_spike` (see `data/incidents.json`).

---

## 1. High latency P95

- **Alert name**: `high_latency_p95`
- **Severity**: P2 (investigate within 30 minutes)
- **Trigger**: `latency_p95_ms > 1500 for 10m`
- **SLO**: P95 latency < 1000ms (99.5% of 28-day window)
- **Impact**: Tail latency breaches SLO; users experience slow responses

### Detection
- Dashboard Panel 1 (Latency P50/P95/P99) shows P95 crossing the 1000ms SLO line
- `/metrics` endpoint: check `latency_p95` and `latency_p99`
- Langfuse: filter traces by duration > 1000ms

### Triage
1. Open the **slowest traces** in Langfuse from the last 1 hour
2. Compare the **RAG span** duration vs **LLM span** duration
   - If RAG span > 2000ms → retrieval is the bottleneck (likely `rag_slow` incident)
   - If LLM span > 2000ms → model inference is slow
3. Check incident toggles: `GET /health` → look at `incidents.rag_slow`
4. Check recent log entries: filter by `latency_ms > 1000` in `data/logs.jsonl`

### Mitigation
1. **If `rag_slow` is enabled**: Disable it: `POST /incidents/rag_slow/disable`
2. **If organic**: Truncate long queries before sending to RAG
3. Fallback to a simpler retrieval source
4. Lower prompt size to reduce LLM processing time

### Prevention
- Set up auto-scaling for the retrieval layer
- Add a circuit breaker with timeout (e.g., 2s max for RAG)
- Cache frequent queries

---

## 2. High error rate

- **Alert name**: `high_error_rate`
- **Severity**: P1 (page on-call immediately)
- **Trigger**: `error_rate_pct > 1 for 5m`
- **SLO**: Error rate < 1% (99.0% of 28-day window)
- **Impact**: Users receive 500 errors; complete request failure

### Detection
- Dashboard Panel 3 (Error Rate) shows spike above 1%
- `/metrics` endpoint: check `error_breakdown` for error types
- Logs: filter for `"level": "error"` in `data/logs.jsonl`

### Triage
1. Group logs by `error_type` to identify the failure pattern:
   - `RuntimeError` → likely `tool_fail` incident (Vector store timeout)
   - `ValidationError` → schema mismatch in request/response
   - `TimeoutError` → upstream service unresponsive
2. Inspect **failed traces** in Langfuse (filter by status = error)
3. Check incident toggles: `GET /health` → look at `incidents.tool_fail`
4. Check if the error correlates with a specific `feature` or `user_id_hash`

### Mitigation
1. **If `tool_fail` is enabled**: Disable it: `POST /incidents/tool_fail/disable`
2. **If organic**: Rollback the latest code change
3. Disable the failing tool/retrieval source
4. Switch to a fallback model or return a cached response

### Prevention
- Add retry logic with exponential backoff for tool calls
- Implement circuit breaker pattern for external dependencies
- Add canary deployments to catch errors before full rollout

---

## 3. Cost budget spike

- **Alert name**: `cost_budget_spike`
- **Severity**: P2 (investigate within 30 minutes)
- **Trigger**: `hourly_cost_usd > 2x_baseline for 15m`
- **SLO**: Daily cost < $5.00 (100% adherence)
- **Impact**: Token burn rate exceeds budget allocation

### Detection
- Dashboard Panel 4 (Cost Over Time) shows sharp cost increase
- `/metrics` endpoint: compare `avg_cost_usd` against baseline ($0.0021)
- Langfuse: check `usage_details.output` for abnormally high token counts

### Triage
1. Split traces by **feature** and **model** in Langfuse to isolate the source
2. Compare `tokens_in` vs `tokens_out` — check if output tokens are abnormal
   - Normal output: 80–180 tokens → ~$0.002/req
   - `cost_spike` active: 320–720 tokens → ~$0.008/req (4x)
3. Check incident toggles: `GET /health` → look at `incidents.cost_spike`
4. Check if a specific user or feature is driving the cost spike

### Mitigation
1. **If `cost_spike` is enabled**: Disable it: `POST /incidents/cost_spike/disable`
2. **If organic**: Shorten system prompts to reduce token usage
3. Route simple queries (e.g., `feature=summary`) to a cheaper model
4. Apply prompt caching for repeated queries

### Prevention
- Set per-user token budgets
- Implement request-level cost guards (reject if estimated cost > threshold)
- Use tiered models: cheap model for simple queries, expensive for complex

---

## 4. Low quality score

- **Alert name**: `low_quality_score`
- **Severity**: P2 (investigate within 30 minutes)
- **Trigger**: `quality_score_avg < 0.70 for 15m`
- **SLO**: Quality score average ≥ 0.70 (95.0% of 28-day window)
- **Impact**: Answer quality degradation; users receive poor or irrelevant responses

### Detection
- Dashboard Panel 6 (Quality Proxy) shows average dropping below 0.70
- `/metrics` endpoint: check `quality_avg`
- Langfuse: check `metadata.doc_count` — if frequently 0, RAG is failing

### Triage
1. Check if RAG is returning empty results (`doc_count: 0` in trace metadata)
   - This drops quality score from ~0.88 to ~0.60
2. Check if answers are unusually short (< 40 chars loses 0.1 quality points)
3. Check if PII redaction is being applied to answers (loses 0.2 quality points)
4. Look for keyword overlap failures between questions and answers

### Mitigation
1. Expand the RAG corpus with more domain documents
2. Broaden keyword matching in `mock_rag.py` to catch more queries
3. Tune the LLM prompt to produce longer, more relevant answers
4. Review PII patterns to avoid over-redaction

### Prevention
- Add automated quality regression tests with expected answer benchmarks
- Monitor `doc_count` as a leading indicator for quality degradation
- Use human feedback (thumbs up/down) as a secondary quality signal

---

## 5. Token budget exceeded

- **Alert name**: `token_budget_exceeded`
- **Severity**: P3 (informational, investigate during business hours)
- **Trigger**: `tokens_out_total > 50000 in 1h`
- **SLO**: Leading indicator for `daily_cost_usd`
- **Impact**: Approaching daily cost budget; early warning before budget breach

### Detection
- Dashboard Panel 5 (Tokens In/Out) shows rapid accumulation
- `/metrics` endpoint: check `tokens_out_total`
- This alert fires *before* the cost alert, giving time to react

### Triage
1. Check the current request rate (`traffic` from `/metrics`)
2. Calculate the projected hourly cost: `tokens_out_total / 1,000,000 * 15`
3. Identify the top users/features consuming tokens in Langfuse
4. Determine if the trend is sustained or a burst

### Mitigation
1. Apply rate limiting to high-volume users
2. Implement response length caps (e.g., `max_tokens = 150`)
3. Route lower-priority requests to a queue for batch processing

### Prevention
- Set up per-user and per-feature token quotas
- Implement progressive rate limiting that tightens as budget usage increases
- Add cost estimation to request preprocessor (reject expensive requests early)

