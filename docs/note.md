# Note - Member C: SLO & Alerts (Phạm Tuấn Anh)

## ✅ Đã làm xong (tự điền được, không cần app chạy)

| File | Nội dung |
|---|---|
| `config/slo.yaml` | Định nghĩa 5 SLIs + error budget. Metric names lấy từ `app/metrics.py` → `snapshot()` |
| `config/alert_rules.yaml` | 6 alert rules phân cấp P1/P2/P3. Tên incidents (`rag_slow`, `cost_spike`, `tool_fail`) lấy từ `app/incidents.py` |
| `docs/alerts.md` | 6 runbooks đầy đủ — investigation steps, lệnh `jq`, mitigation, escalation |
| `docs/blueprint-template.md` | Điền phần Member C với mô tả 4 tasks, design decisions |

---

## ⚠️ Còn thiếu — cần app chạy mới điền được

| Mục trong blueprint | Cách lấy |
|---|---|
| `[VALIDATE_LOGS_FINAL_SCORE]` | Chạy: `python scripts/validate_logs.py` (sau khi nhóm hoàn thành TODOs) |
| `[TOTAL_TRACES_COUNT]` | Xem Langfuse dashboard (cần `.env` có `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`) |
| `[SLO_TABLE]` — cột *Current Value* | Chạy: `python scripts/load_test.py` → `curl localhost:8000/metrics` |
| `[ALERT_RULES_SCREENSHOT]` | Chụp màn hình file `alert_rules.yaml` hoặc dashboard |
| `[EVIDENCE_LINK]` | Link commit trên GitHub sau khi push |

---

## 🔴 TODOs trong code — KHÔNG phải việc của Member C

| TODO | File | Ai làm |
|---|---|---|
| Implement `correlation_id` (clear + bind contextvars) | `app/middleware.py` line 13–21 | **Member A** |
| Enrich logs: `user_id_hash, session_id, feature, model` | `app/main.py` line 47–48 | **Member B** |
| Bật `scrub_event` PII processor | `app/logging_config.py` line 46 | **Member A** |

---

## Cách chạy app để lấy số liệu thực

```bash
# 1. Tạo venv và cài thư viện
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Copy file .env
cp .env.example .env
# (điền LANGFUSE keys nếu có)

# 3. Chạy server
uvicorn app.main:app --reload

# 4. Chạy load test (terminal khác)
python scripts/load_test.py --concurrency 5

# 5. Xem metrics thực
curl http://localhost:8000/metrics

# 6. Kiểm tra điểm
python scripts/validate_logs.py
```

---

## Liên kết giữa file của Member C và code thực

```
config/slo.yaml
  └── metrics đến từ: app/metrics.py → snapshot()
      - latency_p95_ms   ← percentile(REQUEST_LATENCIES, 95)
      - error_rate_pct   ← sum(ERRORS.values()) / TRAFFIC * 100
      - daily_cost_usd   ← sum(REQUEST_COSTS)
      - quality_score_avg ← mean(QUALITY_SCORES)

config/alert_rules.yaml
  └── incident names từ: app/incidents.py → STATE keys
      - "rag_slow", "tool_fail", "cost_spike"
  └── runbook links trỏ tới: docs/alerts.md#<section>

docs/alerts.md
  └── lệnh check incidents: curl POST /incidents/{name}/enable|disable
  └── lệnh check metrics:   curl GET /metrics
  └── lệnh grep logs:       jq 'select(.level=="error")' data/logs.jsonl
```

---

# Note - Member E: Demo & Report (Phạm Tuấn Anh)

## 🎯 Tổng quan nhiệm vụ
Vai trò của Member E (Demo & Report) là tổng hợp toàn bộ kết quả của nhóm vào file `docs/blueprint-template.md`, chuẩn bị các màn demo thực tế trên máy, và đảm bảo mọi tiêu chí chấm điểm (Rubric) đều đạt mức tối đa.

## ✅ Checklist những việc CÓ THỂ LÀM NGAY (Tự làm)

- [ ] **1. Điền thông tin cơ bản vào thủ công:**
  - [ ] `[GROUP_NAME]`: VD "C401-Group" (phần `1. Team Metadata`)
  - [ ] `[REPO_URL]`: Điền link Repo Github của nhóm.
  - [ ] `[MEMBERS]`: Điền tên và vai trò của 5 thành viên (A, B, C, D, E).
