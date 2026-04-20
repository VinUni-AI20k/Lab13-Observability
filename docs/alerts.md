# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 2500 for 5m`
- Impact: tail latency is trending toward the 3s SLO
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size
- Test it:
  1. Enable `rag_slow`
  2. Send 10 requests
  3. Confirm `latency_p95` rises above 2500ms in `/metrics`

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model
- Test it:
  1. Enable `tool_fail`
  2. Send a few requests
  3. Confirm `error_breakdown` includes `RuntimeError`

## 3. Cost budget spike
- Severity: P2
- Trigger: `avg_cost_usd > 0.003 for 15m`
- Impact: request economics drift above the expected baseline
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache
- Test it:
  1. Enable `cost_spike`
  2. Send 10 requests
  3. Confirm `avg_cost_usd` increases in `/metrics`
