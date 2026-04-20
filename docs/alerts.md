# Alert Rules and Runbooks

Architecture: FastAPI chat endpoint - agent pipeline (retrieve + generate) - metrics collection

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 4000 for 10m`
- Impact: tail latency approaches SLO (3000ms), users experience slowness
- First checks:
  1. Open Langfuse - filter by duration > 4000ms
  2. Compare retrieve() span vs generate() span
  3. Check if `rag_slow` incident enabled: `curl http://localhost:8000/health | grep rag_slow`
- Mitigation:
  - If retrieve() slow: optimize RAG or cache results
  - If generate() slow: reduce doc count or use faster LLM
  - Disable incident if enabled

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Check error breakdown: `curl http://localhost:8000/metrics | grep error_breakdown`
  2. Check if `tool_fail` incident enabled: `curl http://localhost:8000/health | grep tool_fail`
  3. Inspect failed traces in Langfuse
  4. Find error type: `grep "error_type\|traceback" data/logs.jsonl | tail -10`
- Mitigation:
  - Disable tool_fail incident immediately
  - If mock_llm RuntimeError: check prompt format
  - If persistent: restart service and verify dependencies

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: burn rate exceeds budget
- First checks:
  1. Check token usage: `curl http://localhost:8000/metrics | grep tokens`
  2. Check if `cost_spike` incident enabled: `curl http://localhost:8000/health | grep cost_spike`
  3. Analyze tokens by feature in Langfuse traces
  4. Check request sizes: `grep "message" data/logs.jsonl | tail -10`
- Mitigation:
  - Disable cost_spike incident if enabled
  - Implement request size limits
  - Route expensive queries to cheaper model

## 4. Low quality score
- Severity: P3
- Trigger: `quality_score_avg < 0.75 for 15m`
- Impact: response quality degrading, users may regenerate
- First checks:
  1. Check current quality: `curl http://localhost:8000/metrics | grep quality`
  2. Review quality formula in agent.py: 0.5 base + 0.2 (docs) + 0.1 (length) + 0.1 (keywords) - 0.2 (PII)
  3. Analyze by feature in Langfuse
  4. Check PII redactions: `grep "pii_redacted" data/logs.jsonl`
- Mitigation:
  - If no docs retrieved: check RAG retrieval
  - If answers too short: adjust LLM prompt
  - If PII being redacted: review patterns in pii.py

