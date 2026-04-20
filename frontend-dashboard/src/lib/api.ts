export type DashboardBucket = {
  ts: string;
  traffic: number;
  error_count: number;
  error_by_type: Record<string, number>;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  cost_usd: number;
  tokens_in: number;
  tokens_out: number;
  quality_avg: number;
};

export type DashboardSeriesResponse = {
  window_minutes: number;
  bucket_seconds: number;
  series: DashboardBucket[];
};

export type HealthResponse = {
  ok: boolean;
  tracing?: {
    configured?: boolean;
    ready?: boolean;
    import_error?: string | null;
  };
};

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

export function getBaseUrl(): string {
  const v = (import.meta as any).env?.VITE_API_BASE_URL as string | undefined;
  return (v && v.trim()) || DEFAULT_BASE_URL;
}

async function fetchJson<T>(path: string): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const r = await fetch(url, { method: "GET" });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${path}`);
  return (await r.json()) as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>("/health");
}

export async function fetchSeries(windowMinutes: number, bucketSeconds: number): Promise<DashboardSeriesResponse> {
  const qs = new URLSearchParams({
    window_minutes: String(windowMinutes),
    bucket_seconds: String(bucketSeconds),
  });
  return fetchJson<DashboardSeriesResponse>(`/dashboard/series?${qs.toString()}`);
}

