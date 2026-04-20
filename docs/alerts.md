# Alert Runbooks: FAQ Store Support System

## 1. FAQ Retrieval Slowdown
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 10m`
- Impact: Customer support queries are taking too long; SLA breach risk
- **Root Cause Checklist:**
  1. Check if `rag_slow` incident toggle is enabled via `/health` endpoint
  2. Review traces from last 30m and compare retrieval span duration vs LLM span
  3. Check if knowledge base lookup tool is under load (concurrent queries spike)
  4. Verify network latency to knowledge backend
- **Immediate Mitigation:**
  - If `rag_slow` is on: disable via `POST /incidents/rag_slow/disable`
  - Cache recent FAQ answers to avoid repeated lookups
  - Reduce payload size in retrieval query
  - Fall back to generic answer template if retrieval > 2s
- **Long-term Fix:**
  - Optimize knowledge corpus indexing
  - Add caching layer for popular refund/shipping policy questions
  - Preload frequently accessed documents

## 2. FAQ Service Errors
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: **CRITICAL**: Customers cannot get FAQ answers; revenue impact
- **Root Cause Checklist:**
  1. Check if `tool_fail` incident toggle is enabled via `/health` endpoint
  2. Review logs grouped by `error_type` (e.g., RuntimeError, TimeoutError)
  3. Inspect traces to separate retrieval errors vs response generation errors
  4. Check customer input patterns (malformed requests, edge cases)
- **Immediate Mitigation:**
  - If `tool_fail` is on: disable via `POST /incidents/tool_fail/disable`
  - Return safe fallback message: "Our FAQ system is temporarily unavailable. Please contact support."
  - Retry failed queries with longer timeout (up to 5s)
  - Route to human support agent if auto-response fails
- **Long-term Fix:**
  - Add circuit breaker for knowledge tool
  - Implement graceful degradation (return cached answer if retrieval fails)
  - Add monitoring alerts for specific error types

## 3. Token Cost Spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: Unexpected cost growth; budget burn
- **Root Cause Checklist:**
  1. Check if `cost_spike` incident toggle is enabled via `/health` endpoint
  2. Review traces and compare `tokens_out` distribution (which queries generate long responses)
  3. Identify which intent category is driving cost (refund_policy, shipping, warranty, etc)
  4. Check if verbose mode or extra explanation is enabled
- **Immediate Mitigation:**
  - If `cost_spike` is on: disable via `POST /incidents/cost_spike/disable`
  - Shorten answer templates (remove redundant policy details)
  - Truncate responses after key answer (max 200 tokens output)
  - Route summary requests to cheaper model or template
- **Long-term Fix:**
  - Pre-compute FAQ answers and store as templates (no LLM generation)
  - Implement prompt caching for common policy questions
  - Set token output limit per request (max 300 tokens)
  - Monitor cost-per-query by feature and optimize high-cost categories
