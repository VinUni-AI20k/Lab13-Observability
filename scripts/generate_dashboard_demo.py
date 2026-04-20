from __future__ import annotations

import argparse
import os
import random
import time
from typing import Any

import httpx


def _post(client: httpx.Client, url: str, json: dict[str, Any]) -> tuple[int, dict[str, Any] | None]:
    try:
        r = client.post(url, json=json)
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.status_code, r.json()
        return r.status_code, None
    except Exception:
        return 0, None


def _set_incident(client: httpx.Client, base_url: str, name: str, enabled: bool) -> None:
    path = f"/incidents/{name}/enable" if enabled else f"/incidents/{name}/disable"
    try:
        client.post(f"{base_url}{path}", timeout=10.0)
    except Exception:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--traces", type=int, default=14)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--sleep", type=float, default=0.15)
    args = parser.parse_args()

    random.seed(args.seed)
    base_url = args.base_url.rstrip("/")

    ok = 0
    failed = 0
    by_status: dict[int, int] = {}

    messages = [
        "What is our monitoring policy?",
        "How does monitoring help during incidents?",
        "Refund policy for a purchase?",
        "Please explain observability: metrics vs logs vs traces.",
        "policy: do we redact emails like test@example.com?",
        "monitoring and dashboards for the lab",
    ]

    with httpx.Client(timeout=20.0) as client:
        for incident in ["rag_slow", "tool_fail", "cost_spike"]:
            _set_incident(client, base_url, incident, False)

        plan: list[tuple[str | None, bool]] = []
        plan += [(None, False)] * max(6, args.traces // 2)
        plan += [("rag_slow", True)] * 3
        plan += [("tool_fail", True)] * 2
        plan += [("cost_spike", True)] * 3
        while len(plan) < args.traces:
            plan.append((None, False))
        random.shuffle(plan)

        for idx, (incident, enabled) in enumerate(plan[: args.traces], start=1):
            for name in ["rag_slow", "tool_fail", "cost_spike"]:
                _set_incident(client, base_url, name, False)
            if incident:
                _set_incident(client, base_url, incident, enabled)

            payload = {
                "user_id": f"user-{random.randint(1, 6)}",
                "session_id": f"sess-{random.randint(1, 4)}",
                "feature": random.choice(["refunds", "faq", "monitoring", "policy"]),
                "message": random.choice(messages),
            }
            status, data = _post(client, f"{base_url}/chat", payload)
            by_status[status] = by_status.get(status, 0) + 1
            if status and 200 <= status < 300:
                ok += 1
            else:
                failed += 1

            corr = (data or {}).get("correlation_id")
            detail = ""
            if status == 422 and isinstance(data, dict) and "detail" in data:
                detail = f" detail={data['detail']}"
            print(f"[{idx:02d}/{args.traces}] incident={incident or 'none'} status={status} correlation_id={corr}{detail}")
            time.sleep(args.sleep)

        for incident in ["rag_slow", "tool_fail", "cost_spike"]:
            _set_incident(client, base_url, incident, False)

    print("\nSummary")
    print(f"- ok: {ok}")
    print(f"- failed: {failed}")
    print(f"- status_breakdown: {dict(sorted(by_status.items(), key=lambda kv: kv[0]))}")
    print("\nNext")
    print("- Open Langfuse traces and filter by tags like: lab, error, refunds/faq/monitoring/policy")
    print("- Build the 6-panel dashboard following docs/langfuse-dashboard-runbook.md")


if __name__ == "__main__":
    main()

