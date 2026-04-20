from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Clear any previously bound context so values do not leak between requests.
        # Clear contextvars to avoid leakage between requests
        clear_contextvars()

        incoming_request_id = request.headers.get("x-request-id", "").strip()
        correlation_id = incoming_request_id if incoming_request_id.startswith("req-") and len(incoming_request_id) == 12 else f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        response.headers["x-request-id"] = correlation_id
        processing_ms = int((time.perf_counter() - start) * 1000)
        response.headers["x-response-time-ms"] = str(processing_ms)

        return response
