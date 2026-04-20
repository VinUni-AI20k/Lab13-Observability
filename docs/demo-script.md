# Demo Script — Day 13 Observability Lab

**Presenter**: Nguyễn Hải Văn (Dung)  
**Duration**: ~5 minutes  
**Goal**: Show the full observability stack running live — logs, metrics, alerts, incident response

---

## Setup (before presentation)

```bash
# Terminal 1 — start the app
uvicorn app.main:app --reload

# Terminal 2 — ready for commands
cd /path/to/Lab13-Observability
```

---

## Step 1 — Show the running system (30s)

```bash
curl http://127.0.0.1:8000/health
```

**Say**: "The system is up. Tracing is enabled via Langfuse. No incidents active."

---

## Step 2 — Generate traffic and show logs (60s)

```bash
python scripts/load_test.py --concurrency 5
```

Open `data/logs.jsonl` in editor or run:
```bash
tail -n 5 data/logs.jsonl | python3 -m json.tool
```

**Point out**:
- `correlation_id: req-xxxxxxxx` present on every log
- `user_id_hash` — PII-safe, never raw user ID
- `feature`, `model`, `session_id` — full enrichment context
- `payload.message_preview` — truncated, PII scrubbed

---

## Step 3 — Show metrics (30s)

```bash
curl http://127.0.0.1:8000/metrics
```

**Point out**:
- `latency_p50/p95/p99` — all well under 3000ms SLO
- `quality_avg` — above 0.75 SLO target
- `total_cost_usd` — well within $2.50/day budget
- `error_breakdown: {}` — zero errors

---

## Step 4 — Inject incident (90s)

```bash
# Enable rag_slow incident
python scripts/inject_incident.py --scenario rag_slow
```

Send a few requests:
```bash
for i in 1 2 3; do curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","session_id":"s1","feature":"qa","message":"test"}'; done
```

Check metrics again:
```bash
curl http://127.0.0.1:8000/metrics
```

**Say**: "P95 latency spiked. In a real setup, the `high_latency_p95` alert would fire after 30 minutes. The runbook tells on-call to check which span is slow — and the trace shows it's `retrieve()`, not the LLM."

---

## Step 5 — Fix and verify (30s)

```bash
python scripts/inject_incident.py --scenario rag_slow --disable
curl http://127.0.0.1:8000/metrics
```

**Say**: "Latency returns to normal. The alert would resolve. Runbook step: confirm with `/metrics` and Langfuse traces."

---

## Step 6 — Show validate_logs score (30s)

```bash
python scripts/validate_logs.py
```

**Expected output**:
```
+ [PASSED] Basic JSON schema
+ [PASSED] Correlation ID propagation
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing
Estimated Score: 100/100
```

---

## Step 7 — Show dashboard (30s)

Open Grafana (if available) and show the 6-panel dashboard imported from `config/grafana_dashboard.json`.

If no Grafana: show the JSON file and describe each panel:
1. **Latency P50/P95/P99** — SLO line at 3000ms
2. **Traffic** — request count stat
3. **Error Rate** — gauge with red zone at 5%
4. **Cost Over Time** — area chart with $2.50/day SLO line
5. **Tokens In/Out** — stacked bar showing prompt vs completion ratio
6. **Quality Score** — gauge, green ≥ 0.75, red < 0.60

---

## Closing (15s)

"This system gives us the four observability signals we need for an LLM agent: structured logs with correlation IDs and PII scrubbing, distributed traces via Langfuse, in-memory RED + quality metrics, and SLO-aligned alerts with actionable runbooks."
