import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis, ReferenceLine, Legend } from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

export function LatencyPanel(props: { data: DashboardBucket[] }) {
  const rows = props.data.map((d) => ({
    ...d,
    t: fmtTs(d.ts),
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <ReferenceLine y={2000} stroke="#f59e0b" strokeDasharray="5 5" />
        <Line type="monotone" dataKey="latency_p50_ms" stroke="#60a5fa" dot={false} name="P50" />
        <Line type="monotone" dataKey="latency_p95_ms" stroke="#a78bfa" dot={false} name="P95" />
        <Line type="monotone" dataKey="latency_p99_ms" stroke="#f87171" dot={false} name="P99" />
      </LineChart>
    </ResponsiveContainer>
  );
}

