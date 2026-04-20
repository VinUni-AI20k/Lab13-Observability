import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchHealth, fetchSeries } from "../lib/api";
import { ChartCard } from "./components/ChartCard";
import { LatencyPanel } from "./panels/LatencyPanel";
import { TrafficPanel } from "./panels/TrafficPanel";
import { ErrorsPanel } from "./panels/ErrorsPanel";
import { CostPanel } from "./panels/CostPanel";
import { TokensPanel } from "./panels/TokensPanel";
import { QualityPanel } from "./panels/QualityPanel";

const DEFAULT_WINDOW_MINUTES = 60;
const DEFAULT_BUCKET_SECONDS = 60;
const REFRESH_MS = 15_000;

export function App() {
  const [windowMinutes, setWindowMinutes] = useState(DEFAULT_WINDOW_MINUTES);
  const [bucketSeconds, setBucketSeconds] = useState(DEFAULT_BUCKET_SECONDS);

  const healthQ = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchInterval: REFRESH_MS,
  });

  const seriesQ = useQuery({
    queryKey: ["series", windowMinutes, bucketSeconds],
    queryFn: () => fetchSeries(windowMinutes, bucketSeconds),
    refetchInterval: REFRESH_MS,
  });

  const status = useMemo(() => {
    const t = healthQ.data?.tracing;
    if (!t) return "health unknown";
    if (t.import_error) return `tracing import_error: ${t.import_error}`;
    if (t.ready === false) return "tracing not ready";
    if (t.ready === true) return "tracing ready";
    return "tracing status unknown";
  }, [healthQ.data]);

  return (
    <div className="page">
      <header className="header">
        <div className="titleBlock">
          <div className="title">Lab13 Team61 — Layer 2 Dashboard</div>
          <div className="subtitle">
            Default range: last {windowMinutes} minutes • Auto-refresh: {Math.round(REFRESH_MS / 1000)}s • {status}
          </div>
        </div>
        <div className="controls">
          <label className="field">
            <span>Window</span>
            <select value={windowMinutes} onChange={(e) => setWindowMinutes(Number(e.target.value))}>
              <option value={60}>Last 1 hour</option>
              <option value={180}>Last 3 hours</option>
              <option value={1440}>Last 1 day</option>
            </select>
          </label>
          <label className="field">
            <span>Bucket</span>
            <select value={bucketSeconds} onChange={(e) => setBucketSeconds(Number(e.target.value))}>
              <option value={60}>1 min</option>
              <option value={30}>30 sec</option>
              <option value={120}>2 min</option>
            </select>
          </label>
        </div>
      </header>

      <main className="grid">
        <ChartCard title="Latency (P50 / P95 / P99)" unit="ms" hint="SLO line: P95 < 2000ms">
          <LatencyPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>

        <ChartCard title="Traffic" unit="requests/min" hint="Count of completed requests per bucket">
          <TrafficPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>

        <ChartCard title="Error rate + breakdown" unit="errors/min" hint="Breakdown by error_type">
          <ErrorsPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>

        <ChartCard title="Cost over time" unit="USD" hint="Bucketed total cost">
          <CostPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>

        <ChartCard title="Tokens in/out" unit="tokens" hint="Bucketed token totals">
          <TokensPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>

        <ChartCard title="Quality proxy" unit="0.0–1.0" hint="Threshold line: 0.7">
          <QualityPanel data={seriesQ.data?.series ?? []} />
        </ChartCard>
      </main>

      {(healthQ.isError || seriesQ.isError) && (
        <div className="errorBanner">
          {healthQ.isError ? "Health fetch failed. " : ""}
          {seriesQ.isError ? "Series fetch failed. " : ""}
          Ensure backend is running on 127.0.0.1:8000 and CORS is enabled.
        </div>
      )}
    </div>
  );
}

