from __future__ import annotations

import os
from typing import Any

try:
    import langfuse

    observe = langfuse.observe
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

class _DummyContext:
    def update_current_trace(self, **kwargs: Any) -> None:
        return None

    def update_current_observation(self, **kwargs: Any) -> None:
        return None


# `langfuse_context` exists in some SDK variants; keep a safe no-op so the lab code
# can attach metadata without breaking if the SDK doesn't expose that API.
langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
