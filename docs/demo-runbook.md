# Day 13 Observability Demo Runbook

Use this runbook during the live demo so every rubric claim is backed by logs, traces, metrics, dashboard evidence, or configuration.

Suggested speaking order for this 4-member team:
1. Trần Đặng Quang Huy: intro, logging, correlation IDs, PII
2. Phạm Đan Kha: Langfuse traces and trace-waterfall explanation
3. Nguyễn Duy Hiếu: SLOs, alerts, and incident reasoning
4. Vũ Đức Kiên: dashboard walkthrough, live traffic, and screenshot checklist

## 1. Pre-demo verification

Run these commands from the repo root:

```powershell
cd "e:\AI Thuc Chien\New folder\Lab13-Observability"
python -m pytest -q
python scripts/validate_logs.py
```

Expected outcome:
- tests pass
- validator prints `Estimated Score: 100/100`
- you can say the logging/tracing core is verified before the audience joins

If you prefer a double-click launcher on Windows, run `run-dashboard.bat` from the repo root. It starts the app on a free local port and opens the dashboard automatically.

## 2. Start the app and health-check it

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/health` and say:
- the app is live
- tracing is enabled
- all incident toggles are off before the baseline run

## 3. Explain the architecture in one minute

Narration order:
1. request enters FastAPI
2. middleware injects or propagates `x-request-id`
3. logs are emitted as structured JSON and scrubbed for PII
4. the agent call emits Langfuse traces with metadata
5. `/metrics` aggregates latency, cost, traffic, errors, and quality

## 4. Show a clean baseline

In a second terminal:

```powershell
python scripts/load_test.py
```

While traffic runs, show:
- terminal responses with correlation IDs
- `data/logs.jsonl` lines that include `correlation_id`, `user_id_hash`, `session_id`, and `feature`
- a redacted email, phone number, or credit card value in the logs

## 5. Re-run the validator

```powershell
python scripts/validate_logs.py
```

Say:
- schema validation passes
- correlation propagation passes
- enrichment passes
- PII scrubbing passes

## 6. Show trace evidence in Langfuse

Open the Langfuse trace list and point out:
- at least 10 traces
- one full trace waterfall
- metadata fields for hashed user, session, feature, doc count, tokens, cost, and latency

Say:
- metrics show that something is wrong
- traces show where inside the request it is wrong
- logs provide the exact request context for debugging

## 7. Show the 6-panel dashboard

Required panels:
1. latency P50, P95, P99
2. traffic
3. error rate with breakdown
4. cost over time
5. tokens in and out
6. quality proxy

Say:
- the dashboard maps directly to `docs/dashboard-spec.md`
- SLO or threshold lines are visible where required
- this dashboard is the top-level operational view for the service

## 8. Run the main incident live

Use `rag_slow` as the primary scenario:

```powershell
python scripts/inject_incident.py --scenario rag_slow
python scripts/load_test.py --concurrency 5
```

Then show:
- latency increasing in `/metrics` or the dashboard
- slower traces in Langfuse
- correlated log lines for the same request IDs

Debugging story to narrate:
1. the metric shows the symptom
2. the trace isolates the slow path
3. the logs confirm affected requests and their context

## 9. Prove alert readiness

Open:
- `config/alert_rules.yaml`
- `docs/alerts.md`

Call out for each rule:
- severity
- threshold
- runbook link
- matching test scenario

## 10. Close with grading evidence

Present these artifacts:
- validator score
- trace count
- dashboard screenshot
- alert screenshot
- one trace waterfall screenshot
- one log screenshot with redaction

Then state:
- root cause of the injected incident
- corrective action
- preventive measure

## 11. Finalize the submission pack immediately after the demo

Update `docs/blueprint-template.md` with:
- final commit or PR links for each member
- screenshot file paths under `docs/evidence/`
- final incident notes if the live run exposed anything new

## Canonical screenshot filenames

Store evidence under `docs/evidence/` using these names:
- `correlation-id-log.png`
- `pii-redaction-log.png`
- `trace-waterfall.png`
- `dashboard-6-panels.png`
- `alert-rules.png`
