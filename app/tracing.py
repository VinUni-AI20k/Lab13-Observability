from __future__ import annotations
import os
from typing import Any

try:
    from langfuse import observe
    from langfuse import get_client
    _client = get_client()
    
    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            try:
                _client.update_current_trace(**kwargs)
            except Exception:
                pass
        def update_current_observation(self, **kwargs: Any) -> None:
            try:
                _client.update_current_observation(**kwargs)
            except Exception:
                pass
    
    langfuse_context = _LangfuseContext()

except Exception:
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None
        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))