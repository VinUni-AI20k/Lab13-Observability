import sys
import json
import subprocess
from pathlib import Path

# Add project root to sys.path to resolve 'app' module
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_chat_pii():
    print("Testing /chat with PII...")
    payload = {
        "user_id": "user_test_01",
        "session_id": "session_test_01",
        "feature": "qa",
        "message": "My email is test@example.com and my phone is 0912345678. My CCCD is 123456789012. My address is Số 1, Đường Đại Cồ Việt, Quận Hai Bà Trưng. My passport is B1234567."
    }
    response = client.post("/chat", json=payload)
    print(f"Response Status: {response.status_code}")
    print(f"Correlation ID in Header: {response.headers.get('x-request-id')}")
    print(f"Response Time in Header: {response.headers.get('x-response-time-ms')}ms")
    
    # Check logs
    print("\nChecking logs for redaction...")
    with open("data/logs.jsonl", "r") as f:
        lines = f.readlines()
        last_logs = lines[-5:] # Get last few logs
        for line in last_logs:
            if "request_received" in line or "response_sent" in line:
                print(f"Log: {line.strip()}")
                if "@example.com" in line or "0912345678" in line or "B1234567" in line:
                    print("!!! PII LEAK DETECTED !!!")
                else:
                    print("PII Redacted successfully.")

if __name__ == "__main__":
    test_chat_pii()
    print("-" * 20)
    test_chat_pii()
    print("\nRunning official validation script...")
    import sys
    result = subprocess.run([sys.executable, "scripts/validate_logs.py"], capture_output=True, text=True)
    print(result.stdout)
