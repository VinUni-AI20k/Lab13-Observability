# Hướng Dẫn Đẩy Code Lên GitHub — Lab 13 Observability

> **Repo chung**: https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability

---

## 👤 TV1: Trịnh Kế Tiến (2A202600500) — Correlation ID & Middleware

**Files phụ trách:** `app/middleware.py`, `app/main.py`

```powershell
# Bước 1: Clone repo
git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day13
cd Day13

# Bước 2: Cấu hình tên cho máy này
git config user.name "Trinh Ke Tien"
git config user.email "2A202600500@student.vinuni.edu.vn"

# Bước 3: Tạo branch cá nhân
git checkout -b tv1-middleware

# Bước 4: Chỉnh sửa file của bạn (middleware.py đã được implement)
# Thêm comment vào đầu file để có dấu ấn cá nhân:
# Mở app/middleware.py và thêm dòng: # Author: Trinh Ke Tien - 2A202600500

# Bước 5: Commit với tên của bạn
git add app/middleware.py app/main.py
git commit -m "feat(middleware): correlation ID middleware - Trinh Ke Tien (2A202600500)

- CorrelationIdMiddleware tạo req-<8hex> ID cho mỗi request
- clear_contextvars() để tránh context leakage
- bind_contextvars: user_id_hash, session_id, feature, model, env
- Inject x-request-id vào response headers"

# Bước 6: Push lên repo chung
git push origin tv1-middleware
```

---

## 👤 TV2: Vũ Hoàng Minh (2A202600440) — PII Scrubbing & Privacy

**Files phụ trách:** `app/pii.py`, `app/logging_config.py`, `tests/test_pii.py`

```powershell
# Bước 1: Clone repo
git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day13
cd Day13

# Bước 2: Cấu hình tên
git config user.name "Vu Hoang Minh"
git config user.email "2A202600440@student.vinuni.edu.vn"

# Bước 3: Tạo branch cá nhân
git checkout -b tv2-pii-scrubbing

# Bước 4: Thêm comment author vào đầu app/pii.py:
# # Author: Vu Hoang Minh - 2A202600440

# Bước 5: Commit
git add app/pii.py app/logging_config.py tests/test_pii.py
git commit -m "feat(pii): implement PII scrubbing - Vu Hoang Minh (2A202600440)

- 6 regex patterns: email, credit_card, cccd, phone_vn, passport, vn_address
- Fix regex ordering: cccd trước phone_vn để tránh collision
- Enable scrub_event processor trong structlog pipeline
- 12 test cases: all patterns, edge cases, hash determinism"

# Bước 6: Push
git push origin tv2-pii-scrubbing
```

---

## 👤 TV3: Phạm Văn Thành (2A202600272) — Dashboard & Metrics

**Files phụ trách:** `dashboard.html`

```powershell
# Bước 1: Clone repo
git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day13
cd Day13

# Bước 2: Cấu hình tên
git config user.name "Pham Van Thanh"
git config user.email "2A202600272@student.vinuni.edu.vn"

# Bước 3: Tạo branch cá nhân
git checkout -b tv3-dashboard

# Bước 4: Thêm comment vào đầu dashboard.html:
# <!-- Author: Pham Van Thanh - 2A202600272 -->

# Bước 5: Commit
git add dashboard.html
git commit -m "feat(dashboard): 6-panel real-time monitoring - Pham Van Thanh (2A202600272)

- Panel 1: Latency P50/P95/P99 + SLO line 3000ms
- Panel 2: Traffic count
- Panel 3: Error rate doughnut chart
- Panel 4: Cost + budget line $2.50
- Panel 5: Tokens In/Out stacked bar
- Panel 6: Quality score + SLO line 0.75
- Auto-refresh 15s, dark theme, Chart.js"

# Bước 6: Push
git push origin tv3-dashboard
```

---

## 👤 TV4: Nguyễn Thành Luân (2A202600204) — Alerts, SLO & Runbooks

**Files phụ trách:** `config/alert_rules.yaml`, `config/slo.yaml`, `docs/alerts.md`

```powershell
# Bước 1: Clone repo
git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day13
cd Day13

# Bước 2: Cấu hình tên
git config user.name "Nguyen Thanh Luan"
git config user.email "2A202600204@student.vinuni.edu.vn"

# Bước 3: Tạo branch cá nhân
git checkout -b tv4-alerts-slo

# Bước 4: Thêm comment vào đầu config/alert_rules.yaml:
# # Author: Nguyen Thanh Luan - 2A202600204

# Bước 5: Commit
git add config/alert_rules.yaml config/slo.yaml docs/alerts.md
git commit -m "feat(alerts): 5 alert rules + SLO + runbooks - Nguyen Thanh Luan (2A202600204)

- high_latency_p95 (P2): P95 > 5000ms for 30m
- high_error_rate (P1): Error > 5% for 15m
- cost_budget_spike (P2): Cost > $2.5/day
- quality_score_drop (P2): Quality < 0.65 for 1h
- token_budget_exceeded (P3): Tokens > 100k/day
- 4 SLO targets (latency/error/cost/quality) 28-day window
- Runbooks: Description, Impact, Investigation, Remediation, Prevention"

# Bước 6: Push
git push origin tv4-alerts-slo
```

---

## 👤 TV5: Thái Tuấn Khang (2A202600289) — Tracing, Testing & Report

**Files phụ trách:** `app/tracing.py`, `tests/test_middleware.py`, `docs/blueprint-template.md`

```powershell
# Bước 1: Clone repo
git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day13
cd Day13

# Bước 2: Cấu hình tên
git config user.name "Thai Tuan Khang"
git config user.email "2A202600289@student.vinuni.edu.vn"

# Bước 3: Tạo branch cá nhân
git checkout -b tv5-tracing-testing

# Bước 4: Thêm comment vào đầu app/tracing.py:
# # Author: Thai Tuan Khang - 2A202600289

# Bước 5: Chạy validate để confirm 100/100
python scripts/validate_logs.py

# Bước 6: Commit
git add app/tracing.py tests/test_middleware.py docs/blueprint-template.md
git commit -m "feat(tracing): Langfuse v3 adapter + validate 100/100 - Thai Tuan Khang (2A202600289)

- Migrate to Langfuse v3.2.1: from langfuse import observe, get_client
- _LangfuseContext adapter: merge usage_details -> metadata
- Graceful fallback decorator when Langfuse unavailable
- test_middleware.py: verify req-XXXXXXXX format, 100 IDs no collision
- validate_logs.py: 100/100 (schema, correlation_id, enrichment, PII)
- Load test: 30 requests, 100% success, incident injection verified"

# Bước 7: Push
git push origin tv5-tracing-testing
```

---

## 📌 Lưu Ý Chung

1. **Phải cài Git**: https://git-scm.com/download/win
2. **Cần quyền push**: Nhờ Tiến thêm bạn vào repo với quyền Contributor trên GitHub
3. **Nếu bị hỏi login GitHub**: Dùng tài khoản GitHub của bạn, hoặc Personal Access Token
4. **Sau khi push branch**: Mở GitHub → tạo Pull Request từ branch của bạn vào `main`

### Cách yêu cầu quyền push:
Tiến (owner) vào GitHub repo → `Settings` → `Collaborators` → `Add people` → nhập username GitHub của từng người.
