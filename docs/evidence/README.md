# Evidence Artifacts

Save the screenshots used in the report and live demo in this folder.

## Required filenames

- `correlation-id-log.png`
- `pii-redaction-log.png`
- `trace-waterfall.png`
- `dashboard-6-panels.png`
- `alert-rules.png`

## What each file should show

- `correlation-id-log.png`: JSON log lines with `correlation_id`, `user_id_hash`, `session_id`, and `feature`
- `pii-redaction-log.png`: a log line where email, phone, passport, or card data is redacted
- `trace-waterfall.png`: one full Langfuse trace waterfall with useful metadata visible
- `dashboard-6-panels.png`: the six required panels from `docs/dashboard-spec.md`
- `alert-rules.png`: the alert rules with visible runbook references

## Capture checklist

Before submission, confirm:
- screenshots are up to date with the final demo run
- screenshot names match the paths referenced in `docs/blueprint-template.md`
- the trace screenshot clearly shows the latency story for the chosen incident

## Team assignments

- `correlation-id-log.png` and `pii-redaction-log.png`: Trần Đặng Quang Huy
- `trace-waterfall.png`: Phạm Đan Kha
- `alert-rules.png`: Nguyễn Duy Hiếu
- `dashboard-6-panels.png`: Vũ Đức Kiên
