# FAQ Store Support System - Observability Lab Report

> **Instruction**: Fill in all sections below. This report is for the mini online store FAQ assistant system. Preserve all tags (e.g., `[GROUP_NAME]`).

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: [Name] | Role: Logging & PII Scrubbing
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alert Configuration
  - Member D: [Name] | Role: Load Test & Dashboard Implementation
  - Member E: [Name] | Role: RCA & Demo Lead

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Baseline |
|---|---:|---|---:|
| Latency P95 | < 2000ms | 28d | FAQ retrieval + generation time |
| Error Rate | < 1% | 28d | FAQ tool failures + schema validation errors |
| Cost Budget | < $1.0/day | 1d | Mock LLM token estimation |
| Quality Score | > 0.80 | 28d | Heuristic: answer length + keyword match + no redaction leaks |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---


### Scenario 1: rag_slow
- [SYMPTOMS_OBSERVED]: p95 latency spike to >3000ms; customer notices slow FAQ answers
- [ROOT_CAUSE_PROVED_BY]: (Trace ID showing slow retrieval span; log line with latency_ms field)
- [FIX_ACTION]: (e.g., disable rag_slow incident, add caching, optimize corpus)
- [PREVENTIVE_MEASURE]: (e.g., alert on p95 > 2000ms; preload FAQ corpus)

### Scenario 2: tool_fail
- [SYMPTOMS_OBSERVED]: error_rate_pct jumps to >5%; logs show RuntimeError or TimeoutError
- [ROOT_CAUSE_PROVED_BY]: (Error type from logs; trace with failed span)
- [FIX_ACTION]: (Disable tool_fail incident; implement fallback answer template)
- [PREVENTIVE_MEASURE]: (Circuit breaker; error rate alert with 5m window)

### Scenario 3: cost_spike
- [SYMPTOMS_OBSERVED]: hourly_cost_usd doubles; tokens_out per request increase
- [ROOT_CAUSE_PROVED_BY]: (Trace showing high token_out; log with cost_usd field spike)
- [FIX_ACTION]: (Disable cost_spike; truncate response to max 200 tokens)
- [PREVENTIVE_MEASURE]: (Pre-compute answers as templates; alert on cost >$1/hour)

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence) 

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
