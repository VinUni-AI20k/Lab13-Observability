# Evidence Collection Sheet

Team:
- Trần Đặng Quang Huy
- Phạm Đan Kha
- Nguyễn Duy Hiếu
- Vũ Đức Kiên

## Required screenshots
- Langfuse trace list with >= 10 traces
- One full trace waterfall
- JSON logs showing correlation_id
- Log line with PII redaction
- Dashboard with 6 panels
- Alert rules with runbook link

## Suggested capture ownership
- Trần Đặng Quang Huy: correlation-id log screenshot, PII redaction screenshot
- Phạm Đan Kha: trace list screenshot, trace waterfall screenshot
- Nguyễn Duy Hiếu: alert rules screenshot, runbook cross-check
- Vũ Đức Kiên: dashboard screenshot, optional incident before/after screenshot

## Current verified values
- Validator score: 100/100
- Trace count in `data/logs.jsonl`: 85
- PII leaks detected by validator: 0
- Clean-run metrics snapshot: latency P95 150ms, error rate 0.0%, avg cost 0.0018 USD/request

## Optional screenshots
- Incident before/after fix
- Cost comparison before/after optimization
- Auto-instrumentation proof
