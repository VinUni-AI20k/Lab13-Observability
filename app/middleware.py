from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Tao mot ngu canh dinh danh nguoi dung, dam bao moi hanh dong sau do deu duoc gan voi id cu the nay,
    Giup viec tracing tro nen de dang.
    """
    async def dispatch(self, request: Request, call_next):
        # TODO: Clear contextvars to avoid leakage between requests
        clear_contextvars()

        # TODO: Extract x-request-id from headers or generate a new one
        # Use format: req-<8-char-hex>
        header_id = request.headers.get("x-request-id")
        correlation_id = header_id or f"req-{uuid.uuid4().hex[:8]}"
        
        # TODO: Bind the correlation_id to structlog contextvars
        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id # Luu lai vao state de cac phan khac co the truy cap
        
        start = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start) * 1000 # Chuyen sang ms

        # TODO: Add the correlation_id and processing time to response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{process_time:.2f}"
        
        return response
