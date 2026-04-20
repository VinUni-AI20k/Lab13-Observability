import { ResponsiveContainer, Area, AreaChart, Tooltip, XAxis, YAxis, Legend } from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

export function TokensPanel(props: { data: DashboardBucket[] }) {
  const rows = props.data.map((d) => ({ ...d, t: fmtTs(d.ts) }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Area type="monotone" dataKey="tokens_in" stackId="1" stroke="#60a5fa" fill="#60a5fa" fillOpacity={0.25} name="Tokens in" />
        <Area type="monotone" dataKey="tokens_out" stackId="1" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.25} name="Tokens out" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

