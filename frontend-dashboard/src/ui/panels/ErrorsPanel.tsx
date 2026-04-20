import { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
  Bar,
  Line,
  ComposedChart,
} from "recharts";
import type { DashboardBucket } from "../../lib/api";

function fmtTs(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return ts;
  }
}

const COLORS = ["#f87171", "#fb7185", "#fbbf24", "#60a5fa", "#34d399", "#a78bfa", "#94a3b8"];

export function ErrorsPanel(props: { data: DashboardBucket[] }) {
  const { rows, keys } = useMemo(() => {
    const allKeys = new Set<string>();
    for (const b of props.data) for (const k of Object.keys(b.error_by_type || {})) allKeys.add(k);
    const keys = Array.from(allKeys).slice(0, 6);
    const rows = props.data.map((b) => {
      const row: any = { t: fmtTs(b.ts), error_count: b.error_count };
      for (const k of keys) row[k] = b.error_by_type?.[k] ?? 0;
      return row;
    });
    return { rows, keys };
  }, [props.data]);

  if (keys.length === 0) {
    return (
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
          <XAxis dataKey="t" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="error_count" fill="#f87171" />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={rows} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <XAxis dataKey="t" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {keys.map((k, idx) => (
          <Bar key={k} dataKey={k} stackId="a" fill={COLORS[idx % COLORS.length]} name={k} />
        ))}
        <Line type="monotone" dataKey="error_count" stroke="#ef4444" dot={false} name="Errors (total)" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

