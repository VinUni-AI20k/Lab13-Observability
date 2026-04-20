# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: A20-Observability-Lab
- [REPO_URL]: https://github.com/trinhketien/2A202600500_TrinhKeTien_Lab13-Observability.git
- [MEMBERS]:
  - Member A: Trá»‹nh Káº¿ Tiáº¿n (2A202600500) | Role: Correlation ID & Middleware
  - Member B: VÅ© HoĂ ng Minh (2A202600440) | Role: PII Scrubbing & Privacy
  - Member C: Pháº¡m VÄƒn ThĂ nh (2A202600272) | Role: Dashboard & Metrics
  - Member D: Nguyá»…n ThĂ nh LuĂ¢n (2A202600204) | Role: Alerts, SLO & Runbooks
  - Member E: ThĂ¡i Tuáº¥n Khang (2A202600289) | Role: Tracing, Testing & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 35+ (15 REST API + 20 via app)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: Táº¥t cáº£ logs chá»©a `req-<8hex>` unique
  - Xem: `docs/screenshots/04_pii_redacted_logs.txt`
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: Verified:
  - `student@vinuni.edu.vn` â†’ `[REDACTED_EMAIL]`
  - `0987654321` â†’ `[REDACTED_PHONE_VN]`
  - `4111 1111 1111 1111` â†’ `[REDACTED_CREDIT_CARD]`
  - `012345678901` â†’ `[REDACTED_CCCD]`
  - `B12345678` â†’ `[REDACTED_PASSPORT]`
  - Xem: `docs/screenshots/04_pii_redacted_logs.txt`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: 20+ traces hiá»‡n trĂªn Langfuse self-hosted (localhost:3000)
  - Xem: `docs/screenshots/01_traces_list.png`
  - Xem: `docs/screenshots/02_trace_detail.png`
- [TRACE_WATERFALL_EXPLANATION]: Má»—i trace ghi nháº­n pipeline: request â†’ PII scrub â†’ RAG retrieval â†’ LLM generation â†’ response. Decorator `@observe()` trĂªn `LabAgent.run()` táº¡o parent span, metadata gá»“m doc_count, query_preview, token usage.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: `dashboard.html` â€” 6 panels Chart.js:
  - Xem: `docs/screenshots/03_langfuse_dashboard.png`
  - Xem: `docs/screenshots/07_langfuse_full_dashboard.png` â† Langfuse Dashboard: **20 Traces tracked**, biá»ƒu Ä‘á»“ traces theo thá»i gian (4/19-4/20/2026)
  1. **Latency P50/P95/P99** (line chart, SLO threshold 3000ms)
  2. **Traffic count** (line chart, request volume)
  3. **Error rate + breakdown** (doughnut chart)
  4. **Cost over time** (line chart, budget line $2.50)
  5. **Tokens In/Out** (bar chart)
  6. **Quality proxy score** (line chart, SLO 0.75)
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2651ms âœ… |
| Error Rate | < 2% | 28d | 0.0% âœ… |
| Cost Budget | < $2.5/day | 1d | $0.0605 âœ… |
| Quality Avg | â‰¥ 0.75 | 28d | 0.88 âœ… |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: 5 alert rules trong `config/alert_rules.yaml`
  1. `high_latency_p95` (P2) â€” threshold 5000ms for 30m
  2. `high_error_rate` (P1) â€” threshold 5% for 15m
  3. `cost_budget_spike` (P2) â€” threshold $2.5 for 1d
  4. `quality_score_drop` (P2) â€” threshold 0.65 for 1h
  5. `token_budget_exceeded` (P3) â€” threshold 100000 for 1d
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]:
  - Latency tÄƒng tá»« ~460ms baseline lĂªn ~2654ms (5.8x increase)
  - P95 latency vÆ°á»£t SLO threshold
  - Táº¥t cáº£ requests váº«n tráº£ 200 OK nhÆ°ng tail latency gĂ¢y suy giáº£m UX
- [ROOT_CAUSE_PROVED_BY]:
  - Metrics endpoint: `latency_p95: 2651ms` (vs ~150ms baseline)
  - Log timestamps: má»—i request máº¥t ~2654ms trong thá»i gian incident
  - Incident toggle `rag_slow` confirmed enabled via `/health`
  - Flow: Metrics (P95 spike) â†’ Traces (RAG span cháº­m) â†’ Logs (correlation ID xĂ¡c Ä‘á»‹nh request cá»¥ thá»ƒ)
