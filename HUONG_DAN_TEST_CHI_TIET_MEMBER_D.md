================================================================================
HƯỚNG DẪN TEST CHI TIẾT - MEMBER D
Load Test + Incident Injection cho Banking Chatbot
================================================================================

📋 4 TASKS CHÍNH:
1. Enhanced Load Test Script
2. Banking-Specific Queries  
3. Banking-Specific Incidents
4. Load Test Report

Mỗi task có TÁC DỤNG riêng, tôi sẽ giải thích chi tiết.

================================================================================
TASK 1: ENHANCED LOAD TEST SCRIPT
================================================================================

📌 BẠN ĐÃ LÀM GÌ:
File: scripts/load_test.py
- Thêm class LoadTestMetrics để track metrics
- Thêm feature performance tracking
- Thêm error tracking
- Thêm summary report

🎯 TÁC DỤNG:
- Test xem chatbot chịu được BAO NHIÊU REQUESTS CÙNG LÚC
- Đo LATENCY (thời gian phản hồi): P50, P95, P99
- Đo ERROR RATE (tỷ lệ lỗi)
- So sánh PERFORMANCE giữa các features (credit_inquiry vs card_info)
- Cung cấp DATA cho Member E build dashboard

🧪 CÁCH TEST:

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 1.1: Load Test Đơn Giản (1 request)                               │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
python scripts/load_test.py --concurrency 1

KẾT QUẢ MONG ĐỢI:
Starting load test with 1 concurrent workers...
Total queries: 25
[200] req-a1b2c3d4 | qa | 245.3ms
[200] req-e5f6g7h8 | credit_inquiry | 267.2ms
...
================================================================================
LOAD TEST SUMMARY - Banking Chatbot
================================================================================
Duration: 12.45s
Total Requests: 25
Successful: 25 (100.0%)
Failed: 0 (0.0%)

Latency Statistics:
  P50: 180.5ms
  P95: 1800.2ms
  P99: 2200.8ms
  Min: 150.1ms
  Max: 2300.5ms
  Avg: 245.3ms

Feature Performance:
  credit_inquiry:
    Requests: 5 | Success: 100.0%
    P95: 1900.0ms | Avg: 260.0ms
  card_info:
    Requests: 4 | Success: 100.0%
    P95: 1800.0ms | Avg: 240.0ms
  account_balance:
    Requests: 6 | Success: 100.0%
    P95: 1850.0ms | Avg: 250.0ms
================================================================================

GIẢI THÍCH OUTPUT:
- Duration: 12.45s → Tổng thời gian test
- Total Requests: 25 → Gửi 25 requests (từ sample_queries.jsonl)
- Successful: 25 (100%) → Tất cả thành công
- P50: 180.5ms → 50% requests nhanh hơn 180ms
- P95: 1800.2ms → 95% requests nhanh hơn 1800ms (SLO < 3000ms)
- P99: 2200.8ms → 99% requests nhanh hơn 2200ms
- Feature Performance → Hiệu suất từng tính năng banking

TẠI SAO QUAN TRỌNG:
✅ P95 < 3000ms → ĐẠT SLO (Service Level Objective)
✅ Success rate = 100% → Không có lỗi
✅ Feature breakdown → Biết feature nào chậm nhất

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 1.2: Load Test 5 Concurrent (Normal Load)                         │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
python scripts/load_test.py --concurrency 5

TÁC DỤNG:
- Test chatbot với 5 USERS CÙNG LÚC (normal load)
- Xem có bị chậm không khi nhiều người dùng
- Đây là load BÌNH THƯỜNG của chatbot banking

KẾT QUẢ MONG ĐỢI:
Starting load test with 5 concurrent workers...
[200] req-aaaa | credit_inquiry | 245ms
[200] req-bbbb | card_info | 198ms
[200] req-cccc | account_balance | 267ms
[200] req-dddd | loan_status | 289ms
[200] req-eeee | payment_schedule | 234ms
...
Total Requests: 25
Successful: 25 (100.0%)
P95: 1800ms

TẠI SAO QUAN TRỌNG:
✅ Chatbot phải xử lý được 5 users cùng lúc
✅ Latency không tăng nhiều (vẫn ~1800ms)
✅ Đây là baseline để so sánh khi có incident

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 1.3: Load Test 20 Concurrent (Peak Load)                          │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
python scripts/load_test.py --concurrency 20

