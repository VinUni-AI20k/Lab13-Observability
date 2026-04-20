"""Simple dashboard that polls /metrics and displays in terminal."""
import time, requests, os

BASE = os.getenv("APP_URL", "http://localhost:8000")

def render():
    try:
        m = requests.get(f"{BASE}/metrics", timeout=2).json()
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\033[2J\033[H")  # clear screen
    print("=" * 55)
    print("  Day 13 Observability Dashboard")
    print("=" * 55)
    print(f"  [1] Latency (ms)   P50:{m['latency_p50']:>7.0f}  "
          f"P95:{m['latency_p95']:>7.0f}  P99:{m['latency_p99']:>7.0f}")
    print(f"      SLO: P95 < 3000ms  {'OK' if m['latency_p95'] < 3000 else 'BREACH':>6}")
    print(f"  [2] Traffic        {m['traffic']:>7} requests total")
    total = m['traffic'] or 1
    err_count = sum(m['error_breakdown'].values())
    err_rate = err_count / total * 100
    print(f"  [3] Error Rate     {err_rate:>7.2f}%  "
          f"({'OK' if err_rate < 2 else 'BREACH'})")
    print(f"  [4] Cost           avg ${m['avg_cost_usd']:>8.4f}  "
          f"total ${m['total_cost_usd']:>8.4f}")
    print(f"  [5] Tokens         in:{m['tokens_in_total']:>8}  out:{m['tokens_out_total']:>8}")
    print(f"  [6] Quality Avg    {m['quality_avg']:>7.4f}  "
          f"({'OK' if m['quality_avg'] >= 0.75 else 'LOW'})")
    print("=" * 55)
    print(f"  Last updated: {time.strftime('%H:%M:%S')}  (refresh 15s)")

if __name__ == "__main__":
    while True:
        render()
        time.sleep(15)