- [FIX_ACTION]:
  - Disable incident toggle via `POST /incidents/rag_slow/disable`
  - RAG retrieval latency quay láº¡i normal
  - Post-fix: requests trá»Ÿ láº¡i ~460ms
- [PREVENTIVE_MEASURE]:
  - Alert rule `high_latency_p95` tá»± Ä‘á»™ng phĂ¡t hiá»‡n
  - Runbook hÆ°á»›ng dáº«n check RAG span vs LLM span
  - Long-term: circuit breaker cho RAG, fallback cached results

---

## 5. Individual Reports

---

### 5.1 Trá»‹nh Káº¿ Tiáº¿n (2A202600500) â€” Correlation ID & Middleware

**Pháº§n viá»‡c Ä‘áº£m nháº­n:**
- Thiáº¿t káº¿ vĂ  implement `CorrelationIdMiddleware` trong `app/middleware.py`
- Cáº¥u hĂ¬nh log enrichment trong `app/main.py` (endpoint `/chat`)
- ThĂªm `load_dotenv()` vĂ o `main.py` Ä‘á»ƒ load `.env` trÆ°á»›c khi import modules

**Chi tiáº¿t ká»¹ thuáº­t:**

1. **Correlation ID Generation**: Táº¡o ID dáº¡ng `req-<8-char-hex>` báº±ng `uuid.uuid4().hex[:8]`. UUID4 Ä‘áº£m báº£o uniqueness trĂªn distributed systems mĂ  khĂ´ng cáº§n central coordinator.

2. **Context Management**: Sá»­ dá»¥ng `structlog.contextvars` Ä‘á»ƒ:
   - `clear_contextvars()` Ä‘áº§u má»—i request â†’ trĂ¡nh context leakage giá»¯a requests
   - `bind_contextvars(correlation_id=cid)` â†’ má»i log trong request tá»± Ä‘á»™ng cĂ³ ID

3. **Response Headers**: ThĂªm `x-request-id` (correlation ID) vĂ  `x-response-time-ms` vĂ o response â†’ client cĂ³ thá»ƒ trace láº¡i request khi report bug.

4. **Log Enrichment**: Trong `/chat` endpoint, bind thĂªm 5 context fields:
   - `user_id_hash`: SHA-256 truncated 12 chars (khĂ´ng lÆ°u plaintext user ID)
   - `session_id`: Grouping requests cĂ¹ng phiĂªn
   - `feature`: Loáº¡i tĂ­nh nÄƒng (qa/summary)
   - `model`: Model LLM Ä‘ang dĂ¹ng
   - `env`: MĂ´i trÆ°á»ng (dev/staging/prod)

**BĂ i há»c rĂºt ra:**
- `contextvars` lĂ  cĂ¡ch thread-safe Ä‘á»ƒ truyá»n context trong async Python, khĂ´ng cáº§n truyá»n tham sá»‘ qua tá»«ng hĂ m.
- Correlation ID pháº£i Ä‘Æ°á»£c clear Ä‘áº§u request Ä‘á»ƒ trĂ¡nh "context pollution" â€” má»™t request nháº­n ID cá»§a request trÆ°á»›c.

**Evidence**: Commits trong `app/middleware.py`, `app/main.py`

---

### 5.2 VÅ© HoĂ ng Minh (2A202600440) â€” PII Scrubbing & Privacy

**Pháº§n viá»‡c Ä‘áº£m nháº­n:**
- Má»Ÿ rá»™ng PII regex patterns trong `app/pii.py`
- KĂ­ch hoáº¡t PII scrubbing processor trong `app/logging_config.py`
- Viáº¿t test cases cho PII trong `tests/test_pii.py`

**Chi tiáº¿t ká»¹ thuáº­t:**

1. **PII Regex Patterns**: XĂ¢y dá»±ng 6 patterns:
   - `email`: `[\w\.-]+@[\w\.-]+\.\w+` â€” match má»i dáº¡ng email
   - `credit_card`: `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b` â€” 16 digits, cĂ³/khĂ´ng separator
   - `cccd`: `\b\d{12}\b` â€” CCCD/CMND Viá»‡t Nam 12 sá»‘
   - `phone_vn`: `(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}` â€” SÄT VN
   - `passport`: `\b[A-Z]\d{7,8}\b` â€” Há»™ chiáº¿u format quá»‘c táº¿
   - `vn_address`: `(?:sá»‘\s+\d+|Ä‘Æ°á»ng\s+\S+|...)` â€” Äá»‹a chá»‰ Viá»‡t Nam

