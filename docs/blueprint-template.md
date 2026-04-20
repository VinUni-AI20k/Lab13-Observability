# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- X3: 
- [https://github.com/BanBannBannn/Day13-C401-X3.git]: 
- [MEMBERS]:
  - Member A: Kiều Đức Lâm | Role: Logging & PII
  - Member B: Trần Văn Gia Bân | Role: Tracing & Enrichment
  - Member C: Võ Đại Phước | Role: SLO & Alerts
  - Member D: Nguyễn Tùng Lâm | Role: Load Test & Dashboard
  - Member E: Trần Phan Văn Nhân | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 26
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: .\docs\images\correlationid.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: .docs\images\evidencePII.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: .\docs\images\evidencetrace.png
- [TRACE_WATERFALL_EXPLANATION]: .\docs\images\tracewaterfall.png

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: .\docs\images\dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 503ms |
| Error Rate | < 2% | 28d | 0.15|
| Cost Budget | < $2.5/day | 1d | 0.00010$ |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: .\docs\images\alert.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency spiked, response time exceeded 3000ms SLO threshold
- [ROOT_CAUSE_PROVED_BY]: Log line with correlation_id req-c7d209f4 showing latency_ms > 3000
- [FIX_ACTION]: Disabled rag_slow incident toggle, truncated long queries
- [PREVENTIVE_MEASURE]: Add latency alert (alert_rules.yaml#high_latency_p95), fallback retrieval source


---

## 5. Individual Contributions & Evidence

### [Kiều Đức Lâm]

- [TASKS_COMPLETED]: logging + PII
- [EVIDENCE_LINK]: [\(Link to specific commit or PR)](https://github.com/BanBannBannn/Day13-C401-X3/commit/15362623edd3c3577c6bb4f4b88e34b4752b14b3)

### [Trần Văn Gia Bân]

- [TASKS_COMPLETED]: fix tracing.py
- [EVIDENCE_LINK]: https://github.com/BanBannBannn/Day13-C401-X3/tree/811405621b1c34ccca31645f37385d4e1bfa4e49

### [MEMBER_C_NAME]

- [TASKS_COMPLETED]:
- [EVIDENCE_LINK]:

### Nguyễn Tùng Lâm
- [TASKS_COMPLETED]:  UI(frontend)
- [EVIDENCE_LINK]: https://github.com/BanBannBannn/Day13-C401-X3/tree/Liam

### Trần Phan Văn Nhân
- [TASKS_COMPLETED]: Markdown
- [EVIDENCE_LINK]: https://github.com/BanBannBannn/Day13-C401-X3/tree/nhan-D

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
