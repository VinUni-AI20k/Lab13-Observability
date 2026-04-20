from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xóa context log của request trước để tránh rò rỉ ID giữa các request.
        clear_contextvars()
        correlation_id = request.headers.get("x-request-id", f"req-{uuid.uuid4().hex[:8]}")
        # Bind correlation_id một lần để mọi log trong request này đều kế thừa nó.
        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        # Trả lại header để client có thể đối chiếu request và thời gian xử lý.
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
        return response
