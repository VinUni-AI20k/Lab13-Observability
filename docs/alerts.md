# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3500 for 10m`
- Impact: tail latency breaches SLO
- First checks:
  1. Open `/metrics` and confirm `latency_p95` trend is sustained
  2. Open top slow traces in the last 1h, compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries and lower prompt size
  - fallback retrieval source for low-confidence retrieval
  - set temporary rate limit for high-latency feature paths

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 3 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Check if incident toggle `tool_fail` is enabled and isolate failing step
- Mitigation:
  - rollback latest change
  - disable failing tool/branch in the pipeline
  - retry with fallback model

## 3. Cost budget spike
- Severity: P2
- Trigger: `avg_cost_usd > 0.06 for 15m`
- Impact: burn rate exceeds budget
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts and response length
  - route easy requests to cheaper model
  - apply prompt cache
