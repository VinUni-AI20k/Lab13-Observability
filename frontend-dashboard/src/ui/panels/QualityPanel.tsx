import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

export function QualityPanel(props: { data: DashboardBucket[] }) {
  const rows = props.data.map((d) => ({ ...d, t: fmtTs(d.ts) }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
        <Tooltip />
        <ReferenceLine y={0.7} stroke="#f59e0b" strokeDasharray="5 5" />
        <Line type="monotone" dataKey="quality_avg" stroke="#fbbf24" dot={false} name="Quality avg" />
      </LineChart>
    </ResponsiveContainer>
  );
}