2. **Regex Ordering Bug & Fix**: PhĂ¡t hiá»‡n CCCD 12 chá»¯ sá»‘ (`012345678901`) bá»‹ phone regex match trÆ°á»›c (vĂ¬ báº¯t Ä‘áº§u báº±ng `0`). Fix: Ä‘áº·t `credit_card` â†’ `cccd` trÆ°á»›c `phone_vn` trong dict Ä‘á»ƒ longer patterns match trÆ°á»›c.

3. **Structlog Processor**: KĂ­ch hoáº¡t `scrub_event` processor trong pipeline â€” tá»± Ä‘á»™ng scan má»i string value trong log event vĂ  thay tháº¿ PII báº±ng `[REDACTED_*]`.

4. **Testing**: 12 test cases phá»§ táº¥t cáº£ patterns, edge cases (multiple PII, clean text), hash determinism, vĂ  summarize function.

**BĂ i há»c rĂºt ra:**
- Thá»© tá»± regex quan trá»ng khi patterns overlap â€” luĂ´n Ä‘áº·t specific/longer patterns trÆ°á»›c generic/shorter ones.
- PII scrubbing nĂªn á»Ÿ cuá»‘i structlog pipeline, trÆ°á»›c renderer, Ä‘á»ƒ catch má»i data.

**Evidence**: Commits trong `app/pii.py`, `app/logging_config.py`, `tests/test_pii.py`

---

### 5.3 Pháº¡m VÄƒn ThĂ nh (2A202600272) â€” Dashboard & Metrics Visualization

**Pháº§n viá»‡c Ä‘áº£m nháº­n:**
- Thiáº¿t káº¿ vĂ  xĂ¢y dá»±ng `dashboard.html` â€” real-time monitoring dashboard
- Cáº¥u hĂ¬nh Chart.js cho 6 panels theo spec `docs/dashboard-spec.md`
- TĂ­ch há»£p auto-refresh vĂ  SLO threshold lines

**Chi tiáº¿t ká»¹ thuáº­t:**

1. **Technology Stack**: HTML + CSS + Chart.js CDN â€” khĂ´ng cáº§n build tool, má»Ÿ trá»±c tiáº¿p trong browser. Dark theme cho professional look.

2. **6 Panels Implementation**:
   - **Panel 1 - Latency**: Line chart P50/P95/P99 vá»›i SLO line táº¡i 3000ms (mĂ u Ä‘á» dashed)
   - **Panel 2 - Traffic**: Line chart request count, border gradient xanh
   - **Panel 3 - Error Rate**: Doughnut chart phĂ¢n loáº¡i lá»—i (timeout, validation, internal)
   - **Panel 4 - Cost**: Line chart tá»•ng cost USD, budget line táº¡i $2.50
   - **Panel 5 - Tokens**: Stacked bar chart In/Out tokens â€” giĂºp theo dĂµi usage
   - **Panel 6 - Quality**: Line chart quality score, SLO line táº¡i 0.75

3. **Auto-refresh**: `setInterval(fetchMetrics, 15000)` â€” poll `/metrics` má»—i 15s, cáº­p nháº­t data + chart animation smooth.

4. **SLO Banner**: Header hiá»ƒn thá»‹ tráº¡ng thĂ¡i 4 SLO vá»›i indicator xanh/Ä‘á» real-time.

**BĂ i há»c rĂºt ra:**
- Dashboard nĂªn hiá»ƒn thá»‹ SLO thresholds trá»±c tiáº¿p trĂªn chart (khĂ´ng riĂªng báº£ng) Ä‘á»ƒ operator phĂ¡t hiá»‡n vi pháº¡m ngay báº±ng máº¯t.
- Auto-refresh 15s lĂ  cĂ¢n báº±ng giá»¯a real-time vĂ  táº£i server.

**Evidence**: File `dashboard.html`, demo live

---

### 5.4 Nguyá»…n ThĂ nh LuĂ¢n (2A202600204) â€” Alerts, SLO & Runbooks

**Pháº§n viá»‡c Ä‘áº£m nháº­n:**
- Thiáº¿t káº¿ 5 alert rules trong `config/alert_rules.yaml`
- Cáº¥u hĂ¬nh SLO targets trong `config/slo.yaml`
- Viáº¿t runbooks chi tiáº¿t trong `docs/alerts.md`

**Chi tiáº¿t ká»¹ thuáº­t:**

1. **5 Alert Rules**:

| Rule | Severity | Condition | Window |
|---|---|---|---|
| `high_latency_p95` | P2 | P95 > 5000ms | 30m |
| `high_error_rate` | P1 | Error > 5% | 15m |
| `cost_budget_spike` | P2 | Cost > $2.5 | 1d |
| `quality_score_drop` | P2 | Quality < 0.65 | 1h |
| `token_budget_exceeded` | P3 | Tokens > 100k | 1d |

