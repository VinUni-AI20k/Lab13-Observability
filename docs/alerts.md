# Alert Rules and Runbooks

Architecture: FastAPI chat endpoint - agent pipeline (retrieve + generate) - metrics collection

## Alert 1: High Latency P95 (> 4000ms for 10 minutes)

SLO target: 3000ms. Alert at 4000ms provides 33% buffer.

Diagnosis:
1. Check if rag_slow incident enabled:
   curl http://localhost:8000/health | grep rag_slow

2. Check Langfuse traces for bottleneck:
   - Retrieve time + Generate time = total latency
   - If retrieve ~5ms, generate ~4000ms: LLM is slow
   - If retrieve ~4000ms, generate ~100ms: RAG is slow

3. Check error logs:
   grep "error\|failed" data/logs.jsonl

Action:
- Disable incident if enabled
- If LLM slow: reduce context size or use faster model
- If RAG slow: optimize retrieval or cache results

---

## Alert 2: High Error Rate (> 5% for 5 minutes) - CRITICAL

SLO target: 2% error rate.

Diagnosis:
1. Check error types:
   curl http://localhost:8000/metrics | grep error_breakdown

2. Check if tool_fail incident enabled:
   curl http://localhost:8000/health | grep tool_fail

3. Check which operation failed:
   grep "error_type\|traceback" data/logs.jsonl | tail -10

4. Check Langfuse for failed traces

Action:
- Disable tool_fail incident immediately
- If RuntimeError in mock_llm: check prompt format
- If persistent: restart service and verify dependencies

---

## Alert 3: Cost Spike (> 2x baseline for 15 minutes)

SLO target: daily cost $2.5.

Diagnosis:
1. Check current token usage:
   curl http://localhost:8000/metrics | grep tokens

2. Check if cost_spike incident enabled:
   curl http://localhost:8000/health | grep cost_spike

3. Analyze by feature in Langfuse traces

4. Check request sizes:
   grep "message" data/logs.jsonl | tail -10

Action:
- Disable cost_spike incident if enabled
- Implement request size limits if users sending long queries
- Route expensive queries to cheaper model if needed

---

## Alert 4: Low Quality Score (< 0.75 for 15 minutes)

SLO target: quality score 0.75.

Diagnosis:
1. Check current quality metrics:
   curl http://localhost:8000/metrics | grep quality

2. Review quality calculation in agent.py:
   Base 0.5 + 0.2 (docs retrieved) + 0.1 (answer length) + 0.1 (keywords) - 0.2 (PII issues)

3. Check traces by feature

4. Check logs for PII redactions:
   grep "pii_redacted" data/logs.jsonl

Action:
- If no docs retrieved: check RAG retrieval
- If answers too short: adjust LLM prompt
- If PII being redacted: review patterns in pii.py

---

## Configuration Mapping

SLO targets (config/slo.yaml) to alert thresholds (config/alert_rules.yaml):

1. Latency P95: SLO 3000ms, alert 4000ms (33% buffer)
2. Error rate: SLO 2%, alert 5% (150% buffer)
3. Daily cost: SLO $2.5, alert 2x baseline
4. Quality: SLO 0.75, alert below 0.75

Debug endpoints:
- GET /health: shows enabled incidents
- GET /metrics: shows current metric values
- data/logs.jsonl: structured request logs
- Langfuse UI: trace visualization and analysis
