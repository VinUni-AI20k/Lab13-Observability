# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Impact: tail latency breaches SLO
- Dashboard to check: Latency P50/P95/P99 panel and Traffic panel.
- Relevant traces: Open the slowest Langfuse traces in the last 1 hour and inspect RAG vs LLM spans.
- Relevant logs: Search by `correlation_id`, then compare `latency_ms`, `feature`, `model`, and `session_id`.
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size
- Owner: team-oncall

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: users receive failed responses
- Dashboard to check: Error rate with breakdown panel and Traffic panel.
- Relevant traces: Filter failed traces and inspect the failing span or exception metadata.
- Relevant logs: Search `event=request_failed`, group by `error_type`, then follow the `correlation_id`.
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model
- Owner: team-oncall

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: burn rate exceeds budget
- Dashboard to check: Cost over time panel and Tokens in/out panel.
- Relevant traces: Split traces by `feature` and `model`, then compare token usage across requests.
- Relevant logs: Search `cost_usd`, `tokens_in`, `tokens_out`, `feature`, and `model`.
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache
- Owner: finops-owner

## 4. Low quality score
- Severity: P2
- Trigger: `quality_score_avg < 0.75 for 30m`
- Impact: responses may be too short, poorly grounded, or not useful enough for users.
- Dashboard to check: Quality proxy panel, Latency P95 panel, and Tokens in/out panel.
- Relevant traces: Inspect traces with low-quality answers and compare retrieved documents with the final response.
- Relevant logs: Search `quality_score`, `feature`, `model`, and `message_preview` using the same `correlation_id`.
- First checks:
  1. Check whether retrieval returned enough relevant context.
  2. Compare low-quality traces by feature and model.
  3. Verify that prompt compaction or cost optimization did not remove required context.
- Mitigation:
  - improve retrieval query terms
  - increase context budget for difficult questions
  - add quality regression examples to the test set
- Owner: model-quality-owner