TÁC DỤNG:
- Test chatbot với 20 USERS CÙNG LÚC (peak load)
- Giả lập GIỜ CAO ĐIỂM (8-10 AM, 5-7 PM)
- Xem chatbot có bị OVERLOAD không

KẾT QUẢ MONG ĐỢI:
Starting load test with 20 concurrent workers...
...
Total Requests: 25
Successful: 24 (96.0%)
Failed: 1 (4.0%)
P95: 2800ms  ← TĂNG TỪ 1800ms!

Error Breakdown:
  TimeoutError: 1

TẠI SAO QUAN TRỌNG:
⚠️ Success rate giảm xuống 96% (có 1 lỗi)
⚠️ P95 tăng lên 2800ms (+55%)
⚠️ Có TimeoutError → Cần scale thêm instances

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 1.4: Filter by Feature                                            │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
python scripts/load_test.py --concurrency 5 --filter-feature credit_inquiry

TÁC DỤNG:
- Test CHỈ 1 FEATURE cụ thể (credit_inquiry)
- Xem feature này có vấn đề gì không
- Hữu ích khi debug lỗi của 1 feature

KẾT QUẢ MONG ĐỢI:
Filtered to 5 requests for feature: credit_inquiry
Starting load test with 5 concurrent workers...
[200] req-aaaa | credit_inquiry | 260ms
[200] req-bbbb | credit_inquiry | 275ms
...
Feature Performance:
  credit_inquiry:
    Requests: 5 | Success: 100.0%
    P95: 1900.0ms | Avg: 260.0ms

TẠI SAO QUAN TRỌNG:
✅ Isolate 1 feature để debug
✅ So sánh performance giữa các features
✅ Tìm feature nào chậm nhất

================================================================================
TASK 2: BANKING-SPECIFIC QUERIES
================================================================================

📌 BẠN ĐÃ LÀM GÌ:
File: data/sample_queries.jsonl
- Thêm 15 câu hỏi banking (credit_inquiry, card_info, account_balance, etc.)
- Câu hỏi có PII (email, phone, CCCD) để test scrubbing

🎯 TÁC DỤNG:
- Cung cấp REALISTIC TEST DATA cho banking chatbot
- Test các features banking: vay tiền, thẻ tín dụng, số dư, etc.
- Test PII scrubbing (Member A đã làm)
- Đảm bảo chatbot hiểu tiếng Việt

🧪 CÁCH TEST:

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 2.1: Xem Banking Queries                                          │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
type data\sample_queries.jsonl

KẾT QUẢ MONG ĐỢI:
{"user_id":"u_banking_001","session_id":"s_morning_peak_001","feature":"credit_inquiry","message":"Tôi muốn vay 100 triệu đồng để mua nhà, lãi suất bao nhiêu? Email tôi là nguyen.van.a@gmail.com"}
{"user_id":"u_banking_002","session_id":"s_morning_peak_002","feature":"card_info","message":"Thẻ tín dụng của tôi có hạn mức bao nhiêu? Số thẻ là 4111 5555 6666 7777"}
{"user_id":"u_banking_003","session_id":"s_morning_peak_003","feature":"account_balance","message":"Số dư tài khoản 0123456789 của tôi là bao nhiêu? CCCD: 001234567890"}
...

GIẢI THÍCH:
- feature: credit_inquiry → Vay tiền
- feature: card_info → Thẻ tín dụng
- feature: account_balance → Số dư tài khoản
- feature: loan_status → Trạng thái khoản vay
- feature: payment_schedule → Lịch trả nợ

TẠI SAO QUAN TRỌNG:
✅ Queries có PII (email, phone, CCCD) → Test scrubbing
✅ Queries tiếng Việt → Test chatbot hiểu tiếng Việt
✅ Queries realistic → Giống câu hỏi thật của khách hàng

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 2.2: Count Banking Queries                                        │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
find /c "u_banking" data\sample_queries.jsonl

KẾT QUẢ MONG ĐỢI:
15

GIẢI THÍCH:
- Có 15 banking queries (u_banking_001 đến u_banking_015)
- Đủ để test các features banking

