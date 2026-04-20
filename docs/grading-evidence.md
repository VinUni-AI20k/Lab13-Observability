# 📊 Bảng Theo Dõi Tiến Độ & Bằng Chứng (Team Dashboard)

> **Hướng dẫn cho Team**: Mỗi thành viên sau khi hoàn thành Task của mình, hãy cập nhật link ảnh/commit và đổi trạng thái sang ✅ vào file này. Member F sẽ căn cứ vào đây để tổng hợp báo cáo Blueprint.

## 📈 Trạng thái tổng quát
| Thành viên | Vai trò | Trạng thái | Ghi chú |
|---|---|---|---|
| **A** | Logging & PII | 🟦 Pending | |
| **B** | Tracing & Tags | 🟦 Pending | |
| **C** | SLO & Alerts | 🟦 Pending | |
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
- [ ] **Alert rules screenshot**: `[Link ảnh]`
- [ ] **Link Runbook**: `[docs/alerts.md#L...]`
- [ ] **SLO Results**: `Latency: ..., Error: ..., Cost: ...`

### 👤 Member D: Load Test & Incident
- [x] **Scenario đã chạy**: `rag_slow` / `tool_fail` / `cost_spike`
- [x] **Kết quả từng scenario**:
  | Scenario | HTTP Status | Latency P95 | Tokens Out | Error Count |
  |---|---|---|---|---|
  | Baseline (normal) | 200 OK | **~815 ms** | ~278/req | 0 |
  | `rag_slow` | 200 OK | **~13 294 ms** (+16×) | ~278/req | 0 |
  | `tool_fail` | **500 Error** | ~50 ms | — | **10/10 failed** |
  | `cost_spike` | 200 OK | ~789 ms | **~571/req** (+4×) | 0 |
- [x] **Bằng chứng lỗi (Root Cause — `tool_fail`)**:
  ```json
  {"service":"api","error_type":"RuntimeError","payload":{"detail":"Vector store timeout"},"event":"request_failed","session_id":"s01","correlation_id":"req-7997d76f","user_id_hash":"2055254ee30a","feature":"qa","env":"dev","level":"error","ts":"2026-04-20T08:27:35.049818Z"}
  ```
  → `error_type: RuntimeError` + `detail: "Vector store timeout"` xác nhận RAG layer bị lỗi.
- [x] **Metrics snapshot khi `cost_spike`**: `avg_cost_usd` tăng từ **$0.0022 → $0.0038/req**, `tokens_out_total` tăng từ ~278 → ~571 token/req (×4 đúng như thiết kế incident).
- [x] **Ảnh Dashboard khi có lỗi**: ![D_incident_tool_fail](images/D_incident_tool_fail.png)

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
