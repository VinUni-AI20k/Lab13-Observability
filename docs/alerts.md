# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- SLO: `latency_p95_ms < 3000ms` (see config/slo.yaml)
- Impact: tail latency breaches SLO; slow UX for top 5% of users
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span (which one is slow?)
  3. Check if incident toggle `rag_slow` is enabled: `GET /health` → incidents
  4. Check `latency_p95` in `/metrics` endpoint for current value
- Mitigation:
  - If `rag_slow` is enabled: `POST /incidents/rag_slow/disable`
  - Truncate long queries before sending to RAG
  - Switch to fallback retrieval source (lower-latency index)
  - Reduce prompt size to lower LLM processing time

---

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- SLO: `error_rate_pct < 2%` (see config/slo.yaml)
- Impact: users receive failed responses (HTTP 500)
- First checks:
  1. Check `error_breakdown` in `/metrics` endpoint to group by `error_type`
  2. Inspect failed traces in Langfuse (filter by `level=error`)
  3. Look at recent logs in `data/logs.jsonl` for `"event":"request_failed"`
  4. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - Rollback latest deployment if errors started after a deploy
  - Disable failing tool via incidents: `POST /incidents/tool_fail/disable`
  - Retry with fallback model if LLM provider is degraded
  - Check for schema validation errors in `error_type` field

---

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- SLO: `daily_cost_usd < $2.50` (see config/slo.yaml)
- Impact: burn rate exceeds budget; risk of daily cap breach
- First checks:
  1. Check `avg_cost_usd` and `total_cost_usd` in `/metrics`
  2. Split traces by feature and model in Langfuse
  3. Compare `tokens_in` vs `tokens_out` ratio (high tokens_in = long prompts)
  4. Check if `cost_spike` incident toggle is enabled: `GET /health`
- Mitigation:
  - Shorten system prompts / RAG context window
  - Route low-complexity requests to cheaper/smaller model
  - Apply prompt caching for repeated system prompt segments
  - If incident active: `POST /incidents/cost_spike/disable`

---

## 4. Quality score degradation
- Severity: P3
- Trigger: `quality_score_avg < 0.6 for 15m`
- SLO: `quality_score_avg >= 0.75` (see config/slo.yaml)
- Impact: users receive low-quality or unhelpful answers
- First checks:
  1. Check `quality_avg` in `/metrics` for current rolling value
  2. Review recent `response_sent` logs for low `quality_score` values
  3. Check if RAG is returning empty `doc_count` (metadata in traces)
  4. Verify answer length — short answers score lower heuristically
- Mitigation:
  - Verify RAG index health and connectivity
  - Improve retrieval by adding more documents to `data/` corpus
  - Review heuristic scoring function in `app/agent.py#_heuristic_quality`
  - Check if PII redaction is over-scrubbing answer content