- [ ] **2. Phần việc của bản thân (Mục 5. Individual Contributions):**
  - [ ] Điền mục báo cáo cho Member E (tasks completed: viết báo cáo, chuẩn bị demo logic, ghép nối code các thành viên).
  - [ ] Đính kèm `[EVIDENCE_LINK]` là link commit đến file `blueprint-template.md` sau khi hoàn thành.
- [ ] **3. Soạn sẵn kịch bản Demo (Live Demo chiếm 20đ nhóm):**
  - [ ] **Phần 1: Chạy app mượt mà.** Code lệnh start server, start load test để hiển thị metrics nhảy liên tục.
  - [ ] **Phần 2: Giả lập lỗi (Incident).** Chạy `python scripts/inject_incident.py --scenario rag_slow`.
  - [ ] **Phần 3: Debugging flow.** Mở Dashboard -> Mở Langfuse tìm dòng đỏ (Traces) -> Copy TraceID dán vào logs (chứng minh truy vết lỗi). Giải thích cách middleware đính kèm `correlation_id` vào request.

---

## ⏳ NGUYÊN LIỆU PHẢI CHỜ TỪ NGƯỜI KHÁC (Thu thập sau)

*Đánh dấu (*) là cực kỳ quan trọng, cần hối thúc team làm sớm để ghép vào báo cáo.*

### Từ Member A (Logging & PII)
- [ ] Ảnh chụp `[EVIDENCE_CORRELATION_ID_SCREENSHOT]` (log JSON có chứa ID).
- [ ] Ảnh chụp `[EVIDENCE_PII_REDACTION_SCREENSHOT]` (log JSON hiển thị `[REDACTED_EMAIL]`).
- [ ] Link commit evidence và tasks completed của Member A (cho Mục 5).

### Từ Member B (Tracing & Enrichment)
- [ ] `[TOTAL_TRACES_COUNT]`: Truy cập Langfuse dashboard đếm số traces (>= 10).
- [ ] Ảnh chụp `[EVIDENCE_TRACE_WATERFALL_SCREENSHOT]`.
- [ ] Câu giải thích `[TRACE_WATERFALL_EXPLANATION]` (nhờ Member B viết 1 câu).
- [ ] Link commit evidence và tasks completed của Member B (cho Mục 5).

### Từ Member C (SLO & Alerts) & Member D (Load Test)
- [ ] Vận hành bảng SLO `[SLO_TABLE]`: Chạy Load Test (`scripts/load_test.py`) và điền cột **Current Value** (Ví dụ: Latency đo được thực tế là bao nhiêu, Error rate là 0%...).
- [ ] Ảnh chụp `[DASHBOARD_6_PANELS_SCREENSHOT]`: Xin Member D.
- [ ] Ảnh chụp `[ALERT_RULES_SCREENSHOT]`: File của Member C.
- [ ] Mẫu `[SAMPLE_RUNBOOK_LINK]`: Kéo link từ file của Member C.
- [ ] Link commit evidence và tasks completed của Member C & D (cho Mục 5).

### Thông tin chung cả nhóm (Hoàn tất phần code)
- [ ] **Điểm số tự động `[VALIDATE_LOGS_FINAL_SCORE]`:** Chạy `python scripts/validate_logs.py` -> Phải đảm bảo đạt tối đa/100đ thì mới dán vào báo cáo.
- [ ] `[PII_LEAKS_FOUND]`: Điền số lượng (Phải cố gắng = `0`).
- [ ] **Mục 4. Incident Response:** Ngồi lại với người làm Load/Fail (Member D) để mô tả cách ứng phó sự cố (Scenario Name, Symptoms, Root cause bằng Trace ID, Fix Action).

---

# Note - Nhiệm vụ các thành viên theo Đề tài 2 (Chatbot CSKH Ngân hàng)

Đề tài 2: **Chatbot CSKH Ngân hàng & Tín dụng**
Ngữ cảnh: Bot giải đáp thắc mắc tài khoản, nhắc nợ, khóa thẻ khẩn cấp. Do làm việc trong mảng tài chính, **bảo mật dữ liệu (PII)** và **độ ổn định (Error Rate, Latency)** là ưu tiên cao nhất.

