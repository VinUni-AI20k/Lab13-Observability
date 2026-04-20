# 📊 Bảng Theo Dõi Tiến Độ & Bằng Chứng (Team Dashboard)

> **Hướng dẫn cho Team**: Mỗi thành viên sau khi hoàn thành Task của mình, hãy cập nhật link ảnh/commit và đổi trạng thái sang ✅ vào file này. Member F sẽ căn cứ vào đây để tổng hợp báo cáo Blueprint.

## 📈 Trạng thái tổng quát
| Thành viên | Vai trò | Trạng thái | Ghi chú |
|---|---|---|---|
| **A** | Logging & PII | 🟦 Pending | |
| **B** | Tracing & Tags | 🟦 Pending | |
| **C** | SLO & Alerts | 🟦 Pending | |
| **D** | Load Test & Incident | 🟦 Pending | |
| **E** | Dashboard & Evidence | 🟦 Pending | |
| **F** | Blueprint & Demo | 🟦 Pending | Chốt báo cáo sau cùng |

---

## 🛠 Chi tiết bằng chứng theo vai trò

### 👤 Member A: Logging & PII
- [ ] **JSON logs showing correlation_id**: `[Dán link ảnh hoặc log mẫu ở đây]`
- [ ] **Log line with PII redaction**: `[Dán link ảnh ở đây]`
- [ ] **Validation Score**: `.../100` (Chạy `python scripts/validate_logs.py`)

### 👤 Member B: Tracing & Enrichment
- [ ] **Langfuse trace list (>= 10 traces)**: `[Link ảnh]`
- [ ] **One full trace waterfall**: `[Link ảnh]`
- [ ] **Trace ID tiêu biểu**: `[ID]` (Dùng để giải thích span trong báo cáo)

### 👤 Member C: SLO & Alerts
- [ ] **Alert rules screenshot**: `[Link ảnh]`
- [ ] **Link Runbook**: `[docs/alerts.md#L...]`
- [ ] **SLO Results**: `Latency: ..., Error: ..., Cost: ...`

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
