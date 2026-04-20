# 🎤 Kịch Bản Thuyết Trình & Live Demo (Đề Tài: AI CSKH Ngân Hàng)
**Demo Lead:** Phạm Tuấn Anh (Member F)

> *Chú ý: Trong lúc nói, bạn hãy thao tác trên màn hình trùng khớp với những gì đang đọc.*

---

## Phần 1: Giới thiệu chung (1 phút)
**Bạn (Tuấn Anh):** 
"Chào thầy/cô và các bạn. Nhóm chúng em là nhóm C401. Đề bài của nhóm là xây dựng một hệ thống **AI Assistant CSKH Ngân hàng**, hỗ trợ khách hàng kiểm tra số dư và khóa thẻ khẩn cấp. 
Trong lĩnh vực ngân hàng, chuẩn bảo mật thông tin chuẩn PCI-DSS là tối quan trọng, đồng thời hệ thống phải luôn đáp ứng Latency thấp và Uptime cao. Do đó, hệ thống Observability của chúng em tập trung mạnh vào 2 tính năng: **Redact PII số thẻ tín dụng/CCCD** và **Alert tự động báo lỗi 500 khi Core Banking sập**.

Sau đây em xin gửi tới thầy cô bản Demo live của hệ thống."

---

## Phần 2: Demo Normal Flow - Redact PII (2 phút)

**Thao tác chuẩn bị:**
- Đảm bảo app đang chạy bằng lệnh `uvicorn app.main:app --reload`.
- Mở sẵn 1 cửa sổ Terminal xem Log, và 1 tab trình duyệt xem Langfuse.

**Bạn (Tuấn Anh):**
"Đầu tiên là luồng chuẩn. Khách hàng thông báo mất thẻ và để lại số thẻ tín dụng cũng như số Hộ chiếu. Em sẽ gửi một request POST giả lập."
*(Gõ lệnh gửi request: "Tôi muốn khóa khẩn cấp thẻ credit mang số 4111 2222... Số passport mặt trước của tôi là B12345")*

**Bạn (Tuấn Anh):**
"Hệ thống đã phản hồi thành công xử lý khóa thẻ. Bây giờ chúng ta hãy nhìn vào màn hình Terminal Logs."
*(Chỉ chuột vào màn hình Terminal Logs đoạn có chữ `[REDACTED_CREDIT_CARD]`)*
"Như thầy cô thấy, Regex Scrubber do **Member A** viết đã ngay lập tức đánh chặn và mã hóa toàn bộ số điện thoại, CCCD và chuỗi thẻ tín dụng 4111. Hệ thống Log chỉ lưu lại biến `[REDACTED_CREDIT_CARD]`. Điều này đảm bảo AI của team đáp ứng tiêu chuẩn đạo đức và bảo mật dữ liệu ngân hàng. Ngoài ra, Log cũng chứa trường `correlation_id` do hệ thống Middleware tự động inject vào để theo dõi request theo chiều sâu."

---

## Phần 3: Demo Incident Injection & Monitoring (3 phút)

**Thao tác chuẩn bị:**
- Mở Dashboard hoặc chuẩn bị chạy Load Test. Mở file `config/alert_rules.yaml`.

**Bạn (Tuấn Anh):**
"Tiếp theo, ứng dụng ngân hàng phải đối mặt với một sự cố thực tế: API Core Banking bị đứt kết nối. Để test hệ thống cảnh báo (Alerts) và Dashboard do **Member C và Member D** làm, em sẽ dùng script tiêm mã lỗi vào hệ thống."
*(Chạy lệnh: `python scripts/inject_incident.py --scenario core_banking_fail`)*

**Bạn (Tuấn Anh):**
"Tiếp theo, dưới góc độ người dùng, khi hỏi về số dư, họ sẽ bắt gặp lỗi màn hình 500 Internal Server Error. Để hệ thống báo động, em sẽ chạy Load Test tạo traffic giả lặp sự cố đồng loạt."
*(Chạy lệnh: `python scripts/load_test.py --concurrency 5`)*

**Bạn (Tuấn Anh):**
"Lúc này, quay lại Dashboard, chúng ta sẽ thấy biểu đồ Error Rate tăng vọt. Và ngay lập tức, một Alert có tên `high_error_rate` (P1) sẽ chớp đỏ và gửi tin nhắn cảnh báo thiết lập sẵn đến Slack cho kĩ sư On-Call, thông báo Error Rate vọt quá ngưỡng % cho phép, bào trực tiếp vào lượng Error Budget của SLO."

---

## Phần 4: Debugging và Giải thích Root Cause (2 phút)

**Bạn (Tuấn Anh):**
"Dưới vai trò là nhân viên trực hệ thống vừa nhận Alert, em sẽ phải tìm nguyên nhân. Khởi đầu từ Dashboard có Error Rate vọt lên, em sẽ chuyển sang Langfuse (Tracing) do **Member B** thiết lập để truy vết chi tiết."
*(Mở Langfuse Dashboard ở trình duyệt, lọc lỗi HTTP 500).*

**Bạn (Tuấn Anh):**
"Tại đây, em thấy một loạt Trace hiện màu đỏ. Bấm vào một Trace Waterfall..."
*(Click vào Trace bị lỗi)*
"Thầy cô có thể thấy rõ dòng thời gian Request. Root Cause không phải do model AI trả lời quá lâu, mà chính xác nằm tại đoạn ứng dụng gọi sang hàm `mock_core_banking_api()` để lấy số dư. Node Tracing này gặp lỗi 500 và sập. 
Đứng từ Langfuse, em copy mã Trace ID và đưa vào terminal duyệt file Logs JSON."
*(Mở terminal, gõ một lệnh grep log hoặc tìm kiếm file JSON theo Trace ID)*
"Từ Log, nguyên nhân kĩ thuật chính xác đã hiện ra dòng chữ đỏ: 'Connection Timeout to Core Banking'." 

"Để khắc phục (Fix Action) kịp thời, kĩ sư on-call sẽ chuyển hướng bypass hoặc gọi API phụ. Ở bài Lab này, em xin được tắt toggle giả lập lỗi kết nối đi."
*(Chạy lệnh tắt lỗi - disable incident, gửi lại request -> App trả lời Thành công)*.

"Hệ thống đã phục hồi trở lại, Error rate trên Dashboard sẽ từ từ giảm. Báo cáo sự cố đã được lưu vào Runbook của Member C. Đó là toàn bộ hệ thống Observability mà team C401 đã áp dụng, từ lúc filter PII, Trace lỗi, đến quy trình Incident Response. Em xin cảm ơn thầy cô đã lắng nghe!"
