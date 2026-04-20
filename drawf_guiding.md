## 📋 **GIẢI THÍCH CHI TIẾT BÀI TẬP OBSERVABILITY LAB**

### **1. BÀI TẬP LÀM GÌ?**

Đây là bài tập **"Observability Lab"** - xây dựng hệ thống **giám sát toàn diện (Monitoring)** cho một ứng dụng AI. Bạn cần triển khai:

| Thành phần | Mục đích |
|-----------|---------|
| **Logging (Ghi nhật ký)** | Theo dõi những gì xảy ra trong ứng dụng với ID duy nhất |
| **Tracing (Theo dõi)** | Xem toàn bộ journey của 1 request từ đầu đến cuối |
| **Metrics (Chỉ số)** | Đo lường hiệu suất (tốc độ, lỗi, chi phí) |
| **Alerts (Cảnh báo)** | Tự động thông báo khi có vấn đề |
| **Dashboard (Bảng điều khiển)** | Visualize dữ liệu dễ hiểu |
| **PII Protection (Bảo vệ dữ liệu)** | Ẩn đi thông tin nhạy cảm (email, phone, CCCD...) |

---

### **2. KIẾN TRÚC ỨNG DỤNG (Hiểu ngay để làm đúng)**

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (người dùng)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /chat
                         ▼
        ┌─────────────────────────────────────────┐
        │    FastAPI App (main.py)                │
        │  • Nhận request từ client               │
        │  • Gửi response về client               │
        └────────────┬──────────────┬─────────────┘
                     │              │
         ┌───────────▼──┐   ┌──────▼────────┐
         │ Middleware   │   │ Agent Pipeline │
         │ (Correlation │   │ • LLM (mock)   │
         │  ID)         │   │ • RAG (mock)   │
         └──────┬───────┘   └──────┬────────┘
                │                  │
    ┌───────────▼──────────────────▼──────────────┐
    │  Logging Output (structlog)                 │
    │  ↓                                          │
    │  📄 data/logs.jsonl (Logs được ghi ra)     │
    │  📊 Langfuse (Traces được gửi lên)        │
    │  📈 Metrics (In-memory counters)           │
    └──────────────────────────────────────────┘
