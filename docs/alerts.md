# Alert Rules and Runbooks

> **Mục đích**: Tài liệu này là "sổ tay cấp cứu" khi hệ thống báo động.
> Mỗi alert trong `config/alert_rules.yaml` trỏ tới một mục tương ứng ở đây.
> Người trực (on-call) mở file này ra, làm theo từng bước để khắc phục sự cố.

---

## 1. High latency P95

| Thuộc tính | Giá trị |
|---|---|
| **Alert name** | `high_latency_p95` |
| **Severity** | P2 (Warning) |
| **Trigger** | `latency_p95_ms > 5000 for 30m` |
| **Impact** | Tail latency vi phạm SLO, user phải chờ >5 giây mới nhận được câu trả lời |

### Quy trình xử lý
1. **Mở Langfuse** → Tab Traces → Lọc theo 1 giờ gần nhất → Sắp xếp theo `duration DESC`
2. **So sánh span**: Kiểm tra thời gian RAG retrieval vs LLM generation. Nếu RAG span > 2s thì vấn đề nằm ở retrieval
3. **Kiểm tra incident toggle**: Chạy `GET /incidents` xem `rag_slow` có đang bật không
4. **Kiểm tra tài nguyên**: CPU / Memory có bị quá tải do request đồng thời không

### Biện pháp khắc phục
- Truncate query dài trước khi gửi vào RAG (giới hạn 500 ký tự)
- Chuyển sang fallback retrieval source (cache hoặc simplified search)
- Giảm kích thước prompt gửi cho LLM
- Nếu do incident toggle: tắt bằng `POST /incidents {"rag_slow": false}`

### Escalation
- Nếu sau 30 phút vẫn chưa giải quyết → Escalate lên P1 → Thông báo Tech Lead

---

## 2. High error rate

| Thuộc tính | Giá trị |
|---|---|
| **Alert name** | `high_error_rate` |
| **Severity** | P1 (Critical) |
| **Trigger** | `error_rate_pct > 5 for 5m` |
| **Impact** | User nhận response lỗi trực tiếp, ảnh hưởng nghiêm trọng đến trải nghiệm |

### Quy trình xử lý
1. **Mở log file** (`data/logs.jsonl`) → Lọc `level: "error"` trong 10 phút gần nhất
2. **Phân loại lỗi**: Group logs theo trường `error_type` để xác định nguồn gốc:
   - `LLMError`: LLM timeout hoặc rate limit
   - `ToolError`: Vector store / external tool bị sập
   - `SchemaError`: Request không đúng format
3. **Mở Langfuse** → Lọc traces có `status: ERROR` → Xem chi tiết span nào bị fail
4. **Kiểm tra incident toggle**: `GET /incidents` xem `tool_fail` có bật không

### Biện pháp khắc phục
- Rollback commit gần nhất nếu lỗi xuất hiện sau deploy mới
- Disable tool đang fail (nếu là ToolError) để agent chạy không tool
- Retry với fallback model (ví dụ: chuyển từ claude-sonnet sang gpt-4o-mini)
- Nếu do incident toggle: tắt bằng `POST /incidents {"tool_fail": false}`

### Escalation
- P1 → Phải xử lý trong 15 phút. Nếu không giải quyết được → gọi điện cho Tech Lead ngay lập tức

---

## 3. Cost budget spike

| Thuộc tính | Giá trị |
|---|---|
| **Alert name** | `cost_budget_spike` |
| **Severity** | P2 (Warning) |
| **Trigger** | `hourly_cost_usd > 2x_baseline for 15m` |
| **Impact** | Tốc độ đốt tiền (burn rate) vượt ngân sách, có thể cháy budget trong vài giờ |

### Quy trình xử lý
1. **Mở Langfuse** → Tab Traces → Xem cột `tokens` và `cost`
2. **Split theo feature**: Xem feature nào đang tiêu tốn nhiều token nhất
3. **So sánh tokens_in vs tokens_out**: Nếu tokens_out tăng đột biến (>3x) → LLM đang trả lời quá dài
4. **Kiểm tra incident toggle**: `GET /incidents` xem `cost_spike` có bật không

### Biện pháp khắc phục
- Rút ngắn system prompt (bỏ ví dụ thừa, giảm few-shot examples)
- Route các request đơn giản sang model rẻ hơn (ví dụ: gpt-4o-mini thay vì claude-sonnet)
- Bật prompt cache nếu có nhiều request tương tự
- Set `max_tokens` cho LLM output để giới hạn độ dài câu trả lời
- Nếu do incident toggle: tắt bằng `POST /incidents {"cost_spike": false}`

### Escalation
- Nếu cost vẫn tăng sau 1 giờ → Thông báo FinOps owner để tạm dừng service

---

## 4. Quality degradation

| Thuộc tính | Giá trị |
|---|---|
| **Alert name** | `quality_degradation` |
| **Severity** | P2 (Warning) |
| **Trigger** | `quality_score_avg < 0.5 for 15m` |
| **Impact** | Chất lượng câu trả lời AI xuống thấp, user nhận được câu trả lời kém chất lượng |

### Quy trình xử lý
1. **Mở metrics endpoint** (`GET /metrics`) → Kiểm tra trường `quality_avg`
2. **Mở Langfuse** → So sánh các traces gần đây với traces cũ (thời điểm quality còn cao)
3. **Kiểm tra RAG**: Xem context được trả về có relevant không (có thể RAG đang trả sai document)
4. **Kiểm tra prompt**: Xem system prompt có bị thay đổi gần đây không

### Biện pháp khắc phục
- Kiểm tra và sửa lại retrieval pipeline (query rewriting, reranking)
- Rollback prompt nếu có thay đổi gần đây
- Tăng số lượng context chunks từ RAG (top_k từ 3 lên 5)
- Thêm output validation để reject câu trả lời quá ngắn hoặc không liên quan

### Escalation
- Nếu quality không phục hồi sau 1 giờ → Báo cáo ML Engineer để review pipeline

---

## 5. Token anomaly

| Thuộc tính | Giá trị |
|---|---|
| **Alert name** | `token_anomaly` |
| **Severity** | P3 (Info) |
| **Trigger** | `tokens_out_avg > 3x_baseline for 10m` |
| **Impact** | Cảnh báo sớm — lượng token output bất thường, có thể dẫn đến cost spike |

### Quy trình xử lý
1. **Mở metrics endpoint** (`GET /metrics`) → So sánh `tokens_out_total` với baseline
2. **Mở Langfuse** → Lọc traces theo thời gian → Xem traces nào có output_tokens cao bất thường
3. **Kiểm tra input**: Có user nào gửi query đặc biệt dài hoặc yêu cầu LLM "viết chi tiết" không

### Biện pháp khắc phục
- Set `max_tokens` limit cho LLM response (ví dụ: 500 tokens)
- Thêm output truncation logic trước khi trả về user
- Monitor thêm 10 phút — nếu tự ổn thì đây chỉ là burst tạm thời

### Escalation
- P3 không cần escalation ngay. Ghi lại vào incident log để review trong daily standup

---

## Quick Reference Card

| Alert | Severity | Thời gian phản hồi tối đa | Người phụ trách |
|---|:---:|:---:|---|
| high_error_rate | P1 | 15 phút | team-oncall |
| high_latency_p95 | P2 | 30 phút | team-oncall |
| cost_budget_spike | P2 | 30 phút | finops-owner |
| quality_degradation | P2 | 30 phút | team-oncall |
| token_anomaly | P3 | Next standup | finops-owner |
