# Alert Rules and Runbooks
> **Note**: These runbooks are tailored to our specific architecture: 
> FastAPI → Agent Pipeline (RAG retrieve + LLM generate) → Metrics

## 1. High latency P95 (> 4000ms for 10min)
**Why this matters:** P95 latency approaching SLO (3000ms). Gives 33% buffer before SLO breach.

**Root cause check (in order):**
1. Check if `rag_slow` incident is enabled:
   ```bash
   curl http://localhost:8000/health | grep rag_slow
   # If "rag_slow": true → This is the problem!
   ```

2. If not, analyze traces to find bottleneck:
   ```bash
   # Open Langfuse → Last 1 hour → Filter by duration > 4000ms
   # Look at the span breakdown:
   - If retrieve() ~ 5ms + generate() ~ 26000ms → **LLM is slow**
   - If retrieve() ~ 5000ms + generate() ~ 1000ms → **RAG is slow**
   ```

3. Check logs for errors:
   ```bash
   grep "error_type\|request_failed" data/logs.jsonl | tail -20
   ```

**Mitigation actions:**
- **If RAG slow:** Disable RAG temporarily, or cache common queries
- **If LLM slow:** Use faster LLM model, reduce prompt size (lower doc_count)
- **If test incident:** Disable with `curl -X POST http://localhost:8000/incidents/rag_slow/disable`

---

## 2. High error rate (> 5% for 5min) - **P1 CRITICAL**
**Why this matters:** Users can't get responses. Service is down.

**Root cause check:**
1. See which error type is happening:
   ```bash
   # Check metrics endpoint
   curl http://localhost:8000/metrics | grep error_breakdown
   # Example: {"RuntimeError": 10, "ValueError": 2}
   ```

2. Check if `tool_fail` incident is enabled:
   ```bash
   curl http://localhost:8000/health | grep tool_fail
   # If "tool_fail": true → Disable it: 
   # curl -X POST http://localhost:8000/incidents/tool_fail/disable
   ```

3. Inspect logs for error details:
   ```bash
   grep "error_type.*RuntimeError\|request_failed" data/logs.jsonl | tail -5
   # Shows what went wrong in agent.run()
   ```

4. Check traces for failed spans:
   ```bash
   # Langfuse → Filter failed traces (red status)
   # Look for: mock_llm.generate() or retrieve() exceptions
   ```

**Mitigation actions:**
- **If RuntimeError:** Check mock_llm.generate() - may need to fix prompt format
- **If tool_fail incident enabled:** Disable immediately with incident API
- **If persistent:** Restart app, check dependencies (mock LLM, mock RAG)

---

## 3. Cost spike (hourly_cost > 2x baseline for 15min) - **P2**
**Why this matters:** Unexpected expense spike could exhaust monthly budget.

**Root cause check:**
1. Compare tokens to baseline:
   ```bash
   # Check metrics
   curl http://localhost:8000/metrics | grep -E "tokens_in|tokens_out|avg_cost"
   # If tokens_out >> normal → User sent longer message
   ```

2. Check if `cost_spike` incident is enabled:
   ```bash
   curl http://localhost:8000/health | grep cost_spike
   # If "cost_spike": true → This simulates higher token output
   ```

3. Analyze which feature is expensive:
   ```bash
   # Langfuse → Filter by tags (feature=search vs feature=qa)
   # Compare tokens_in/tokens_out by feature
   ```

4. Check request payload size:
   ```bash
   grep "message_preview" data/logs.jsonl | tail -10
   # Long messages = more context = higher cost
   ```

**Mitigation actions:**
- **If cost_spike incident:** Disable with `curl -X POST http://localhost:8000/incidents/cost_spike/disable`
- **If users sending long queries:** Implement query truncation (max 500 chars)
- **If feature too expensive:** Route simple queries to cheaper model
- **General:** Monitor daily cost budget, set hourly alert threshold

---

## Summary: Alert → Debug Flow

| Alert | 1st Check | 2nd Check | Action |
|-------|-----------|-----------|--------|
| **High Latency** | `curl /health` for rag_slow | Langfuse trace breakdown | Disable incident OR optimize LLM |
| **High Error Rate** | Check error_breakdown metrics | Inspect logs + failed traces | Disable tool_fail OR restart app |
| **Cost Spike** | Check cost_spike incident | Compare tokens by feature | Disable incident OR truncate queries |

**Key metric endpoints:**
- Health: `GET /health` → see incidents enabled
- Metrics: `GET /metrics` → see latency_p95, error_breakdown, avg_cost
- Logs: `data/logs.jsonl` → see detailed request flow
- Traces: Langfuse UI → see span breakdown