```

**Dòng chảy dữ liệu:**
1. Request đến → Middleware **tạo Correlation ID duy nhất** (ví dụ: `req-abc12345`)
2. Correlation ID **đính kèm vào mọi log** (để truy vết)
3. Logs được **xóa thông tin nhạy cảm** (PII scrubbing)
4. Logs được **ghi vào file** logs.jsonl dạng JSON
5. Traces được **gửi lên Langfuse** (dịch vụ tracing)
6. Metrics được **tính toán** (latency, error rate, cost)

---

### **3. CÁC VIỆC BẠN CẦN LÀM (Từng bước)**

#### **BƯỚC 1️⃣: Correlation ID Middleware** ⭐ **ĐÂY LÀ CỬ ĐỘNG ĐẦU TIÊN**
**Tệp:** middleware.py

**Làm gì?** Thêm code vào TODO comments để:
- 🔄 **Clear contextvars** tại đầu mỗi request (tránh rò rỉ dữ liệu qua các request khác nhau)
- 📌 **Tạo/Lấy x-request-id** từ headers request (nếu client gửi), nếu không thì tạo mới với format `req-<8-hex>`
- 🔗 **Bind correlation_id** vào structlog (để tất cả logs tự động có ID này)
- 📤 **Thêm headers vào response** (x-request-id, x-response-time-ms)

**Ý nghĩa:** Mỗi request có ID duy nhất được theo dõi từ đầu đến cuối. Giúp bạn xem toàn bộ journey.

---

#### **BƯỚC 2️⃣: Enrich Logs** (Làm phong phú log)
**Tệp:** main.py - trong hàm `chat()`

**Làm gì?** Thêm context vào log:
```python
bind_contextvars(
    user_id_hash=hash_user_id(body.user_id),  # Hash ID để bảo vệ
    session_id=body.session_id,
    feature=body.feature,
    model="gpt-4-turbo",
    env=os.getenv("APP_ENV", "dev")
)
```

**Ý nghĩa:** Bây giờ mỗi log sẽ tự động ghi kèm user, session, feature... Giúp filter và debug dễ hơn.

---

#### **BƯỚC 3️⃣: PII Scrubbing (Ẩn thông tin nhạy cảm)**
**Tệp:** pii.py + logging_config.py

**Làm gì?**
1. ➕ **Thêm regex patterns** để detect thêm PII (ví dụ: passport, địa chỉ Việt Nam, số CMND)
2. ✅ **Enable scrub_event processor** trong `configure_logging()`:
   ```python
   scrub_event,  # Thêm dòng này vào processors list
   ```

**Ý nghĩa:** Khi log được ghi, tất cả email, phone, CCCD sẽ tự động bị thay thế bằng `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`... → Bảo vệ dữ liệu khách hàng.

---

#### **BƯỚC 4️⃣: Xác thực Log bằng Script**
**Câu lệnh:**
```bash
python scripts/validate_logs.py
```

**Kết quả mong muốn:** Score ≥ 80/100
- ✓ Logs có correlation ID xuyên suốt
- ✓ Không có PII leaks
- ✓ Schema JSON đúng

---

#### **BƯỚC 5️⃣: Tạo Traces (Tracing)**
**Tệp:** tracing.py (xem file này)

**Làm gì?**
- Xác nhận Langfuse key đã cấu hình (trong .env)
- Gửi ít nhất **10 traces** lên Langfuse
- Mỗi trace theo dõi: LLM call → RAG retrieval → Response

**Cách test:**
```bash
python scripts/load_test.py --concurrency 5
```
Sau đó vào **Langfuse UI** → xem traces.

---

#### **BƯỚC 6️⃣: Xây dựng Dashboard (6 panels)**
**Tệp:** dashboard-spec.md

**6 panels bắt buộc:**
1. 📊 **Latency** (P50, P95, P99)
2. 📈 **Traffic** (request count)
3. ❌ **Error Rate** (với breakdown)
4. 💰 **Cost** (chi phí LLM theo thời gian)
5. 🔤 **Tokens** (tokens in/out)
6. ⭐ **Quality** (heuristic hoặc regenerate rate)

**Tool:** Dùng tool nào cũng được (Grafana, DataDog, Google Sheets + chart...)

---

#### **BƯỚC 7️⃣: Cảnh báo (Alerts & Runbooks)**
**Tệp:** alert_rules.yaml + alerts.md

**Tạo 3 rules cảnh báo:**
1. ⚠️ **High Latency**: P95 > 5 giây trong 30 phút
2. 🔴 **High Error Rate**: Lỗi > 5% trong 5 phút
3. 💥 **Cost Spike**: Chi phí giờ này gấp 2x bình thường trong 15 phút

**Mỗi alert cần Runbook:** Hướng dẫn debug bước 1, 2, 3...

---

#### **BƯỚC 8️⃣: Test Incident (Inject Failure)**
**Câu lệnh:**
```bash
# Bật scenario "RAG slow"
python scripts/inject_incident.py --scenario rag_slow

# Tạo requests để trigger
python scripts/load_test.py --concurrency 5

