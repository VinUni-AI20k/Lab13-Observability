# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: [Hoàng Văn Kiên] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: Ha Huu An | Role: SLO & Alerts
  - Member D: [Name] | Role: Load Test & Incident Injection
  - Member E: [Name] | Role: Dashboard & Evidence
  - Member F: [Name] | Role: Blueprint & Demo Lead

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
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
- [DASHBOARD_6_PANELS_SCREENSHOT]: ![Alert Rules](/docs/images/C_alerts.png)

- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 2500ms | 28d | 2651ms |
| Error Rate | < 1% | 28d | 0% |
| Cost Budget | < $2.0/day | 1d | $0.0428 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: ![Alert Rules](/docs/images/C_alert_rules.png)
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md](/docs/alerts.md)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 tăng vọt lên 2651ms (vi phạm SLO 2500ms). Hệ thống phản hồi chậm rõ rệt.
- [ROOT_CAUSE_PROVED_BY]: Check /metrics thấy latency tăng sau khi kích hoạt scenario rag_slow.
- [FIX_ACTION]: Disable scenario rag_slow bằng lệnh inject_incident.
- [PREVENTIVE_MEASURE]: Tối ưu hóa việc caching kết quả RAG và hạ thấp prompt size khi phát hiện latency tăng.
---

## 5. Individual Contributions & Evidence

### [MEMBER_A: Hoàng Văn Kiên]
- [TASKS_COMPLETED]: logging + PII
- [EVIDENCE_LINK]: (https://github.com/tonhii/Nhom11-402-Day13/commit/ce432426f2a69610399324ed63d01f3a32862a09 )

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Ha Huu An
- [TASKS_COMPLETED]: Thiết lập SLO trong config/slo.yaml, cấu hình Alert Rules trong config/alert_rules.yaml, và hoàn thiện Runbook trong docs/alerts.md. Phân tích và xử lý sự cố rag_slow.
- [EVIDENCE_LINK]: [config/slo.yaml](file:///d:/VinAction/Nhom11-402-Day13/config/slo.yaml), [config/alert_rules.yaml](file:///d:/VinAction/Nhom11-402-Day13/config/alert_rules.yaml)
### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_F_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