### 👤 Member A: Logging & PII
*Trọng tâm: Data Security (PCI-DSS)*
- **Task Chính:** Viết Regex cực mạnh để che các dữ liệu nhạy cảm của khách hàng ngân hàng.
- **Data cần ẩn:** 
  - **Số thẻ tín dụng (Credit Card):** Ví dụ regex `\b(?:\d{4}[ -]?){3}\d{4}\b` che thành `[REDACTED_CREDIT_CARD]`.
  - **Số CMND/CCCD/Passport:** Ví dụ che `B12345` hoặc `0123456...`.
  - **Số điện thoại, Email đăng ký.**
- **Log Enrichment:** Đảm bảo mọi log giao dịch (lock_card, check_balance) đều có `correlation_id` để truy vết ai đã thực hiện thao tác khóa thẻ.

### 👤 Member B: Tracing & Enrichment
*Trọng tâm: Phân loại User Data*
- **Task Chính:** Gắn các thông tin nghiệp vụ ngân hàng vào Log & Traces.
- **Context Variables cần thêm:**
  - `user_segment`: "VIP", "Standard" (Ví dụ khách VIP ưu tiên xử lý nhanh).
  - `intent`: "lock_card", "balance_inquiry", "debt_reminder".
  - `card_type`: "credit", "debit".
- **Tracing (Langfuse):** Set up Node cho các công cụ như `fetch_bank_balance` hoặc `suspend_card`. Theo dõi xem API ngân hàng tốn mất bao nhiêu milliseconds.

### 👤 Member C: SLO & Alerts
*Trọng tâm: Đảm bảo Uptime & Cảnh báo lỗi 500*
- **Task Chính:** Canh gác hệ thống khi API Core Banking "sập".
- **SLOs:** Thiết lập SLO về **Error Rate** rất chặt (Mất kết nối Core Banking là phải trừ ngay Error Budget).
- **Alerts (Cảnh báo):**
  - **P1 (Critical):** Alert `core_banking_down` hoặc `high_error_rate` (Khi > 5% request ra lỗi `500 Server Error`).
  - **Runbook:** Hướng dẫn On-call engineer cách kiểm tra xem do Core Banking hay do Bot AI.

### 👤 Member D: Load Test & Dashboard
*Trọng tâm: Stress Test & Incident Injection*
- **Task Chính:** Giả lập sự kiện đổ bộ của khách báo mất thẻ và giả lập lỗi Core Banking.
- **Incident Injection:** 
  - Tạo Scenario: `core_banking_fail` -> Làm cho hàm `mock_core_banking_api()` trả về lỗi HTTP 500.
- **Load Test:** Bơm dữ liệu (concurrency cao) yêu cầu Khóa thẻ khẩn cấp để xem hệ thống chịu tải thế nào.
- **Dashboard Panels (Grafana/Kibana):** Vẽ biểu đồ Error 500 Rate, Biểu đồ phân bổ Intent (bao nhiêu lock_card, bao nhiêu balance_inquiry).

### 👤 Member E: Demo & Report (Vai trò của bạn)
*Trọng tâm: Báo cáo tính thực tiễn & Demo kịch tính*
- **Kịch bản Demo:**
  - **Bước 1 (Bình thường):** Chat "Tôi muốn khóa khẩn cấp thẻ credit mang số 4111 2222... Số passport mặt trước của tôi là B12345". 
    => **Show Logs:** Thể hiện Regex của Member A đã loại bỏ số thẻ, bảo vệ Data Privacy.
  - **Bước 2 (Sự cố):** Member D bật lỗi kết nối Core Banking (`core_banking_fail`).
  - **Bước 3 (Phản ứng nhanh):** Thực hiện lại request "Kiểm tra số dư". Hệ thống văng lỗi 500. Chờ 1 phút để xem Alert báo còi (Slack/PagerDuty). 
  - **Bước 4 (Root Cause):** Mở Langfuse truy vết theo `Trace ID`. Chỉ ra chính xác Block/Node "Gọi API Ngân Hàng" có màu đỏ bầm (Lỗi HTTP 500). Tuyên bố Fix lỗi bằng cách đóng toggle Incident.
  - **Báo cáo chuẩn mực:** Tổng hợp những ý đồ thiết kế phía trên của A, B, C, D vào `blueprint-template.md`.

