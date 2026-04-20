# Dashboard Spec: FAQ Store Support System

## Required 6 Panels

### Panel 1: FAQ Request Traffic
- **Chart type**: Line area
- **Metric**: Requests per minute (count)
- **SLO line**: None (informational)
- **Purpose**: Monitor customer support load and patterns
- **Time range**: 1 hour default, refreshes every 15s

### Panel 2: Response Latency Distribution
- **Chart type**: Multi-line (P50, P95, P99)
- **Metric**: latency_ms percentiles
- **SLO line**: 2000ms for P95 (objective)
- **Purpose**: Detect tail latency and retrieval slowness
- **Thresholds**: Green <2000ms, Yellow 2000-3000ms, Red >3000ms

### Panel 3: Error Rate & Type Breakdown
- **Chart type**: Line (rate %) + stacked bar (error counts by type)
- **Metric**: error_rate_pct, error_type counts
- **SLO line**: 1% for error_rate (objective)
- **Purpose**: Identify service health and error root causes
- **Thresholds**: Green <1%, Yellow 1-5%, Red >5%

### Panel 4: Cost & Token Usage
- **Chart type**: Dual-axis (cost USD left, tokens right)
- **Metrics**: total_cost_usd, tokens_in_total, tokens_out_total
- **SLO line**: 1.0 USD daily budget (objective)
- **Purpose**: Monitor financial and resource efficiency
- **Thresholds**: Green <$0.5/day, Yellow $0.5-1.0, Red >$1.0

### Panel 5: Answer Quality Score
- **Chart type**: Line or area
- **Metric**: quality_score_avg (0-1 scale)
- **SLO line**: 0.80 (objective)
- **Purpose**: Track if FAQ answers match customer expectations
- **Thresholds**: Green >0.80, Yellow 0.70-0.80, Red <0.70

### Panel 6: Safety & Incident Status
- **Chart type**: Stat card + timeline
- **Metrics**: PII leak count (cumulative), active incidents (boolean flags)
- **SLO line**: 0 leaks (hard requirement)
- **Purpose**: Ensure data safety and track injected failures
- **Details**: Show rag_slow, tool_fail, cost_spike toggle status

## Configuration Requirements
- **Default time range**: Last 1 hour
- **Auto-refresh interval**: Every 15-30 seconds
- **Visualization**: Grid layout, 3 rows x 2 columns
- **Labels**: All axes and metrics clearly labeled with units
- **Thresholds**: Color-coded red/yellow/green per panel above
- **Data source**: `/metrics` endpoint for real-time snapshot
