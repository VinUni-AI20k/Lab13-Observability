# Alert Rules and Runbooks

This file is the runbook target referenced by `config/alert_rules.yaml`. The lab app exposes these signals through `/metrics`:

- `latency_p50`, `latency_p95`, `latency_p99`
- `traffic`
- `error_breakdown`
- `avg_cost_usd`, `total_cost_usd`
- `tokens_in_total`, `tokens_out_total`
- `quality_avg`

Recommended operating assumptions for this repo:

- Healthy baseline latency is roughly 150-300ms per request.
- `rag_slow` adds about 2.5s in retrieval and should push P95 above 1.2s almost immediately.
- `tool_fail` creates 500 responses from the retrieval layer and should show up as `RuntimeError`.
- `cost_spike` multiplies output tokens by 4 and should be visible in both cost and tokens-out charts.

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 1200 for 10m`
- Impact: tail latency breaches the latency SLO and users feel the app is slow even if median latency looks normal.
- Main signal:
  `latency_p95` or `latency_p99` climbs while traffic remains stable.
- First checks:
  1. Open slow traces from the last 10-15 minutes in Langfuse.
  2. Compare retrieval time versus LLM generation time inside the waterfall.
  3. Check whether the `rag_slow` incident toggle is currently enabled.
  4. Confirm whether only one feature is affected or every feature is slow.
- Likely root cause in this lab:
  `app/mock_rag.py` is sleeping for 2.5 seconds because `rag_slow` is enabled.
- Mitigation:
  - Disable `rag_slow` if this is an injected incident: `python scripts/inject_incident.py --scenario rag_slow --disable`
  - Reduce retrieval fanout or move to a fallback knowledge source.
  - Trim prompt/context if the LLM span is the real bottleneck.
- Evidence to capture:
  - one slow trace waterfall
  - dashboard panel showing P95/P99 crossing threshold

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: users receive failed responses and demo traffic may stop generating useful traces or quality data.
- Main signal:
  5xx responses increase and `error_breakdown` becomes non-empty.
- First checks:
  1. Group logs by `error_type`.
  2. Inspect recent failed traces and note where the exception occurs.
  3. Confirm whether the `tool_fail` incident toggle is enabled.
  4. Compare failure rate by feature to see whether the blast radius is limited.
- Likely root cause in this lab:
  `app/mock_rag.py` raises `RuntimeError("Vector store timeout")` when `tool_fail` is enabled.
- Mitigation:
  - Disable `tool_fail` if this is the planned incident.
  - Retry with a fallback retrieval path or bypass retrieval for low-risk prompts.
  - If the error is not part of the drill, inspect the last code change touching retrieval or request parsing.
- Evidence to capture:
  - one failed trace
  - one structured log line showing `error_type`

## 3. Cost budget spike
- Severity: P2
- Trigger: `avg_cost_usd > 0.004 for 10m`
- Impact: token burn increases faster than expected and the team can no longer explain cost behavior.
- Main signal:
  `avg_cost_usd` rises together with `tokens_out_total`, even if traffic is flat.
- First checks:
  1. Compare `tokens_in_total` versus `tokens_out_total`.
  2. Split traces by feature and model if your dashboard supports it.
  3. Check whether the `cost_spike` incident toggle is enabled.
  4. Verify whether a recent prompt/template change increased output length.
- Likely root cause in this lab:
  `app/mock_llm.py` multiplies output tokens by 4 when `cost_spike` is enabled.
- Mitigation:
  - Disable the incident toggle if this is part of the drill.
  - Shorten prompts and cap output length.
  - Route simple requests to a cheaper model tier.
- Evidence to capture:
  - cost panel before/after incident
  - tokens in/out panel showing output-token jump

## 4. Quality drop
- Severity: P3
- Trigger: `quality_score_avg < 0.85 for 15m`
- Impact: the system may still be up, but answers are becoming less grounded or less useful.
- Main signal:
  `quality_avg` trends downward while latency and error rate may still look healthy.
- First checks:
  1. Sample a few recent responses and compare them with the input question.
  2. Check whether retrieval returned any relevant document.
  3. Review logs for messages containing redaction markers or fallback answers.
- Likely root cause in this lab:
  retrieval misses, weak answer generation, or repeated fallback responses.
- Mitigation:
  - Improve retrieval keywords or corpus coverage.
  - Tighten prompt instructions for concise grounded answers.
  - Add better quality heuristics if the signal is too noisy.
- Evidence to capture:
  - quality panel with threshold line
  - one response example showing degraded quality

## 5. Traffic gap
- Severity: P3
- Trigger: `traffic < 10 requests in 5m during demo window`
- Impact: dashboards may look empty, making it hard to validate SLOs, alerts, and traces live.
- Main signal:
  traffic panel is flat or near zero while the app is otherwise healthy.
- First checks:
  1. Confirm the app is running and `/health` returns `ok`.
  2. Run `python scripts/load_test.py --concurrency 5`.
  3. Verify that the dashboard time window includes the latest requests.
- Likely root cause in this lab:
  load generation was not run, the wrong server address is in use, or the dashboard time range is off.
- Mitigation:
  - Re-run the load test to generate fresh data.
  - Check whether the app is listening on `127.0.0.1:8000`.
  - Refresh the dashboard time filter to the last 15-60 minutes.

## Suggested demo sequence

1. Start from a healthy baseline and capture one screenshot of all panels.
2. Enable `rag_slow`, run `python scripts/load_test.py --concurrency 5`, and show P95 rising.
3. Disable `rag_slow`, enable `tool_fail`, and show error-rate plus `error_breakdown`.
4. Disable `tool_fail`, enable `cost_spike`, and show cost/tokens-out increasing.
5. Reset incidents and capture a recovery screenshot for the report.