TẠI SAO QUAN TRỌNG:
✅ Đủ data để test
✅ Cover tất cả features banking

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 2.3: Test PII Scrubbing (Member A đã làm)                         │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"user_id\":\"u_test\",\"session_id\":\"s_test\",\"feature\":\"qa\",\"message\":\"Email tôi là test@gmail.com và SĐT 0912345678\"}"

KẾT QUẢ MONG ĐỢI:
{"answer":"...","correlation_id":"req-12345678",...}

SAU ĐÓ CHECK LOGS:
curl http://127.0.0.1:8000/logs

TÌM THẤY:
"message_preview":"Email tôi là [REDACTED_EMAIL] và SĐT [REDACTED_PHONE_VN]"

TẠI SAO QUAN TRỌNG:
✅ PII đã bị scrub (email, phone)
✅ Logs không chứa thông tin nhạy cảm
✅ Tuân thủ quy định bảo mật

================================================================================
TASK 3: BANKING-SPECIFIC INCIDENTS
================================================================================

📌 BẠN ĐÃ LÀM GÌ:
File: app/incidents.py, app/mock_rag.py, app/mock_llm.py, app/agent.py
- Thêm 5 incidents: account_lookup_slow, credit_check_fail, high_token_usage, rate_limiter_triggered, core_banking_fail
- Implement logic để simulate incidents

🎯 TÁC DỤNG:
- SIMULATE SỰ CỐ THẬT (database chậm, API lỗi, etc.)
- Test chatbot hoạt động thế nào KHI CÓ LỖI
- Train team INCIDENT RESPONSE (phát hiện, debug, fix)
- Chuẩn bị cho PRODUCTION (biết cách handle lỗi)

🧪 CÁCH TEST:

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 3.1: List All Incidents                                           │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
curl http://127.0.0.1:8000/incidents/status

KẾT QUẢ MONG ĐỢI:
{
  "rag_slow": false,
  "tool_fail": false,
  "cost_spike": false,
  "account_lookup_slow": false,
  "credit_check_fail": false,
  "rate_limiter_triggered": false,
  "high_token_usage": false,
  "core_banking_fail": false
}

GIẢI THÍCH:
- 8 incidents total (3 original + 5 banking)
- Tất cả = false (không có sự cố)

TẠI SAO QUAN TRỌNG:
✅ Biết có bao nhiêu incidents
✅ Check status trước khi test

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 3.2: INCIDENT - account_lookup_slow                               │
└─────────────────────────────────────────────────────────────────────────┘

TÁC DỤNG:
Simulate DATABASE QUERY CHẬM khi tra cứu tài khoản
→ Giống như database bị overload hoặc query không tối ưu

BƯỚC 1: Chạy load test BÌNH THƯỜNG (baseline)
----------------------------------------------
python scripts/load_test.py --concurrency 5

GHI NHỚ:
P95: 1800ms
Success: 100%

BƯỚC 2: BẬT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/enable

KẾT QUẢ:
{"ok":true,"incidents":{"account_lookup_slow":true,...}}

BƯỚC 3: Chạy load test VỚI SỰ CỐ
---------------------------------
python scripts/load_test.py --concurrency 5

KẾT QUẢ MONG ĐỢI:
[200] req-aaaa | credit_inquiry | 2645ms  ← CHẬM HƠN!
[200] req-bbbb | card_info | 2598ms      ← CHẬM HƠN!
[200] req-cccc | account_balance | 2667ms ← CHẬM HƠN!
...
P95: 2800ms  ← TĂNG TỪ 1800ms (+55%)!
Success: 100%

GIẢI THÍCH:
- Latency TĂNG từ 1800ms → 2800ms (+55%)
- Vì mock_rag.py có: time.sleep(2.5) khi account_lookup_slow = true
- Simulate database query chậm 2.5 giây

BƯỚC 4: CHECK METRICS
---------------------
curl http://127.0.0.1:8000/metrics

KẾT QUẢ:
{
  "latency_p95": 2800,  ← TĂNG!
  ...
}

BƯỚC 5: TẮT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/account_lookup_slow/disable

KẾT QUẢ:
{"ok":true,"incidents":{"account_lookup_slow":false,...}}

