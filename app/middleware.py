from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()

        header_id = request.headers.get("x-request-id")
        correlation_id = None
        if header_id:
            candidate = header_id.strip().lower()
            if candidate.startswith("req-") and len(candidate) == 12:
                hex_part = candidate[4:]
                if all(ch in "0123456789abcdef" for ch in hex_part):
                    correlation_id = candidate
        if correlation_id is None:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(int((time.perf_counter() - start) * 1000))

        return response