2. **Severity Design**: P1 = immediate (page on-call), P2 = urgent (Slack alert), P3 = informational (email). Má»—i rule cĂ³ `for` window Ä‘á»ƒ trĂ¡nh false positive tá»« transient spikes.

3. **SLO Configuration**: 4 SLO targets vá»›i 28-day rolling window (phĂ¹ há»£p sprint cycle). Má»—i SLO cĂ³ `notes` mĂ´ táº£ rationale.

4. **Runbook Structure**: Má»—i alert cĂ³ 5 pháº§n:
   - Description â†’ khi nĂ o trigger
   - Impact â†’ áº£nh hÆ°á»Ÿng user
   - Investigation â†’ step-by-step debug
   - Remediation â†’ hĂ nh Ä‘á»™ng fix
   - Prevention â†’ long-term improvement

**BĂ i há»c rĂºt ra:**
- Alert fatigue lĂ  váº¥n Ä‘á» thá»±c táº¿ â€” cáº§n `for` window vĂ  severity phĂ¢n táº§ng rĂµ rĂ ng.
- Runbook pháº£i actionable (cĂ³ command cá»¥ thá»ƒ), khĂ´ng chá»‰ mĂ´ táº£ chung chung.

**Evidence**: Commits trong `config/alert_rules.yaml`, `config/slo.yaml`, `docs/alerts.md`

---

### 5.5 ThĂ¡i Tuáº¥n Khang (2A202600289) â€” Tracing, Testing & Integration

**Pháº§n viá»‡c Ä‘áº£m nháº­n:**
- Fix Langfuse v3.2.1 tracing adapter trong `app/tracing.py`
- Viáº¿t test middleware trong `tests/test_middleware.py`
- Cháº¡y load test, incident injection, vĂ  validation
- Tá»•ng há»£p bĂ¡o cĂ¡o nhĂ³m

**Chi tiáº¿t ká»¹ thuáº­t:**

1. **Langfuse v3 Migration**: SDK v3.2.1 thay Ä‘á»•i hoĂ n toĂ n API:
   - Import: `from langfuse import observe, get_client` (thay vĂ¬ `langfuse.decorators`)
   - Context: `get_client().update_current_trace()` (thay vĂ¬ `langfuse_context`)
   - `update_current_span()` khĂ´ng há»— trá»£ `usage_details` â†’ merge vĂ o `metadata`
   - Adapter class `_LangfuseContext` wrap API má»›i, giá»¯ interface cÅ© cho `agent.py`

2. **Testing Strategy**:
   - `test_middleware.py`: 2 tests verify correlation ID format (`req-XXXXXXXX`) vĂ  uniqueness (100 IDs, 0 collisions)
   - `test_metrics.py`: Percentile calculation (cĂ³ sáºµn)
   - Tá»•ng: 15/15 tests passed

3. **Load Testing & Validation**:
   - 3 batches Ă— 10 requests = 30 requests, 100% success rate
   - Incident injection `rag_slow`: latency 460ms â†’ 2654ms â†’ 460ms
   - `validate_logs.py`: 100/100 (4/4 checks PASSED)

4. **REST API Trace Ingestion**: Khi decorator-based tracing gáº·p delay, sá»­ dá»¥ng REST API `/api/public/ingestion` Ä‘á»ƒ gá»­i 15 traces trá»±c tiáº¿p â†’ 15/15 status 201 Created.

**BĂ i há»c rĂºt ra:**
- SDK major version changes cĂ³ thá»ƒ break import paths hoĂ n toĂ n â€” luĂ´n check `dir(module)` trÆ°á»›c khi assume API.
- `try/except` fallback pattern trong `tracing.py` lĂ  excellent practice â€” app cháº¡y bĂ¬nh thÆ°á»ng ngay cáº£ khi tracing service down.

**Evidence**: Commits trong `app/tracing.py`, `tests/test_middleware.py`, load_test output

---

## 6. Bonus Items
- [BONUS_DASHBOARD]: Dashboard dark theme, Chart.js animations, SLO threshold lines, auto-refresh 15s (+3Ä‘)
- [BONUS_AUDIT_LOGS]: Audit log path tĂ¡ch riĂªng táº¡i `data/audit.jsonl` (+2Ä‘)
- [BONUS_CUSTOM_METRIC]: Quality score proxy metric vá»›i heuristic scoring (+2Ä‘)