---

# Bảng phân công thành viên TỰ ĐIỀN vào file `docs/blueprint-template.md`

Từng thành viên (Role) bắt buộc phải tự vào file `docs/blueprint-template.md` và thay thế các Placeholder (chữ trong ngoặc vuông `[...]`) bằng ảnh hoặc số liệu của mình. Dưới đây là bảng phân công rõ ràng:

## 1. Member A (Logging & PII)
- [ ] Ảnh chụp dòng Log JSON có hiển thị biến `[REDACTED_CREDIT_CARD]` dán đè vào `[EVIDENCE_PII_REDACTION_SCREENSHOT]` (Ở mục 3.1).
- [ ] Điền mục báo cáo cá nhân của mình ở **Mục 5: `### [MEMBER_A_NAME]`**: điền `[TASKS_COMPLETED]` làm được gì, và dán `[EVIDENCE_LINK]` là link tới Commit GitHub chứa code phần khai báo Regex của mình.
- [ ] Chịu trách nhiệm đảm bảo số lượng `[PII_LEAKS_FOUND]` ở Mục 2 bằng **0**.

## 2. Member B (Tracing & Enrichment)
- [ ] Điền con số lớn hơn 10 vào `[TOTAL_TRACES_COUNT]` (Ở mục 2).
- [ ] Ảnh chụp Log có dòng `correlation_id` dán vào `[EVIDENCE_CORRELATION_ID_SCREENSHOT]` (Ở mục 3.1).
- [ ] Cung cấp 1 ảnh chụp một nhánh Trace bị lỗi 500 hoặc Trace hiển thị API dán vào `[EVIDENCE_TRACE_WATERFALL_SCREENSHOT]`. Thay phần `[TRACE_WATERFALL_EXPLANATION]` bằng một câu giải thích bằng lời (Ví dụ: Trace id xx-yyy cho thấy API lock_card mất quá nhiều thời gian).
- [ ] Điền cá nhân ở **Mục 5: `### [MEMBER_B_NAME]`** bao gồm task đã làm và link Evidence Commit.

## 3. Member C (SLO & Alerts - Vũ Lê Hoàng)
- [ ] Ảnh chụp file code khai báo 6 alert hoặc màn hình alert dán vào `[EVIDENCE_ALERT_RULES_SCREENSHOT]` (Ở mục 3.3).
- [ ] Thay `[SAMPLE_RUNBOOK_LINK]` bằng hyperlink dẫn vào file `alerts.md` của mình.
- [ ] (Đã hoàn thành) Cập nhật Mục 5 bằng báo cáo và commit của màn SLO & Alert.

## 4. Member D & Member E (Load test, Dashboard & Dashboard panel)
- [ ] Nhóm người cầm trịch Dashboard (Member D và E) ghép 6 tấm Panel Grafana/HTML lại chụp trọn màn hình và dán vào `[DASHBOARD_6_PANELS_SCREENSHOT]` (Mục 3.2).
- [ ] Thay đổi số đo ở cột **Current Value** của bảng `[SLO_TABLE]`. Cần chạy file `python scripts/load_test.py` rồi đọc dữ liệu điền vào (Ví dụ: Latency đo dược 151ms, v.v.).
- [ ] Điền **Mục 4: Incident Response**. Người tạo giả lập lỗi sẽ điền các kịch bản như: `[SCENARIO_NAME]` = `core_banking_fail` , `[SYMPTOMS_OBSERVED]` = Báo màn hình 500.

## 5. Cả team nhắc nhau
Tất cả các Member (Bao gồm cả Tuấn Anh - Demo Lead) đều phải đảm bảo phần cá nhân của mình ở Mục 5 (`### [MEMBER_NAME]`) có **một đoạn văn mô tả công việc mình đã làm**, và **phải có 1 Link Commit GitHub**. Đừng để bất kì chữ ngoặc ở dạng `[MEMBER_NAME]` nào sót lại.



