# 6-Panel Dashboard Spec

Source of truth: `GET /metrics` from the FastAPI app, exported on a rolling basis into your dashboard tool of choice.

## Panel 1 — Latency P50 / P95 / P99
- **Metric fields:** `latency_p50`, `latency_p95`, `latency_p99`
- **Visualization:** line chart
- **Unit:** ms
- **Threshold line:** `latency_p95_ms = 3000` (SLO target)
- **Notes:** Use the same 1h window and compare all three percentiles on one plot.

## Panel 2 — Traffic
- **Metric fields:** `traffic`, `request_total`
- **Visualization:** time series or single-stat + sparkline
- **Unit:** requests
- **Threshold line:** none required; optional target for load-test runs
- **Notes:** Show request volume and include error-inclusive total if your dashboard source supports it.

## Panel 3 — Error Rate With Breakdown
- **Metric fields:** `error_rate_pct`, `error_count_total`, `error_breakdown`
- **Visualization:** stacked bar or pie for breakdown + line for rate
- **Unit:** %, count
- **Threshold line:** `error_rate_pct = 2`
- **Notes:** Break out `RuntimeError` vs any other error types so incident testing is obvious.

## Panel 4 — Cost Over Time
- **Metric fields:** `avg_cost_usd`, `total_cost_usd`
- **Visualization:** line chart
- **Unit:** USD
- **Threshold line:** `daily_cost_usd = 2.5`
- **Notes:** If your dashboard tool supports a rate function, add an estimated hourly burn as a secondary series.

## Panel 5 — Tokens In / Out
- **Metric fields:** `tokens_in_total`, `tokens_out_total`
- **Visualization:** dual-line or stacked bar
- **Unit:** tokens
- **Threshold line:** none required
- **Notes:** Token volume should visibly jump when the `cost_spike` incident is enabled.

## Panel 6 — Quality Proxy
- **Metric fields:** `quality_avg`
- **Visualization:** gauge or line chart
- **Unit:** score from 0.0 to 1.0
- **Threshold line:** `quality_score_avg = 0.75`
- **Notes:** Use this as the top-level quality bar for the agent output.

## Dashboard settings
- **Default time range:** 1 hour
- **Auto-refresh:** 15–30 seconds
- **Main layer size:** 6 panels
- **Labels:** always show units in panel titles
- **Reference lines:** include SLO or alert thresholds where relevant

## Suggested layout
1. Latency
2. Traffic
3. Error rate
4. Cost
5. Tokens
6. Quality

This layout matches the lab rubric and maps directly to the exported metrics payload.
