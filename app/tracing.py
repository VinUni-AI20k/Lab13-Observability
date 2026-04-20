from __future__ import annotations

import os
from typing import Any

_langfuse_client = None

try:
    from langfuse import Langfuse, observe
    
    # Initialize global client for Langfuse v3
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
    
    if pk and sk:
        _langfuse_client = Langfuse(public_key=pk, secret_key=sk, host=host)

    class _LangfuseContextShim:
        """Compatibility layer for langfuse_context in v3"""
        def update_current_trace(self, **kwargs: Any) -> None:
            if _langfuse_client:
                try:
                    _langfuse_client.update_current_trace(**kwargs)
                except Exception:
                    pass

        def update_current_observation(self, **kwargs: Any) -> None:
            if _langfuse_client:
                try:
                    _langfuse_client.update_current_span(**kwargs)
                except Exception:
                    pass

    langfuse_context = _LangfuseContextShim()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            pass
        def update_current_observation(self, **kwargs: Any) -> None:
            pass

    langfuse_context = _DummyContext()

def tracing_enabled() -> bool:
    return _langfuse_client is not None
