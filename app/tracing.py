from __future__ import annotations

import os
from typing import Any

try:
    from langfuse.decorators import observe, langfuse_context
    SDK_LOADED = True
except Exception:  # pragma: no cover
    SDK_LOADED = False
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
    enabled = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    if enabled and not SDK_LOADED:
        print("⚠️ WARNING: Langfuse keys found but SDK failed to load!")
    return enabled and SDK_LOADED
