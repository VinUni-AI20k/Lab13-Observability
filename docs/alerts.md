# Alert Rules and Runbooks

## 1. High Latency P95
- Severity: P2
- Condition: latency_p95 > 1000 for 5m
- Meaning: Most requests are slower than expected, likely due to retrieval slowdown or downstream bottlenecks.
- Likely causes:
  - rag_slow incident enabled
  - increased concurrency
  - slow tool or vector store
- Verification:
  - check metrics snapshot: latency_p95, latency_p99
  - inspect logs for high latency_ms in response_sent events
  - (if enabled) inspect traces for slow retrieval span
- Immediate action:
  - confirm whether rag_slow incident was injected
  - reduce load (lower concurrency)
  - isolate slow component (RAG / tool)

---

## 2. Critical Latency P99
- Severity: P1
- Condition: latency_p99 > 2000 for 5m
- Meaning: Tail latency is severely degraded (worst-case requests are very slow).
- Likely causes:
  - extreme slowdown in RAG or LLM
  - uneven load distribution
- Verification:
  - compare latency_p95 vs latency_p99 (if p99 >> p95 → tail issue)
  - inspect slowest requests in logs
- Immediate action:
  - identify worst-case requests
  - check if incident (rag_slow) is active
  - reduce concurrency or disable incident

---

## 3. Tool or Pipeline Errors
- Severity: P1
- Condition: total_error_count > 0 for 2m
- Meaning: Requests are failing due to tool or pipeline issues.
- Likely causes:
  - tool_fail incident
  - vector store or tool exception
- Verification:
  - inspect error_breakdown in metrics snapshot
  - inspect logs for error events
- Immediate action:
  - identify failing component from error type
  - disable failing incident or restart component
  - re-run test to confirm recovery

---

## 4. Cost Budget Spike
- Severity: P2
- Condition: total_cost_usd > 2.5
- Meaning: Token spending exceeds expected lab budget.
- Likely causes:
  - cost_spike incident
  - excessive output tokens
- Verification:
  - check tokens_out_total and avg_cost_usd
  - compare before/after incident
- Immediate action:
  - reduce output length (max tokens)
  - inspect prompt causing verbose output
  - confirm if cost_spike scenario is active

---

## 5. Quality Drop
- Severity: P2
- Condition: quality_avg < 0.75 for 10m
- Meaning: Answers are becoming less useful or less accurate.
- Likely causes:
  - degraded prompt quality
  - RAG returning irrelevant context
- Verification:
  - inspect recent responses in logs
  - compare quality score trend
- Immediate action:
  - review recent answers manually
  - check RAG relevance
  - adjust prompt or context retrieval