# Day 13 – Observability Lab Report  
**Author:** Phạm Đan Kha  

> Individual report derived from `docs/blueprint-template.md`

---

## 1. Team Metadata

- **Group Name:** Huy-Kha-Hieu-Kien  
- **Repository:** https://github.com/khadpham/Lab13-Observability  

### Members

| Name | Role |
|------|------|
| Trần Đặng Quang Huy | Logging, PII, Final Integration |
| Phạm Đan Kha | Tracing, Enrichment, Trace Walkthrough |
| Nguyễn Duy Hiếu | SLOs, Alerts, Incident Reasoning |
| Vũ Đức Kiên | Load Testing, Dashboard, Evidence Capture |

---

## 2. Group Performance (Auto-Verified)

| Metric | Value |
|--------|------|
| Log Validation Score | **100 / 100** |
| Total Traces | **85** |
| PII Leaks Found | **0** |

---

## 3. Technical Evidence

### 3.1 Logging & Tracing

- **Correlation ID Evidence:**  
  `docs/evidence/correlation-id-log.png`

- **PII Redaction Evidence:**  
  `docs/evidence/pii-redaction-log.png`

- **Trace Waterfall Evidence:**  
  `docs/evidence/trace-waterfall.png`

- **Explanation:**  
  The slowest span occurs in the retrieval phase during `rag_slow`, confirming that the incident impacts tail latency before response generation.

---

### 3.2 Dashboard & SLOs

- **Dashboard Screenshot:**  
  `docs/evidence/dashboard-6-panels.png`

#### SLO Table

| SLI | Target | Window | Current |
|-----|--------|--------|--------|
| Latency (P95) | < 3000 ms | 28 days | 150 ms |
| Error Rate | < 2% | 28 days | 0.0% |
| Cost Budget | < $2.5/day | 1 day | $0.0018 / request |

---

### 3.3 Alerts & Runbook

- **Alert Rules:**  
  `docs/evidence/alert-rules.png`

- **Runbook:**  
  `docs/alerts.md#1-high-latency-p95`

---

## 4. Incident Response

- **Scenario:** `rag_slow`

- **Observed Symptoms:**
  - Increased P95 latency  
  - Tail latency spike on dashboard  
  - Slow traces visible in Langfuse  

- **Root Cause:**
  Identified via Langfuse Trace ID  
  `473e676cb3070b357fbb120c294b5edc`  
  and correlated logs with  
  `correlation_id=req-2f38c0a0`

- **Fix Action:**
  Disabled injected incident post-demo and reran traffic to verify latency recovery.

- **Preventive Measure:**
  - Add tail-latency alerting  
  - Review retrieval latency before deploying changes  

---

## 5. Individual Contribution

### Phạm Đan Kha

- **Tasks Completed:**
  - Prepared tracing walkthrough  
  - Verified Langfuse metadata  
  - Supported trace waterfall evidence during demo  

- **Evidence:**
  Commit/PR link to be attached after team push  
  (not available in local repository history)

---

## 6. Bonus Items

- **Cost Optimization:**  
  Not claimed (no before/after experiment conducted)

- **Audit Logs:**  
  Not claimed (`audit.jsonl` not implemented as pipeline)

- **Custom Metric:**  
  ✅ Claimed  

  The application exposes `quality_avg` (from `app/metrics.py`)  
  and visualizes it on the dashboard as the **“Quality Proxy”** panel.