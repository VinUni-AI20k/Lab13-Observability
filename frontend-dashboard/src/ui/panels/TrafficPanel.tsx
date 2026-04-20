import { ResponsiveContainer, Area, AreaChart, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

export function TrafficPanel(props: { data: DashboardBucket[] }) {
  const rows = props.data.map((d) => ({ ...d, t: fmtTs(d.ts) }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Area type="monotone" dataKey="traffic" stroke="#34d399" fill="#34d399" fillOpacity={0.25} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

