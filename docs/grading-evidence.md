# 📊 Bảng Theo Dõi Tiến Độ & Bằng Chứng (Team Dashboard)

> **Hướng dẫn cho Team**: Mỗi thành viên sau khi hoàn thành Task của mình, hãy cập nhật link ảnh/commit và đổi trạng thái sang ✅ vào file này. Member F sẽ căn cứ vào đây để tổng hợp báo cáo Blueprint.

## 📈 Trạng thái tổng quát
| Thành viên | Vai trò | Trạng thái | Ghi chú |
|---|---|---|---|
| **A** | Logging & PII | 🟦 Pending | |
| **B** | Tracing & Tags | 🟦 Pending | |
| **C** | SLO & Alerts | ✅ Done | Alert Rules & Runbook completed (P95: 151ms) |
| **D** | Load Test & Incident | ✅ Done | 3 scenarios: rag_slow, tool_fail, cost_spike |
| **E** | Dashboard & Evidence | 🟦 Pending | |
| **F** | Blueprint & Demo | 🟦 Pending | Chốt báo cáo sau cùng |

---

## 🛠 Chi tiết bằng chứng theo vai trò

### 👤 Member A: Logging & PII
- [X] **JSON logs showing correlation_id**: ![logs](/docs/images/A_logs.png)
- [X] **Log line with PII redaction**: ![alt text](/docs/images/A_pii_redacted.png)
{"service": "api", "payload": {"message_preview": "Ch\u00e0o ad, email c\u1ee7a t\u00f4i l\u00e0 [REDACTED_EMAIL] v\u00e0 [REDACTED_ADDRESS_VN] \u0111i\u1ec7n tho\u1ea1i l..."}, "event": "request_received", "model": "gpt-4", "env": "dev", "user_id_hash": "7f56369cbde6", "feature": "customer_support", "session_id": "session_alpha_99", "correlation_id": "req-20fb636f", "level": "info", "ts": "2026-04-20T08:29:35.374780Z"}
- [X] **Validation Score**: `100/100` (Chạy `python scripts/validate_logs.py`)
![alt text](/docs/images/A_validation_score.png)

### 👤 Member B: Tracing & Enrichment
- [ ] **Langfuse trace list (>= 10 traces)**: `[Link ảnh]`
- [ ] **One full trace waterfall**: `[Link ảnh]`
- [ ] **Trace ID tiêu biểu**: `[ID]` (Dùng để giải thích span trong báo cáo)

### 👤 Member C: SLO & Alerts
- [x] **Alert rules screenshot**: ![Alert Rules](/docs/images/C_alert_rules.png)
- [x] **Link Runbook**: [docs/alerts.md](/docs/alerts.md)
- [x] **SLO Results**: `Latency P95: 151ms, Error Rate: 0%, Cost: $0.0399, Quality: 0.88`

### 👤 Member D: Load Test & Incident
- [ ] **Scenario đã chạy**: `[Vd: rag_slow / llm_outage]`
- [ ] **Bằng chứng lỗi (Root Cause)**: `[Mã log hoặc Trace ID tìm thấy lỗi]`
- [ ] **Trạng thái hệ thống trên Dashboard khi có lỗi**: `[Link ảnh]`

### 👤 Member E: Dashboard & Evidence
- [ ] **Dashboard (Đủ 6 panels)**: `[Link ảnh]`
- [ ] **Cấu trúc thư mục ảnh**: ✅ Sạch sẽ, đúng quy định.

---

## 📂 Quy định lưu trữ ảnh bằng chứng
- **Vị trí**: Lưu vào thư mục `docs/images/`
- **Định dạng tên**: `[Member]_[Mo_ta].png`
  - Vd: `A_pii_redacted.png`, `B_trace_waterfall.png`, `E_dashboard_all.png`
- **Lưu ý**: Chụp ảnh rõ nét, chỉ tập trung vào phần cần chứng minh, không để lộ thông tin nhạy cảm khác.

---

## 🔗 Liên kết nhanh phục vụ báo cáo
| Mục tiêu | Tài liệu tham khảo |
|---|---|
| Mẫu báo cáo cuối | [blueprint-template.md](./blueprint-template.md) |
| Tiêu chí chấm điểm | [day13-rubric-for-instructor.md](../day13-rubric-for-instructor.md) |
| Đặc tả Dashboard | [dashboard-spec.md](./dashboard-spec.md) |