BƯỚC 6: Chạy load test SAU KHI TẮT (recovery)
----------------------------------------------
python scripts/load_test.py --concurrency 5

KẾT QUẢ MONG ĐỢI:
P95: 1800ms  ← TRỞ VỀ BÌNH THƯỜNG!
Success: 100%

TẠI SAO QUAN TRỌNG:
✅ Biết latency tăng BAO NHIÊU khi database chậm
✅ Biết cách PHÁT HIỆN (monitor latency_p95)
✅ Biết cách FIX (add caching, optimize query)
✅ Train team incident response

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 3.3: INCIDENT - credit_check_fail                                 │
└─────────────────────────────────────────────────────────────────────────┘

TÁC DỤNG:
Simulate CREDIT CHECK API LỖI (credit bureau down)
→ Giống như API của ngân hàng trung ương bị sập

BƯỚC 1: BẬT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/credit_check_fail/enable

BƯỚC 2: Chạy load test CHỈ credit_inquiry
------------------------------------------
python scripts/load_test.py --concurrency 5 --filter-feature credit_inquiry

KẾT QUẢ MONG ĐỢI:
[500] ERROR | credit_inquiry | RuntimeError: Credit check service unavailable
[500] ERROR | credit_inquiry | RuntimeError: Credit check service unavailable
[200] req-aaaa | credit_inquiry | 245ms
...
Success: 88% (12% LỖI!)  ← CÓ LỖI!

Error Breakdown:
  RuntimeError: 3

GIẢI THÍCH:
- 12% requests BỊ LỖI (RuntimeError)
- Vì agent.py có: raise RuntimeError khi credit_check_fail = true
- Simulate credit check API down

BƯỚC 3: TẮT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/credit_check_fail/disable

BƯỚC 4: Chạy load test lại
---------------------------
python scripts/load_test.py --concurrency 5 --filter-feature credit_inquiry

KẾT QUẢ:
Success: 100%  ← TRỞ VỀ BÌNH THƯỜNG!

TẠI SAO QUAN TRỌNG:
✅ Biết error rate tăng BAO NHIÊU khi API lỗi
✅ Biết cách PHÁT HIỆN (monitor error_rate)
✅ Biết cách FIX (fallback to cached data, retry)
✅ Biết cách NOTIFY customer (show error message)

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 3.4: INCIDENT - high_token_usage                                  │
└─────────────────────────────────────────────────────────────────────────┘

TÁC DỤNG:
Simulate LLM TẠO RESPONSE DÀI (verbose)
→ Giống như prompt không tối ưu, LLM trả lời dài dòng

BƯỚC 1: CHECK COST TRƯỚC
-------------------------
curl http://127.0.0.1:8000/metrics

GHI NHỚ:
avg_cost_usd: 0.0025
tokens_out_total: 3000

BƯỚC 2: BẬT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/high_token_usage/enable

BƯỚC 3: Chạy load test
-----------------------
python scripts/load_test.py --concurrency 5

BƯỚC 4: CHECK COST SAU
-----------------------
curl http://127.0.0.1:8000/metrics

KẾT QUẢ MONG ĐỢI:
{
  "avg_cost_usd": 0.0048,  ← TĂNG TỪ 0.0025 (+92%)!
  "tokens_out_total": 6000,  ← TĂNG GẤP ĐÔI!
  ...
}

GIẢI THÍCH:
- Cost TĂNG từ $0.0025 → $0.0048 (+92%)
- Vì mock_llm.py có: output_tokens *= 2 khi high_token_usage = true
- Simulate LLM tạo response dài gấp đôi

BƯỚC 5: TẮT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/high_token_usage/disable

TẠI SAO QUAN TRỌNG:
✅ Biết cost tăng BAO NHIÊU khi LLM verbose
✅ Biết cách PHÁT HIỆN (monitor avg_cost_usd)
✅ Biết cách FIX (optimize prompt, add length constraint)
✅ Tránh VƯỢT BUDGET

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 3.5: INCIDENT - core_banking_fail                                 │
└─────────────────────────────────────────────────────────────────────────┘

TÁC DỤNG:
Simulate HỆ THỐNG NGÂN HÀNG SẬP (core banking down)
→ Giống như API core banking bị sập hoàn toàn

