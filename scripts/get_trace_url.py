from dotenv import load_dotenv
load_dotenv()
import httpx

payload = {
    "user_id": "user-test-002",
    "session_id": "session-test",
    "feature": "qa",
    "message": "How to design alerts?"
}

print("Sending request...")
resp = httpx.post("http://127.0.0.1:8000/chat", json=payload, timeout=30)
data = resp.json()
print(f"Correlation ID: {data.get('correlation_id')}")
print(f"Latency: {data.get('latency_ms')}ms")
print(f"Tokens: {data.get('tokens_in')} in / {data.get('tokens_out')} out")
print()

from langfuse import get_client
client = get_client()
client.flush()

trace_id = client.get_current_trace_id()
print()
print("=" * 60)
print("Open this URL in your browser:")
print(f"https://cloud.langfuse.com/project/cmo6ibnd300d9ad08ewr0fwcp/traces/{trace_id}")
print("=" * 60)
