import time

from dotenv import load_dotenv

load_dotenv()
import httpx, os

payload = {
    "user_id": "user-demo-001",
    "session_id": "session-demo",
    "feature": "qa",
    "message": "What is observability?"
}

print("Sending request to /chat...")
resp = httpx.post("http://127.0.0.1:8000/chat", json=payload, timeout=30)
resp.raise_for_status()
data = resp.json()
correlation_id = data.get("correlation_id")
print(f"Status: {resp.status_code}")
print(f"Correlation ID: {correlation_id}")
print(f"Latency: {data.get('latency_ms')}ms")
print(f"Tokens: {data.get('tokens_in')} in / {data.get('tokens_out')} out")
print()

# Verify the trace appeared in Langfuse via the API
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
project_id = "cmo6ibnd300d9ad08ewr0fwcp"

if public_key and secret_key:
    print("Waiting for Langfuse to ingest the trace...")
    time.sleep(2)
    auth = (public_key, secret_key)
    trace_found = None
    for _ in range(3):
        resp = httpx.get(
            f"{base_url}/api/public/projects/{project_id}/traces",
            auth=auth,
            timeout=15,
        )
        if resp.status_code == 200:
            traces = resp.json().get("data", [])
            for t in traces:
                if t.get("metadata", {}).get("correlation_id") == correlation_id:
                    trace_found = t
                    break
            if trace_found:
                break
        time.sleep(2)

    if trace_found:
        trace_id = trace_found["id"]
        print(f"[OK] Trace found in Langfuse!")
        print(f"     Trace ID: {trace_id}")
        print(f"     View at: {base_url}/project/{project_id}/traces/{trace_id}")
    else:
        print("[WARN] Trace not found in Langfuse via API — check the dashboard manually:")
        print(f"       {base_url}/project/{project_id}/traces")
else:
    print("Langfuse credentials not set — skipping trace verification.")
    print(f"View traces at: {base_url}/project/{project_id}/traces")