BƯỚC 1: BẬT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/core_banking_fail/enable

BƯỚC 2: Chạy load test
-----------------------
python scripts/load_test.py --concurrency 5

KẾT QUẢ MONG ĐỢI:
[500] ERROR | credit_inquiry | RuntimeError: Lỗi hệ thống khi móc nối API Core Banking
[500] ERROR | card_info | RuntimeError: Lỗi hệ thống khi móc nối API Core Banking
...
Success: 0% (100% LỖI!)  ← TẤT CẢ LỖI!

GIẢI THÍCH:
- TẤT CẢ requests BỊ LỖI
- Vì agent.py có: raise RuntimeError khi core_banking_fail = true
- Simulate core banking API down

BƯỚC 3: TẮT SỰ CỐ
------------------
curl -X POST http://127.0.0.1:8000/incidents/core_banking_fail/disable

TẠI SAO QUAN TRỌNG:
✅ Biết chatbot hoạt động thế nào khi core banking sập
✅ Biết cách PHÁT HIỆN (monitor error_rate > 50%)
✅ Biết cách HANDLE (show maintenance page, queue requests)
✅ Escalate to P1 (critical incident)

================================================================================
TASK 4: LOAD TEST REPORT
================================================================================

📌 BẠN ĐÃ LÀM GÌ:
File: docs/load_test_report.md
- Document 3 test scenarios (Normal, Peak, Stress)
- Analyze 5 incident impacts
- Provide recommendations

🎯 TÁC DỤNG:
- DOCUMENT findings từ load test
- SHARE với team (Member E, F)
- JUSTIFY recommendations (add caching, scale, etc.)
- EVIDENCE cho grading

🧪 CÁCH TEST:

┌─────────────────────────────────────────────────────────────────────────┐
│ TEST 4.1: Xem Report                                                   │
└─────────────────────────────────────────────────────────────────────────┘

COMMAND:
type docs\load_test_report.md

KẾT QUẢ:
- Executive Summary
- 3 Test Scenarios
- Feature Performance Analysis
- 5 Incident Impact Analyses
- Recommendations

TẠI SAO QUAN TRỌNG:
✅ Document findings
✅ Share với team
✅ Evidence cho grading

================================================================================
TÓM TẮT: TẠI SAO CẦN TEST?
================================================================================

TASK 1: Load Test Script
→ Đo PERFORMANCE (latency, error rate)
→ Biết chatbot chịu được BAO NHIÊU USERS
→ Cung cấp DATA cho dashboard

TASK 2: Banking Queries
→ Test với REALISTIC DATA
→ Test PII scrubbing
→ Test tiếng Việt

TASK 3: Incidents
→ SIMULATE SỰ CỐ THẬT
→ Train team INCIDENT RESPONSE
→ Biết cách PHÁT HIỆN + FIX

TASK 4: Report
→ DOCUMENT findings
→ JUSTIFY recommendations
→ EVIDENCE cho grading

================================================================================
CHECKLIST CUỐI CÙNG
================================================================================

□ TEST 1.1: Load test 1 concurrent (baseline)
□ TEST 1.2: Load test 5 concurrent (normal load)
□ TEST 1.3: Load test 20 concurrent (peak load)
□ TEST 2.1: Xem banking queries
□ TEST 2.2: Count banking queries (15 queries)
□ TEST 2.3: Test PII scrubbing
□ TEST 3.1: List all incidents
□ TEST 3.2: Test account_lookup_slow (latency +55%)
□ TEST 3.3: Test credit_check_fail (error rate +12%)
□ TEST 3.4: Test high_token_usage (cost +92%)
□ TEST 3.5: Test core_banking_fail (error rate 100%)
□ TEST 4.1: Xem load test report

================================================================================
KẾT LUẬN
================================================================================

BẠN ĐÃ LÀM:
✅ Enhanced load test script
✅ 15 banking queries
✅ 5 banking incidents
✅ Load test report

TÁC DỤNG:
✅ Đo performance
✅ Simulate sự cố
✅ Train incident response
✅ Cung cấp data cho dashboard
✅ Document findings

GOOD LUCK! 🚀
================================================================================
