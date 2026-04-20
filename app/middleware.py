from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Reset per-request context to avoid leaking metadata across requests.
        clear_contextvars()

        # Reuse upstream request ID when present, otherwise generate one.
        header_request_id = request.headers.get("x-request-id", "").strip()
        correlation_id = header_request_id or f"req-{uuid.uuid4().hex[:8]}"
        
        # Bind the correlation_id to structlog contextvars
        bind_contextvars(correlation_id=correlation_id)
        
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        response = await call_next(request)
        
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(latency_ms)
        
        return response
