# Dashboard Spec: Da Nang Travel Agent

1. Latency P50/P95/P99 (Hiệu năng)
> Mô tả: Thời gian phản hồi từ lúc nhận câu hỏi đến khi Mock LLM hoàn tất lịch trình.
> Threshold (SLO): Vẽ một đường đỏ tại 5s (SLO cho P95).
> Evidence: Chụp ảnh lúc hệ thống chạy bình thường và lúc bị "lag" khi chạy Load Test.
> Đơn vị: Milliseconds (ms) hoặc Seconds (s).

2. Traffic (QPS/Request Count)
> Mô tả: Tổng lưu lượng người dùng đang hỏi về du lịch Đà Nẵng.
> Chi tiết: Chia theo các endpoint (ví dụ: /chat, /checklist, /suggest).
> Ý nghĩa: Thấy được thời điểm "cao điểm" mà khách du lịch vào tra cứu.

3. Error Rate with Breakdown (Tỉ lệ lỗi)
> Mô tả: Tỉ lệ % lỗi (4xx, 5xx).
> Breakdown: Phân loại lỗi theo: RAG_Failure (không tìm thấy địa điểm), LLM_Timeout, hoặc PII_Blocked (chặn do vi phạm bảo mật).
> Evidence: Đây là bằng chứng quan trọng nhất khi Member D thực hiện Incident Injection.

4. Cost Over Time (Chi phí vận hành)
> Mô tả: Ước tính số tiền (USD) đã tiêu tốn cho việc gọi AI.
> Công thức: (Tokens_In * Price_In) + (Tokens_Out * Price_Out).
> Ý nghĩa: Cho thấy khả năng quản trị tài chính của hệ thống.

5. Tokens In/Out (Thông lượng dữ liệu)
> Mô tả: Số lượng token khách gửi vào (input) và chatbot trả ra (output).
> Đặc thù Đà Nẵng: Các yêu cầu "Lên lịch trình 4 ngày" sẽ có Tokens Out cao hơn nhiều so với yêu cầu "Hỏi địa chỉ quán Mì Quảng".

6. Quality Proxy (Chất lượng phản hồi)
> Mô tả: Sử dụng Heuristic (quy tắc tự động).
> Cách đo: Đếm số lần câu trả lời của Mock LLM chứa các từ khóa bắt buộc phải có trong dữ liệu Đà Nẵng (như "Bà Nà", "Sơn Trà", "Cầu Rồng").
> Regenerate Rate: Số lần người dùng nhấn "Tạo lại lịch trình" (giả lập bằng click rate).

---
## Technical Implementation Details
* **Tooling:** Langfuse Dashboard + Custom Metrics API.
* **Auto-refresh:** 15s (Enabled during live demo).
* **SLO Visualization:** Constant line at 5000ms for P95 Latency.

## Evidence Checklist (Member E)
- [ ] Ảnh chụp Dashboard lúc 10h sáng (Trạng thái ổn định).
- [ ] Ảnh chụp Dashboard lúc chạy Load Test (Traffic vọt lên).
- [ ] Ảnh chụp màn hình Panel 3 & 6 đỏ rực khi Member D chạy `inject_incident.py`.