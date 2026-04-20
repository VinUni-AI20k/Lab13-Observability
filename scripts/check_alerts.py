import time
import httpx

# Alert Rules defined in config/alert_rules.yaml
# We hardcode the simplified logic here for testing purposes
RULES = [
    {
        "name": "high_latency_p95",
        "severity": "P2",
        "check": lambda m: m.get("latency_p95", 0) > 5000,
        "desc": "latency_p95_ms > 5000 for 30m",
        "runbook": "docs/alerts.md#1-high-latency-p95"
    },
    {
        "name": "high_error_rate",
        "severity": "P1",
        "check": lambda m: (sum(m.get("error_breakdown", {}).values()) / m.get("traffic", 1) * 100) > 5 if m.get("traffic", 0) > 0 else False,
        "desc": "error_rate_pct > 5 for 5m",
        "runbook": "docs/alerts.md#2-high-error-rate"
    },
    {
        "name": "cost_budget_spike",
        "severity": "P2",
        "check": lambda m: m.get("total_cost_usd", 0) > 1.0, # Using $1.0 as a mock 2x_baseline threshold
        "desc": "hourly_cost_usd > 2x_baseline for 15m",
        "runbook": "docs/alerts.md#3-cost-budget-spike"
    }
]

def main():
    print("🚀 Alert Monitor Started. Press Ctrl+C to stop.")
    print("Waiting for metrics from http://127.0.0.1:8000/metrics...")
    
    while True:
        try:
            r = httpx.get("http://127.0.0.1:8000/metrics", timeout=5.0)
            metrics = r.json()
            
            print("\n--- Evaluating Alerts ---")
            all_ok = True
            for rule in RULES:
                if rule["check"](metrics):
                    print(f"🚨 [ALERT TRIGGERED] {rule['name']} (Severity: {rule['severity']})")
                    print(f"   Condition: {rule['desc']}")
                    print(f"   Runbook: {rule['runbook']}")
                    all_ok = False
                else:
                    print(f"✅ [OK] {rule['name']}")
                    
            if all_ok:
                print("Systems normal. No active alerts.")
                
        except Exception as e:
            print(f"⚠️ Could not connect to metrics endpoint: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    main()