# Sau đó kiểm tra:
# - Dashboard có spike latency không?
# - Traces có thấy RAG span chậm không?
# - Alert có trigger không?
```

**Ý nghĩa:** Kiểm tra cả hệ thống observability có hoạt động đúng không.

---

#### **BƯỚC 9️⃣: Viết Báo Cáo**
**Tệp:** blueprint-template.md

**Điền vào:**
- 👥 Tên team members + vai trò từng người
- ✅ Validate logs score
- 📸 Screenshots (correlation ID, PII redaction, traces, dashboard)
- 🎯 Root cause analysis của incident
- 🔗 Git commit evidence (chứng minh mình đã code)

---

### **4. QUY TRÌNH LÀM (Thứ tự nên làm)**

```
START
  │
  ├─► ✅ Setup: pip install -r requirements.txt, copy .env
  │
  ├─► 👤 Gán vai trò từng người (xem drawf_report.md)
  │
  ├─► 📌 Person A: Middleware (Correlation ID)
  │     └─► Run: python scripts/validate_logs.py
  │
  ├─► 📝 Person A: PII Scrubbing + Logging Config
  │     └─► Run: python scripts/validate_logs.py (goal: ≥80/100)
  │
  ├─► 🏷️  Person B: Enrich Logs + Tracing (bind user, session, feature)
  │     └─► Run: python scripts/load_test.py
  │     └─► Check: 10+ traces in Langfuse
  │
  ├─► 📊 Person C: SLO Table + Metrics
  │     └─► Tính: P95 latency, error rate, cost
  │
  ├─► 📈 Person D: Dashboard (6 panels)
  │     └─► Run: export logs.jsonl → import vào tool visualize
  │
  ├─► ⚠️  Person E: Alerts + Runbooks
  │     └─► Config alert_rules.yaml
  │     └─► Write 3 runbooks
  │
  ├─► 🧪 TEAM: Test Incident
  │     └─► python scripts/inject_incident.py --scenario rag_slow
  │     └─► python scripts/load_test.py
  │     └─► Verify: Dashboard spike? Traces show root cause?
  │
  ├─► 📄 TEAM: Write Blueprint Report
  │     └─► Fill all sections in docs/blueprint-template.md
  │     └─► Add Git evidence (commits)
  │
  └─► 🎤 DEMO + Q&A (tối đa 20 phút)
       └─► Show live system
       └─► Trả lời các câu hỏi hóc búa của giảng viên
END
```

---

### **5. ĐIỂM SỐ (60/40 Split)**

| Phần | Điểm | Chi tiết |
|------|------|---------|
| **Nhóm (60%)** | **60** | |
| - Implementation | 30 | Logging, Tracing, Dashboard, Alerts |
| - Incident Debug | 10 | Tìm được root cause |
| - Live Demo | 20 | Trình bày + trả lời Q&A |
| **Cá nhân (40%)** | **40** | |
| - Báo cáo | 20 | Chi tiết công việc mình làm |
| - Git Evidence | 20 | Commit logs chứng minh code |
| **Bonus** | +10 | Tối ưu chi phí, Audit logs... |

**Điều kiện PASS:** VALIDATE_LOGS_SCORE ≥ 80/100 + 10 traces + 6 panels

---

### **6. FILES QUAN TRỌNG - HIỂU NGAY**

| File | Mục đích | Status |
|------|---------|--------|
| middleware.py | Tạo Correlation ID | ⚠️ **TODO #1** |
| main.py | Bind context vào logs | ⚠️ **TODO #2** |
| logging_config.py | Enable PII scrubbing | ⚠️ **TODO #3** |
| pii.py | Regex patterns PII | ⚠️ **TODO #4** |
| tracing.py | Gửi traces lên Langfuse | ✅ Đã xong |
| alert_rules.yaml | Cảnh báo khi sự cố | ⚠️ **TODO #5** |
| blueprint-template.md | Báo cáo team | ⚠️ **TODO #6** |

---

### **7. LỆNH THƯỜNG DÙNG**

```bash
# 1. Chạy app
uvicorn app.main:app --reload

# 2. Tạo requests (tạo logs)
python scripts/load_test.py --concurrency 5

# 3. Kiểm tra logs
python scripts/validate_logs.py

# 4. Inject incident (tạo failure để test cảnh báo)
python scripts/inject_incident.py --scenario rag_slow

# 5. Xem metrics
curl http://localhost:8000/metrics

# 6. Xem status
curl http://localhost:8000/health
```
