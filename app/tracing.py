from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    def get_client(*args: Any, **kwargs: Any) -> _DummyContext:
        return _DummyContext()


langfuse_context = get_client()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
