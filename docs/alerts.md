# Alert Rules and Runbooks

> **Runbook** là tài liệu hướng dẫn kỹ sư oncall (người trực) xử lý khi alert kích hoạt.
> Mỗi alert PHẢI có runbook — nếu không, oncall sẽ hoảng loạn lúc 3h sáng.

---

## 1. High latency P95
- **Severity**: P2 (Warning)
- **Trigger**: `latency_p95_ms > 5000 for 30m`
- **Impact**: 5% user chịu latency > 5 giây → trải nghiệm xấu, có thể bỏ session
- **SLO liên quan**: `latency_p95_ms < 3000ms, target 99.5%`
- **First checks** (kiểm tra theo thứ tự):
  1. Mở Dashboard → panel Latency → xác nhận P95 thực sự > 5000ms (không phải false alarm)
  2. Mở Langfuse → lọc traces chậm nhất trong 1h qua → so sánh RAG span vs LLM span
  3. Kiểm tra incident toggle: `GET /health` → xem `rag_slow` có đang `true` không
  4. Kiểm tra log: lọc theo `correlation_id` của request chậm nhất → đọc chi tiết
- **Mitigation** (cách xử lý):
  - Nếu RAG chậm → truncate query dài, dùng fallback retrieval source
  - Nếu LLM chậm → giảm prompt size, set timeout thấp hơn
  - Nếu do incident toggle → `python scripts/inject_incident.py --scenario rag_slow --disable`
- **Escalation**: nếu không giải quyết trong 1h → escalate lên P1

---

## 2. High error rate
- **Severity**: P1 (Critical — khẩn cấp!)
- **Trigger**: `error_rate_pct > 5 for 5m`
- **Impact**: User nhận response lỗi (HTTP 500) → mất niềm tin → churn
- **SLO liên quan**: `error_rate_pct < 2%, target 99%`
- **First checks**:
  1. `GET /metrics` → xem `error_breakdown` → lỗi Runtime? Timeout? Schema?
  2. Lọc log theo `error_type` → tìm pattern chung (cùng user? cùng feature?)
  3. Mở Langfuse → lọc traces failed → inspect span nào gây lỗi
  4. Kiểm tra: `GET /health` → xem `tool_fail` có đang `true` không
- **Mitigation**:
  - Nếu vector store timeout → restart RAG service, disable failing tool tạm
  - Nếu schema error → rollback commit gần nhất
  - Nếu LLM error → retry với fallback model
  - Mọi trường hợp: **rollback nếu lỗi bắt đầu từ deploy gần nhất**
- **Escalation**: P1 → phải response trong 15 phút, resolve trong 1h

---

## 3. Cost budget spike
- **Severity**: P2 (Warning)
- **Trigger**: `hourly_cost_usd > 2x_baseline for 15m`
- **Impact**: Burn rate vượt budget → hết tiền trước kỳ hạn
- **SLO liên quan**: `daily_cost_usd < $2.5/day`
- **First checks**:
  1. `GET /metrics` → so sánh `avg_cost_usd` hiện tại vs baseline (~$0.001)
  2. Mở Langfuse → split traces theo `feature` và `model` → feature nào tốn nhất?
  3. So sánh `tokens_in` vs `tokens_out` → token output tăng bất thường?
  4. Kiểm tra: `GET /health` → xem `cost_spike` có đang `true` không (gấp 4x output tokens)
- **Mitigation**:
  - Rút ngắn prompt (giảm tokens_in)
  - Route request dễ sang model rẻ hơn (ví dụ: haiku thay sonnet)
  - Bật prompt caching nếu có request trùng lặp
  - Rate limit user gửi quá nhiều request
- **Escalation**: nếu tổng cost/ngày > $5 → escalate lên FinOps lead

---

## 4. Quality degradation
- **Severity**: P2 (Warning)
- **Trigger**: `quality_score_avg < 0.6 for 15m`
- **Impact**: AI trả lời đúng format nhưng nội dung kém → user không tin → chuyển sang tool khác
- **SLO liên quan**: `quality_score_avg >= 0.75, target 95%`
- **Tại sao cần alert riêng cho quality?**
  - Latency tốt + Error rate thấp ≠ AI trả lời đúng
  - Quality degradation là "silent failure" — hệ thống KHÔNG báo lỗi nhưng câu trả lời vô nghĩa
- **First checks**:
  1. `GET /metrics` → xem `quality_avg` → dưới 0.6 bao lâu rồi?
  2. Kiểm tra RAG: câu hỏi có match domain không? (`refund`, `monitoring`, `policy`)
  3. Kiểm tra `[REDACTED]` trong answer → PII leak gây trừ điểm (-0.2)?
  4. Xem log: `answer_preview` có chứa nội dung hữu ích không?
- **Mitigation**:
  - Cải thiện corpus RAG (thêm documents)
  - Sửa fallback answer để chứa nội dung hữu ích hơn
  - Kiểm tra PII scrubber có chạy quá "mạnh" không (redact cả dữ liệu hợp lệ)
  - Thêm few-shot examples vào prompt
- **Escalation**: nếu quality < 0.4 trong 30m → escalate lên ML team lead

---

## 5. Token budget exceeded
- **Severity**: P3 (Info/Warning)
- **Trigger**: `tokens_in_total > 50000 per hour`
- **Impact**: Dấu hiệu sớm của cost spike hoặc prompt injection attack
- **SLO liên quan**: `daily_cost_usd` (leading indicator)
- **Tại sao tách riêng khỏi cost alert?**
  - Token budget là **leading indicator** (phát hiện TRƯỚC khi cost tăng)
  - Cost alert là **lagging indicator** (chỉ biết KHI ĐÃ tốn tiền)
  - Giống smoke alarm vs fire alarm: phát hiện khói trước khi cháy
- **First checks**:
  1. `GET /metrics` → `tokens_in_total` và `tokens_out_total`
  2. So sánh tokens_in trung bình/request → có request nào gửi prompt quá dài?
  3. Xem log: user nào gửi message dài bất thường? (prompt injection?)
  4. Kiểm tra `cost_spike` incident toggle
- **Mitigation**:
  - Set max input length cho message (VD: 2000 ký tự)
  - Rate limit per user
  - Truncate prompt trước khi gửi LLM
  - Monitor cho prompt injection patterns
- **Escalation**: nếu tokens > 100,000/h → tự động upgrade lên P2

---

## Flow debug tổng quát: Metrics → Traces → Logs

Khi BẤT KỲ alert nào kích hoạt, follow flow này:

```
1. DASHBOARD (Metrics)     → Xác nhận vấn đề có thật không, quy mô bao lớn?
   ↓
2. LANGFUSE (Traces)       → Tìm request cụ thể bị ảnh hưởng, span nào gây vấn đề?
   ↓
3. LOGS (correlation_id)   → Đọc chi tiết từng bước, tìm root cause chính xác
```
