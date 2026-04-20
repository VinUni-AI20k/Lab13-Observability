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
  - check metrics snapshot latency_p95 / latency_p99
  - inspect logs for slow response_sent events
  - inspect traces for slow retrieval span
- Immediate action:
  - confirm whether rag_slow incident was injected
  - reduce concurrency and retry
  - inspect retrieval component

## 2. Critical Latency P99
- Severity: P1
- Condition: latency_p99 > 2000 for 5m
- Meaning: Tail latency is severely degraded.
- Immediate action:
  - inspect worst requests
  - correlate with RAG/tool spans
  - mitigate load or disable incident

## 3. Tool or Pipeline Errors
- Severity: P1
- Condition: total_error_count > 0 for 2m
- Meaning: Requests are failing due to tool or pipeline issues.
- Likely causes:
  - tool_fail incident
  - vector/tool exception
- Verification:
  - inspect error_breakdown
  - inspect logs for failure event
- Immediate action:
  - identify failing component
  - disable failing incident or restart component

## 4. Cost Budget Spike
- Severity: P2
- Condition: total_cost_usd > 2.5
- Meaning: Token spending exceeds expected lab budget.
- Likely causes:
  - cost_spike incident
  - excessive output length
- Immediate action:
  - inspect tokens_out_total
  - reduce verbose output or cap max tokens

## 5. Quality Drop
- Severity: P2
- Condition: quality_avg < 0.75 for 10m
- Meaning: Answers are becoming less useful or less accurate.
- Immediate action:
  - review recent answers
  - inspect prompt/tool changes
  - compare with baseline quality