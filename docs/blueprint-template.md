# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: [Name] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: [Name] | Role: Load Test & Dashboard
  - Member E: Nguyễn Văn Đạt (2A202600411) | Role: Dashboard & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/evidence/evidence-correlation-id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/evidence/evidence-pii-redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/evidence/evidence-trace-waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/evidence/evidence-dashboard-6-panels.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 2500ms | 28d | |
| Error Rate | < 1% | 28d | |
| Cost Budget | < $2.0/day | 1d | |
| Quality Score | >= 0.75 | 28d | |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency tăng từ ~200ms lên ~2700ms khi user search "tracking đơn hàng" / "refund policy" trong giờ sale. Dashboard panel Latency P95 breach SLO 2500ms.
- [ROOT_CAUSE_PROVED_BY]: Trace waterfall cho thấy span `retrieve` trên product catalog mất 2.5s; LLM span chỉ 150ms. Log line `grep rag_slow data/logs.jsonl` xác nhận `incident_enabled: rag_slow`.
- [FIX_ACTION]: `python scripts/inject_incident.py --scenario rag_slow --disable`. Production fix: thêm timeout 1s + fallback catalog cache cho vector store.
- [PREVENTIVE_MEASURE]: Alert rule `latency_p95_ms > 2500` trigger runbook; circuit breaker cho RAG vector store khi p95 > 2s liên tiếp 3 phút.

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

### Nguyễn Văn Đạt (2A202600411)
- [TASKS_COMPLETED]:
  - Implement dashboard 6 panels tại `/dashboard` endpoint (HTML + SVG sparklines, auto-refresh 15s, SLO threshold lines)
  - Thêm `/dashboard-data` API endpoint trả `snapshot`, `history`, `slo_targets`, `raw_logs`, `incidents` từ `data/logs.jsonl`
  - Nâng cấp `app/metrics.py`: thêm `METRIC_HISTORY`, `_append_history_point()`, `history()`, `error_rate_pct()` để dashboard có time-series data
  - Cập nhật `config/slo.yaml` với group target: P95 < 2500ms, error < 1%, cost < $2/day
  - Tạo `docs/evidence/` với screenshot dashboard 6 panels
- [EVIDENCE_LINK]: (Link to specific commit or PR)

#### Giải thích kỹ thuật (B1 — Individual Report Quality)

**Cách tính P95:**
P95 (percentile thứ 95) là giá trị latency mà 95% requests hoàn thành trong thời gian đó hoặc nhanh hơn. Công thức trong `metrics.py`:
```python
items = sorted(values)
idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
return float(items[idx])
```
Ví dụ: 100 requests, sort latency, lấy phần tử thứ 95 → đó là P95. Nếu P95 = 2700ms > SLO 2500ms thì dashboard hiện badge "Attention Required" màu cam.

**Dashboard architecture:**
- `/dashboard-data` đọc `data/logs.jsonl`, filter theo `window_seconds`, tính metrics từ log events `response_sent` và `request_failed`, build `history_points` theo thứ tự thời gian.
- `/dashboard` phục vụ HTML tĩnh với JavaScript `fetch("/dashboard-data")` mỗi 15 giây, render 6 SVG sparklines. SLO line được vẽ bằng `<line stroke-dasharray="5 3">` màu amber trên mỗi chart.
- **6 panels**: (1) Latency P50/P95/P99 + SLO line, (2) Traffic req/min, (3) Error rate % + breakdown JSON, (4) Cost USD cumulative + budget line, (5) Tokens in/out total, (6) Quality score avg + target threshold.

**`METRIC_HISTORY` design:**
Giới hạn 120 điểm (xóa điểm cũ nhất khi vượt) để tránh memory leak trong long-running server. `history()` trả 60 điểm gần nhất cho sparklines đủ mượt mà không quá nặng.

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
