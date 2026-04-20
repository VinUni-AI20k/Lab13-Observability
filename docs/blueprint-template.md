# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: C401-A4-Day13
- [REPO_URL]: https://github.com/imdhiep/C401-A4-Day13
- [MEMBERS]:
  - Member A: Hoàng Thái Dương | Role: Logging & PII
  - Member B: Hoàng Quốc Chung | Role: Tracing & Enrichment
  - Member C: Trịnh Đức Anh | Role: SLO & Alerts
  - Member D: Bùi Văn Đạt | Role: Load Test & Dashboard
  - Member E: Nguyễn Minh Quân |Role: dashboard + evidence
  - Member F: Dương Văn Hiệp | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 15
- [PII_LEAKS_FOUND]: 0 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: evidence/correlation_ids.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: evidence/pii_redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: evidence/langfuse_trace_detail.png, evidence/langfuse_trace_list1.png,  evidence/langfuse_trace_list1.png 
- [TRACE_WATERFALL_EXPLANATION]: Each trace represents a complete `/chat` request with ~150ms latency. The trace includes enriched context (session_id, user_id_hash, feature type, environment), metadata (doc_count, query_preview), and usage details (input/output tokens). The @observe() decorator captures LabAgent.run() as the root span, demonstrating proper tracing integration with Langfuse for end-to-end observability.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: evidence/dashboard_6_panels.jpg, evidence/dashboard_6_panels_2.jpg
- [SLO_TABLE]:
| SLI         |     Target | Window | Current Value |
| ----------- | ---------: | ------ | ------------: |
| Latency P95 |   < 3000ms | 28d    |         192ms |
| Error Rate  |       < 2% | 28d    |            0% |
| Cost Budget | < $2.5/day | 1d     |       $0.0209 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: evidence/alert_rules_config.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: End-to-end latency increased from ~770ms to ~10620 (+ 1279%) when rag_slow incident enabled. All requests still succeed (HTTP 200).
- [ROOT_CAUSE_PROVED_BY]: Log records show latency_ms=150 at API layer unchanged, indicating slowdown in agent.retrieve() or mock_rag stage. Verified by enabling/disabling incident scenario and re-running load tests.
- [FIX_ACTION]: Disabled rag_slow incident. Latency returned to baseline ~722.
- [PREVENTIVE_MEASURE]: Set timeout threshold for RAG retrieval stage; trigger P2 alert if P95 latency exceeds 5000ms for 30m window (see config/alert_rules.yaml). 

---

## 5. Individual Contributions & Evidence

### [Hoàng Thái Dương]
- [TASKS_COMPLETED]: Implemented correlation ID middleware with unique req-xxxxx format. Enriched logs with user_id_hash, session_id, feature, model, env context. Enabled PII scrubbing processor to redact emails, phone numbers, and credit cards in logs.
- [EVIDENCE_LINK]: validate_logs.py output showing 100/100 score and PII scrubbing verification (Link to specific commit or PR)

### [Hoàng Quốc Chung]
- [TASKS_COMPLETED]: Configured Langfuse tracing integration with public/secret keys. Verified 15 traces captured with enriched metadata (session_id, user_id_hash, feature, environment). Each trace shows LabAgent.run() span with ~150ms latency and usage details (input/output tokens).
- [EVIDENCE_LINK]: Langfuse dashboard traces and trace detail screenshots 

### [Trịnh Đức Anh]
- [TASKS_COMPLETED]: Configured alert rules in config/alert_rules.yaml with 3 rules (high latency P95, high error rate, cost budget spike). Set SLO targets in config/slo.yaml (latency <3000ms, error <2%, cost <$2.5/day). Created runbooks in docs/alerts.md with mitigation steps.
- [EVIDENCE_LINK]: alert_rules.yaml and slo.yaml configurations 

### [Bùi Văn Đạt]
- [TASKS_COMPLETED]: Executed load testing with concurrency=5, generated 20 requests with correlation IDs. Enabled rag_slow incident, observed 37% latency increase from 813ms to 1100ms. Disabled incident, latency returned to baseline. Verified metrics aggregation and error-free operation.
- [EVIDENCE_LINK]: Load test terminal output and incident injection logs 

### [Nguyễn Minh Quân]
- [TASKS_COMPLETED]: Built 6-panel dashboard from /metrics endpoint showing latency P95 (192ms), error rate (0%), cost ($0.0417), traffic (20 requests), quality score (0.8), and token usage (824 in, 2616 out). Created SLO table with current values meeting targets.
- [EVIDENCE_LINK]: Google Sheets dashboard with 6 panels and SLO table screenshot 

### [Dương Văn Hiệp]
- [TASKS_COMPLETED]: Compiled blueprint report with all evidence, screenshots, and individual contributions. Led demo presentation covering logging/tracing, incident response, and dashboard walkthrough.
- [EVIDENCE_LINK]: demo recording + report

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
