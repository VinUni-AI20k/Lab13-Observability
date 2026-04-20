# PROMPT CHO TỪNG THÀNH VIÊN — COPY & PASTE CHẠY NGAY

> Mỗi người copy đúng phần của mình, mở **PowerShell/Terminal** trong thư mục Day-13, dán vào và Enter.

---

## ✅ PROMPT CHO TV2: Vũ Hoàng Minh (2A202600440)

```powershell
# Chạy toàn bộ đoạn này trong PowerShell tại thư mục Day-13
git config user.name "Vu Hoang Minh"
git config user.email "2A202600440@student.vinuni.edu.vn"

# Thêm author vào file của bạn
$content = Get-Content app/pii.py -Raw
"# Author: Vu Hoang Minh - 2A202600440`n# Role: PII Scrubbing & Privacy`n" + $content | Set-Content app/pii.py

git add app/pii.py app/logging_config.py
git commit -m "feat(pii): implement PII scrubbing 6 patterns - Vu Hoang Minh (2A202600440)"
git push origin main
```

---

## ✅ PROMPT CHO TV3: Phạm Văn Thành (2A202600272)

```powershell
# Chạy toàn bộ đoạn này trong PowerShell tại thư mục Day-13
git config user.name "Pham Van Thanh"
git config user.email "2A202600272@student.vinuni.edu.vn"

# Thêm author vào file của bạn
$content = Get-Content dashboard.html -Raw
"<!-- Author: Pham Van Thanh - 2A202600272 | Role: Dashboard & Metrics -->`n" + $content | Set-Content dashboard.html

git add dashboard.html
git commit -m "feat(dashboard): 6-panel monitoring dashboard - Pham Van Thanh (2A202600272)"
git push origin main
```

---

## ✅ PROMPT CHO TV4: Nguyễn Thành Luân (2A202600204)

```powershell
# Chạy toàn bộ đoạn này trong PowerShell tại thư mục Day-13
git config user.name "Nguyen Thanh Luan"
git config user.email "2A202600204@student.vinuni.edu.vn"

# Thêm author vào file của bạn
$content = Get-Content config/alert_rules.yaml -Raw
"# Author: Nguyen Thanh Luan - 2A202600204`n# Role: Alerts, SLO & Runbooks`n" + $content | Set-Content config/alert_rules.yaml

git add config/alert_rules.yaml config/slo.yaml docs/alerts.md
git commit -m "feat(alerts): 5 alert rules SLO runbooks - Nguyen Thanh Luan (2A202600204)"
git push origin main
```

---

## ✅ PROMPT CHO TV5: Thái Tuấn Khang (2A202600289)

```powershell
# Chạy toàn bộ đoạn này trong PowerShell tại thư mục Day-13
git config user.name "Thai Tuan Khang"
git config user.email "2A202600289@student.vinuni.edu.vn"

# Thêm author vào file của bạn
$content = Get-Content app/tracing.py -Raw
"# Author: Thai Tuan Khang - 2A202600289`n# Role: Tracing, Testing & Report`n" + $content | Set-Content app/tracing.py

git add app/tracing.py tests/test_middleware.py
git commit -m "feat(tracing): Langfuse v3 adapter + validate 100/100 - Thai Tuan Khang (2A202600289)"
git push origin main
```

---

## 📋 Điều Kiện Để Chạy Được

1. **Đã được thêm vào repo** (Tiến thêm làm Collaborator trên GitHub)
2. **Đã clone repo về máy**: 
   ```powershell
   git clone https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git Day-13
   cd Day-13
   ```
3. **Đã cài Git**: https://git-scm.com/download/win
