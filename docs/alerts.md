# Alert Rules and Runbooks (By Ha Huu An)

## 1. High latency P95
- **Severity:** P2
- **Trigger:** `latency_p95_ms > 3500 for 5m`
- **Impact:** Người dùng phản hồi hệ thống bị "treo" hoặc trả lời cực chậm.
- **First checks:**
  1. Kiểm tra Langfuse Tracing để xem bước nào chậm (RAG hay LLM).
  2. Kiểm tra log xem có query nào quá dài không (Long context).
- **Mitigation:** 
  - Kích hoạt fallback retrieval nếu RAG chậm.
  - Cắt bớt độ dài prompt gửi đi.

## 2. High error rate
- **Severity:** P1
- **Trigger:** `error_rate_pct > 2 for 2m`
- **Impact:** Người dùng không nhận được câu trả lời (Lỗi 500).
- **First checks:**
  1. Kiểm tra log tìm `error_type` (ví dụ: `RateLimitError` hay `SchemaValidationError`).
  2. Xác định xem lỗi do API LLM hay do code backend.
- **Mitigation:**
  - Chuyển sang sử dụng Model dự phòng (Model fallback).
  - Tạm thời tắt các công cụ (tools) đang gây lỗi.
