import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware import CorrelationIdMiddleware

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)

@app.get("/test")
async def test_endpoint(request: Request):
    # Trả về ID để chứng minh ID đã được nạp thành công ở Middleware
    return {"id_in_state": getattr(request.state, "correlation_id", "Not Found")}

client = TestClient(app)

print("--- KIỂM TRA MIDDLEWARE ---")
response = client.get("/test")
print("Response Body:", response.json())
print("Response Headers có x-request-id không?:", "x-request-id" in response.headers)
print("Response Headers có tính thời gian không?:", "x-response-time-ms" in response.headers)
print("Headers của Middleware trả về:", dict(response.headers))
