import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

export function CostPanel(props: { data: DashboardBucket[] }) {
  const rows = props.data.map((d) => ({ ...d, t: fmtTs(d.ts) }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line type="monotone" dataKey="cost_usd" stroke="#22c55e" dot={false} name="Cost (USD)" />
      </LineChart>
    </ResponsiveContainer>
  );
}

