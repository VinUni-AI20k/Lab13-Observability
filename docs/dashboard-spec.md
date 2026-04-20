# Dashboard Spec

Required Layer-2 panels:
1. Latency P50/P95/P99
2. Traffic (request count or QPS)
3. Error rate with breakdown
4. Cost over time
5. Tokens in/out
6. Quality proxy (heuristic, thumbs, or regenerate rate)

Quality bar:
- default time range = 1 hour
- auto refresh every 15-30 seconds
- visible threshold/SLO line
- units clearly labeled
- no more than 6-8 panels on the main layer

---

## Panel Implementation Details

### Panel 1 — Latency P50 / P95 / P99
- **Data source**: `/metrics` endpoint → `latency_p50`, `latency_p95`, `latency_p99`
- **Visualization**: Time-series line chart (3 series)
- **SLO line**: horizontal rule at 3000ms (P95 SLO target)
- **Unit**: milliseconds (ms)
- **Alert indicator**: red zone above 5000ms

### Panel 2 — Traffic (Request Count / QPS)
- **Data source**: `/metrics` endpoint → `traffic` (cumulative counter)
- **Visualization**: Bar chart or stat panel showing total + rate/min
- **Unit**: requests / minute
- **SLO line**: N/A (informational)

### Panel 3 — Error Rate with Breakdown
- **Data source**: `/metrics` endpoint → `error_breakdown` (dict by error_type)
- **Visualization**: Pie chart (breakdown) + stat for total error rate %
- **SLO line**: horizontal rule at 2% error rate
- **Unit**: percentage (%)
- **Alert indicator**: red zone above 5%

### Panel 4 — Cost Over Time
- **Data source**: `/metrics` endpoint → `total_cost_usd`, `avg_cost_usd`
- **Visualization**: Time-series area chart (cumulative) + stat for avg cost/request
- **SLO line**: horizontal rule at $2.50/day budget
- **Unit**: USD ($)
- **Alert indicator**: spike indicator when rate exceeds 2x baseline

### Panel 5 — Tokens In / Out
- **Data source**: `/metrics` endpoint → `tokens_in_total`, `tokens_out_total`
- **Visualization**: Stacked bar chart (tokens_in vs tokens_out per request window)
- **Unit**: tokens (count)
- **Derived metric**: tokens_in/tokens_out ratio (prompt efficiency indicator)

### Panel 6 — Quality Score (Heuristic)
- **Data source**: `/metrics` endpoint → `quality_avg`
- **Visualization**: Gauge panel (0.0 – 1.0 range) + time-series trend
- **SLO line**: threshold marker at 0.75 (quality SLO target)
- **Unit**: score (0–1)
- **Color zones**: red < 0.6, yellow 0.6–0.75, green ≥ 0.75

---

## Dashboard JSON (Grafana-compatible)

See `config/grafana_dashboard.json` for the full panel configuration
that can be imported directly into Grafana.

## Metrics API Reference

Endpoint: `GET http://127.0.0.1:8000/metrics`

```json
{
  "traffic": 15,
  "latency_p50": 155.0,
  "latency_p95": 156.0,
  "latency_p99": 156.0,
  "avg_cost_usd": 0.0021,
  "total_cost_usd": 0.0317,
  "tokens_in_total": 435,
  "tokens_out_total": 2025,
  "error_breakdown": {},
  "quality_avg": 0.8
}
```
